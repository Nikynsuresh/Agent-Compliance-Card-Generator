import asyncio
import os
import sys

# Ensure backend folder is in python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.db.database import init_db, AsyncSessionLocal
from app.models.user import User
from app.models.agent_scan import AgentScan
from app.models.compliance_card import ComplianceCard
from app.core.security import get_password_hash
from app.services.discovery_service import discover_agent_assets
from app.services.compliance_engine import build_compliance_card_payload
from app.services.framework_mapper import GovernanceFrameworkMapper


async def seed_database():
    print("Initializing Agent Compliance Card Generator database...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # 1. Create Admin & Auditor Users
        admin_user = User(
            username="admin",
            email="admin@agentcompliance.ai",
            hashed_password=get_password_hash("admin123"),
            full_name="Enterprise Admin",
            role="Admin"
        )
        auditor_user = User(
            username="auditor",
            email="auditor@agentcompliance.ai",
            hashed_password=get_password_hash("auditor123"),
            full_name="Lead AI Auditor",
            role="Auditor"
        )
        db.add(admin_user)
        db.add(auditor_user)
        await db.commit()

        # 2. Seed Sample Agents
        samples = [
            ("finance_agent", "Finance & Trading Agent", "1.4.0"),
            ("customer_support_agent", "Customer Support Bot", "1.0.0"),
            ("high_risk_sql_agent", "Autonomous SQL Agent", "2.1.0-alpha")
        ]

        base_samples = os.path.join(os.path.dirname(__file__), "..", "samples")

        for key, name, version in samples:
            sample_dir = os.path.join(base_samples, key)
            if os.path.exists(sample_dir):
                discovered = discover_agent_assets(sample_dir)
                discovered["agent_name"] = name
                discovered["version"] = version
                
                card_payload = build_compliance_card_payload(discovered)
                framework_eval = GovernanceFrameworkMapper.evaluate_frameworks(
                    scan_data=discovered,
                    risk_score=card_payload["risk_score"],
                    compliance_score=card_payload["compliance_score"]
                )

                scan_record = AgentScan(
                    agent_name=name,
                    version=version,
                    source_type="sample",
                    source_path=sample_dir,
                    framework=discovered.get("framework", "Custom Python"),
                    compliance_score=card_payload["compliance_score"],
                    risk_score=card_payload["risk_score"],
                    risk_tier=card_payload["risk_tier"],
                    llm_providers=discovered.get("llm_providers", []),
                    tools_detected=discovered.get("tools_detected", []),
                    data_sources=discovered.get("data_sources", []),
                    external_apis=discovered.get("external_apis", []),
                    framework_compliance=framework_eval,
                    summary=f"Automated compliance scan of {name}."
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

                print(f"Seeded agent: {name} (Compliance Score: {card_payload['compliance_score']}%, Risk Tier: {card_payload['risk_tier']})")

    print("Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_database())
