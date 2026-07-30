import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from app.db.database import Base


class AgentScan(Base):
    __tablename__ = "agent_scans"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, index=True, nullable=False)
    version = Column(String, default="1.0.0")
    source_type = Column(String, default="upload")  # zip, folder, github, sample
    source_path = Column(String, nullable=True)
    framework = Column(String, default="Custom Python")  # LangChain, AutoGen, CrewAI, LlamaIndex, Custom
    
    # Quantitative metrics
    compliance_score = Column(Float, default=0.0)  # 0 - 100
    risk_score = Column(Float, default=0.0)        # 0 - 100
    risk_tier = Column(String, default="Unclassified")  # Minimal, Low, Medium, High, Critical
    
    # Detected capabilities (JSON lists)
    llm_providers = Column(JSON, default=list)  # ["OpenAI", "Google Gemini", "Anthropic"]
    tools_detected = Column(JSON, default=list) # [{"name": "db_query", "category": "Database"}]
    data_sources = Column(JSON, default=list)   # ["PostgreSQL", "S3 Bucket", "Local Files"]
    external_apis = Column(JSON, default=list)  # ["Stripe", "Twilio", "REST API"]
    
    # Framework compliance evaluations (JSON dicts)
    framework_compliance = Column(JSON, default=dict) # {"eu_ai_act": {...}, "iso_42001": {...}, "nist_ai_rmf": {...}}
    
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
