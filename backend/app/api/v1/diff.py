from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db.database import get_db
from app.models.agent_scan import AgentScan
from app.models.compliance_card import ComplianceCard, CardVersionHistory
from app.services.diff_engine import compare_compliance_cards
from app.services.pdf_exporter import generate_diff_pdf

router = APIRouter()


class CompareRequest(BaseModel):
    v1_id: Optional[int] = None
    v2_id: Optional[int] = None
    scan_id_v1: Optional[int] = None
    scan_id_v2: Optional[int] = None


@router.get("/versions")
async def list_all_versions(db: AsyncSession = Depends(get_db)):
    """Lists all stored compliance card versions across all agents."""
    result = await db.execute(select(CardVersionHistory).order_by(CardVersionHistory.timestamp.desc()))
    versions = result.scalars().all()
    
    # If version history table is empty, construct from agent scans
    if not versions:
        scans_res = await db.execute(select(AgentScan).order_by(AgentScan.created_at.desc()))
        scans = scans_res.scalars().all()
        response = []
        for s in scans:
            response.append({
                "id": s.id,
                "scan_id": s.id,
                "agent_name": s.agent_name,
                "version": s.version,
                "version_number": 1,
                "timestamp": s.created_at.isoformat() if s.created_at else "",
                "risk_score": s.risk_score,
                "compliance_score": s.compliance_score
            })
        return response

    return [{
        "id": v.id,
        "scan_id": v.scan_id,
        "agent_name": v.agent_name,
        "version": v.version,
        "version_number": v.version_number,
        "timestamp": v.timestamp.isoformat() if v.timestamp else "",
        "risk_score": v.risk_score,
        "compliance_score": v.compliance_score
    } for v in versions]


@router.get("/versions/{agent_name}")
async def list_agent_versions(agent_name: str, db: AsyncSession = Depends(get_db)):
    """Lists recorded version history for a specific agent name."""
    result = await db.execute(
        select(CardVersionHistory)
        .where(CardVersionHistory.agent_name == agent_name)
        .order_by(CardVersionHistory.version_number.asc())
    )
    versions = result.scalars().all()
    return [{
        "id": v.id,
        "scan_id": v.scan_id,
        "agent_name": v.agent_name,
        "version": v.version,
        "version_number": v.version_number,
        "timestamp": v.timestamp.isoformat() if v.timestamp else "",
        "risk_score": v.risk_score,
        "compliance_score": v.compliance_score
    } for v in versions]


@router.post("/compare")
async def compare_versions(payload: CompareRequest, db: AsyncSession = Depends(get_db)):
    """
    Compares two compliance card versions (by CardVersionHistory ID or AgentScan ID).
    Executes in under 1 second.
    """
    v1_card_json = {}
    v2_card_json = {}
    v1_meta = {}
    v2_meta = {}

    v1_id = payload.v1_id or payload.scan_id_v1
    v2_id = payload.v2_id or payload.scan_id_v2

    # Fetch Version 1
    if payload.v1_id:
        res1 = await db.execute(select(CardVersionHistory).where(CardVersionHistory.id == payload.v1_id))
        v1_rec = res1.scalars().first()
        if v1_rec:
            v1_card_json = v1_rec.compliance_card_json or {}
            v1_meta = {
                "agent_name": v1_rec.agent_name,
                "version": f"v{v1_rec.version} (Ver {v1_rec.version_number})",
                "risk_score": v1_rec.risk_score,
                "compliance_score": v1_rec.compliance_score
            }
    if not v1_card_json and v1_id:
        res1_scan = await db.execute(select(AgentScan).where(AgentScan.id == v1_id))
        s1 = res1_scan.scalars().first()
        if s1:
            res1_card = await db.execute(select(ComplianceCard).where(ComplianceCard.scan_id == v1_id))
            c1 = res1_card.scalars().first()
            v1_card_json = c1.raw_card_json if c1 else {}
            v1_meta = {
                "agent_name": s1.agent_name,
                "version": f"v{s1.version}",
                "risk_score": s1.risk_score,
                "compliance_score": s1.compliance_score,
                "risk_tier": s1.risk_tier,
                "tools_detected": s1.tools_detected,
                "data_sources": s1.data_sources,
                "llm_providers": s1.llm_providers
            }

    # Fetch Version 2
    if payload.v2_id:
        res2 = await db.execute(select(CardVersionHistory).where(CardVersionHistory.id == payload.v2_id))
        v2_rec = res2.scalars().first()
        if v2_rec:
            v2_card_json = v2_rec.compliance_card_json or {}
            v2_meta = {
                "agent_name": v2_rec.agent_name,
                "version": f"v{v2_rec.version} (Ver {v2_rec.version_number})",
                "risk_score": v2_rec.risk_score,
                "compliance_score": v2_rec.compliance_score
            }
    if not v2_card_json and v2_id:
        res2_scan = await db.execute(select(AgentScan).where(AgentScan.id == v2_id))
        s2 = res2_scan.scalars().first()
        if s2:
            res2_card = await db.execute(select(ComplianceCard).where(ComplianceCard.scan_id == v2_id))
            c2 = res2_card.scalars().first()
            v2_card_json = c2.raw_card_json if c2 else {}
            v2_meta = {
                "agent_name": s2.agent_name,
                "version": f"v{s2.version}",
                "risk_score": s2.risk_score,
                "compliance_score": s2.compliance_score,
                "risk_tier": s2.risk_tier,
                "tools_detected": s2.tools_detected,
                "data_sources": s2.data_sources,
                "llm_providers": s2.llm_providers
            }

    # Fallback to default demo comparison if no IDs provided
    if not v1_card_json or not v2_card_json:
        all_v = await db.execute(select(CardVersionHistory).order_by(CardVersionHistory.id.asc()))
        records = all_v.scalars().all()
        if len(records) >= 2:
            v1_rec, v2_rec = records[0], records[-1]
            v1_card_json = v1_rec.compliance_card_json
            v1_meta = {"agent_name": v1_rec.agent_name, "version": f"v{v1_rec.version}", "risk_score": v1_rec.risk_score, "compliance_score": v1_rec.compliance_score}
            v2_card_json = v2_rec.compliance_card_json
            v2_meta = {"agent_name": v2_rec.agent_name, "version": f"v{v2_rec.version}", "risk_score": v2_rec.risk_score, "compliance_score": v2_rec.compliance_score}

    return compare_compliance_cards(v1_card_json, v2_card_json, v1_meta, v2_meta)


def safe_int(val: Any, default: int) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


@router.get("/export/pdf")
async def export_diff_pdf(v1_id: Optional[str] = Query("1"), v2_id: Optional[str] = Query("2"), db: AsyncSession = Depends(get_db)):
    """Exports comparison results as a downloadable PDF report."""
    id1 = safe_int(v1_id, 1)
    id2 = safe_int(v2_id, 2)
    diff_data = await compare_versions(CompareRequest(v1_id=id1, v2_id=id2), db)
    pdf_bytes = generate_diff_pdf(diff_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Card_Diff_{id1}_vs_{id2}.pdf"}
    )


@router.get("/export/json")
async def export_diff_json(v1_id: Optional[str] = Query("1"), v2_id: Optional[str] = Query("2"), db: AsyncSession = Depends(get_db)):
    """Exports comparison results as JSON."""
    id1 = safe_int(v1_id, 1)
    id2 = safe_int(v2_id, 2)
    diff_data = await compare_versions(CompareRequest(v1_id=id1, v2_id=id2), db)
    return diff_data


@router.get("/export/html")
async def export_diff_html(v1_id: Optional[str] = Query("1"), v2_id: Optional[str] = Query("2"), db: AsyncSession = Depends(get_db)):
    """Exports comparison results as standalone interactive HTML diff report."""
    id1 = safe_int(v1_id, 1)
    id2 = safe_int(v2_id, 2)
    diff_data = await compare_versions(CompareRequest(v1_id=id1, v2_id=id2), db)
    
    rows_html = ""
    for r in diff_data.get("diff_table", []):
        sev_color = "#ef4444" if r.get("severity") == "CRITICAL" else "#f59e0b" if r.get("severity") == "HIGH" else "#3b82f6" if r.get("severity") == "MEDIUM" else "#10b981"
        rows_html += f"""
        <tr>
            <td style="padding:10px; border-bottom:1px solid #e2e8f0; font-weight:bold;">{r.get('field')}</td>
            <td style="padding:10px; border-bottom:1px solid #e2e8f0; color:#64748b;">{r.get('old_value')}</td>
            <td style="padding:10px; border-bottom:1px solid #e2e8f0; font-weight:bold;">{r.get('new_value')}</td>
            <td style="padding:10px; border-bottom:1px solid #e2e8f0;"><span style="background:#f1f5f9; padding:3px 8px; border-radius:4px; font-size:12px;">{r.get('status')}</span></td>
            <td style="padding:10px; border-bottom:1px solid #e2e8f0; color:{sev_color}; font-weight:bold;">{r.get('severity')}</td>
            <td style="padding:10px; border-bottom:1px solid #e2e8f0;">{r.get('framework')}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Compliance Card Diff: {diff_data.get('agent_name')}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; background:#f8fafc; color:#0f172a; }}
            .card {{ background: white; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
            h1 {{ margin-top: 0; color: #1e293b; }}
            .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
            .box {{ background: #f1f5f9; padding: 15px; border-radius: 8px; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ text-align: left; background: #e2e8f0; padding: 10px; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Agent Compliance Card Diff: {diff_data.get('agent_name')}</h1>
            <p>Baseline <b>{diff_data.get('baseline_version')}</b> vs Target <b>{diff_data.get('target_version')}</b></p>
            
            <div class="grid">
                <div class="box">Compliance Score: {diff_data.get('compliance_score_baseline')}% &rarr; {diff_data.get('compliance_score_target')}% ({diff_data.get('compliance_score_delta')}%)</div>
                <div class="box">Security Risk: {diff_data.get('risk_score_baseline')} &rarr; {diff_data.get('risk_score_target')} ({diff_data.get('overall_status')})</div>
                <div class="box">Fields Changed: {diff_data.get('fields_changed_count')} ({diff_data.get('critical_changes_count')} Critical)</div>
                <div class="box">Frameworks Impacted: {diff_data.get('frameworks_impacted_count')}</div>
            </div>

            <div style="background:#eff6ff; padding:15px; border-radius:8px; border-left:4px solid #3b82f6; margin-bottom:20px;">
                <strong>AI Executive Auditor Summary:</strong><br/>
                <em>"{diff_data.get('ai_explanation')}"</em>
            </div>

            <table>
                <thead>
                    <tr><th>Field</th><th>Old Value</th><th>New Value</th><th>Status</th><th>Severity</th><th>Framework</th></tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return Response(content=html_content, media_type="text/html")
