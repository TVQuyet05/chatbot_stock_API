import pytest
from langchain_core.documents import Document
from src.rag.chunking import split_by_articles

def test_split_by_articles_basic():
    doc = Document(page_content="Điều 1. Phạm vi điều chỉnh\nNội dung điều 1.\nĐiều 2. Đối tượng\nNội dung điều 2.", metadata={"source": "test.txt"})
    chunks = split_by_articles(doc)
    assert len(chunks) == 2
    assert chunks[0].metadata["dieu_so"] == "1"
    assert chunks[1].metadata["dieu_so"] == "2"

def test_split_by_articles_empty():
    doc = Document(page_content="", metadata={})
    chunks = split_by_articles(doc)
    assert len(chunks) == 0
