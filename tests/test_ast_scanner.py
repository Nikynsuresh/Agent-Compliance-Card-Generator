from app.services.ast_scanner import scan_python_code


def test_ast_scanner_openai_and_sqlite():
    code = """
import sqlite3
from openai import OpenAI

def tool(f): return f

@tool
def query_db(sql: str):
    conn = sqlite3.connect("test.db")
    return conn.execute(sql).fetchall()

def run():
    client = OpenAI(api_key="key")
    query_db("SELECT * FROM users")
"""
    res = scan_python_code(code)
    assert any("OpenAI" in provider for provider in res["llm_providers"])
    assert any("Database" in ds for ds in res["data_sources"])
    assert len(res["tools_detected"]) >= 1
    assert res["tools_detected"][0]["name"] == "query_db"


def test_ast_scanner_dangerous_shell():
    code = """
import os

def run_shell(cmd):
    return os.popen(cmd).read()
"""
    res = scan_python_code(code)
    assert len(res["dangerous_calls"]) >= 1
    assert "popen" in res["dangerous_calls"][0]
