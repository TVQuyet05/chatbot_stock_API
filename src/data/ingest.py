"""
Data ingestion pipeline — load → chunk → embed → store in Milvus.

Usage:
    python -m src.data.ingest
"""

import logging
import sys
import time

from src.core.config import get_settings
from src.data.loader import load_text_files
from src.rag.chunking import chunk_documents
from src.rag.embedding import get_embedding_model
from src.db.milvus_store import create_milvus_store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the full ingestion pipeline."""
    settings = get_settings()
    start = time.time()

    logger.info("=== INGESTION PIPELINE START ===")

    # Step 1 — Load documents
    logger.info("Step 1: Loading documents from %s", settings.KNOWLEDGE_DIR)
    documents = load_text_files(settings.KNOWLEDGE_DIR)
    if not documents:
        logger.error("No documents found. Check KNOWLEDGE_DIR.")
        sys.exit(1)

    # Step 2 — Chunk
    logger.info("Step 2: Chunking documents")
    chunks = chunk_documents(documents)
    if not chunks:
        logger.error("No chunks generated.")
        sys.exit(1)

    # Step 3 — Embedding model
    logger.info("Step 3: Loading embedding model")
    embeddings = get_embedding_model()

    # Step 4 — Store in Milvus
    logger.info("Step 4: Storing vectors in Milvus")
    try:
        create_milvus_store(
            embeddings=embeddings,
            documents=chunks,
            collection_name=settings.MILVUS_COLLECTION,
        )
    except Exception as exc:
        logger.error("Milvus error: %s", exc)
        logger.info("Make sure Docker + Milvus are running: docker-compose up -d")
        sys.exit(1)

    elapsed = time.time() - start
    logger.info("=== INGESTION COMPLETE ===")
    logger.info("Documents: %d | Chunks: %d | Time: %.1fs", len(documents), len(chunks), elapsed)


if __name__ == "__main__":
    main()
