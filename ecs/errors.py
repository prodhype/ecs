# ecs/errors.py


class ECSException(Exception):
    """Base exception for ECS-related errors."""


class EntityNotFound(ECSException):
    """Raised when an operation references a non-existent entity."""


class ComponentNotFound(ECSException):
    """Raised when a requested component is missing on an entity."""


class ComponentAlreadyExists(ECSException):
    """Raised when adding a component that already exists on an entity."""
