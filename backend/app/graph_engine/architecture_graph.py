from typing import Dict, Any, List


def discover_architecture_graph(agent_name: str, scanned_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Automatic Architecture & Agent Dependency Graph Discovery:
    User -> Agent -> Planner -> Retriever -> LLM -> Tools -> Database -> Response.
    """
    nodes = [
        {"id": "user", "label": "User Input", "type": "actor", "category": "Client"},
        {"id": "agent", "label": agent_name, "type": "agent", "category": "Core Agent"},
        {"id": "planner", "label": "LangGraph / Task Planner", "type": "planner", "category": "Orchestrator"},
        {"id": "retriever", "label": "RAG Vector Retriever", "type": "retriever", "category": "Retrieval"},
        {"id": "llm", "label": (scanned_data.get("llm_providers") or ["OpenAI"])[0], "type": "llm", "category": "Model"},
        {"id": "response", "label": "Sanitized Response", "type": "output", "category": "Client"}
    ]

    edges = [
        {"source": "user", "target": "agent", "label": "Prompt Directive"},
        {"source": "agent", "target": "planner", "label": "Decompose Goal"},
        {"source": "planner", "target": "retriever", "label": "Fetch Context"},
        {"source": "retriever", "target": "llm", "label": "Augmented Prompt"},
        {"source": "llm", "target": "response", "label": "Output Generation"}
    ]

    # Add Tools
    for idx, t in enumerate(scanned_data.get("tools_detected", [])):
        t_id = f"tool_{idx}"
        nodes.append({"id": t_id, "label": t.get("name"), "type": "tool", "category": "Execution"})
        edges.append({"source": "agent", "target": t_id, "label": "Invoke Tool"})

    # Add Database
    for idx, ds in enumerate(scanned_data.get("data_sources", [])):
        ds_id = f"db_{idx}"
        nodes.append({"id": ds_id, "label": ds, "type": "database", "category": "Storage"})
        edges.append({"source": "agent", "target": ds_id, "label": "Query / Store"})

    return {
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }
