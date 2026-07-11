from collections.abc import Callable

from app.application.rules import RefundPolicyEngine
from app.domain.entities import Action, AuditEvent, ComplaintAnalysis, Transaction
from app.domain.enums import ActionType, DecisionMode
from app.domain.exceptions import EntityNotFoundError
from app.domain.ports import ActionGateway, UnitOfWork


class ActionWorkflowService:
    """Owns action proposal, approval, execution, and audit transitions."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        rule_engine: RefundPolicyEngine,
        gateway: ActionGateway,
    ) -> None:
        self._uow_factory = uow_factory
        self._rule_engine = rule_engine
        self._gateway = gateway

    async def propose_and_process(
        self,
        *,
        customer_id: str,
        conversation_id: str,
        transaction: Transaction | None,
        analysis: ComplaintAnalysis,
    ) -> Action | None:
        decision = self._rule_engine.evaluate(transaction, analysis)
        if decision is None:
            return None

        transaction_id = transaction.id if transaction else None
        key = f"{decision.action_type}:{transaction_id or customer_id}"

        async with self._uow_factory() as uow:
            existing = await uow.actions.get_by_idempotency_key(key)
            if existing:
                return existing

            action = Action(
                customer_id=customer_id,
                transaction_id=transaction_id,
                conversation_id=conversation_id,
                action_type=decision.action_type,
                amount=transaction.amount if transaction else 0.0,
                reason=decision.reason,
                policy_reference=decision.policy_reference,
                idempotency_key=key,
            )

            if decision.mode == DecisionMode.AUTOMATIC:
                await uow.actions.add(action)
                await self._execute_within_uow(uow, action, transaction, actor="system")
            elif decision.mode in {
                DecisionMode.APPROVAL_REQUIRED,
                DecisionMode.HUMAN_ESCALATION,
            }:
                action.request_approval()
                await uow.actions.add(action)
                await uow.audits.add(
                    AuditEvent(
                        event_type="action_approval_requested",
                        actor="system",
                        action_id=action.id,
                        conversation_id=conversation_id,
                        details={
                            "mode": decision.mode,
                            "reason": action.reason,
                            "policy_reference": action.policy_reference,
                        },
                    )
                )
            else:
                action.reject(decision.reason)
                await uow.actions.add(action)
                await uow.audits.add(
                    AuditEvent(
                        event_type="action_rejected_by_policy",
                        actor="rule_engine",
                        action_id=action.id,
                        conversation_id=conversation_id,
                        details={"reason": decision.reason},
                    )
                )

            await uow.commit()
            return action

    async def approve(self, action_id: str, comment: str | None) -> Action:
        async with self._uow_factory() as uow:
            action = await uow.actions.get(action_id)
            if not action:
                raise EntityNotFoundError("Action not found")

            action.approve(comment)
            await uow.actions.update(action)
            transaction = (
                await uow.transactions.get(action.transaction_id) if action.transaction_id else None
            )
            await self._execute_within_uow(uow, action, transaction, actor="operator")
            await uow.commit()
            return action

    async def reject(self, action_id: str, comment: str | None) -> Action:
        async with self._uow_factory() as uow:
            action = await uow.actions.get(action_id)
            if not action:
                raise EntityNotFoundError("Action not found")

            action.reject(comment)
            await uow.actions.update(action)
            await uow.audits.add(
                AuditEvent(
                    event_type="action_rejected_by_operator",
                    actor="operator",
                    action_id=action.id,
                    conversation_id=action.conversation_id,
                    details={"comment": comment},
                )
            )
            await uow.commit()
            return action

    async def _execute_within_uow(
        self,
        uow: UnitOfWork,
        action: Action,
        transaction: Transaction | None,
        *,
        actor: str,
    ) -> None:
        if action.action_type != ActionType.ISSUE_REFUND or not transaction:
            # Unsupported actions stay in approval instead of pretending to execute.
            if action.status.value == "proposed":
                action.request_approval()
                await uow.actions.update(action)
            return

        action.start_execution()
        await uow.actions.update(action)
        try:
            reference = await self._gateway.issue_refund(transaction, action.amount)
            transaction.mark_refunded()
            action.complete(reference)
            await uow.transactions.update(transaction)
            await uow.actions.update(action)
            await uow.audits.add(
                AuditEvent(
                    event_type="refund_completed",
                    actor=actor,
                    action_id=action.id,
                    conversation_id=action.conversation_id,
                    details={
                        "amount": action.amount,
                        "transaction_id": transaction.id,
                        "external_reference": reference,
                        "policy_reference": action.policy_reference,
                    },
                )
            )
        except Exception as exc:
            action.fail(str(exc))
            await uow.actions.update(action)
            raise
