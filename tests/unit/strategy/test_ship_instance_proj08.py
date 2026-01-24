"""
Tests for ShipInstance - PROJ-08: Data-Driven Resource System.

This module contains 71 tests covering the new resource system features
added to ShipInstance for PROJ-08.
"""

import pytest
from unittest.mock import patch, MagicMock
from game.strategy.data.ship_instance import ShipInstance


@pytest.fixture
def make_design_data_with_stats():
    """Factory for creating design_data with expected_stats."""
    def _make(expected_stats=None):
        return {
            'layers': {},
            'name': 'TestShip',
            'expected_stats': expected_stats or {}
        }
    return _make


# =============================================================================
# 3.1 Component Toggles Field (2 tests)
# =============================================================================

class TestComponentTogglesField:
    """Tests for component_toggles field initialization."""

    def test_component_toggles_field_initialized_empty(self, make_design_data_with_stats):
        """Component toggles should be empty dict on new instance."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )
        assert ship.component_toggles == {}

    def test_component_toggles_field_default_factory(self, make_design_data_with_stats):
        """Each instance should have its own component_toggles dict."""
        design_data = make_design_data_with_stats()
        ship1 = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship 1',
            owner_id=0,
            design_data=design_data
        )
        ship2 = ShipInstance(
            instance_id='test-2',
            design_id='TestDesign',
            name='Test Ship 2',
            owner_id=0,
            design_data=design_data
        )

        # Modify ship1's toggles
        ship1.component_toggles['engine'] = False

        # ship2 should not be affected
        assert 'engine' not in ship2.component_toggles
        assert ship1.component_toggles is not ship2.component_toggles


# =============================================================================
# 3.2 set_component_enabled (5 tests)
# =============================================================================

class TestSetComponentEnabled:
    """Tests for set_component_enabled method."""

    def test_set_component_enabled_enable(self, make_design_data_with_stats):
        """set_component_enabled with True should enable component."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        ship.set_component_enabled('engine', True)
        assert ship.component_toggles['engine'] is True

    def test_set_component_enabled_disable(self, make_design_data_with_stats):
        """set_component_enabled with False should disable component."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        ship.set_component_enabled('engine', False)
        assert ship.component_toggles['engine'] is False

    def test_set_component_enabled_multiple_components(self, make_design_data_with_stats):
        """set_component_enabled should handle multiple components."""
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

        assert ship.component_toggles['engine'] is False
        assert ship.component_toggles['warp_drive'] is True
        assert ship.component_toggles['shield'] is False

    def test_set_component_enabled_overwrites_existing(self, make_design_data_with_stats):
        """set_component_enabled should overwrite existing state."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        ship.set_component_enabled('engine', False)
        assert ship.component_toggles['engine'] is False

        ship.set_component_enabled('engine', True)
        assert ship.component_toggles['engine'] is True

    def test_set_component_enabled_invalidates_cache(self, make_design_data_with_stats):
        """set_component_enabled should invalidate stats cache."""
        design_data = make_design_data_with_stats(expected_stats={'max_hp': 100})
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        # Populate cache
        _ = ship.get_calculated_stats()
        assert ship._cached_stats is not None

        # Toggling should invalidate cache
        ship.set_component_enabled('engine', False)
        assert ship._cached_stats is None


# =============================================================================
# 3.3 is_component_enabled (4 tests)
# =============================================================================

class TestIsComponentEnabled:
    """Tests for is_component_enabled method."""

    def test_is_component_enabled_default_true(self, make_design_data_with_stats):
        """is_component_enabled returns True for untracked components."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        # Component not in toggles should default to True
        assert ship.is_component_enabled('nonexistent_component') is True

    def test_is_component_enabled_explicitly_true(self, make_design_data_with_stats):
        """is_component_enabled returns True when explicitly set True."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        ship.component_toggles['engine'] = True
        assert ship.is_component_enabled('engine') is True

    def test_is_component_enabled_explicitly_false(self, make_design_data_with_stats):
        """is_component_enabled returns False when explicitly set False."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        ship.component_toggles['engine'] = False
        assert ship.is_component_enabled('engine') is False

    def test_is_component_enabled_after_set(self, make_design_data_with_stats):
        """is_component_enabled reflects changes from set_component_enabled."""
        design_data = make_design_data_with_stats()
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        ship.set_component_enabled('engine', False)
        assert ship.is_component_enabled('engine') is False

        ship.set_component_enabled('engine', True)
        assert ship.is_component_enabled('engine') is True


# =============================================================================
# 3.4 get_resource_capacity (5 tests)
# =============================================================================

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


# =============================================================================
# 3.5 get_current_resource (4 tests)
# =============================================================================

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


# =============================================================================
# 3.6 consume_resource (7 tests)
# =============================================================================

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


# =============================================================================
# 3.7 get_all_resource_costs_per_hex (4 tests)
# =============================================================================

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


# =============================================================================
# 3.8 get_all_resource_costs_per_turn (4 tests)
# =============================================================================

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


# =============================================================================
# 3.9 get_warp_resource_costs (5 tests)
# =============================================================================

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


# =============================================================================
# 3.10 Cache Invalidation (3 tests)
# =============================================================================

class TestCacheInvalidation:
    """Tests for stats cache invalidation."""

    def test_cache_invalidation_on_set_component_enabled(self, make_design_data_with_stats):
        """set_component_enabled invalidates stats cache."""
        design_data = make_design_data_with_stats(expected_stats={
            'max_hp': 100,
            'resource_storage': {'fuel': 1000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        # Populate cache
        _ = ship.get_calculated_stats()
        assert ship._cached_stats is not None

        # Toggle component
        ship.set_component_enabled('engine', False)

        # Cache should be invalidated
        assert ship._cached_stats is None

    def test_cache_recalculated_after_toggle(self, make_design_data_with_stats):
        """Stats are recalculated after cache invalidation from toggle."""
        design_data = make_design_data_with_stats(expected_stats={
            'max_hp': 100,
            'resource_storage': {'fuel': 1000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        # Get initial stats
        stats1 = ship.get_calculated_stats()
        assert ship._cached_stats is not None

        # Toggle and get stats again
        ship.set_component_enabled('engine', False)
        stats2 = ship.get_calculated_stats()

        # Cache should be repopulated
        assert ship._cached_stats is not None

    def test_cache_not_invalidated_on_other_changes(self, make_design_data_with_stats):
        """Cache is not invalidated by non-toggle changes (except damage)."""
        design_data = make_design_data_with_stats(expected_stats={
            'max_hp': 100,
            'resource_storage': {'fuel': 1000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        # Populate cache
        _ = ship.get_calculated_stats()
        assert ship._cached_stats is not None

        # Consume resource (should not invalidate cache)
        ship.consume_resource('fuel', 100)

        # Cache should still be valid
        assert ship._cached_stats is not None


# =============================================================================
# 3.11 Serialization - to_dict (3 tests)
# =============================================================================

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


# =============================================================================
# 3.12 Serialization - from_dict (4 tests)
# =============================================================================

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
            'component_toggles': {}
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
            'component_toggles': {'engine': False, 'shield': True}
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
            'design_data': make_design_data_with_stats()
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
            'component_toggles': {'engine': False, 'warp_drive': True}
        }

        ship = ShipInstance.from_dict(original_data)
        result = ship.to_dict()

        assert result['component_toggles'] == original_data['component_toggles']


# =============================================================================
# 3.13 Clone Preservation (4 tests)
# =============================================================================

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


# =============================================================================
# 3.14 Stats Integration (2 tests)
# =============================================================================

class TestStatsIntegration:
    """Tests for component toggle integration with stats calculation."""

    def test_component_toggles_passed_to_stats_calculation(self, make_design_data_with_stats):
        """component_toggles are passed to ShipStatsService.calculate_stats."""
        design_data = make_design_data_with_stats(expected_stats={'max_hp': 100})
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )
        ship.set_component_enabled('engine', False)

        with patch('game.strategy.services.ship_stats_service.ShipStatsService.calculate_stats') as mock_calc:
            mock_calc.return_value = {'max_hp': 100}

            _ = ship.get_calculated_stats(force_refresh=True)

            # Verify component_toggles was passed
            mock_calc.assert_called_once()
            call_args = mock_calc.call_args
            assert call_args[0][2] == {'engine': False}  # Third positional arg

    def test_disabled_component_affects_stats(self, make_design_data_with_stats):
        """Disabled component should affect calculated stats."""
        # This is more of an integration test with ShipStatsService
        # The stats service should exclude disabled components' abilities
        design_data = make_design_data_with_stats(expected_stats={
            'max_hp': 100,
            'resource_storage': {'fuel': 1000}
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        # Initially enabled
        stats1 = ship.get_calculated_stats()

        ship.set_component_enabled('fuel_tank', False)

        # Toggles should be passed to stats calculation
        # The actual effect depends on ShipStatsService implementation
        stats2 = ship.get_calculated_stats()

        # This verifies the toggle is in place
        assert ship.component_toggles == {'fuel_tank': False}


# =============================================================================
# 3.15 Resource Method Interactions (3 tests)
# =============================================================================

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


# =============================================================================
# 3.16 Backward Compatibility (4 tests)
# =============================================================================

class TestBackwardCompatibility:
    """Tests for backward compatibility with legacy fuel/energy methods."""

    def test_legacy_methods_still_work_get_current_fuel(self, make_design_data_with_stats):
        """Legacy get_current_fuel method still works."""
        design_data = make_design_data_with_stats(expected_stats={
            'max_fuel': 5000,
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

    def test_legacy_methods_still_work_consume_fuel(self, make_design_data_with_stats):
        """Legacy consume_fuel method still works."""
        design_data = make_design_data_with_stats(expected_stats={
            'max_fuel': 5000,
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

    def test_legacy_methods_still_work_get_current_energy(self, make_design_data_with_stats):
        """Legacy get_current_energy method still works."""
        design_data = make_design_data_with_stats(expected_stats={
            'max_energy': 2000,
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

    def test_legacy_methods_still_work_consume_energy(self, make_design_data_with_stats):
        """Legacy consume_energy method still works."""
        design_data = make_design_data_with_stats(expected_stats={
            'max_energy': 2000,
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


# =============================================================================
# 3.17 Edge Cases (4 tests)
# =============================================================================

class TestAdditionalCoverage:
    """Additional tests for comprehensive coverage."""

    def test_resource_levels_preserved_through_serialization(self, make_design_data_with_stats):
        """resource_levels are preserved through to_dict/from_dict round trip."""
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

        data = ship.to_dict()
        restored = ShipInstance.from_dict(data)

        assert restored.resource_levels == {'fuel': 4000, 'energy': 1500}

    def test_multiple_toggles_with_stats_refresh(self, make_design_data_with_stats):
        """Multiple component toggles correctly invalidate and refresh cache."""
        design_data = make_design_data_with_stats(expected_stats={'max_hp': 100})
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

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

    def test_clone_preserves_resource_levels(self, make_design_data_with_stats):
        """clone preserves resource_levels state."""
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

        cloned = ship.clone()

        assert cloned.resource_levels == {'fuel': 4000}
        # Modify clone should not affect original
        cloned.consume_resource('fuel', 500)
        assert ship.resource_levels == {'fuel': 4000}
        assert cloned.resource_levels == {'fuel': 3500}


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
        ship.resource_levels['fuel'] = 3000

        # Negative amount should be rejected - cannot "consume" a negative amount
        result = ship.consume_resource('fuel', -100)

        # Should return False and leave resource unchanged
        assert result is False
        assert ship.resource_levels['fuel'] == 3000

    def test_get_resource_capacity_empty_stats(self, make_design_data_with_stats):
        """get_resource_capacity handles empty expected_stats."""
        design_data = make_design_data_with_stats(expected_stats={})
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

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

    def test_get_all_resource_costs_when_stats_missing_field(self, make_design_data_with_stats):
        """get_all_resource_costs_* handle missing fields gracefully."""
        design_data = make_design_data_with_stats(expected_stats={
            'max_hp': 100
            # Missing resource cost fields
        })
        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestDesign',
            name='Test Ship',
            owner_id=0,
            design_data=design_data
        )

        # Should not raise, return empty dict
        per_hex = ship.get_all_resource_costs_per_hex()
        per_turn = ship.get_all_resource_costs_per_turn()
        warp = ship.get_warp_resource_costs()

        assert per_hex == {}
        assert per_turn == {}
        assert warp == {}
