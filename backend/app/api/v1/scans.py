import os
import shutil
import tempfile
import subprocess
import httpx
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.agent_scan import AgentScan
from app.models.compliance_card import ComplianceCard
from app.schemas.schemas import AgentScanResponse
from app.services.discovery_service import discover_agent_assets, extract_zip_and_discover
from app.services.ast_scanner import scan_python_code
from app.services.compliance_engine import build_compliance_card_payload
from app.services.framework_mapper import GovernanceFrameworkMapper

router = APIRouter()


class GithubScanRequest(BaseModel):
    repo_url: str
    agent_name: Optional[str] = None


class CodeSnippetScanRequest(BaseModel):
    agent_name: str
    code_content: str
    version: Optional[str] = "1.0.0"


@router.get("/", response_model=List[AgentScanResponse])
async def list_scans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentScan).order_by(AgentScan.created_at.desc()))
    scans = result.scalars().all()
    
    response = []
    for s in scans:
        response.append({
            "id": s.id,
            "agent_name": s.agent_name,
            "version": s.version,
            "source_type": s.source_type,
            "framework": s.framework,
            "compliance_score": s.compliance_score,
            "risk_score": s.risk_score,
            "risk_tier": s.risk_tier,
            "llm_providers": s.llm_providers or [],
            "tools_detected": s.tools_detected or [],
            "data_sources": s.data_sources or [],
            "external_apis": s.external_apis or [],
            "framework_compliance": s.framework_compliance or {},
            "summary": s.summary,
            "created_at": s.created_at.isoformat() if s.created_at else ""
        })
    return response


@router.post("/scan-sample", response_model=AgentScanResponse)
async def scan_sample_agent(
    sample_key: str = "finance_agent",
    db: AsyncSession = Depends(get_db)
):
    base_samples = "/Users/nikynsuresh/Documents/Aivar drive/samples"
    sample_path = os.path.join(base_samples, sample_key)
    
    if not os.path.exists(sample_path):
        raise HTTPException(status_code=404, detail=f"Sample '{sample_key}' not found")

    discovered = discover_agent_assets(sample_path)
    card_payload = build_compliance_card_payload(discovered)
    
    framework_eval = GovernanceFrameworkMapper.evaluate_frameworks(
        scan_data=discovered,
        risk_score=card_payload["risk_score"],
        compliance_score=card_payload["compliance_score"]
    )

    scan_record = AgentScan(
        agent_name=discovered.get("agent_name", sample_key.replace("_", " ").title()),
        version=discovered.get("version", "1.0.0"),
        source_type="sample",
        source_path=sample_path,
        framework=discovered.get("framework", "Custom Python"),
        compliance_score=card_payload["compliance_score"],
        risk_score=card_payload["risk_score"],
        risk_tier=card_payload["risk_tier"],
        llm_providers=discovered.get("llm_providers", []),
        tools_detected=discovered.get("tools_detected", []),
        data_sources=discovered.get("data_sources", []),
        external_apis=discovered.get("external_apis", []),
        framework_compliance=framework_eval,
        summary=f"Automated scan of {sample_key} sample agent codebase."
    )
    db.add(scan_record)
    await db.commit()
    await db.refresh(scan_record)

    card_rec = ComplianceCard(
        scan_id=scan_record.id,
        agent_purpose=card_payload["card"]["agent_purpose"],
        llm_and_version=card_payload["card"]["llm_and_version"],
        tool_inventory=card_payload["card"]["tool_inventory"],
        data_sources=card_payload["card"]["data_sources"],
        decision_authority=card_payload["card"]["decision_authority"],
        human_oversight=card_payload["card"]["human_oversight"],
        risk_classification=card_payload["card"]["risk_classification"],
        known_limitations=card_payload["card"]["known_limitations"],
        incident_contact=card_payload["card"]["incident_contact"],
        completeness_score=card_payload["completeness_score"],
        missing_fields=card_payload["missing_fields"],
        placeholder_warnings=card_payload["placeholder_warnings"],
        raw_card_json=card_payload
    )
    db.add(card_rec)
    await db.commit()

    return {
        "id": scan_record.id,
        "agent_name": scan_record.agent_name,
        "version": scan_record.version,
        "source_type": scan_record.source_type,
        "framework": scan_record.framework,
        "compliance_score": scan_record.compliance_score,
        "risk_score": scan_record.risk_score,
        "risk_tier": scan_record.risk_tier,
        "llm_providers": scan_record.llm_providers,
        "tools_detected": scan_record.tools_detected,
        "data_sources": scan_record.data_sources,
        "external_apis": scan_record.external_apis,
        "framework_compliance": scan_record.framework_compliance,
        "summary": scan_record.summary,
        "created_at": scan_record.created_at.isoformat()
    }


@router.post("/upload-zip", response_model=AgentScanResponse)
async def upload_and_scan_zip(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported")

    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, file.filename)
        with open(zip_path, "wb") as f:
            f.write(await file.read())

        extract_dir = os.path.join(tmp_dir, "extracted")
        discovered = extract_zip_and_discover(zip_path, extract_dir)
        discovered["agent_name"] = file.filename.replace(".zip", "").replace("_", " ").title()

        card_payload = build_compliance_card_payload(discovered)
        framework_eval = GovernanceFrameworkMapper.evaluate_frameworks(
            scan_data=discovered,
            risk_score=card_payload["risk_score"],
            compliance_score=card_payload["compliance_score"]
        )

        scan_record = AgentScan(
            agent_name=discovered["agent_name"],
            version=discovered.get("version", "1.0.0"),
            source_type="zip_upload",
            source_path=file.filename,
            framework=discovered.get("framework", "Custom Python"),
            compliance_score=card_payload["compliance_score"],
            risk_score=card_payload["risk_score"],
            risk_tier=card_payload["risk_tier"],
            llm_providers=discovered.get("llm_providers", []),
            tools_detected=discovered.get("tools_detected", []),
            data_sources=discovered.get("data_sources", []),
            external_apis=discovered.get("external_apis", []),
            framework_compliance=framework_eval,
            summary=f"ZIP Archive scan of '{file.filename}'."
        )
        db.add(scan_record)
        await db.commit()
        await db.refresh(scan_record)

        card_rec = ComplianceCard(
            scan_id=scan_record.id,
            agent_purpose=card_payload["card"]["agent_purpose"],
            llm_and_version=card_payload["card"]["llm_and_version"],
            tool_inventory=card_payload["card"]["tool_inventory"],
            data_sources=card_payload["card"]["data_sources"],
            decision_authority=card_payload["card"]["decision_authority"],
            human_oversight=card_payload["card"]["human_oversight"],
            risk_classification=card_payload["card"]["risk_classification"],
            known_limitations=card_payload["card"]["known_limitations"],
            incident_contact=card_payload["card"]["incident_contact"],
            completeness_score=card_payload["completeness_score"],
            missing_fields=card_payload["missing_fields"],
            placeholder_warnings=card_payload["placeholder_warnings"],
            raw_card_json=card_payload
        )
        db.add(card_rec)
        await db.commit()

        return {
            "id": scan_record.id,
            "agent_name": scan_record.agent_name,
            "version": scan_record.version,
            "source_type": scan_record.source_type,
            "framework": scan_record.framework,
            "compliance_score": scan_record.compliance_score,
            "risk_score": scan_record.risk_score,
            "risk_tier": scan_record.risk_tier,
            "llm_providers": scan_record.llm_providers,
            "tools_detected": scan_record.tools_detected,
            "data_sources": scan_record.data_sources,
            "external_apis": scan_record.external_apis,
            "framework_compliance": scan_record.framework_compliance,
            "summary": scan_record.summary,
            "created_at": scan_record.created_at.isoformat()
        }


@router.post("/scan-github", response_model=AgentScanResponse)
async def scan_github_repository(
    payload: GithubScanRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Parses a public GitHub repository URL (supports .git suffix, main/master/custom branches, git clone),
    runs AST scanner, and returns compliance card.
    """
    url = payload.repo_url.strip().rstrip("/")
    if not ("github.com" in url or url.startswith("http")):
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL")

    # Clean URL format (strip .git)
    clean_url = url.replace(".git", "")
    parts = clean_url.replace("https://github.com/", "").replace("http://github.com/", "").split("/")
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="URL must be in format: https://github.com/username/repository")

    owner, repo = parts[0], parts[1]
    repo_name = repo.replace(".git", "")

    with tempfile.TemporaryDirectory() as tmp_dir:
        cloned = False

        # Attempt 1: Git clone --depth 1 (most reliable for any branch/repo name)
        try:
            clone_cmd = ["git", "clone", "--depth", "1", f"https://github.com/{owner}/{repo_name}.git", tmp_dir]
            proc = subprocess.run(clone_cmd, capture_output=True, text=True, timeout=25)
            if proc.returncode == 0:
                cloned = True
        except Exception:
            pass

        # Attempt 2: Download zip archive fallback
        if not cloned:
            zip_urls = [
                f"https://github.com/{owner}/{repo_name}/archive/refs/heads/main.zip",
                f"https://github.com/{owner}/{repo_name}/archive/refs/heads/master.zip",
                f"https://github.com/{owner}/{repo_name}/archive/refs/heads/dev.zip"
            ]
            zip_path = os.path.join(tmp_dir, "repo.zip")
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                for z_url in zip_urls:
                    try:
                        resp = await client.get(z_url)
                        if resp.status_code == 200:
                            with open(zip_path, "wb") as f:
                                f.write(resp.content)
                            extract_dir = os.path.join(tmp_dir, "extracted")
                            extract_zip_and_discover(zip_path, extract_dir)
                            cloned = True
                            break
                    except Exception:
                        continue

        if not cloned and not os.listdir(tmp_dir):
            raise HTTPException(status_code=400, detail=f"Could not fetch GitHub repository '{owner}/{repo_name}'. Ensure repository is public and URL is correct.")

        discovered = discover_agent_assets(tmp_dir)
        discovered["agent_name"] = payload.agent_name or f"{owner}/{repo_name}"

        card_payload = build_compliance_card_payload(discovered)
        framework_eval = GovernanceFrameworkMapper.evaluate_frameworks(
            scan_data=discovered,
            risk_score=card_payload["risk_score"],
            compliance_score=card_payload["compliance_score"]
        )

        scan_record = AgentScan(
            agent_name=discovered["agent_name"],
            version=discovered.get("version", "1.0.0"),
            source_type="github",
            source_path=url,
            framework=discovered.get("framework", "Custom Python"),
            compliance_score=card_payload["compliance_score"],
            risk_score=card_payload["risk_score"],
            risk_tier=card_payload["risk_tier"],
            llm_providers=discovered.get("llm_providers", []),
            tools_detected=discovered.get("tools_detected", []),
            data_sources=discovered.get("data_sources", []),
            external_apis=discovered.get("external_apis", []),
            framework_compliance=framework_eval,
            summary=f"GitHub Repository scan of '{url}'."
        )
        db.add(scan_record)
        await db.commit()
        await db.refresh(scan_record)

        card_rec = ComplianceCard(
            scan_id=scan_record.id,
            agent_purpose=card_payload["card"]["agent_purpose"],
            llm_and_version=card_payload["card"]["llm_and_version"],
            tool_inventory=card_payload["card"]["tool_inventory"],
            data_sources=card_payload["card"]["data_sources"],
            decision_authority=card_payload["card"]["decision_authority"],
            human_oversight=card_payload["card"]["human_oversight"],
            risk_classification=card_payload["card"]["risk_classification"],
            known_limitations=card_payload["card"]["known_limitations"],
            incident_contact=card_payload["card"]["incident_contact"],
            completeness_score=card_payload["completeness_score"],
            missing_fields=card_payload["missing_fields"],
            placeholder_warnings=card_payload["placeholder_warnings"],
            raw_card_json=card_payload
        )
        db.add(card_rec)
        await db.commit()

        return {
            "id": scan_record.id,
            "agent_name": scan_record.agent_name,
            "version": scan_record.version,
            "source_type": scan_record.source_type,
            "framework": scan_record.framework,
            "compliance_score": scan_record.compliance_score,
            "risk_score": scan_record.risk_score,
            "risk_tier": scan_record.risk_tier,
            "llm_providers": scan_record.llm_providers,
            "tools_detected": scan_record.tools_detected,
            "data_sources": scan_record.data_sources,
            "external_apis": scan_record.external_apis,
            "framework_compliance": scan_record.framework_compliance,
            "summary": scan_record.summary,
            "created_at": scan_record.created_at.isoformat()
        }


@router.post("/scan-code-snippet", response_model=AgentScanResponse)
async def scan_code_snippet(
    payload: CodeSnippetScanRequest,
    db: AsyncSession = Depends(get_db)
):
    if not payload.code_content.strip():
        raise HTTPException(status_code=400, detail="Code content cannot be empty")

    ast_res = scan_python_code(payload.code_content)
    discovered = {
        "agent_name": payload.agent_name,
        "version": payload.version or "1.0.0",
        "framework": "Custom Python Code",
        "agent_purpose": "Single file / pasted Python agent script",
        "llm_providers": ast_res["llm_providers"] or ["OpenAI GPT-4o"],
        "tools_detected": ast_res["tools_detected"],
        "data_sources": ast_res["data_sources"] or ["InMemory Application State"],
        "external_apis": ast_res["external_apis"] or [],
        "human_oversight": "Human-in-the-Loop Required",
        "incident_contact": "security@enterprise.com"
    }

    card_payload = build_compliance_card_payload(discovered)
    framework_eval = GovernanceFrameworkMapper.evaluate_frameworks(
        scan_data=discovered,
        risk_score=card_payload["risk_score"],
        compliance_score=card_payload["compliance_score"]
    )

    scan_record = AgentScan(
        agent_name=payload.agent_name,
        version=payload.version or "1.0.0",
        source_type="code_snippet",
        source_path="Pasted Source Code",
        framework="Custom Python",
        compliance_score=card_payload["compliance_score"],
        risk_score=card_payload["risk_score"],
        risk_tier=card_payload["risk_tier"],
        llm_providers=discovered["llm_providers"],
        tools_detected=discovered["tools_detected"],
        data_sources=discovered["data_sources"],
        external_apis=discovered["external_apis"],
        framework_compliance=framework_eval,
        summary=f"Pasted source code snippet scan of '{payload.agent_name}'."
    )
    db.add(scan_record)
    await db.commit()
    await db.refresh(scan_record)

    card_rec = ComplianceCard(
        scan_id=scan_record.id,
        agent_purpose=card_payload["card"]["agent_purpose"],
        llm_and_version=card_payload["card"]["llm_and_version"],
        tool_inventory=card_payload["card"]["tool_inventory"],
        data_sources=card_payload["card"]["data_sources"],
        decision_authority=card_payload["card"]["decision_authority"],
        human_oversight=card_payload["card"]["human_oversight"],
        risk_classification=card_payload["card"]["risk_classification"],
        known_limitations=card_payload["card"]["known_limitations"],
        incident_contact=card_payload["card"]["incident_contact"],
        completeness_score=card_payload["completeness_score"],
        missing_fields=card_payload["missing_fields"],
        placeholder_warnings=card_payload["placeholder_warnings"],
        raw_card_json=card_payload
    )
    db.add(card_rec)
    await db.commit()

    return {
        "id": scan_record.id,
        "agent_name": scan_record.agent_name,
        "version": scan_record.version,
        "source_type": scan_record.source_type,
        "framework": scan_record.framework,
        "compliance_score": scan_record.compliance_score,
        "risk_score": scan_record.risk_score,
        "risk_tier": scan_record.risk_tier,
        "llm_providers": scan_record.llm_providers,
        "tools_detected": scan_record.tools_detected,
        "data_sources": scan_record.data_sources,
        "external_apis": scan_record.external_apis,
        "framework_compliance": scan_record.framework_compliance,
        "summary": scan_record.summary,
        "created_at": scan_record.created_at.isoformat()
    }


@router.get("/{scan_id}", response_model=AgentScanResponse)
async def get_scan(scan_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentScan).where(AgentScan.id == scan_id))
    s = result.scalars().first()
    if not s:
        raise HTTPException(status_code=404, detail="Scan record not found")

    return {
        "id": s.id,
        "agent_name": s.agent_name,
        "version": s.version,
        "source_type": s.source_type,
        "framework": s.framework,
        "compliance_score": s.compliance_score,
        "risk_score": s.risk_score,
        "risk_tier": s.risk_tier,
        "llm_providers": s.llm_providers or [],
        "tools_detected": s.tools_detected or [],
        "data_sources": s.data_sources or [],
        "external_apis": s.external_apis or [],
        "framework_compliance": s.framework_compliance or {},
        "summary": s.summary,
        "created_at": s.created_at.isoformat() if s.created_at else ""
    }
