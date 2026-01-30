"""
Shared fixtures for turn engine tests.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.data.ship_instance import ShipInstance


@pytest.fixture
def turn_engine():
    """Create a fresh turn engine."""
    return TurnEngine()


@pytest.fixture
def mock_empire():
    """Create a mock empire."""
    empire = MagicMock(spec=Empire)
    empire.id = 0
    empire.name = "Test Empire"
    empire.fleets = []
    empire.colonies = []
    return empire


@pytest.fixture
def mock_fleet():
    """Create a mock fleet."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = HexCoord(0, 0)
    fleet.speed = 10.0
    fleet.orders = []
    fleet.path = []
    # Use mock ShipInstance instead of string
    mock_ship = MagicMock(spec=ShipInstance)
    mock_ship.name = "Colony Ship"
    mock_ship.is_combat_capable = MagicMock(return_value=True)
    fleet.ships = [mock_ship]
    fleet.get_current_order = MagicMock(return_value=None)
    fleet.pop_order = MagicMock()
    fleet.has_resources_for_movement = MagicMock(return_value=True)
    fleet.has_resources_for_warp = MagicMock(return_value=True)
    fleet.consume_movement_resources = MagicMock()
    fleet.consume_warp_resources = MagicMock()
    fleet.clear_orders = MagicMock()
    return fleet


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy."""
    galaxy = MagicMock()
    galaxy.systems = {}
    galaxy.get_planets_at_global_hex = MagicMock(return_value=[])
    galaxy.get_system_of_planet = MagicMock(return_value=None)
    return galaxy


@pytest.fixture
def mock_planet():
    """Create a mock unowned planet."""
    planet = MagicMock()
    planet.id = 1
    planet.name = "Test Planet"
    planet.owner_id = None
    planet.location = HexCoord(0, 0)
    planet.construction_queue = []
    planet.facilities = []
    planet.has_space_shipyard = True
    return planet
