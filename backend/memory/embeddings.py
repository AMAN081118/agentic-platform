"""
Embedding service — generates vector embeddings using local sentence-transformers.
Model: all-MiniLM-L6-v2 (384 dimensions, fast, free, runs locally).
"""

import os
import time
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class EmbeddingService:
    """
    Generates text embeddings using sentence-transformers.
    Singleton pattern — model loads once and stays in memory.
    """

    _model = None
    _model_name: str = ""

    @classmethod
    def is_enabled(cls) -> bool:
        """Whether this instance is allowed to load the local ML model."""
        return os.getenv("ENABLE_EMBEDDINGS", "true").strip().lower() in {
            "1", "true", "yes", "on"
        }

    @classmethod
    def _load_model(cls) -> None:
        """Load the embedding model (lazy, one-time)."""
        if not cls.is_enabled():
            raise RuntimeError(
                "Embeddings are disabled (set ENABLE_EMBEDDINGS=true to enable them)."
            )

        if cls._model is not None:
            return

        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        cls._model_name = model_name

        print(f"📦 Loading embedding model: {model_name}...")
        start = time.time()

        try:
            from sentence_transformers import SentenceTransformer
            cls._model = SentenceTransformer(model_name)
            elapsed = time.time() - start
            print(f"✅ Embedding model loaded in {elapsed:.1f}s")
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {e}")

    @classmethod
    def embed(cls, text: str) -> list[float]:
        """
        Generate embedding for a single text string.

        Args:
            text: Input text to embed

        Returns:
            List of floats (384 dimensions for all-MiniLM-L6-v2)
        """
        cls._load_model()

        if not text or not text.strip():
            # Return zero vector for empty text
            dimension = cls.get_dimension()
            return [0.0] * dimension

        embedding = cls._model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    @classmethod
    def embed_batch(cls, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts at once (more efficient).

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        cls._load_model()

        if not texts:
            return []

        # Filter empty strings but track indices
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)

        if not valid_texts:
            dimension = cls.get_dimension()
            return [[0.0] * dimension for _ in texts]

        embeddings = cls._model.encode(valid_texts, normalize_embeddings=True)

        # Build result with zero vectors for empty inputs
        dimension = cls.get_dimension()
        result = [[0.0] * dimension for _ in texts]
        for idx, emb in zip(valid_indices, embeddings):
            result[idx] = emb.tolist()

        return result

    @classmethod
    def get_dimension(cls) -> int:
        """Get the embedding dimension for the current model."""
        cls._load_model()
        return cls._model.get_sentence_embedding_dimension()

    @classmethod
    def similarity(cls, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.
        Returns value between -1 and 1 (1 = identical meaning).
        """
        emb1 = cls.embed(text1)
        emb2 = cls.embed(text2)

        # Cosine similarity (embeddings are already normalized)
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        return dot_product

    @classmethod
    def get_model_info(cls) -> dict:
        """Get info about the loaded model."""
        if not cls.is_enabled():
            return {
                "enabled": False,
                "model_name": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            }

        cls._load_model()
        return {
            "enabled": True,
            "model_name": cls._model_name,
            "dimension": cls.get_dimension(),
            "max_seq_length": cls._model.max_seq_length,
        }
