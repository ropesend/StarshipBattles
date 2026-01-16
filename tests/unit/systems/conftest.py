"""
Conftest for systems module tests.

Provides fixtures and setup for systems-related tests.
"""
import pytest
import pygame
from pathlib import Path

from tests.fixtures.paths import get_data_dir, get_project_root
from game.simulation.entities.ship import Ship, initialize_ship_data
from game.simulation.components.component import load_components, load_modifiers
from game.core.registry import RegistryManager


@pytest.fixture(autouse=True)
def systems_test_setup():
    """Auto-setup for systems tests: initialize pygame and clean up after."""
    if not pygame.get_init():
        pygame.init()
    yield
    RegistryManager.instance().clear()


@pytest.fixture
def data_dir() -> Path:
    """Return the data directory path."""
    return get_data_dir()


@pytest.fixture
def project_root() -> Path:
    """Return the project root path."""
    return get_project_root()


@pytest.fixture
def initialized_ship_data():
    """Initialize ship data from the project root."""
    initialize_ship_data(str(get_project_root()))
    load_components(str(get_data_dir() / "components.json"))
    return True


@pytest.fixture
def initialized_ship_data_with_modifiers():
    """Initialize ship data with modifiers loaded."""
    initialize_ship_data(str(get_project_root()))
    data_dir = get_data_dir()
    load_components(str(data_dir / "components.json"))
    load_modifiers(str(data_dir / "modifiers.json"))
    return True


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
