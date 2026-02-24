# -*- coding: utf-8 -*-
"""Edge case tests for ShipStatsCalculator.

Tests cover:
- Constructor validation (registries required)
- Formula evaluation edge cases
- Empty/None ability data
- has_warp_capability edge cases
- Fallback to expected_stats
- Zero/negative HP components
- Multiple resource types
"""

import pytest
from unittest.mock import MagicMock, PropertyMock

from game.core.exceptions import ValidationException
from .conftest import create_mock_registries, MockComponent, make_design_data


class TestConstructorValidation:
    """Tests for constructor parameter validation."""

    def test_registries_required(self):
        """Should raise ValidationException if registries is None."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        with pytest.raises(ValidationException, match="registries is required"):
            ShipStatsCalculator(registries=None)

    def test_valid_registries_accepted(self):
        """Should accept valid registries without error."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        registries = create_mock_registries()
        service = ShipStatsCalculator(registries=registries)
        assert service is not None


class TestFormulaEvaluation:
    """Tests for formula evaluation edge cases."""

    def test_evaluate_value_with_none(self):
        """None value should return default."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        result = ShipStatsCalculator._evaluate_value(None, 42.0, {})
        assert result == 42.0

    def test_evaluate_value_numeric(self):
        """Numeric value should be returned as float."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        result_int = ShipStatsCalculator._evaluate_value(100, 0.0, {})
        assert result_int == 100.0

        result_float = ShipStatsCalculator._evaluate_value(3.14, 0.0, {})
        assert result_float == 3.14

    def test_evaluate_value_formula_with_context(self):
        """Formula string should be evaluated with context."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        context = {'ship_class_mass': 2000}
        result = ShipStatsCalculator._evaluate_value("=ship_class_mass * 2", 0.0, context)
        assert result == 4000.0

    def test_evaluate_value_formula_without_context(self):
        """Formula string without context should return default."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        result = ShipStatsCalculator._evaluate_value("=ship_class_mass * 2", 99.0, None)
        assert result == 99.0

    def test_evaluate_value_non_formula_string(self):
        """Non-formula string should return default."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        result = ShipStatsCalculator._evaluate_value("not_a_formula", 50.0, {'x': 1})
        assert result == 50.0


class TestGetAbilityList:
    """Tests for _get_ability_list helper."""

    def test_ability_not_present(self):
        """Missing ability should return empty list."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        result = ShipStatsCalculator._get_ability_list({}, 'NonExistent')
        assert result == []

    def test_ability_as_list(self):
        """List ability should be returned as-is."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        abilities = {'ResourceStorage': [{'resource': 'fuel', 'amount': 100}]}
        result = ShipStatsCalculator._get_ability_list(abilities, 'ResourceStorage')
        assert result == [{'resource': 'fuel', 'amount': 100}]

    def test_ability_as_dict(self):
        """Dict ability should be wrapped in list."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        abilities = {'ResourceStorage': {'resource': 'fuel', 'amount': 100}}
        result = ShipStatsCalculator._get_ability_list(abilities, 'ResourceStorage')
        assert result == [{'resource': 'fuel', 'amount': 100}]

    def test_ability_as_simple_value(self):
        """Simple value should be wrapped in dict and list."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        abilities = {'StrategicMovement': 50}
        result = ShipStatsCalculator._get_ability_list(abilities, 'StrategicMovement')
        assert result == [{'value': 50}]


class TestGetAbilityValue:
    """Tests for _get_ability_value helper."""

    def test_missing_ability(self):
        """Missing ability should return 0."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        result = ShipStatsCalculator._get_ability_value({}, 'NonExistent')
        assert result == 0.0

    def test_numeric_ability(self):
        """Numeric ability value should be returned as float."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        result = ShipStatsCalculator._get_ability_value({'StrategicMovement': 100}, 'StrategicMovement')
        assert result == 100.0

    def test_dict_ability_with_value_key(self):
        """Dict ability with 'value' key should extract it."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        abilities = {'StrategicMovement': {'value': 75, 'other': 'ignored'}}
        result = ShipStatsCalculator._get_ability_value(abilities, 'StrategicMovement')
        assert result == 75.0

    def test_dict_ability_with_amount_key(self):
        """Dict ability with 'amount' key should extract it."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        abilities = {'ResourceStorage': {'amount': 5000}}
        result = ShipStatsCalculator._get_ability_value(abilities, 'ResourceStorage')
        assert result == 5000.0

    def test_dict_ability_with_movement_points_key(self):
        """Dict ability with 'movement_points' key should extract it."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        abilities = {'StrategicMovement': {'movement_points': 120}}
        result = ShipStatsCalculator._get_ability_value(abilities, 'StrategicMovement')
        assert result == 120.0

    def test_dict_ability_no_recognized_key(self):
        """Dict ability without recognized key should return 0."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        abilities = {'Something': {'unknown_key': 999}}
        result = ShipStatsCalculator._get_ability_value(abilities, 'Something')
        assert result == 0.0


class TestFallbackToExpectedStats:
    """Tests for fallback to expected_stats when no components found."""

    def test_fallback_when_no_layers(self):
        """Should use expected_stats when design has no layers."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        design_data = {
            'layers': {},
            'expected_stats': {
                'max_hp': 500,
                'mass': 1000,
                'strategic_movement': 50,
                'warp_max_tonnage': 3000,
            }
        }
        registries = create_mock_registries()
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(design_data)

        assert stats['max_hp'] == 500
        assert stats['mass'] == 1000
        assert stats['strategic_movement'] == 50
        assert stats['warp_max_tonnage'] == 3000

    def test_fallback_when_all_components_missing(self):
        """Should use expected_stats when all components missing from registry."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        design_data = {
            'layers': {'CORE': [{'id': 'nonexistent'}]},
            'expected_stats': {'max_hp': 999}
        }
        registries = create_mock_registries(components={})
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(design_data)
        assert stats['max_hp'] == 999


class TestZeroHPComponents:
    """Tests for components with zero or no HP."""

    def test_zero_max_hp_always_effective(self):
        """Component with 0 max HP should always be 100% effective."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('sensor', max_hp=0)
        eff = ShipStatsCalculator.get_component_effectiveness('sensor', comp, {})
        assert eff == 1.0

    def test_negative_max_hp_always_effective(self):
        """Component with negative max HP should always be 100% effective."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('weird', max_hp=-100)
        eff = ShipStatsCalculator.get_component_effectiveness('weird', comp, {})
        assert eff == 1.0


class TestWarpEffectiveness:
    """Tests for warp drive effectiveness."""

    def test_warp_full_hp_functional(self):
        """Warp drive at full HP should be functional."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('warp', max_hp=100)
        eff = ShipStatsCalculator._get_warp_effectiveness('warp', comp, {'warp': 100})
        assert eff == 1.0

    def test_warp_undamaged_functional(self):
        """Warp drive not in damage dict should be functional."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('warp', max_hp=100)
        eff = ShipStatsCalculator._get_warp_effectiveness('warp', comp, {})
        assert eff == 1.0

    def test_warp_any_damage_disabled(self):
        """Warp drive with any damage should be disabled."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('warp', max_hp=100)
        eff = ShipStatsCalculator._get_warp_effectiveness('warp', comp, {'warp': 99})
        assert eff == 0.0

    def test_warp_no_hp_tracked_always_works(self):
        """Warp drive with 0 max HP should always work."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent('warp', max_hp=0)
        eff = ShipStatsCalculator._get_warp_effectiveness('warp', comp, {})
        assert eff == 1.0


class TestHasWarpCapability:
    """Tests for has_warp_capability static method."""

    def test_no_mass_returns_false(self):
        """Ship with zero mass should not have warp capability."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 0,
            'warp_max_tonnage': 5000,
        }

        assert ShipStatsCalculator.has_warp_capability(ship) is False

    def test_no_warp_drive_returns_false(self):
        """Ship without warp drive should not have warp capability."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 0,
        }

        assert ShipStatsCalculator.has_warp_capability(ship) is False

    def test_warp_tonnage_too_low_returns_false(self):
        """Ship heavier than warp drive capacity should not have warp capability."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 5000,
            'warp_max_tonnage': 2000,  # Can't warp this ship
        }

        assert ShipStatsCalculator.has_warp_capability(ship) is False

    def test_warp_with_sufficient_tonnage(self):
        """Ship within warp drive capacity should have warp capability."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1500,
            'warp_max_tonnage': 2000,
            'warp_resource_costs': {},
            'resource_storage': {},
        }

        assert ShipStatsCalculator.has_warp_capability(ship) is True

    def test_warp_insufficient_energy_storage(self):
        """Ship with insufficient energy storage should not have warp capability."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
        from game.core.constants import ResourceType

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 2000,
            'warp_resource_costs': {ResourceType.ENERGY: 500},
            'resource_storage': {ResourceType.ENERGY: 100},  # Not enough
        }

        assert ShipStatsCalculator.has_warp_capability(ship) is False

    def test_warp_insufficient_fuel_storage(self):
        """Ship with insufficient fuel storage should not have warp capability."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
        from game.core.constants import ResourceType

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 2000,
            'warp_resource_costs': {ResourceType.FUEL: 1000},
            'resource_storage': {ResourceType.FUEL: 500},  # Not enough
        }

        assert ShipStatsCalculator.has_warp_capability(ship) is False

    def test_warp_sufficient_storage(self):
        """Ship with sufficient resource storage should have warp capability."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
        from game.core.constants import ResourceType

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 2000,
            'warp_resource_costs': {ResourceType.ENERGY: 500, ResourceType.FUEL: 200},
            'resource_storage': {ResourceType.ENERGY: 600, ResourceType.FUEL: 300},
        }

        assert ShipStatsCalculator.has_warp_capability(ship) is True


class TestComponentToggles:
    """Tests for component toggles."""

    def test_toggled_off_component_skipped_for_abilities(self):
        """Toggled off component should not contribute abilities."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        design_data = make_design_data({'OUTER': ['engine']})

        registries = create_mock_registries(components={'engine': engine})
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(
            design_data,
            component_damage={},
            component_toggles={'engine': False}  # Toggled off
        )

        assert stats['strategic_movement'] == 0  # No movement from disabled engine
        assert stats['mass'] == 80  # But mass is still counted

    def test_toggled_on_component_contributes(self):
        """Toggled on component should contribute abilities."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        design_data = make_design_data({'OUTER': ['engine']})

        registries = create_mock_registries(components={'engine': engine})
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(
            design_data,
            component_damage={},
            component_toggles={'engine': True}
        )

        assert stats['strategic_movement'] == 100


class TestMultipleResourceTypes:
    """Tests for multiple resource types."""

    def test_multiple_resource_storage_types(self):
        """Multiple resource storage abilities should all be tracked."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        multi_tank = MockComponent(
            'multi_tank', mass=50, max_hp=100,
            abilities={
                'ResourceStorage': [
                    {'resource': 'fuel', 'amount': 5000},
                    {'resource': 'energy', 'amount': 1000},
                    {'resource': 'ammo', 'amount': 200},
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['multi_tank']})

        registries = create_mock_registries(components={'multi_tank': multi_tank})
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(design_data)

        assert stats['resource_storage']['fuel'] == 5000
        assert stats['resource_storage']['energy'] == 1000
        assert stats['resource_storage']['ammo'] == 200

    def test_multiple_consumption_triggers(self):
        """Multiple consumption triggers should be tracked separately."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        complex_engine = MockComponent(
            'complex_engine', mass=100, max_hp=150,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 50, 'trigger': 'strategic_per_hex'},
                    {'resource': 'energy', 'amount': 10, 'trigger': 'per_turn'},
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['complex_engine']})

        registries = create_mock_registries(components={'complex_engine': complex_engine})
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(design_data)

        assert stats['resource_consumption_per_hex']['fuel'] == 50
        assert stats['resource_consumption_per_turn']['energy'] == 10


class TestCargoStorage:
    """Tests for cargo storage abilities."""

    def test_cargo_storage_aggregation(self):
        """Cargo storage should be tracked by cargo type."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        cargo_hold = MockComponent(
            'cargo_hold', mass=30, max_hp=50,
            abilities={
                'CargoStorage': [
                    {'cargo_type': 'passengers', 'capacity': 100},
                    {'cargo_type': 'generic', 'capacity': 500},
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['cargo_hold']})

        registries = create_mock_registries(components={'cargo_hold': cargo_hold})
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(design_data)

        assert stats['cargo_storage']['passengers'] == 100
        assert stats['cargo_storage']['generic'] == 500

    def test_cargo_storage_degrades_with_damage(self):
        """Cargo storage should degrade with damage."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        # MockComponent default damage_threshold is 0.3
        # With threshold 0.3: At 65% HP = (0.65 - 0.3) / (1.0 - 0.3) = 0.5 effectiveness
        cargo_hold = MockComponent(
            'cargo_hold', mass=30, max_hp=100, damage_threshold=0.3,
            abilities={
                'CargoStorage': [{'cargo_type': 'generic', 'capacity': 1000}]
            }
        )
        design_data = make_design_data({'OUTER': ['cargo_hold']})

        registries = create_mock_registries(components={'cargo_hold': cargo_hold})
        service = ShipStatsCalculator(registries=registries)

        # At 65% HP with 0.3 threshold:
        # effectiveness = (0.65 - 0.3) / (1.0 - 0.3) = 0.35 / 0.7 = 0.5
        stats = service.calculate_stats(
            design_data,
            component_damage={'cargo_hold': 65}
        )

        # 1000 * 0.5 = 500 (use approx for floating point)
        assert stats['cargo_storage']['generic'] == pytest.approx(500, rel=0.001)
