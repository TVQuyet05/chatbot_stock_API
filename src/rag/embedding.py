"""
Embedding model using vietnamese-bi-encoder for Vietnamese text.

Uses a singleton pattern to avoid reloading the ~800MB model.
"""

import logging
from threading import Lock

from langchain_huggingface import HuggingFaceEmbeddings

from src.core.config import get_settings

logger = logging.getLogger(__name__)

_embedding_model: HuggingFaceEmbeddings | None = None
_lock = Lock()


def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Return the embedding model (singleton).

    Thread-safe: uses a lock to prevent concurrent model loading.
    """
    global _embedding_model

    if _embedding_model is not None:
        return _embedding_model

    with _lock:
        # Double-check after acquiring lock
        if _embedding_model is not None:
            return _embedding_model

        settings = get_settings()
        logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)

        _embedding_model = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={
                "normalize_embeddings": True,
                "batch_size": 32,
            },
        )

        logger.info("Embedding model loaded successfully")
        return _embedding_model
