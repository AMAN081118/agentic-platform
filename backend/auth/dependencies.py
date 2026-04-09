"""
FastAPI dependencies for authentication.
Use as route dependencies for protected endpoints.
"""

from fastapi import Depends, HTTPException, Header
from typing import Optional
from auth.service import AuthService


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> dict:
    """
    Extract and verify user from the Authorization header.
    Returns user dict or raises 401.

    Usage:
        @router.get("/protected")
        async def protected(user: dict = Depends(get_current_user)):
            ...
    """
    if not authorization:
        # Allow anonymous access — return default user
        return {"id": "anonymous", "email": "anonymous@local"}

    # Expect: "Bearer <token>"
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = parts[1]
    user = AuthService.get_user(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user


async def get_optional_user(
    authorization: Optional[str] = Header(None),
) -> dict:
    """
    Same as get_current_user but never raises — returns anonymous fallback.
    Useful for endpoints that work with or without auth.
    """
    if not authorization:
        return {"id": "anonymous", "email": "anonymous@local"}

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return {"id": "anonymous", "email": "anonymous@local"}

    token = parts[1]
    user = AuthService.get_user(token)
    return user or {"id": "anonymous", "email": "anonymous@local"}