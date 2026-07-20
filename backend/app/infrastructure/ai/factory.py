from dataclasses import dataclass
from urllib.parse import urlparse

from app.core.config import Settings
from app.domain.ports import (
    AnswerGenerator,
    ComplaintAnalyzer,
    EmbeddingProvider,
)
from app.infrastructure.ai.fallback import (
    FallbackAnswerGenerator,
    FallbackComplaintAnalyzer,
)
from app.infrastructure.ai.local import (
    LocalAnswerGenerator,
    LocalComplaintAnalyzer,
    LocalHashEmbeddingProvider,
)
from app.infrastructure.ai.openai_compatible import (
    OpenAICompatibleAnswerGenerator,
    OpenAICompatibleClient,
    OpenAICompatibleComplaintAnalyzer,
    OpenAICompatibleEmbeddingProvider,
)

LOCAL_OPENAI_COMPATIBLE_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "host.docker.internal",
}
LOCAL_EMBEDDING_MODEL_NAMES = {"local", "hash", "local_hash"}


@dataclass(slots=True)
class AIComponents:
    analyzer: ComplaintAnalyzer
    answer_generator: AnswerGenerator
    embedding_provider: EmbeddingProvider
    closable_client: OpenAICompatibleClient | None = None


def _requires_api_key(base_url: str) -> bool:
    host = urlparse(base_url).hostname
    return host not in LOCAL_OPENAI_COMPATIBLE_HOSTS


def build_ai_components(settings: Settings) -> AIComponents:
    if settings.ai_provider == "openai_compatible":
        if not settings.llm_api_key and _requires_api_key(settings.llm_base_url):
            raise ValueError(
                "LLM_API_KEY or CHATBOT_API_KEY is required for external "
                "AI_PROVIDER=openai_compatible endpoints. Use AI_PROVIDER=local "
                "for the built-in free mode, or use a local endpoint such as "
                "http://localhost:11434/v1."
            )
        client = OpenAICompatibleClient(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            embedding_model=settings.embedding_model,
            timeout=settings.request_timeout_seconds,
        )
        embedding_provider: EmbeddingProvider
        if settings.embedding_model.lower() in LOCAL_EMBEDDING_MODEL_NAMES:
            embedding_provider = LocalHashEmbeddingProvider()
        else:
            embedding_provider = OpenAICompatibleEmbeddingProvider(client)
        return AIComponents(
            analyzer=FallbackComplaintAnalyzer(
                OpenAICompatibleComplaintAnalyzer(client),
                LocalComplaintAnalyzer(),
            ),
            answer_generator=FallbackAnswerGenerator(
                OpenAICompatibleAnswerGenerator(client),
                LocalAnswerGenerator(),
            ),
            embedding_provider=embedding_provider,
            closable_client=client,
        )

    return AIComponents(
        analyzer=LocalComplaintAnalyzer(),
        answer_generator=LocalAnswerGenerator(),
        embedding_provider=LocalHashEmbeddingProvider(),
    )
