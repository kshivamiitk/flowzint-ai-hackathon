from app.domain.entities import ComplaintAnalysis, Customer, PolicyDocument, Transaction
from app.domain.exceptions import ExternalServiceError
from app.domain.ports import AnswerGenerator, ComplaintAnalyzer


class FallbackComplaintAnalyzer:
    """Uses deterministic analysis when a hosted free-tier model is unavailable."""

    def __init__(
        self,
        primary: ComplaintAnalyzer,
        fallback: ComplaintAnalyzer,
    ) -> None:
        self._primary = primary
        self._fallback = fallback

    async def analyze(self, message: str) -> ComplaintAnalysis:
        try:
            return await self._primary.analyze(message)
        except ExternalServiceError:
            return await self._fallback.analyze(message)


class FallbackAnswerGenerator:
    """Keeps grounded responses available during provider errors or rate limits."""

    def __init__(
        self,
        primary: AnswerGenerator,
        fallback: AnswerGenerator,
    ) -> None:
        self._primary = primary
        self._fallback = fallback

    async def generate(
        self,
        *,
        message: str,
        analysis: ComplaintAnalysis,
        policies: list[PolicyDocument],
        customer: Customer,
        transaction: Transaction | None,
        action_summary: str | None,
    ) -> str:
        try:
            return await self._primary.generate(
                message=message,
                analysis=analysis,
                policies=policies,
                customer=customer,
                transaction=transaction,
                action_summary=action_summary,
            )
        except ExternalServiceError:
            return await self._fallback.generate(
                message=message,
                analysis=analysis,
                policies=policies,
                customer=customer,
                transaction=transaction,
                action_summary=action_summary,
            )
