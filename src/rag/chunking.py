"""
Chunking module optimised for Vietnamese legal text.

Strategy:
- Split by Điều (Article) — the fundamental legal unit
- Long articles are sub-split by khoản using RecursiveCharacterTextSplitter
- Rich metadata: document name, article number, title
"""

import logging
import re
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.config import get_settings

logger = logging.getLogger(__name__)


def split_by_articles(document: Document) -> List[Document]:
    """
    Split a legal document by Điều (Article).

    Each article becomes a chunk. Articles that exceed *MAX_CHUNK_SIZE*
    are sub-split using ``RecursiveCharacterTextSplitter``.
    """
    settings = get_settings()
    content = document.page_content
    base_metadata = document.metadata.copy()

    article_pattern = re.compile(r"(?=Điều\s+\d+[\.\:])")
    parts = article_pattern.split(content)

    fallback_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.MAX_CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", r"\n(?=\d+\.)", r"\n(?=[a-z]\))", "\n", ". ", " "],
        is_separator_regex=True,
    )

    chunks: List[Document] = []

    for part in parts:
        part = part.strip()
        if not part:
            continue

        article_match = re.match(r"Điều\s+(\d+)[\.\:]?\s*(.*)", part, re.DOTALL)
        if article_match:
            article_num = article_match.group(1)
            article_title = part.split("\n")[0].strip()
        else:
            article_num = "0"
            article_title = "Phần mở đầu / Mục"

        chunk_metadata = {
            **base_metadata,
            "dieu_so": article_num,
            "tieu_de_dieu": article_title,
        }

        if len(part) > settings.MAX_CHUNK_SIZE:
            sub_docs = fallback_splitter.create_documents(
                texts=[part],
                metadatas=[chunk_metadata],
            )
            for i, sub_doc in enumerate(sub_docs):
                sub_doc.metadata["phan"] = f"{i + 1}/{len(sub_docs)}"
                sub_doc.metadata["tieu_de_dieu"] = article_title
            chunks.extend(sub_docs)
        else:
            if len(part) < 50:
                continue
            chunks.append(Document(page_content=part, metadata=chunk_metadata))

    return chunks


def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Split all documents into optimised chunks.

    Returns a flat list of all chunks across all input documents.
    """
    all_chunks: List[Document] = []

    for doc in documents:
        doc_name = doc.metadata.get("ten_van_ban", "Unknown")
        chunks = split_by_articles(doc)
        all_chunks.extend(chunks)
        logger.info("%s: %d chunks", doc_name, len(chunks))

    if all_chunks:
        sizes = [len(c.page_content) for c in all_chunks]
        logger.info(
            "Total: %d chunks | avg %d chars | min %d | max %d",
            len(all_chunks),
            sum(sizes) // len(sizes),
            min(sizes),
            max(sizes),
        )

    return all_chunks
