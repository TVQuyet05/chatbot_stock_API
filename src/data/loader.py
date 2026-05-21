"""
Data loader — reads Vietnamese legal documents from the knowledge directory.
"""

import glob
import logging
import os
from typing import List

from langchain_core.documents import Document

from src.core.constants import FILE_METADATA

logger = logging.getLogger(__name__)


def load_text_files(knowledge_dir: str) -> List[Document]:
    """
    Read all ``.txt`` files from *knowledge_dir*.

    Each file is returned as a single ``Document`` with metadata parsed
    from ``FILE_METADATA`` (document name, number, type).
    """
    documents: List[Document] = []
    txt_files = glob.glob(os.path.join(knowledge_dir, "*.txt"))

    if not txt_files:
        logger.warning("No .txt files found in: %s", knowledge_dir)
        return documents

    for file_path in sorted(txt_files):
        filename = os.path.basename(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                content = fh.read().strip()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="utf-8-sig") as fh:
                content = fh.read().strip()

        if not content:
            logger.warning("Empty file: %s", filename)
            continue

        metadata = FILE_METADATA.get(
            filename,
            {
                "ten_van_ban": filename.replace(".txt", ""),
                "so_hieu": filename.replace(".txt", ""),
                "loai_van_ban": "Không xác định",
            },
        )
        metadata = {**metadata, "source": filename}

        documents.append(Document(page_content=content, metadata=metadata))
        logger.info("Loaded: %s (%s chars)", metadata["ten_van_ban"], f"{len(content):,}")

    logger.info("Total: %d documents loaded", len(documents))
    return documents
