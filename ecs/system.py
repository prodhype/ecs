# ecs/system.py

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .world import World


class System(ABC):
    """Base class for systems."""

    __slots__ = ("priority",)

    def __init__(self, *, priority: int = 0) -> None:
        self.priority = priority

    def start(self, world: "World") -> None:  # noqa: F821
        """Optional hook when the system is added to a started world."""

    def stop(self, world: "World") -> None:  # noqa: F821
        """Optional hook when the system is removed or world stops."""

    @abstractmethod
    def update(self, world: "World", dt: float) -> None:  # noqa: F821
        """Run the system logic."""


class Scheduler:
    """Runs systems in priority order (higher runs first)."""

    __slots__ = ("_systems", "_started", "_world_ref")

    def __init__(self) -> None:
        self._systems: List[System] = []
        self._started: bool = False
        self._world_ref: Optional["World"] = None

    def add(self, system: System) -> None:
        self._systems.append(system)
        self._systems.sort(key=lambda s: s.priority, reverse=True)
        if self._started and self._world_ref is not None:
            system.start(self._world_ref)

    def remove(self, system: System) -> bool:
        if system in self._systems:
            if self._started and self._world_ref is not None:
                system.stop(self._world_ref)
            self._systems.remove(system)
            return True
        return False

    def start(self, world: "World") -> None:  # noqa: F821
        self._world_ref = world
        self._started = True
        for sys in self._systems:
            sys.start(world)

    def stop(self, world: "World") -> None:  # noqa: F821
        for sys in reversed(self._systems):
            sys.stop(world)
        self._started = False
        self._world_ref = None

    def update(self, world: "World", dt: float) -> None:  # noqa: F821
        for sys in self._systems:
            sys.update(world, dt)
