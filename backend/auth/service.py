"""
Authentication service using Supabase Auth (free tier).
Supports email/password sign-up, sign-in, and token verification.
"""

from typing import Optional
from db.supabase_client import get_supabase
from db.models import UserSignUp, UserSignIn, UserResponse


class AuthService:
    """Handles user authentication via Supabase Auth."""

    @staticmethod
    def sign_up(data: UserSignUp) -> dict:
        """Register a new user."""
        try:
            result = get_supabase().auth.sign_up(
                {
                    "email": data.email,
                    "password": data.password,
                }
            )

            if result.user:
                return {
                    "success": True,
                    "user": {
                        "id": result.user.id,
                        "email": result.user.email,
                    },
                    "message": "User created. Check email for confirmation.",
                }
            return {"success": False, "message": "Sign up failed"}

        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def sign_in(data: UserSignIn) -> dict:
        """Sign in an existing user."""
        try:
            result = get_supabase().auth.sign_in_with_password(
                {
                    "email": data.email,
                    "password": data.password,
                }
            )

            if result.user and result.session:
                return {
                    "success": True,
                    "user": {
                        "id": result.user.id,
                        "email": result.user.email,
                        "access_token": result.session.access_token,
                        "refresh_token": result.session.refresh_token,
                    },
                }
            return {"success": False, "message": "Invalid credentials"}

        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_user(token: str) -> Optional[dict]:
        """Verify a JWT token and return user info."""
        try:
            result = get_supabase().auth.get_user(token)
            if result.user:
                return {
                    "id": result.user.id,
                    "email": result.user.email,
                }
            return None
        except Exception:
            return None

    @staticmethod
    def sign_out(token: str) -> bool:
        """Sign out a user."""
        try:
            get_supabase().auth.sign_out(token)
            return True
        except Exception:
            return False