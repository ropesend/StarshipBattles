"""Round-trip tests for Order serialization (PROJ-223 Phase 2).

Tests all 7 target formats at the serialization level.
Fleet/planet reference RESOLUTION is tested in Phase 4.
"""

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.order_types import OrderType, Order
from game.strategy.data.order_serializer import OrderSerializer


class TestFleetOrderHexCoordTarget:
    """MOVE/WARP orders with HexCoord target."""

    def test_move_hex_coord_round_trip(self):
        order = Order(OrderType.MOVE, HexCoord(5, -3))
        d = order.to_dict()
        assert d['target'] == {'q': 5, 'r': -3}

        orders = OrderSerializer.deserialize_orders([d], fleet_id="test")
        assert len(orders) == 1
        assert orders[0].type == OrderType.MOVE
        assert orders[0].target == HexCoord(5, -3)

    def test_warp_hex_coord_round_trip(self):
        order = Order(OrderType.WARP, HexCoord(-2, 7))
        d = order.to_dict()
        orders = OrderSerializer.deserialize_orders([d], fleet_id="test")
        assert orders[0].type == OrderType.WARP
        assert orders[0].target == HexCoord(-2, 7)


class TestFleetOrderFleetRefTarget:
    """MOVE_TO_FLEET/JOIN_FLEET orders with fleet references."""

    def test_fleet_ref_serialization(self):
        """Fleet reference is serialized as {'type': 'fleet_ref', 'id': N}."""
        # Simulate a fleet reference using a mock fleet with .id
        class MockFleet:
            id = 42
        from game.strategy.data.fleet import Fleet as RealFleet

        # Use a real Fleet object for serialization
        target_fleet = Fleet.__new__(Fleet)
        target_fleet.id = 42

        order = Order(OrderType.MOVE_TO_FLEET, target_fleet)
        d = order.to_dict()
        assert d['target'] == {'type': 'fleet_ref', 'id': 42}

    def test_fleet_ref_deserialization(self):
        """Fleet ref is deserialized as a marker dict (not resolved yet)."""
        d = {'type': 'MOVE_TO_FLEET', 'target': {'type': 'fleet_ref', 'id': 42}}
        orders = OrderSerializer.deserialize_orders([d], fleet_id="test")
        assert len(orders) == 1
        assert orders[0].type == OrderType.MOVE_TO_FLEET
        assert orders[0].target == {'_fleet_ref': 42}  # Marker dict


class TestFleetOrderPlanetRefTarget:
    """COLONIZE/IMPLODE_PLANET orders with planet references."""

    def test_planet_ref_deserialization(self):
        """Planet ref is deserialized as a marker dict."""
        d = {'type': 'COLONIZE', 'target': {'type': 'planet_ref', 'id': 7}}
        orders = OrderSerializer.deserialize_orders([d], fleet_id="test")
        assert len(orders) == 1
        assert orders[0].type == OrderType.COLONIZE
        assert orders[0].target == {'_planet_ref': 7}  # Marker dict


class TestFleetOrderTransferTarget:
    """TRANSFER orders with transfer parameter dict."""

    def test_transfer_round_trip(self):
        transfer_params = {
            "direction": "unload",
            "cargo_type": "minerals",
            "amount": 100,
            "planet_id": 5,
        }
        order = Order(OrderType.TRANSFER, transfer_params)
        d = order.to_dict()
        assert d['target'] == {'type': 'transfer', 'value': transfer_params}

        orders = OrderSerializer.deserialize_orders([d], fleet_id="test")
        assert orders[0].target == transfer_params


class TestFleetOrderWarpParamsTarget:
    """OPEN_WARP_POINT orders with warp parameters."""

    def test_warp_params_round_trip(self):
        warp_params = {
            "destination_system": "Alpha Centauri",
            "energy_cost": 500,
        }
        order = Order(OrderType.OPEN_WARP_POINT, warp_params)
        d = order.to_dict()
        assert d['target'] == {'type': 'warp_params', 'value': warp_params}

        orders = OrderSerializer.deserialize_orders([d], fleet_id="test")
        assert orders[0].target == warp_params


class TestFleetOrderShipIdListTarget:
    """SELF_DESTRUCT orders with ship ID list."""

    def test_ship_id_list_round_trip(self):
        ship_ids = ["ship_001", "ship_003", "ship_005"]
        order = Order(OrderType.SELF_DESTRUCT, ship_ids)
        d = order.to_dict()
        assert d['target'] == {'type': 'ship_id_list', 'value': ship_ids}

        orders = OrderSerializer.deserialize_orders([d], fleet_id="test")
        assert orders[0].target == ship_ids


class TestFleetOrderExecutionProgress:
    """Execution progress preservation."""

    def test_progress_greater_than_zero_serialized(self):
        order = Order(OrderType.COLONIZE, HexCoord(0, 0))
        order.execution_progress = 5
        d = order.to_dict()
        assert d['execution_progress'] == 5

    def test_progress_zero_omitted(self):
        order = Order(OrderType.MOVE, HexCoord(0, 0))
        d = order.to_dict()
        assert 'execution_progress' not in d

    def test_progress_preserved_round_trip(self):
        order = Order(OrderType.MOVE, HexCoord(3, -1))
        order.execution_progress = 12
        d = order.to_dict()
        orders = OrderSerializer.deserialize_orders([d], fleet_id="test")
        assert orders[0].execution_progress == 12


class TestFleetOrderAllOrderTypes:
    """All OrderType enum values can be serialized/deserialized."""

    @pytest.mark.parametrize("order_type", list(OrderType))
    def test_order_type_round_trip(self, order_type):
        """Every OrderType enum serializes to its name and back."""
        d = {'type': order_type.name, 'target': None}
        orders = OrderSerializer.deserialize_orders([d], fleet_id="test")
        assert len(orders) == 1
        assert orders[0].type == order_type


# Import Fleet for mock fleet ref test
from game.strategy.data.fleet import Fleet
