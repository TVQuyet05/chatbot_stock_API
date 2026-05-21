import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_milvus():
    return MagicMock()

@pytest.fixture
def mock_embeddings():
    return MagicMock()

@pytest.fixture
def mock_llm():
    return MagicMock()
