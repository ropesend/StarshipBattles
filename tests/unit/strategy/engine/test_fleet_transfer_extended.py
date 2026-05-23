"""
Tests for OrderProcessor fleet-to-fleet transfer, resource cargo load/unload,
and BUG-70 auto-resolve colony.

PROJ-264 Phase 2: Coverage for zero-coverage methods in order_processor.py.
"""

import pytest
from game.strategy.data.order_types import OrderType
from unittest.mock import MagicMock

from game.strategy.engine.order_processor import OrderProcessor


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def processor():
    return OrderProcessor()


def _make_cargo_transfer_fleet(cargo_current=50, cargo_capacity=100):
    """Create a mock fleet with configurable cargo state."""
    fleet = MagicMock()
    fleet.resources = MagicMock()
    fleet.resources.get_fleet_cargo_current = MagicMock(return_value=cargo_current)
    fleet.resources.get_fleet_cargo_capacity = MagicMock(return_value=cargo_capacity)
    fleet.resources.load_cargo_to_fleet = MagicMock()
    fleet.resources.unload_cargo_from_fleet = MagicMock(return_value=cargo_current)
    fleet.location = MagicMock()
    fleet.ships = []
    return fleet


def _make_planet(stockpile=200, owner_id=0):
    """Create a mock planet with stockpile."""
    planet = MagicMock()
    planet.id = 100
    planet.name = "Colony"
    planet.owner_id = owner_id
    planet.get_stockpile = MagicMock(return_value=stockpile)
    planet.consume_from_stockpile = MagicMock()
    planet.add_to_stockpile = MagicMock()
    planet.populations = []
    return planet


def _make_empire(empire_id=0):
    empire = MagicMock()
    empire.id = empire_id
    empire.race_config = MagicMock()
    empire.race_config.race_id = "humans"
    return empire


# =============================================================================
# _execute_fleet_transfer Tests
# =============================================================================


class TestExecuteFleetTransfer:
    """Tests for OrderProcessor._execute_fleet_transfer()."""

    def test_unload_direction_transfers_from_fleet_to_target(self, processor):
        """Unload direction: source=fleet, dest=target_fleet."""
        fleet = _make_cargo_transfer_fleet(cargo_current=80, cargo_capacity=100)
        target = _make_cargo_transfer_fleet(cargo_current=10, cargo_capacity=100)
        fleet.resources.unload_cargo_from_fleet.return_value = 50

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_fleet_to_fleet(fleet, target, "metals", "unload", 50)

        assert result == 50
        fleet.resources.unload_cargo_from_fleet.assert_called_once_with("metals", 50)
        target.resources.load_cargo_to_fleet.assert_called_once_with("metals", 50)

    def test_load_direction_transfers_from_target_to_fleet(self, processor):
        """Load direction: source=target_fleet, dest=fleet."""
        fleet = _make_cargo_transfer_fleet(cargo_current=10, cargo_capacity=100)
        target = _make_cargo_transfer_fleet(cargo_current=80, cargo_capacity=100)
        target.resources.unload_cargo_from_fleet.return_value = 50

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_fleet_to_fleet(fleet, target, "metals", "load", 50)

        assert result == 50
        target.resources.unload_cargo_from_fleet.assert_called_once_with("metals", 50)
        fleet.resources.load_cargo_to_fleet.assert_called_once_with("metals", 50)

    def test_caps_by_source_cargo(self, processor):
        """Transfer capped by source's available cargo."""
        fleet = _make_cargo_transfer_fleet(cargo_current=20, cargo_capacity=100)  # Only 20 available
        target = _make_cargo_transfer_fleet(cargo_current=0, cargo_capacity=100)
        fleet.resources.unload_cargo_from_fleet.return_value = 20

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_fleet_to_fleet(fleet, target, "fuel", "unload", 50)

        assert result == 20

    def test_caps_by_dest_space(self, processor):
        """Transfer capped by destination's available space."""
        fleet = _make_cargo_transfer_fleet(cargo_current=100, cargo_capacity=100)
        target = _make_cargo_transfer_fleet(cargo_current=90, cargo_capacity=100)  # Only 10 space
        fleet.resources.unload_cargo_from_fleet.return_value = 10

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_fleet_to_fleet(fleet, target, "fuel", "unload", 50)

        assert result == 10

    def test_amount_zero_transfers_all(self, processor):
        """amount=0 means transfer all available cargo."""
        fleet = _make_cargo_transfer_fleet(cargo_current=30, cargo_capacity=100)
        target = _make_cargo_transfer_fleet(cargo_current=0, cargo_capacity=100)
        fleet.resources.unload_cargo_from_fleet.return_value = 30

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_fleet_to_fleet(fleet, target, "metals", "unload", 0)

        assert result == 30

    def test_zero_space_returns_zero(self, processor):
        """Zero available space returns 0."""
        fleet = _make_cargo_transfer_fleet(cargo_current=50, cargo_capacity=100)
        target = _make_cargo_transfer_fleet(cargo_current=100, cargo_capacity=100)  # Full

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_fleet_to_fleet(fleet, target, "metals", "unload", 50)

        assert result == 0

    def test_zero_source_returns_zero(self, processor):
        """Zero source cargo returns 0."""
        fleet = _make_cargo_transfer_fleet(cargo_current=0, cargo_capacity=100)  # Empty
        target = _make_cargo_transfer_fleet(cargo_current=0, cargo_capacity=100)

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_fleet_to_fleet(fleet, target, "metals", "unload", 50)

        assert result == 0


# =============================================================================
# _execute_load Resource Cargo Tests
# =============================================================================


class TestExecuteLoadResource:
    """Tests for _execute_load() resource cargo path (non-passenger, non-drop_pod)."""

    def test_loads_from_planet_stockpile(self, processor):
        """Loads resource from planet stockpile to fleet."""
        fleet = _make_cargo_transfer_fleet(cargo_current=0, cargo_capacity=100)
        planet = _make_planet(stockpile=200)
        empire = _make_empire()

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_load_planet_resource(fleet, planet, "metals", 50)

        assert result == 50
        planet.consume_from_stockpile.assert_called_once_with("metals", 50.0)
        fleet.resources.load_cargo_to_fleet.assert_called_once_with("metals", 50)

    def test_caps_by_fleet_space(self, processor):
        """Capped by fleet available cargo space."""
        fleet = _make_cargo_transfer_fleet(cargo_current=90, cargo_capacity=100)  # Only 10 space
        planet = _make_planet(stockpile=200)
        empire = _make_empire()

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_load_planet_resource(fleet, planet, "metals", 50)

        assert result == 10

    def test_caps_by_stockpile(self, processor):
        """Capped by planet stockpile amount."""
        fleet = _make_cargo_transfer_fleet(cargo_current=0, cargo_capacity=100)
        planet = _make_planet(stockpile=5)  # Only 5 available
        empire = _make_empire()

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_load_planet_resource(fleet, planet, "metals", 50)

        assert result == 5

    def test_amount_zero_loads_max(self, processor):
        """amount=0 loads maximum possible."""
        fleet = _make_cargo_transfer_fleet(cargo_current=0, cargo_capacity=100)
        planet = _make_planet(stockpile=200)
        empire = _make_empire()

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_load_planet_resource(fleet, planet, "metals", 0)

        assert result == 100  # Limited by fleet capacity

    def test_zero_stockpile_returns_zero(self, processor):
        """Empty stockpile returns 0."""
        fleet = _make_cargo_transfer_fleet(cargo_current=0, cargo_capacity=100)
        planet = _make_planet(stockpile=0)
        empire = _make_empire()

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_load_planet_resource(fleet, planet, "metals", 50)

        assert result == 0


# =============================================================================
# _execute_unload Resource Cargo Tests
# =============================================================================


class TestExecuteUnloadResource:
    """Tests for _execute_unload() resource cargo path."""

    def test_unloads_to_planet_stockpile(self, processor):
        """Unloads resource from fleet to planet stockpile."""
        fleet = _make_cargo_transfer_fleet(cargo_current=80, cargo_capacity=100)
        fleet.resources.unload_cargo_from_fleet.return_value = 50
        planet = _make_planet()
        empire = _make_empire()

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_unload_planet_resource(fleet, planet, "metals", 50)

        assert result == 50
        fleet.resources.unload_cargo_from_fleet.assert_called_once_with("metals", 50)
        planet.add_to_stockpile.assert_called_once_with("metals", 50.0)

    def test_caps_by_fleet_cargo(self, processor):
        """Capped by fleet's current cargo."""
        fleet = _make_cargo_transfer_fleet(cargo_current=20, cargo_capacity=100)
        fleet.resources.unload_cargo_from_fleet.return_value = 20
        planet = _make_planet()
        empire = _make_empire()

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_unload_planet_resource(fleet, planet, "metals", 50)

        assert result == 20

    def test_amount_zero_unloads_all(self, processor):
        """amount=0 unloads all cargo."""
        fleet = _make_cargo_transfer_fleet(cargo_current=75, cargo_capacity=100)
        fleet.resources.unload_cargo_from_fleet.return_value = 75
        planet = _make_planet()
        empire = _make_empire()

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_unload_planet_resource(fleet, planet, "metals", 0)

        assert result == 75

    def test_zero_cargo_returns_zero(self, processor):
        """Fleet with no cargo returns 0."""
        fleet = _make_cargo_transfer_fleet(cargo_current=0, cargo_capacity=100)
        planet = _make_planet()
        empire = _make_empire()

        result = processor._handler_registry.get(OrderType.TRANSFER)._dispatch_unload_planet_resource(fleet, planet, "metals", 50)

        assert result == 0
