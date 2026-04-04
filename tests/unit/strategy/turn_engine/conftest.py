"""
Shared fixtures for turn engine tests.

PROJ-55: Updated mock_fleet and mock_planet to include colony pod requirements.
"""
import pytest
from enum import Enum
from unittest.mock import MagicMock

from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.data.ship_instance import ShipInstance


# PROJ-55: Mock planet type enum for tests
class MockPlanetType(Enum):
    CONTINENTAL = "CONTINENTAL"


@pytest.fixture
def turn_engine(fresh_registries):
    """Create a fresh turn engine with DI registries."""
    return TurnEngine(registries=fresh_registries)


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
    """Create a mock fleet with colony pod ship.

    PROJ-55: Ships now need colony pods to colonize specific planet types.
    PROJ-67: Added construction_queue and is_building for fleet yards.
    """
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = HexCoord(0, 0)
    fleet.speed = 10.0
    fleet.orders = []
    fleet.path = []
    # PROJ-67: Fleet production attributes
    fleet.construction_queue = []
    fleet.is_building = False
    fleet.has_space_shipyard = False
    # Use mock ShipInstance with colony pod design data (PROJ-55)
    mock_ship = MagicMock(spec=ShipInstance)
    mock_ship.name = "Colony Ship"
    mock_ship.is_combat_capable = MagicMock(return_value=True)
    # PROJ-55: Add design_data with colony pod for CONTINENTAL planet type
    mock_ship.design_data = {
        'layers': {
            'HULL': [{'id': 'colony_pod'}]
        }
    }
    fleet.ships = [mock_ship]
    # PROJ-55: remove_ship must actually modify ships list for fleet removal logic
    fleet.remove_ship = MagicMock(side_effect=lambda ship: fleet.ships.remove(ship))
    fleet.get_current_order = MagicMock(return_value=None)
    fleet.pop_order = MagicMock()
    fleet.resources.has_resources_for_movement = MagicMock(return_value=True)
    fleet.resources.has_resources_for_warp = MagicMock(return_value=True)
    fleet.resources.consume_movement_resources = MagicMock()
    fleet.resources.consume_warp_resources = MagicMock()
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
    """Create a mock unowned planet.

    PROJ-55: Includes planet_type attribute for colony pod matching.
    """
    planet = MagicMock()
    planet.id = 1
    planet.name = "Test Planet"
    planet.owner_id = None
    planet.location = HexCoord(0, 0)
    planet.construction_queue = []
    planet.facilities = []
    planet.has_space_shipyard = True
    # PROJ-55: Add planet type to match the colony pod in mock_fleet
    planet.planet_type = MockPlanetType.CONTINENTAL
    return planet
