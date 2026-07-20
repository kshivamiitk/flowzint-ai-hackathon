from collections.abc import Callable

from app.application.action_service import ActionWorkflowService
from app.application.dto import (
    ChatResponse,
    MessageRequest,
    PolicyReferenceDTO,
    ResolutionTraceStepDTO,
)
from app.application.incident_service import IncidentDetectionService
from app.application.mappers import to_action_dto, to_incident_dto
from app.domain.entities import Action, AuditEvent, Conversation, Transaction
from app.domain.enums import ActionStatus
from app.domain.exceptions import EntityNotFoundError
from app.domain.ports import (
    AnswerGenerator,
    ComplaintAnalyzer,
    EmbeddingProvider,
    UnitOfWork,
)


class ChatOrchestrator:
    """Coordinates one support turn while delegating focused responsibilities."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        analyzer: ComplaintAnalyzer,
        answer_generator: AnswerGenerator,
        embedding_provider: EmbeddingProvider,
        action_workflow: ActionWorkflowService,
        incident_detector: IncidentDetectionService,
        automatic_limit: float,
        approval_limit: float,
    ) -> None:
        self._uow_factory = uow_factory
        self._analyzer = analyzer
        self._answer_generator = answer_generator
        self._embedding_provider = embedding_provider
        self._action_workflow = action_workflow
        self._incident_detector = incident_detector
        self._automatic_limit = automatic_limit
        self._approval_limit = approval_limit

    async def handle(self, request: MessageRequest) -> ChatResponse:
        analysis = await self._analyzer.analyze(request.message)
        embedding = await self._embedding_provider.embed(analysis.summary)

        async with self._uow_factory() as uow:
            customer = await uow.customers.get(request.customer_id)
            if not customer:
                raise EntityNotFoundError("Customer not found")

            transaction = (
                await uow.transactions.latest_for_customer(customer.id)
                if analysis.transaction_required
                else None
            )
            if transaction:
                analysis.attributes.update(
                    {
                        "transaction_id": transaction.id,
                        "payment_method": transaction.payment_method,
                        "app_version": transaction.app_version,
                        "error_code": transaction.error_code,
                    }
                )

            policies = await uow.policies.search(embedding, limit=3)
            conversation = Conversation(
                customer_id=customer.id,
                message=request.message,
                analysis=analysis,
                embedding=embedding,
                assistant_response="",
                policy_references=[f"{item.title} §{item.section}" for item in policies],
                transaction_id=transaction.id if transaction else None,
            )
            await uow.conversations.add(conversation)
            await uow.audits.add(
                AuditEvent(
                    event_type="complaint_classified",
                    actor="ai_analyzer",
                    conversation_id=conversation.id,
                    details={
                        "intent": analysis.intent,
                        "severity": analysis.severity,
                        "confidence": analysis.confidence,
                    },
                )
            )
            await uow.commit()

        action = await self._action_workflow.propose_and_process(
            customer_id=customer.id,
            conversation_id=conversation.id,
            transaction=transaction,
            analysis=analysis,
        )

        action_summary = None
        if action:
            action_summary = (
                f"Action {action.action_type.value} is {action.status.value}. "
                f"Reference: {action.external_reference or 'pending'}"
            )

        answer = await self._answer_generator.generate(
            message=request.message,
            analysis=analysis,
            policies=policies,
            customer=customer,
            transaction=transaction,
            action_summary=action_summary,
        )
        conversation.assistant_response = answer

        async with self._uow_factory() as uow:
            await uow.conversations.add(conversation)
            await uow.commit()

        incident = await self._incident_detector.detect(conversation)
        decision_mode, risk_level = self._decision_profile(action, transaction)
        return ChatResponse(
            conversation_id=conversation.id,
            message=answer,
            intent=analysis.intent,
            severity=analysis.severity,
            language=analysis.language,
            confidence=analysis.confidence,
            decision_mode=decision_mode,
            risk_level=risk_level,
            resolution_trace=self._build_trace(
                analysis=analysis,
                transaction=transaction,
                policies=policies,
                action=action,
                incident=incident,
                decision_mode=decision_mode,
            ),
            policy_references=[
                PolicyReferenceDTO(title=item.title, section=item.section) for item in policies
            ],
            action=to_action_dto(action) if action else None,
            incident=to_incident_dto(incident) if incident else None,
        )

    def _decision_profile(
        self,
        action: Action | None,
        transaction: Transaction | None,
    ) -> tuple[str, str]:
        if action is None:
            return "information_only", "none"
        if action.status == ActionStatus.REJECTED:
            return "blocked_by_policy", "blocked"
        if transaction is None or action.amount > self._approval_limit:
            return "human_escalation", "high"
        if action.amount > self._automatic_limit:
            return "approval_required", "medium"
        return "automatic", "low"

    @staticmethod
    def _build_trace(
        *,
        analysis,
        transaction,
        policies,
        action,
        incident,
        decision_mode: str,
    ) -> list[ResolutionTraceStepDTO]:
        transaction_detail = (
            f"Verified {transaction.order_reference} for ₹{transaction.amount:,.0f}."
            if transaction
            else "No matching transaction was loaded."
        )
        policy_detail = (
            ", ".join(f"{item.title} §{item.section}" for item in policies)
            if policies
            else "No policy evidence was retrieved."
        )
        if action:
            action_detail = (
                f"{action.action_type.value.replace('_', ' ')} is "
                f"{action.status.value.replace('_', ' ')}."
            )
            action_status = "complete" if action.status == ActionStatus.COMPLETED else "attention"
        else:
            action_detail = "No account or monetary action was required."
            action_status = "not_needed"
        incident_detail = (
            f"Detected {incident.affected_customer_count} affected customers."
            if incident
            else "Complaint similarity is being monitored."
        )
        return [
            ResolutionTraceStepDTO(
                id="understand",
                label="Understand",
                status="complete",
                detail=(
                    f"{analysis.intent.value.replace('_', ' ')} at "
                    f"{analysis.confidence:.0%} confidence."
                ),
            ),
            ResolutionTraceStepDTO(
                id="verify",
                label="Verify",
                status="complete" if transaction else "attention",
                detail=transaction_detail,
            ),
            ResolutionTraceStepDTO(
                id="ground",
                label="Ground",
                status="complete" if policies else "attention",
                detail=policy_detail,
            ),
            ResolutionTraceStepDTO(
                id="authorize",
                label="Authorize",
                status="attention" if decision_mode == "human_escalation" else "complete",
                detail=(
                    "Deterministic policy selected "
                    f"{decision_mode.replace('_', ' ')}; the LLM cannot authorize funds."
                ),
            ),
            ResolutionTraceStepDTO(
                id="act",
                label="Act",
                status=action_status,
                detail=action_detail,
            ),
            ResolutionTraceStepDTO(
                id="detect",
                label="Detect",
                status="complete" if incident else "monitoring",
                detail=incident_detail,
            ),
        ]
