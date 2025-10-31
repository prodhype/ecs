# example_usage.py


from dataclasses import dataclass

from ecs import System, World


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


def main() -> None:
    world = World()
    world.add_system(Movement(priority=10))
    world.start()

    e1 = world.create_entity()
    world.add_component(e1, Position(0, 0))
    world.add_component(e1, Velocity(1, 0.5))

    world.update(1 / 60)
    world.update(1 / 60)

    world.stop()


if __name__ == "__main__":
    main()
