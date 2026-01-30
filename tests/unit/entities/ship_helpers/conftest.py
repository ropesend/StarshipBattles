"""
Shared fixtures for Ship helper method tests.

These helper methods consolidate common layer iteration patterns,
reducing code duplication throughout the codebase.
"""
import pytest

from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component, create_component
from game.simulation.components.component_constants import LayerType


@pytest.fixture
def registry_with_components(fresh_registries):
    """
    Populate registries with test vehicle class and components.
    Uses fresh_registries fixture for isolation.
    """
    # Store registries for component creation
    regs = fresh_registries

    # Vehicle class with layers
    regs.vehicle_classes.update({
        "Escort": {
            "type": "Ship",
            "max_mass": 1000,
            "default_hull_id": "hull_escort",
            "layers": [
                {"type": "CORE", "radius_pct": 0.2, "restrictions": []},
                {"type": "INNER", "radius_pct": 0.5, "restrictions": []},
                {"type": "OUTER", "radius_pct": 0.8, "restrictions": []},
            ]
        }
    })

    # Hull component
    regs.components["hull_escort"] = Component({
        "id": "hull_escort",
        "name": "Escort Hull",
        "type": "Hull",
        "mass": 50,
        "hp": 100,
        "abilities": {"HullComponent": True}
    }, registries=regs)

    # Bridge with CommandAndControl
    regs.components["test_bridge"] = Component({
        "id": "test_bridge",
        "name": "Test Bridge",
        "type": "Bridge",
        "mass": 30,
        "hp": 40,
        "abilities": {"CommandAndControl": True}
    }, registries=regs)

    # Engine with CombatPropulsion
    regs.components["test_engine"] = Component({
        "id": "test_engine",
        "name": "Test Engine",
        "type": "Engine",
        "mass": 20,
        "hp": 30,
        "abilities": {"CombatPropulsion": {"thrust": 100}}
    }, registries=regs)

    # Weapon with WeaponAbility
    regs.components["test_laser"] = Component({
        "id": "test_laser",
        "name": "Test Laser",
        "type": "Weapon",
        "mass": 15,
        "hp": 25,
        "abilities": {"WeaponAbility": {"damage": 10, "range": 500}}
    }, registries=regs)

    # Shield Generator
    regs.components["test_shield"] = Component({
        "id": "test_shield",
        "name": "Test Shield",
        "type": "Shield",
        "mass": 25,
        "hp": 35,
        "abilities": {"ShieldGenerator": {"capacity": 50}}
    }, registries=regs)

    # Armor (no special abilities)
    regs.components["test_armor"] = Component({
        "id": "test_armor",
        "name": "Test Armor",
        "type": "Armor",
        "mass": 40,
        "hp": 60,
        "abilities": {}
    }, registries=regs)

    return regs


@pytest.fixture
def empty_ship(registry_with_components):
    """Create a ship with only the auto-equipped hull (no other components)."""
    return Ship(name="EmptyShip", x=0, y=0, color=(255, 255, 255), ship_class="Escort", registries=registry_with_components)


@pytest.fixture
def basic_ship(registry_with_components):
    """Create a ship with bridge and engine in CORE layer."""
    ship = Ship(name="BasicShip", x=0, y=0, color=(255, 255, 255), ship_class="Escort", registries=registry_with_components)

    bridge = create_component("test_bridge", registries=registry_with_components)
    engine = create_component("test_engine", registries=registry_with_components)

    if bridge:
        ship.add_component(bridge, LayerType.CORE)
    if engine:
        ship.add_component(engine, LayerType.CORE)

    ship.recalculate_stats()
    return ship


@pytest.fixture
def armed_ship(registry_with_components):
    """Create a ship with weapons, shields, and components across multiple layers."""
    ship = Ship(name="ArmedShip", x=0, y=0, color=(255, 255, 255), ship_class="Escort", registries=registry_with_components)

    # CORE layer: bridge, engine
    bridge = create_component("test_bridge", registries=registry_with_components)
    engine = create_component("test_engine", registries=registry_with_components)
    if bridge:
        ship.add_component(bridge, LayerType.CORE)
    if engine:
        ship.add_component(engine, LayerType.CORE)

    # INNER layer: shield
    shield = create_component("test_shield", registries=registry_with_components)
    if shield:
        ship.add_component(shield, LayerType.INNER)

    # OUTER layer: weapons and armor
    laser1 = create_component("test_laser", registries=registry_with_components)
    laser2 = create_component("test_laser", registries=registry_with_components)
    armor = create_component("test_armor", registries=registry_with_components)
    if laser1:
        ship.add_component(laser1, LayerType.OUTER)
    if laser2:
        ship.add_component(laser2, LayerType.OUTER)
    if armor:
        ship.add_component(armor, LayerType.OUTER)

    ship.recalculate_stats()
    return ship
