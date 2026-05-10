"""Tests for battle state deserialization validation.

PROJ-171: Phase 5 - Simulation state validation for ComponentState and ShipState.
"""

import pytest
from game.simulation.battle_state import ComponentState, ShipState
from game.core.exceptions import PersistenceException


# ============================================================================
# ComponentState Validation Tests
# ============================================================================

class TestComponentStateValidation:
    """Tests for ComponentState.from_dict() validation."""

    @pytest.fixture
    def valid_component_data(self):
        """Minimal valid ComponentState data."""
        return {
            'component_id': 'laser_mk1',
            'current_hp': 10,
            'max_hp': 15,
            'is_active': True,
            'layer': 'WEAPONS',
            'modifiers': []
        }

    def test_valid_data_creates_component_state(self, valid_component_data):
        """Valid data should create ComponentState successfully."""
        state = ComponentState.from_dict(valid_component_data)
        assert state.component_id == 'laser_mk1'
        assert state.current_hp == 10
        assert state.max_hp == 15
        assert state.is_active is True
        assert state.layer == 'WEAPONS'

    @pytest.mark.parametrize('field', [
        'component_id',
        'current_hp',
        'max_hp',
        'layer',
    ])
    def test_missing_required_field_raises_persistence_exception(
        self, valid_component_data, field,
    ):
        """Each required ComponentState field, when absent, raises a
        PersistenceException naming the field. Parametrized in PROJ-322
        Task 1.7 (S08-CAT4-002)."""
        del valid_component_data[field]
        with pytest.raises(PersistenceException) as exc_info:
            ComponentState.from_dict(valid_component_data)
        assert field in str(exc_info.value)
        if field == 'component_id':
            # Original test asserted on the exception's class context label.
            assert 'ComponentState' in str(exc_info.value)

    def test_negative_current_hp_raises_persistence_exception(self, valid_component_data):
        """Negative current_hp should raise PersistenceException."""
        valid_component_data['current_hp'] = -1
        with pytest.raises(PersistenceException) as exc_info:
            ComponentState.from_dict(valid_component_data)
        assert 'current_hp' in str(exc_info.value)
        assert 'non-negative' in str(exc_info.value)

    def test_zero_max_hp_raises_persistence_exception(self, valid_component_data):
        """Zero max_hp should raise PersistenceException (max_hp must be positive)."""
        valid_component_data['max_hp'] = 0
        with pytest.raises(PersistenceException) as exc_info:
            ComponentState.from_dict(valid_component_data)
        assert 'max_hp' in str(exc_info.value)
        assert 'positive' in str(exc_info.value)

    def test_negative_max_hp_raises_persistence_exception(self, valid_component_data):
        """Negative max_hp should raise PersistenceException."""
        valid_component_data['max_hp'] = -5
        with pytest.raises(PersistenceException) as exc_info:
            ComponentState.from_dict(valid_component_data)
        assert 'max_hp' in str(exc_info.value)

    def test_zero_current_hp_is_valid(self, valid_component_data):
        """Zero current_hp is valid (component can be destroyed)."""
        valid_component_data['current_hp'] = 0
        state = ComponentState.from_dict(valid_component_data)
        assert state.current_hp == 0

    def test_modifiers_default_to_empty_list(self, valid_component_data):
        """Missing modifiers should default to empty list."""
        del valid_component_data['modifiers']
        state = ComponentState.from_dict(valid_component_data)
        assert state.modifiers == []


# ============================================================================
# ShipState Validation Tests
# ============================================================================

class TestShipStateValidation:
    """Tests for ShipState.from_dict() validation."""

    @pytest.fixture
    def valid_ship_data(self):
        """Minimal valid ShipState data."""
        return {
            'ship_id': 'ship_001',
            'name': 'USS Enterprise',
            'ship_class': 'Cruiser',
            'theme_id': 'federation',
            'team_id': 0,
            'color': [255, 0, 0],
            'movement_policy': 'brawl_close',
            'position': [100.0, 200.0],
            'velocity': [1.0, 0.0],
            'angle': 45.0,
            'current_hp': 100,
            'max_hp': 100,
            'current_shields': 50.0,
            'max_shields': 50.0,
            'components': {},
            'resource_levels': {},
            'resource_max': {},
            'is_alive': True,
            'is_derelict': False,
            'retreat_status': None,
            'current_target_id': None
        }

    def test_valid_data_creates_ship_state(self, valid_ship_data):
        """Valid data should create ShipState successfully."""
        state = ShipState.from_dict(valid_ship_data)
        assert state.ship_id == 'ship_001'
        assert state.name == 'USS Enterprise'
        assert state.position == (100.0, 200.0)

    def test_missing_ship_id_raises_persistence_exception(self, valid_ship_data):
        """Missing ship_id should raise PersistenceException."""
        del valid_ship_data['ship_id']
        with pytest.raises(PersistenceException) as exc_info:
            ShipState.from_dict(valid_ship_data)
        assert 'ship_id' in str(exc_info.value)
        assert 'ShipState' in str(exc_info.value)

    def test_missing_name_raises_persistence_exception(self, valid_ship_data):
        """Missing name should raise PersistenceException."""
        del valid_ship_data['name']
        with pytest.raises(PersistenceException) as exc_info:
            ShipState.from_dict(valid_ship_data)
        assert 'name' in str(exc_info.value)

    def test_missing_position_raises_persistence_exception(self, valid_ship_data):
        """Missing position should raise PersistenceException."""
        del valid_ship_data['position']
        with pytest.raises(PersistenceException) as exc_info:
            ShipState.from_dict(valid_ship_data)
        assert 'position' in str(exc_info.value)

    def test_invalid_color_not_list_raises_persistence_exception(self, valid_ship_data):
        """Color that is not a list/tuple should raise PersistenceException."""
        valid_ship_data['color'] = "red"  # Not a list/tuple
        with pytest.raises(PersistenceException) as exc_info:
            ShipState.from_dict(valid_ship_data)
        assert 'color' in str(exc_info.value)

    def test_invalid_color_too_short_raises_persistence_exception(self, valid_ship_data):
        """Color with fewer than 3 elements should raise PersistenceException."""
        valid_ship_data['color'] = [255, 0]  # Only 2 elements
        with pytest.raises(PersistenceException) as exc_info:
            ShipState.from_dict(valid_ship_data)
        assert 'color' in str(exc_info.value)

    def test_invalid_position_not_list_raises_persistence_exception(self, valid_ship_data):
        """Position that is not a list/tuple should raise PersistenceException."""
        valid_ship_data['position'] = "center"  # Not a list/tuple
        with pytest.raises(PersistenceException) as exc_info:
            ShipState.from_dict(valid_ship_data)
        assert 'position' in str(exc_info.value)

    def test_invalid_position_too_short_raises_persistence_exception(self, valid_ship_data):
        """Position with fewer than 2 elements should raise PersistenceException."""
        valid_ship_data['position'] = [100.0]  # Only 1 element
        with pytest.raises(PersistenceException) as exc_info:
            ShipState.from_dict(valid_ship_data)
        assert 'position' in str(exc_info.value)

    def test_invalid_velocity_not_list_raises_persistence_exception(self, valid_ship_data):
        """Velocity that is not a list/tuple should raise PersistenceException."""
        valid_ship_data['velocity'] = 5.0  # Scalar, not a list/tuple
        with pytest.raises(PersistenceException) as exc_info:
            ShipState.from_dict(valid_ship_data)
        assert 'velocity' in str(exc_info.value)

    def test_bad_component_in_layer_is_skipped(self, valid_ship_data, caplog):
        """Bad component data should be skipped with warning, not crash."""
        valid_ship_data['components'] = {
            'WEAPONS': [
                {'component_id': 'good_laser', 'current_hp': 10, 'max_hp': 15, 'is_active': True, 'layer': 'WEAPONS'},
                {'bad_data': 'missing_required_keys'},  # Bad component
                {'component_id': 'good_missile', 'current_hp': 5, 'max_hp': 10, 'is_active': True, 'layer': 'WEAPONS'}
            ]
        }
        state = ShipState.from_dict(valid_ship_data)
        # Should load the two good components, skip the bad one
        assert len(state.components['WEAPONS']) == 2
        assert state.components['WEAPONS'][0].component_id == 'good_laser'
        assert state.components['WEAPONS'][1].component_id == 'good_missile'
        # Should have logged a warning
        assert any('component' in record.message.lower() for record in caplog.records)

    def test_color_as_tuple_works(self, valid_ship_data):
        """Color provided as tuple should work (in-memory case)."""
        valid_ship_data['color'] = (128, 64, 32)
        state = ShipState.from_dict(valid_ship_data)
        assert state.color == (128, 64, 32)

    def test_optional_fields_have_defaults(self, valid_ship_data):
        """Optional fields should have sensible defaults when missing."""
        # Remove optional fields
        del valid_ship_data['resource_levels']
        del valid_ship_data['resource_max']
        del valid_ship_data['is_alive']
        del valid_ship_data['is_derelict']
        del valid_ship_data['retreat_status']
        del valid_ship_data['current_target_id']

        state = ShipState.from_dict(valid_ship_data)
        assert state.resource_levels == {}
        assert state.resource_max == {}
        assert state.is_alive is True
        assert state.is_derelict is False
        assert state.retreat_status is None
        assert state.current_target_id is None
