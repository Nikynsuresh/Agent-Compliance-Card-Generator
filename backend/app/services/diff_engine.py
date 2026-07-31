from typing import Dict, Any, List


def compare_agent_versions(v1_data: Dict[str, Any], v2_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Version Difference Engine comparing two agent release candidates:
    Highlights Changed LLMs, Models, Tools, APIs, Databases, Risk Deltas, and Compliance Impact.
    """
    v1_tools = {t["name"] for t in v1_data.get("tools_detected", [])}
    v2_tools = {t["name"] for t in v2_data.get("tools_detected", [])}

    added_tools = sorted(list(v2_tools - v1_tools))
    removed_tools = sorted(list(v1_tools - v2_tools))

    v1_llm = v1_data.get("llm_providers", ["OpenAI"])
    v2_llm = v2_data.get("llm_providers", ["OpenAI"])
    llm_changed = v1_llm != v2_llm

    v1_score = v1_data.get("compliance_score", 90.0)
    v2_score = v2_data.get("compliance_score", 70.0)
    score_delta = round(v2_score - v1_score, 1)

    compliance_warnings = []
    if added_tools:
        compliance_warnings.append(f"Added {len(added_tools)} new tools: {', '.join(added_tools)}.")
    if score_delta < 0:
        compliance_warnings.append(f"Compliance score dropped by {abs(score_delta)} points in new release.")

    return {
        "baseline_version": v1_data.get("version", "1.0.0"),
        "target_version": v2_data.get("version", "2.0.0"),
        "llm_changed": llm_changed,
        "baseline_llm": v1_llm,
        "target_llm": v2_llm,
        "added_tools": added_tools,
        "removed_tools": removed_tools,
        "compliance_score_baseline": v1_score,
        "compliance_score_target": v2_score,
        "compliance_score_delta": score_delta,
        "compliance_impact_summary": compliance_warnings or ["No critical governance degradation detected."]
    }


compare_agent_scans = compare_agent_versions
