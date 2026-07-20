import pytest

from app.domain.enums import Intent
from app.infrastructure.ai.openai_compatible import OpenAICompatibleComplaintAnalyzer


class FakeJsonClient:
    async def chat_json(self, system: str, user: str) -> dict:
        return {
            "intent": "failed_payment",
            "severity": "high",
            "language": "hinglish",
            "summary": "Payment deducted but order was not confirmed.",
            "confidence": 0.82,
            "transaction_required": False,
        }


@pytest.mark.asyncio
async def test_failed_payment_requires_transaction_even_when_model_says_false():
    analyzer = OpenAICompatibleComplaintAnalyzer(FakeJsonClient())

    analysis = await analyzer.analyze("Payment deduct ho gaya but order confirm nahi hua.")

    assert analysis.intent == Intent.FAILED_PAYMENT
    assert analysis.transaction_required is True
