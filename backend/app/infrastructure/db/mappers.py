from app.domain.entities import (
    Action,
    AuditEvent,
    ComplaintAnalysis,
    Conversation,
    Customer,
    Incident,
    PolicyDocument,
    Transaction,
)
from app.domain.enums import (
    ActionStatus,
    ActionType,
    IncidentStatus,
    Intent,
    Severity,
    TransactionStatus,
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


def customer_to_domain(model: CustomerModel) -> Customer:
    return Customer(
        id=model.id,
        name=model.name,
        email=model.email,
        language=model.language,
        plan=model.plan,
        created_at=model.created_at,
    )


def transaction_to_domain(model: TransactionModel) -> Transaction:
    return Transaction(
        id=model.id,
        customer_id=model.customer_id,
        amount=model.amount,
        payment_method=model.payment_method,
        status=TransactionStatus(model.status),
        order_reference=model.order_reference,
        app_version=model.app_version,
        error_code=model.error_code,
        refunded_at=model.refunded_at,
        created_at=model.created_at,
    )


def policy_to_domain(model: PolicyModel) -> PolicyDocument:
    return PolicyDocument(
        id=model.id,
        title=model.title,
        section=model.section,
        content=model.content,
        embedding=list(model.embedding),
        created_at=model.created_at,
    )


def conversation_to_domain(model: ConversationModel) -> Conversation:
    analysis = ComplaintAnalysis(
        intent=Intent(model.intent),
        severity=Severity(model.severity),
        language=model.language,
        summary=model.summary,
        confidence=model.confidence,
        transaction_required=model.transaction_required,
        attributes=dict(model.attributes),
    )
    return Conversation(
        id=model.id,
        customer_id=model.customer_id,
        transaction_id=model.transaction_id,
        incident_id=model.incident_id,
        message=model.message,
        analysis=analysis,
        embedding=list(model.embedding),
        assistant_response=model.assistant_response,
        policy_references=list(model.policy_references),
        created_at=model.created_at,
    )


def incident_to_domain(model: IncidentModel) -> Incident:
    return Incident(
        id=model.id,
        title=model.title,
        fingerprint=model.fingerprint,
        description=model.description,
        probable_root_cause=model.probable_root_cause,
        confidence=model.confidence,
        affected_customer_count=model.affected_customer_count,
        evidence=list(model.evidence),
        status=IncidentStatus(model.status),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def action_to_domain(model: ActionModel) -> Action:
    return Action(
        id=model.id,
        customer_id=model.customer_id,
        transaction_id=model.transaction_id,
        conversation_id=model.conversation_id,
        action_type=ActionType(model.action_type),
        status=ActionStatus(model.status),
        amount=model.amount,
        reason=model.reason,
        policy_reference=model.policy_reference,
        idempotency_key=model.idempotency_key,
        external_reference=model.external_reference,
        reviewer_comment=model.reviewer_comment,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def audit_to_domain(model: AuditEventModel) -> AuditEvent:
    return AuditEvent(
        id=model.id,
        event_type=model.event_type,
        actor=model.actor,
        details=dict(model.details),
        action_id=model.action_id,
        conversation_id=model.conversation_id,
        created_at=model.created_at,
    )
