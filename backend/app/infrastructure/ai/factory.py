from dataclasses import dataclass

from app.core.config import Settings
from app.domain.ports import (
    AnswerGenerator,
    ComplaintAnalyzer,
    EmbeddingProvider,
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


@dataclass(slots=True)
class AIComponents:
    analyzer: ComplaintAnalyzer
    answer_generator: AnswerGenerator
    embedding_provider: EmbeddingProvider
    closable_client: OpenAICompatibleClient | None = None


def build_ai_components(settings: Settings) -> AIComponents:
    if settings.ai_provider == "openai_compatible":
        if not settings.llm_api_key:
            raise ValueError("LLM_API_KEY is required when AI_PROVIDER=openai_compatible")
        client = OpenAICompatibleClient(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            embedding_model=settings.embedding_model,
            timeout=settings.request_timeout_seconds,
        )
        return AIComponents(
            analyzer=OpenAICompatibleComplaintAnalyzer(client),
            answer_generator=OpenAICompatibleAnswerGenerator(client),
            embedding_provider=OpenAICompatibleEmbeddingProvider(client),
            closable_client=client,
        )

    return AIComponents(
        analyzer=LocalComplaintAnalyzer(),
        answer_generator=LocalAnswerGenerator(),
        embedding_provider=LocalHashEmbeddingProvider(),
    )
