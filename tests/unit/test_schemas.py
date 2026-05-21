import pytest
from src.api.schemas import AskRequest, TokenRequest

def test_ask_request_validation():
    # Valid
    req = AskRequest(question="test question")
    assert req.question == "test question"
    assert req.top_k == 5
    
    # Invalid (too short)
    with pytest.raises(ValueError):
        AskRequest(question="")

def test_token_request_validation():
    req = TokenRequest(client_id="id", client_secret="secret")
    assert req.client_id == "id"
    assert req.client_secret == "secret"
