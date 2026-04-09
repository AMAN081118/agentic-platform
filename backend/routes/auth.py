"""
Auth routes — sign up, sign in, get current user.
"""

from fastapi import APIRouter, Depends
from db.models import UserSignUp, UserSignIn
from auth.service import AuthService
from auth.dependencies import get_current_user

router = APIRouter()


@router.post("/auth/signup")
async def signup(data: UserSignUp):
    """Register a new user."""
    result = AuthService.sign_up(data)
    if not result["success"]:
        return {"error": result["message"]}, 400
    return result


@router.post("/auth/signin")
async def signin(data: UserSignIn):
    """Sign in and receive tokens."""
    result = AuthService.sign_in(data)
    if not result["success"]:
        return {"error": result["message"]}, 401
    return result


@router.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    """Get current authenticated user."""
    return {"user": user}