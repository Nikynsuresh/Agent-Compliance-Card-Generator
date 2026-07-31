from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.agent_scan import AgentScan
from app.models.compliance_card import ComplianceCard
from app.services.pdf_exporter import generate_compliance_pdf

router = APIRouter()


@router.get("/pdf/{scan_id}")
async def export_pdf_report(scan_id: str, db: AsyncSession = Depends(get_db)):
    target_id = None
    try:
        target_id = int(scan_id)
    except (ValueError, TypeError):
        pass

    scan = None
    if target_id is not None:
        res1 = await db.execute(select(AgentScan).where(AgentScan.id == target_id))
        scan = res1.scalars().first()

    if not scan:
        res_latest = await db.execute(select(AgentScan).order_by(AgentScan.id.desc()))
        scan = res_latest.scalars().first()

    if not scan:
        raise HTTPException(status_code=404, detail="No scans found in database")

    res2 = await db.execute(select(ComplianceCard).where(ComplianceCard.scan_id == scan.id))
    card = res2.scalars().first()

    scan_dict = {
        "agent_name": scan.agent_name,
        "framework": scan.framework,
        "compliance_score": scan.compliance_score,
        "risk_score": scan.risk_score,
        "risk_tier": scan.risk_tier,
        "tools_detected": scan.tools_detected or [],
        "data_sources": scan.data_sources or []
    }

    card_dict = {
        "agent_purpose": card.agent_purpose if card else "Enterprise Task Automation",
        "llm_and_version": card.llm_and_version if card else ", ".join(scan.llm_providers or []),
        "decision_authority": card.decision_authority if card else "Semi-Autonomous",
        "human_oversight": card.human_oversight if card else "Human-in-the-Loop",
        "incident_contact": card.incident_contact if card else "security@enterprise.com"
    }

    pdf_bytes = generate_compliance_pdf(scan_dict, card_dict)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Agent_Compliance_Audit_Scan_{scan.id}.pdf"}
    )


@router.get("/json/{scan_id}")
async def export_json_report(scan_id: str, db: AsyncSession = Depends(get_db)):
    target_id = None
    try:
        target_id = int(scan_id)
    except (ValueError, TypeError):
        pass

    scan = None
    if target_id is not None:
        res1 = await db.execute(select(AgentScan).where(AgentScan.id == target_id))
        scan = res1.scalars().first()

    if not scan:
        res_latest = await db.execute(select(AgentScan).order_by(AgentScan.id.desc()))
        scan = res_latest.scalars().first()

    if not scan:
        raise HTTPException(status_code=404, detail="No scans found in database")

    res2 = await db.execute(select(ComplianceCard).where(ComplianceCard.scan_id == scan.id))
    card = res2.scalars().first()

    return {
        "scan": {
            "id": scan.id,
            "agent_name": scan.agent_name,
            "version": scan.version,
            "compliance_score": scan.compliance_score,
            "risk_score": scan.risk_score,
            "risk_tier": scan.risk_tier,
            "llm_providers": scan.llm_providers,
            "tools_detected": scan.tools_detected,
            "data_sources": scan.data_sources,
            "framework_compliance": scan.framework_compliance
        },
        "compliance_card": {
            "agent_purpose": card.agent_purpose if card else "",
            "human_oversight": card.human_oversight if card else "",
            "incident_contact": card.incident_contact if card else "",
            "completeness_score": card.completeness_score if card else 100.0
        }
    }
