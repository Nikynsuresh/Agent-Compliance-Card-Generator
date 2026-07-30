from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr, Field


# Auth Schemas
class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    full_name: Optional[str] = None

    class Config:
        from_attributes = True


# Scan Schemas
class AgentScanCreate(BaseModel):
    agent_name: str
    version: str = "1.0.0"
    source_type: str = "sample"  # sample, folder, zip, github
    sample_key: Optional[str] = None


class AgentScanResponse(BaseModel):
    id: int
    agent_name: str
    version: str
    source_type: str
    framework: str
    compliance_score: float
    risk_score: float
    risk_tier: str
    llm_providers: List[str]
    tools_detected: List[Dict[str, Any]]
    data_sources: List[str]
    external_apis: List[str]
    framework_compliance: Dict[str, Any]
    summary: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


# Compliance Card Schemas
class ComplianceCardResponse(BaseModel):
    id: int
    scan_id: int
    agent_purpose: Optional[str]
    llm_and_version: Optional[str]
    tool_inventory: List[Dict[str, Any]]
    data_sources: List[str]
    decision_authority: str
    human_oversight: str
    risk_classification: str
    known_limitations: List[str]
    incident_contact: str
    completeness_score: float
    missing_fields: List[str]
    placeholder_warnings: List[str]

    class Config:
        from_attributes = True


# Diff & Version Comparison Schemas
class DiffRequest(BaseModel):
    scan_id_v1: int
    scan_id_v2: int


class DiffResponse(BaseModel):
    agent_name: str
    v1_version: str
    v2_version: str
    score_change: float
    risk_score_change: float
    added_tools: List[Dict[str, Any]]
    removed_tools: List[Dict[str, Any]]
    llm_changes: List[str]
    data_source_changes: List[str]
    compliance_impacts: List[str]
    summary: str


# RAG Audit Assistant Schemas
class AuditQueryRequest(BaseModel):
    scan_id: int
    question: str


class AuditQueryResponse(BaseModel):
    question: str
    answer: str
    confidence: float
    sources: List[str]
    risk_flag: bool
