"""Tests for superweapon order types and command dataclasses.

PROJ-102 Phase 2: Order Types & Command Definitions
"""
import pytest
from game.strategy.data.fleet import OrderType, FleetOrder, Fleet
from game.strategy.engine.commands import (
    CommandType,
    IssueImplodePlanetCommand,
    IssueStellerateStarCommand,
    IssueOpenWarpPointCommand,
    IssueCloseWarpPointCommand,
    IssueCreateDysonSphereCommand,
    IssueSelfDestructCommand,
    QueueImplodePlanetMissionCommand,
    QueueStellerateStarMissionCommand,
    QueueOpenWarpPointMissionCommand,
    QueueCloseWarpPointMissionCommand,
    QueueCreateDysonSphereMissionCommand,
)
from game.core.hex_math import HexCoord


class TestSuperweaponOrderTypes:
    """Test that all 6 superweapon OrderType enum values exist."""

    def test_implode_planet_order_type_exists(self):
        """IMPLODE_PLANET OrderType is defined."""
        assert hasattr(OrderType, 'IMPLODE_PLANET')
        assert isinstance(OrderType.IMPLODE_PLANET, OrderType)

    def test_stellerate_star_order_type_exists(self):
        """STELLERATE_STAR OrderType is defined."""
        assert hasattr(OrderType, 'STELLERATE_STAR')
        assert isinstance(OrderType.STELLERATE_STAR, OrderType)

    def test_open_warp_point_order_type_exists(self):
        """OPEN_WARP_POINT OrderType is defined."""
        assert hasattr(OrderType, 'OPEN_WARP_POINT')
        assert isinstance(OrderType.OPEN_WARP_POINT, OrderType)

    def test_close_warp_point_order_type_exists(self):
        """CLOSE_WARP_POINT OrderType is defined."""
        assert hasattr(OrderType, 'CLOSE_WARP_POINT')
        assert isinstance(OrderType.CLOSE_WARP_POINT, OrderType)

    def test_create_dyson_sphere_order_type_exists(self):
        """CREATE_DYSON_SPHERE OrderType is defined."""
        assert hasattr(OrderType, 'CREATE_DYSON_SPHERE')
        assert isinstance(OrderType.CREATE_DYSON_SPHERE, OrderType)

    def test_self_destruct_order_type_exists(self):
        """SELF_DESTRUCT OrderType is defined."""
        assert hasattr(OrderType, 'SELF_DESTRUCT')
        assert isinstance(OrderType.SELF_DESTRUCT, OrderType)


class TestFleetOrderSerialization:
    """Test FleetOrder to_dict/from_dict for superweapon order types."""

    def test_implode_planet_order_round_trip(self):
        """IMPLODE_PLANET order serializes with planet_ref target."""
        from unittest.mock import MagicMock
        from game.strategy.data.planet import Planet

        # Use MagicMock with spec=Planet to pass isinstance check
        planet = MagicMock(spec=Planet)
        planet.id = 42
        order = FleetOrder(OrderType.IMPLODE_PLANET, planet)
        data = order.to_dict()

        assert data['type'] == 'IMPLODE_PLANET'
        assert data['target']['type'] == 'planet_ref'
        assert data['target']['id'] == 42

    def test_self_destruct_order_round_trip(self):
        """SELF_DESTRUCT order serializes with ship_id_list target."""
        ship_ids = [101, 102, 103]
        order = FleetOrder(OrderType.SELF_DESTRUCT, ship_ids)
        data = order.to_dict()

        assert data['type'] == 'SELF_DESTRUCT'
        assert data['target']['type'] == 'ship_id_list'
        assert data['target']['value'] == [101, 102, 103]

    def test_open_warp_point_order_round_trip(self):
        """OPEN_WARP_POINT order serializes with warp_params target."""
        params = {'target_hex': (5, 3), 'target_system_name': 'Alpha Centauri'}
        order = FleetOrder(OrderType.OPEN_WARP_POINT, params)
        data = order.to_dict()

        assert data['type'] == 'OPEN_WARP_POINT'
        assert data['target']['type'] == 'warp_params'
        assert data['target']['value'] == params

    def test_stellerate_star_order_round_trip_no_target(self):
        """STELLERATE_STAR order serializes with None target."""
        order = FleetOrder(OrderType.STELLERATE_STAR, None)
        data = order.to_dict()

        assert data['type'] == 'STELLERATE_STAR'
        assert data['target'] is None

    def test_create_dyson_sphere_order_round_trip_no_target(self):
        """CREATE_DYSON_SPHERE order serializes with None target."""
        order = FleetOrder(OrderType.CREATE_DYSON_SPHERE, None)
        data = order.to_dict()

        assert data['type'] == 'CREATE_DYSON_SPHERE'
        assert data['target'] is None

    def test_close_warp_point_order_round_trip(self):
        """CLOSE_WARP_POINT order serializes with warp_point_ref target."""
        order = FleetOrder(OrderType.CLOSE_WARP_POINT, "warp_point_dest_42")
        data = order.to_dict()

        assert data['type'] == 'CLOSE_WARP_POINT'
        # String target uses raw format
        assert data['target']['type'] == 'raw'
        assert data['target']['value'] == "warp_point_dest_42"


class TestFleetFromDictDeserialization:
    """Test Fleet.from_dict correctly deserializes superweapon order types."""

    def test_deserialize_implode_planet_with_planet_ref(self):
        """Planet reference is restored as dict with _planet_ref key."""
        fleet_data = {
            'id': 1,
            'owner_id': 0,
            'location': {'q': 0, 'r': 0},
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'IMPLODE_PLANET', 'target': {'type': 'planet_ref', 'id': 42}}
            ],
            'path': [],
            'construction_queue': [],
        }
        fleet = Fleet.from_dict(fleet_data)

        assert len(fleet.orders) == 1
        assert fleet.orders[0].type == OrderType.IMPLODE_PLANET
        assert fleet.orders[0].target == {'_planet_ref': 42}

    def test_deserialize_self_destruct_with_ship_id_list(self):
        """Ship ID list is restored as list."""
        fleet_data = {
            'id': 1,
            'owner_id': 0,
            'location': {'q': 0, 'r': 0},
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'SELF_DESTRUCT', 'target': {'type': 'ship_id_list', 'value': [101, 102, 103]}}
            ],
            'path': [],
            'construction_queue': [],
        }
        fleet = Fleet.from_dict(fleet_data)

        assert len(fleet.orders) == 1
        assert fleet.orders[0].type == OrderType.SELF_DESTRUCT
        assert fleet.orders[0].target == [101, 102, 103]

    def test_deserialize_open_warp_point_with_warp_params(self):
        """Warp params dict is restored."""
        warp_params = {'target_hex': [5, 3], 'target_system_name': 'Alpha Centauri'}
        fleet_data = {
            'id': 1,
            'owner_id': 0,
            'location': {'q': 0, 'r': 0},
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'OPEN_WARP_POINT', 'target': {'type': 'warp_params', 'value': warp_params}}
            ],
            'path': [],
            'construction_queue': [],
        }
        fleet = Fleet.from_dict(fleet_data)

        assert len(fleet.orders) == 1
        assert fleet.orders[0].type == OrderType.OPEN_WARP_POINT
        assert fleet.orders[0].target == warp_params


class TestDirectCommandDataclasses:
    """Test the 6 direct (immediate) command dataclasses."""

    def test_issue_implode_planet_command(self):
        """IssueImplodePlanetCommand has correct structure."""
        cmd = IssueImplodePlanetCommand(fleet_id=1, planet_id=42)
        assert cmd.name == 'IssueImplodePlanetCommand'
        assert cmd.type == CommandType.ISSUE_ORDER
        assert cmd.fleet_id == 1
        assert cmd.planet_id == 42

    def test_issue_stellerate_star_command(self):
        """IssueStellerateStarCommand has correct structure."""
        cmd = IssueStellerateStarCommand(fleet_id=1)
        assert cmd.name == 'IssueStellerateStarCommand'
        assert cmd.type == CommandType.ISSUE_ORDER
        assert cmd.fleet_id == 1

    def test_issue_open_warp_point_command(self):
        """IssueOpenWarpPointCommand has correct structure."""
        target_hex = HexCoord(5, 3)
        cmd = IssueOpenWarpPointCommand(fleet_id=1, target_hex=target_hex, target_system_name='Alpha')
        assert cmd.name == 'IssueOpenWarpPointCommand'
        assert cmd.type == CommandType.ISSUE_ORDER
        assert cmd.fleet_id == 1
        assert cmd.target_hex == target_hex
        assert cmd.target_system_name == 'Alpha'

    def test_issue_close_warp_point_command(self):
        """IssueCloseWarpPointCommand has correct structure."""
        cmd = IssueCloseWarpPointCommand(fleet_id=1, warp_point_destination_id='dest_42')
        assert cmd.name == 'IssueCloseWarpPointCommand'
        assert cmd.type == CommandType.ISSUE_ORDER
        assert cmd.fleet_id == 1
        assert cmd.warp_point_destination_id == 'dest_42'

    def test_issue_create_dyson_sphere_command(self):
        """IssueCreateDysonSphereCommand has correct structure."""
        cmd = IssueCreateDysonSphereCommand(fleet_id=1)
        assert cmd.name == 'IssueCreateDysonSphereCommand'
        assert cmd.type == CommandType.ISSUE_ORDER
        assert cmd.fleet_id == 1

    def test_issue_self_destruct_command(self):
        """IssueSelfDestructCommand has correct structure."""
        ship_ids = [101, 102, 103]
        cmd = IssueSelfDestructCommand(fleet_id=1, ship_ids=ship_ids)
        assert cmd.name == 'IssueSelfDestructCommand'
        assert cmd.type == CommandType.ISSUE_ORDER
        assert cmd.fleet_id == 1
        assert cmd.ship_ids == ship_ids


class TestMissionCommandDataclasses:
    """Test the 5 mission (queued movement + action) command dataclasses."""

    def test_queue_implode_planet_mission_command(self):
        """QueueImplodePlanetMissionCommand has correct structure."""
        target_hex = HexCoord(5, 3)
        cmd = QueueImplodePlanetMissionCommand(fleet_id=1, target_hex=target_hex, planet_id=42)
        assert cmd.name == 'QueueImplodePlanetMissionCommand'
        assert cmd.type == CommandType.ISSUE_ORDER
        assert cmd.fleet_id == 1
        assert cmd.target_hex == target_hex
        assert cmd.planet_id == 42

    def test_queue_stellerate_star_mission_command(self):
        """QueueStellerateStarMissionCommand has correct structure."""
        target_hex = HexCoord(5, 3)
        cmd = QueueStellerateStarMissionCommand(fleet_id=1, target_hex=target_hex)
        assert cmd.name == 'QueueStellerateStarMissionCommand'
        assert cmd.type == CommandType.ISSUE_ORDER
        assert cmd.fleet_id == 1
        assert cmd.target_hex == target_hex

    def test_queue_open_warp_point_mission_command(self):
        """QueueOpenWarpPointMissionCommand has correct structure."""
        target_hex = HexCoord(5, 3)
        cmd = QueueOpenWarpPointMissionCommand(fleet_id=1, target_hex=target_hex, target_system_name='Alpha')
        assert cmd.name == 'QueueOpenWarpPointMissionCommand'
        assert cmd.type == CommandType.ISSUE_ORDER
        assert cmd.fleet_id == 1
        assert cmd.target_hex == target_hex
        assert cmd.target_system_name == 'Alpha'

    def test_queue_close_warp_point_mission_command(self):
        """QueueCloseWarpPointMissionCommand has correct structure."""
        target_hex = HexCoord(5, 3)
        cmd = QueueCloseWarpPointMissionCommand(fleet_id=1, target_hex=target_hex, warp_point_destination_id='dest_42')
        assert cmd.name == 'QueueCloseWarpPointMissionCommand'
        assert cmd.type == CommandType.ISSUE_ORDER
        assert cmd.fleet_id == 1
        assert cmd.target_hex == target_hex
        assert cmd.warp_point_destination_id == 'dest_42'

    def test_queue_create_dyson_sphere_mission_command(self):
        """QueueCreateDysonSphereMissionCommand has correct structure."""
        target_hex = HexCoord(5, 3)
        cmd = QueueCreateDysonSphereMissionCommand(fleet_id=1, target_hex=target_hex)
        assert cmd.name == 'QueueCreateDysonSphereMissionCommand'
        assert cmd.type == CommandType.ISSUE_ORDER
        assert cmd.fleet_id == 1
        assert cmd.target_hex == target_hex
