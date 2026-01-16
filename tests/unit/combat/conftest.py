"""
Conftest for combat module tests.

Provides fixtures and setup for combat-related tests.
"""
import pytest
import pygame
from pathlib import Path

from tests.fixtures.paths import get_data_dir, get_project_root, get_unit_test_data_dir
from game.simulation.entities.ship import Ship, LayerType, initialize_ship_data
from game.simulation.components.component import load_components, load_modifiers, create_component
from game.core.registry import RegistryManager
from game.ai.controller import StrategyManager


@pytest.fixture(autouse=True)
def combat_test_setup():
    """Auto-setup for combat tests: initialize pygame and clean up after."""
    if not pygame.get_init():
        pygame.init()
    yield
    # Cleanup after each test
    RegistryManager.instance().clear()
    StrategyManager.instance().clear()


@pytest.fixture
def data_dir() -> Path:
    """Return the production data directory path."""
    return get_data_dir()


@pytest.fixture
def project_root() -> Path:
    """Return the project root path."""
    return get_project_root()


@pytest.fixture
def unit_test_data_dir() -> Path:
    """Return the unit test data directory path."""
    return get_unit_test_data_dir()


@pytest.fixture
def initialized_ship_data():
    """Initialize ship data from production data directory."""
    initialize_ship_data(str(get_project_root()))
    load_components(str(get_data_dir() / "components.json"))
    return True


@pytest.fixture
def initialized_ship_data_with_modifiers():
    """Initialize ship data and modifiers from production data directory."""
    initialize_ship_data(str(get_project_root()))
    data_dir = get_data_dir()
    load_components(str(data_dir / "components.json"))
    load_modifiers(str(data_dir / "modifiers.json"))
    return True


@pytest.fixture
def strategy_manager_with_test_data(unit_test_data_dir):
    """
    Set up StrategyManager with test data.

    Loads AI strategies from the test data directory.
    """
    manager = StrategyManager.instance()
    manager.load_data(
        str(unit_test_data_dir),
        targeting_file="test_targeting_policies.json",
        movement_file="test_movement_policies.json",
        strategy_file="test_combat_strategies.json"
    )
    manager._loaded = True
    yield manager
    manager.clear()


@pytest.fixture
def basic_combat_ship(initialized_ship_data):
    """Create a basic ship with bridge, crew quarters, and life support."""
    ship = Ship("CombatTestShip", 0, 0, (255, 255, 255), ship_class="Cruiser")
    ship.add_component(create_component('bridge'), LayerType.CORE)
    ship.add_component(create_component('crew_quarters'), LayerType.CORE)
    ship.add_component(create_component('life_support'), LayerType.CORE)
    ship.recalculate_stats()
    return ship


@pytest.fixture
def armed_combat_ship(initialized_ship_data):
    """Create a combat ship with weapons."""
    ship = Ship("ArmedShip", 0, 0, (255, 255, 255), ship_class="Cruiser")
    ship.add_component(create_component('bridge'), LayerType.CORE)
    ship.add_component(create_component('crew_quarters'), LayerType.CORE)
    ship.add_component(create_component('life_support'), LayerType.CORE)
    ship.add_component(create_component('laser_cannon'), LayerType.OUTER)
    ship.recalculate_stats()
    return ship
