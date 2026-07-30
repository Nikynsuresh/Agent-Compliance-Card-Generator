import os
import zipfile
import yaml
from typing import Dict, Any
from app.services.ast_scanner import scan_directory_ast


def extract_zip_safely(zip_path: str, extract_to_dir: str) -> None:
    """
    Extracts a ZIP archive with strict Zip Slip / Path Traversal protection.
    Rejects any archive entry attempting to escape target_dir via '../'.
    """
    os.makedirs(extract_to_dir, exist_ok=True)
    abs_extract_dir = os.path.abspath(extract_to_dir)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.infolist():
            target_path = os.path.abspath(os.path.join(extract_to_dir, member.filename))
            if not target_path.startswith(abs_extract_dir):
                raise ValueError(f"Security Alert: Illegal Zip Slip path traversal detected in file '{member.filename}'")
            zip_ref.extract(member, extract_to_dir)


def discover_agent_assets(target_dir: str) -> Dict[str, Any]:
    """
    Discovers agent manifests, YAML/JSON configs, prompts, environment variables,
    docstrings, and runs AST code analysis on Python code files (max 500 files).
    """
    result = {
        "agent_name": "Scanned Enterprise Agent",
        "version": "1.0.0",
        "framework": "Custom Python Agent",
        "agent_purpose": "AI Agent for automated code execution, database queries, and system tasks",
        "llm_providers": [],
        "tools_detected": [],
        "data_sources": [],
        "external_apis": [],
        "prompts_found": [],
        "env_vars_found": [],
        "config_files": [],
        "human_oversight": "Human-in-the-Loop Required",
        "incident_contact": "security-team@enterprise.com",
        "known_limitations": []
    }

    if not os.path.exists(target_dir):
        return result

    # 1. Scan directory with AST
    ast_res = scan_directory_ast(target_dir)
    result["llm_providers"] = ast_res["llm_providers"]
    result["tools_detected"] = ast_res["tools_detected"]
    result["data_sources"] = ast_res["data_sources"]
    result["external_apis"] = ast_res["external_apis"]

    # Try extracting purpose from README.md
    readme_path = os.path.join(target_dir, "README.md")
    if os.path.exists(readme_path):
        try:
            with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(500)
                lines = [l.strip("# ").strip() for l in content.splitlines() if l.strip() and not l.startswith("#")]
                if lines:
                    result["agent_purpose"] = lines[0][:200]
        except Exception:
            pass

    # Deduce framework from tools/ast
    if any("langchain" in str(tool).lower() or "langchain" in str(ast_res) for tool in ast_res["tools_detected"]):
        result["framework"] = "LangChain"
    elif any("autogen" in str(tool).lower() for tool in ast_res["tools_detected"]):
        result["framework"] = "AutoGen"
    elif any("crewai" in str(tool).lower() for tool in ast_res["tools_detected"]):
        result["framework"] = "CrewAI"

    # 2. Look for configuration files
    for root, _, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root, file)
            lower_file = file.lower()

            if lower_file in ("agent.yaml", "agent.yml", "config.yaml", "config.yml"):
                result["config_files"].append(file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        cfg = yaml.safe_load(f)
                        if isinstance(cfg, dict):
                            if "name" in cfg or "agent_name" in cfg:
                                result["agent_name"] = cfg.get("name") or cfg.get("agent_name")
                            if "version" in cfg:
                                result["version"] = str(cfg.get("version"))
                            if "purpose" in cfg or "description" in cfg:
                                result["agent_purpose"] = cfg.get("purpose") or cfg.get("description")
                            if "human_oversight" in cfg:
                                result["human_oversight"] = cfg.get("human_oversight")
                            if "incident_contact" in cfg:
                                result["incident_contact"] = cfg.get("incident_contact")
                except Exception:
                    pass

    # Defaults if missing
    if not result["llm_providers"]:
        result["llm_providers"] = ["OpenAI GPT-4o"]
    if not result["data_sources"]:
        result["data_sources"] = ["Application Context Memory"]

    return result


def extract_zip_and_discover(zip_path: str, extract_to_dir: str) -> Dict[str, Any]:
    extract_zip_safely(zip_path, extract_to_dir)
    return discover_agent_assets(extract_to_dir)
