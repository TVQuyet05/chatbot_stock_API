"""
Milvus vector store connection and operations.
"""

import logging
from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import Milvus
from pymilvus import connections, utility

from src.core.config import get_settings

logger = logging.getLogger(__name__)


def create_milvus_store(
    embeddings,
    documents: Optional[List[Document]] = None,
    collection_name: Optional[str] = None,
) -> Milvus:
    """
    Create or connect to a Milvus vector store.

    Args:
        embeddings: Embedding model instance.
        documents: If provided, ingest these documents (drops existing collection).
        collection_name: Override collection name (defaults to settings).

    Returns:
        Milvus vector store instance.
    """
    settings = get_settings()
    collection_name = collection_name or settings.MILVUS_COLLECTION

    logger.info("Connecting to Milvus: %s:%s", settings.MILVUS_HOST, settings.MILVUS_PORT)

    # Ensure default pymilvus connection exists
    try:
        existing = [alias for alias, _ in connections.list_connections()]
        if "default" not in existing:
            connections.connect(
                alias="default",
                host=settings.MILVUS_HOST,
                port=str(settings.MILVUS_PORT),
            )
            logger.info("Established default pymilvus connection")
    except Exception as exc:
        logger.warning("pymilvus connection issue: %s", exc)

    connection_args = {
        "host": settings.MILVUS_HOST,
        "port": str(settings.MILVUS_PORT),
    }

    if documents:
        logger.info("Ingesting %d chunks into Milvus …", len(documents))

        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)
            logger.info("Dropped existing collection: %s", collection_name)

        vector_store = Milvus.from_documents(
            documents=documents,
            embedding=embeddings,
            collection_name=collection_name,
            connection_args=connection_args,
        )
        logger.info("Ingested %d chunks successfully", len(documents))
    else:
        vector_store = Milvus(
            embedding_function=embeddings,
            collection_name=collection_name,
            connection_args=connection_args,
        )
        logger.info("Connected to Milvus collection: %s", collection_name)

    return vector_store


def search_similar(
    vector_store: Milvus,
    query: str,
    top_k: Optional[int] = None,
) -> List[Document]:
    """
    Perform semantic similarity search.

    Returns documents with similarity_score attached to metadata.
    """
    settings = get_settings()
    top_k = top_k or settings.TOP_K

    results = vector_store.similarity_search_with_score(query=query, k=top_k)

    docs: List[Document] = []
    for doc, score in results:
        doc.metadata["similarity_score"] = round(score, 4)
        docs.append(doc)

    return docs
