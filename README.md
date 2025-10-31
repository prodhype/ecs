# Minimal Python ECS (Entity Component System)

A tiny, dependency-free Entity Component System framework intended as a clear starting point for games, simulations, and data-driven architectures. It favors readability and explicitness over cleverness.

- **Entities** are integer IDs.
- **Components** are plain Python objects (dataclasses recommended).
- **Systems** are classes with an `update(world, dt)` method.
- **World** coordinates entities, components, systems, and global **resources**.

Python **3.9+**.

---

## Quick Start

```python
from dataclasses import dataclass
from ecs import World, System

@dataclass
class Position:
    x: float
    y: float

@dataclass
class Velocity:
    dx: float
    dy: float

class Movement(System):
    def update(self, world: World, dt: float) -> None:
        for eid, pos, vel in world.view(Position, Velocity):
            pos.x += vel.dx * dt
            pos.y += vel.dy * dt

world = World()
world.add_system(Movement(priority=10))
world.start()

e = world.create_entity()
world.add_component(e, Position(0, 0))
world.add_component(e, Velocity(1, 0.5))

world.update(1/60)  # run a frame
world.stop()
```

---

## Directory Layout

```
ecs/
  __init__.py
  errors.py
  types.py
  entity.py
  storage.py
  system.py
  resources.py
  world.py
example_usage.py
```

---

## Concepts

### World

Central façade for:

* Entity lifecycle (`create_entity()`, `destroy_entity()`, `is_alive()`).
* Component operations (`add_component()`, `upsert_component()`, `remove_component()`, `get_component()`, `require_component()`, `has_component()`).
* Queries (`view(...)`, `entities_with(...)`).
* System management (`add_system()`, `remove_system()`, `start()`, `stop()`, `update(dt)`).
* Global resources via `world.resources`.

### Entities

* Opaque integer IDs managed by `EntityManager`.
* Reused IDs via a free-list; destroying an entity invalidates its components.

### Components

* Any Python object; dataclasses are a good fit.
* Stored as "type → {entity → instance}".
* Adding an existing component type to an entity raises `ComponentAlreadyExists`; use `upsert_component` to overwrite.

### Systems & Scheduler

* Subclass `ecs.System` and implement `update(world, dt)`.
* Optional `start(world)` / `stop(world)` hooks.
* `priority` (higher runs first) determines execution order each `world.update(dt)`.

### Resources

* Type-keyed container for global state (`put(obj)`, `get(Type)`, `try_get(Type)`, `remove(Type)`, `clear()`).
* Example: time accumulator, input state, random generator, configuration.

---

## Queries

Use `world.view(ComponentA, ComponentB, ...)` to iterate entities that have **all** listed components:

```python
for eid, pos in world.view(Position):
    ...

for eid, pos, vel in world.view(Position, Velocity):
    ...
```

* Yields live references to component instances; mutate in place.
* `world.entities_with(A, B)` yields just entity IDs.

---

## API Cheatsheet

**World**

* `create_entity() -> int`
* `destroy_entity(entity: int) -> None`
* `add_component(entity, component) -> None`
* `upsert_component(entity, component) -> None`
* `remove_component(entity, ctype) -> None`
* `get_component(entity, Type[T]) -> Optional[T]`
* `require_component(entity, Type[T]) -> T` (raises if missing)
* `has_component(entity, ctype) -> bool`
* `view(*ctypes) -> Iterator[(entity, ...components...)]`
* `entities_with(*ctypes) -> Iterator[int]`
* `add_system(system: System) -> None`
* `remove_system(system: System) -> bool`
* `start() / stop() / update(dt: float)`
* `clear()` (stops world, clears components/resources)

**Exceptions**

* `ECSException` (base)
* `EntityNotFound`
* `ComponentNotFound`
* `ComponentAlreadyExists`

---

## Design Notes

* **Storage:** Per-type maps (`component_type -> {entity -> component}`) + bidirectional indices for fast set-intersection queries.
* **Query cost:** Intersection of component entity sets; roughly `O(k * m)` where `k` is number of component types in the query and `m` is size of the smallest set.
* **Mutability:** Components are returned by reference; systems mutate them directly.
* **No threading:** This skeleton is **not** thread-safe. If you need concurrency, introduce a command buffer or stage writes.

---

## Lifecycle Tips

* Call `world.start()` before first `update()` to trigger `System.start()`.
* Call `world.stop()` to trigger `System.stop()` (reverse order).
* Destroying an entity automatically removes all of its components.

---

## Extending the Skeleton

* **Command buffers:** Add a deferred queue to avoid mutating storage during iteration.
* **Filters:** Support "with / without" queries or optional components.
* **Events:** Introduce a lightweight event bus (as a resource).
* **Serialization:** Add import/export for snapshots.
* **Profiling:** Track system durations and iteration counts.

---

## Known Limitations / TODO

* **Double start on hot-add:** Adding a system after `world.start()` currently calls `System.start()` **twice** (once via `Scheduler.add`, once in `World.add_system`). Fix by removing one of those start calls.
* **No removal callbacks:** There’s no hook for component removal or entity destruction beyond `System.stop()`.
* **No "without" queries:** Only conjunctive "has all" queries are supported.

---

## Example: Using Resources

```python
from dataclasses import dataclass
from ecs import World, System

@dataclass
class TimeScale:
    value: float

class ScaledMovement(System):
    def update(self, world: World, dt: float) -> None:
        scale = world.resources.try_get(TimeScale) or TimeScale(1.0)
        for eid, pos, vel in world.view(Position, Velocity):
            pos.x += vel.dx * dt * scale.value
            pos.y += vel.dy * dt * scale.value

world = World()
world.resources.put(TimeScale(0.5))
```

---

## Version & Requirements

* Python **3.9+**
* No third-party packages

---

## License

Copyright 2025 John Perkins

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
