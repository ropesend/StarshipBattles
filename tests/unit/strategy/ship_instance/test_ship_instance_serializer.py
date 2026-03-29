"""Tests for ShipInstanceSerializer - extracted serialization logic."""

import pytest
from unittest.mock import MagicMock

from game.core.exceptions import PersistenceException
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
        component_damage={'comp_1': 50},
        resource_levels={'fuel': 100.0, 'energy': 50.0},
        component_toggles={'comp_2': False},
        cargo_contents={'passengers': 10},
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
        assert restored.component_damage == full_ship.component_damage
        assert restored.resource_levels == full_ship.resource_levels
        assert restored.component_toggles == full_ship.component_toggles
        assert restored.cargo_contents == full_ship.cargo_contents
        assert restored.is_alive == full_ship.is_alive
        assert restored.is_derelict == full_ship.is_derelict
        assert restored.experience == full_ship.experience
        assert restored.kills == full_ship.kills
        assert restored.battles_survived == full_ship.battles_survived
        assert restored.serial == full_ship.serial

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
        }
        instance = ShipInstanceSerializer.from_dict(data, registries=mock_registries)
        assert instance._registries is mock_registries


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
        assert cloned.component_damage == full_ship.component_damage
        assert cloned.cargo_contents == full_ship.cargo_contents

    def test_clone_deep_copies_mutable_fields(self, full_ship):
        """clone deep copies dicts so mutations don't propagate."""
        cloned = ShipInstanceSerializer.clone(full_ship)
        cloned.component_damage['new_comp'] = 10
        assert 'new_comp' not in full_ship.component_damage


class TestJson:
    def test_json_round_trip(self, full_ship):
        """to_json -> from_json preserves data."""
        json_str = ShipInstanceSerializer.to_json(full_ship)
        restored = ShipInstanceSerializer.from_json(json_str)
        assert restored.instance_id == full_ship.instance_id
        assert restored.name == full_ship.name
        assert restored.current_hp == full_ship.current_hp
