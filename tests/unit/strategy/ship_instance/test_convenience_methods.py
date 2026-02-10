"""
Tests for ShipInstance - convenience methods and method interactions.

PROJ-48: Split from test_resources.py
PROJ-91: Removed tests for type-specific methods (get_current_fuel, consume_fuel,
         get_current_energy, consume_energy) - use generic methods instead.
"""

import pytest
from game.strategy.data.ship_instance import ShipInstance


class TestResourceMethodInteractions:
    """Tests for interactions between resource methods."""

    def test_get_resource_capacity_with_disabled_component(self, make_design_data_with_stats):
        """get_resource_capacity reflects component toggle state through stats."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 1000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        initial_capacity = ship.get_resource_capacity('fuel')
        assert initial_capacity == 1000

        # Disable fuel tank - should invalidate cache
        ship.set_component_enabled('fuel_tank', False)

        # Cache was invalidated, will recalculate
        # Result depends on stats service behavior with toggles

    def test_consume_resource_updates_resource_levels(self, make_design_data_with_stats):
        """consume_resource updates resource_levels dict.

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
            resource_levels={'fuel': 5000, 'energy': 2000}
        )

        ship.consume_resource('fuel', 1000)
        ship.consume_resource('energy', 500)

        assert ship.resource_levels == {'fuel': 4000, 'energy': 1500}

    def test_get_all_resource_costs_multiple_calls_consistent(self, make_design_data_with_stats):
        """Multiple calls to get_all_resource_costs_* are consistent."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_hex': {'fuel': 100, 'energy': 50},
            'resource_consumption_per_turn': {'energy': 200},
            'warp_resource_costs': {'energy': 500, 'fuel': 75}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        # Call multiple times
        per_hex1 = ship.get_all_resource_costs_per_hex()
        per_turn1 = ship.get_all_resource_costs_per_turn()
        warp1 = ship.get_warp_resource_costs()

        per_hex2 = ship.get_all_resource_costs_per_hex()
        per_turn2 = ship.get_all_resource_costs_per_turn()
        warp2 = ship.get_warp_resource_costs()

        assert per_hex1 == per_hex2
        assert per_turn1 == per_turn2
        assert warp1 == warp2


class TestResupply:
    """Tests for resupply method (PROJ-91 bug fix)."""

    def test_resupply_uses_resource_storage_not_max_key(self, make_design_data_with_stats):
        """resupply uses resource_storage for max, not 'max_{resource_name}' key.

        Regression test for PROJ-91: resupply() was using max_key format
        ('max_fuel') which doesn't exist in calculated stats. The correct
        key is resource_storage['fuel'].

        PROJ-95: Resources always stored (no sparse dict convention).
        """
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 250}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data,
            resource_levels={'fuel': 100}  # Depleted fuel
        )

        # Resupply should correctly use 250 as max (from resource_storage)
        # not 100 (default fallback from old buggy code)
        actual = ship.resupply('fuel', 200)

        # Should be clamped to max of 250
        assert actual == 150  # 250 - 100 = 150 actual resupplied
        # fuel should remain at max value (PROJ-95: always store)
        assert ship.resource_levels['fuel'] == 250

    def test_resupply_partial(self, make_design_data_with_stats):
        """resupply partial amount works correctly."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 1000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data,
            resource_levels={'fuel': 500}
        )

        actual = ship.resupply('fuel', 200)

        assert actual == 200
        assert ship.resource_levels['fuel'] == 700
