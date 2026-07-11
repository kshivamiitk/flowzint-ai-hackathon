from enum import StrEnum


class Intent(StrEnum):
    FAILED_PAYMENT = "failed_payment"
    REFUND_REQUEST = "refund_request"
    DELIVERY_ISSUE = "delivery_issue"
    ACCOUNT_ISSUE = "account_issue"
    FAQ = "faq"
    OTHER = "other"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TransactionStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    REFUNDED = "refunded"


class ActionType(StrEnum):
    ISSUE_REFUND = "issue_refund"
    ADD_WALLET_CREDIT = "add_wallet_credit"
    CREATE_TICKET = "create_ticket"
    ESCALATE_TO_HUMAN = "escalate_to_human"


class ActionStatus(StrEnum):
    PROPOSED = "proposed"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"


class DecisionMode(StrEnum):
    AUTOMATIC = "automatic"
    APPROVAL_REQUIRED = "approval_required"
    HUMAN_ESCALATION = "human_escalation"
    REJECT = "reject"


class IncidentStatus(StrEnum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    RESOLVING = "resolving"
    RESOLVED = "resolved"
