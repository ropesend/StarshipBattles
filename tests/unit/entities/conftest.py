"""
Conftest for entities module tests.

Provides fixtures and setup for entity-related tests.
"""
import pytest
import pygame

from tests.fixtures.paths import data_dir, project_root, unit_test_data_dir  # noqa: F401
from tests.fixtures.common import initialized_ship_data, initialized_ship_data_with_modifiers  # noqa: F401
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import create_component
from game.core.registry import RegistryManager


@pytest.fixture(autouse=True)
def entities_test_setup():
    """Auto-setup for entities tests: initialize pygame and clean up after."""
    if not pygame.get_init():
        pygame.init()
    yield
    RegistryManager.instance().clear()


@pytest.fixture
def basic_ship(initialized_ship_data):
    """Create a basic ship with bridge, crew quarters, and life support."""
    ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Cruiser")
    ship.add_component(create_component('bridge'), LayerType.CORE)
    ship.add_component(create_component('crew_quarters'), LayerType.CORE)
    ship.add_component(create_component('life_support'), LayerType.CORE)
    ship.recalculate_stats()
    return ship
