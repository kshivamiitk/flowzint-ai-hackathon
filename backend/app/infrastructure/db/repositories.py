from dataclasses import asdict
from datetime import datetime
from math import sqrt

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import (
    Action,
    AuditEvent,
    Conversation,
    Customer,
    Incident,
    PolicyDocument,
    Transaction,
)
from app.domain.enums import ActionStatus, IncidentStatus
from app.infrastructure.db.mappers import (
    action_to_domain,
    audit_to_domain,
    conversation_to_domain,
    customer_to_domain,
    incident_to_domain,
    policy_to_domain,
    transaction_to_domain,
)
from app.infrastructure.db.models import (
    ActionModel,
    AuditEventModel,
    ConversationModel,
    CustomerModel,
    IncidentModel,
    PolicyModel,
    TransactionModel,
)


def _cosine(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0


class SqlAlchemyCustomerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, customer_id: str) -> Customer | None:
        model = await self._session.get(CustomerModel, customer_id)
        return customer_to_domain(model) if model else None

    async def list_all(self) -> list[Customer]:
        result = await self._session.scalars(select(CustomerModel).order_by(CustomerModel.name))
        return [customer_to_domain(item) for item in result]

    async def add(self, customer: Customer) -> None:
        self._session.add(CustomerModel(**asdict(customer)))


class SqlAlchemyTransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, transaction_id: str) -> Transaction | None:
        model = await self._session.get(TransactionModel, transaction_id)
        return transaction_to_domain(model) if model else None

    async def latest_for_customer(self, customer_id: str) -> Transaction | None:
        statement = (
            select(TransactionModel)
            .where(TransactionModel.customer_id == customer_id)
            .order_by(TransactionModel.created_at.desc())
            .limit(1)
        )
        model = await self._session.scalar(statement)
        return transaction_to_domain(model) if model else None

    async def list_for_customer(self, customer_id: str) -> list[Transaction]:
        result = await self._session.scalars(
            select(TransactionModel)
            .where(TransactionModel.customer_id == customer_id)
            .order_by(TransactionModel.created_at.desc())
        )
        return [transaction_to_domain(item) for item in result]

    async def add(self, transaction: Transaction) -> None:
        values = asdict(transaction)
        values["status"] = transaction.status.value
        self._session.add(TransactionModel(**values))

    async def update(self, transaction: Transaction) -> None:
        model = await self._session.get(TransactionModel, transaction.id)
        if model:
            model.status = transaction.status.value
            model.refunded_at = transaction.refunded_at


class SqlAlchemyPolicyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, policy: PolicyDocument) -> None:
        self._session.add(PolicyModel(**asdict(policy)))

    async def list_all(self) -> list[PolicyDocument]:
        result = await self._session.scalars(select(PolicyModel))
        return [policy_to_domain(item) for item in result]

    async def search(self, embedding: list[float], limit: int = 3) -> list[PolicyDocument]:
        policies = await self.list_all()
        policies.sort(key=lambda item: _cosine(item.embedding, embedding), reverse=True)
        return policies[:limit]


class SqlAlchemyConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, conversation: Conversation) -> None:
        model = await self._session.get(ConversationModel, conversation.id)
        values = {
            "customer_id": conversation.customer_id,
            "transaction_id": conversation.transaction_id,
            "incident_id": conversation.incident_id,
            "message": conversation.message,
            "assistant_response": conversation.assistant_response,
            "intent": conversation.analysis.intent.value,
            "severity": conversation.analysis.severity.value,
            "language": conversation.analysis.language,
            "summary": conversation.analysis.summary,
            "confidence": conversation.analysis.confidence,
            "transaction_required": conversation.analysis.transaction_required,
            "attributes": conversation.analysis.attributes,
            "embedding": conversation.embedding,
            "policy_references": conversation.policy_references,
            "created_at": conversation.created_at,
        }
        if model:
            for key, value in values.items():
                setattr(model, key, value)
        else:
            self._session.add(ConversationModel(id=conversation.id, **values))

    async def list_recent(self, since: datetime) -> list[Conversation]:
        result = await self._session.scalars(
            select(ConversationModel)
            .where(ConversationModel.created_at >= since)
            .order_by(ConversationModel.created_at.desc())
        )
        return [conversation_to_domain(item) for item in result]

    async def attach_incident(self, conversation_ids: list[str], incident_id: str) -> None:
        if conversation_ids:
            await self._session.execute(
                update(ConversationModel)
                .where(ConversationModel.id.in_(conversation_ids))
                .values(incident_id=incident_id)
            )


class SqlAlchemyIncidentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, incident_id: str) -> Incident | None:
        model = await self._session.get(IncidentModel, incident_id)
        return incident_to_domain(model) if model else None

    async def find_open_by_fingerprint(self, fingerprint: str) -> Incident | None:
        model = await self._session.scalar(
            select(IncidentModel)
            .where(
                IncidentModel.fingerprint == fingerprint,
                IncidentModel.status != IncidentStatus.RESOLVED.value,
            )
            .order_by(IncidentModel.created_at.desc())
            .limit(1)
        )
        return incident_to_domain(model) if model else None

    async def list_all(self) -> list[Incident]:
        result = await self._session.scalars(
            select(IncidentModel).order_by(IncidentModel.updated_at.desc())
        )
        return [incident_to_domain(item) for item in result]

    async def add(self, incident: Incident) -> None:
        values = asdict(incident)
        values["status"] = incident.status.value
        self._session.add(IncidentModel(**values))

    async def update(self, incident: Incident) -> None:
        model = await self._session.get(IncidentModel, incident.id)
        if model:
            model.description = incident.description
            model.probable_root_cause = incident.probable_root_cause
            model.confidence = incident.confidence
            model.affected_customer_count = incident.affected_customer_count
            model.evidence = incident.evidence
            model.status = incident.status.value
            model.updated_at = incident.updated_at


class SqlAlchemyActionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, action_id: str) -> Action | None:
        model = await self._session.get(ActionModel, action_id)
        return action_to_domain(model) if model else None

    async def get_by_idempotency_key(self, key: str) -> Action | None:
        model = await self._session.scalar(
            select(ActionModel).where(ActionModel.idempotency_key == key).limit(1)
        )
        return action_to_domain(model) if model else None

    async def list_by_status(self, status: ActionStatus | None = None) -> list[Action]:
        statement = select(ActionModel).order_by(ActionModel.updated_at.desc())
        if status:
            statement = statement.where(ActionModel.status == status.value)
        result = await self._session.scalars(statement)
        return [action_to_domain(item) for item in result]

    async def add(self, action: Action) -> None:
        values = asdict(action)
        values["action_type"] = action.action_type.value
        values["status"] = action.status.value
        self._session.add(ActionModel(**values))

    async def update(self, action: Action) -> None:
        model = await self._session.get(ActionModel, action.id)
        if model:
            model.status = action.status.value
            model.external_reference = action.external_reference
            model.reviewer_comment = action.reviewer_comment
            model.updated_at = action.updated_at


class SqlAlchemyAuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, event: AuditEvent) -> None:
        self._session.add(AuditEventModel(**asdict(event)))

    async def list_recent(self, limit: int = 100) -> list[AuditEvent]:
        result = await self._session.scalars(
            select(AuditEventModel).order_by(AuditEventModel.created_at.desc()).limit(limit)
        )
        return [audit_to_domain(item) for item in result]


class SqlAlchemyMetricsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def count_customers(self) -> int:
        return int(await self._session.scalar(select(func.count(CustomerModel.id))) or 0)

    async def count_conversations(self) -> int:
        return int(await self._session.scalar(select(func.count(ConversationModel.id))) or 0)

    async def count_incidents(self, statuses: set[IncidentStatus] | None = None) -> int:
        statement = select(func.count(IncidentModel.id))
        if statuses:
            statement = statement.where(
                IncidentModel.status.in_([status.value for status in statuses])
            )
        return int(await self._session.scalar(statement) or 0)

    async def count_actions(self, status: ActionStatus | None = None) -> int:
        statement = select(func.count(ActionModel.id))
        if status:
            statement = statement.where(ActionModel.status == status.value)
        return int(await self._session.scalar(statement) or 0)

    async def count_completed_actions(self) -> int:
        return await self.count_actions(ActionStatus.COMPLETED)
