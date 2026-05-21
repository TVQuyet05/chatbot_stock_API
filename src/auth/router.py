"""
Authentication and Admin routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from src.api.dependencies import verify_admin
from src.api.schemas import (
    ClientRegisterRequest,
    ClientRegisterResponse,
    TokenResponse,
    TokenRequest,
    ClientListResponse,
    ClientInfo,
    MessageResponse
)
from src.auth.oauth2 import (
    register_client,
    authenticate_client,
    list_clients,
    delete_client,
    reset_client_secret
)
from src.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/register", response_model=ClientRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(request: ClientRegisterRequest):
    """Register a new API client."""
    result = await register_client(request.name)
    return result


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(request: TokenRequest):
    """
    OAuth2 client credentials token issuance.
    Exchange client_id and client_secret for a JWT.
    """
    client = await authenticate_client(request.client_id, request.client_secret)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect client_id or client_secret",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token, expires_in = create_access_token(client.client_id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in
    }


# Support for standard OAuth2 form login (useful for Swagger UI)
@router.post("/token/form", include_in_schema=False)
async def token_form(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    client = await authenticate_client(form_data.username, form_data.password)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token, expires_in = create_access_token(client.client_id)
    return {"access_token": access_token, "token_type": "bearer"}


@admin_router.get("/clients", response_model=ClientListResponse, dependencies=[Depends(verify_admin)])
async def get_all_clients():
    """List all registered API clients (Admin only)."""
    clients = await list_clients()
    return {
        "total": len(clients),
        "clients": [
            ClientInfo(
                client_id=c.client_id,
                name=c.name,
                tier=c.tier,
                is_active=c.is_active,
                created_at=c.created_at,
                request_count=c.request_count
            ) for c in clients
        ]
    }


@admin_router.delete("/clients/{client_id}", response_model=MessageResponse, dependencies=[Depends(verify_admin)])
async def deactivate_client(client_id: str):
    """Revoke/Deactivate an API client (Admin only)."""
    success = await delete_client(client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deactivated successfully"}


@admin_router.post("/clients/{client_id}/reset-secret", response_model=MessageResponse, dependencies=[Depends(verify_admin)])
async def reset_secret(client_id: str):
    """Generate a new secret for a client (Admin only)."""
    new_secret = await reset_client_secret(client_id)
    if not new_secret:
        raise HTTPException(status_code=404, detail="Client not found or inactive")
    return {
        "message": "Secret reset successfully",
        "detail": f"New client_secret: {new_secret} (Store this securely!)"
    }
