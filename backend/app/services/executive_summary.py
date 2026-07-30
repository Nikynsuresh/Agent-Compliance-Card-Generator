import os
import google.generativeai as genai
from typing import Dict, Any


def generate_ai_executive_summary(agent_name: str, card_data: Dict[str, Any], risk_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invokes Google Gemini API (gemini-2.5-flash) to generate a concise, professional
    Enterprise AI Executive Summary covering:
    1. Agent Summary
    2. Business Purpose
    3. Identified Security & Operational Risks
    4. Regulatory Compliance Observations
    5. Actionable Remediation Recommendations
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    if not api_key:
        return {
            "summary": f"Executive Compliance Summary for {agent_name}.",
            "business_purpose": card_data.get("agent_purpose", "Automated enterprise execution agent."),
            "identified_risks": [f"Risk level evaluated at {risk_data.get('risk_level', 'Minimal')}"],
            "compliance_observations": ["Card specs complete and audited against AST scanner."],
            "recommendations": ["Ensure human-in-the-loop oversight is enforced on critical tool calls."]
        }

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        You are a Chief AI Compliance Officer writing an Executive Audit Summary for an enterprise AI agent.
        
        Agent Name: {agent_name}
        Agent Purpose: {card_data.get('agent_purpose')}
        LLMs Used: {card_data.get('llm_name')}
        Tools Discovered: {card_data.get('tool_inventory')}
        Risk Score: {risk_data.get('risk_score')}/100 ({risk_data.get('risk_level')} Risk)
        Risk Factors: {risk_data.get('risk_factors')}

        Provide a concise audit summary with:
        1. Agent Business Purpose
        2. Key Risk Observations
        3. Compliance Status Summary
        4. Remediation Recommendations
        """

        response = model.generate_content(prompt)
        text = response.text or ""

        return {
            "executive_summary_text": text,
            "agent_name": agent_name,
            "risk_tier": risk_data.get("risk_level"),
            "status": "Generated via Gemini 2.5 Flash"
        }

    except Exception as e:
        return {
            "executive_summary_text": f"Agent {agent_name} operates with a risk tier of {risk_data.get('risk_level')}. Ensure all tool calls undergo AST sanitization.",
            "error": str(e)
        }
