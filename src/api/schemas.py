"""
Pydantic request / response schemas for the API.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ── RAG Endpoint ────────────────────────────────────────

class AskRequest(BaseModel):
    """Request body for POST /api/v1/ask."""

    question: str = Field(..., min_length=1, max_length=2000, description="User question")
    top_k: int = Field(5, ge=1, le=20, description="Number of context chunks to retrieve")


class SourceInfo(BaseModel):
    """A single source reference in the answer."""

    document_name: str
    article_number: str
    similarity_score: float


class AskResponse(BaseModel):
    """Response body for POST /api/v1/ask."""

    answer: str
    sources: List[SourceInfo]
    processing_time: float


# ── Health ──────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Response body for GET /api/v1/health."""

    status: str = "ok"
    version: str
    milvus_connected: bool


# ── Documents ───────────────────────────────────────────

class DocumentInfo(BaseModel):
    """Metadata about one available legal document."""

    name: str
    code: str
    doc_type: str


class DocumentListResponse(BaseModel):
    """Response body for GET /api/v1/documents."""

    total: int
    documents: List[DocumentInfo]


# ── Auth ────────────────────────────────────────────────

class ClientRegisterRequest(BaseModel):
    """Request body for POST /auth/register."""

    name: str = Field(..., min_length=2, max_length=100, description="Client / app name")


class ClientRegisterResponse(BaseModel):
    """Response body for POST /auth/register."""

    client_id: str
    client_secret: str
    name: str
    message: str = "Store the client_secret securely — it cannot be retrieved later."


class TokenRequest(BaseModel):
    """Request body for POST /auth/token."""

    client_id: str
    client_secret: str


class TokenResponse(BaseModel):
    """Response body for POST /auth/token."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ── Admin ───────────────────────────────────────────────

class ClientInfo(BaseModel):
    """Admin view of a registered client."""

    client_id: str
    name: str
    tier: str
    is_active: bool
    created_at: datetime
    request_count: int


class ClientListResponse(BaseModel):
    """Response body for GET /admin/clients."""

    total: int
    clients: List[ClientInfo]


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    detail: Optional[str] = None
