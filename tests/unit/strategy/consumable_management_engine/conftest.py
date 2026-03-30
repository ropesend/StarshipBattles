"""
Shared fixtures for ConsumableManagementEngine tests.

PROJ-50: Added mock_registries fixture for strict DI.
"""

import pytest
from unittest.mock import MagicMock
from game.core.registry import GameRegistries


@pytest.fixture
def mock_registries():
    """Create minimal registries for testing."""
    return GameRegistries(
        components={},
        modifiers={},
        vehicle_classes={},
        resources={}
    )


@pytest.fixture
def mock_ship():
    """Create a mock ship with resource consumption capabilities."""
    ship = MagicMock()
    ship.name = "Test Ship"
    ship.is_combat_capable = MagicMock(return_value=True)
    ship.get_all_resource_costs_per_turn = MagicMock(return_value={})
    ship.consume_resource = MagicMock(return_value=True)
    ship.set_component_enabled = MagicMock()
    ship.design_data = {'layers': {}}
    return ship


@pytest.fixture
def mock_fleet(mock_ship):
    """Create a mock fleet with ships."""
    fleet = MagicMock()
    fleet.id = 1
    fleet.ships = [mock_ship]
    return fleet


@pytest.fixture
def mock_empire(mock_fleet):
    """Create a mock empire."""
    empire = MagicMock()
    empire.id = 0
    empire.name = "Test Empire"
    empire.fleets = [mock_fleet]
    return empire
