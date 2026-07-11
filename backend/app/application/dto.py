from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import ActionStatus, ActionType, IncidentStatus, Intent, Severity


class MessageRequest(BaseModel):
    customer_id: str
    message: str = Field(min_length=2, max_length=2000)


class PolicyReferenceDTO(BaseModel):
    title: str
    section: str


class ActionDTO(BaseModel):
    id: str
    action_type: ActionType
    status: ActionStatus
    amount: float
    reason: str
    policy_reference: str
    transaction_id: str | None
    external_reference: str | None
    reviewer_comment: str | None
    created_at: datetime
    updated_at: datetime


class IncidentDTO(BaseModel):
    id: str
    title: str
    description: str
    probable_root_cause: str
    confidence: float
    affected_customer_count: int
    evidence: list[str]
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    intent: Intent
    severity: Severity
    language: str
    confidence: float
    policy_references: list[PolicyReferenceDTO]
    action: ActionDTO | None = None
    incident: IncidentDTO | None = None


class CustomerDTO(BaseModel):
    id: str
    name: str
    email: str
    language: str
    plan: str


class TransactionDTO(BaseModel):
    id: str
    customer_id: str
    amount: float
    payment_method: str
    status: str
    order_reference: str
    app_version: str
    error_code: str | None
    refunded_at: datetime | None
    created_at: datetime


class ReviewRequest(BaseModel):
    comment: str | None = Field(default=None, max_length=500)


class AuditEventDTO(BaseModel):
    id: str
    event_type: str
    actor: str
    details: dict
    action_id: str | None
    conversation_id: str | None
    created_at: datetime


class DashboardMetricsDTO(BaseModel):
    customers: int
    conversations: int
    open_incidents: int
    pending_approvals: int
    completed_actions: int
    automation_rate: float
