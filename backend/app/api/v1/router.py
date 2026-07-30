from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.scans import router as scans_router
from app.api.v1.compliance import router as compliance_router
from app.api.v1.frameworks import router as frameworks_router
from app.api.v1.diff import router as diff_router
from app.api.v1.graph import router as graph_router
from app.api.v1.audit_rag import router as audit_rag_router
from app.api.v1.export import router as export_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(scans_router, prefix="/scans", tags=["Agent Scans"])
api_router.include_router(compliance_router, prefix="/compliance", tags=["Compliance Cards"])
api_router.include_router(frameworks_router, prefix="/frameworks", tags=["Governance Frameworks"])
api_router.include_router(diff_router, prefix="/diff", tags=["Version Diff"])
api_router.include_router(graph_router, prefix="/graph", tags=["Architecture Graph Topology"])
api_router.include_router(audit_rag_router, prefix="/audit-rag", tags=["RAG Audit Assistant"])
api_router.include_router(export_router, prefix="/export", tags=["PDF & JSON Exporter"])
