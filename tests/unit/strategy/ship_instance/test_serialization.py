"""
Tests for ShipInstance - serialization, cloning, and edge cases.

PROJ-48: Split from test_ship_instance_proj08.py
PROJ-211: Updated to use make_ship_with_stats fixture for DI compliance.
"""

import pytest
from game.strategy.data.ship_instance import ShipInstance


class TestToDictSerialization:
    """Tests for to_dict serialization."""

    def test_to_dict_includes_component_toggles_empty(self, make_design_data_with_stats):
        """to_dict includes empty component_toggles."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.to_dict()

        assert 'component_toggles' in result
        assert result['component_toggles'] == {}

    def test_to_dict_includes_component_toggles_with_values(self, make_design_data_with_stats):
        """to_dict includes component_toggles with values."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        ship.set_component_enabled('engine', False)
        ship.set_component_enabled('shield', True)

        result = ship.to_dict()

        assert result['component_toggles'] == {'engine': False, 'shield': True}

    def test_to_dict_preserves_all_toggle_states(self, make_design_data_with_stats):
        """to_dict preserves all toggle states including mixed values."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        ship.set_component_enabled('engine', False)
        ship.set_component_enabled('warp_drive', True)
        ship.set_component_enabled('shield', False)
        ship.set_component_enabled('reactor', True)

        result = ship.to_dict()

        assert result['component_toggles'] == {
            'engine': False,
            'warp_drive': True,
            'shield': False,
            'reactor': True
        }


class TestFromDictSerialization:
    """Tests for from_dict deserialization."""

    def test_from_dict_restores_component_toggles_empty(self, make_design_data_with_stats):
        """from_dict restores empty component_toggles."""
        data = {
            'instance_id': 'test-1',
            'design_id': 'TestDesign',
            'name': 'Test Ship',
            'owner_id': 0,
            'design_data': make_design_data_with_stats(),
            'component_toggles': {},
            'components': {},
        }

        ship = ShipInstance.from_dict(data)

        assert ship.component_toggles == {}

    def test_from_dict_restores_component_toggles_with_values(self, make_design_data_with_stats):
        """from_dict restores component_toggles with values."""
        data = {
            'instance_id': 'test-1',
            'design_id': 'TestDesign',
            'name': 'Test Ship',
            'owner_id': 0,
            'design_data': make_design_data_with_stats(),
            'component_toggles': {'engine': False, 'shield': True},
            'components': {},
        }

        ship = ShipInstance.from_dict(data)

        assert ship.component_toggles == {'engine': False, 'shield': True}

    def test_from_dict_missing_component_toggles_defaults_to_empty(self, make_design_data_with_stats):
        """from_dict defaults to empty dict when component_toggles is missing."""
        data = {
            'instance_id': 'test-1',
            'design_id': 'TestDesign',
            'name': 'Test Ship',
            'owner_id': 0,
            'design_data': make_design_data_with_stats(),
            'components': {},
            # No component_toggles key
        }

        ship = ShipInstance.from_dict(data)

        assert ship.component_toggles == {}

    def test_from_dict_then_to_dict_round_trip(self, make_design_data_with_stats):
        """from_dict followed by to_dict preserves component_toggles."""
        original_data = {
            'instance_id': 'test-1',
            'design_id': 'TestDesign',
            'name': 'Test Ship',
            'owner_id': 0,
            'design_data': make_design_data_with_stats(),
            'component_toggles': {'engine': False, 'warp_drive': True},
            'components': {},
        }

        ship = ShipInstance.from_dict(original_data)
        result = ship.to_dict()

        assert result['component_toggles'] == original_data['component_toggles']


class TestClonePreservation:
    """Tests for clone method preserving component_toggles."""

    def test_clone_preserves_component_toggles_empty(self, make_design_data_with_stats):
        """clone preserves empty component_toggles."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        cloned = ship.clone()

        assert cloned.component_toggles == {}

    def test_clone_preserves_component_toggles_with_values(self, make_design_data_with_stats):
        """clone preserves component_toggles with values."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )
        ship.set_component_enabled('engine', False)
        ship.set_component_enabled('shield', True)

        cloned = ship.clone()

        assert cloned.component_toggles == {'engine': False, 'shield': True}

    def test_clone_toggles_are_independent_copies(self, make_design_data_with_stats):
        """clone creates independent copy of component_toggles."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )
        ship.set_component_enabled('engine', False)

        cloned = ship.clone()

        # Modify clone
        cloned.set_component_enabled('engine', True)
        cloned.set_component_enabled('reactor', False)

        # Original should be unchanged
        assert ship.component_toggles == {'engine': False}
        assert ship.component_toggles is not cloned.component_toggles

    def test_clone_preserves_new_instance_id(self, make_design_data_with_stats):
        """clone creates new instance_id while preserving toggles."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )
        ship.set_component_enabled('engine', False)

        cloned = ship.clone()

        # New ID but same toggles
        assert cloned.instance_id != ship.instance_id
        assert cloned.component_toggles == {'engine': False}


class TestAdditionalCoverage:
    """Additional tests for comprehensive coverage."""

    def test_consumable_levels_preserved_through_serialization(self, make_design_data_with_stats):
        """consumable_levels are preserved through to_dict/from_dict round trip.

        PROJ-95: Resources always stored with actual values.
        """
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000, 'energy': 2000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data,
            consumable_levels={'fuel': 5000, 'energy': 2000}
        )

        ship.consume_resource('fuel', 1000)
        ship.consume_resource('energy', 500)

        data = ship.to_dict()
        restored = ShipInstance.from_dict(data)

        assert restored.consumable_levels == {'fuel': 4000, 'energy': 1500}

    def test_multiple_toggles_with_stats_refresh(self, make_ship_with_stats):
        """Multiple component toggles correctly invalidate and refresh cache."""
        ship = make_ship_with_stats(expected_stats={'max_hp': 100})

        # Initial cache
        _ = ship.get_calculated_stats()
        assert ship._cached_stats is not None

        # First toggle
        ship.set_component_enabled('engine', False)
        assert ship._cached_stats is None

        # Get stats again
        _ = ship.get_calculated_stats()
        assert ship._cached_stats is not None

        # Second toggle
        ship.set_component_enabled('shield', True)
        assert ship._cached_stats is None

    def test_get_current_resource_for_zero_capacity_resource(self, make_design_data_with_stats):
        """get_current_resource returns 0 for resource with zero capacity."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 0}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        # Zero capacity means current is also 0 (assumed full of 0)
        assert ship.get_current_resource('fuel') == 0

    def test_clone_preserves_consumable_levels(self, make_design_data_with_stats):
        """clone preserves consumable_levels state.

        PROJ-95: Resources always stored with actual values.
        """
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000, 'energy': 2000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data,
            consumable_levels={'fuel': 5000, 'energy': 2000}
        )

        ship.consume_resource('fuel', 1000)

        cloned = ship.clone()

        assert cloned.consumable_levels == {'fuel': 4000, 'energy': 2000}
        # Modify clone should not affect original
        cloned.consume_resource('fuel', 500)
        assert ship.consumable_levels == {'fuel': 4000, 'energy': 2000}
        assert cloned.consumable_levels == {'fuel': 3500, 'energy': 2000}


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_consume_resource_negative_amount(self, make_design_data_with_stats):
        """consume_resource with negative amount should return False without modifying resources."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )
        ship.consumable_levels['fuel'] = 3000

        # Negative amount should be rejected - cannot "consume" a negative amount
        result = ship.consume_resource('fuel', -100)

        # Should return False and leave resource unchanged
        assert result is False
        assert ship.consumable_levels['fuel'] == 3000

    def test_get_resource_capacity_empty_stats(self, make_ship_with_stats):
        """get_resource_capacity handles empty expected_stats."""
        ship = make_ship_with_stats(expected_stats={})

        capacity = ship.get_resource_capacity('fuel')
        assert capacity == 0

    def test_component_toggles_with_nonexistent_component(self, make_design_data_with_stats):
        """Toggling nonexistent component is allowed."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        # Should not raise
        ship.set_component_enabled('nonexistent_component', False)

        assert ship.component_toggles['nonexistent_component'] is False
        assert ship.is_component_enabled('nonexistent_component') is False

    def test_get_all_resource_costs_when_stats_missing_field(self, make_ship_with_stats):
        """get_all_resource_costs_* handle missing fields gracefully."""
        ship = make_ship_with_stats(expected_stats={
            'max_hp': 100
            # Missing resource cost fields
        })

        # Should not raise, return empty dict
        per_hex = ship.get_all_resource_costs_per_hex()
        per_turn = ship.get_all_resource_costs_per_turn()
        warp = ship.get_warp_resource_costs()

        assert per_hex == {}
        assert per_turn == {}
        assert warp == {}
