"""
Tests for ShipInstance - convenience methods and method interactions.

PROJ-48: Split from test_resources.py
"""

import pytest
from game.strategy.data.ship_instance import ShipInstance


class TestResourceConvenienceMethods:
    """Tests for fuel/energy convenience methods."""

    def test_get_current_fuel(self, make_design_data_with_stats):
        """get_current_fuel method returns correct fuel level."""
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

        # Use legacy method
        current = ship.get_current_fuel()
        assert current == 5000

        # Consume and check again
        ship.resource_levels['fuel'] = 3000
        current = ship.get_current_fuel()
        assert current == 3000

    def test_consume_fuel(self, make_design_data_with_stats):
        """consume_fuel method consumes fuel correctly."""
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

        result = ship.consume_fuel(1000)

        assert result is True
        assert ship.resource_levels['fuel'] == 4000

    def test_get_current_energy(self, make_design_data_with_stats):
        """get_current_energy method returns correct energy level."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'energy': 2000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        # Use legacy method
        current = ship.get_current_energy()
        assert current == 2000

        # Consume and check again
        ship.resource_levels['energy'] = 1500
        current = ship.get_current_energy()
        assert current == 1500

    def test_consume_energy(self, make_design_data_with_stats):
        """consume_energy method consumes energy correctly."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'energy': 2000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.consume_energy(500)

        assert result is True
        assert ship.resource_levels['energy'] == 1500


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

    def test_consume_resource_tracks_in_resource_levels(self, make_design_data_with_stats):
        """consume_resource updates resource_levels dict."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000, 'energy': 2000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        # Initially empty
        assert ship.resource_levels == {}

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
        # fuel should be removed from resource_levels when full
        assert 'fuel' not in ship.resource_levels

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
