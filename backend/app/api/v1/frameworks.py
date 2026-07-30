from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.agent_scan import AgentScan

router = APIRouter()


@router.get("/{scan_id}")
async def get_framework_evaluation(scan_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentScan).where(AgentScan.id == scan_id))
    scan = result.scalars().first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return scan.framework_compliance or {}
