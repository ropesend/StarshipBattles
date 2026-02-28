"""
Shared fixtures for conflict resolution engine tests.
"""

import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord


@pytest.fixture
def mock_fleet():
    """Create a mock fleet."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = HexCoord(0, 0)
    mock_ship = MagicMock()
    mock_ship.name = "Test Ship"
    fleet.ships = [mock_ship]
    # PROJ-210: battle adapter is now accessed via fleet.battle property
    fleet.battle = MagicMock()
    fleet.battle.update_from_battle_results = MagicMock()
    return fleet


@pytest.fixture
def mock_empire():
    """Create a mock empire."""
    empire = MagicMock()
    empire.id = 0
    empire.name = "Test Empire"
    empire.fleets = []
    return empire
