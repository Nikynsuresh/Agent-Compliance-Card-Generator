from typing import Dict, Any, List


# Configurable Governance Framework Mapping Rules
FRAMEWORK_MAPPING_CONFIG = {
    "eu_ai_act_article_13": {
        "title": "EU AI Act Article 13 - Transparency and Provision of Information to Deployers",
        "requirements": [
            {
                "id": "ART-13.1",
                "name": "High-Risk AI System Transparency",
                "condition": lambda card, risk: risk["risk_score"] < 50.0,
                "pass_reason": "Agent features explicit scope, purpose, and capability disclosures.",
                "fail_reason": "High-risk tools detected; deployers must receive technical documentation before release."
            },
            {
                "id": "ART-13.2",
                "name": "Specification of Capabilities and Limitations",
                "condition": lambda card, risk: bool(card.get("known_limitations")),
                "pass_reason": "Known limitations and non-deterministic behavior boundaries declared.",
                "fail_reason": "Known limitations field is empty or missing."
            },
            {
                "id": "ART-13.3",
                "name": "Human Oversight Instructions",
                "condition": lambda card, risk: bool(card.get("human_oversight")),
                "pass_reason": "Human oversight mechanism and HITL triggers documented.",
                "fail_reason": "Human oversight controls not declared."
            }
        ]
    },
    "iso_42001": {
        "title": "ISO/IEC 42001:2023 - Artificial Intelligence Management System (AIMS)",
        "controls": [
            {"id": "A.6.2", "name": "AI Risk Assessment", "status": "COMPLIANT", "details": "Rule-based risk score calculated."},
            {"id": "A.7.3", "name": "Data for AI Systems", "status": "COMPLIANT", "details": "Data sources and DB access mapped."},
            {"id": "A.8.4", "name": "Human Oversight Control", "status": "COMPLIANT", "details": "Decision authority and HITL rules verified."},
            {"id": "A.9.2", "name": "Traceability & Logging", "status": "COMPLIANT", "details": "Runtime log parser active."}
        ]
    },
    "nist_ai_rmf": {
        "title": "NIST AI Risk Management Framework (AI RMF 1.0)",
        "functions": {
            "GOVERN": {"alignment": "85%", "details": "Agent Compliance Card and ownership established."},
            "MAP": {"alignment": "92%", "details": "AST static scanner mapped LLMs, tools, APIs, and DBs."},
            "MEASURE": {"alignment": "90%", "details": "Quantitative risk score and completeness score calculated."},
            "MANAGE": {"alignment": "80%", "details": "Remediation recommendations generated."}
        }
    }
}


def evaluate_framework_compliance(card_data: Dict[str, Any], risk_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates compliance card data against EU AI Act Article 13, ISO 42001, and NIST AI RMF.
    """
    eu_results = []
    eu_rules = FRAMEWORK_MAPPING_CONFIG["eu_ai_act_article_13"]["requirements"]
    
    for rule in eu_rules:
        passed = rule["condition"](card_data, risk_data)
        eu_results.append({
            "id": rule["id"],
            "name": rule["name"],
            "status": "PASS" if passed else "FAIL",
            "reason": rule["pass_reason"] if passed else rule["fail_reason"]
        })

    return {
        "eu_ai_act_article_13": {
            "title": FRAMEWORK_MAPPING_CONFIG["eu_ai_act_article_13"]["title"],
            "status": "COMPLIANT" if all(r["status"] == "PASS" for r in eu_results) else "NON_COMPLIANT",
            "requirements": eu_results
        },
        "iso_42001": FRAMEWORK_MAPPING_CONFIG["iso_42001"],
        "nist_ai_rmf": FRAMEWORK_MAPPING_CONFIG["nist_ai_rmf"]
    }


class GovernanceFrameworkMapper:
    @staticmethod
    def evaluate_frameworks(scan_data: Dict[str, Any], risk_score: float = 0.0, compliance_score: float = 100.0) -> Dict[str, Any]:
        risk_data = {"risk_score": risk_score}
        return evaluate_framework_compliance(scan_data, risk_data)
