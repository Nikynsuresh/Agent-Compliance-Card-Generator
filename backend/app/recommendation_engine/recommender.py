from typing import Dict, Any, List


def generate_ai_recommendations(scanned_data: Dict[str, Any], risk_data: Dict[str, Any], security_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    AI Recommendation Engine producing itemized recommendations:
    Problem, Reason, Priority, Suggested Fix, Example Implementation.
    """
    recommendations: List[Dict[str, Any]] = []

    tools = scanned_data.get("tools_detected", [])
    dangerous_ops = scanned_data.get("dangerous_operations", [])

    # Recommendation 1: Shell Execution
    if dangerous_ops or any(t.get("risk") == "Critical" for t in tools):
        recommendations.append({
            "problem": "Un-sanitized Shell / System Exec Tools",
            "reason": "Direct execution of shell commands (`os.system`, `exec`) risks remote code execution.",
            "priority": "P0 - CRITICAL",
            "suggested_fix": "Encapsulate execution in a Docker sandbox container with strict RPC permissions.",
            "example_implementation": """# Secure Sandbox Tool Wrapper
@tool
def execute_sandboxed_command(cmd_args: list[str]) -> str:
    # Run in isolated container without shell=True
    result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=10)
    return result.stdout"""
        })

    # Recommendation 2: Missing Human Oversight
    if risk_data.get("risk_score", 0) >= 40.0:
        recommendations.append({
            "problem": "Un-governed High-Risk Tool Invocation",
            "reason": "High-risk database/API actions execute autonomously without human approval.",
            "priority": "P1 - HIGH",
            "suggested_fix": "Implement a Human-in-the-Loop (HITL) confirmation step before executing high-risk operations.",
            "example_implementation": """# Human Approval Intercept
if tool.risk_level == "High":
    approval = request_human_approval(action=tool.name, params=kwargs)
    if not approval.granted:
        raise PermissionError("Human supervisor rejected tool execution.")"""
        })

    # Recommendation 3: SAST Hardcoded Secrets
    if security_data.get("total_findings", 0) > 0:
        recommendations.append({
            "problem": "Hardcoded Secrets / Security Vulnerabilities",
            "reason": f"Detected {security_data['total_findings']} security issues in static code audit.",
            "priority": "P1 - HIGH",
            "suggested_fix": "Extract all API credentials into environment variables or Secret Manager.",
            "example_implementation": "api_key = os.getenv('OPENAI_API_KEY')"
        })

    return recommendations
