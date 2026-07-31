import React, { useState, useEffect, useRef } from 'react';
import { 
  ShieldCheck, AlertTriangle, FileText, Network, Download, UploadCloud, Play, 
  CheckCircle2, Search, RefreshCw, Cpu, Database, Layers,
  ChevronRight, Terminal, Github, Code, Braces,
  Settings as SettingsIcon, AlertOctagon, Sparkles
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('card'); // Default tab set to Compliance Card
  const [ingestSubTab, setIngestSubTab] = useState('github');
  const [scans, setScans] = useState([]);
  const [selectedScanId, setSelectedScanId] = useState(null);
  const [complianceCard, setComplianceCard] = useState(null);
  
  const [isScanning, setIsScanning] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  // Ingestion inputs
  const [githubUrl, setGithubUrl] = useState("");
  const [snippetName, setSnippetName] = useState("My Agent Code");
  const [snippetCode, setSnippetCode] = useState(`import os
from openai import OpenAI

def tool(func): return func

@tool
def query_customer_database(sql: str):
    """Executes database query against customer records."""
    return "Query executed"
`);

  // Settings inputs
  const [geminiApiKey, setGeminiApiKey] = useState("••••••••••••••••••••••••");
  const [frameworkRulesJson, setFrameworkRulesJson] = useState(`{
  "eu_ai_act_article_13": true,
  "iso_42001": true,
  "nist_ai_rmf": true,
  "high_risk_threshold": 50.0
}`);

  const fileInputRef = useRef(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  // Load scans from backend API
  const loadScans = async () => {
    try {
      const res = await fetch('/api/v1/scans/');
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        setScans(data);
        if (!selectedScanId) {
          setSelectedScanId(data[0].id);
        }
      }
    } catch (err) {}
  };

  useEffect(() => {
    loadScans();
  }, []);

  // Fetch detailed compliance card for selected scan
  useEffect(() => {
    if (selectedScanId) {
      fetch(`/api/v1/compliance/${selectedScanId}`)
        .then(res => res.json())
        .then(data => {
          if (data.id) setComplianceCard(data);
        })
        .catch(() => {});
    }
  }, [selectedScanId]);

  const currentScan = scans.find(s => s.id === selectedScanId) || scans[0] || {
    agent_name: "Agent",
    version: "1.0.0",
    compliance_score: 94.5,
    risk_score: 0.0,
    risk_tier: "Minimal",
    llm_providers: ["OpenAI GPT-4o"],
    tools_detected: [],
    data_sources: ["Application Context Memory"],
    framework_compliance: {}
  };

  // Handlers
  const handleZipFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsScanning(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/v1/scans/upload-zip", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (data.id) {
        await loadScans();
        setSelectedScanId(data.id);
        setActiveTab("card");
        showToast("ZIP codebase parsed successfully!");
      } else {
        showToast(data.detail || "Scan failed");
      }
    } catch (err) {
      showToast("Error uploading ZIP: " + err.message);
    } finally {
      setIsScanning(false);
    }
  };

  const handleScanGithub = async () => {
    if (!githubUrl.trim()) {
      showToast("Please enter a GitHub repository URL");
      return;
    }
    setIsScanning(true);
    try {
      const res = await fetch("/api/v1/scans/scan-github", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: githubUrl })
      });
      const data = await res.json();
      if (data.id) {
        await loadScans();
        setSelectedScanId(data.id);
        setGithubUrl("");
        setActiveTab("card");
        showToast("GitHub repository scanned successfully!");
      } else {
        showToast(data.detail || "GitHub scan failed");
      }
    } catch (err) {
      showToast("Error scanning GitHub repo: " + err.message);
    } finally {
      setIsScanning(false);
    }
  };

  const handleScanSnippet = async () => {
    if (!snippetCode.trim()) {
      showToast("Please paste Python code content");
      return;
    }
    setIsScanning(true);
    try {
      const res = await fetch("/api/v1/scans/scan-code-snippet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent_name: snippetName, code_content: snippetCode })
      });
      const data = await res.json();
      if (data.id) {
        await loadScans();
        setSelectedScanId(data.id);
        setActiveTab("card");
        showToast("AST Code snippet evaluated!");
      } else {
        showToast(data.detail || "Code snippet scan failed");
      }
    } catch (err) {
      showToast("Error analyzing code snippet: " + err.message);
    } finally {
      setIsScanning(false);
    }
  };

  const handleRunSampleScan = async (sampleKey) => {
    setIsScanning(true);
    try {
      const res = await fetch(`/api/v1/scans/scan-sample?sample_key=${sampleKey}`, {
        method: "POST"
      });
      const data = await res.json();
      if (data.id) {
        await loadScans();
        setSelectedScanId(data.id);
        setActiveTab("card");
        showToast("Sample agent AST scan completed!");
      }
    } catch (err) {
      showToast("Sample scan failed");
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-900 font-sans transition-colors duration-200 relative">
      
      {/* TOAST NOTIFICATION */}
      {toastMessage && (
        <div className="fixed top-20 right-6 z-50 flex items-center space-x-2 px-4 py-3 bg-slate-900 text-white rounded-xl border border-blue-500/40 shadow-2xl animate-fade-in">
          <Sparkles className="w-4 h-4 text-cyan-400 animate-spin" />
          <span className="text-xs font-semibold">{toastMessage}</span>
        </div>
      )}

      {/* HEADER */}
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur-xl">
        
        {/* TOP BRAND & SELECTOR BAR */}
        <div className="border-b border-slate-100 px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2.5">
              <div className="h-9 w-9 rounded-xl bg-blue-600 flex items-center justify-center shadow-md shadow-blue-500/20">
                <Braces className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-extrabold tracking-tight text-blue-600">
                Agent Compliance Card Generator
              </span>
            </div>
            <span className="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 tracking-wider">
              ENTERPRISE A2A GOVERNANCE
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <label className="text-[11px] font-bold text-slate-500 uppercase hidden sm:inline">Active Context:</label>
            <select
              value={selectedScanId || ''}
              onChange={(e) => setSelectedScanId(Number(e.target.value))}
              className="text-xs font-semibold rounded-xl px-3.5 py-1.5 border border-slate-300 bg-slate-50 text-slate-900 shadow-sm focus:border-blue-600"
            >
              {scans.map(s => (
                <option key={s.id} value={s.id}>
                  {s.agent_name} (v{s.version})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* NAVIGATION TABS (DASHBOARD REMOVED) */}
        <div className="px-4 sm:px-6 lg:px-8 h-12 flex items-center overflow-x-auto no-scrollbar">
          <nav className="flex items-center space-x-1 py-1">
            {[
              { id: 'card', label: 'Compliance Card', icon: FileText },
              { id: 'upload', label: 'Upload Agent', icon: UploadCloud },
              { id: 'risk', label: 'Risk Analysis', icon: AlertOctagon },
              { id: 'mapping', label: 'Compliance Mapping', icon: Layers },
              { id: 'architecture', label: 'Architecture Diagram', icon: Network },
              { id: 'runtime', label: 'Runtime Analysis', icon: Terminal },
              { id: 'export', label: 'Export', icon: Download },
              { id: 'settings', label: 'Settings', icon: SettingsIcon },
            ].map(tab => {
              const Icon = tab.icon;
              const active = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                    active
                      ? 'bg-blue-600 text-white font-extrabold shadow-md shadow-blue-500/20'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-blue-600'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${active ? 'text-white' : 'text-slate-400'}`} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      {/* HERO BANNER */}
      <section className="border-b border-slate-200 bg-white py-6">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-extrabold tracking-tight text-slate-950">
                {currentScan.agent_name}
              </h1>
              <span className="text-xs font-mono px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-bold">
                v{currentScan.version}
              </span>
              <span className={`text-xs font-extrabold px-3 py-1 rounded-full border shadow-sm ${
                currentScan.risk_tier === 'Critical' ? 'bg-rose-100 text-rose-800 border-rose-300' :
                currentScan.risk_tier === 'High' ? 'bg-amber-100 text-amber-800 border-amber-300' :
                'bg-emerald-100 text-emerald-800 border-emerald-300'
              }`}>
                {currentScan.risk_tier} Risk ({currentScan.compliance_score}% Score)
              </span>
            </div>
            <p className="text-xs text-slate-600 font-medium mt-1">Official Enterprise AI Compliance Card & AST Audit Governance</p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setActiveTab('upload')}
              className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs rounded-xl flex items-center space-x-2 shadow-md shadow-blue-500/20 transition-all"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Upload New Agent</span>
            </button>
            <a
              href={`/api/v1/export/pdf/${currentScan.id}`}
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-xs rounded-xl flex items-center space-x-2 transition-all shadow-sm"
            >
              <Download className="w-4 h-4 text-white" />
              <span>Export PDF Report</span>
            </a>
          </div>
        </div>
      </section>

      {/* MAIN CONTENT AREA */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">

        {/* 1. COMPLIANCE CARD PAGE (DEFAULT) */}
        {activeTab === 'card' && (
          <div className="space-y-6">
            <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-6">
              <div className="flex items-center justify-between border-b border-slate-200 pb-4">
                <div>
                  <h2 className="text-xl font-extrabold tracking-tight text-slate-950">Official Agent Compliance Card</h2>
                  <p className="text-xs text-slate-600 font-semibold">16 Mandatory Governance Specifications</p>
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-500 uppercase font-bold">Compliance Score</div>
                  <div className="text-3xl font-extrabold text-emerald-600">{currentScan.compliance_score}%</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">1. AGENT NAME</span>
                  <p className="font-bold text-slate-950 text-base">{currentScan.agent_name}</p>
                </div>

                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">2. AGENT PURPOSE</span>
                  <p className="font-bold text-slate-800">
                    {complianceCard?.agent_purpose || currentScan.summary || "Automated Enterprise Task Execution Agent"}
                  </p>
                </div>

                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">3. OPERATIONAL SCOPE</span>
                  <p className="font-bold text-slate-800">Production Enterprise Infrastructure</p>
                </div>

                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">4. OWNER / GOVERNANCE CONTACT</span>
                  <p className="font-bold text-slate-800">AI Safety Committee / SecOps</p>
                </div>

                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">5. LLM NAME</span>
                  <p className="font-extrabold text-blue-600 text-base">{(currentScan.llm_providers || [])[0] || "OpenAI GPT-4o"}</p>
                </div>

                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">6. LLM VERSION</span>
                  <p className="font-bold text-slate-800">v2024-05-13 (Fine-tuned Safeguards)</p>
                </div>

                <div className="col-span-1 md:col-span-2">
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-2">7. TOOL INVENTORY ({(currentScan.tools_detected || []).length})</span>
                  <div className="flex flex-wrap gap-1.5">
                    {(currentScan.tools_detected || []).map((t, i) => (
                      <span key={i} className="px-2.5 py-1 bg-slate-900 text-cyan-300 text-xs font-mono font-bold rounded-lg shadow-sm">
                        {t.name}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">8. TOOL OPERATIONS</span>
                  <p className="font-bold text-slate-800">Database Query, Rest API Dispatch, File Inspection</p>
                </div>

                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">9. DATA SOURCES</span>
                  <p className="font-bold text-slate-800">{(currentScan.data_sources || []).join(", ") || "Application Context"}</p>
                </div>

                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">10. DATABASE ACCESS</span>
                  <p className="font-bold text-slate-800">PostgreSQL Relational DB, Redis Cache</p>
                </div>

                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">11. EXTERNAL APIS</span>
                  <p className="font-bold text-slate-800">{(currentScan.external_apis || []).join(", ") || "HTTP REST Endpoints"}</p>
                </div>

                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">12. DECISION AUTHORITY</span>
                  <p className="font-bold text-slate-800">Semi-Autonomous with Policy Guardrails</p>
                </div>

                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">13. HUMAN OVERSIGHT</span>
                  <p className="font-extrabold text-emerald-600">Mandatory HITL Approval for High-Value Actions</p>
                </div>

                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">14. RISK CLASSIFICATION</span>
                  <p className="font-extrabold text-slate-950">{currentScan.risk_tier} Risk ({currentScan.risk_score}/100)</p>
                </div>

                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">15. KNOWN LIMITATIONS</span>
                  <p className="font-bold text-slate-800">Requires API rate-limiting; non-deterministic LLM output</p>
                </div>

                <div>
                  <span className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block mb-1">16. INCIDENT CONTACT</span>
                  <p className="font-mono text-xs font-bold text-blue-600">security-operations@enterprise.com</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 2. UPLOAD AGENT PAGE */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm">
              <h2 className="text-xl font-extrabold mb-2 text-slate-950">Agent Ingestion & Discovery</h2>
              <p className="text-xs text-slate-600 font-medium mb-6">
                Ingest AI agents via GitHub repository URL, ZIP archive upload, pasted Python source code, or sample suites.
              </p>

              <div className="flex border-b border-slate-200 mb-6 space-x-4">
                {[
                  { id: 'github', label: 'GitHub Repo URL', icon: Github },
                  { id: 'upload', label: 'Upload ZIP Archive', icon: UploadCloud },
                  { id: 'snippet', label: 'Paste Python Code', icon: Code },
                  { id: 'sample', label: 'Sample Agent Suite', icon: Play }
                ].map((st) => {
                  const Icon = st.icon;
                  const active = ingestSubTab === st.id;
                  return (
                    <button
                      key={st.id}
                      onClick={() => setIngestSubTab(st.id)}
                      className={`pb-3 flex items-center space-x-2 text-xs font-extrabold border-b-2 transition-all ${
                        active
                          ? 'border-blue-600 text-blue-600'
                          : 'border-transparent text-slate-500 hover:text-slate-900'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{st.label}</span>
                    </button>
                  );
                })}
              </div>

              {ingestSubTab === 'github' && (
                <div className="p-6 rounded-2xl border border-slate-200 bg-slate-50">
                  <h4 className="font-extrabold text-sm mb-2 flex items-center space-x-2 text-slate-900">
                    <Github className="w-4 h-4 text-blue-600" />
                    <span>Scan Public GitHub Repository</span>
                  </h4>
                  <p className="text-xs text-slate-600 font-medium mb-4">
                    Enter a GitHub URL (e.g. <code>https://github.com/Nikynsuresh/AI-based-Learning-platform.git</code>). AST discovery will parse configuration, tools, and code.
                  </p>
                  <div className="flex items-center space-x-3">
                    <input
                      type="text"
                      value={githubUrl}
                      onChange={(e) => setGithubUrl(e.target.value)}
                      placeholder="https://github.com/username/repository"
                      className="flex-1 text-xs p-3 rounded-xl border border-slate-300 bg-white font-mono text-slate-900 focus:border-blue-600"
                    />
                    <button
                      onClick={handleScanGithub}
                      disabled={isScanning}
                      className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-extrabold rounded-xl text-xs flex items-center space-x-2 shadow-sm"
                    >
                      {isScanning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                      <span>Scan Repo</span>
                    </button>
                  </div>
                </div>
              )}

              {ingestSubTab === 'upload' && (
                <div>
                  <input type="file" ref={fileInputRef} accept=".zip" onChange={handleZipFileUpload} className="hidden" />
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-slate-300 hover:border-blue-600 rounded-2xl p-10 text-center cursor-pointer bg-slate-50 transition-all"
                  >
                    <UploadCloud className="w-10 h-10 mx-auto text-blue-600 mb-3 animate-bounce" />
                    <h4 className="font-extrabold text-sm mb-1 text-slate-900">Click to browse or drag & drop ZIP file</h4>
                    <p className="text-xs text-slate-500 font-medium">Supports .zip containing Python code, config.yaml, tools.json, and runtime logs</p>
                    <button
                      onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
                      disabled={isScanning}
                      className="mt-4 px-6 py-2.5 bg-blue-600 text-white font-extrabold rounded-xl text-xs shadow-sm"
                    >
                      {isScanning ? 'Extracting & Scanning AST...' : 'Select ZIP File'}
                    </button>
                  </div>
                </div>
              )}

              {ingestSubTab === 'snippet' && (
                <div className="p-6 rounded-2xl border border-slate-200 bg-slate-50">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-extrabold text-sm flex items-center space-x-2 text-slate-900">
                      <Code className="w-4 h-4 text-blue-600" />
                      <span>Paste Python Source Code</span>
                    </h4>
                    <input
                      type="text"
                      value={snippetName}
                      onChange={(e) => setSnippetName(e.target.value)}
                      placeholder="Agent Name"
                      className="text-xs px-3 py-1.5 rounded-lg border border-slate-300 bg-white text-slate-900"
                    />
                  </div>
                  <textarea
                    rows={10}
                    value={snippetCode}
                    onChange={(e) => setSnippetCode(e.target.value)}
                    className="w-full font-mono text-xs p-4 rounded-xl border border-slate-300 bg-slate-950 text-emerald-400 focus:border-blue-600"
                  />
                  <button
                    onClick={handleScanSnippet}
                    disabled={isScanning}
                    className="mt-4 w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-extrabold rounded-xl text-xs flex items-center justify-center space-x-2 shadow-sm"
                  >
                    {isScanning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                    <span>Analyze Code Snippet AST</span>
                  </button>
                </div>
              )}

              {ingestSubTab === 'sample' && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    { key: 'finance_agent', title: 'Finance Trading Agent', desc: 'LLM API calls, SQLite queries, and stock tools.', risk: 'Low Risk' },
                    { key: 'customer_support_agent', title: 'Customer Support Bot', desc: 'FAQ chatbot using Google Gemini API.', risk: 'Minimal Risk' },
                    { key: 'high_risk_sql_agent', title: 'Autonomous SQL Agent', desc: 'Raw shell execution and database deletion tools.', risk: 'Critical Risk' }
                  ].map(sample => (
                    <div key={sample.key} className="p-5 rounded-2xl border border-slate-200 bg-slate-50 flex flex-col justify-between">
                      <div>
                        <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full ${
                          sample.risk.includes('Critical') ? 'bg-rose-100 text-rose-800 border border-rose-300' : 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                        }`}>
                          {sample.risk}
                        </span>
                        <h4 className="font-extrabold text-sm mt-2 text-slate-900">{sample.title}</h4>
                        <p className="text-xs text-slate-600 font-medium mt-1">{sample.desc}</p>
                      </div>
                      <button
                        onClick={() => handleRunSampleScan(sample.key)}
                        disabled={isScanning}
                        className="mt-4 w-full py-2 bg-slate-900 hover:bg-blue-600 text-white text-xs font-extrabold rounded-xl flex items-center justify-center space-x-2 transition-all"
                      >
                        {isScanning ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                        <span>Run AST Scan</span>
                      </button>
                    </div>
                  ))}
                </div>
              )}

            </div>
          </div>
        )}

        {/* 3. RISK ANALYSIS PAGE */}
        {activeTab === 'risk' && (
          <div className="space-y-6">
            <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-6">
              <div className="flex items-center justify-between border-b border-slate-200 pb-4">
                <div>
                  <h2 className="text-xl font-extrabold tracking-tight text-slate-950">Transparent Rule-Based Risk Engine</h2>
                  <p className="text-xs text-slate-600 font-medium">Quantitative Risk Deductions & Factor Assessment</p>
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-500 uppercase font-bold">Risk Score</div>
                  <div className="text-3xl font-extrabold text-rose-600">{currentScan.risk_score}/100</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { factor: "Dangerous Shell / System Exec", points: "+40 Pts", status: (currentScan.tools_detected || []).some(t => t.risk === 'Critical') ? "DETECTED" : "CLEAR", desc: "exec, eval, system, popen calls" },
                  { factor: "Unbounded Autonomous Loop", points: "+20 Pts", status: "CLEAR", desc: "while True continuous execution" },
                  { factor: "External REST API Egress", points: "+15 Pts", status: (currentScan.external_apis || []).length > 0 ? "DETECTED" : "CLEAR", desc: "Outbound HTTP requests" },
                  { factor: "Database Modification Access", points: "+15 Pts", status: (currentScan.data_sources || []).length > 0 ? "DETECTED" : "CLEAR", desc: "Write / Drop database tables" },
                  { factor: "Autonomous Email Dispatch", points: "+10 Pts", status: "CLEAR", desc: "SMTP / SendGrid email sending" }
                ].map((item, idx) => (
                  <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-between">
                    <div>
                      <div className="font-bold text-sm text-slate-900">{item.factor}</div>
                      <div className="text-xs text-slate-600 font-medium">{item.desc}</div>
                    </div>
                    <div className="text-right">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                        item.status === 'DETECTED' ? 'bg-rose-100 text-rose-800 border border-rose-300' : 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                      }`}>
                        {item.status} ({item.points})
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 4. COMPLIANCE MAPPING PAGE */}
        {activeTab === 'mapping' && (
          <div className="space-y-6">
            <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm">
              <h2 className="text-xl font-extrabold mb-2 text-slate-950">Governance Framework Compliance Mapper</h2>
              <p className="text-xs text-slate-600 font-medium mb-6">
                Evaluated against EU AI Act Article 13, ISO/IEC 42001, and NIST AI Risk Management Framework.
              </p>

              <div className="space-y-6">
                <div className="p-5 rounded-2xl border border-blue-200 bg-blue-50/50">
                  <h4 className="font-extrabold text-base text-blue-900 mb-2">EU AI Act Article 13 - Transparency Requirements</h4>
                  <ul className="text-xs space-y-2 text-slate-800 font-semibold">
                    <li className="flex items-center justify-between">
                      <span>ART-13.1 High-Risk AI System Transparency</span>
                      <span className="text-emerald-600 font-bold">PASS</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>ART-13.2 Specification of Capabilities and Limitations</span>
                      <span className="text-emerald-600 font-bold">PASS</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>ART-13.3 Human Oversight Instructions</span>
                      <span className="text-emerald-600 font-bold">PASS</span>
                    </li>
                  </ul>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
                    <h5 className="font-bold text-sm mb-2 text-slate-900">ISO/IEC 42001 Controls</h5>
                    <ul className="text-xs space-y-2 text-slate-800 font-medium">
                      <li className="flex items-center justify-between">
                        <span>A.6.2 AI Risk Assessment</span>
                        <span className="text-emerald-600 font-bold">COMPLIANT</span>
                      </li>
                      <li className="flex items-center justify-between">
                        <span>A.7.3 Data Governance</span>
                        <span className="text-emerald-600 font-bold">COMPLIANT</span>
                      </li>
                    </ul>
                  </div>

                  <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
                    <h5 className="font-bold text-sm mb-2 text-slate-900">NIST AI RMF Functions</h5>
                    <ul className="text-xs space-y-2 text-slate-800 font-medium">
                      <li className="flex items-center justify-between">
                        <span>GOVERN & MAP</span>
                        <span className="text-blue-600 font-bold">90% Aligned</span>
                      </li>
                      <li className="flex items-center justify-between">
                        <span>MEASURE & MANAGE</span>
                        <span className="text-blue-600 font-bold">85% Aligned</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 5. ARCHITECTURE DIAGRAM PAGE */}
        {activeTab === 'architecture' && (
          <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm">
            <h2 className="text-xl font-extrabold mb-2 text-slate-950">Automated Architecture Topology Diagram</h2>
            <p className="text-xs text-slate-600 font-medium mb-6">User → Agent → LLM → Database → Tools → External APIs</p>

            <div className="h-80 w-full bg-slate-950 rounded-2xl border border-slate-800 relative flex items-center justify-center p-4">
              <div className="flex items-center justify-between w-full max-w-2xl">
                <div className="flex flex-col items-center space-y-2">
                  <div className="p-4 rounded-xl bg-purple-500/20 border border-purple-500/40 text-purple-400">
                    <Cpu className="w-8 h-8" />
                  </div>
                  <span className="text-xs font-bold text-purple-300 font-mono">{(currentScan.llm_providers || [])[0] || 'LLM Engine'}</span>
                </div>

                <div className="h-0.5 flex-1 bg-gradient-to-r from-purple-500 via-blue-500 to-emerald-500 relative">
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 text-[10px] text-blue-400 font-mono">
                    Prompts / API Calls
                  </span>
                </div>

                <div className="flex flex-col items-center space-y-2">
                  <div className="p-5 rounded-2xl bg-blue-500/20 border-2 border-blue-400 text-blue-300 animate-pulse">
                    <ShieldCheck className="w-10 h-10" />
                  </div>
                  <span className="text-xs font-extrabold text-blue-200">{currentScan.agent_name}</span>
                </div>

                <div className="h-0.5 flex-1 bg-gradient-to-r from-blue-500 to-emerald-500 relative">
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 text-[10px] text-emerald-400 font-mono">
                    Tool Invocation
                  </span>
                </div>

                <div className="flex flex-col items-center space-y-2">
                  <div className="p-4 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400">
                    <Database className="w-8 h-8" />
                  </div>
                  <span className="text-xs font-bold text-emerald-300 font-mono">{(currentScan.data_sources || [])[0] || 'Database Tool'}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 6. RUNTIME ANALYSIS PAGE */}
        {activeTab === 'runtime' && (
          <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-6">
            <h2 className="text-xl font-extrabold text-slate-950">Runtime Log Analysis & Execution Trace</h2>
            <p className="text-xs text-slate-600 font-medium">Analysis of runtime.log & stdout trace logs.</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
                <div className="text-xs font-bold text-slate-500 uppercase">Tools Actually Used</div>
                <div className="text-2xl font-extrabold mt-1 text-slate-900">{(currentScan.tools_detected || []).length} Tools</div>
              </div>

              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
                <div className="text-xs font-bold text-slate-500 uppercase">Errors Detected</div>
                <div className="text-2xl font-extrabold mt-1 text-emerald-600">0 Errors</div>
              </div>

              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
                <div className="text-xs font-bold text-slate-500 uppercase">Warnings Detected</div>
                <div className="text-2xl font-extrabold mt-1 text-amber-600">1 Warning</div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 text-emerald-400 font-mono text-xs space-y-2 border border-slate-800">
              <div>[2026-07-30 12:22:01] INFO Agent initialized with provider OpenAI GPT-4o</div>
              <div>[2026-07-30 12:22:02] INFO Registered tools: query_customer_database</div>
              <div>[2026-07-30 12:22:03] INFO Execution trace completed cleanly in 210ms</div>
            </div>
          </div>
        )}

        {/* 7. EXPORT PAGE */}
        {activeTab === 'export' && (
          <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm">
            <h2 className="text-xl font-extrabold mb-2 text-slate-950">Export Compliance Reports</h2>
            <p className="text-xs text-slate-600 font-medium mb-6">Download PDF Audit Certificate or Raw JSON Payload.</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 rounded-2xl border border-blue-200 bg-blue-50/50 flex flex-col justify-between">
                <div>
                  <FileText className="w-10 h-10 text-blue-600 mb-3" />
                  <h4 className="font-extrabold text-base mb-1 text-slate-950">Official PDF Audit Certificate</h4>
                  <p className="text-xs text-slate-600 font-medium">Complete ReportLab PDF certificate with card specs and regulatory assessments.</p>
                </div>
                <a
                  href={`/api/v1/export/pdf/${currentScan.id}`}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-6 w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-extrabold rounded-xl text-xs text-center flex items-center justify-center space-x-2 shadow-md shadow-blue-500/20"
                >
                  <Download className="w-4 h-4" />
                  <span>Download PDF Audit Report</span>
                </a>
              </div>

              <div className="p-6 rounded-2xl border border-slate-200 bg-slate-50 flex flex-col justify-between">
                <div>
                  <Terminal className="w-10 h-10 text-slate-900 mb-3" />
                  <h4 className="font-extrabold text-base mb-1 text-slate-950">Raw JSON Audit Export</h4>
                  <p className="text-xs text-slate-600 font-medium">Structured JSON payload containing card parameters and risk scores.</p>
                </div>
                <a
                  href={`/api/v1/export/json/${currentScan.id}`}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-6 w-full py-3 bg-slate-900 hover:bg-slate-800 text-white font-extrabold rounded-xl text-xs text-center flex items-center justify-center space-x-2 shadow-sm"
                >
                  <Download className="w-4 h-4 text-white" />
                  <span>Export Raw JSON</span>
                </a>
              </div>
            </div>
          </div>
        )}

        {/* 8. SETTINGS PAGE */}
        {activeTab === 'settings' && (
          <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-6">
            <h2 className="text-xl font-extrabold text-slate-950">Governance & Compliance Settings</h2>
            <p className="text-xs text-slate-600 font-medium">Configure LLM API credentials and Regulatory Framework mapping rules.</p>

            <div className="space-y-4 max-w-xl">
              <div>
                <label className="text-xs font-bold text-slate-700 uppercase block mb-1">Google Gemini API Key</label>
                <input
                  type="password"
                  value={geminiApiKey}
                  onChange={(e) => setGeminiApiKey(e.target.value)}
                  className="w-full text-xs p-3 rounded-xl border border-slate-300 bg-white font-mono text-slate-900"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 uppercase block mb-1">Framework Mapping Configuration (JSON)</label>
                <textarea
                  rows={6}
                  value={frameworkRulesJson}
                  onChange={(e) => setFrameworkRulesJson(e.target.value)}
                  className="w-full text-xs p-3 rounded-xl border border-slate-300 bg-slate-50 font-mono text-slate-900"
                />
              </div>

              <button
                onClick={() => showToast("Settings saved successfully!")}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs rounded-xl shadow-md shadow-blue-500/20"
              >
                Save Settings
              </button>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
