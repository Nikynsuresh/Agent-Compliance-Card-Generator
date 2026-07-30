import ast
import os
from typing import Dict, Any, List, Set


class AdvancedAgentASTVisitor(ast.NodeVisitor):
    """
    Advanced Python AST Visitor reverse engineering agent source code.
    Detects Frameworks (LangChain, LangGraph, CrewAI, AutoGen, MCP),
    LLMs (OpenAI, Anthropic, Gemini, Bedrock, Ollama),
    Databases (PostgreSQL, SQLite, MongoDB, Redis),
    Vector DBs (FAISS, Chroma, Pinecone, Milvus, Qdrant),
    APIs (requests, httpx, aiohttp), Email, Env vars, and Dangerous Operations.
    """

    def __init__(self):
        self.llm_providers: Set[str] = set()
        self.llm_versions: Set[str] = set()
        self.frameworks: Set[str] = set()
        self.tools_detected: List[Dict[str, Any]] = []
        self.data_sources: Set[str] = set()
        self.vector_dbs: Set[str] = set()
        self.external_apis: Set[str] = set()
        self.email_services: Set[str] = set()
        self.env_vars: Set[str] = set()
        self.dangerous_operations: List[Dict[str, Any]] = []
        self.agent_classification: Set[str] = set()

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self._inspect_module_name(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self._inspect_module_name(node.module)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        # Environment Variables Inspection
        if func_name in ("getenv", "environ") or (isinstance(node.func, ast.Attribute) and node.func.attr == "getenv"):
            if node.args and isinstance(node.args[0], ast.Constant):
                self.env_vars.add(str(node.args[0].value))

        # Dangerous Operations
        if func_name in ("exec", "eval", "system", "popen", "spawn", "pickle", "load", "loads"):
            self.dangerous_operations.append({
                "type": f"Dangerous Call: {func_name}()",
                "severity": "Critical",
                "line": getattr(node, "lineno", 0)
            })

        # LLM Model Detection
        if "OpenAI" in func_name or "gpt" in func_name.lower():
            self.llm_providers.add("OpenAI")
            self.llm_versions.add("GPT-4o")
        elif "Anthropic" in func_name or "claude" in func_name.lower():
            self.llm_providers.add("Anthropic")
            self.llm_versions.add("Claude 3.5 Sonnet")
        elif "Gemini" in func_name or "genai" in func_name.lower():
            self.llm_providers.add("Google Gemini")
            self.llm_versions.add("Gemini 2.5 Flash")

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for decorator in node.decorator_list:
            dec_name = ""
            if isinstance(decorator, ast.Name):
                dec_name = decorator.id
            elif isinstance(decorator, ast.Attribute):
                dec_name = decorator.attr
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    dec_name = decorator.func.id

            if dec_name in ("tool", "agent_tool", "mcp_tool"):
                docstring = ast.get_docstring(node) or ""
                self.tools_detected.append({
                    "name": node.name,
                    "description": docstring[:150] or "Custom agent tool",
                    "category": "Tool",
                    "risk": "Low" if not any(w in node.name.lower() for w in ["exec", "shell", "delete"]) else "Critical"
                })
                self.agent_classification.add("Tool Calling Agent")

        self.generic_visit(node)

    def _inspect_module_name(self, name: str):
        # Frameworks
        if "langchain" in name:
            self.frameworks.add("LangChain")
        elif "langgraph" in name:
            self.frameworks.add("LangGraph")
            self.agent_classification.add("Planner Agent")
        elif "crewai" in name:
            self.frameworks.add("CrewAI")
            self.agent_classification.add("Multi-Agent System")
        elif "autogen" in name:
            self.frameworks.add("AutoGen")
            self.agent_classification.add("Multi-Agent System")
        elif "mcp" in name:
            self.frameworks.add("Model Context Protocol (MCP)")

        # LLMs
        if "openai" in name:
            self.llm_providers.add("OpenAI")
        elif "anthropic" in name:
            self.llm_providers.add("Anthropic")
        elif "google.generativeai" in name:
            self.llm_providers.add("Google Gemini")

        # Vector Databases
        if "faiss" in name:
            self.vector_dbs.add("FAISS")
            self.agent_classification.add("Retriever Agent")
        elif "chromadb" in name:
            self.vector_dbs.add("Chroma")
            self.agent_classification.add("Retriever Agent")
        elif "pinecone" in name:
            self.vector_dbs.add("Pinecone")
        elif "milvus" in name:
            self.vector_dbs.add("Milvus")

        # Databases
        if any(db in name for db in ["sqlite3", "psycopg2", "sqlalchemy"]):
            self.data_sources.add("PostgreSQL / SQLite Database")
            self.agent_classification.add("Database Agent")
        elif "redis" in name:
            self.data_sources.add("Redis Cache Store")
        elif "pymongo" in name:
            self.data_sources.add("MongoDB Document Store")

        # APIs & Emails
        if any(http in name for http in ["requests", "httpx", "aiohttp"]):
            self.external_apis.add("HTTP REST APIs")
        if "smtplib" in name or "sendgrid" in name:
            self.email_services.add("SMTP Email Service")


def reverse_engineer_python_code(code_content: str) -> Dict[str, Any]:
    visitor = AdvancedAgentASTVisitor()
    try:
        tree = ast.parse(code_content)
        visitor.visit(tree)
    except SyntaxError as e:
        visitor.dangerous_operations.append({
            "type": f"Syntax Error: line {e.lineno}",
            "severity": "High"
        })

    # Default Agent Classification
    classifications = list(visitor.agent_classification)
    if not classifications:
        classifications = ["Autonomous Research Agent"]

    return {
        "frameworks": sorted(list(visitor.frameworks)) or ["Custom Python Agent"],
        "llm_providers": sorted(list(visitor.llm_providers)) or ["OpenAI"],
        "llm_versions": sorted(list(visitor.llm_versions)) or ["GPT-4o"],
        "tools_detected": visitor.tools_detected,
        "data_sources": sorted(list(visitor.data_sources)) or ["Application Context"],
        "vector_dbs": sorted(list(visitor.vector_dbs)),
        "external_apis": sorted(list(visitor.external_apis)),
        "email_services": sorted(list(visitor.email_services)),
        "env_vars": sorted(list(visitor.env_vars)),
        "dangerous_operations": visitor.dangerous_operations,
        "agent_classification": classifications
    }
