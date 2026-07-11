from app.application.rules import (
    RefundPolicyEngine,
    RefundRuleConfig,
)
from app.domain.entities import ComplaintAnalysis, Transaction
from app.domain.enums import (
    DecisionMode,
    Intent,
    Severity,
    TransactionStatus,
)


def analysis(
    intent: Intent = Intent.FAILED_PAYMENT,
) -> ComplaintAnalysis:
    return ComplaintAnalysis(
        intent=intent,
        severity=Severity.MEDIUM,
        language="en",
        summary="Payment failed after debit.",
        confidence=0.9,
        transaction_required=True,
    )


def transaction(
    amount: float,
    status: TransactionStatus = TransactionStatus.SUCCESS,
) -> Transaction:
    return Transaction(
        customer_id="customer",
        amount=amount,
        payment_method="UPI",
        status=status,
        order_reference=f"order-{amount}",
        error_code="PAYMENT_CALLBACK_TIMEOUT",
    )


def test_small_refund_is_automatic():
    engine = RefundPolicyEngine(RefundRuleConfig(automatic_limit=500, approval_limit=2000))
    decision = engine.evaluate(transaction(449), analysis())
    assert decision is not None
    assert decision.mode == DecisionMode.AUTOMATIC


def test_medium_refund_requires_approval():
    engine = RefundPolicyEngine(RefundRuleConfig(automatic_limit=500, approval_limit=2000))
    decision = engine.evaluate(transaction(1499), analysis())
    assert decision is not None
    assert decision.mode == DecisionMode.APPROVAL_REQUIRED


def test_large_refund_escalates():
    engine = RefundPolicyEngine(RefundRuleConfig(automatic_limit=500, approval_limit=2000))
    decision = engine.evaluate(transaction(3299), analysis())
    assert decision is not None
    assert decision.mode == DecisionMode.HUMAN_ESCALATION


def test_unrelated_intent_produces_no_action():
    engine = RefundPolicyEngine(RefundRuleConfig(automatic_limit=500, approval_limit=2000))
    assert engine.evaluate(transaction(449), analysis(Intent.FAQ)) is None
