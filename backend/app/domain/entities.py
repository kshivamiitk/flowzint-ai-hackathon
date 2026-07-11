from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.domain.enums import (
    ActionStatus,
    ActionType,
    DecisionMode,
    IncidentStatus,
    Intent,
    Severity,
    TransactionStatus,
)


def new_id() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class Customer:
    name: str
    email: str
    language: str = "en"
    plan: str = "standard"
    id: str = field(default_factory=new_id)
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Transaction:
    customer_id: str
    amount: float
    payment_method: str
    status: TransactionStatus
    order_reference: str
    app_version: str = "4.2.1"
    error_code: str | None = None
    id: str = field(default_factory=new_id)
    refunded_at: datetime | None = None
    created_at: datetime = field(default_factory=utc_now)

    def mark_refunded(self) -> None:
        if self.status == TransactionStatus.REFUNDED:
            return
        self.status = TransactionStatus.REFUNDED
        self.refunded_at = utc_now()


@dataclass(slots=True)
class PolicyDocument:
    title: str
    section: str
    content: str
    embedding: list[float]
    id: str = field(default_factory=new_id)
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class ComplaintAnalysis:
    intent: Intent
    severity: Severity
    language: str
    summary: str
    confidence: float
    transaction_required: bool
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Conversation:
    customer_id: str
    message: str
    analysis: ComplaintAnalysis
    embedding: list[float]
    assistant_response: str
    policy_references: list[str]
    transaction_id: str | None = None
    incident_id: str | None = None
    id: str = field(default_factory=new_id)
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Incident:
    title: str
    fingerprint: str
    description: str
    probable_root_cause: str
    confidence: float
    affected_customer_count: int
    evidence: list[str]
    status: IncidentStatus = IncidentStatus.DETECTED
    id: str = field(default_factory=new_id)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def refresh(self, count: int, evidence: list[str], confidence: float) -> None:
        self.affected_customer_count = max(self.affected_customer_count, count)
        self.evidence = evidence
        self.confidence = max(self.confidence, confidence)
        self.updated_at = utc_now()


@dataclass(slots=True)
class ActionDecision:
    mode: DecisionMode
    action_type: ActionType
    reason: str
    policy_reference: str


@dataclass(slots=True)
class Action:
    customer_id: str
    action_type: ActionType
    amount: float
    reason: str
    policy_reference: str
    idempotency_key: str
    transaction_id: str | None = None
    conversation_id: str | None = None
    status: ActionStatus = ActionStatus.PROPOSED
    external_reference: str | None = None
    reviewer_comment: str | None = None
    id: str = field(default_factory=new_id)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def request_approval(self) -> None:
        if self.status != ActionStatus.PROPOSED:
            raise ValueError("Only a proposed action can request approval")
        self.status = ActionStatus.AWAITING_APPROVAL
        self.updated_at = utc_now()

    def approve(self, comment: str | None = None) -> None:
        if self.status != ActionStatus.AWAITING_APPROVAL:
            raise ValueError("Only actions awaiting approval can be approved")
        self.status = ActionStatus.APPROVED
        self.reviewer_comment = comment
        self.updated_at = utc_now()

    def reject(self, comment: str | None = None) -> None:
        if self.status not in {ActionStatus.PROPOSED, ActionStatus.AWAITING_APPROVAL}:
            raise ValueError("This action can no longer be rejected")
        self.status = ActionStatus.REJECTED
        self.reviewer_comment = comment
        self.updated_at = utc_now()

    def start_execution(self) -> None:
        if self.status not in {ActionStatus.PROPOSED, ActionStatus.APPROVED}:
            raise ValueError("Action is not ready for execution")
        self.status = ActionStatus.EXECUTING
        self.updated_at = utc_now()

    def complete(self, external_reference: str) -> None:
        if self.status != ActionStatus.EXECUTING:
            raise ValueError("Only an executing action can complete")
        self.status = ActionStatus.COMPLETED
        self.external_reference = external_reference
        self.updated_at = utc_now()

    def fail(self, error: str) -> None:
        if self.status != ActionStatus.EXECUTING:
            raise ValueError("Only an executing action can fail")
        self.status = ActionStatus.FAILED
        self.reviewer_comment = error
        self.updated_at = utc_now()


@dataclass(slots=True)
class AuditEvent:
    event_type: str
    actor: str
    details: dict[str, Any]
    action_id: str | None = None
    conversation_id: str | None = None
    id: str = field(default_factory=new_id)
    created_at: datetime = field(default_factory=utc_now)
