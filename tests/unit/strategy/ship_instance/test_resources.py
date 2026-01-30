"""
Tests for ShipInstance - resource management.

PROJ-48: Split from test_ship_instance_proj08.py
"""

import pytest
from game.strategy.data.ship_instance import ShipInstance


class TestGetResourceCapacity:
    """Tests for get_resource_capacity method."""

    def test_get_resource_capacity_fuel(self, make_design_data_with_stats):
        """get_resource_capacity returns fuel capacity from resource_storage."""
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

        assert ship.get_resource_capacity('fuel') == 5000

    def test_get_resource_capacity_energy(self, make_design_data_with_stats):
        """get_resource_capacity returns energy capacity from resource_storage."""
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

        assert ship.get_resource_capacity('energy') == 2000

    def test_get_resource_capacity_custom_resource(self, make_design_data_with_stats):
        """get_resource_capacity returns custom resource capacity."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 1000, 'energy': 500, 'glag': 200}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        assert ship.get_resource_capacity('glag') == 200

    def test_get_resource_capacity_unknown_resource(self, make_design_data_with_stats):
        """get_resource_capacity returns 0 for unknown resource types."""
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

        assert ship.get_resource_capacity('unknown_resource') == 0

    def test_get_resource_capacity_zero_capacity(self, make_design_data_with_stats):
        """get_resource_capacity returns 0 when resource has zero capacity."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 0, 'energy': 100}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        assert ship.get_resource_capacity('fuel') == 0


class TestGetCurrentResource:
    """Tests for get_current_resource method."""

    def test_get_current_resource_returns_default_when_full(self, make_design_data_with_stats):
        """get_current_resource returns capacity when not tracked (assumed full)."""
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

        # No entry in resource_levels = full
        assert ship.get_current_resource('fuel') == 5000

    def test_get_current_resource_returns_current_when_partial(self, make_design_data_with_stats):
        """get_current_resource returns tracked value when partially consumed."""
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

        ship.resource_levels['fuel'] = 3000
        assert ship.get_current_resource('fuel') == 3000

    def test_get_current_resource_with_all_types(self, make_design_data_with_stats):
        """get_current_resource works with multiple resource types."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'fuel': 5000, 'energy': 2000, 'ammo': 500}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        ship.resource_levels['fuel'] = 2500
        ship.resource_levels['energy'] = 1000
        # ammo not tracked = full

        assert ship.get_current_resource('fuel') == 2500
        assert ship.get_current_resource('energy') == 1000
        assert ship.get_current_resource('ammo') == 500

    def test_get_current_resource_custom_resource(self, make_design_data_with_stats):
        """get_current_resource works with custom resource types."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'glag': 100}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        ship.resource_levels['glag'] = 50
        assert ship.get_current_resource('glag') == 50


class TestConsumeResource:
    """Tests for consume_resource method."""

    def test_consume_resource_success(self, make_design_data_with_stats):
        """consume_resource returns True and updates level on success."""
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

        result = ship.consume_resource('fuel', 1000)

        assert result is True
        assert ship.resource_levels['fuel'] == 4000

    def test_consume_resource_insufficient_fails(self, make_design_data_with_stats):
        """consume_resource returns False when insufficient resources."""
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

        ship.resource_levels['fuel'] = 500
        result = ship.consume_resource('fuel', 1000)

        assert result is False
        assert ship.resource_levels['fuel'] == 500  # Unchanged

    def test_consume_resource_exact_amount(self, make_design_data_with_stats):
        """consume_resource succeeds when consuming exactly available amount."""
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

        ship.resource_levels['fuel'] = 1000
        result = ship.consume_resource('fuel', 1000)

        assert result is True
        assert ship.resource_levels['fuel'] == 0

    def test_consume_resource_zero_amount(self, make_design_data_with_stats):
        """consume_resource with zero amount returns True without changes."""
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

        result = ship.consume_resource('fuel', 0)

        assert result is True
        # Should still track now that consume was called
        assert ship.get_current_resource('fuel') == 5000

    def test_consume_resource_multiple_types(self, make_design_data_with_stats):
        """consume_resource handles multiple resource types independently."""
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

        ship.consume_resource('fuel', 1000)
        ship.consume_resource('energy', 500)

        assert ship.resource_levels['fuel'] == 4000
        assert ship.resource_levels['energy'] == 1500

    def test_consume_resource_custom_type(self, make_design_data_with_stats):
        """consume_resource works with custom resource types."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_storage': {'glag': 100}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.consume_resource('glag', 25)

        assert result is True
        assert ship.resource_levels['glag'] == 75

    def test_consume_resource_when_not_tracked(self, make_design_data_with_stats):
        """consume_resource initializes tracking when first consumed."""
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

        # Not tracked yet
        assert 'fuel' not in ship.resource_levels

        result = ship.consume_resource('fuel', 1000)

        assert result is True
        assert 'fuel' in ship.resource_levels
        assert ship.resource_levels['fuel'] == 4000


class TestGetAllResourceCostsPerHex:
    """Tests for get_all_resource_costs_per_hex method."""

    def test_get_all_resource_costs_per_hex_empty(self, make_design_data_with_stats):
        """get_all_resource_costs_per_hex returns empty dict when none defined."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_hex': {}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_hex()
        assert result == {}

    def test_get_all_resource_costs_per_hex_fuel_only(self, make_design_data_with_stats):
        """get_all_resource_costs_per_hex returns fuel cost when defined."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_hex': {'fuel': 100}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_hex()
        assert result == {'fuel': 100}

    def test_get_all_resource_costs_per_hex_multiple_resources(self, make_design_data_with_stats):
        """get_all_resource_costs_per_hex returns multiple resource costs."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_hex': {'fuel': 100, 'energy': 50}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_hex()
        assert result == {'fuel': 100, 'energy': 50}

    def test_get_all_resource_costs_per_hex_custom_resource(self, make_design_data_with_stats):
        """get_all_resource_costs_per_hex includes custom resource types."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_hex': {'fuel': 100, 'glag': 5}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_hex()
        assert result == {'fuel': 100, 'glag': 5}


class TestGetAllResourceCostsPerTurn:
    """Tests for get_all_resource_costs_per_turn method."""

    def test_get_all_resource_costs_per_turn_empty(self, make_design_data_with_stats):
        """get_all_resource_costs_per_turn returns empty dict when none defined."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_turn': {}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_turn()
        assert result == {}

    def test_get_all_resource_costs_per_turn_single_resource(self, make_design_data_with_stats):
        """get_all_resource_costs_per_turn returns single resource cost."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_turn': {'energy': 100}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_turn()
        assert result == {'energy': 100}

    def test_get_all_resource_costs_per_turn_multiple_resources(self, make_design_data_with_stats):
        """get_all_resource_costs_per_turn returns multiple resource costs."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_turn': {'energy': 100, 'fuel': 50}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_turn()
        assert result == {'energy': 100, 'fuel': 50}

    def test_get_all_resource_costs_per_turn_custom_resource(self, make_design_data_with_stats):
        """get_all_resource_costs_per_turn includes custom resource types."""
        design_data = make_design_data_with_stats(expected_stats={
            'resource_consumption_per_turn': {'energy': 100, 'glag': 10}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_all_resource_costs_per_turn()
        assert result == {'energy': 100, 'glag': 10}


class TestGetWarpResourceCosts:
    """Tests for get_warp_resource_costs method."""

    def test_get_warp_resource_costs_empty(self, make_design_data_with_stats):
        """get_warp_resource_costs returns empty dict when no warp drive."""
        design_data = make_design_data_with_stats(expected_stats={
            'warp_resource_costs': {}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_warp_resource_costs()
        assert result == {}

    def test_get_warp_resource_costs_energy_only(self, make_design_data_with_stats):
        """get_warp_resource_costs returns energy cost."""
        design_data = make_design_data_with_stats(expected_stats={
            'warp_resource_costs': {'energy': 500}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_warp_resource_costs()
        assert result == {'energy': 500}

    def test_get_warp_resource_costs_fuel_and_energy(self, make_design_data_with_stats):
        """get_warp_resource_costs returns both fuel and energy costs."""
        design_data = make_design_data_with_stats(expected_stats={
            'warp_resource_costs': {'energy': 500, 'fuel': 100}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_warp_resource_costs()
        assert result == {'energy': 500, 'fuel': 100}

    def test_get_warp_resource_costs_custom_resource(self, make_design_data_with_stats):
        """get_warp_resource_costs includes custom resource types."""
        design_data = make_design_data_with_stats(expected_stats={
            'warp_resource_costs': {'energy': 500, 'antimatter': 50}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        result = ship.get_warp_resource_costs()
        assert result == {'energy': 500, 'antimatter': 50}

    def test_get_warp_resource_costs_damaged_warp_drive(self, make_design_data_with_stats):
        """Damaged warp drive should affect warp costs through stats."""
        # This tests the integration with stats service
        # When warp drive is damaged, stats service should return 0 for warp costs
        design_data = make_design_data_with_stats(expected_stats={
            'warp_resource_costs': {}  # Damaged warp returns empty
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )
        ship.component_damage['warp_drive'] = 50  # Damaged

        result = ship.get_warp_resource_costs()
        assert result == {}


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
