"""
Shared fixtures for fleet navigation service tests.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.hex_math import HexCoord
from game.strategy.data.fleet import Fleet


@pytest.fixture
def basic_fleet():
    """Create a basic fleet for testing."""
    fleet = Fleet(
        fleet_id='test-fleet',
        owner_id=0,
        location=HexCoord(0, 0),
        speed=5.0
    )
    fleet.path = []
    fleet.orders = []
    fleet.can_use_warp = MagicMock(return_value=False)
    return fleet


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy for testing."""
    return MagicMock()
