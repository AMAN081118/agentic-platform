"""
LLM Provider — manages LLM instances.
Supports Groq free tier.
"""

import os
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from dotenv import load_dotenv

load_dotenv()


class LLMProvider:
    """Factory for LLM instances."""

    _instances: dict[str, BaseChatModel] = {}

    @classmethod
    def get(
        cls,
        model: Optional[str] = None,
        temperature: float = 0.7,
        streaming: bool = True,
    ) -> BaseChatModel:
        model = model or os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")
        cache_key = f"{model}_{temperature}_{streaming}"

        if cache_key not in cls._instances:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not set in .env")

            cls._instances[cache_key] = ChatGroq(
                api_key=api_key,
                model=model,
                temperature=temperature,
                streaming=streaming,
                max_tokens=2048,
            )

        return cls._instances[cache_key]

    @classmethod
    def get_for_decision(
        cls,
        model: Optional[str] = None,
        temperature: float = 0.1,
    ) -> BaseChatModel:
        """
        Get LLM for structured decision making.
        NO json_mode — we parse the output ourselves.
        Low temperature for consistency.
        """
        model = model or os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")
        cache_key = f"decision_{model}_{temperature}"

        if cache_key not in cls._instances:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not set in .env")

            cls._instances[cache_key] = ChatGroq(
                api_key=api_key,
                model=model,
                temperature=temperature,
                streaming=False,
                max_tokens=1024,
            )

        return cls._instances[cache_key]