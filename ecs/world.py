# ecs/world.py

from typing import Any, Iterator, Optional, Type, overload

from .entity import EntityManager
from .errors import ComponentNotFound, EntityNotFound
from .resources import Resources
from .storage import ComponentStore
from .system import Scheduler, System
from .types import (T1, T2, T3, T4, T5, ComponentInstance, ComponentType,
                    EntityId)


class World:
    """The central ECS object managing entities, components, and systems."""

    __slots__ = ("entities", "_store", "_scheduler", "resources", "_started")

    def __init__(self) -> None:
        self.entities = EntityManager()
        self._store = ComponentStore()
        self._scheduler = Scheduler()
        self.resources = Resources()
        self._started: bool = False

    # --- Lifecycle ----------------------------------------------------------------

    def start(self) -> None:
        if not self._started:
            self._scheduler.start(self)
            self._started = True

    def stop(self) -> None:
        if self._started:
            self._scheduler.stop(self)
            self._started = False

    # --- Entity API ----------------------------------------------------------------

    def create_entity(self) -> EntityId:
        return self.entities.create()

    def destroy_entity(self, entity: EntityId) -> None:
        if not self.entities.destroy(entity):
            raise EntityNotFound(f"Entity {entity} not found")
        self._store.remove_all_for_entity(entity)

    def is_alive(self, entity: EntityId) -> bool:
        return self.entities.is_alive(entity)

    # --- Component API -------------------------------------------------------------

    def add_component(self, entity: EntityId, component: ComponentInstance) -> None:
        self._require_alive(entity)
        self._store.add(entity, component)

    def upsert_component(self, entity: EntityId, component: ComponentInstance) -> None:
        self._require_alive(entity)
        self._store.upsert(entity, component)

    def remove_component(self, entity: EntityId, ctype: ComponentType) -> None:
        self._require_alive(entity)
        self._store.remove(entity, ctype)

    def get_component(self, entity: EntityId, ctype: Type[T1]) -> Optional[T1]:
        self._require_alive(entity)
        comp = self._store.get(entity, ctype)
        return comp  # type: ignore[return-value]

    def require_component(self, entity: EntityId, ctype: Type[T1]) -> T1:
        self._require_alive(entity)
        comp = self._store.get(entity, ctype)
        if comp is None:
            raise ComponentNotFound(f"{ctype.__name__} missing on entity {entity}")
        return comp  # type: ignore[return-value]

    def has_component(self, entity: EntityId, ctype: ComponentType) -> bool:
        self._require_alive(entity)
        return self._store.has(entity, ctype)

    # --- Query API -----------------------------------------------------------------

    @overload
    def view(self, c1: Type[T1]) -> Iterator[tuple[EntityId, T1]]: ...
    @overload
    def view(self, c1: Type[T1], c2: Type[T2]) -> Iterator[tuple[EntityId, T1, T2]]: ...
    @overload
    def view(
        self, c1: Type[T1], c2: Type[T2], c3: Type[T3]
    ) -> Iterator[tuple[EntityId, T1, T2, T3]]: ...
    @overload
    def view(
        self, c1: Type[T1], c2: Type[T2], c3: Type[T3], c4: Type[T4]
    ) -> Iterator[tuple[EntityId, T1, T2, T3, T4]]: ...
    @overload
    def view(
        self, c1: Type[T1], c2: Type[T2], c3: Type[T3], c4: Type[T4], c5: Type[T5]
    ) -> Iterator[tuple[EntityId, T1, T2, T3, T4, T5]]: ...

    def view(
        self,
        c1: ComponentType,
        c2: ComponentType | None = None,
        c3: ComponentType | None = None,
        c4: ComponentType | None = None,
        c5: ComponentType | None = None,
        *extra: ComponentType,
    ) -> Iterator[tuple[Any, ...]]:
        """Iterate (entity, c1, c2, ...) over entities containing all ctypes."""

        component_list: list[ComponentType] = [c1]
        for opt in (c2, c3, c4, c5):
            if opt is not None:
                component_list.append(opt)
        if extra:
            component_list.extend(extra)

        component_types = tuple(component_list)

        def generator() -> Iterator[tuple[Any, ...]]:
            for entity in self._store.all_of(*component_types):
                components: list[Any] = []
                for ctype in component_types:
                    component = self._store.get(entity, ctype)
                    if component is None:
                        raise ComponentNotFound(
                            f"{ctype.__name__} missing on entity {entity}"
                        )
                    components.append(component)
                yield (entity, *components)

        return generator()

    def entities_with(self, *ctypes: ComponentType) -> Iterator[EntityId]:
        return self._store.all_of(*ctypes)

    # --- Systems API ---------------------------------------------------------------

    def add_system(self, system: System) -> None:
        self._scheduler.add(system)
        if self._started:
            system.start(self)

    def remove_system(self, system: System) -> bool:
        return self._scheduler.remove(system)

    def update(self, dt: float) -> None:
        self._scheduler.update(self, dt)

    # --- Utilities -----------------------------------------------------------------

    def clear(self) -> None:
        self.stop()
        for e in list(self.entities):
            self._store.remove_all_for_entity(e)
        self._store.clear()
        self.resources.clear()
        # EntityManager keeps free-list; leave as-is for deterministic reuse.

    def _require_alive(self, entity: EntityId) -> None:
        if not self.entities.is_alive(entity):
            raise EntityNotFound(f"Entity {entity} not found or already destroyed")
