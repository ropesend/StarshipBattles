"""
Conftest for systems module tests.

Provides fixtures and setup for systems-related tests.
"""
import pytest
import pygame

from tests.fixtures.paths import data_dir, project_root  # noqa: F401
from tests.fixtures.common import initialized_ship_data, initialized_ship_data_with_modifiers  # noqa: F401
from game.simulation.entities.ship import Ship
from game.core.registry import RegistryManager


@pytest.fixture(autouse=True)
def systems_test_setup():
    """Auto-setup for systems tests: initialize pygame and clean up after."""
    if not pygame.get_init():
        pygame.init()
    yield
    RegistryManager.instance().clear()


@pytest.fixture
def basic_cruiser_ship(initialized_ship_data):
    """Create a basic Cruiser ship for testing."""
    ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Cruiser")
    ship.recalculate_stats()
    return ship


@pytest.fixture
def basic_escort_ship(initialized_ship_data):
    """Create a basic Escort ship for testing."""
    ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
    ship.recalculate_stats()
    return ship
