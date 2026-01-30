"""
Tests for ShipStatsCalculator - basic functionality and damage effectiveness.

PROJ-48: Split from test_ship_stats_calculator.py
"""

import pytest
from unittest.mock import MagicMock

from .conftest import create_mock_registries, MockComponent, make_design_data


class TestShipStatsCalculatorBasics:
    """Basic functionality tests."""

    def test_empty_design_returns_zeros(self):
        """Empty design should return zero stats."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        design_data = {'layers': {}}
        registries = create_mock_registries()
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data)

        assert stats['max_hp'] == 0
        assert stats['mass'] == 0
        assert stats['resource_storage'].get('fuel', 0) == 0
        assert stats['strategic_movement'] == 0
        assert stats['warp_max_tonnage'] == 0

    def test_undamaged_component_full_effectiveness(self):
        """Undamaged components should have full effectiveness."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('test_comp', mass=100, max_hp=200)
        effectiveness = ShipStatsCalculator.get_component_effectiveness(
            'test_comp', comp, {}
        )

        assert effectiveness == 1.0

    def test_missing_component_skipped(self):
        """Components not in registry should be skipped with warning."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        design_data = make_design_data({'CORE': ['nonexistent_component']})
        registries = create_mock_registries(components={})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data)

        assert stats['max_hp'] == 0
        assert stats['mass'] == 0


class TestDamageEffectiveness:
    """Tests for damage effectiveness calculation."""

    def test_full_hp_full_effectiveness(self):
        """100% HP = 100% effectiveness."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('engine', max_hp=100)
        eff = ShipStatsCalculator.get_component_effectiveness('engine', comp, {})
        assert eff == 1.0

    def test_below_threshold_zero_effectiveness(self):
        """Below 30% HP = 0% effectiveness (inactive)."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('engine', max_hp=100, damage_threshold=0.3)
        # At 25% HP (below 30% threshold)
        eff = ShipStatsCalculator.get_component_effectiveness(
            'engine', comp, {'engine': 25}
        )
        assert eff == 0.0

    def test_at_threshold_zero_effectiveness(self):
        """At exactly 30% HP = 0% effectiveness."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('engine', max_hp=100, damage_threshold=0.3)
        eff = ShipStatsCalculator.get_component_effectiveness(
            'engine', comp, {'engine': 30}
        )
        assert eff == 0.0

    def test_gradual_degradation(self):
        """Between 30% and 100% HP = gradual degradation."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('engine', max_hp=100, damage_threshold=0.3)

        # At 65% HP: (0.65 - 0.3) / (1.0 - 0.3) = 0.35 / 0.7 = 0.5
        eff = ShipStatsCalculator.get_component_effectiveness(
            'engine', comp, {'engine': 65}
        )
        assert abs(eff - 0.5) < 0.01

        # At 100% HP = full
        eff_full = ShipStatsCalculator.get_component_effectiveness(
            'engine', comp, {'engine': 100}
        )
        assert eff_full == 1.0

    def test_armor_never_degrades(self):
        """Armor should always be 100% effective regardless of damage."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        # Test by type
        armor_by_type = MockComponent('armor', max_hp=100, type_str='Armor')
        eff = ShipStatsCalculator.get_component_effectiveness(
            'armor', armor_by_type, {'armor': 1}  # 1% HP
        )
        assert eff == 1.0

        # Test by ability marker
        armor_by_ability = MockComponent(
            'armor2', max_hp=100, type_str='Generic',
            abilities={'Armor': True}
        )
        eff2 = ShipStatsCalculator.get_component_effectiveness(
            'armor2', armor_by_ability, {'armor2': 1}
        )
        assert eff2 == 1.0


class TestStatAggregation:
    """Tests for stat aggregation from components."""

    def test_mass_does_not_degrade(self):
        """Mass should be full regardless of damage."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('heavy_part', mass=500, max_hp=100)
        design_data = make_design_data({'CORE': ['heavy_part']})

        registries = create_mock_registries(components={'heavy_part': comp})
        service = ShipStatsCalculator(registries=registries)

        # Even with damaged component
        stats = service.calculate_stats(
            design_data, {'heavy_part': 1}  # 1% HP
        )

        assert stats['mass'] == 500  # Full mass

    def test_hp_degrades_with_damage(self):
        """HP contribution should degrade with damage."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('hull', mass=100, max_hp=200, damage_threshold=0.3)
        design_data = make_design_data({'CORE': ['hull']})

        registries = create_mock_registries(components={'hull': comp})
        service = ShipStatsCalculator(registries=registries)

        # Full HP
        stats_full = service.calculate_stats(design_data, {})
        assert stats_full['max_hp'] == 200

        # At 130 current HP out of 200 = 65% HP
        # effectiveness = (0.65 - 0.3) / (1.0 - 0.3) = 0.35/0.7 = 0.5
        # HP contribution = 200 * 0.5 = 100
        stats_half = service.calculate_stats(
            design_data, {'hull': 130}  # 130/200 = 65% HP
        )
        assert stats_half['max_hp'] == 100

    def test_strategic_movement_aggregation(self):
        """Strategic movement should sum across engines, degraded by damage."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        design_data = make_design_data({'OUTER': ['engine']})

        registries = create_mock_registries(components={'engine': engine})
        service = ShipStatsCalculator(registries=registries)

        # Full HP
        stats = service.calculate_stats(design_data, {})
        assert stats['strategic_movement'] == 100

        # Damaged (65% HP = 50% effectiveness)
        stats_damaged = service.calculate_stats(
            design_data, {'engine': 65}
        )
        assert abs(stats_damaged['strategic_movement'] - 50) < 1

    def test_fuel_storage_aggregation(self):
        """Fuel storage should sum, degraded by damage."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        tank = MockComponent(
            'fuel_tank', mass=20, max_hp=50,
            abilities={'FuelStorage': 10000}
        )
        design_data = make_design_data({'OUTER': ['fuel_tank']})

        registries = create_mock_registries(components={'fuel_tank': tank})
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(design_data, {})
        assert stats['resource_storage']['fuel'] == 10000

    def test_strategic_fuel_consumption(self):
        """Strategic fuel per hex should sum across engines."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 100, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['engine']})

        registries = create_mock_registries(components={'engine': engine})
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(design_data, {})
        assert stats['resource_consumption_per_hex']['fuel'] == 100


class TestComponentIdMatching:
    """Tests for component ID matching with damage dict."""

    def test_indexed_component_id(self):
        """Should match indexed component IDs (e.g., 'engine_0')."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('engine', max_hp=100)

        # Damage dict uses indexed ID
        current_hp = ShipStatsCalculator._get_current_hp('engine', 100, {'engine_0': 50})
        assert current_hp == 50

    def test_base_id_takes_precedence(self):
        """Base ID should match before indexed forms."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('engine', max_hp=100)

        # Both base and indexed exist - base wins
        current_hp = ShipStatsCalculator._get_current_hp(
            'engine', 100, {'engine': 30, 'engine_0': 50}
        )
        assert current_hp == 30

    def test_no_damage_returns_max_hp(self):
        """No damage entry should return max HP."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        current_hp = ShipStatsCalculator._get_current_hp('engine', 100, {})
        assert current_hp == 100


class TestIntegrationScenarios:
    """Integration tests with realistic ship configurations."""

    def test_escort_with_warp_drive(self):
        """Test escort ship with engine and warp drive."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        bridge = MockComponent(
            'bridge', mass=50, max_hp=200,
            abilities={'CommandAndControl': True}
        )
        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={
                'StrategicMovement': 100,
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 100, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        warp = MockComponent(
            'warp_drive', mass=40, max_hp=60,
            abilities={
                'WarpJump': {'max_tonnage': 2000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 500, 'trigger': 'warp_jump'}]
            }
        )
        tank = MockComponent(
            'fuel_tank', mass=30, max_hp=50,
            abilities={'FuelStorage': 50000}
        )

        design_data = make_design_data({
            'CORE': ['bridge'],
            'OUTER': ['engine', 'warp_drive', 'fuel_tank']
        })

        registries = create_mock_registries(components={
            'bridge': bridge,
            'engine': engine,
            'warp_drive': warp,
            'fuel_tank': tank
        })
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(design_data, {})

        assert stats['mass'] == 50 + 80 + 40 + 30  # 200
        assert stats['max_hp'] == 200 + 100 + 60 + 50  # 410
        assert stats['resource_storage']['fuel'] == 50000
        assert stats['strategic_movement'] == 100
        assert stats['resource_consumption_per_hex']['fuel'] == 100
        assert stats['warp_max_tonnage'] == 2000
        assert stats['warp_resource_costs'].get('energy', 0) == 500

    def test_damaged_escort_loses_warp(self):
        """Escort with damaged warp drive loses warp capability."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        warp = MockComponent(
            'warp_drive', mass=40, max_hp=60,
            abilities={
                'WarpJump': {'max_tonnage': 2000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 500, 'trigger': 'warp_jump'}]
            }
        )

        design_data = make_design_data({'OUTER': ['engine', 'warp_drive']})

        registries = create_mock_registries(components={'engine': engine, 'warp_drive': warp})
        service = ShipStatsCalculator(registries=registries)

        # Warp drive at 99% HP - disabled
        stats = service.calculate_stats(
            design_data, {'warp_drive': 59}  # Just under 100%
        )

        assert stats['warp_max_tonnage'] == 0
        assert stats['warp_resource_costs'].get('energy', 0) == 0
        # Engine still works (100% HP)
        assert stats['strategic_movement'] == 100
