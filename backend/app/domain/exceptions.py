class DomainError(Exception):
    """Base class for expected business errors."""


class EntityNotFoundError(DomainError):
    pass


class ExternalServiceError(DomainError):
    pass
