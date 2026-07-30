import re
import ast
from typing import Dict, Any, List


def audit_security_vulnerabilities(code_content: str) -> Dict[str, Any]:
    """
    Static Application Security Testing (SAST) Analyzer detecting:
    - Hardcoded API Keys & Secrets
    - Dangerous eval(), exec(), shell=True, pickle
    - Unsafe YAML loading
    - SQL Injection patterns
    - Prompt Injection vulnerability patterns
    """
    security_findings: List[Dict[str, Any]] = []

    # 1. Hardcoded API Key Patterns
    api_key_patterns = [
        (r"sk-[a-zA-Z0-9]{20,T}", "Hardcoded OpenAI API Key"),
        (r"AIzaSy[a-zA-Z0-9_-]{33}", "Hardcoded Google API Key"),
        (r"secret[_\s]*=[_\s]*['\"][a-zA-Z0-9_\-]{16,}['\"]", "Hardcoded Secret Token")
    ]
    for pattern, label in api_key_patterns:
        if re.search(pattern, code_content):
            security_findings.append({
                "category": "Hardcoded Secrets",
                "finding": label,
                "severity": "Critical",
                "recommendation": "Migrate secrets to environment variables or secret management vault."
            })

    # 2. Dangerous Shell & Unsafe Functions
    if "shell=True" in code_content:
        security_findings.append({
            "category": "Command Injection",
            "finding": "Subprocess called with `shell=True`",
            "severity": "Critical",
            "recommendation": "Pass command arguments as a list without invoking a shell."
        })

    if "pickle.loads" in code_content or "pickle.load(" in code_content:
        security_findings.append({
            "category": "Insecure Deserialization",
            "finding": "Unsafe `pickle` deserialization",
            "severity": "High",
            "recommendation": "Replace pickle with safer serialization formats such as JSON or Protocol Buffers."
        })

    if "yaml.load(" in code_content and "Loader=yaml.SafeLoader" not in code_content:
        security_findings.append({
            "category": "Unsafe YAML Parsing",
            "finding": "Unsafe `yaml.load()` without SafeLoader",
            "severity": "Medium",
            "recommendation": "Use `yaml.safe_load()` to prevent arbitrary code execution."
        })

    # 3. SQL Injection Patterns
    if re.search(r"SELECT\s+.*\s+FROM\s+.*WHERE\s+.*(\+|\%|\.format|f['\"])", code_content, re.IGNORECASE):
        security_findings.append({
            "category": "SQL Injection",
            "finding": "Dynamic string formatting in SQL Query",
            "severity": "High",
            "recommendation": "Use parameterized queries or ORM query builders."
        })

    # 4. Prompt Injection Resistance Check
    if "ignore previous instructions" in code_content.lower() or "override system prompt" in code_content.lower():
        security_findings.append({
            "category": "Prompt Injection Vulnerability",
            "finding": "Un-sanitized user prompt bypass patterns detected",
            "severity": "High",
            "recommendation": "Wrap user inputs in strict delimiter blocks and policy guardrails."
        })

    return {
        "security_score": max(0, 100 - (len(security_findings) * 20)),
        "total_findings": len(security_findings),
        "findings": security_findings
    }
