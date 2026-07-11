from collections.abc import Callable

from app.application.dto import (
    ActionDTO,
    AuditEventDTO,
    CustomerDTO,
    DashboardMetricsDTO,
    IncidentDTO,
    TransactionDTO,
)
from app.application.mappers import to_action_dto, to_incident_dto
from app.domain.enums import ActionStatus, IncidentStatus
from app.domain.ports import UnitOfWork


class QueryService:
    """Read-only application service used by operations screens."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    async def customers(self) -> list[CustomerDTO]:
        async with self._uow_factory() as uow:
            items = await uow.customers.list_all()
            return [
                CustomerDTO(
                    id=item.id,
                    name=item.name,
                    email=item.email,
                    language=item.language,
                    plan=item.plan,
                )
                for item in items
            ]

    async def transactions(self, customer_id: str | None = None) -> list[TransactionDTO]:
        async with self._uow_factory() as uow:
            if customer_id:
                items = await uow.transactions.list_for_customer(customer_id)
            else:
                items = []
                for customer in await uow.customers.list_all():
                    items.extend(await uow.transactions.list_for_customer(customer.id))
            return [
                TransactionDTO(
                    id=item.id,
                    customer_id=item.customer_id,
                    amount=item.amount,
                    payment_method=item.payment_method,
                    status=item.status,
                    order_reference=item.order_reference,
                    app_version=item.app_version,
                    error_code=item.error_code,
                    refunded_at=item.refunded_at,
                    created_at=item.created_at,
                )
                for item in items
            ]

    async def incidents(self) -> list[IncidentDTO]:
        async with self._uow_factory() as uow:
            return [to_incident_dto(item) for item in await uow.incidents.list_all()]

    async def actions(self, status: ActionStatus | None = None) -> list[ActionDTO]:
        async with self._uow_factory() as uow:
            return [to_action_dto(item) for item in await uow.actions.list_by_status(status)]

    async def audits(self, limit: int = 100) -> list[AuditEventDTO]:
        async with self._uow_factory() as uow:
            return [
                AuditEventDTO(
                    id=item.id,
                    event_type=item.event_type,
                    actor=item.actor,
                    details=item.details,
                    action_id=item.action_id,
                    conversation_id=item.conversation_id,
                    created_at=item.created_at,
                )
                for item in await uow.audits.list_recent(limit)
            ]

    async def dashboard(self) -> DashboardMetricsDTO:
        async with self._uow_factory() as uow:
            customers = await uow.metrics.count_customers()
            conversations = await uow.metrics.count_conversations()
            open_incidents = await uow.metrics.count_incidents(
                {
                    IncidentStatus.DETECTED,
                    IncidentStatus.INVESTIGATING,
                    IncidentStatus.CONFIRMED,
                    IncidentStatus.RESOLVING,
                }
            )
            pending = await uow.metrics.count_actions(ActionStatus.AWAITING_APPROVAL)
            completed = await uow.metrics.count_completed_actions()
            all_actions = await uow.metrics.count_actions()
            rate = round((completed / all_actions) * 100, 1) if all_actions else 0.0
            return DashboardMetricsDTO(
                customers=customers,
                conversations=conversations,
                open_incidents=open_incidents,
                pending_approvals=pending,
                completed_actions=completed,
                automation_rate=rate,
            )
