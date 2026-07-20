from functools import lru_cache

from app.application.action_service import ActionWorkflowService
from app.application.chat_service import ChatOrchestrator
from app.application.demo_service import DemoResetService
from app.application.incident_service import IncidentDetectionService
from app.application.query_service import QueryService
from app.application.rules import RefundPolicyEngine, RefundRuleConfig
from app.core.config import get_settings
from app.infrastructure.ai.factory import (
    AIComponents,
    build_ai_components,
)
from app.infrastructure.db.seed import reset_demo_database
from app.infrastructure.db.session import (
    build_engine,
    build_session_factory,
)
from app.infrastructure.db.uow import SqlAlchemyUnitOfWork
from app.infrastructure.gateways.refund import MockRefundGateway

settings = get_settings()
engine = build_engine(settings)
session_factory = build_session_factory(engine)
ai_components: AIComponents = build_ai_components(settings)


def uow_factory() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory)


@lru_cache
def get_action_service() -> ActionWorkflowService:
    return ActionWorkflowService(
        uow_factory=uow_factory,
        rule_engine=RefundPolicyEngine(
            RefundRuleConfig(
                automatic_limit=settings.auto_refund_limit,
                approval_limit=settings.approval_refund_limit,
            )
        ),
        gateway=MockRefundGateway(),
    )


@lru_cache
def get_incident_service() -> IncidentDetectionService:
    return IncidentDetectionService(
        uow_factory=uow_factory,
        similarity_threshold=settings.incident_similarity_threshold,
        minimum_complaints=settings.incident_min_complaints,
        window_minutes=settings.incident_window_minutes,
    )


@lru_cache
def get_chat_service() -> ChatOrchestrator:
    return ChatOrchestrator(
        uow_factory=uow_factory,
        analyzer=ai_components.analyzer,
        answer_generator=ai_components.answer_generator,
        embedding_provider=ai_components.embedding_provider,
        action_workflow=get_action_service(),
        incident_detector=get_incident_service(),
        automatic_limit=settings.auto_refund_limit,
        approval_limit=settings.approval_refund_limit,
    )


@lru_cache
def get_query_service() -> QueryService:
    return QueryService(uow_factory)


@lru_cache
def get_demo_service() -> DemoResetService:
    async def resetter() -> None:
        await reset_demo_database(session_factory, ai_components.embedding_provider)

    return DemoResetService(resetter, enabled=settings.demo_mode)
