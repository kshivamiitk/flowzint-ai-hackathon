import pytest

from app.core.config import Settings
from app.infrastructure.ai.factory import build_ai_components
from app.infrastructure.ai.local import LocalHashEmbeddingProvider
from app.infrastructure.ai.openai_compatible import (
    OpenAICompatibleEmbeddingProvider,
)


def test_openai_compatible_local_endpoint_does_not_require_api_key():
    settings = Settings(
        ai_provider="openai_compatible",
        llm_base_url="http://localhost:11434/v1",
        llm_api_key="",
        llm_model="llama3",
        embedding_model="local",
    )

    components = build_ai_components(settings)

    assert components.closable_client is not None
    assert isinstance(components.embedding_provider, LocalHashEmbeddingProvider)


def test_openai_compatible_external_endpoint_requires_api_key():
    settings = Settings(
        ai_provider="openai_compatible",
        llm_base_url="https://example.com/v1",
        llm_api_key="",
        llm_model="provider-model",
        embedding_model="local",
    )

    with pytest.raises(ValueError, match="CHATBOT_API_KEY"):
        build_ai_components(settings)


def test_openai_compatible_uses_remote_embeddings_when_model_is_not_local():
    settings = Settings(
        ai_provider="openai_compatible",
        llm_base_url="https://example.com/v1",
        llm_api_key="test-key",
        llm_model="provider-model",
        embedding_model="text-embedding-3-small",
    )

    components = build_ai_components(settings)

    assert components.closable_client is not None
    assert isinstance(components.embedding_provider, OpenAICompatibleEmbeddingProvider)
