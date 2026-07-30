from app.services.compliance_engine import ComplianceEngine


def test_evaluate_compliance_completeness_full():
    card = {
        "agent_purpose": "Trading Bot",
        "llm_and_version": "GPT-4o",
        "tool_inventory": [{"name": "trade"}],
        "data_sources": ["SQLite"],
        "decision_authority": "Semi-Autonomous",
        "human_oversight": "Human-in-the-Loop",
        "risk_classification": "Low Risk",
        "known_limitations": ["Requires internet"],
        "incident_contact": "sec@enterprise.com"
    }
    score, missing, warnings = ComplianceEngine.evaluate_compliance_completeness(card)
    assert score == 100.0
    assert len(missing) == 0


def test_evaluate_compliance_completeness_with_placeholder():
    card = {
        "agent_purpose": "TODO: fill this in",
        "llm_and_version": "GPT-4o",
        "tool_inventory": [],
        "data_sources": ["SQLite"],
        "decision_authority": "Autonomous",
        "human_oversight": "None",
        "risk_classification": "Low Risk",
        "known_limitations": [],
        "incident_contact": "sec@enterprise.com"
    }
    score, missing, warnings = ComplianceEngine.evaluate_compliance_completeness(card)
    assert score < 100.0
    assert len(warnings) >= 1
    assert any("agent_purpose" in w for w in warnings)


def test_risk_formula_calculation():
    discovered = {
        "tools_detected": [{"name": "system_exec", "risk": "Critical", "category": "Shell Execution"}],
        "llm_providers": ["OpenAI"],
        "data_sources": ["SQL Database"],
        "autonomous_triggers": ["while True"],
        "human_oversight": "None"
    }
    comp_score, risk_score, risk_tier, breakdown = ComplianceEngine.calculate_scores(discovered, 100.0)
    assert risk_score >= 70.0
    assert risk_tier == "Critical"
    assert comp_score < 60.0
