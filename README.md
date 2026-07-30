# 🛡️ AgentGuard AI – Enterprise AI Agent Governance & Compliance Platform

> **A production-grade, enterprise SaaS platform to audit, reverse-engineer, govern, and generate official Compliance Cards for autonomous AI Agents.**

---

## 🌟 Executive Overview

**AgentGuard AI** is an enterprise governance platform designed for AI Safety Officers, SecOps, and Auditors to inspect, analyze, and govern autonomous AI agents.

Unlike generic AI management tools, **AgentGuard AI** focuses strictly on **AI Agent Compliance Cards, Risk Assessment, AST Reverse Engineering, SAST Security Auditing, and Regulatory Reporting** against global AI standards including the **EU AI Act (Article 13)**, **ISO/IEC 42001 (AIMS)**, and **NIST AI Risk Management Framework (AI RMF 1.0)**.

---

## 🚀 Core Features & Architectural Engines

### 1. 🔍 Python AST Reverse Engineering Engine (`app/ast_engine/`)
- Automatically parses raw Python source code and directory trees without running code.
- **Framework Discovery**: Detects LangChain, LangGraph, CrewAI, AutoGen, and Model Context Protocol (MCP).
- **LLM Provider Detection**: Detects OpenAI (GPT-4o), Anthropic (Claude 3.5 Sonnet), Google Gemini (2.5 Flash), AWS Bedrock, and Ollama.
- **Database & Vector DB Detection**: Identifies PostgreSQL, SQLite, MongoDB, Redis, FAISS, ChromaDB, Pinecone, and Milvus.
- **Agent Capability Classifier**: Automatically classifies uploaded projects as *Research Agent*, *Database Agent*, *Tool Calling Agent*, *Retriever Agent*, or *Multi-Agent System*.

### 2. 📄 16-Field Agent Compliance Card Generator (`app/compliance_engine/`)
Generates structured compliance cards containing 16 mandatory governance specifications:
1. **Agent Name**
2. **Agent Purpose**
3. **Operational Scope**
4. **Owner / Governance Contact**
5. **LLM Name**
6. **LLM Version**
7. **Tool Inventory**
8. **Tool Operations**
9. **Data Sources**
10. **Database Access**
11. **External APIs**
12. **Decision Authority**
13. **Human Oversight Mechanism**
14. **Risk Classification**
15. **Known Limitations**
16. **Incident Contact**

### 3. ⚖️ Explainable Rule-Based Risk Engine (`app/risk_engine/`)
Computes quantitative, transparent risk scores (0–100) using rule-based positive and negative weights:
- 🔴 **Delete / Destructive Permission**: `+25 Pts`
- 🔴 **Database Write Access**: `+20 Pts`
- 🟠 **Internet Access**: `+10 Pts`
- 🟠 **External REST APIs**: `+10 Pts`
- 🟡 **Email Dispatch Capability**: `+8 Pts`
- 🟢 **Human-in-the-Loop (HITL) Approval**: `-15 Pts` *(Mitigation)*
- 🟢 **Audit Logging Active**: `-5 Pts` *(Mitigation)*

### 4. 🛡️ SAST Security Analyzer Engine (`app/security_engine/`)
Scans Python code for static security vulnerabilities:
- **Hardcoded API Keys**: Detects exposed OpenAI, Gemini, and secret tokens.
- **Dangerous Operations**: Identifies `eval()`, `exec()`, `shell=True`, and `pickle.loads()`.
- **Unsafe Parsing**: Detects `yaml.load()` without `SafeLoader`.
- **Injection Vulnerabilities**: Flags dynamic SQL string formatting and prompt injection patterns.

### 5. 📚 RAG Regulation Engine (`app/rag_engine/`)
- Embeds regulatory knowledge bases (**EU AI Act Article 13**, **ISO 42001**, **NIST AI RMF**).
- Uses FAISS vector search and Google Gemini API (`gemini-2.5-flash`) to explain *why a regulation applies*, *what compliance fields are missing*, and *step-by-step remediation steps*.

### 6. 🌐 Automatic Architecture Discovery (`app/graph_engine/`)
- Generates node and edge topology maps visualizing:  
  `User → Agent → Planner → Retriever → LLM → Tools → Database → Response`

### 7. 📈 Version Difference Engine (`app/services/diff_engine.py`)
- Compares baseline vs. release candidate agent versions.
- Highlights added/removed tools, changed LLM providers, risk score deltas, and compliance impact summaries.

### 8. 📥 ReportLab PDF & JSON Exporter (`app/report_engine/`)
- Exports formal PDF Audit Certificates with risk scores, card specifications, and framework assessments via ReportLab.
- Exports raw JSON payloads for SIEM integration.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Backend Framework** | Python 3.12, FastAPI, SQLAlchemy, Pydantic v2 |
| **Parsing & Static Analysis** | Python AST, PyYAML, JSON |
| **AI & LLM Services** | Google Gemini API (`gemini-2.5-flash`), LangChain, LangGraph |
| **Vector Search / RAG** | FAISS, Sentence Transformers |
| **Database** | SQLite (Local Dev) / PostgreSQL (Production) |
| **PDF Generation** | ReportLab |
| **Frontend UI** | React 18, Vite, Tailwind CSS, Lucide Icons |

---

## 📂 Project Directory Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/v1/                # FastAPI Routers (scans, compliance, risk, rag, export)
│   │   ├── ast_engine/            # Python AST Reverse Engineering Engine
│   │   ├── runtime_engine/        # Runtime Log Analyzer
│   │   ├── risk_engine/           # Explainable Risk Engine
│   │   ├── security_engine/       # SAST Static Code Security Analyzer
│   │   ├── compliance_engine/     # 16-Field Compliance Card Generator
│   │   ├── rag_engine/            # FAISS + Gemini Regulation Engine
│   │   ├── recommendation_engine/ # AI Remediation Engine
│   │   ├── graph_engine/          # Architecture Topology Discovery
│   │   ├── report_engine/         # ReportLab PDF Generator
│   │   ├── db/                    # SQLAlchemy Connection Wrapper
│   │   ├── models/                # Database ORM Models
│   │   └── schemas/               # Pydantic Schemas
│   └── main.py                    # FastAPI Entrypoint & Middleware
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main React UI Application
│   │   └── index.css              # Tailwind CSS Directives
│   └── vite.config.js             # Vite Dev Server Config
└── README.md                      # Detailed Project Documentation
```

---

## 💻 How to Run the Application

### 1️⃣ Start the Backend Server (FastAPI)

Open a terminal and run:

```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
- **Backend API URL**: `http://localhost:8000`
- **Swagger OpenAPI Docs**: `http://localhost:8000/docs`

---

### 2️⃣ Start the Frontend Server (React + Vite)

Open a **second terminal tab** and run:

```bash
cd frontend
npm install
npm run dev -- --port 5173
```
- **Web Application Dashboard**: `http://localhost:5173`

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/scans/` | List all scanned agent records |
| `POST` | `/api/v1/scans/upload-zip` | Upload and analyze a ZIP archive containing agent code |
| `POST` | `/api/v1/scans/scan-github` | Clone and audit a public GitHub repository |
| `POST` | `/api/v1/scans/scan-code-snippet` | Analyze raw pasted Python code |
| `GET` | `/api/v1/compliance/{scan_id}` | Fetch the 16-field Agent Compliance Card |
| `GET` | `/api/v1/risk/{scan_id}` | Fetch transparent risk scores & weight factors |
| `POST` | `/api/v1/audit-rag/chat` | Query RAG regulation engine over EU AI Act / ISO / NIST |
| `GET` | `/api/v1/export/pdf/{scan_id}` | Download PDF Audit Certificate |
| `GET` | `/api/v1/export/json/{scan_id}` | Download raw JSON compliance dump |

---

## 📜 License & Compliance Statement

This software is built for enterprise AI governance and regulatory auditing under the EU AI Act (Regulation 2024/1689).
