"""
Prompt utilities for the RAG pipeline.
"""

from typing import List

from langchain_core.documents import Document

from src.core.constants import CONTEXT_TEMPLATE


def format_context(documents: List[Document]) -> str:
    """
    Format retrieved documents into a context string for the LLM prompt.

    Args:
        documents: Documents returned by the vector store.

    Returns:
        Formatted context string.
    """
    if not documents:
        return "Không tìm thấy tài liệu tham khảo phù hợp."

    parts: list[str] = []
    for doc in documents:
        source = doc.metadata.get("ten_van_ban", doc.metadata.get("source", "N/A"))
        article = doc.metadata.get("dieu_so", "N/A")
        content = doc.page_content.strip()
        parts.append(
            CONTEXT_TEMPLATE.format(source=source, article=article, content=content)
        )

    return "\n---\n".join(parts)
