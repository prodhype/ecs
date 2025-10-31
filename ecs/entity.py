# ecs/entity.py

from typing import Iterator, Set

from .types import EntityId


class EntityManager:
    """Allocates and tracks entity identifiers."""

    __slots__ = ("_alive", "_free", "_next_id")

    def __init__(self) -> None:
        self._alive: Set[EntityId] = set()
        self._free: list[EntityId] = []
        self._next_id: EntityId = 1

    def create(self) -> EntityId:
        if self._free:
            eid = self._free.pop()
        else:
            eid = self._next_id
            self._next_id += 1
        self._alive.add(eid)
        return eid

    def destroy(self, entity: EntityId) -> bool:
        if entity in self._alive:
            self._alive.remove(entity)
            self._free.append(entity)
            return True
        return False

    def is_alive(self, entity: EntityId) -> bool:
        return entity in self._alive

    def __len__(self) -> int:
        return len(self._alive)

    def __iter__(self) -> Iterator[EntityId]:
        return iter(self._alive.copy())
