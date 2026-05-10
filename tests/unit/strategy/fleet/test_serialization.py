"""Tests for Fleet module - serialization and deserialization."""
import pytest

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.core.hex_math import HexCoord


class TestFleetSerialization:
    """Test cases for fleet serialization."""

    def test_to_dict_basic(self, make_ship_instance):
        """Test basic fleet serialization."""
        fleet = Fleet("f1", 0, HexCoord(2, 3), speed=7.5)
        ship = make_ship_instance(name="Scout")
        fleet.ships.append(ship)  # Bypass add_ship to avoid speed recalc

        d = fleet.to_dict()

        assert d['id'] == 'f1'
        assert d['owner_id'] == 0
        assert d['speed'] == 7.5
        assert len(d['ships']) == 1
        assert d['ships'][0]['name'] == 'Scout'
        assert d['ships'][0]['design_id'] == 'Scout'

    def test_from_dict_basic(self):
        """Test basic fleet deserialization."""
        ship_data = {
            'instance_id': 'test-destroyer',
            'design_id': 'Destroyer',
            'name': 'Destroyer',
            'owner_id': 1,
            'design_data': {'name': 'Destroyer', 'vehicle_type': 'Ship'},
            'components': {},
        }
        d = {
            'id': 'f1',
            'owner_id': 1,
            'location': [5, -2],
            'speed': 6.0,
            'ships': [ship_data],
            'orders': [],
            'path': [],
        }

        fleet = Fleet.from_dict(d)

        assert fleet.id == 'f1'
        assert fleet.owner_id == 1
        assert fleet.location == HexCoord(5, -2)
        assert fleet.speed == 6.0
        assert len(fleet.ships) == 1
        assert fleet.ships[0].name == 'Destroyer'

    def test_roundtrip_serialization(self, make_ship_instance):
        """Test serialization roundtrip preserves data (BUG-77 fix)."""
        original = Fleet("test_fleet", 0, HexCoord(3, -1), speed=8.0)
        original.ships.append(make_ship_instance(name="Cruiser"))
        original.ships.append(make_ship_instance(name="Frigate"))

        d = original.to_dict()

        # HexCoord should now serialize properly without manual fix
        restored = Fleet.from_dict(d)

        assert restored.id == original.id
        assert restored.owner_id == original.owner_id
        assert restored.location == original.location
        assert restored.speed == original.speed
        assert len(restored.ships) == 2
        assert restored.ships[0].name == "Cruiser"
        assert restored.ships[1].name == "Frigate"

    def test_to_dict_serializes_hexcoord_location(self):
        """Test that HexCoord location is properly serialized (BUG-77 fix)."""
        fleet = Fleet("f1", 0, HexCoord(2, 3))
        d = fleet.to_dict()

        # HexCoord should serialize as {'q': 2, 'r': 3}
        assert d['location'] == {'q': 2, 'r': 3}

    def test_from_dict_restores_hexcoord_dict_format(self):
        """Test that {'q': ..., 'r': ...} location format is deserialized (BUG-77 fix)."""
        d = {
            'id': 'f1',
            'owner_id': 0,
            'location': {'q': 7, 'r': -3},
            'speed': 5.0,
            'ships': [],
            'orders': [],
            'path': [],
        }

        fleet = Fleet.from_dict(d)

        assert fleet.location == HexCoord(7, -3)

    def test_repr(self, make_ship_instance):
        """Test fleet string representation."""
        fleet = Fleet("f1", 0, HexCoord(1, 2), speed=5.0)
        fleet.ships.append(make_ship_instance(name="Scout"))
        fleet.ships.append(make_ship_instance(name="Destroyer"))

        r = repr(fleet)
        assert "f1" in r
        assert "Owner:0" in r
        assert "Ships:2" in r

    def test_from_dict_restores_move_orders(self):
        """Test that MOVE orders are restored from serialized data (STRAT-001)."""
        d = {
            'id': 'f1',
            'owner_id': 0,
            'location': [0, 0],
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'MOVE', 'target': {'q': 5, 'r': 3}}
            ],
            'path': [],
        }

        fleet = Fleet.from_dict(d)

        assert len(fleet.orders) == 1
        assert fleet.orders[0].type == OrderType.MOVE
        # Target should be HexCoord
        assert fleet.orders[0].target == HexCoord(5, 3)

    def test_from_dict_restores_colonize_orders(self):
        """Test that COLONIZE orders are restored from serialized data."""
        d = {
            'id': 'f1',
            'owner_id': 0,
            'location': [0, 0],
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'COLONIZE', 'target': None}
            ],
            'path': [],
        }

        fleet = Fleet.from_dict(d)

        assert len(fleet.orders) == 1
        assert fleet.orders[0].type == OrderType.COLONIZE
        assert fleet.orders[0].target is None

    def test_warp_order_serialization_roundtrip(self):
        """Test that WARP orders are properly serialized and restored (PROJ-187)."""
        warp_target = HexCoord(10, 5)
        fleet = Fleet("f1", 0, HexCoord(0, 0), speed=5.0)
        fleet.orders.append(Order(OrderType.WARP, target=warp_target))

        # Serialize
        d = fleet.to_dict()

        # Verify serialized format
        assert len(d['orders']) == 1
        assert d['orders'][0]['type'] == 'WARP'
        assert d['orders'][0]['target'] == {'q': 10, 'r': 5}

        # Deserialize
        restored = Fleet.from_dict(d)

        # Verify restored order
        assert len(restored.orders) == 1
        assert restored.orders[0].type == OrderType.WARP
        assert restored.orders[0].target == warp_target

    def test_roundtrip_orders_preserved(self):
        """Test that orders survive serialization roundtrip."""
        original = Fleet("test", 0, HexCoord(0, 0))
        original.add_order(Order(OrderType.MOVE, HexCoord(2, 2)))

        d = original.to_dict()

        restored = Fleet.from_dict(d)

        assert len(restored.orders) == 1
        assert restored.orders[0].type == OrderType.MOVE


class TestFleetOrderExecutionProgress:
    """Test cases for Order execution_progress tracking (PROJ-187 Phase 1)."""

    def test_fleet_order_execution_progress_default_zero(self):
        """Test that Order.execution_progress defaults to 0."""
        order = Order(OrderType.MOVE, HexCoord(1, 2))
        assert order.execution_progress == 0

    def test_fleet_order_execution_progress_settable(self):
        """Test that execution_progress can be set."""
        order = Order(OrderType.COLONIZE, None)
        order.execution_progress = 5
        assert order.execution_progress == 5

    def test_fleet_order_repr_excludes_zero_progress(self):
        """Test that repr excludes execution_progress when it's 0."""
        order = Order(OrderType.MOVE, HexCoord(1, 2))
        r = repr(order)
        assert "execution_progress" not in r
        assert "MOVE" in r

    def test_fleet_order_repr_includes_nonzero_progress(self):
        """Test that repr includes execution_progress when > 0."""
        order = Order(OrderType.COLONIZE, None)
        order.execution_progress = 3
        r = repr(order)
        assert "progress=3" in r

    def test_fleet_order_to_dict_excludes_zero_progress(self):
        """Test that to_dict excludes execution_progress when it's 0."""
        order = Order(OrderType.MOVE, HexCoord(1, 2))
        d = order.to_dict()
        assert 'execution_progress' not in d

    def test_fleet_order_to_dict_includes_nonzero_progress(self):
        """Test that to_dict includes execution_progress when > 0."""
        order = Order(OrderType.COLONIZE, None)
        order.execution_progress = 7
        d = order.to_dict()
        assert d['execution_progress'] == 7

    def test_fleet_order_roundtrip_with_progress(self):
        """Test that execution_progress survives Fleet serialization roundtrip."""
        fleet = Fleet("test", 0, HexCoord(0, 0))
        order = Order(OrderType.COLONIZE, None)
        order.execution_progress = 3
        fleet.add_order(order)

        d = fleet.to_dict()
        restored = Fleet.from_dict(d)

        assert len(restored.orders) == 1
        assert restored.orders[0].execution_progress == 3

    def test_fleet_order_roundtrip_zero_progress(self):
        """Test that zero progress (default) survives roundtrip."""
        fleet = Fleet("test", 0, HexCoord(0, 0))
        order = Order(OrderType.MOVE, HexCoord(5, 5))
        fleet.add_order(order)

        d = fleet.to_dict()
        restored = Fleet.from_dict(d)

        assert len(restored.orders) == 1
        assert restored.orders[0].execution_progress == 0

    def test_backward_compat_old_save_without_progress(self):
        """Test that old saves without execution_progress load with default 0."""
        d = {
            'id': 'f1',
            'owner_id': 0,
            'location': [0, 0],
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'COLONIZE', 'target': None}
                # Note: no execution_progress field
            ],
            'path': [],
        }

        fleet = Fleet.from_dict(d)

        assert len(fleet.orders) == 1
        assert fleet.orders[0].execution_progress == 0


class TestWarpOrderType:
    """Test cases for OrderType.WARP (PROJ-187 Phase 1)."""

    def test_warp_order_type_exists(self):
        """Test that WARP is a valid OrderType."""
        assert hasattr(OrderType, 'WARP')
        assert OrderType.WARP.name == 'WARP'

    def test_warp_order_creation(self):
        """Test creating a Order with WARP type."""
        target = HexCoord(3, 4)
        order = Order(OrderType.WARP, target)
        assert order.type == OrderType.WARP
        assert order.target == target

    def test_warp_order_serialization(self):
        """Test that WARP orders serialize correctly."""
        target = HexCoord(5, 6)
        order = Order(OrderType.WARP, target)
        d = order.to_dict()
        assert d['type'] == 'WARP'
        assert d['target'] == {'q': 5, 'r': 6}

    def test_warp_order_roundtrip(self):
        """Test that WARP orders survive Fleet serialization roundtrip."""
        fleet = Fleet("test", 0, HexCoord(0, 0))
        fleet.add_order(Order(OrderType.WARP, HexCoord(7, 8)))

        d = fleet.to_dict()
        restored = Fleet.from_dict(d)

        assert len(restored.orders) == 1
        assert restored.orders[0].type == OrderType.WARP
        assert restored.orders[0].target == HexCoord(7, 8)
