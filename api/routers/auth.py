"""Endpoint /auth/login · échange username/password contre JWT."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ..schemas import LoginRequest, TokenResponse
from ..security import create_access_token, verify_credentials

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest) -> TokenResponse:
    if not verify_credentials(req.username, req.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="bad credentials",
        )
    token = create_access_token(subject=req.username)
    return TokenResponse(access_token=token)
