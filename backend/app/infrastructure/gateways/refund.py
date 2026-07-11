import asyncio
import hashlib

from app.domain.entities import Transaction


class MockRefundGateway:
    """Deterministic external gateway adapter for local demos and tests."""

    async def issue_refund(self, transaction: Transaction, amount: float) -> str:
        await asyncio.sleep(0.05)
        digest = hashlib.sha1(f"{transaction.id}:{amount}".encode()).hexdigest()[:12].upper()
        return f"RFND-{digest}"
