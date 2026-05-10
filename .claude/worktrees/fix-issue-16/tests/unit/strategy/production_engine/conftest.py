"""Shared fixtures for ProductionEngine tests."""
import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.engine.production_engine import ProductionEngine


@pytest.fixture
def production_engine(fresh_registries):
    """Create a ProductionEngine with registries.

    PROJ-218: Now requires registries for cost calculation via Ship loading.
    """
    return ProductionEngine(registries=fresh_registries)


@pytest.fixture
def mock_empire():
    """Create a mock empire."""
    empire = MagicMock()
    empire.id = 0
    empire.name = "Test Empire"
    empire.colonies = []
    empire.fleets = []
    empire.add_fleet = MagicMock()
    empire.get_next_fleet_id = MagicMock(return_value=1)
    return empire


@pytest.fixture
def mock_planet():
    """Create a mock planet/colony."""
    planet = MagicMock()
    planet.id = 1
    planet.name = "Test Colony"
    planet.owner_id = 0
    planet.location = HexCoord(5, 5)
    planet.construction_queue = []
    planet.facilities = []
    planet.has_space_shipyard = True
    return planet


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy."""
    galaxy = MagicMock()
    galaxy.get_system_of_planet = MagicMock(return_value=None)
    return galaxy
