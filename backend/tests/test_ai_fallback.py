import pytest

from app.domain.entities import ComplaintAnalysis, Customer
from app.domain.enums import Intent, Severity
from app.domain.exceptions import ExternalServiceError
from app.infrastructure.ai.fallback import (
    FallbackAnswerGenerator,
    FallbackComplaintAnalyzer,
)
from app.infrastructure.ai.local import LocalAnswerGenerator, LocalComplaintAnalyzer


class UnavailableAnalyzer:
    async def analyze(self, message: str) -> ComplaintAnalysis:
        raise ExternalServiceError("rate limited")


class UnavailableAnswerGenerator:
    async def generate(self, **kwargs) -> str:
        raise ExternalServiceError("rate limited")


@pytest.mark.asyncio
async def test_analyzer_falls_back_when_hosted_provider_is_unavailable():
    analyzer = FallbackComplaintAnalyzer(UnavailableAnalyzer(), LocalComplaintAnalyzer())
    result = await analyzer.analyze("Payment charged but no order was created")
    assert result.intent == Intent.FAILED_PAYMENT
    assert result.severity == Severity.MEDIUM


@pytest.mark.asyncio
async def test_answer_generator_falls_back_when_hosted_provider_is_unavailable():
    generator = FallbackAnswerGenerator(
        UnavailableAnswerGenerator(),
        LocalAnswerGenerator(),
    )
    result = await generator.generate(
        message="What happened?",
        analysis=ComplaintAnalysis(
            intent=Intent.OTHER,
            severity=Severity.LOW,
            language="en",
            summary="General question",
            confidence=0.7,
            transaction_required=False,
        ),
        policies=[],
        customer=Customer(name="Demo User", email="demo@example.com"),
        transaction=None,
        action_summary=None,
    )
    assert result.startswith("Hi Demo,")
