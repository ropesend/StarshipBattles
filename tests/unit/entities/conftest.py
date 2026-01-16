"""
Conftest for entities module tests.

Provides fixtures and setup for entity-related tests.
"""
import pytest
import pygame
from pathlib import Path

from tests.fixtures.paths import get_data_dir, get_project_root, get_unit_test_data_dir
from game.simulation.entities.ship import Ship, LayerType, initialize_ship_data
from game.simulation.components.component import load_components, load_modifiers, create_component
from game.core.registry import RegistryManager


@pytest.fixture(autouse=True)
def entities_test_setup():
    """Auto-setup for entities tests: initialize pygame and clean up after."""
    if not pygame.get_init():
        pygame.init()
    yield
    RegistryManager.instance().clear()


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
def basic_ship(initialized_ship_data):
    """Create a basic ship with bridge, crew quarters, and life support."""
    ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Cruiser")
    ship.add_component(create_component('bridge'), LayerType.CORE)
    ship.add_component(create_component('crew_quarters'), LayerType.CORE)
    ship.add_component(create_component('life_support'), LayerType.CORE)
    ship.recalculate_stats()
    return ship
