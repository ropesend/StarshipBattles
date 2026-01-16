"""
Conftest for combat module tests.

Provides fixtures and setup for combat-related tests.
"""
import pytest
import pygame

from tests.fixtures.paths import data_dir, project_root, unit_test_data_dir, get_unit_test_data_dir  # noqa: F401
from tests.fixtures.common import initialized_ship_data, initialized_ship_data_with_modifiers  # noqa: F401
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import create_component
from game.core.registry import RegistryManager
from game.ai.controller import StrategyManager


@pytest.fixture(autouse=True)
def combat_test_setup():
    """Auto-setup for combat tests: initialize pygame and clean up after."""
    if not pygame.get_init():
        pygame.init()
    yield
    RegistryManager.instance().clear()
    StrategyManager.instance().clear()


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
    _ = initialized_ship_data  # Ensure ship data is loaded
    ship = Ship("CombatTestShip", 0, 0, (255, 255, 255), ship_class="Cruiser")
    ship.add_component(create_component('bridge'), LayerType.CORE)
    ship.add_component(create_component('crew_quarters'), LayerType.CORE)
    ship.add_component(create_component('life_support'), LayerType.CORE)
    ship.recalculate_stats()
    return ship


@pytest.fixture
def armed_combat_ship(initialized_ship_data):
    """Create a combat ship with weapons."""
    _ = initialized_ship_data  # Ensure ship data is loaded
    ship = Ship("ArmedShip", 0, 0, (255, 255, 255), ship_class="Cruiser")
    ship.add_component(create_component('bridge'), LayerType.CORE)
    ship.add_component(create_component('crew_quarters'), LayerType.CORE)
    ship.add_component(create_component('life_support'), LayerType.CORE)
    ship.add_component(create_component('laser_cannon'), LayerType.OUTER)
    ship.recalculate_stats()
    return ship
