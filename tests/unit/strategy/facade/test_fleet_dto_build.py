"""Tests for Fleet DTO BUILD-related fields (PROJ-67 Phase 2)."""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord
from game.strategy.facade.dto.fleet_dto import FleetInfo


class TestFleetInfoBuildFields:
    """Test cases for FleetInfo BUILD-related DTO fields."""

    @pytest.fixture
    def make_ship_with_yard(self):
        """Factory for creating ship with fleet_space_yard component."""
        def _make(name="Yard Ship"):
            mock = MagicMock()
            mock.name = name
            mock.instance_id = f"inst_{name}"
            mock.design_id = "construction_ship"
            mock.is_combat_capable.return_value = True
            mock.get_hp_percentage.return_value = 1.0
            # For can_use_warp() via ShipStatsCalculator
            mock.get_calculated_stats.return_value = {'mass': 5000}
            mock.design_data = {
                'name': name,
                'ship_class': 'Support',
                'vehicle_type': 'Ship',
                'layers': {
                    'core': [{'id': 'fleet_space_yard', 'name': 'Fleet Space Yard'}]
                }
            }
            return mock
        return _make

    @pytest.fixture
    def make_regular_ship(self):
        """Factory for creating regular ship without yard."""
        def _make(name="Scout"):
            mock = MagicMock()
            mock.name = name
            mock.instance_id = f"inst_{name}"
            mock.design_id = "scout"
            mock.is_combat_capable.return_value = True
            mock.get_hp_percentage.return_value = 1.0
            # For can_use_warp() via ShipStatsCalculator
            mock.get_calculated_stats.return_value = {'mass': 2000}
            mock.design_data = {
                'name': name,
                'ship_class': 'Scout',
                'vehicle_type': 'Ship',
                'layers': {'core': [{'id': 'engine'}]}
            }
            return mock
        return _make

    def test_fleet_info_has_is_building_field(self):
        """Test FleetInfo has is_building field."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        info = FleetInfo.from_fleet(fleet)

        assert hasattr(info, 'is_building')

    def test_fleet_info_is_building_true_when_build_order(self, make_ship_with_yard):
        """Test is_building is True when fleet has BUILD order."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_ship_with_yard())
        fleet.add_order(FleetOrder(OrderType.BUILD))
        fleet.construction_queue = [{'design_id': 'frigate', 'turns_remaining': 5}]

        info = FleetInfo.from_fleet(fleet)

        assert info.is_building is True

    def test_fleet_info_is_building_false_when_no_order(self, make_regular_ship):
        """Test is_building is False when no orders."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_regular_ship())

        info = FleetInfo.from_fleet(fleet)

        assert info.is_building is False

    def test_fleet_info_is_building_false_when_move_order(self, make_regular_ship):
        """Test is_building is False when MOVE order."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_regular_ship())
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(5, 5)))

        info = FleetInfo.from_fleet(fleet)

        assert info.is_building is False

    def test_fleet_info_has_space_shipyard_field(self):
        """Test FleetInfo has has_space_shipyard field."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        info = FleetInfo.from_fleet(fleet)

        assert hasattr(info, 'has_space_shipyard')

    def test_fleet_info_has_space_shipyard_true(self, make_ship_with_yard):
        """Test has_space_shipyard is True when fleet has yard ship."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_ship_with_yard())

        info = FleetInfo.from_fleet(fleet)

        assert info.has_space_shipyard is True

    def test_fleet_info_has_space_shipyard_false(self, make_regular_ship):
        """Test has_space_shipyard is False when no yard ship."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_regular_ship())

        info = FleetInfo.from_fleet(fleet)

        assert info.has_space_shipyard is False

    def test_fleet_info_has_construction_queue_size_field(self):
        """Test FleetInfo has construction_queue_size field."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        info = FleetInfo.from_fleet(fleet)

        assert hasattr(info, 'construction_queue_size')

    def test_fleet_info_construction_queue_size_correct(self, make_ship_with_yard):
        """Test construction_queue_size reflects actual queue size."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_ship_with_yard())
        fleet.construction_queue = [
            {'design_id': 'frigate', 'turns_remaining': 5},
            {'design_id': 'destroyer', 'turns_remaining': 8},
            {'design_id': 'cruiser', 'turns_remaining': 12},
        ]

        info = FleetInfo.from_fleet(fleet)

        assert info.construction_queue_size == 3

    def test_fleet_info_construction_queue_size_zero_when_empty(self, make_regular_ship):
        """Test construction_queue_size is 0 when queue is empty."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_regular_ship())

        info = FleetInfo.from_fleet(fleet)

        assert info.construction_queue_size == 0

    def test_fleet_info_is_immutable(self, make_ship_with_yard):
        """Test FleetInfo DTO is frozen (immutable)."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_ship_with_yard())
        fleet.add_order(FleetOrder(OrderType.BUILD))
        fleet.construction_queue = [{'design_id': 'frigate', 'turns_remaining': 5}]

        info = FleetInfo.from_fleet(fleet)

        with pytest.raises(Exception):  # FrozenInstanceError
            info.is_building = False
