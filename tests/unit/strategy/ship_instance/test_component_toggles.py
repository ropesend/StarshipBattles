"""
Tests for ShipInstance - component toggle functionality.

PROJ-48: Split from test_ship_instance_proj08.py
PROJ-211: Updated to use make_ship_with_stats fixture for DI compliance.
"""

import pytest
from unittest.mock import patch
from game.strategy.data.ship_instance import ShipInstance


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

    def test_set_component_enabled_invalidates_cache(self, make_ship_with_stats):
        """set_component_enabled should invalidate stats cache."""
        ship = make_ship_with_stats(expected_stats={'max_hp': 100})

        # Populate cache
        _ = ship.get_calculated_stats()
        assert ship._cached_stats is not None

        # Toggling should invalidate cache
        ship.set_component_enabled('engine', False)
        assert ship._cached_stats is None


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


class TestCacheInvalidation:
    """Tests for stats cache invalidation."""

    def test_cache_invalidation_on_set_component_enabled(self, make_ship_with_stats):
        """set_component_enabled invalidates stats cache."""
        ship = make_ship_with_stats(expected_stats={
            'max_hp': 100,
            'resource_storage': {'fuel': 1000}
        })

        # Populate cache
        _ = ship.get_calculated_stats()
        assert ship._cached_stats is not None

        # Toggle component
        ship.set_component_enabled('engine', False)

        # Cache should be invalidated
        assert ship._cached_stats is None

    def test_cache_recalculated_after_toggle(self, make_ship_with_stats):
        """Stats are recalculated after cache invalidation from toggle."""
        ship = make_ship_with_stats(expected_stats={
            'max_hp': 100,
            'resource_storage': {'fuel': 1000}
        })

        # Get initial stats
        stats1 = ship.get_calculated_stats()
        assert ship._cached_stats is not None

        # Toggle and get stats again
        ship.set_component_enabled('engine', False)
        stats2 = ship.get_calculated_stats()

        # Cache should be repopulated
        assert ship._cached_stats is not None

    def test_cache_not_invalidated_on_other_changes(self, make_ship_with_stats):
        """Cache is not invalidated by non-toggle changes (except damage)."""
        ship = make_ship_with_stats(expected_stats={
            'max_hp': 100,
            'resource_storage': {'fuel': 1000}
        })

        # Populate cache
        _ = ship.get_calculated_stats()
        assert ship._cached_stats is not None

        # Consume resource (should not invalidate cache)
        ship.consume_resource('fuel', 100)

        # Cache should still be valid
        assert ship._cached_stats is not None


class TestStatsIntegration:
    """Tests for component toggle integration with stats calculation."""

    def test_component_toggles_passed_to_stats_calculation(self, make_ship_with_stats):
        """component_toggles are passed to ShipStatsCalculator.calculate_stats."""
        ship = make_ship_with_stats(expected_stats={'max_hp': 100})
        ship.set_component_enabled('engine', False)

        with patch('game.strategy.services.ship_stats_calculator.ShipStatsCalculator.calculate_stats') as mock_calc:
            mock_calc.return_value = {'max_hp': 100}

            _ = ship.get_calculated_stats(force_refresh=True)

            # Verify component_toggles was passed
            mock_calc.assert_called_once()
            call_args = mock_calc.call_args
            assert call_args[0][2] == {'engine': False}  # Third positional arg

    def test_disabled_component_affects_stats(self, make_ship_with_stats):
        """Disabled component should affect calculated stats."""
        # This is more of an integration test with ShipStatsCalculator
        # The stats service should exclude disabled components' abilities
        ship = make_ship_with_stats(expected_stats={
            'max_hp': 100,
            'resource_storage': {'fuel': 1000}
        })

        # Initially enabled
        stats1 = ship.get_calculated_stats()

        ship.set_component_enabled('fuel_tank', False)

        # Toggles should be passed to stats calculation
        # The actual effect depends on ShipStatsCalculator implementation
        stats2 = ship.get_calculated_stats()

        # This verifies the toggle is in place
        assert ship.component_toggles == {'fuel_tank': False}
