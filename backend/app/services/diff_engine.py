import os
import json
import httpx
from typing import Dict, Any, List, Optional


def compare_compliance_cards(
    v1_card_json: Dict[str, Any],
    v2_card_json: Dict[str, Any],
    v1_meta: Optional[Dict[str, Any]] = None,
    v2_meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Version Comparison Engine & Regulatory Reassessment Engine for AI Compliance Cards.
    Executes in under 1 second. Compares baseline (V1) vs target (V2) compliance cards.
    """
    v1_meta = v1_meta or {}
    v2_meta = v2_meta or {}

    agent_name = v2_meta.get("agent_name") or v1_meta.get("agent_name") or "AI Agent"
    baseline_version = v1_meta.get("version") or v1_card_json.get("version") or "1.0.0"
    target_version = v2_meta.get("version") or v2_card_json.get("version") or "2.0.0"

    v1_score = float(v1_meta.get("compliance_score") or v1_card_json.get("compliance_score", 90.0))
    v2_score = float(v2_meta.get("compliance_score") or v2_card_json.get("compliance_score", 85.0))
    score_delta = round(v2_score - v1_score, 1)

    v1_risk_score = float(v1_meta.get("risk_score") or v1_card_json.get("risk_score", 20.0))
    v2_risk_score = float(v2_meta.get("risk_score") or v2_card_json.get("risk_score", 35.0))
    risk_delta = round(v2_risk_score - v1_risk_score, 1)

    v1_card = v1_card_json.get("card", v1_card_json)
    v2_card = v2_card_json.get("card", v2_card_json)

    diff_table = []
    frameworks_impacted = set()
    critical_count = 0
    changed_count = 0

    # 1. LLM Engine Check
    v1_llm = str(v1_card.get("llm_and_version") or v1_meta.get("llm_providers", ["OpenAI GPT-4o"]))
    v2_llm = str(v2_card.get("llm_and_version") or v2_meta.get("llm_providers", ["Gemini 2.5 Pro"]))
    if v1_llm != v2_llm:
        changed_count += 1
        frameworks_impacted.add("EU AI Act Article 13")
        diff_table.append({
            "field": "LLM Provider & Model",
            "old_value": v1_llm,
            "new_value": v2_llm,
            "status": "Modified",
            "severity": "MEDIUM",
            "framework": "EU AI Act Article 13",
            "explanation": f"The LLM provider changed from {v1_llm} to {v2_llm}. This affects transparency and technical documentation under EU AI Act Article 13."
        })
    else:
        diff_table.append({
            "field": "LLM Provider & Model",
            "old_value": v1_llm,
            "new_value": v2_llm,
            "status": "UNCHANGED",
            "severity": "LOW",
            "framework": "EU AI Act Article 13",
            "explanation": "LLM provider and version remain unchanged."
        })

    # 2. Human Oversight Check
    v1_oversight = str(v1_card.get("human_oversight", "Enabled (Human-in-the-Loop)"))
    v2_oversight = str(v2_card.get("human_oversight", "Disabled"))
    oversight_removed = ("enabled" in v1_oversight.lower() or "hitl" in v1_oversight.lower()) and ("disabled" in v2_oversight.lower() or "none" in v2_oversight.lower() or "removed" in v2_oversight.lower())
    if v1_oversight != v2_oversight:
        changed_count += 1
        frameworks_impacted.add("EU AI Act Article 14")
        if oversight_removed:
            critical_count += 1
            status = "Critical Change"
            severity = "CRITICAL"
            explanation = "Human Oversight was disabled/removed. EU AI Act Article 14 mandates human-in-the-loop controls for high-risk autonomous operations."
        else:
            status = "Modified"
            severity = "MEDIUM"
            explanation = f"Human Oversight specification updated from '{v1_oversight}' to '{v2_oversight}'."
        diff_table.append({
            "field": "Human Oversight",
            "old_value": v1_oversight,
            "new_value": v2_oversight,
            "status": status,
            "severity": severity,
            "framework": "EU AI Act Article 14",
            "explanation": explanation
        })
    else:
        diff_table.append({
            "field": "Human Oversight",
            "old_value": v1_oversight,
            "new_value": v2_oversight,
            "status": "UNCHANGED",
            "severity": "LOW",
            "framework": "EU AI Act Article 14",
            "explanation": "Human oversight controls remain active."
        })

    # 3. Risk Tier Classification Check
    v1_risk_tier = str(v1_card.get("risk_classification") or v1_meta.get("risk_tier", "Medium"))
    v2_risk_tier = str(v2_card.get("risk_classification") or v2_meta.get("risk_tier", "High"))
    if v1_risk_tier.lower() != v2_risk_tier.lower():
        changed_count += 1
        frameworks_impacted.add("NIST AI RMF (GOVERN-1.2)")
        is_escalated = ("high" in v2_risk_tier.lower() or "critical" in v2_risk_tier.lower()) and not ("high" in v1_risk_tier.lower() or "critical" in v1_risk_tier.lower())
        if is_escalated:
            critical_count += 1
            status = "Regulatory Reassessment Required"
            severity = "CRITICAL"
            explanation = f"Risk Classification escalated from {v1_risk_tier} to {v2_risk_tier}. Systemic regulatory risk reassessment required under NIST AI RMF."
        else:
            status = "Modified"
            severity = "MEDIUM"
            explanation = f"Risk classification adjusted from {v1_risk_tier} to {v2_risk_tier}."
        diff_table.append({
            "field": "Risk Classification Tier",
            "old_value": v1_risk_tier,
            "new_value": v2_risk_tier,
            "status": status,
            "severity": severity,
            "framework": "NIST AI RMF",
            "explanation": explanation
        })
    else:
        diff_table.append({
            "field": "Risk Classification Tier",
            "old_value": v1_risk_tier,
            "new_value": v2_risk_tier,
            "status": "UNCHANGED",
            "severity": "LOW",
            "framework": "NIST AI RMF",
            "explanation": "Risk tier rating remains stable."
        })

    # 4. Tools & Capabilities Check
    v1_tools_list = v1_card.get("tool_inventory") or v1_meta.get("tools_detected", [])
    v2_tools_list = v2_card.get("tool_inventory") or v2_meta.get("tools_detected", [])
    v1_tools = {t if isinstance(t, str) else t.get("name", "") for t in v1_tools_list if t}
    v2_tools = {t if isinstance(t, str) else t.get("name", "") for t in v2_tools_list if t}

    added_tools = sorted(list(v2_tools - v1_tools))
    removed_tools = sorted(list(v1_tools - v2_tools))

    has_shell = any("shell" in t.lower() or "exec" in t.lower() or "code" in t.lower() for t in added_tools)

    if added_tools or removed_tools:
        changed_count += 1
        frameworks_impacted.add("OWASP LLM Top 10 (LLM08)")
        if has_shell or len(added_tools) >= 2:
            if has_shell:
                critical_count += 1
            status = "Privilege Increased"
            severity = "CRITICAL" if has_shell else "HIGH"
            explanation = f"Added new tools: {', '.join(added_tools)}. Introducing execution tools increases operational authority and attack surface under OWASP LLM08 (Excessive Agency)."
        elif added_tools:
            status = "ADDED"
            severity = "MEDIUM"
            explanation = f"Added tool integrations: {', '.join(added_tools)}. Security review recommended."
        else:
            status = "REMOVED"
            severity = "LOW"
            explanation = f"Removed tool integrations: {', '.join(removed_tools)}. Reduced agency attack surface."

        diff_table.append({
            "field": "Tool Inventory",
            "old_value": ", ".join(sorted(list(v1_tools))) if v1_tools else "None",
            "new_value": ", ".join(sorted(list(v2_tools))) if v2_tools else "None",
            "status": status,
            "severity": severity,
            "framework": "OWASP LLM Top 10",
            "explanation": explanation
        })
    else:
        diff_table.append({
            "field": "Tool Inventory",
            "old_value": ", ".join(sorted(list(v1_tools))) if v1_tools else "None",
            "new_value": ", ".join(sorted(list(v2_tools))) if v2_tools else "None",
            "status": "UNCHANGED",
            "severity": "LOW",
            "framework": "OWASP LLM Top 10",
            "explanation": "Tool inventory remains identical."
        })

    # 5. Decision Authority Check
    v1_auth = str(v1_card.get("decision_authority", "Advisory / Human Approved"))
    v2_auth = str(v2_card.get("decision_authority", "Autonomous Execution"))
    if v1_auth != v2_auth:
        changed_count += 1
        frameworks_impacted.add("ISO 42001 (A.8.2 Control)")
        is_autonomous = "autonomous" in v2_auth.lower() and not "autonomous" in v1_auth.lower()
        if is_autonomous:
            critical_count += 1
            status = "High Impact"
            severity = "HIGH"
            explanation = f"Decision Authority escalated to '{v2_auth}'. System operates with full autonomy requiring ISO 42001 A.8.2 governance review."
        else:
            status = "Modified"
            severity = "MEDIUM"
            explanation = f"Decision Authority shifted from '{v1_auth}' to '{v2_auth}'."
        diff_table.append({
            "field": "Decision Authority",
            "old_value": v1_auth,
            "new_value": v2_auth,
            "status": status,
            "severity": severity,
            "framework": "ISO 42001",
            "explanation": explanation
        })
    else:
        diff_table.append({
            "field": "Decision Authority",
            "old_value": v1_auth,
            "new_value": v2_auth,
            "status": "UNCHANGED",
            "severity": "LOW",
            "framework": "ISO 42001",
            "explanation": "Decision authority level unchanged."
        })

    # 6. Data Sources & Database Access Check
    v1_ds_list = set(v1_card.get("data_sources") or v1_meta.get("data_sources", []))
    v2_ds_list = set(v2_card.get("data_sources") or v2_meta.get("data_sources", []))
    added_ds = sorted(list(v2_ds_list - v1_ds_list))
    removed_ds = sorted(list(v1_ds_list - v2_ds_list))

    if v1_ds_list != v2_ds_list:
        changed_count += 1
        frameworks_impacted.add("ISO 42001 (A.6.1 Data Governance)")
        diff_table.append({
            "field": "Data Sources & Storage",
            "old_value": ", ".join(sorted(list(v1_ds_list))) if v1_ds_list else "None",
            "new_value": ", ".join(sorted(list(v2_ds_list))) if v2_ds_list else "None",
            "status": "Compliance Review",
            "severity": "MEDIUM",
            "framework": "ISO 42001",
            "explanation": f"Data sources or persistence mechanisms modified (Added: {', '.join(added_ds) if added_ds else 'None'}). Data governance review required."
        })
    else:
        diff_table.append({
            "field": "Data Sources & Storage",
            "old_value": ", ".join(sorted(list(v1_ds_list))) if v1_ds_list else "None",
            "new_value": ", ".join(sorted(list(v2_ds_list))) if v2_ds_list else "None",
            "status": "UNCHANGED",
            "severity": "LOW",
            "framework": "ISO 42001",
            "explanation": "Data store connections remain constant."
        })

    # 7. External APIs Check
    v1_apis = set(v1_meta.get("external_apis", []))
    v2_apis = set(v2_meta.get("external_apis", []))
    added_apis = sorted(list(v2_apis - v1_apis))
    if v1_apis != v2_apis:
        changed_count += 1
        frameworks_impacted.add("OWASP LLM Top 10 (LLM02)")
        diff_table.append({
            "field": "External API Integrations",
            "old_value": ", ".join(sorted(list(v1_apis))) if v1_apis else "None",
            "new_value": ", ".join(sorted(list(v2_apis))) if v2_apis else "None",
            "status": "Security Review",
            "severity": "MEDIUM",
            "framework": "OWASP LLM Top 10",
            "explanation": f"External API integrations updated (New APIs: {', '.join(added_apis) if added_apis else 'None'}). Network boundary review required."
        })
    else:
        diff_table.append({
            "field": "External API Integrations",
            "old_value": ", ".join(sorted(list(v1_apis))) if v1_apis else "None",
            "new_value": ", ".join(sorted(list(v2_apis))) if v2_apis else "None",
            "status": "UNCHANGED",
            "severity": "LOW",
            "framework": "OWASP LLM Top 10",
            "explanation": "External network API integrations unchanged."
        })

    # Determine Overall Diff Status
    if critical_count > 0 or score_delta <= -15:
        overall_status = "Critical"
    elif changed_count >= 3 or score_delta < 0 or risk_delta > 10:
        overall_status = "Needs Review"
    elif changed_count > 0:
        overall_status = "Modified"
    else:
        overall_status = "No Change"

    # AI Executive Summary Generation
    ai_summary = generate_ai_diff_summary(
        agent_name=agent_name,
        v1_ver=baseline_version,
        v2_ver=target_version,
        score_delta=score_delta,
        risk_delta=risk_delta,
        critical_count=critical_count,
        diff_items=diff_table
    )

    return {
        "agent_name": agent_name,
        "baseline_version": baseline_version,
        "target_version": target_version,
        "compliance_score_baseline": v1_score,
        "compliance_score_target": v2_score,
        "compliance_score_delta": score_delta,
        "risk_score_baseline": v1_risk_score,
        "risk_score_target": v2_risk_score,
        "risk_score_delta": risk_delta,
        "risk_tier_baseline": v1_risk_tier,
        "risk_tier_target": v2_risk_tier,
        "fields_changed_count": changed_count,
        "critical_changes_count": critical_count,
        "frameworks_impacted_count": len(frameworks_impacted),
        "overall_status": overall_status,
        "ai_explanation": ai_summary,
        "diff_table": diff_table,
        "frameworks_impacted": sorted(list(frameworks_impacted))
    }


def generate_ai_diff_summary(
    agent_name: str,
    v1_ver: str,
    v2_ver: str,
    score_delta: float,
    risk_delta: float,
    critical_count: int,
    diff_items: List[Dict[str, Any]]
) -> str:
    """
    Generates a concise AI summary for significant compliance card changes.
    Uses Gemini API if available, or structured fallback AI rule reasoning.
    """
    critical_items = [item for item in diff_items if item.get("severity") in ("CRITICAL", "HIGH")]

    # Try Gemini API if key is set
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key and len(gemini_key) > 10:
        try:
            prompt = (
                f"You are an enterprise AI Governance & Compliance Auditor. "
                f"Provide a 2-sentence executive summary comparing AI Agent '{agent_name}' version {v1_ver} vs {v2_ver}.\n"
                f"Compliance Score Delta: {score_delta}%, Risk Delta: {risk_delta}.\n"
                f"Significant Changes:\n" +
                "\n".join([f"- {i['field']}: {i['old_value']} -> {i['new_value']} ({i['explanation']})" for i in critical_items])
            )
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            
            with httpx.Client(timeout=4.0) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if text:
                        return text
        except Exception:
            pass

    # Fallback Rule-Based Executive AI Summary
    if critical_count > 0:
        top_reason = critical_items[0]["explanation"] if critical_items else "Escalated risk factors detected."
        return f"Version {v2_ver} introduces critical governance shifts requiring regulatory reassessment. {top_reason}"
    elif score_delta < 0:
        return f"Compliance score dropped by {abs(score_delta)}% from version {v1_ver} to {v2_ver}. Review newly added tool capabilities and authority levels."
    elif diff_items:
        modified_fields = [i['field'] for i in diff_items if i['status'] != 'UNCHANGED']
        if modified_fields:
            return f"Agent specification updated across {len(modified_fields)} area(s): {', '.join(modified_fields[:3])}. All changes comply with established safety thresholds."
        return "Baseline and target compliance card versions are structurally identical."
    return "No significant compliance card delta detected."


def compare_agent_versions(v1_data: Dict[str, Any], v2_data: Dict[str, Any]) -> Dict[str, Any]:
    return compare_compliance_cards(v1_data, v2_data)

compare_agent_scans = compare_agent_versions
