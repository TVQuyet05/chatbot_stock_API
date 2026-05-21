import pytest
from src.auth.jwt_handler import create_access_token, verify_access_token
from jose import JWTError

def test_jwt_flow():
    client_id = "test_client"
    token, expires_in = create_access_token(client_id)
    assert token is not None
    assert expires_in > 0
    
    payload = verify_access_token(token)
    assert payload["sub"] == client_id

def test_invalid_token():
    with pytest.raises(JWTError):
        verify_access_token("invalid_token")
