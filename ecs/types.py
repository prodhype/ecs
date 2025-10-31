# ecs/types.py

from typing import Any, Iterable, Iterator, MutableMapping, Type, TypeVar

EntityId = int

T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")

ComponentType = Type[Any]
ComponentInstance = Any

EntityIterable = Iterable[EntityId]
EntityIterator = Iterator[EntityId]

StoreByEntity = MutableMapping[EntityId, ComponentInstance]
StoreByComponent = MutableMapping[ComponentType, StoreByEntity]
IndexByComponent = MutableMapping[ComponentType, set[EntityId]]
IndexByEntity = MutableMapping[EntityId, set[ComponentType]]
