import re
import os
from typing import Dict, Any, List


MAX_LOG_READ_BYTES = 2 * 1024 * 1024  # Cap log file reads at 2MB to prevent memory spikes


def parse_runtime_logs(log_content: str) -> Dict[str, Any]:
    """
    Parses agent runtime logs (e.g. agent.log, runtime.log, stdout dumps) to extract:
    - Tools actually executed
    - APIs actually invoked
    - Databases accessed
    - Error counts and messages
    - Warning counts and messages
    - Execution trace timeline summary
    """
    lines = log_content.splitlines()

    tools_used = set()
    apis_called = set()
    dbs_accessed = set()
    errors = []
    warnings = []
    trace_events = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Detect tool execution logs
        if any(keyword in stripped.lower() for keyword in ["tool execution", "invoking tool", "executing tool", "tool call"]):
            match = re.search(r"tool[:\s]+(['\"]?[\w_-]+['\"]?)", stripped, re.IGNORECASE)
            if match:
                tools_used.add(match.group(1).strip("'\""))
            else:
                tools_used.add("Executed Tool")
            trace_events.append({"type": "tool", "event": stripped[:120]})

        # Detect API calls
        if any(keyword in stripped.lower() for keyword in ["http get", "http post", "api request", "fetching endpoint"]):
            apis_called.add("HTTP REST API")
            trace_events.append({"type": "api", "event": stripped[:120]})

        # Detect DB calls
        if any(keyword in stripped.lower() for keyword in ["select", "insert", "update", "delete from", "db query", "sqlite"]):
            dbs_accessed.add("Relational DB / SQLite")
            trace_events.append({"type": "db", "event": stripped[:120]})

        # Detect Errors
        if "error" in stripped.lower() or "exception" in stripped.lower() or "traceback" in stripped.lower():
            errors.append(stripped[:150])

        # Detect Warnings
        elif "warn" in stripped.lower() or "deprecated" in stripped.lower():
            warnings.append(stripped[:150])

    return {
        "tools_actually_used": sorted(list(tools_used)),
        "apis_actually_called": sorted(list(apis_called)),
        "databases_accessed": sorted(list(dbs_accessed)),
        "error_count": len(errors),
        "error_samples": errors[:5],
        "warning_count": len(warnings),
        "warning_samples": warnings[:5],
        "total_log_lines": len(lines),
        "trace_summary": trace_events[:10]
    }


def parse_log_file_in_dir(dir_path: str) -> Dict[str, Any]:
    log_files = ["runtime.log", "agent.log", "execution.log", "output.log", "stdout.log"]
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file in log_files or file.endswith(".log"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        # Cap read size at 2MB to prevent memory bloat
                        content = f.read(MAX_LOG_READ_BYTES)
                        return parse_runtime_logs(content)
                except Exception:
                    pass

    return {
        "tools_actually_used": [],
        "apis_actually_called": [],
        "databases_accessed": [],
        "error_count": 0,
        "error_samples": [],
        "warning_count": 0,
        "warning_samples": [],
        "total_log_lines": 0,
        "trace_summary": []
    }
