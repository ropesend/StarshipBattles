"""
Shared fixtures for FleetMovementEngine tests.
"""

import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.strategy.data.hex_math import HexCoord


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy for pathfinding."""
    galaxy = MagicMock()
    galaxy.systems = {}
    return galaxy


@pytest.fixture
def mock_fleet():
    """Create a mock fleet with standard movement attributes."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = HexCoord(0, 0)
    fleet.speed = 10.0
    fleet.path = []
    fleet.orders = []
    fleet.get_current_order = MagicMock(return_value=None)
    fleet.pop_order = MagicMock()
    fleet.clear_orders = MagicMock()
    fleet.has_resources_for_movement = MagicMock(return_value=True)
    fleet.has_resources_for_warp = MagicMock(return_value=True)
    fleet.can_use_warp = MagicMock(return_value=True)
    fleet.consume_movement_resources = MagicMock()
    fleet.consume_warp_resources = MagicMock()
    return fleet
