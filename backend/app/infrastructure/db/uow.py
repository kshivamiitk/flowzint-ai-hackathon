from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.repositories import (
    SqlAlchemyActionRepository,
    SqlAlchemyAuditRepository,
    SqlAlchemyConversationRepository,
    SqlAlchemyCustomerRepository,
    SqlAlchemyIncidentRepository,
    SqlAlchemyMetricsRepository,
    SqlAlchemyPolicyRepository,
    SqlAlchemyTransactionRepository,
)


class SqlAlchemyUnitOfWork:
    """Coordinates repository work inside one database transaction."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self):
        self._session = self._session_factory()
        self.customers = SqlAlchemyCustomerRepository(self._session)
        self.transactions = SqlAlchemyTransactionRepository(self._session)
        self.policies = SqlAlchemyPolicyRepository(self._session)
        self.conversations = SqlAlchemyConversationRepository(self._session)
        self.incidents = SqlAlchemyIncidentRepository(self._session)
        self.actions = SqlAlchemyActionRepository(self._session)
        self.audits = SqlAlchemyAuditRepository(self._session)
        self.metrics = SqlAlchemyMetricsRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        if exc_type:
            await self._session.rollback()
        await self._session.close()
        self._session = None

    async def commit(self) -> None:
        assert self._session is not None
        await self._session.commit()

    async def rollback(self) -> None:
        assert self._session is not None
        await self._session.rollback()
