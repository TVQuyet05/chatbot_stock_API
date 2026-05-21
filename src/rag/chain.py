"""
RAG chain — combines Milvus retriever with Gemini LLM.
"""

import logging
import time
from typing import Optional

from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import Milvus

from src.core.config import get_settings
from src.core.constants import RAG_PROMPT_TEMPLATE, NO_CONTEXT_RESPONSE
from src.db.milvus_store import search_similar
from src.rag.prompts import format_context

logger = logging.getLogger(__name__)


def get_llm():
    """
    Initialise Google Gemini LLM.

    Returns None when GEMINI_API_KEY is not configured.
    """
    settings = get_settings()

    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
        logger.warning("GEMINI_API_KEY not configured — running in retrieval-only mode")
        return None

    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3,
        max_output_tokens=2048,
    )
    logger.info("Connected to Gemini model: %s", settings.GEMINI_MODEL)
    return llm


def create_rag_chain(vector_store: Milvus):
    """
    Build a RAG chain using LCEL (LangChain Expression Language).
    """
    llm = get_llm()
    if llm is None:
        return None

    settings = get_settings()

    # 1. Setup Retriever
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": settings.TOP_K},
    )

    # 2. Setup Prompt
    prompt = PromptTemplate(
        template=RAG_PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )

    # 3. Create LCEL Chain
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser

    def format_docs(docs):
        return format_context(docs)

    # This is the modern way to build RAG in LangChain
    chain = (
        {
            "context": retriever | format_docs, 
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    logger.info("RAG LCEL chain ready")
    return chain


def ask_question(
    query: str,
    vector_store: Milvus,
    rag_chain=None,
) -> dict:
    """
    Process a question and return an answer with sources.

    Args:
        query: User question.
        vector_store: Connected Milvus store.
        rag_chain: Optional RAG chain (None → retrieval-only mode).

    Returns:
        Dict with ``answer``, ``sources``, and ``processing_time``.
    """
    settings = get_settings()
    start = time.perf_counter()

    if rag_chain:
        try:
            # Generate answer using the LCEL chain
            answer = rag_chain.invoke(query)
            # Manually retrieve source docs for the response metadata
            source_docs = search_similar(vector_store, query, top_k=settings.TOP_K)
        except Exception as e:
            logger.error("Gemini LLM error, falling back to retrieval-only: %s", e)
            source_docs = search_similar(vector_store, query, top_k=settings.TOP_K)
            if not source_docs:
                answer = NO_CONTEXT_RESPONSE
            else:
                context = format_context(source_docs)
                answer = (
                    "⚠️ **Chế độ Tạm thời (LLM Fallback)**\n"
                    "Hiện tại dịch vụ AI đang bận hoặc gặp lỗi quota. "
                    "Dưới đây là các đoạn văn bản pháp luật liên quan trực tiếp đến câu hỏi của bạn:\n\n"
                    f"{context}"
                )
    else:
        source_docs = search_similar(vector_store, query, top_k=settings.TOP_K)

        if not source_docs:
            answer = NO_CONTEXT_RESPONSE
        else:
            context = format_context(source_docs)
            answer = (
                "📋 **Chế độ Retrieval-Only** (chưa có Gemini API key)\n"
                "Dưới đây là các đoạn văn bản pháp luật liên quan:\n\n"
                f"{context}\n\n"
                "💡 Thêm GEMINI_API_KEY vào .env để nhận câu trả lời tổng hợp từ AI."
            )

    elapsed = time.perf_counter() - start

    sources = [
        {
            "document_name": doc.metadata.get("ten_van_ban", "N/A"),
            "article_number": doc.metadata.get("dieu_so", "N/A"),
            "similarity_score": doc.metadata.get("similarity_score", 0.0),
        }
        for doc in source_docs
    ]

    return {
        "answer": answer,
        "sources": sources,
        "processing_time": round(elapsed, 3),
    }
