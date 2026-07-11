from collections.abc import Callable

from app.application.action_service import ActionWorkflowService
from app.application.dto import ChatResponse, MessageRequest, PolicyReferenceDTO
from app.application.incident_service import IncidentDetectionService
from app.application.mappers import to_action_dto, to_incident_dto
from app.domain.entities import AuditEvent, Conversation
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
    ) -> None:
        self._uow_factory = uow_factory
        self._analyzer = analyzer
        self._answer_generator = answer_generator
        self._embedding_provider = embedding_provider
        self._action_workflow = action_workflow
        self._incident_detector = incident_detector

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
        return ChatResponse(
            conversation_id=conversation.id,
            message=answer,
            intent=analysis.intent,
            severity=analysis.severity,
            language=analysis.language,
            confidence=analysis.confidence,
            policy_references=[
                PolicyReferenceDTO(title=item.title, section=item.section) for item in policies
            ],
            action=to_action_dto(action) if action else None,
            incident=to_incident_dto(incident) if incident else None,
        )
