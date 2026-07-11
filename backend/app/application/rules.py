from dataclasses import dataclass

from app.domain.entities import ActionDecision, ComplaintAnalysis, Transaction
from app.domain.enums import ActionType, DecisionMode, Intent, TransactionStatus


@dataclass(frozen=True, slots=True)
class RefundRuleConfig:
    automatic_limit: float
    approval_limit: float


class RefundPolicyEngine:
    """Deterministic authorization policy; the LLM never authorizes money movement."""

    def __init__(self, config: RefundRuleConfig) -> None:
        self._config = config

    def evaluate(
        self,
        transaction: Transaction | None,
        analysis: ComplaintAnalysis,
    ) -> ActionDecision | None:
        if analysis.intent not in {Intent.FAILED_PAYMENT, Intent.REFUND_REQUEST}:
            return None

        if transaction is None:
            return ActionDecision(
                mode=DecisionMode.HUMAN_ESCALATION,
                action_type=ActionType.ESCALATE_TO_HUMAN,
                reason="No transaction could be verified for this request.",
                policy_reference="REFUND-1.1",
            )

        if transaction.status == TransactionStatus.REFUNDED:
            return ActionDecision(
                mode=DecisionMode.REJECT,
                action_type=ActionType.ISSUE_REFUND,
                reason="The transaction has already been refunded.",
                policy_reference="REFUND-1.4",
            )

        eligible_status = transaction.status in {
            TransactionStatus.SUCCESS,
            TransactionStatus.FAILED,
        }
        has_failure_evidence = (
            bool(transaction.error_code) or analysis.intent == Intent.FAILED_PAYMENT
        )
        if not eligible_status or not has_failure_evidence:
            return ActionDecision(
                mode=DecisionMode.REJECT,
                action_type=ActionType.ISSUE_REFUND,
                reason="The transaction does not meet failed-payment refund criteria.",
                policy_reference="REFUND-2.1",
            )

        if transaction.amount <= self._config.automatic_limit:
            mode = DecisionMode.AUTOMATIC
        elif transaction.amount <= self._config.approval_limit:
            mode = DecisionMode.APPROVAL_REQUIRED
        else:
            mode = DecisionMode.HUMAN_ESCALATION

        return ActionDecision(
            mode=mode,
            action_type=ActionType.ISSUE_REFUND,
            reason="Payment was recorded but order completion failed.",
            policy_reference="REFUND-2.1",
        )
