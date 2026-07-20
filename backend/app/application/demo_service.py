from collections.abc import Awaitable, Callable

from app.application.dto import DemoResetDTO
from app.domain.exceptions import DomainError


class DemoResetService:
    """Resets only the synthetic hackathon dataset when demo mode is enabled."""

    def __init__(
        self,
        resetter: Callable[[], Awaitable[None]],
        *,
        enabled: bool,
    ) -> None:
        self._resetter = resetter
        self._enabled = enabled

    async def reset(self) -> DemoResetDTO:
        if not self._enabled:
            raise DomainError("Demo reset is disabled in this environment")
        await self._resetter()
        return DemoResetDTO(
            status="ready",
            message="Synthetic customers and scenarios were restored.",
            customers=3,
            scenarios=3,
        )
