from app.application.dto import ActionDTO, IncidentDTO
from app.domain.entities import Action, Incident


def to_action_dto(action: Action) -> ActionDTO:
    return ActionDTO(
        id=action.id,
        action_type=action.action_type,
        status=action.status,
        amount=action.amount,
        reason=action.reason,
        policy_reference=action.policy_reference,
        transaction_id=action.transaction_id,
        external_reference=action.external_reference,
        reviewer_comment=action.reviewer_comment,
        created_at=action.created_at,
        updated_at=action.updated_at,
    )


def to_incident_dto(incident: Incident) -> IncidentDTO:
    return IncidentDTO(
        id=incident.id,
        title=incident.title,
        description=incident.description,
        probable_root_cause=incident.probable_root_cause,
        confidence=incident.confidence,
        affected_customer_count=incident.affected_customer_count,
        evidence=incident.evidence,
        status=incident.status,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
    )
