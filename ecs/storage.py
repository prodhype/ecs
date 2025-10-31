# ecs/storage.py

from typing import Iterator, Optional

from .errors import ComponentAlreadyExists, ComponentNotFound
from .types import (ComponentInstance, ComponentType, EntityId,
                    IndexByComponent, IndexByEntity, StoreByComponent,
                    StoreByEntity)


class ComponentStore:
    """Stores components keyed by (component type -> entity -> instance)."""

    __slots__ = ("_by_component", "_index_by_component", "_index_by_entity")

    def __init__(self) -> None:
        self._by_component: StoreByComponent = {}
        self._index_by_component: IndexByComponent = {}
        self._index_by_entity: IndexByEntity = {}

    def add(self, entity: EntityId, component: ComponentInstance) -> None:
        ctype: ComponentType = type(component)
        entities = self._by_component.setdefault(ctype, {})
        if entity in entities:
            raise ComponentAlreadyExists(f"{ctype.__name__} already on entity {entity}")
        entities[entity] = component

        self._index_by_component.setdefault(ctype, set()).add(entity)
        self._index_by_entity.setdefault(entity, set()).add(ctype)

    def upsert(self, entity: EntityId, component: ComponentInstance) -> None:
        ctype: ComponentType = type(component)
        entities = self._by_component.setdefault(ctype, {})
        entities[entity] = component
        self._index_by_component.setdefault(ctype, set()).add(entity)
        self._index_by_entity.setdefault(entity, set()).add(ctype)

    def remove(self, entity: EntityId, ctype: ComponentType) -> None:
        entities = self._by_component.get(ctype)
        if not entities or entity not in entities:
            raise ComponentNotFound(f"{ctype.__name__} missing on entity {entity}")
        del entities[entity]
        if not entities:
            self._by_component.pop(ctype, None)

        comp_index = self._index_by_component.get(ctype)
        if comp_index:
            comp_index.discard(entity)
            if not comp_index:
                self._index_by_component.pop(ctype, None)

        ent_index = self._index_by_entity.get(entity)
        if ent_index:
            ent_index.discard(ctype)
            if not ent_index:
                self._index_by_entity.pop(entity, None)

    def remove_all_for_entity(self, entity: EntityId) -> int:
        removed = 0
        ctypes = list(self._index_by_entity.get(entity, set()))
        for ctype in ctypes:
            self.remove(entity, ctype)
            removed += 1
        return removed

    def get(
        self, entity: EntityId, ctype: ComponentType
    ) -> Optional[ComponentInstance]:
        return self._by_component.get(ctype, {}).get(entity)

    def has(self, entity: EntityId, ctype: ComponentType) -> bool:
        return entity in self._by_component.get(ctype, {})

    def entities_with(self, ctype: ComponentType) -> set[EntityId]:
        return set(self._index_by_component.get(ctype, set()))

    def all_of(self, *ctypes: ComponentType) -> Iterator[EntityId]:
        if not ctypes:
            return iter(())
        sets = [self.entities_with(ct) for ct in ctypes]
        if not sets:
            return iter(())
        result = sets[0]
        for s in sets[1:]:
            result &= s
            if not result:
                break
        return iter(result)

    def component(self, ctype: ComponentType) -> StoreByEntity:
        return self._by_component.setdefault(ctype, {})

    def clear(self) -> None:
        self._by_component.clear()
        self._index_by_component.clear()
        self._index_by_entity.clear()
