import hashlib
import math
import re
from collections import Counter

from app.domain.entities import (
    ComplaintAnalysis,
    Customer,
    PolicyDocument,
    Transaction,
)
from app.domain.enums import Intent, Severity


class LocalHashEmbeddingProvider:
    """Dependency-free feature hashing for demos, tests, and offline judging."""

    def __init__(self, dimensions: int = 128) -> None:
        self._dimensions = dimensions

    async def embed(self, text: str) -> list[float]:
        normalized = self._normalize(text)
        tokens = re.findall(r"[a-z0-9]+", normalized)
        trigrams = [normalized[index : index + 3] for index in range(max(0, len(normalized) - 2))]
        vector = [0.0] * self._dimensions
        for feature, count in Counter(tokens + trigrams).items():
            digest = hashlib.sha256(feature.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self._dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign * float(count)
        norm = math.sqrt(sum(value * value for value in vector))
        return [value / norm for value in vector] if norm else vector

    @staticmethod
    def _normalize(text: str) -> str:
        replacements = {
            "deduct ho gaya": "money deducted",
            "payment ho gaya": "payment completed",
            "confirm nahi hua": "order failed",
            "booking confirm nahi hui": "order failed",
            "paisa kat gaya": "money deducted",
            "refund chahiye": "refund requested",
        }
        normalized = text.lower().strip()
        for source, target in replacements.items():
            normalized = normalized.replace(source, target)
        return normalized


class LocalComplaintAnalyzer:
    """Readable deterministic analyzer used when no remote LLM is configured."""

    async def analyze(self, message: str) -> ComplaintAnalysis:
        text = message.lower()
        payment_terms = [
            "deduct",
            "debited",
            "charged",
            "payment",
            "paisa kat",
            "money deducted",
        ]
        order_failure_terms = [
            "not confirm",
            "nahi hua",
            "failed",
            "no order",
            "order confirm",
            "booking",
            "not created",
        ]
        refund_terms = ["refund", "money back", "wapas", "return my money"]
        delivery_terms = ["delivery", "late", "parcel", "shipment"]
        account_terms = ["account", "login", "password", "otp"]

        if any(term in text for term in payment_terms) and any(
            term in text for term in order_failure_terms
        ):
            intent = Intent.FAILED_PAYMENT
            summary = "Payment was deducted but the order was not completed."
            transaction_required = True
            confidence = 0.93
        elif any(term in text for term in refund_terms):
            intent = Intent.REFUND_REQUEST
            summary = "Customer requested a refund for a transaction."
            transaction_required = True
            confidence = 0.88
        elif any(term in text for term in delivery_terms):
            intent = Intent.DELIVERY_ISSUE
            summary = "Customer reported a delivery problem."
            transaction_required = False
            confidence = 0.84
        elif any(term in text for term in account_terms):
            intent = Intent.ACCOUNT_ISSUE
            summary = "Customer reported an account access problem."
            transaction_required = False
            confidence = 0.82
        elif "policy" in text or "how" in text or "what" in text:
            intent = Intent.FAQ
            summary = "Customer asked a policy or product question."
            transaction_required = False
            confidence = 0.75
        else:
            intent = Intent.OTHER
            summary = message[:180]
            transaction_required = False
            confidence = 0.62

        critical_terms = ["fraud", "stolen", "emergency", "legal"]
        high_terms = ["angry", "urgent", "immediately", "scam"]
        if any(term in text for term in critical_terms):
            severity = Severity.CRITICAL
        elif any(term in text for term in high_terms):
            severity = Severity.HIGH
        elif intent in {Intent.FAILED_PAYMENT, Intent.REFUND_REQUEST}:
            severity = Severity.MEDIUM
        else:
            severity = Severity.LOW

        language = (
            "hinglish" if any(term in text for term in ["bhai", "nahi", "gaya", "paisa"]) else "en"
        )
        return ComplaintAnalysis(
            intent=intent,
            severity=severity,
            language=language,
            summary=summary,
            confidence=confidence,
            transaction_required=transaction_required,
        )


class LocalAnswerGenerator:
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
        references = ", ".join(f"{policy.title} §{policy.section}" for policy in policies)
        greeting = f"Hi {customer.name.split()[0]},"
        if analysis.intent == Intent.FAILED_PAYMENT and transaction:
            core = (
                f" I found transaction {transaction.order_reference} for "
                f"₹{transaction.amount:.0f}. The payment was recorded while "
                "order completion failed."
            )
        elif analysis.intent == Intent.REFUND_REQUEST and transaction:
            core = (
                f" I reviewed transaction {transaction.order_reference} for "
                f"₹{transaction.amount:.0f}."
            )
        else:
            core = " I reviewed your request against the available support policies."

        action_text = (
            f" {action_summary}." if action_summary else " No account action was required."
        )
        evidence = f" Policy sources: {references}." if references else ""
        return f"{greeting}{core}{action_text}{evidence}"
