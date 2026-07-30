from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.agent_scan import AgentScan
from app.schemas.schemas import DiffRequest, DiffResponse
from app.services.diff_engine import compare_agent_scans

router = APIRouter()


@router.post("/compare", response_model=DiffResponse)
async def compare_scans(payload: DiffRequest, db: AsyncSession = Depends(get_db)):
    res1 = await db.execute(select(AgentScan).where(AgentScan.id == payload.scan_id_v1))
    v1 = res1.scalars().first()

    res2 = await db.execute(select(AgentScan).where(AgentScan.id == payload.scan_id_v2))
    v2 = res2.scalars().first()

    if not v1 or not v2:
        raise HTTPException(status_code=404, detail="One or both scan IDs not found for comparison")

    v1_dict = {
        "agent_name": v1.agent_name,
        "version": v1.version,
        "compliance_score": v1.compliance_score,
        "risk_score": v1.risk_score,
        "tools_detected": v1.tools_detected or [],
        "llm_providers": v1.llm_providers or [],
        "data_sources": v1.data_sources or []
    }

    v2_dict = {
        "agent_name": v2.agent_name,
        "version": v2.version,
        "compliance_score": v2.compliance_score,
        "risk_score": v2.risk_score,
        "tools_detected": v2.tools_detected or [],
        "llm_providers": v2.llm_providers or [],
        "data_sources": v2.data_sources or []
    }

    diff_result = compare_agent_scans(v1_dict, v2_dict)
    return diff_result
