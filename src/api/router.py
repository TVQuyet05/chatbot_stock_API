"""
Giao diện API (RAG, Health, Documents).
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from src.api.dependencies import get_current_client, get_rag_chain, get_vector_store
from src.api.schemas import AskRequest, AskResponse, HealthResponse, DocumentListResponse, DocumentInfo
from src.core.config import get_settings
from src.core.constants import FILE_METADATA
from src.rag.chain import ask_question

router = APIRouter(prefix="/api/v1", tags=["API V1"])


@router.post("/ask", response_model=AskResponse)
async def query_rag(
    request: AskRequest,
    client: Annotated[object, Depends(get_current_client)],
    rag_chain: Annotated[object, Depends(get_rag_chain)],
    vector_store: Annotated[object, Depends(get_vector_store)]
):
    """
    Hỏi đáp về pháp luật chứng khoán Việt Nam (Yêu cầu OAuth2 Token).
    """
    try:
        result = ask_question(
            query=request.question,
            vector_store=vector_store,
            rag_chain=rag_chain
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Kiểm tra trạng thái dịch vụ."""
    settings = get_settings()
    # In a real app, we might check milvus connection here
    return {
        "version": settings.APP_VERSION,
        "milvus_connected": True  # Simplified for now
    }


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """Danh sách các văn bản pháp luật hiện có trong hệ thống."""
    docs = [
        DocumentInfo(
            name=meta["ten_van_ban"],
            code=meta["so_hieu"],
            doc_type=meta["loai_van_ban"]
        ) for meta in FILE_METADATA.values()
    ]
    return {
        "total": len(docs),
        "documents": docs
    }
