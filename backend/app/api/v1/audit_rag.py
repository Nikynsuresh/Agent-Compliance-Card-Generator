from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.agent_scan import AgentScan
from app.schemas.schemas import AuditQueryRequest, AuditQueryResponse
from app.services.rag_audit_service import AuditRAGService

router = APIRouter()


@router.post("/chat", response_model=AuditQueryResponse)
async def audit_chat(payload: AuditQueryRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentScan).where(AgentScan.id == payload.scan_id))
    scan = result.scalars().first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan ID not found")

    scan_dict = {
        "agent_name": scan.agent_name,
        "framework": scan.framework,
        "compliance_score": scan.compliance_score,
        "risk_score": scan.risk_score,
        "risk_tier": scan.risk_tier,
        "llm_providers": scan.llm_providers or [],
        "tools_detected": scan.tools_detected or [],
        "data_sources": scan.data_sources or [],
        "external_apis": scan.external_apis or [],
        "human_oversight": "Human-in-the-Loop Required",
        "summary": scan.summary or ""
    }

    response = AuditRAGService.query_agent_audit(scan_dict, payload.question)
    return response
