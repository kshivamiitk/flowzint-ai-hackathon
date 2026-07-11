import pytest

from app.domain.entities import Action
from app.domain.enums import ActionStatus, ActionType


def make_action() -> Action:
    return Action(
        customer_id="customer",
        transaction_id="transaction",
        action_type=ActionType.ISSUE_REFUND,
        amount=100,
        reason="test",
        policy_reference="REFUND-2.1",
        idempotency_key="key",
    )


def test_action_state_machine_happy_path():
    action = make_action()
    action.request_approval()
    assert action.status == ActionStatus.AWAITING_APPROVAL
    action.approve("verified")
    action.start_execution()
    action.complete("RFND-1")
    assert action.status == ActionStatus.COMPLETED
    assert action.external_reference == "RFND-1"


def test_cannot_approve_unrequested_action():
    action = make_action()
    with pytest.raises(ValueError):
        action.approve()
