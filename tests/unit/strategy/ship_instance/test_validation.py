"""Tests for ShipInstance.from_dict validation.

PROJ-171: Deserialization Input Validation
"""
import pytest
from game.core.exceptions import PersistenceException
from game.strategy.data.ship_instance import ShipInstance


def make_valid_ship_data() -> dict:
    """Create minimal valid ShipInstance data."""
    return {
        'instance_id': 'ship-001',
        'design_id': 'design-001',
        'name': 'USS Enterprise',
        'owner_id': 'empire-001',
        'components': {},
    }


class TestShipInstanceValidation:
    """Tests for ShipInstance.from_dict validation."""

    def test_valid_data_creates_ship_instance(self):
        """Valid data creates ShipInstance successfully."""
        data = make_valid_ship_data()
        ship = ShipInstance.from_dict(data)
        assert ship.instance_id == 'ship-001'
        assert ship.design_id == 'design-001'
        assert ship.name == 'USS Enterprise'
        assert ship.owner_id == 'empire-001'

    def test_missing_instance_id_raises_persistence_exception(self):
        """Missing instance_id raises PersistenceException."""
        data = make_valid_ship_data()
        del data['instance_id']

        with pytest.raises(PersistenceException) as exc_info:
            ShipInstance.from_dict(data)

        assert 'instance_id' in str(exc_info.value)
        assert 'ShipInstance' in str(exc_info.value)
        assert 'missing_keys' in exc_info.value.context

    def test_missing_design_id_raises_persistence_exception(self):
        """Missing design_id raises PersistenceException."""
        data = make_valid_ship_data()
        del data['design_id']

        with pytest.raises(PersistenceException) as exc_info:
            ShipInstance.from_dict(data)

        assert 'design_id' in str(exc_info.value)
        assert 'ShipInstance' in str(exc_info.value)

    def test_missing_name_raises_persistence_exception(self):
        """Missing name raises PersistenceException."""
        data = make_valid_ship_data()
        del data['name']

        with pytest.raises(PersistenceException) as exc_info:
            ShipInstance.from_dict(data)

        assert 'name' in str(exc_info.value)
        assert 'ShipInstance' in str(exc_info.value)

    def test_missing_owner_id_raises_persistence_exception(self):
        """Missing owner_id raises PersistenceException."""
        data = make_valid_ship_data()
        del data['owner_id']

        with pytest.raises(PersistenceException) as exc_info:
            ShipInstance.from_dict(data)

        assert 'owner_id' in str(exc_info.value)
        assert 'ShipInstance' in str(exc_info.value)

    def test_missing_multiple_keys_lists_all(self):
        """Missing multiple keys lists all in exception."""
        data = make_valid_ship_data()
        del data['instance_id']
        del data['name']

        with pytest.raises(PersistenceException) as exc_info:
            ShipInstance.from_dict(data)

        # Both should be mentioned
        context = exc_info.value.context
        assert 'instance_id' in context['missing_keys']
        assert 'name' in context['missing_keys']

    def test_optional_fields_have_defaults(self):
        """Optional fields work with defaults when not provided."""
        data = make_valid_ship_data()
        ship = ShipInstance.from_dict(data)

        # Verify defaults are applied
        assert ship.is_alive is True
        assert ship.is_derelict is False
        assert ship.experience == 0
        assert ship.kills == 0
        assert ship.battles_survived == 0
        assert ship.components == {}
        assert ship.consumable_levels == {}

    @pytest.mark.parametrize("field_name", [
        'current_hp',
        'experience',
        'kills',
        'battles_survived',
    ])
    def test_negative_value_raises_persistence_exception(self, field_name):
        """Negative values for numeric fields raise PersistenceException."""
        data = make_valid_ship_data()
        data[field_name] = -1

        with pytest.raises(PersistenceException) as exc_info:
            ShipInstance.from_dict(data)

        assert field_name in str(exc_info.value)
        assert 'ShipInstance' in str(exc_info.value)
        assert 'non-negative' in str(exc_info.value).lower() or 'negative' in str(exc_info.value).lower()

    @pytest.mark.parametrize("field_name", [
        'current_hp',
        'experience',
        'kills',
        'battles_survived',
    ])
    def test_zero_value_accepted(self, field_name):
        """Zero values for numeric fields are accepted (boundary check)."""
        data = make_valid_ship_data()
        data[field_name] = 0

        ship = ShipInstance.from_dict(data)

        assert getattr(ship, field_name) == 0
