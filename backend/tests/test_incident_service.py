from app.application.incident_service import IncidentDetectionService
from app.domain.entities import ComplaintAnalysis, Conversation
from app.domain.enums import Intent, Severity


def conversation(error_code: str | None, embedding: list[float]) -> Conversation:
    return Conversation(
        customer_id="customer",
        message="Payment issue",
        analysis=ComplaintAnalysis(
            intent=Intent.FAILED_PAYMENT,
            severity=Severity.MEDIUM,
            language="en",
            summary="Payment issue",
            confidence=0.9,
            transaction_required=True,
            attributes={"error_code": error_code},
        ),
        embedding=embedding,
        assistant_response="",
        policy_references=[],
    )


def test_shared_error_signal_matches_even_when_summaries_differ():
    service = IncidentDetectionService(
        lambda: None,
        similarity_threshold=0.68,
        minimum_complaints=3,
        window_minutes=60,
    )
    assert service._matches(
        conversation("PAYMENT_CALLBACK_TIMEOUT", [1.0, 0.0]),
        conversation("PAYMENT_CALLBACK_TIMEOUT", [0.0, 1.0]),
    )


def test_unrelated_error_and_embedding_do_not_match():
    service = IncidentDetectionService(
        lambda: None,
        similarity_threshold=0.68,
        minimum_complaints=3,
        window_minutes=60,
    )
    assert not service._matches(
        conversation("PAYMENT_CALLBACK_TIMEOUT", [1.0, 0.0]),
        conversation("ORDER_VALIDATION_FAILED", [0.0, 1.0]),
    )
