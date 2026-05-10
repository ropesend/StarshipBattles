"""Round-trip tests for Fleet serialization (PROJ-223 Phase 3)."""

import json
import pytest

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.core.hex_math import HexCoord
from tests.fixtures.strategy_entities import create_test_fleet, create_test_fleet_order
from tests.integration.save_load.conftest import assert_round_trip_fidelity, assert_field_preserved


class TestFleetRoundTrip:
    """Fleet compound round-trip serialization tests."""

    def test_core_fields(self):
        f = create_test_fleet()
        d = f.to_dict()
        assert 'id' in d
        assert 'owner_id' in d
        assert 'location' in d
        assert 'speed' in d

    def test_round_trip_core_fields(self):
        f = create_test_fleet(fleet_id=42, owner_id=1, speed=12.5)
        d = f.to_dict()
        restored = Fleet.from_dict(d)
        assert restored.id == 42
        assert restored.owner_id == 1
        assert restored.speed == 12.5

    def test_ships_nested_round_trip(self):
        f = create_test_fleet(num_ships=3)
        d = f.to_dict()
        restored = Fleet.from_dict(d)
        assert len(restored.ships) == 3
        for orig, rest in zip(f.ships, restored.ships):
            assert rest.instance_id == orig.instance_id
            assert rest.name == orig.name
            assert rest.design_data == orig.design_data

    def test_orders_nested_round_trip(self):
        f = create_test_fleet(num_ships=1)
        f.orders = [
            create_test_fleet_order(OrderType.MOVE, HexCoord(5, -3)),
            create_test_fleet_order(OrderType.MOVE, HexCoord(10, 0)),
        ]
        d = f.to_dict()
        restored = Fleet.from_dict(d)
        assert len(restored.orders) == 2
        assert restored.orders[0].type == OrderType.MOVE
        assert restored.orders[0].target == HexCoord(5, -3)

    def test_path_list_round_trip(self):
        f = create_test_fleet()
        f.path = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, -1)]
        d = f.to_dict()
        restored = Fleet.from_dict(d)
        assert len(restored.path) == 3
        assert restored.path[0] == HexCoord(1, 0)
        assert restored.path[2] == HexCoord(3, -1)

    def test_construction_queue_round_trip(self):
        f = create_test_fleet()
        f.construction_queue = [{"design_id": "escort", "progress": 3, "cost": 50}]
        d = f.to_dict()
        restored = Fleet.from_dict(d)
        assert len(restored.construction_queue) == 1
        assert restored.construction_queue[0]["design_id"] == "escort"

    def test_registries_passed_to_ships(self, fresh_registries):
        f = create_test_fleet(num_ships=2)
        d = f.to_dict()
        restored = Fleet.from_dict(d, registries=fresh_registries)
        for ship in restored.ships:
            assert ship._registries is not None

    def test_fleet_with_multiple_order_types(self):
        f = create_test_fleet(num_ships=1)
        f.orders = [
            create_test_fleet_order(OrderType.MOVE, HexCoord(5, 0)),
            create_test_fleet_order(OrderType.WARP, HexCoord(10, -5)),
        ]
        f.orders[1].execution_progress = 3
        d = f.to_dict()
        restored = Fleet.from_dict(d)
        assert len(restored.orders) == 2
        assert restored.orders[1].execution_progress == 3

    def test_location_hex_coord(self):
        f = create_test_fleet(location=HexCoord(-7, 12))
        d = f.to_dict()
        restored = Fleet.from_dict(d)
        assert restored.location == HexCoord(-7, 12)
