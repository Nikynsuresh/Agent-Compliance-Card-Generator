import datetime
from typing import Dict, Any, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.compliance_card import CardVersionHistory
from app.models.agent_scan import AgentScan


async def record_card_version(
    db: AsyncSession,
    scan_id: int,
    agent_name: str,
    version: str,
    card_payload: Dict[str, Any],
    risk_score: float,
    compliance_score: float
) -> CardVersionHistory:
    """
    Saves every Compliance Card as an immutable version history entry.
    Calculates incremental version numbers (Version 1, Version 2, Version 3...) per agent_name.
    """
    # Count existing versions for this agent_name
    res = await db.execute(
        select(func.count(CardVersionHistory.id)).where(CardVersionHistory.agent_name == agent_name)
    )
    count = res.scalar() or 0
    next_v_num = count + 1

    version_record = CardVersionHistory(
        scan_id=scan_id,
        agent_name=agent_name,
        version=version,
        version_number=next_v_num,
        compliance_card_json=card_payload,
        risk_score=risk_score,
        compliance_score=compliance_score,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(version_record)
    await db.commit()
    await db.refresh(version_record)
    return version_record
