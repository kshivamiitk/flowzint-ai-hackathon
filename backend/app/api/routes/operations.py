from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_action_service, get_query_service
from app.application.action_service import ActionWorkflowService
from app.application.dto import (
    ActionDTO,
    AuditEventDTO,
    DashboardMetricsDTO,
    IncidentDTO,
    ReviewRequest,
)
from app.application.mappers import to_action_dto
from app.application.query_service import QueryService
from app.domain.enums import ActionStatus

router = APIRouter(tags=["operations"])


@router.get("/dashboard/metrics", response_model=DashboardMetricsDTO)
async def dashboard(
    service: QueryService = Depends(get_query_service),
) -> DashboardMetricsDTO:
    return await service.dashboard()


@router.get("/incidents", response_model=list[IncidentDTO])
async def incidents(
    service: QueryService = Depends(get_query_service),
) -> list[IncidentDTO]:
    return await service.incidents()


@router.get("/actions", response_model=list[ActionDTO])
async def actions(
    status: ActionStatus | None = Query(default=None),
    service: QueryService = Depends(get_query_service),
) -> list[ActionDTO]:
    return await service.actions(status)


@router.post("/actions/{action_id}/approve", response_model=ActionDTO)
async def approve_action(
    action_id: str,
    payload: ReviewRequest,
    service: ActionWorkflowService = Depends(get_action_service),
) -> ActionDTO:
    return to_action_dto(await service.approve(action_id, payload.comment))


@router.post("/actions/{action_id}/reject", response_model=ActionDTO)
async def reject_action(
    action_id: str,
    payload: ReviewRequest,
    service: ActionWorkflowService = Depends(get_action_service),
) -> ActionDTO:
    return to_action_dto(await service.reject(action_id, payload.comment))


@router.get("/audit-events", response_model=list[AuditEventDTO])
async def audit_events(
    limit: int = Query(default=100, ge=1, le=500),
    service: QueryService = Depends(get_query_service),
) -> list[AuditEventDTO]:
    return await service.audits(limit)
