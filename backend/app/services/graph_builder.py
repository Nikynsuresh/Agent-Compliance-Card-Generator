from typing import Dict, Any, List


def build_topology_graph(agent_name: str, card_data: Dict[str, Any], scanned_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Builds node and edge topology structure visualizing:
    User -> Agent -> LLM -> Database -> Tools -> External APIs
    """
    nodes = [
        {"id": "user", "label": "User / Client Request", "type": "actor", "category": "Input"},
        {"id": "agent", "label": agent_name, "type": "agent", "category": "Agent Core"},
        {"id": "llm", "label": card_data.get("llm_name", "LLM Inference Engine"), "type": "llm", "category": "Model"}
    ]

    edges = [
        {"source": "user", "target": "agent", "label": "Prompts / Directives"},
        {"source": "agent", "target": "llm", "label": "Inference API Call"}
    ]

    # Add Database Nodes
    data_sources = scanned_data.get("data_sources", []) + scanned_data.get("vector_dbs", [])
    for idx, ds in enumerate(data_sources):
        ds_id = f"db_{idx}"
        nodes.append({"id": ds_id, "label": ds, "type": "database", "category": "Storage"})
        edges.append({"source": "agent", "target": ds_id, "label": "Read / Write Query"})

    # Add Tool Nodes
    tools = scanned_data.get("tools_detected", [])
    for idx, t in enumerate(tools):
        t_id = f"tool_{idx}"
        nodes.append({"id": t_id, "label": t.get("name"), "type": "tool", "category": t.get("category", "Tool")})
        edges.append({"source": "agent", "target": t_id, "label": "Tool Invocation"})

    # Add External API Nodes
    apis = scanned_data.get("external_apis", [])
    for idx, api in enumerate(apis):
        api_id = f"api_{idx}"
        nodes.append({"id": api_id, "label": api, "type": "api", "category": "External API"})
        edges.append({"source": "agent", "target": api_id, "label": "HTTP Request"})

    return {
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }

# Alias for graph.py router
build_architecture_graph = build_topology_graph
