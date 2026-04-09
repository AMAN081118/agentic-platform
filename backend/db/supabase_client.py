"""
Supabase client — singleton connection manager.
Handles all direct communication with Supabase (Postgres + Auth).
"""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class SupabaseManager:
    """Singleton manager for Supabase client."""

    _instance: Optional["SupabaseManager"] = None
    _client: Optional[Client] = None

    def __new__(cls) -> "SupabaseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def client(self) -> Client:
        if self._client is None:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")

            if not url or not key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_KEY must be set in .env"
                )

            self._client = create_client(url, key)
            print("✅ Supabase client initialized")

        return self._client


# Global accessor
def get_supabase() -> Client:
    """Get the Supabase client singleton."""
    return SupabaseManager().client