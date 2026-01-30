"""
Shared fixtures for pathfinding tests.
"""

import pytest
from unittest.mock import MagicMock

from game.strategy.data.hex_math import HexCoord
from game.strategy.data.fleet import Fleet


@pytest.fixture
def origin():
    """Origin hex coordinate."""
    return HexCoord(0, 0)


@pytest.fixture
def nearby_hex():
    """A hex 5 units away."""
    return HexCoord(5, 0)


@pytest.fixture
def distant_hex():
    """A hex far away."""
    return HexCoord(100, 50)


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy with star systems."""
    galaxy = MagicMock()

    # Create mock systems
    sys_a = MagicMock()
    sys_a.name = "Alpha"
    sys_a.global_location = HexCoord(0, 0)
    sys_a.warp_points = []

    sys_b = MagicMock()
    sys_b.name = "Beta"
    sys_b.global_location = HexCoord(50, 0)
    sys_b.warp_points = []

    sys_c = MagicMock()
    sys_c.name = "Gamma"
    sys_c.global_location = HexCoord(100, 0)
    sys_c.warp_points = []

    # Create warp points connecting systems
    wp_a_to_b = MagicMock()
    wp_a_to_b.destination_id = "Beta"
    wp_a_to_b.location = HexCoord(5, 0)  # Local coords within system

    wp_b_to_a = MagicMock()
    wp_b_to_a.destination_id = "Alpha"
    wp_b_to_a.location = HexCoord(-5, 0)

    wp_b_to_c = MagicMock()
    wp_b_to_c.destination_id = "Gamma"
    wp_b_to_c.location = HexCoord(5, 0)

    wp_c_to_b = MagicMock()
    wp_c_to_b.destination_id = "Beta"
    wp_c_to_b.location = HexCoord(-5, 0)

    sys_a.warp_points = [wp_a_to_b]
    sys_b.warp_points = [wp_b_to_a, wp_b_to_c]
    sys_c.warp_points = [wp_c_to_b]

    # Set up galaxy systems
    galaxy.systems = {
        HexCoord(0, 0): sys_a,
        HexCoord(50, 0): sys_b,
        HexCoord(100, 0): sys_c,
    }

    def get_system_by_name(name):
        for sys in galaxy.systems.values():
            if sys.name == name:
                return sys
        return None

    galaxy.get_system_by_name = get_system_by_name

    return galaxy, sys_a, sys_b, sys_c


@pytest.fixture
def mock_fleet(origin):
    """Create a mock fleet at origin."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.location = origin
    fleet.speed = 10.0
    fleet.orders = []
    fleet.path = []
    return fleet
