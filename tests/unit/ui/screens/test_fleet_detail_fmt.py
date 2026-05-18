import pytest
from unittest.mock import MagicMock
from game.ui.screens.strategy_detail_fmt import format_fleet_info
from game.strategy.data.order_types import OrderType


# --- Mock Helpers ---

def _make_mock_ship(design_id: str, design_name: str, mass: float, cargo=None):
    """Create a MagicMock ship with design, mass, and optional cargo.

    PROJ-436 Phase 3c: production reads cargo via
    ``ship._cargo_mgr.get_all_cargo()``; wire the manager method
    instead of (or in addition to) the legacy dict.
    """
    ship = MagicMock()
    ship.design_id = design_id
    ship.design_data = {'name': design_name}
    ship.get_calculated_stats.return_value = {'mass': mass}
    ship.cargo_contents = cargo or {}
    ship._cargo_mgr.get_all_cargo.return_value = cargo or {}
    return ship


def _make_mock_fleet(fleet_id=1, owner_id=0, ships=None, orders=None,
                     speed=5.0, fuel_endurance=20):
    """Create a MagicMock fleet with configurable attributes."""
    fleet = MagicMock()
    fleet.id = fleet_id
    fleet.owner_id = owner_id
    fleet.ships = ships or []
    fleet.orders = orders or []
    fleet.speed = speed
    fleet.resources.fuel_endurance.return_value = fuel_endurance
    fleet.location = MagicMock(__str__=lambda self: "(0, 0)")
    fleet.construction_queue = []
    return fleet


# --- Existing TRANSFER Tests ---

def test_format_fleet_info_with_transfer_order():
    """Verify that TRANSFER orders are formatted correctly in fleet info."""
    # Arrange
    fleet = _make_mock_fleet(fleet_id=5, owner_id=1, ships=[MagicMock(), MagicMock()])

    # Mock a TRANSFER order
    order = MagicMock()
    order.type = OrderType.TRANSFER
    order.target = {
        'direction': 'load',
        'cargo_type': 'passengers',
        'amount': 50
    }
    fleet.orders = [order]

    # Act
    html = format_fleet_info(fleet)

    # Assert
    assert "LOAD 50 passengers" in html

def test_format_fleet_info_with_transfer_all():
    """Verify that TRANSFER orders with amount 0 are formatted as 'All'."""
    # Arrange
    fleet = _make_mock_fleet(fleet_id=5, owner_id=1)

    order = MagicMock()
    order.type = OrderType.TRANSFER
    order.target = {
        'direction': 'unload',
        'cargo_type': 'passengers',
        'amount': 0
    }
    fleet.orders = [order]

    # Act
    html = format_fleet_info(fleet)

    # Assert
    assert "UNLOAD All passengers" in html


# --- Travel Range Tests ---

class TestFormatFleetInfoTravelRange:
    """Tests for travel range section of format_fleet_info()."""

    def test_travel_range_normal(self):
        """Fleet with speed=5.0 and fuel_endurance=20 shows both values."""
        fleet = _make_mock_fleet(speed=5.0, fuel_endurance=20)
        html = format_fleet_info(fleet)
        assert "5 hex/turn" in html
        assert "20 hex fuel" in html

    def test_unlimited_fuel(self):
        """Fleet with fuel_endurance=-1 shows 'unlimited fuel'."""
        fleet = _make_mock_fleet(fuel_endurance=-1)
        html = format_fleet_info(fleet)
        assert "unlimited fuel" in html.lower()

    def test_zero_speed(self):
        """Empty fleet with speed=0 shows '0 hex/turn'."""
        fleet = _make_mock_fleet(speed=0.0, fuel_endurance=-1)
        html = format_fleet_info(fleet)
        assert "0 hex/turn" in html


# --- Ship Grouping Tests ---

class TestFormatFleetInfoShipGrouping:
    """Tests for ship grouping section of format_fleet_info()."""

    def test_ship_grouping(self):
        """Ships are grouped by design_id with count."""
        ships = [
            _make_mock_ship("Destroyer", "Destroyer", 5000),
            _make_mock_ship("Destroyer", "Destroyer", 5000),
            _make_mock_ship("Scout", "Scout", 1000),
        ]
        fleet = _make_mock_fleet(ships=ships)
        html = format_fleet_info(fleet)
        assert "Destroyer x 2" in html
        assert "Scout" in html
        assert "Ships (3):" in html

    def test_sorted_by_mass(self):
        """Ships are sorted by mass descending (heaviest first)."""
        ships = [
            _make_mock_ship("Scout", "Scout", 1000),
            _make_mock_ship("Destroyer", "Destroyer", 5000),
        ]
        fleet = _make_mock_fleet(ships=ships)
        html = format_fleet_info(fleet)
        destroyer_pos = html.index("Destroyer")
        scout_pos = html.index("Scout")
        assert destroyer_pos < scout_pos, "Destroyer (heavier) should appear before Scout"

    def test_single_ship_no_multiplier(self):
        """A single ship should show name without 'x 1'."""
        ships = [_make_mock_ship("Frigate", "Frigate", 3000)]
        fleet = _make_mock_fleet(ships=ships)
        html = format_fleet_info(fleet)
        assert "Frigate" in html
        assert "x 1" not in html

    def test_empty_fleet(self):
        """Empty fleet shows 'Ships: None' and does not crash."""
        fleet = _make_mock_fleet(ships=[])
        html = format_fleet_info(fleet)
        assert "Ships: None" in html


# --- Cargo Summary Tests ---

class TestFormatFleetInfoCargoSummary:
    """Tests for cargo summary section of format_fleet_info()."""

    def test_cargo_summary(self):
        """Cargo from multiple ships is aggregated correctly."""
        ships = [
            _make_mock_ship("Transport", "Transport", 2000, cargo={'passengers': 50}),
            _make_mock_ship("Transport", "Transport", 2000,
                            cargo={'passengers': 30, 'minerals': 10}),
        ]
        fleet = _make_mock_fleet(ships=ships)
        html = format_fleet_info(fleet)
        assert "Passengers: 80" in html
        assert "Minerals: 10" in html

    def test_no_cargo(self):
        """Fleet with no cargo should not show 'Cargo:' section."""
        ships = [
            _make_mock_ship("Destroyer", "Destroyer", 5000, cargo={}),
        ]
        fleet = _make_mock_fleet(ships=ships)
        html = format_fleet_info(fleet)
        assert "Cargo:" not in html


# --- Order Formatting Tests ---

class TestFormatFleetInfoOrders:
    """Tests for order formatting section of format_fleet_info()."""

    def test_move_order(self):
        """MOVE order shows target hex."""
        order = MagicMock()
        order.type = OrderType.MOVE
        order.target = MagicMock(__str__=lambda self: "(5, 3)")
        fleet = _make_mock_fleet(orders=[order])
        html = format_fleet_info(fleet)
        assert "MOVE" in html
        assert "(5, 3)" in html

    def test_build_order(self):
        """BUILD order shows queue size."""
        order = MagicMock()
        order.type = OrderType.BUILD
        fleet = _make_mock_fleet(orders=[order])
        fleet.construction_queue = [MagicMock(), MagicMock()]
        html = format_fleet_info(fleet)
        assert "BUILDING (2 items)" in html

    def test_no_orders(self):
        """Empty orders list shows '(No Orders)'."""
        fleet = _make_mock_fleet(orders=[])
        html = format_fleet_info(fleet)
        assert "(No Orders)" in html
