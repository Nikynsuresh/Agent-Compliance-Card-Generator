from typing import Dict, Any, List
from app.services.risk_engine import calculate_agent_risk


MANDATORY_CARD_FIELDS = [
    "agent_name", "agent_purpose", "scope", "owner", "llm_name", "llm_version",
    "tool_inventory", "tool_operations", "data_sources", "database_access",
    "external_apis", "decision_authority", "human_oversight",
    "risk_classification", "known_limitations", "incident_contact"
]


def generate_compliance_card(scanned_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a structured 16-field Enterprise AI Agent Compliance Card,
    runs Completeness Warnings, and computes mathematical compliance score (0-100%).
    """
    risk_res = calculate_agent_risk(scanned_data)

    agent_name = scanned_data.get("agent_name", "Enterprise AI Agent")
    agent_purpose = scanned_data.get("agent_purpose", "Automated enterprise task processing agent")
    scope = scanned_data.get("scope", "Production Enterprise Infrastructure")
    owner = scanned_data.get("owner", "AI Governance Committee / SecOps")
    
    llms = scanned_data.get("llm_providers", ["OpenAI"])
    llm_name = ", ".join(llms) if llms else "OpenAI GPT-4o"
    llm_versions = scanned_data.get("llm_versions", ["GPT-4o"])
    llm_version = ", ".join(llm_versions) if llm_versions else "GPT-4o (2024-05-13)"

    tools = scanned_data.get("tools_detected", [])
    tool_inventory = [t.get("name") for t in tools]
    tool_operations = [f"{t.get('name')}: {t.get('category')} ({t.get('risk')} Risk)" for t in tools]

    data_sources = scanned_data.get("data_sources", ["Application Context Memory"])
    vector_dbs = scanned_data.get("vector_dbs", [])
    database_access = ", ".join(data_sources + vector_dbs)

    external_apis = scanned_data.get("external_apis", ["External HTTP Services"])
    decision_authority = "Semi-Autonomous with Policy Guardrails" if risk_res["risk_score"] < 50 else "High-Risk Autonomous Execution"
    human_oversight = "Mandatory Human-in-the-Loop Approval Required" if risk_res["requires_human_in_loop"] else "Automated Monitoring with Audit Logs"
    
    risk_classification = f"{risk_res['risk_level']} Risk ({risk_res['risk_score']}/100)"
    known_limitations = ["Non-deterministic LLM responses", "Requires rate-limiting on external API calls"]
    incident_contact = scanned_data.get("incident_contact", "security-operations@enterprise.com")

    card = {
        "agent_name": agent_name,
        "agent_purpose": agent_purpose,
        "scope": scope,
        "owner": owner,
        "llm_name": llm_name,
        "llm_version": llm_version,
        "tool_inventory": tool_inventory,
        "tool_operations": tool_operations,
        "data_sources": data_sources,
        "database_access": database_access,
        "external_apis": external_apis,
        "decision_authority": decision_authority,
        "human_oversight": human_oversight,
        "risk_classification": risk_classification,
        "known_limitations": known_limitations,
        "incident_contact": incident_contact,
        "llm_and_version": f"{llm_name} ({llm_version})"
    }

    # Completeness Checker
    warnings = []
    missing_fields = []
    completed_count = 0

    for field in MANDATORY_CARD_FIELDS:
        val = card.get(field)
        if not val or val == "" or val == [] or "TODO" in str(val) or "FILL_ME" in str(val):
            missing_fields.append(field)
            warnings.append(f"Missing or placeholder value detected in field '{field}'")
        else:
            completed_count += 1

    if risk_res["risk_score"] >= 50.0:
        warnings.append("High risk execution tools present without explicit sandbox verification.")

    completeness_score = round((completed_count / len(MANDATORY_CARD_FIELDS)) * 100, 1)
    overall_compliance_score = round(max(0.0, completeness_score - (risk_res["risk_score"] * 0.3)), 1)

    return {
        "card": card,
        "completeness_score": completeness_score,
        "compliance_score": overall_compliance_score,
        "overall_compliance_score": overall_compliance_score,
        "risk_score": risk_res["risk_score"],
        "risk_tier": risk_res["risk_level"],
        "risk_summary": risk_res,
        "missing_fields": missing_fields,
        "completeness_warnings": warnings,
        "placeholder_warnings": warnings,
        "scoring_explanation": f"Base completeness score of {completeness_score}% adjusted by risk deduction of {round(risk_res['risk_score'] * 0.3, 1)} points."
    }

# Alias for backwards compatibility with scans.py router
build_compliance_card_payload = generate_compliance_card
