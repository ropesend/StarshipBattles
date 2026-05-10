"""
Fixtures for ShipCombatEngine unit tests.
"""

import pytest
from unittest.mock import MagicMock

from game.core.math import Vector2


@pytest.fixture
def mock_ship():
    """Create a mock ship for testing."""
    ship = MagicMock()
    ship.position = Vector2(0, 0)
    ship.velocity = Vector2(0, 0)
    ship.team_id = 0
    ship.is_alive = True
    ship.is_derelict = False
    return ship


@pytest.fixture
def armed_ship(fresh_registries):
    """Create an armed ship for testing."""
    from tests.fixtures.ships import create_test_ship
    return create_test_ship(
        name="TestShip",
        x=0, y=0,
        team_id=0,
        add_bridge=True,
        add_engine=True,
        add_weapons=2,
        registries=fresh_registries,
    )
