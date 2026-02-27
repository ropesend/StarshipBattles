"""Tests for Fleet.from_dict validation.

PROJ-171: Deserialization Input Validation
"""
import pytest
from game.core.exceptions import PersistenceException
from game.strategy.data.fleet import Fleet, OrderType


def make_valid_fleet_data():
    """Create minimal valid Fleet data."""
    return {
        'id': 'fleet-001',
        'owner_id': 'empire-001',
        'location': [0, 0],
        'speed': 5.0,
        'ships': [],
        'orders': [],
        'path': [],
    }


def make_valid_ship_data(instance_id='ship-001'):
    """Create minimal valid ShipInstance data."""
    return {
        'instance_id': instance_id,
        'design_id': 'design-001',
        'name': 'USS Enterprise',
        'owner_id': 'empire-001',
    }


class TestFleetValidation:
    """Tests for Fleet.from_dict validation."""

    def test_valid_data_creates_fleet(self):
        """Valid data creates Fleet successfully."""
        data = make_valid_fleet_data()
        fleet = Fleet.from_dict(data)
        assert fleet.id == 'fleet-001'
        assert fleet.owner_id == 'empire-001'

    def test_missing_id_raises_persistence_exception(self):
        """Missing id raises PersistenceException."""
        data = make_valid_fleet_data()
        del data['id']

        with pytest.raises(PersistenceException) as exc_info:
            Fleet.from_dict(data)

        assert 'id' in str(exc_info.value)
        assert 'Fleet' in str(exc_info.value)
        assert 'missing_keys' in exc_info.value.context

    def test_missing_owner_id_raises_persistence_exception(self):
        """Missing owner_id raises PersistenceException."""
        data = make_valid_fleet_data()
        del data['owner_id']

        with pytest.raises(PersistenceException) as exc_info:
            Fleet.from_dict(data)

        assert 'owner_id' in str(exc_info.value)
        assert 'Fleet' in str(exc_info.value)

    def test_valid_fleet_with_ships_and_orders(self):
        """Fleet with valid ships and orders loads correctly."""
        data = make_valid_fleet_data()
        data['ships'] = [make_valid_ship_data()]
        data['orders'] = [{'type': 'MOVE', 'target': {'q': 1, 'r': 2}}]

        fleet = Fleet.from_dict(data)
        assert len(fleet.ships) == 1
        assert len(fleet.orders) == 1
        assert fleet.orders[0].type == OrderType.MOVE

    def test_bad_ship_skipped_fleet_loads(self):
        """Corrupt ship in list is skipped, fleet loads with remaining ships."""
        data = make_valid_fleet_data()
        data['ships'] = [
            make_valid_ship_data('ship-001'),
            {'corrupt': 'data'},  # Missing required fields
            make_valid_ship_data('ship-002'),
        ]

        fleet = Fleet.from_dict(data)
        # Bad ship skipped, 2 good ships loaded
        assert len(fleet.ships) == 2
        assert fleet.ships[0].instance_id == 'ship-001'
        assert fleet.ships[1].instance_id == 'ship-002'

    def test_bad_order_skipped_fleet_loads(self):
        """Corrupt order in list is skipped, fleet loads with remaining orders."""
        data = make_valid_fleet_data()
        data['orders'] = [
            {'type': 'MOVE', 'target': {'q': 1, 'r': 2}},
            {'type': 'INVALID_ORDER_TYPE'},  # Invalid order type
            {'type': 'COLONIZE', 'target': None},
        ]

        fleet = Fleet.from_dict(data)
        # Bad order skipped, 2 good orders loaded
        assert len(fleet.orders) == 2
        assert fleet.orders[0].type == OrderType.MOVE
        assert fleet.orders[1].type == OrderType.COLONIZE

    def test_invalid_order_type_skipped(self):
        """Invalid OrderType enum value causes order to be skipped."""
        data = make_valid_fleet_data()
        data['orders'] = [
            {'type': 'TOTALLY_FAKE_ORDER_TYPE'},
        ]

        fleet = Fleet.from_dict(data)
        # Invalid order skipped
        assert len(fleet.orders) == 0

    def test_all_order_types_valid(self):
        """All valid OrderType enum values work."""
        data = make_valid_fleet_data()
        data['orders'] = [
            {'type': 'MOVE', 'target': {'q': 1, 'r': 2}},
            {'type': 'COLONIZE', 'target': None},
            {'type': 'BUILD', 'target': None},
            {'type': 'TRANSFER', 'target': {'type': 'transfer', 'value': {'amount': 100}}},
        ]

        fleet = Fleet.from_dict(data)
        assert len(fleet.orders) == 4

    def test_fleet_with_path_loads(self):
        """Fleet with path points loads correctly."""
        data = make_valid_fleet_data()
        data['path'] = [{'q': 1, 'r': 2}, {'q': 3, 'r': 4}]

        fleet = Fleet.from_dict(data)
        assert len(fleet.path) == 2

    def test_optional_location_defaults(self):
        """Fleet without location works (optional field)."""
        data = {
            'id': 'fleet-001',
            'owner_id': 'empire-001',
        }
        fleet = Fleet.from_dict(data)
        assert fleet.location is None
