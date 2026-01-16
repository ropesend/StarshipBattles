"""
Shared ship-related fixtures for tests.

This module provides common ship initialization fixtures that are used
across multiple test modules. Import these fixtures into module conftest.py
files or use the pytest_plugins mechanism.

Usage in conftest.py:
    from tests.fixtures.ship_fixtures import (
        initialized_ship_data,
        initialized_ship_data_with_modifiers,
        basic_cruiser_ship,
        basic_escort_ship,
    )
"""
import pytest
from pathlib import Path

from tests.fixtures.paths import get_data_dir, get_project_root
from game.simulation.entities.ship import Ship, LayerType, initialize_ship_data
from game.simulation.components.component import load_components, load_modifiers, create_component


@pytest.fixture
def initialized_ship_data():
    """
    Initialize ship data from production data directory.

    This fixture loads vehicle classes and components from the data/ directory,
    making the ship system ready for testing.

    Note: Requires cleanup via RegistryManager.instance().clear() after test.
    """
    initialize_ship_data(str(get_project_root()))
    load_components(str(get_data_dir() / "components.json"))
    return True


@pytest.fixture
def initialized_ship_data_with_modifiers():
    """
    Initialize ship data and modifiers from production data directory.

    Like initialized_ship_data but also loads the modifiers.json file.

    Note: Requires cleanup via RegistryManager.instance().clear() after test.
    """
    initialize_ship_data(str(get_project_root()))
    data_dir = get_data_dir()
    load_components(str(data_dir / "components.json"))
    load_modifiers(str(data_dir / "modifiers.json"))
    return True


@pytest.fixture
def basic_cruiser_ship(initialized_ship_data):
    """
    Create a basic Cruiser ship for testing.

    The Cruiser class has 4 layers (CORE, INNER, OUTER, ARMOR) which makes
    it suitable for testing features that require the INNER layer.
    """
    ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Cruiser")
    ship.recalculate_stats()
    return ship


@pytest.fixture
def basic_escort_ship(initialized_ship_data):
    """
    Create a basic Escort ship for testing.

    The Escort class has 3 layers (CORE, OUTER, ARMOR) and is a smaller
    ship class suitable for basic testing.
    """
    ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
    ship.recalculate_stats()
    return ship


@pytest.fixture
def equipped_cruiser_ship(initialized_ship_data):
    """
    Create a Cruiser ship with basic infrastructure (bridge, crew, life support).

    This ship has minimal components to function properly for tests that
    need a "working" ship without weapons.
    """
    ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Cruiser")
    ship.add_component(create_component('bridge'), LayerType.CORE)
    ship.add_component(create_component('crew_quarters'), LayerType.CORE)
    ship.add_component(create_component('life_support'), LayerType.CORE)
    ship.recalculate_stats()
    return ship


@pytest.fixture
def armed_cruiser_ship(initialized_ship_data):
    """
    Create a Cruiser ship with basic infrastructure and a weapon.

    Includes bridge, crew quarters, life support, and a laser cannon.
    """
    ship = Ship("ArmedShip", 0, 0, (255, 255, 255), ship_class="Cruiser")
    ship.add_component(create_component('bridge'), LayerType.CORE)
    ship.add_component(create_component('crew_quarters'), LayerType.CORE)
    ship.add_component(create_component('life_support'), LayerType.CORE)
    ship.add_component(create_component('laser_cannon'), LayerType.OUTER)
    ship.recalculate_stats()
    return ship
