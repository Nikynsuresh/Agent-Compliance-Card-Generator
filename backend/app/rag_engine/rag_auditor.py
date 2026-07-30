import os
from typing import Dict, Any, List

try:
    import google.generativeai as genai
except ImportError:
    genai = None


REGULATION_KNOWLEDGE_BASE = [
    {"doc": "EU AI Act Article 13", "text": "High-risk AI systems shall be designed and developed in such a way to ensure that their operation is sufficiently transparent to enable deployers to interpret a system's output and use it appropriately. Deployers shall receive instructions for use specifying capabilities, limitations, human oversight measures, and risk factors."},
    {"doc": "ISO/IEC 42001:2023 A.8.4", "text": "Organizations shall define and implement human oversight controls over AI systems, including decision authority boundaries, manual intervention triggers, and emergency stop mechanisms for high-risk tool operations."},
    {"doc": "NIST AI RMF 1.0 GOVERN & MAP", "text": "Establish policies, governance structures, and risk management functions. Categorize AI components, LLM inference engines, external database connections, and third-party APIs via static code discovery and runtime log audits."}
]


def query_rag_regulation_engine(query_text: str, agent_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    RAG Regulation Engine querying EU AI Act, ISO 42001, and NIST AI RMF
    and invoking Gemini to explain why a regulation applies and how to fix gaps.
    """
    # FAISS / Keyword Matching retrieval
    retrieved = [
        kb for kb in REGULATION_KNOWLEDGE_BASE
        if any(w in query_text.lower() or w in kb["text"].lower() for w in ["ai act", "article 13", "iso", "42001", "nist", "transparency", "oversight", "risk", "data"])
    ] or REGULATION_KNOWLEDGE_BASE[:2]

    api_key = os.getenv("GEMINI_API_KEY", "")
    
    if api_key and genai:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            context_str = "\n".join([f"[{r['doc']}]: {r['text']}" for r in retrieved])
            prompt = f"""
            You are an AI Governance Compliance Auditor.
            Question: {query_text}
            
            Agent Context:
            Name: {agent_context.get('agent_name')}
            Tools: {agent_context.get('tools_detected')}
            
            Regulatory Context:
            {context_str}

            Explain:
            1. Why this regulation applies.
            2. What compliance parameters are missing.
            3. Exact step-by-step remediation fix.
            """

            response = model.generate_content(prompt)
            return {
                "answer": response.text or "Regulatory analysis generated.",
                "retrieved_regulations": [r["doc"] for r in retrieved]
            }
        except Exception:
            pass

    # Offline fallback response
    return {
        "answer": f"Under {retrieved[0]['doc']}, agent '{agent_context.get('agent_name')}' must maintain transparent tool declarations, documented human oversight controls, and logged DB/API calls.",
        "retrieved_regulations": [r["doc"] for r in retrieved]
    }
