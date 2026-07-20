from fastapi import APIRouter, Depends, Query

from app.api.dependencies import (
    get_action_service,
    get_demo_service,
    get_incident_service,
    get_query_service,
)
from app.application.action_service import ActionWorkflowService
from app.application.demo_service import DemoResetService
from app.application.dto import (
    ActionDTO,
    AuditEventDTO,
    DashboardMetricsDTO,
    DemoResetDTO,
    IncidentDTO,
    IncidentStatusRequest,
    ReviewRequest,
)
from app.application.incident_service import IncidentDetectionService
from app.application.mappers import to_action_dto, to_incident_dto
from app.application.query_service import QueryService
from app.domain.enums import ActionStatus

router = APIRouter(tags=["operations"])


@router.post("/demo/reset", response_model=DemoResetDTO)
async def reset_demo(
    service: DemoResetService = Depends(get_demo_service),
) -> DemoResetDTO:
    return await service.reset()


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


@router.post("/incidents/{incident_id}/status", response_model=IncidentDTO)
async def update_incident_status(
    incident_id: str,
    payload: IncidentStatusRequest,
    service: IncidentDetectionService = Depends(get_incident_service),
) -> IncidentDTO:
    return to_incident_dto(await service.update_status(incident_id, payload.status))


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
