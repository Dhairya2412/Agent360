"""Tests for Chroma client configuration."""

import pytest

from app.config import Settings
from app.vectorstore.chroma_client import _mock_embedding


def test_mock_embedding_dimension_matches_openai():
    vec = _mock_embedding("test document chunk", 1536)
    assert len(vec) == 1536
    assert all(-1.0 <= v <= 1.0 for v in vec)


def test_mock_embedding_is_deterministic():
    a = _mock_embedding("same text", 1536)
    b = _mock_embedding("same text", 1536)
    assert a == b


def test_mock_embedding_differs_for_different_text():
    a = _mock_embedding("text one", 1536)
    b = _mock_embedding("text two", 1536)
    assert a != b


def test_chroma_cloud_settings_defaults():
    s = Settings(
        chroma_use_cloud=True,
        chroma_tenant="21b63392-6e72-4f1f-828b-0fb0e9abe21b",
        chroma_database="AgentOps360",
    )
    assert s.chroma_database == "AgentOps360"
    assert s.embedding_dimension == 1536
    assert s.chroma_collection_name == "agentops360_knowledge"
