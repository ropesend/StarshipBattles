from typing import TYPE_CHECKING

from game.simulation.entities.ship import Ship
from game.simulation.components.component import create_component
from game.core.constants import LayerType

if TYPE_CHECKING:
    from game.core.registry import GameRegistries


def create_brick(x, y, *, registries: 'GameRegistries'):
    """Create "The Brick" ship - a heavily armored cruiser.

    Args:
        x: X position
        y: Y position
        registries: GameRegistries for component creation
    """
    ship = Ship("The Brick", x, y, (150, 150, 150), ship_class="Cruiser", registries=registries)

    ship.add_component(create_component("bridge", registries=registries), LayerType.CORE)

    for _ in range(15):
         ship.add_component(create_component("armor_plate", registries=registries), LayerType.ARMOR)

    ship.add_component(create_component("railgun", registries=registries), LayerType.OUTER)
    ship.add_component(create_component("standard_engine", registries=registries), LayerType.INNER)
    ship.add_component(create_component("standard_engine", registries=registries), LayerType.INNER)
    ship.add_component(create_component("thruster", registries=registries), LayerType.INNER)
    ship.add_component(create_component("thruster", registries=registries), LayerType.INNER)

    ship.add_component(create_component("fuel_tank", registries=registries), LayerType.CORE)
    ship.add_component(create_component("ordnance_tank", registries=registries), LayerType.CORE)
    ship.add_component(create_component("generator", registries=registries), LayerType.INNER)

    return ship


def create_interceptor(x, y, *, registries: 'GameRegistries'):
    """Create "The Interceptor" ship - a fast maneuverable cruiser.

    Args:
        x: X position
        y: Y position
        registries: GameRegistries for component creation
    """
    ship = Ship("The Interceptor", x, y, (50, 200, 50), ship_class="Cruiser", registries=registries)

    ship.add_component(create_component("bridge", registries=registries), LayerType.CORE)

    ship.add_component(create_component("railgun", registries=registries), LayerType.OUTER)
    ship.add_component(create_component("railgun", registries=registries), LayerType.OUTER)

    ship.add_component(create_component("standard_engine", registries=registries), LayerType.INNER)
    ship.add_component(create_component("standard_engine", registries=registries), LayerType.INNER)
    ship.add_component(create_component("standard_engine", registries=registries), LayerType.OUTER)
    ship.add_component(create_component("standard_engine", registries=registries), LayerType.OUTER)

    for _ in range(6):
        ship.add_component(create_component("thruster", registries=registries), LayerType.INNER)

    ship.add_component(create_component("fuel_tank", registries=registries), LayerType.CORE)
    ship.add_component(create_component("fuel_tank", registries=registries), LayerType.INNER)
    ship.add_component(create_component("ordnance_tank", registries=registries), LayerType.CORE)
    ship.add_component(create_component("ordnance_tank", registries=registries), LayerType.INNER)
    ship.add_component(create_component("generator", registries=registries), LayerType.INNER)

    return ship
