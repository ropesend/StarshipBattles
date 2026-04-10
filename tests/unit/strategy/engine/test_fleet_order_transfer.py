"""
Unit tests for OrderProcessor TRANSFER operations.

PROJ-119 Task 1.2: TCG-STR-002 - OrderProcessor Transfer logic has minimal tests.
Tests focus on cargo transfer between fleets and colonies.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_fleet():
    """Create a mock fleet for transfer tests."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = HexCoord(5, 5)
    fleet.orders = []
    fleet.get_current_order = MagicMock(return_value=None)
    fleet.pop_order = MagicMock()
    # PROJ-210: cargo methods accessed via fleet.resources property
    fleet.resources = MagicMock()
    fleet.resources.get_fleet_cargo_capacity = MagicMock(return_value=100)
    fleet.resources.get_fleet_cargo_current = MagicMock(return_value=50)
    fleet.resources.load_cargo_to_fleet = MagicMock()
    fleet.resources.unload_cargo_from_fleet = MagicMock(return_value=50)
    return fleet


@pytest.fixture
def mock_empire():
    """Create a mock empire."""
    empire = MagicMock()
    empire.id = 0
    empire.name = "Test Empire"
    empire.race_config = MagicMock()
    empire.race_config.race_id = "humans"
    return empire


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy."""
    galaxy = MagicMock()
    galaxy.get_planet_by_id = MagicMock(return_value=None)
    # Setup system containment for transfer validation
    mock_system = MagicMock()
    mock_system.planets = []  # Will be populated per-test
    galaxy.get_system_at_location = MagicMock(return_value=mock_system)
    galaxy.systems = {'sys1': mock_system}
    galaxy._mock_system = mock_system  # Expose for test access
    return galaxy


@pytest.fixture
def mock_planet():
    """Create a mock planet for transfer tests."""
    planet = MagicMock()
    planet.id = 100
    planet.name = "Colony Alpha"
    planet.location = HexCoord(5, 5)
    planet.owner_id = 0
    planet.populations = []
    # Required for is_planet() protocol check (IPlanet)
    planet.planet_type = MagicMock()
    planet.deposits = {}
    return planet


@pytest.fixture
def processor():
    """Create a OrderProcessor."""
    from game.strategy.engine.order_processor import OrderProcessor
    return OrderProcessor()


# =============================================================================
# Test: TRANSFER Order Processing
# =============================================================================

class TestProcessTransfer:
    """Tests for process_transfer() method."""

    def test_transfer_no_order_returns_failure(self, processor, mock_fleet, mock_empire, mock_galaxy):
        """Returns failure when no TRANSFER order exists."""
        mock_fleet.get_current_order.return_value = None

        result = processor.process_transfer(mock_fleet, mock_empire, mock_galaxy)

        assert result.success is False

    def test_transfer_wrong_order_type_returns_failure(self, processor, mock_fleet, mock_empire, mock_galaxy):
        """Returns failure when current order is not TRANSFER."""
        order = FleetOrder(OrderType.MOVE, HexCoord(10, 10))
        mock_fleet.get_current_order.return_value = order

        result = processor.process_transfer(mock_fleet, mock_empire, mock_galaxy)

        assert result.success is False

    def test_transfer_invalid_params_returns_failure(self, processor, mock_fleet, mock_empire, mock_galaxy):
        """Returns failure when transfer params are invalid."""
        order = FleetOrder(OrderType.TRANSFER, "not_a_dict")
        mock_fleet.get_current_order.return_value = order

        result = processor.process_transfer(mock_fleet, mock_empire, mock_galaxy)

        assert result.success is False
        mock_fleet.pop_order.assert_called()

