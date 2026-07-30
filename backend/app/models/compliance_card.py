import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, ForeignKey
from app.db.database import Base


class ComplianceCard(Base):
    __tablename__ = "compliance_cards"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("agent_scans.id"), nullable=False, index=True)
    
    # Standard compliance card sections
    agent_purpose = Column(Text, nullable=True)
    llm_and_version = Column(String, nullable=True)
    tool_inventory = Column(JSON, default=list)
    data_sources = Column(JSON, default=list)
    decision_authority = Column(String, default="Autonomous with Thresholds")
    human_oversight = Column(String, default="Human-in-the-Loop")
    risk_classification = Column(String, default="Medium Risk")
    known_limitations = Column(JSON, default=list)
    incident_contact = Column(String, default="security@enterprise.com")
    
    # Completeness check data
    completeness_score = Column(Float, default=100.0)
    missing_fields = Column(JSON, default=list)
    placeholder_warnings = Column(JSON, default=list)
    
    # Full raw card payload
    raw_card_json = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    role = Column(String, nullable=False)
    action = Column(String, nullable=False)  # SCAN_CREATED, POLICY_UPDATED, REPORT_EXPORTED
    details = Column(Text, nullable=True)
    ip_address = Column(String, default="127.0.0.1")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
