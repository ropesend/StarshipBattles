"""Tests for ShipInstanceSerializer - extracted serialization logic."""

import pytest
from unittest.mock import MagicMock

from game.core.exceptions import PersistenceException
from game.core.component_state import ComponentState, component_state_key
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer


@pytest.fixture
def full_ship():
    """ShipInstance with all fields populated."""
    ship = ShipInstance(
        instance_id='test-id-123',
        design_id='TestDesign',
        name='Test Ship',
        owner_id=1,
        design_data={'name': 'TestDesign', 'layers': {}},
        current_hp=80,
        components={
            component_state_key('comp_1', 0): ComponentState(
                component_id='comp_1', instance_index=0, current_hp=50.0,
            ),
        },
        _consumable_levels={'fuel': 100.0, 'energy': 50.0},
        component_toggles={'comp_2': False},
        _cargo_contents={'passengers': 10},
        is_alive=True,
        is_derelict=False,
        experience=5,
        kills=2,
        battles_survived=3,
        serial=42,
    )
    return ship


class TestToDict:
    def test_round_trip_preserves_all_fields(self, full_ship):
        """to_dict -> from_dict preserves every field."""
        data = ShipInstanceSerializer.to_dict(full_ship)
        restored = ShipInstanceSerializer.from_dict(data)

        assert restored.instance_id == full_ship.instance_id
        assert restored.design_id == full_ship.design_id
        assert restored.name == full_ship.name
        assert restored.owner_id == full_ship.owner_id
        assert restored.design_data == full_ship.design_data
        assert restored.current_hp == full_ship.current_hp
        assert set(restored.components) == set(full_ship.components)
        for key, cs in full_ship.components.items():
            assert restored.components[key].current_hp == cs.current_hp
            assert restored.components[key].instance_index == cs.instance_index
        assert restored.consumable_levels == full_ship.consumable_levels
        assert restored.component_toggles == full_ship.component_toggles
        assert restored.cargo_contents == full_ship.cargo_contents
        assert restored.is_alive == full_ship.is_alive
        assert restored.is_derelict == full_ship.is_derelict
        assert restored.experience == full_ship.experience
        assert restored.kills == full_ship.kills
        assert restored.battles_survived == full_ship.battles_survived
        assert restored.serial == full_ship.serial

    def test_to_dict_does_not_emit_legacy_component_damage_key(self, full_ship):
        """PROJ-276 Phase 5: new saves no longer carry `component_damage`."""
        data = ShipInstanceSerializer.to_dict(full_ship)
        assert 'component_damage' not in data

    def test_cargo_contents_omitted_when_empty(self):
        """to_dict does not include cargo_contents key when empty."""
        ship = ShipInstance(
            instance_id='test-1', design_id='D', name='S', owner_id=0,
        )
        data = ShipInstanceSerializer.to_dict(ship)
        assert 'cargo_contents' not in data


class TestFromDict:
    def test_raises_on_missing_required_keys(self):
        """from_dict raises PersistenceException for missing required keys."""
        with pytest.raises(PersistenceException):
            ShipInstanceSerializer.from_dict({'instance_id': 'x'})

    def test_raises_on_negative_current_hp(self):
        """from_dict raises PersistenceException for negative current_hp."""
        data = {
            'instance_id': 'x', 'design_id': 'd', 'name': 'n', 'owner_id': 0,
            'current_hp': -10,
        }
        with pytest.raises(PersistenceException):
            ShipInstanceSerializer.from_dict(data)

    def test_raises_on_negative_experience(self):
        """from_dict raises PersistenceException for negative experience."""
        data = {
            'instance_id': 'x', 'design_id': 'd', 'name': 'n', 'owner_id': 0,
            'experience': -1,
        }
        with pytest.raises(PersistenceException):
            ShipInstanceSerializer.from_dict(data)

    def test_registries_passed_through(self):
        """from_dict passes registries to the constructed instance."""
        mock_registries = MagicMock()
        data = {
            'instance_id': 'x', 'design_id': 'd', 'name': 'n', 'owner_id': 0,
            'components': {},
        }
        instance = ShipInstanceSerializer.from_dict(data, registries=mock_registries)
        assert instance._registries is mock_registries

    def test_missing_components_raises_persistence_exception(self):
        """PROJ-404: missing `components` key routes through require_keys() and
        raises PersistenceException, not raw KeyError."""
        data = {
            'instance_id': 'x', 'design_id': 'd', 'name': 'n', 'owner_id': 0,
            # No 'components' key
        }
        with pytest.raises(PersistenceException):
            ShipInstanceSerializer.from_dict(data)

    def test_legacy_resource_levels_field_is_not_accepted(self):
        """PROJ-404 / Rule 3: the `resource_levels` rename fallback is
        deleted. A legacy payload that supplies only `resource_levels`
        deserializes with empty consumables (it is treated as if the field
        were absent), not silently mapped to `consumable_levels`."""
        data = {
            'instance_id': 'x', 'design_id': 'd', 'name': 'n', 'owner_id': 0,
            'components': {},
            'resource_levels': {'fuel': 99.0, 'energy': 99.0},
        }
        instance = ShipInstanceSerializer.from_dict(data)
        # Legacy field is ignored — does NOT populate consumable_levels.
        assert instance.consumable_levels == {}

    def test_canonical_consumable_levels_round_trip(self):
        """PROJ-404: positive regression — current canonical shape using
        `consumable_levels` deserializes correctly."""
        data = {
            'instance_id': 'x', 'design_id': 'd', 'name': 'n', 'owner_id': 0,
            'components': {},
            'consumable_levels': {'fuel': 75.0, 'energy': 50.0},
        }
        instance = ShipInstanceSerializer.from_dict(data)
        assert instance.consumable_levels == {'fuel': 75.0, 'energy': 50.0}


class TestClone:
    def test_clone_produces_new_instance_id(self, full_ship):
        """clone creates a new instance_id."""
        cloned = ShipInstanceSerializer.clone(full_ship)
        assert cloned.instance_id != full_ship.instance_id

    def test_clone_preserves_data(self, full_ship):
        """clone preserves all non-identity data."""
        cloned = ShipInstanceSerializer.clone(full_ship)
        assert cloned.design_id == full_ship.design_id
        assert cloned.name == full_ship.name
        assert cloned.owner_id == full_ship.owner_id
        assert cloned.design_data == full_ship.design_data
        assert cloned.current_hp == full_ship.current_hp
        assert set(cloned.components) == set(full_ship.components)
        assert cloned.cargo_contents == full_ship.cargo_contents

    def test_clone_deep_copies_mutable_fields(self, full_ship):
        """clone deep copies dicts so mutations don't propagate."""
        cloned = ShipInstanceSerializer.clone(full_ship)
        new_key = component_state_key('new_comp', 0)
        cloned.components[new_key] = ComponentState(
            component_id='new_comp', instance_index=0, current_hp=10.0,
        )
        assert new_key not in full_ship.components


class TestJson:
    def test_json_round_trip(self, full_ship):
        """to_json -> from_json preserves data."""
        json_str = ShipInstanceSerializer.to_json(full_ship)
        restored = ShipInstanceSerializer.from_json(json_str)
        assert restored.instance_id == full_ship.instance_id
        assert restored.name == full_ship.name
        assert restored.current_hp == full_ship.current_hp
