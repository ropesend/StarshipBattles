"""Unit tests for OrderSerializer.

Tests the three public methods:
- deserialize_orders: list deserialization with corrupt-entry handling
- _deserialize_target: all 7 target formats (tested indirectly via deserialize_orders)
- resolve_order_references: fleet/planet reference resolution and pruning

Also tests round-trip serialization (Order.to_dict -> OrderSerializer.deserialize_orders).
"""

import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.data.order_types import OrderType, Order
from game.strategy.data.order_serializer import OrderSerializer


# ---------------------------------------------------------------------------
# deserialize_orders — basic behavior
# ---------------------------------------------------------------------------

class TestDeserializeOrdersBasic:
    """Tests for OrderSerializer.deserialize_orders basic functionality."""

    def test_empty_list_returns_empty(self):
        result = OrderSerializer.deserialize_orders([], fleet_id="f1")
        assert result == []

    def test_single_valid_order(self):
        data = [{'type': 'MOVE', 'target': {'q': 1, 'r': 2}}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert len(result) == 1
        assert result[0].type == OrderType.MOVE

    def test_multiple_orders_preserved_in_order(self):
        data = [
            {'type': 'MOVE', 'target': {'q': 1, 'r': 2}},
            {'type': 'WARP', 'target': {'q': 3, 'r': 4}},
            {'type': 'BUILD', 'target': None},
        ]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert len(result) == 3
        assert result[0].type == OrderType.MOVE
        assert result[1].type == OrderType.WARP
        assert result[2].type == OrderType.BUILD

    def test_corrupt_order_skipped_with_warning(self, caplog):
        """A corrupt entry (missing 'type' key) is skipped, valid ones kept."""
        data = [
            {'type': 'MOVE', 'target': {'q': 1, 'r': 0}},
            {'INVALID_KEY': 'garbage'},  # corrupt
            {'type': 'BUILD', 'target': None},
        ]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f99")
        assert len(result) == 2
        assert result[0].type == OrderType.MOVE
        assert result[1].type == OrderType.BUILD

    def test_unknown_order_type_skipped(self):
        """An order with an unrecognized type string is skipped."""
        data = [{'type': 'NONEXISTENT_TYPE', 'target': None}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert len(result) == 0


# ---------------------------------------------------------------------------
# Target deserialization — all 7 formats
# ---------------------------------------------------------------------------

class TestDeserializeTargetHexCoord:
    """Format 1: HexCoord — {'q': x, 'r': y}."""

    def test_hex_coord_deserialized(self):
        data = [{'type': 'MOVE', 'target': {'q': 5, 'r': -3}}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == HexCoord(5, -3)

    def test_hex_coord_zero_origin(self):
        data = [{'type': 'MOVE', 'target': {'q': 0, 'r': 0}}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == HexCoord(0, 0)

    def test_hex_coord_negative_values(self):
        data = [{'type': 'WARP', 'target': {'q': -10, 'r': -20}}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == HexCoord(-10, -20)


class TestDeserializeTargetFleetRef:
    """Format 2: Fleet reference — {'type': 'fleet_ref', 'id': xxx}."""

    def test_fleet_ref_becomes_marker_dict(self):
        data = [{'type': 'MOVE_TO_FLEET', 'target': {'type': 'fleet_ref', 'id': 42}}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == {'_fleet_ref': 42}

    def test_join_fleet_ref(self):
        data = [{'type': 'JOIN_FLEET', 'target': {'type': 'fleet_ref', 'id': 99}}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == {'_fleet_ref': 99}


class TestDeserializeTargetPlanetRef:
    """Format 3: Planet reference — {'type': 'planet_ref', 'id': xxx}."""

    def test_planet_ref_becomes_marker_dict(self):
        data = [{'type': 'COLONIZE', 'target': {'type': 'planet_ref', 'id': 7}}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == {'_planet_ref': 7}

    def test_implode_planet_ref(self):
        data = [{'type': 'IMPLODE_PLANET', 'target': {'type': 'planet_ref', 'id': 15}}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == {'_planet_ref': 15}


class TestDeserializeTargetTransfer:
    """Format 4: Transfer params — {'type': 'transfer', 'value': {...}}."""

    def test_transfer_params_unwrapped(self):
        params = {"direction": "unload", "cargo_type": "minerals", "amount": 50}
        data = [{'type': 'TRANSFER', 'target': {'type': 'transfer', 'value': params}}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == params

    def test_transfer_empty_dict_value(self):
        data = [{'type': 'TRANSFER', 'target': {'type': 'transfer', 'value': {}}}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == {}


class TestDeserializeTargetWarpParams:
    """Format 5: Warp params — {'type': 'warp_params', 'value': {...}}."""

    def test_warp_params_unwrapped(self):
        params = {"destination_system": "Sol", "energy_cost": 200}
        data = [{'type': 'OPEN_WARP_POINT', 'target': {'type': 'warp_params', 'value': params}}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == params


class TestDeserializeTargetShipIdList:
    """Format 6: Ship ID list — {'type': 'ship_id_list', 'value': [...]}."""

    def test_ship_id_list_unwrapped(self):
        ids = ["s1", "s2", "s3"]
        data = [{'type': 'SELF_DESTRUCT', 'target': {'type': 'ship_id_list', 'value': ids}}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == ids

    def test_ship_id_list_empty(self):
        data = [{'type': 'SELF_DESTRUCT', 'target': {'type': 'ship_id_list', 'value': []}}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == []


class TestDeserializeTargetRaw:
    """Format 7: Raw fallback — {'type': 'raw', 'value': str}."""

    def test_raw_value_returned_as_string(self):
        data = [{'type': 'BUILD', 'target': {'type': 'raw', 'value': 'some_string'}}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == 'some_string'


class TestDeserializeTargetNone:
    """None target preserved."""

    def test_none_target(self):
        data = [{'type': 'BUILD', 'target': None}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target is None

    def test_missing_target_key_treated_as_none(self):
        """If 'target' key is absent, get() returns None."""
        data = [{'type': 'BUILD'}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target is None


class TestDeserializeTargetUnknownFormat:
    """Unknown dict format returned as-is."""

    def test_unknown_dict_returned_unchanged(self):
        weird = {'some_key': 'some_value', 'other': 123}
        data = [{'type': 'BUILD', 'target': weird}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == weird

    def test_non_dict_non_none_target_returned_as_is(self):
        """A plain scalar target is returned as-is."""
        data = [{'type': 'BUILD', 'target': 42}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == 42

    def test_string_target_returned_as_is(self):
        data = [{'type': 'BUILD', 'target': 'hello'}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].target == 'hello'


# ---------------------------------------------------------------------------
# Execution progress
# ---------------------------------------------------------------------------

class TestExecutionProgress:
    """execution_progress deserialization."""

    def test_default_progress_is_zero(self):
        data = [{'type': 'MOVE', 'target': None}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].execution_progress == 0

    def test_explicit_progress_preserved(self):
        data = [{'type': 'MOVE', 'target': None, 'execution_progress': 7}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].execution_progress == 7

    def test_zero_progress_explicit(self):
        data = [{'type': 'MOVE', 'target': None, 'execution_progress': 0}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="f1")
        assert result[0].execution_progress == 0


# ---------------------------------------------------------------------------
# Round-trip: Order.to_dict() -> OrderSerializer.deserialize_orders()
# ---------------------------------------------------------------------------

class TestRoundTrip:
    """Serialize with Order.to_dict, deserialize with OrderSerializer."""

    def test_move_hex_coord_round_trip(self):
        order = Order(OrderType.MOVE, HexCoord(3, -1))
        data = order.to_dict()
        restored = OrderSerializer.deserialize_orders([data], fleet_id="t")[0]
        assert restored.type == OrderType.MOVE
        assert restored.target == HexCoord(3, -1)

    def test_warp_hex_coord_round_trip(self):
        order = Order(OrderType.WARP, HexCoord(-2, 7))
        data = order.to_dict()
        restored = OrderSerializer.deserialize_orders([data], fleet_id="t")[0]
        assert restored.type == OrderType.WARP
        assert restored.target == HexCoord(-2, 7)

    def test_transfer_round_trip(self):
        params = {"direction": "load", "cargo_type": "fuel", "amount": 200}
        order = Order(OrderType.TRANSFER, params)
        data = order.to_dict()
        restored = OrderSerializer.deserialize_orders([data], fleet_id="t")[0]
        assert restored.target == params

    def test_self_destruct_ship_ids_round_trip(self):
        ids = ["ship_a", "ship_b"]
        order = Order(OrderType.SELF_DESTRUCT, ids)
        data = order.to_dict()
        restored = OrderSerializer.deserialize_orders([data], fleet_id="t")[0]
        assert restored.target == ids

    def test_open_warp_point_round_trip(self):
        params = {"destination": "Alpha", "cost": 500}
        order = Order(OrderType.OPEN_WARP_POINT, params)
        data = order.to_dict()
        restored = OrderSerializer.deserialize_orders([data], fleet_id="t")[0]
        assert restored.target == params

    def test_none_target_round_trip(self):
        order = Order(OrderType.BUILD, None)
        data = order.to_dict()
        restored = OrderSerializer.deserialize_orders([data], fleet_id="t")[0]
        assert restored.type == OrderType.BUILD
        assert restored.target is None

    def test_execution_progress_round_trip(self):
        order = Order(OrderType.COLONIZE, HexCoord(0, 0))
        order.execution_progress = 10
        data = order.to_dict()
        restored = OrderSerializer.deserialize_orders([data], fleet_id="t")[0]
        assert restored.execution_progress == 10

    @pytest.mark.parametrize("order_type", list(OrderType))
    def test_every_order_type_deserializes(self, order_type):
        """Every OrderType enum value can be deserialized from its name."""
        data = [{'type': order_type.name, 'target': None}]
        result = OrderSerializer.deserialize_orders(data, fleet_id="t")
        assert len(result) == 1
        assert result[0].type == order_type


# ---------------------------------------------------------------------------
# resolve_order_references
# ---------------------------------------------------------------------------

class TestResolveOrderReferences:
    """Tests for OrderSerializer.resolve_order_references."""

    @staticmethod
    def _make_mock_fleet(fleet_id, orders=None):
        fleet = MagicMock()
        fleet.id = fleet_id
        fleet.orders = orders if orders is not None else []
        fleet.fleets = []  # Not an empire
        return fleet

    @staticmethod
    def _make_mock_empire(fleets):
        empire = MagicMock()
        empire.fleets = fleets
        return empire

    def test_fleet_ref_resolved_to_actual_fleet(self):
        target_fleet = self._make_mock_fleet(42)
        order = Order(OrderType.MOVE_TO_FLEET)
        order.target = {'_fleet_ref': 42}
        source_fleet = self._make_mock_fleet(1, orders=[order])
        empire = self._make_mock_empire([source_fleet, target_fleet])

        OrderSerializer.resolve_order_references(source_fleet, galaxy=MagicMock(), empires=[empire])

        assert order.target is target_fleet

    def test_planet_ref_resolved_to_actual_planet(self):
        mock_planet = MagicMock()
        mock_galaxy = MagicMock()
        mock_galaxy.get_planet_by_id.return_value = mock_planet

        order = Order(OrderType.COLONIZE)
        order.target = {'_planet_ref': 7}
        fleet = self._make_mock_fleet(1, orders=[order])
        empire = self._make_mock_empire([fleet])

        OrderSerializer.resolve_order_references(fleet, galaxy=mock_galaxy, empires=[empire])

        assert order.target is mock_planet
        mock_galaxy.get_planet_by_id.assert_called_once_with(7)

    def test_unresolvable_fleet_ref_removes_order(self):
        order = Order(OrderType.MOVE_TO_FLEET)
        order.target = {'_fleet_ref': 999}  # No fleet with this id
        fleet = self._make_mock_fleet(1, orders=[order])
        empire = self._make_mock_empire([fleet])

        OrderSerializer.resolve_order_references(fleet, galaxy=MagicMock(), empires=[empire])

        assert len(fleet.orders) == 0

    def test_unresolvable_planet_ref_removes_order(self):
        mock_galaxy = MagicMock()
        mock_galaxy.get_planet_by_id.return_value = None

        order = Order(OrderType.COLONIZE)
        order.target = {'_planet_ref': 999}
        fleet = self._make_mock_fleet(1, orders=[order])
        empire = self._make_mock_empire([fleet])

        OrderSerializer.resolve_order_references(fleet, galaxy=mock_galaxy, empires=[empire])

        assert len(fleet.orders) == 0

    def test_non_ref_orders_left_untouched(self):
        order = Order(OrderType.MOVE, HexCoord(1, 2))
        fleet = self._make_mock_fleet(1, orders=[order])
        empire = self._make_mock_empire([fleet])

        OrderSerializer.resolve_order_references(fleet, galaxy=MagicMock(), empires=[empire])

        assert len(fleet.orders) == 1
        assert order.target == HexCoord(1, 2)

    def test_mixed_orders_only_unresolvable_removed(self):
        """Valid orders are kept; only unresolvable refs are removed."""
        target_fleet = self._make_mock_fleet(10)
        good_order = Order(OrderType.MOVE_TO_FLEET)
        good_order.target = {'_fleet_ref': 10}
        bad_order = Order(OrderType.MOVE_TO_FLEET)
        bad_order.target = {'_fleet_ref': 999}
        hex_order = Order(OrderType.MOVE, HexCoord(0, 0))

        fleet = self._make_mock_fleet(1, orders=[good_order, bad_order, hex_order])
        empire = self._make_mock_empire([fleet, target_fleet])

        OrderSerializer.resolve_order_references(fleet, galaxy=MagicMock(), empires=[empire])

        assert len(fleet.orders) == 2
        assert fleet.orders[0].target is target_fleet
        assert fleet.orders[1].target == HexCoord(0, 0)

    def test_fleet_ref_resolved_across_empires(self):
        """Fleet refs can point to fleets in other empires."""
        target_fleet = self._make_mock_fleet(50)
        order = Order(OrderType.MOVE_TO_FLEET)
        order.target = {'_fleet_ref': 50}
        source_fleet = self._make_mock_fleet(1, orders=[order])

        empire1 = self._make_mock_empire([source_fleet])
        empire2 = self._make_mock_empire([target_fleet])

        OrderSerializer.resolve_order_references(
            source_fleet, galaxy=MagicMock(), empires=[empire1, empire2]
        )

        assert order.target is target_fleet

    def test_no_orders_no_error(self):
        fleet = self._make_mock_fleet(1, orders=[])
        OrderSerializer.resolve_order_references(fleet, galaxy=MagicMock(), empires=[])
        assert len(fleet.orders) == 0
