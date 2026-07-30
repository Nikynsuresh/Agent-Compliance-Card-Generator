from typing import Dict, Any, List


def calculate_agent_risk(scanned_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rule-based Risk Engine evaluating:
    1. Dangerous shell execution calls (eval, exec, system, popen)
    2. External Internet / API access
    3. Database write & destruction access
    4. Email sending capabilities
    5. Autonomous unbounded loop execution
    6. Sensitive customer data access
    """
    risk_score = 0.0
    risk_factors: List[Dict[str, Any]] = []

    tools = scanned_data.get("tools_detected", [])
    data_sources = scanned_data.get("data_sources", [])
    external_apis = scanned_data.get("external_apis", [])
    email_services = scanned_data.get("email_services", [])
    dangerous_calls = scanned_data.get("dangerous_calls", [])
    autonomous_triggers = scanned_data.get("autonomous_triggers", [])

    # Factor 1: Dangerous System / Shell Execution (+40 Points)
    if dangerous_calls or any(t.get("risk") == "Critical" for t in tools):
        risk_score += 40.0
        risk_factors.append({
            "factor": "Dangerous Shell / System Execution",
            "weight": 40.0,
            "details": f"Detected {len(dangerous_calls)} un-sanitized shell calls (exec, eval, system)."
        })

    # Factor 2: Autonomous Execution Loops (+20 Points)
    if autonomous_triggers:
        risk_score += 20.0
        risk_factors.append({
            "factor": "Unbounded Autonomous Execution",
            "weight": 20.0,
            "details": "Agent contains un-governed continuous loops (`while True`)."
        })

    # Factor 3: Internet & External API Egress (+15 Points)
    if external_apis:
        risk_score += 15.0
        risk_factors.append({
            "factor": "External Internet & REST API Access",
            "weight": 15.0,
            "details": f"Connects to external web services: {', '.join(external_apis)}."
        })

    # Factor 4: Database Write & Deletion (+15 Points)
    if data_sources or any(t.get("category") == "Data Destruction" for t in tools):
        risk_score += 15.0
        risk_factors.append({
            "factor": "Database Write / Modification Access",
            "weight": 15.0,
            "details": f"Connected data sources: {', '.join(data_sources)}."
        })

    # Factor 5: Email Sending Capabilities (+10 Points)
    if email_services or any("email" in t.get("name", "").lower() for t in tools):
        risk_score += 10.0
        risk_factors.append({
            "factor": "Autonomous Email Dispatch",
            "weight": 10.0,
            "details": "Agent can send un-reviewed outbound emails."
        })

    # Cap risk score at 100
    risk_score = min(100.0, risk_score)

    # Risk Tier Categorization
    if risk_score >= 70.0:
        risk_level = "Critical"
    elif risk_score >= 50.0:
        risk_level = "High"
    elif risk_score >= 25.0:
        risk_level = "Medium"
    elif risk_score > 0.0:
        risk_level = "Low"
    else:
        risk_level = "Minimal"

    return {
        "risk_score": round(risk_score, 1),
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "requires_human_in_loop": risk_score >= 40.0
    }
