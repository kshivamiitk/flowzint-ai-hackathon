from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.entities import (
    ComplaintAnalysis,
    Conversation,
    Customer,
    PolicyDocument,
    Transaction,
    utc_now,
)
from app.domain.enums import Intent, Severity, TransactionStatus
from app.domain.ports import EmbeddingProvider
from app.infrastructure.db.models import CustomerModel
from app.infrastructure.db.uow import SqlAlchemyUnitOfWork

CUSTOMERS = [
    Customer(
        id="cust-kumar",
        name="Kumar Shivam",
        email="kumar@example.com",
        language="hinglish",
        plan="pro",
    ),
    Customer(
        id="cust-aarav",
        name="Aarav Mehta",
        email="aarav@example.com",
        language="en",
        plan="standard",
    ),
    Customer(
        id="cust-neha",
        name="Neha Singh",
        email="neha@example.com",
        language="hi",
        plan="standard",
    ),
]

TRANSACTIONS = [
    Transaction(
        id="txn-kumar-449",
        customer_id="cust-kumar",
        amount=449,
        payment_method="UPI",
        status=TransactionStatus.SUCCESS,
        order_reference="ORD-2026-1001",
        app_version="4.2.1",
        error_code="PAYMENT_CALLBACK_TIMEOUT",
    ),
    Transaction(
        id="txn-aarav-1499",
        customer_id="cust-aarav",
        amount=1499,
        payment_method="UPI",
        status=TransactionStatus.SUCCESS,
        order_reference="ORD-2026-1002",
        app_version="4.2.1",
        error_code="PAYMENT_CALLBACK_TIMEOUT",
    ),
    Transaction(
        id="txn-neha-3299",
        customer_id="cust-neha",
        amount=3299,
        payment_method="UPI",
        status=TransactionStatus.SUCCESS,
        order_reference="ORD-2026-1003",
        app_version="4.2.1",
        error_code="PAYMENT_CALLBACK_TIMEOUT",
    ),
]

POLICIES = [
    (
        "Refund Policy",
        "1.1",
        "A refund request must be linked to a verified customer transaction "
        "before any monetary action is proposed.",
    ),
    (
        "Refund Policy",
        "1.4",
        "A transaction already refunded must not be refunded again. Duplicate "
        "requests return the existing reference.",
    ),
    (
        "Refund Policy",
        "2.1",
        "When payment succeeds but order creation fails, the customer is "
        "eligible for a full refund. Refunds up to ₹500 may be automated; "
        "larger values require approval according to configured limits.",
    ),
    (
        "Escalation Policy",
        "3.2",
        "Requests above the approval limit, fraud allegations, missing "
        "evidence, or account deletion requests require human review.",
    ),
    (
        "Incident Policy",
        "4.1",
        "Three or more semantically related complaints within one hour should "
        "create or update an operational incident.",
    ),
    (
        "Data Safety Policy",
        "5.1",
        "Customer data must be minimized. Internal prompts, credentials, and "
        "unrelated customer records must never be disclosed.",
    ),
]


async def seed_database(
    session_factory: async_sessionmaker[AsyncSession],
    embedding_provider: EmbeddingProvider,
) -> None:
    async with session_factory() as session:
        count = int(await session.scalar(select(func.count(CustomerModel.id))) or 0)
    if count:
        return

    async with SqlAlchemyUnitOfWork(session_factory) as uow:
        for customer in CUSTOMERS:
            await uow.customers.add(customer)
        for transaction in TRANSACTIONS:
            await uow.transactions.add(transaction)
        for title, section, content in POLICIES:
            embedding = await embedding_provider.embed(content)
            await uow.policies.add(
                PolicyDocument(
                    title=title,
                    section=section,
                    content=content,
                    embedding=embedding,
                )
            )

        historical = [
            (
                CUSTOMERS[1],
                TRANSACTIONS[1],
                "UPI charged me but the order was not created.",
            ),
            (
                CUSTOMERS[2],
                TRANSACTIONS[2],
                "Payment ho gaya lekin booking confirm nahi hui.",
            ),
        ]
        for index, (customer, transaction, message) in enumerate(historical, start=1):
            summary = "Payment was deducted but the order was not completed."
            embedding = await embedding_provider.embed(summary)
            analysis = ComplaintAnalysis(
                intent=Intent.FAILED_PAYMENT,
                severity=Severity.MEDIUM,
                language="en" if index == 1 else "hinglish",
                summary=summary,
                confidence=0.94,
                transaction_required=True,
                attributes={
                    "transaction_id": transaction.id,
                    "payment_method": transaction.payment_method,
                    "app_version": transaction.app_version,
                    "error_code": transaction.error_code,
                },
            )
            await uow.conversations.add(
                Conversation(
                    id=f"seed-conversation-{index}",
                    customer_id=customer.id,
                    transaction_id=transaction.id,
                    message=message,
                    analysis=analysis,
                    embedding=embedding,
                    assistant_response=("Historical seeded complaint used for incident demo."),
                    policy_references=["Refund Policy §2.1"],
                    created_at=utc_now() - timedelta(minutes=20 - index * 5),
                )
            )
        await uow.commit()
