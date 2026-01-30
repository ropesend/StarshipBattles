"""
Tests for ShipStatsCalculator - warp capability tests.

PROJ-48: Split from test_ship_stats_calculator.py
"""

import pytest
from unittest.mock import MagicMock

from .conftest import create_mock_registries, MockComponent, make_design_data


class TestWarpCapability:
    """Tests for warp drive special handling."""

    def test_warp_requires_full_hp(self):
        """Warp drives must be at 100% HP to function."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent(
            'warp_drive', max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 5000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 500, 'trigger': 'warp_jump'}]
            }
        )

        # Full HP - warp works
        eff = ShipStatsCalculator._get_warp_effectiveness('warp_drive', comp, {})
        assert eff == 1.0

        # 99% HP - warp disabled
        eff_damaged = ShipStatsCalculator._get_warp_effectiveness(
            'warp_drive', comp, {'warp_drive': 99}
        )
        assert eff_damaged == 0.0

    def test_damaged_warp_drive_zero_tonnage(self):
        """Damaged warp drive should contribute 0 to warp_max_tonnage."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        warp_comp = MockComponent(
            'warp_drive', max_hp=100, mass=50,
            abilities={
                'WarpJump': {'max_tonnage': 5000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 500, 'trigger': 'warp_jump'}]
            }
        )

        design_data = make_design_data({'OUTER': ['warp_drive']})

        registries = create_mock_registries(components={'warp_drive': warp_comp})
        service = ShipStatsCalculator(registries=registries)

        # Undamaged - has warp capability
        stats_ok = service.calculate_stats(design_data, {})
        assert stats_ok['warp_max_tonnage'] == 5000
        assert stats_ok['warp_resource_costs'].get('energy', 0) == 500

        # Damaged - no warp capability
        stats_damaged = service.calculate_stats(
            design_data, {'warp_drive': 99}
        )
        assert stats_damaged['warp_max_tonnage'] == 0
        assert stats_damaged['warp_resource_costs'].get('energy', 0) == 0

    def test_multiple_warp_drives_largest_tonnage(self):
        """With multiple warp drives, use largest tonnage."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        warp1 = MockComponent(
            'warp_small', max_hp=100, mass=30,
            abilities={
                'WarpJump': {'max_tonnage': 2000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 200, 'trigger': 'warp_jump'}]
            }
        )
        warp2 = MockComponent(
            'warp_large', max_hp=100, mass=60,
            abilities={
                'WarpJump': {'max_tonnage': 10000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 800, 'trigger': 'warp_jump'}]
            }
        )

        design_data = make_design_data({'OUTER': ['warp_small', 'warp_large']})

        registries = create_mock_registries(components={'warp_small': warp1, 'warp_large': warp2})
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(design_data, {})

        # Tonnage = max of drives (10000)
        assert stats['warp_max_tonnage'] == 10000
        # Energy = sum of drives (200 + 800)
        assert stats['warp_resource_costs'].get('energy', 0) == 1000

    def test_one_damaged_warp_drive_reduces_capability(self):
        """If one of two warp drives is damaged, only undamaged contributes."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        warp1 = MockComponent(
            'warp_small', max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 2000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 200, 'trigger': 'warp_jump'}]
            }
        )
        warp2 = MockComponent(
            'warp_large', max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 10000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 800, 'trigger': 'warp_jump'}]
            }
        )

        design_data = make_design_data({'OUTER': ['warp_small', 'warp_large']})

        registries = create_mock_registries(components={'warp_small': warp1, 'warp_large': warp2})
        service = ShipStatsCalculator(registries=registries)

        # Large warp damaged - only small works
        stats = service.calculate_stats(
            design_data, {'warp_large': 99}
        )

        assert stats['warp_max_tonnage'] == 2000
        assert stats['warp_resource_costs'].get('energy', 0) == 200


class TestHasWarpCapability:
    """
    Tests for has_warp_capability function in ShipStatsCalculator.

    PROJ-11 Phase 3: This function was moved from game.ui.screens.fleet_report_filters
    to game.strategy.services.ship_stats_calculator to eliminate strategy->UI dependency.

    A ship is warp-capable if:
    1. warp_max_tonnage >= ship's mass
    2. warp drive is undamaged (100% HP)
    3. Ship has enough resource storage capacity for at least one warp jump
    """

    def test_ship_without_warp_drive_not_capable(self):
        """Ship without warp drive should not be warp capable."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 0,  # No warp drive
            'warp_resource_costs': {'energy': 0, 'fuel': 0},
            'resource_storage': {'energy': 500, 'fuel': 5000},
        }

        result = ShipStatsCalculator.has_warp_capability(ship)
        assert result is False

    def test_ship_with_sufficient_warp_drive_capable(self):
        """Ship with warp drive exceeding mass should be warp capable."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 1500,  # Exceeds mass
            'warp_resource_costs': {'energy': 500, 'fuel': 0},
            'resource_storage': {'energy': 1000, 'fuel': 5000},  # Enough for warp
        }

        result = ShipStatsCalculator.has_warp_capability(ship)
        assert result is True

    def test_ship_with_equal_warp_tonnage_capable(self):
        """Ship with warp tonnage equal to mass should be warp capable."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 1000,  # Exactly equal
            'warp_resource_costs': {'energy': 500, 'fuel': 0},
            'resource_storage': {'energy': 1000, 'fuel': 5000},
        }

        result = ShipStatsCalculator.has_warp_capability(ship)
        assert result is True

    def test_ship_with_insufficient_warp_tonnage_not_capable(self):
        """Ship with warp tonnage less than mass should not be warp capable."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 500,  # Less than mass
            'warp_resource_costs': {'energy': 500, 'fuel': 0},
            'resource_storage': {'energy': 1000, 'fuel': 5000},
        }

        result = ShipStatsCalculator.has_warp_capability(ship)
        assert result is False

    def test_ship_with_zero_mass_not_capable(self):
        """Ship with zero mass should not be warp capable (edge case)."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 0,  # Zero mass
            'warp_max_tonnage': 1000,
            'warp_resource_costs': {'energy': 500, 'fuel': 0},
            'resource_storage': {'energy': 1000, 'fuel': 5000},
        }

        result = ShipStatsCalculator.has_warp_capability(ship)
        assert result is False

    def test_insufficient_energy_storage_not_capable(self):
        """Ship with insufficient energy storage for warp should not be capable."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 1500,
            'warp_resource_costs': {'energy': 500, 'fuel': 0},  # Needs 500 energy
            'resource_storage': {'energy': 300, 'fuel': 5000},  # Only has 300 energy capacity
        }

        result = ShipStatsCalculator.has_warp_capability(ship)
        assert result is False

    def test_insufficient_fuel_storage_not_capable(self):
        """Ship with insufficient fuel storage for warp should not be capable."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 1500,
            'warp_resource_costs': {'energy': 0, 'fuel': 1000},  # Needs 1000 fuel
            'resource_storage': {'energy': 500, 'fuel': 500},  # Only has 500 fuel capacity
        }

        result = ShipStatsCalculator.has_warp_capability(ship)
        assert result is False

    def test_exactly_sufficient_storage_capable(self):
        """Ship with exactly enough storage for warp should be capable."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 1500,
            'warp_resource_costs': {'energy': 500, 'fuel': 200},
            'resource_storage': {'energy': 500, 'fuel': 200},  # Exactly enough
        }

        result = ShipStatsCalculator.has_warp_capability(ship)
        assert result is True

    def test_no_warp_cost_no_storage_check(self):
        """If warp has no resource cost, storage check should pass."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 1500,
            'warp_resource_costs': {'energy': 0, 'fuel': 0},  # No resource costs
            'resource_storage': {'energy': 0, 'fuel': 0},  # No storage
        }

        result = ShipStatsCalculator.has_warp_capability(ship)
        assert result is True

    def test_damaged_warp_drive_returns_zero_tonnage(self):
        """
        When warp drive is damaged, warp_max_tonnage from get_calculated_stats
        should already be 0 (handled by ShipStatsCalculator.calculate_stats).
        """
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 0,  # Damaged warp drive = 0 tonnage
            'warp_resource_costs': {'energy': 0, 'fuel': 0},
            'resource_storage': {'energy': 1000, 'fuel': 5000},
        }

        result = ShipStatsCalculator.has_warp_capability(ship)
        assert result is False

    def test_multiple_resource_requirements_all_must_be_met(self):
        """If warp costs both energy and fuel, ship must have enough of both."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 1500,
            'warp_resource_costs': {'energy': 500, 'fuel': 1000},
            'resource_storage': {'energy': 600, 'fuel': 500},  # Enough energy but NOT enough fuel
        }

        result = ShipStatsCalculator.has_warp_capability(ship)
        assert result is False

    def test_missing_stats_default_to_zero(self):
        """Missing stats should default to zero without crashing."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            # Missing warp_max_tonnage - should default to 0
        }

        result = ShipStatsCalculator.has_warp_capability(ship)
        assert result is False  # No warp capability without warp_max_tonnage
