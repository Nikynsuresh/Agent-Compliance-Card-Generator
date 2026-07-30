from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.compliance_card import ComplianceCard
from app.schemas.schemas import ComplianceCardResponse

router = APIRouter()


@router.get("/{scan_id}", response_model=ComplianceCardResponse)
async def get_compliance_card(scan_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ComplianceCard).where(ComplianceCard.scan_id == scan_id))
    card = result.scalars().first()
    if not card:
        raise HTTPException(status_code=404, detail=f"Compliance card for scan_id {scan_id} not found")

    return {
        "id": card.id,
        "scan_id": card.scan_id,
        "agent_purpose": card.agent_purpose,
        "llm_and_version": card.llm_and_version,
        "tool_inventory": card.tool_inventory or [],
        "data_sources": card.data_sources or [],
        "decision_authority": card.decision_authority or "Autonomous with Thresholds",
        "human_oversight": card.human_oversight or "Human-in-the-Loop",
        "risk_classification": card.risk_classification or "Low Risk",
        "known_limitations": card.known_limitations or [],
        "incident_contact": card.incident_contact or "security@enterprise.com",
        "completeness_score": card.completeness_score,
        "missing_fields": card.missing_fields or [],
        "placeholder_warnings": card.placeholder_warnings or []
    }
