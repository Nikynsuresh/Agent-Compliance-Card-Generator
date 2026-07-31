import asyncio
import os
import sys
import datetime

# Ensure backend folder is in python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy import select
from app.db.database import init_db, AsyncSessionLocal
from app.models.user import User
from app.models.agent_scan import AgentScan
from app.models.compliance_card import ComplianceCard, CardVersionHistory
from app.core.security import get_password_hash
from app.services.discovery_service import discover_agent_assets
from app.services.compliance_engine import build_compliance_card_payload
from app.services.framework_mapper import GovernanceFrameworkMapper
from app.services.version_service import record_card_version


async def seed_database():
    print("Initializing Agent Compliance Card Generator database...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # 1. Create Admin & Auditor Users if not already present
        res = await db.execute(select(User).where(User.username == "admin"))
        if not res.scalars().first():
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

        # 2. Seed Sample Agents & Version History
        samples = [
            ("finance_agent", "Finance & Trading Agent", "1.0.0"),
            ("customer_support_agent", "Customer Support Bot", "1.0.0"),
            ("high_risk_sql_agent", "Autonomous SQL Agent", "2.1.0")
        ]

        base_samples = os.path.join(os.path.dirname(__file__), "..", "samples")

        for key, name, version in samples:
            existing_scan = await db.execute(select(AgentScan).where(AgentScan.agent_name == name))
            if existing_scan.scalars().first():
                continue

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

                # Baseline Scan V1
                scan_record_v1 = AgentScan(
                    agent_name=name,
                    version="1.0.0",
                    source_type="sample",
                    source_path=sample_dir,
                    framework=discovered.get("framework", "Custom Python"),
                    compliance_score=card_payload["compliance_score"],
                    risk_score=card_payload["risk_score"],
                    risk_tier=card_payload["risk_tier"],
                    llm_providers=discovered.get("llm_providers", ["OpenAI GPT-4o"]),
                    tools_detected=discovered.get("tools_detected", []),
                    data_sources=discovered.get("data_sources", []),
                    external_apis=discovered.get("external_apis", []),
                    framework_compliance=framework_eval,
                    summary=f"Baseline compliance scan (v1.0.0) of {name}."
                )
                db.add(scan_record_v1)
                await db.commit()
                await db.refresh(scan_record_v1)

                card_rec_v1 = ComplianceCard(
                    scan_id=scan_record_v1.id,
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
                db.add(card_rec_v1)
                await db.commit()

                # Record Version 1 in Version History
                await record_card_version(
                    db=db,
                    scan_id=scan_record_v1.id,
                    agent_name=name,
                    version="1.0.0",
                    card_payload=card_payload,
                    risk_score=scan_record_v1.risk_score,
                    compliance_score=scan_record_v1.compliance_score
                )

                # Target Release Scan V2 (Modified with new capabilities & risk delta for realistic diffing)
                v2_payload = dict(card_payload)
                v2_card = dict(card_payload["card"])
                v2_card["llm_and_version"] = "Gemini 2.5 Pro"
                v2_card["human_oversight"] = "Disabled (Autonomous Execution)"
                v2_card["decision_authority"] = "Autonomous Execution"
                v2_card["risk_classification"] = "High Risk"
                v2_tools = list(card_payload["card"]["tool_inventory"]) + [
                    {"name": "Shell Execution Tool", "category": "Code Execution", "risk": "Critical", "description": "Runs arbitrary bash/terminal scripts."}
                ]
                v2_card["tool_inventory"] = v2_tools
                v2_payload["card"] = v2_card
                v2_payload["compliance_score"] = max(40.0, card_payload["compliance_score"] - 12.0)
                v2_payload["risk_score"] = min(95.0, card_payload["risk_score"] + 25.0)
                v2_payload["risk_tier"] = "High"

                scan_record_v2 = AgentScan(
                    agent_name=name,
                    version="2.0.0",
                    source_type="sample",
                    source_path=sample_dir,
                    framework=discovered.get("framework", "Custom Python"),
                    compliance_score=v2_payload["compliance_score"],
                    risk_score=v2_payload["risk_score"],
                    risk_tier="High",
                    llm_providers=["Gemini 2.5 Pro"],
                    tools_detected=v2_tools,
                    data_sources=discovered.get("data_sources", []) + ["Production Postgres Cluster"],
                    external_apis=discovered.get("external_apis", []) + ["https://api.stripe.com/v1/charges"],
                    framework_compliance=framework_eval,
                    summary=f"Release Candidate (v2.0.0) scan of {name} with expanded capabilities."
                )
                db.add(scan_record_v2)
                await db.commit()
                await db.refresh(scan_record_v2)

                card_rec_v2 = ComplianceCard(
                    scan_id=scan_record_v2.id,
                    agent_purpose=v2_card["agent_purpose"],
                    llm_and_version=v2_card["llm_and_version"],
                    tool_inventory=v2_card["tool_inventory"],
                    data_sources=v2_card["data_sources"],
                    decision_authority=v2_card["decision_authority"],
                    human_oversight=v2_card["human_oversight"],
                    risk_classification=v2_card["risk_classification"],
                    known_limitations=v2_card["known_limitations"],
                    incident_contact=v2_card["incident_contact"],
                    completeness_score=85.0,
                    missing_fields=[],
                    placeholder_warnings=[],
                    raw_card_json=v2_payload
                )
                db.add(card_rec_v2)
                await db.commit()

                # Record Version 2 in Version History
                await record_card_version(
                    db=db,
                    scan_id=scan_record_v2.id,
                    agent_name=name,
                    version="2.0.0",
                    card_payload=v2_payload,
                    risk_score=scan_record_v2.risk_score,
                    compliance_score=scan_record_v2.compliance_score
                )

                print(f"Seeded agent: {name} (V1 Score: {scan_record_v1.compliance_score}%, V2 Score: {scan_record_v2.compliance_score}%)")

    print("Database seeding completed successfully with multi-version history.")


if __name__ == "__main__":
    asyncio.run(seed_database())
