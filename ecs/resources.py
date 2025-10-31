# ecs/resources.py

from typing import Any, Dict, Optional, Type, TypeVar

T = TypeVar("T")


class Resources:
    """Type-keyed resource container for global, non-entity state."""

    __slots__ = ("_data",)

    def __init__(self) -> None:
        self._data: Dict[Type[Any], Any] = {}

    def put(self, resource: T) -> None:
        self._data[type(resource)] = resource

    def get(self, typ: Type[T]) -> T:
        return self._data[typ]

    def try_get(self, typ: Type[T]) -> Optional[T]:
        return self._data.get(typ)

    def remove(self, typ: Type[T]) -> bool:
        return self._data.pop(typ, None) is not None

    def clear(self) -> None:
        self._data.clear()
