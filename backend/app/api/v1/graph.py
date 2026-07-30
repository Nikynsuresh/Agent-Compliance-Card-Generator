from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.agent_scan import AgentScan
from app.services.graph_builder import build_architecture_graph

router = APIRouter()


@router.get("/{scan_id}")
async def get_agent_graph(scan_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentScan).where(AgentScan.id == scan_id))
    scan = result.scalars().first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    scan_dict = {
        "agent_name": scan.agent_name,
        "framework": scan.framework,
        "risk_tier": scan.risk_tier,
        "llm_providers": scan.llm_providers or [],
        "tools_detected": scan.tools_detected or [],
        "data_sources": scan.data_sources or [],
        "external_apis": scan.external_apis or []
    }

    graph = build_architecture_graph(scan_dict)
    return graph
