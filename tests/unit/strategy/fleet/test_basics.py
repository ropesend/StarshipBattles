"""Tests for Fleet module - basic operations, orders, merging, and equality."""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord


class TestFleetOrder:
    """Test cases for FleetOrder class."""

    def test_creation_move_order(self):
        """Test creating a MOVE order."""
        target = HexCoord(5, 3)
        order = FleetOrder(OrderType.MOVE, target)
        assert order.type == OrderType.MOVE
        assert order.target == target

    def test_creation_no_target(self):
        """Test creating order without target."""
        order = FleetOrder(OrderType.COLONIZE)
        assert order.type == OrderType.COLONIZE
        assert order.target is None

    def test_repr(self):
        """Test string representation."""
        order = FleetOrder(OrderType.JOIN_FLEET, "target_fleet")
        assert "JOIN_FLEET" in repr(order)

    def test_to_dict_with_coord_target(self):
        """Test serializing order with coordinate target."""
        # Use real HexCoord for isinstance check
        coord = HexCoord(2, 4)
        order = FleetOrder(OrderType.MOVE, coord)
        d = order.to_dict()
        assert d['type'] == 'MOVE'
        assert d['target'] == {'q': 2, 'r': 4}

    def test_to_dict_with_fleet_ref(self):
        """Test serializing order with fleet reference target."""
        # Use MagicMock with spec=Fleet for isinstance check
        mock_fleet = MagicMock(spec=Fleet)
        mock_fleet.id = "fleet_123"
        order = FleetOrder(OrderType.JOIN_FLEET, mock_fleet)
        d = order.to_dict()
        assert d['target']['type'] == 'fleet_ref'
        assert d['target']['id'] == 'fleet_123'


class TestFleet:
    """Test cases for Fleet class."""

    def test_creation(self, basic_fleet):
        """Test fleet creation with basic parameters."""
        assert basic_fleet.id == "fleet_1"
        assert basic_fleet.owner_id == 0
        assert basic_fleet.location == HexCoord(0, 0)
        assert basic_fleet.speed == 5.0
        assert basic_fleet.ships == []
        assert basic_fleet.orders == []
        assert basic_fleet.path == []

    def test_add_ship(self, basic_fleet, make_mock_ship):
        """Test adding a ShipInstance to fleet."""
        ship = make_mock_ship(name="Destroyer")
        basic_fleet.add_ship(ship)
        assert ship in basic_fleet.ships
        assert len(basic_fleet.ships) == 1

    def test_add_multiple_ships(self, basic_fleet, make_mock_ship):
        """Test adding multiple ships."""
        ship1 = make_mock_ship(name="Scout")
        ship2 = make_mock_ship(name="Cruiser")
        ship3 = make_mock_ship(name="Scout")
        basic_fleet.add_ship(ship1)
        basic_fleet.add_ship(ship2)
        basic_fleet.add_ship(ship3)
        assert len(basic_fleet.ships) == 3

    def test_remove_ship(self, basic_fleet, make_mock_ship):
        """Test removing a ship from fleet."""
        destroyer = make_mock_ship(name="Destroyer")
        scout = make_mock_ship(name="Scout")
        basic_fleet.add_ship(destroyer)
        basic_fleet.add_ship(scout)

        result = basic_fleet.remove_ship(destroyer)
        assert result is True
        assert destroyer not in basic_fleet.ships
        assert len(basic_fleet.ships) == 1

    def test_remove_ship_not_found(self, basic_fleet, make_mock_ship):
        """Test removing a ship that doesn't exist."""
        scout = make_mock_ship(name="Scout")
        battleship = make_mock_ship(name="Battleship")
        basic_fleet.add_ship(scout)
        result = basic_fleet.remove_ship(battleship)
        assert result is False
        assert len(basic_fleet.ships) == 1

    def test_get_ship_names(self, basic_fleet, make_mock_ship):
        """Test getting ship names from ShipInstance objects."""
        scout = make_mock_ship(name="Scout")
        destroyer = make_mock_ship(name="Destroyer")
        basic_fleet.add_ship(scout)
        basic_fleet.add_ship(destroyer)
        names = basic_fleet.get_ship_names()
        assert "Scout" in names
        assert "Destroyer" in names


class TestFleetOrders:
    """Test cases for fleet order management."""

    @pytest.fixture
    def fleet(self):
        """Create a fleet for order testing."""
        return Fleet("f1", 0, HexCoord(0, 0))

    def test_add_order(self, fleet):
        """Test adding an order to queue."""
        order = FleetOrder(OrderType.MOVE, HexCoord(5, 0))
        fleet.add_order(order)
        assert len(fleet.orders) == 1
        assert fleet.orders[0] == order

    def test_add_order_at_index(self, fleet):
        """Test adding order at specific index."""
        order1 = FleetOrder(OrderType.MOVE, HexCoord(1, 0))
        order2 = FleetOrder(OrderType.MOVE, HexCoord(2, 0))
        order3 = FleetOrder(OrderType.MOVE, HexCoord(3, 0))

        fleet.add_order(order1)
        fleet.add_order(order3)
        fleet.add_order(order2, index=1)

        assert fleet.orders[0] == order1
        assert fleet.orders[1] == order2
        assert fleet.orders[2] == order3

    def test_get_current_order(self, fleet):
        """Test getting current (first) order."""
        order = FleetOrder(OrderType.MOVE, HexCoord(5, 0))
        fleet.add_order(order)
        assert fleet.get_current_order() == order

    def test_get_current_order_empty(self, fleet):
        """Test getting current order when queue is empty."""
        assert fleet.get_current_order() is None

    def test_pop_order(self, fleet):
        """Test popping an order from queue."""
        order1 = FleetOrder(OrderType.MOVE, HexCoord(1, 0))
        order2 = FleetOrder(OrderType.MOVE, HexCoord(2, 0))
        fleet.add_order(order1)
        fleet.add_order(order2)
        fleet.path = [HexCoord(0, 0), HexCoord(1, 0)]

        popped = fleet.pop_order()
        assert popped == order1
        assert len(fleet.orders) == 1
        assert fleet.orders[0] == order2
        assert fleet.path == []  # Path cleared on pop

    def test_pop_order_empty(self, fleet):
        """Test popping from empty queue returns None."""
        result = fleet.pop_order()
        assert result is None

    def test_clear_orders(self, fleet):
        """Test clearing all orders."""
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(1, 0)))
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(2, 0)))
        fleet.path = [HexCoord(0, 0), HexCoord(1, 0)]

        fleet.clear_orders()
        assert fleet.orders == []
        assert fleet.path == []


class TestFleetRemoveOrderAt:
    """Test cases for Fleet.remove_order_at() (PROJ-222 Phase 2)."""

    @pytest.fixture
    def fleet(self):
        return Fleet("f1", 0, HexCoord(0, 0))

    def test_remove_order_at_valid_index(self, fleet):
        order1 = FleetOrder(OrderType.MOVE, HexCoord(1, 0))
        order2 = FleetOrder(OrderType.MOVE, HexCoord(2, 0))
        fleet.add_order(order1)
        fleet.add_order(order2)

        removed = fleet.remove_order_at(0)
        assert removed is order1
        assert len(fleet.orders) == 1
        assert fleet.orders[0] is order2

    def test_remove_order_at_index_zero_clears_path(self, fleet):
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(1, 0)))
        fleet.path = [HexCoord(0, 0), HexCoord(1, 0)]

        fleet.remove_order_at(0)
        assert fleet.path == []

    def test_remove_order_at_invalid_index_returns_none(self, fleet):
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(1, 0)))
        assert fleet.remove_order_at(5) is None
        assert fleet.remove_order_at(-1) is None
        assert len(fleet.orders) == 1  # Unchanged

    def test_remove_order_at_middle_preserves_path(self, fleet):
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(1, 0)))
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(2, 0)))
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(3, 0)))
        fleet.path = [HexCoord(0, 0)]

        removed = fleet.remove_order_at(1)
        assert removed is not None
        assert len(fleet.orders) == 2
        assert fleet.path == [HexCoord(0, 0)]  # Path preserved


class TestFleetRemoveOrdersByType:
    """Test cases for Fleet.remove_orders_by_type() (PROJ-222 Phase 2)."""

    @pytest.fixture
    def fleet(self):
        return Fleet("f1", 0, HexCoord(0, 0))

    def test_remove_orders_by_type_removes_matching(self, fleet):
        fleet.add_order(FleetOrder(OrderType.BUILD))
        fleet.add_order(FleetOrder(OrderType.BUILD))
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(1, 0)))

        removed = fleet.remove_orders_by_type(OrderType.BUILD)
        assert len(removed) == 2
        assert all(o.type == OrderType.BUILD for o in removed)
        assert len(fleet.orders) == 1

    def test_remove_orders_by_type_preserves_others(self, fleet):
        move_order = FleetOrder(OrderType.MOVE, HexCoord(1, 0))
        join_order = FleetOrder(OrderType.JOIN_FLEET, target="some_fleet")
        fleet.add_order(move_order)
        fleet.add_order(FleetOrder(OrderType.BUILD))
        fleet.add_order(join_order)

        fleet.remove_orders_by_type(OrderType.BUILD)
        assert len(fleet.orders) == 2
        assert fleet.orders[0] is move_order
        assert fleet.orders[1] is join_order

    def test_remove_orders_by_type_no_matches(self, fleet):
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(1, 0)))
        removed = fleet.remove_orders_by_type(OrderType.BUILD)
        assert removed == []
        assert len(fleet.orders) == 1


class TestFleetMerge:
    """Test cases for fleet merging."""

    def test_merge_transfers_ships(self, make_mock_ship):
        """Test that merge transfers ships to target fleet."""
        fleet1 = Fleet("f1", 0, HexCoord(0, 0))
        fleet2 = Fleet("f2", 0, HexCoord(0, 0))

        scout = make_mock_ship(name="Scout")
        destroyer = make_mock_ship(name="Destroyer")
        cruiser = make_mock_ship(name="Cruiser")

        fleet1.add_ship(scout)
        fleet1.add_ship(destroyer)
        fleet2.add_ship(cruiser)

        fleet1.merge_with(fleet2)

        assert len(fleet1.ships) == 0  # Source fleet emptied
        assert len(fleet2.ships) == 3  # Target fleet has all ships
        assert scout in fleet2.ships
        assert destroyer in fleet2.ships
        assert cruiser in fleet2.ships

    def test_merge_clears_source_orders(self):
        """Test that merge clears orders on source fleet."""
        fleet1 = Fleet("f1", 0, HexCoord(0, 0))
        fleet2 = Fleet("f2", 0, HexCoord(0, 0))

        fleet1.add_order(FleetOrder(OrderType.MOVE, HexCoord(5, 0)))
        fleet1.merge_with(fleet2)

        assert fleet1.orders == []

    def test_merge_with_non_fleet(self, make_mock_ship):
        """Test merge with non-Fleet object does nothing."""
        fleet1 = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(name="Scout")
        fleet1.add_ship(ship)

        fleet1.merge_with("not a fleet")

        assert len(fleet1.ships) == 1  # Ship not removed


class TestFleetPursuerTrackerIntegration:
    """Test that Fleet has a pursuer_tracker property (PROJ-222 Phase 3)."""

    def test_fleet_has_pursuer_tracker(self):
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        assert hasattr(fleet, 'pursuer_tracker')
        assert fleet.pursuer_tracker.pursuer_count == 0


class TestFleetEquality:
    """Test cases for fleet equality and hashing."""

    def test_equality_by_id(self):
        """Test fleets are equal if they have the same ID."""
        fleet1 = Fleet("same_id", 0, HexCoord(0, 0))
        fleet2 = Fleet("same_id", 1, HexCoord(5, 5))  # Different owner/location

        assert fleet1 == fleet2

    def test_inequality_different_id(self):
        """Test fleets are not equal if IDs differ."""
        fleet1 = Fleet("id_1", 0, HexCoord(0, 0))
        fleet2 = Fleet("id_2", 0, HexCoord(0, 0))

        assert fleet1 != fleet2

    def test_inequality_with_non_fleet(self):
        """Test fleet is not equal to non-Fleet."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        assert fleet != "f1"
        assert fleet != None

    def test_hash_for_set(self):
        """Test fleets can be used in sets."""
        fleet1 = Fleet("f1", 0, HexCoord(0, 0))
        fleet2 = Fleet("f1", 1, HexCoord(5, 5))
        fleet3 = Fleet("f2", 0, HexCoord(0, 0))

        s = {fleet1, fleet2, fleet3}
        assert len(s) == 2  # fleet1 and fleet2 have same ID
