from collections import Counter
from collections.abc import Callable
from datetime import timedelta
from math import sqrt

from app.domain.entities import AuditEvent, Conversation, Incident, utc_now
from app.domain.enums import IncidentStatus
from app.domain.ports import UnitOfWork


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


class IncidentDetectionService:
    """Detects and enriches operational incidents from recent conversations."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        *,
        similarity_threshold: float,
        minimum_complaints: int,
        window_minutes: int,
    ) -> None:
        self._uow_factory = uow_factory
        self._threshold = similarity_threshold
        self._minimum = minimum_complaints
        self._window = timedelta(minutes=window_minutes)

    async def detect(self, conversation: Conversation) -> Incident | None:
        since = utc_now() - self._window
        async with self._uow_factory() as uow:
            candidates = await uow.conversations.list_recent(since)
            similar = [
                item
                for item in candidates
                if item.analysis.intent == conversation.analysis.intent
                and cosine_similarity(item.embedding, conversation.embedding) >= self._threshold
            ]

            if len(similar) < self._minimum:
                return None

            fingerprint = conversation.analysis.intent.value
            incident = await uow.incidents.find_open_by_fingerprint(fingerprint)
            evidence, root_cause, confidence = self._build_evidence(similar)
            unique_customers = len({item.customer_id for item in similar})

            if incident:
                incident.refresh(unique_customers, evidence, confidence)
                await uow.incidents.update(incident)
            else:
                title = conversation.analysis.intent.value.replace("_", " ").title()
                incident = Incident(
                    title=f"{title} Spike",
                    fingerprint=fingerprint,
                    description=(
                        f"Detected {len(similar)} semantically related complaints "
                        f"within {int(self._window.total_seconds() // 60)} minutes."
                    ),
                    probable_root_cause=root_cause,
                    confidence=confidence,
                    affected_customer_count=unique_customers,
                    evidence=evidence,
                    status=IncidentStatus.DETECTED,
                )
                await uow.incidents.add(incident)

            await uow.conversations.attach_incident([item.id for item in similar], incident.id)
            await uow.audits.add(
                AuditEvent(
                    event_type="incident_detected",
                    actor="incident_detector",
                    conversation_id=conversation.id,
                    details={
                        "incident_id": incident.id,
                        "related_complaints": len(similar),
                        "confidence": confidence,
                    },
                )
            )
            await uow.commit()
            return incident

    @staticmethod
    def _build_evidence(
        conversations: list[Conversation],
    ) -> tuple[list[str], str, float]:
        error_codes = [
            str(item.analysis.attributes.get("error_code"))
            for item in conversations
            if item.analysis.attributes.get("error_code")
        ]
        app_versions = [
            str(item.analysis.attributes.get("app_version"))
            for item in conversations
            if item.analysis.attributes.get("app_version")
        ]
        payment_methods = [
            str(item.analysis.attributes.get("payment_method"))
            for item in conversations
            if item.analysis.attributes.get("payment_method")
        ]

        evidence: list[str] = []
        root_cause = "Multiple customers reported the same failure pattern."
        confidence = min(0.55 + (0.08 * len(conversations)), 0.95)

        if error_codes:
            code, count = Counter(error_codes).most_common(1)[0]
            evidence.append(f"{count} complaints share error code {code}.")
            root_cause = f"Probable service failure associated with {code}."
        if app_versions:
            version, count = Counter(app_versions).most_common(1)[0]
            evidence.append(f"{count} complaints originated from app version {version}.")
        if payment_methods:
            method, count = Counter(payment_methods).most_common(1)[0]
            evidence.append(f"{count} complaints used payment method {method}.")
        if not evidence:
            evidence.append(
                f"{len(conversations)} complaint summaries exceeded similarity threshold."
            )

        return evidence, root_cause, confidence
