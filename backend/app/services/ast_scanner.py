import ast
import os
from typing import Dict, Any, List, Set


class AgentASTVisitor(ast.NodeVisitor):
    """
    Python AST Node Visitor that extracts LLM providers & versions, tool usage,
    database access, vector DBs, external network calls, email usage, and autonomous execution loops.
    """

    def __init__(self):
        self.llm_providers: Set[str] = set()
        self.llm_versions: Set[str] = set()
        self.tools_detected: List[Dict[str, Any]] = []
        self.data_sources: Set[str] = set()
        self.vector_dbs: Set[str] = set()
        self.external_apis: Set[str] = set()
        self.email_services: Set[str] = set()
        self.autonomous_triggers: List[str] = []
        self.dangerous_calls: List[str] = []
        self.imports: Set[str] = set()
        self.syntax_errors: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self._check_module_name(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self._check_module_name(node.module)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        # Detect dangerous system executions & dynamic reflection
        if func_name in ("system", "popen", "exec", "eval", "spawn", "getattr", "__import__"):
            self.dangerous_calls.append(f"Direct/Reflective call: {func_name}()")
            self.tools_detected.append({
                "name": f"System Exec ({func_name})",
                "category": "Shell / Reflection Execution",
                "risk": "Critical",
                "is_autonomous": True
            })

        # Detect LLM instantiations
        if "OpenAI" in func_name or "gpt" in func_name.lower():
            self.llm_providers.add("OpenAI")
            self.llm_versions.add("GPT-4o / GPT-3.5-Turbo")
        elif "Anthropic" in func_name or "claude" in func_name.lower():
            self.llm_providers.add("Anthropic")
            self.llm_versions.add("Claude 3.5 Sonnet")
        elif "Gemini" in func_name or "genai" in func_name.lower():
            self.llm_providers.add("Google Gemini")
            self.llm_versions.add("Gemini 2.5 Flash / Pro")
        elif "Bedrock" in func_name:
            self.llm_providers.add("AWS Bedrock")
            self.llm_versions.add("Claude / Titan via Bedrock")
        elif "Ollama" in func_name:
            self.llm_providers.add("Ollama Local")
            self.llm_versions.add("Llama-3 70B")

        # Detect Email sending
        if func_name in ("sendmail", "send_email", "send_mail", "sendgrid"):
            self.email_services.add("SMTP / SendGrid Email Client")

        # Detect DB calls
        if func_name in ("execute", "fetchall", "commit", "query", "connect"):
            self.data_sources.add("SQL / Relational Database")

        # Detect HTTP API calls
        if func_name in ("get", "post", "put", "delete", "request"):
            self.external_apis.add("HTTP / REST Services")

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
                tool_category = "Custom Tool"
                risk_level = "Low"
                docstring = ast.get_docstring(node) or ""
                
                if any(w in node.name.lower() or w in docstring.lower() for w in ["delete", "drop", "truncate", "remove"]):
                    tool_category = "Data Destruction"
                    risk_level = "High"
                elif any(w in node.name.lower() or w in docstring.lower() for w in ["sql", "db", "query"]):
                    tool_category = "Database Query"
                    risk_level = "Medium"
                elif any(w in node.name.lower() or w in docstring.lower() for w in ["shell", "bash", "cmd", "exec"]):
                    tool_category = "Shell Execution"
                    risk_level = "Critical"
                elif any(w in node.name.lower() or w in docstring.lower() for w in ["email", "mail", "send"]):
                    tool_category = "Email Dispatch"
                    risk_level = "Medium"

                self.tools_detected.append({
                    "name": node.name,
                    "category": tool_category,
                    "risk": risk_level,
                    "is_autonomous": False
                })

        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            self.autonomous_triggers.append("Unbounded autonomous loop (`while True`)")
        self.generic_visit(node)

    def _check_module_name(self, name: str):
        self.imports.add(name)

        if "openai" in name:
            self.llm_providers.add("OpenAI")
            self.llm_versions.add("GPT-4o")
        elif "anthropic" in name:
            self.llm_providers.add("Anthropic")
            self.llm_versions.add("Claude 3.5 Sonnet")
        elif "google.generativeai" in name or "genai" in name:
            self.llm_providers.add("Google Gemini")
            self.llm_versions.add("Gemini 2.5 Flash")

        if "faiss" in name:
            self.vector_dbs.add("FAISS Vector Index")
        elif "chromadb" in name:
            self.vector_dbs.add("ChromaDB Vector Store")

        if any(db in name for db in ["sqlite3", "psycopg2", "sqlalchemy", "asyncpg"]):
            self.data_sources.add("PostgreSQL / SQLite Database")
        elif "redis" in name:
            self.data_sources.add("Redis Cache Store")

        if "smtplib" in name or "sendgrid" in name:
            self.email_services.add("SMTP / SendGrid Email Client")

        if any(http in name for http in ["requests", "httpx", "aiohttp", "urllib"]):
            self.external_apis.add("HTTP / REST Services")


def scan_python_code(code: str) -> Dict[str, Any]:
    visitor = AgentASTVisitor()
    try:
        tree = ast.parse(code)
        visitor.visit(tree)
    except SyntaxError as e:
        # Flag syntax errors explicitly as high-risk unparsable code
        visitor.dangerous_calls.append(f"Syntax Error in Python code at line {e.lineno}: {e.msg}")
        visitor.tools_detected.append({
            "name": "Unparsable Code (Syntax Error)",
            "category": "Malformed Codebase",
            "risk": "High",
            "is_autonomous": False
        })
    except Exception as e:
        visitor.dangerous_calls.append(f"AST Parsing Failure: {str(e)}")

    return {
        "llm_providers": sorted(list(visitor.llm_providers)),
        "llm_versions": sorted(list(visitor.llm_versions)),
        "tools_detected": visitor.tools_detected,
        "data_sources": sorted(list(visitor.data_sources)),
        "vector_dbs": sorted(list(visitor.vector_dbs)),
        "external_apis": sorted(list(visitor.external_apis)),
        "email_services": sorted(list(visitor.email_services)),
        "autonomous_triggers": visitor.autonomous_triggers,
        "dangerous_calls": visitor.dangerous_calls,
        "imports": sorted(list(visitor.imports))
    }


def scan_directory_ast(dir_path: str) -> Dict[str, Any]:
    aggregated = {
        "llm_providers": set(),
        "llm_versions": set(),
        "tools_detected": [],
        "data_sources": set(),
        "vector_dbs": set(),
        "external_apis": set(),
        "email_services": set(),
        "autonomous_triggers": [],
        "dangerous_calls": [],
        "files_scanned": 0
    }

    if not os.path.exists(dir_path):
        return aggregated

    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                        res = scan_python_code(code)
                        aggregated["llm_providers"].update(res["llm_providers"])
                        aggregated["llm_versions"].update(res["llm_versions"])
                        aggregated["data_sources"].update(res["data_sources"])
                        aggregated["vector_dbs"].update(res["vector_dbs"])
                        aggregated["external_apis"].update(res["external_apis"])
                        aggregated["email_services"].update(res["email_services"])
                        aggregated["autonomous_triggers"].extend(res["autonomous_triggers"])
                        aggregated["dangerous_calls"].extend(res["dangerous_calls"])
                        
                        existing_tool_names = {t["name"] for t in aggregated["tools_detected"]}
                        for tool in res["tools_detected"]:
                            if tool["name"] not in existing_tool_names:
                                aggregated["tools_detected"].append(tool)
                                existing_tool_names.add(tool["name"])
                                
                        aggregated["files_scanned"] += 1
                except Exception:
                    continue

    return {
        "llm_providers": sorted(list(aggregated["llm_providers"])),
        "llm_versions": sorted(list(aggregated["llm_versions"])),
        "tools_detected": aggregated["tools_detected"],
        "data_sources": sorted(list(aggregated["data_sources"])),
        "vector_dbs": sorted(list(aggregated["vector_dbs"])),
        "external_apis": sorted(list(aggregated["external_apis"])),
        "email_services": sorted(list(aggregated["email_services"])),
        "autonomous_triggers": list(set(aggregated["autonomous_triggers"])),
        "dangerous_calls": list(set(aggregated["dangerous_calls"])),
        "files_scanned": aggregated["files_scanned"]
    }
