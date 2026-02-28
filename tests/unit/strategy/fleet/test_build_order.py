"""Tests for Fleet BUILD order functionality (PROJ-67 Phase 2)."""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord


class TestOrderTypeBuild:
    """Test cases for OrderType.BUILD enum."""

    def test_build_order_type_exists(self):
        """Test BUILD is a valid OrderType."""
        assert hasattr(OrderType, 'BUILD')
        assert OrderType.BUILD is not None

    def test_build_order_creates_successfully(self):
        """Test FleetOrder with BUILD type creates successfully."""
        order = FleetOrder(OrderType.BUILD)
        assert order.type == OrderType.BUILD
        assert order.target is None

    def test_build_order_serializes_correctly(self):
        """Test BUILD order serializes without target."""
        order = FleetOrder(OrderType.BUILD)
        d = order.to_dict()

        assert d['type'] == 'BUILD'
        assert d['target'] is None

    def test_build_order_deserializes_correctly(self):
        """Test BUILD order deserializes from save data."""
        data = {
            'id': 'f1',
            'owner_id': 0,
            'location': [5, 3],
            'speed': 5.0,
            'ships': [],
            'orders': [{'type': 'BUILD', 'target': None}],
            'path': [],
            'construction_queue': [{'design_id': 'frigate', 'turns_remaining': 3}],
        }

        fleet = Fleet.from_dict(data)

        assert len(fleet.orders) == 1
        assert fleet.orders[0].type == OrderType.BUILD
        assert fleet.orders[0].target is None

    def test_build_order_roundtrip(self):
        """Test BUILD order survives serialization roundtrip."""
        fleet = Fleet("f1", 0, HexCoord(5, 3))
        fleet.add_order(FleetOrder(OrderType.BUILD))
        fleet.construction_queue = [{'design_id': 'destroyer', 'turns_remaining': 5}]

        d = fleet.to_dict()
        d['location'] = [5, 3]  # Fix HexCoord gap
        restored = Fleet.from_dict(d)

        assert len(restored.orders) == 1
        assert restored.orders[0].type == OrderType.BUILD
        assert len(restored.construction_queue) == 1


class TestFleetIsBuilding:
    """Test cases for Fleet.is_building property."""

    def test_is_building_true_when_build_order_active(self):
        """Test is_building returns True when BUILD is current order."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.add_order(FleetOrder(OrderType.BUILD))

        assert fleet.is_building is True

    def test_is_building_false_when_no_orders(self):
        """Test is_building returns False when no orders."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        assert fleet.is_building is False

    def test_is_building_false_when_move_order(self):
        """Test is_building returns False when MOVE is current order."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(5, 5)))

        assert fleet.is_building is False

    def test_is_building_false_when_colonize_order(self):
        """Test is_building returns False when COLONIZE is current order."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        mock_planet = MagicMock()
        fleet.add_order(FleetOrder(OrderType.COLONIZE, mock_planet))

        assert fleet.is_building is False

    def test_is_building_checks_only_current_order(self):
        """Test is_building only checks current (first) order."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(5, 5)))  # Current
        fleet.add_order(FleetOrder(OrderType.BUILD))  # Queued

        assert fleet.is_building is False  # MOVE is current, not BUILD
