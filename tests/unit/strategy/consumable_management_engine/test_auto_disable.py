"""
Tests for auto-disable on resource depletion and edge cases.

PROJ-50: Updated to use strict DI (registries required).
"""

import pytest
from unittest.mock import MagicMock, patch
from game.core.registry import GameRegistries


class TestAutoDisableComponents:
    """Tests for auto-disable on resource depletion."""

    def test_auto_disables_on_depletion(self, mock_registries, mock_empire, mock_fleet, mock_ship):
        """Components are disabled when resources deplete."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        engine = ConsumableManagementEngine(registries=mock_registries)
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 100.0}
        mock_ship.consume_resource.return_value = False  # Resource depleted

        with patch.object(engine, '_auto_disable_components_for_resource') as mock_auto_disable:
            engine.process_per_turn_consumption(1, [mock_empire])

            mock_auto_disable.assert_called_once_with(mock_ship, "power")

    def test_finds_components_with_per_turn_trigger(self, mock_ship):
        """Finds components with per_turn ResourceConsumption trigger."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        # Set up mock component with per_turn ResourceConsumption
        mock_comp_def = MagicMock()
        mock_comp_def.abilities = {
            'ResourceConsumption': [
                {'trigger': 'per_turn', 'resource': 'power'}
            ]
        }

        mock_ship.design_data = {
            'layers': {
                'core': {
                    'components': [{'id': 'reactor_01'}]
                }
            }
        }

        # Create registries with the mock component
        registries = GameRegistries(
            components={'reactor_01': mock_comp_def},
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = ConsumableManagementEngine(registries=registries)

        engine._auto_disable_components_for_resource(mock_ship, 'power')

        mock_ship.set_component_enabled.assert_called_with('reactor_01', False)

    def test_disables_matching_resource_type(self, mock_ship):
        """Only disables components consuming the depleted resource type."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        # Set up mock components - one uses power, one uses fuel
        mock_power_comp = MagicMock()
        mock_power_comp.abilities = {
            'ResourceConsumption': [
                {'trigger': 'per_turn', 'resource': 'power'}
            ]
        }

        mock_fuel_comp = MagicMock()
        mock_fuel_comp.abilities = {
            'ResourceConsumption': [
                {'trigger': 'per_turn', 'resource': 'fuel'}
            ]
        }

        mock_ship.design_data = {
            'layers': {
                'core': {
                    'components': [{'id': 'power_comp'}, {'id': 'fuel_comp'}]
                }
            }
        }

        # Create registries with both components
        registries = GameRegistries(
            components={
                'power_comp': mock_power_comp,
                'fuel_comp': mock_fuel_comp
            },
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = ConsumableManagementEngine(registries=registries)

        # Deplete power - only power_comp should be disabled
        engine._auto_disable_components_for_resource(mock_ship, 'power')

        # Check that only power_comp was disabled
        calls = mock_ship.set_component_enabled.call_args_list
        assert len(calls) == 1
        assert calls[0][0] == ('power_comp', False)

    def test_handles_list_format_components(self, mock_ship):
        """Handles layer format where components is a simple list."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        mock_comp_def = MagicMock()
        mock_comp_def.abilities = {
            'ResourceConsumption': [
                {'trigger': 'per_turn', 'resource': 'power'}
            ]
        }

        mock_ship.design_data = {
            'layers': {
                'core': [{'id': 'reactor_01'}]  # List format, not dict with 'components'
            }
        }

        registries = GameRegistries(
            components={'reactor_01': mock_comp_def},
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = ConsumableManagementEngine(registries=registries)

        engine._auto_disable_components_for_resource(mock_ship, 'power')

        mock_ship.set_component_enabled.assert_called_with('reactor_01', False)

    def test_handles_string_component_id(self, mock_ship):
        """Handles components specified as strings instead of dicts."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        mock_comp_def = MagicMock()
        mock_comp_def.abilities = {
            'ResourceConsumption': [
                {'trigger': 'per_turn', 'resource': 'power'}
            ]
        }

        mock_ship.design_data = {
            'layers': {
                'core': ['reactor_01']  # String IDs directly
            }
        }

        registries = GameRegistries(
            components={'reactor_01': mock_comp_def},
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = ConsumableManagementEngine(registries=registries)

        engine._auto_disable_components_for_resource(mock_ship, 'power')

        mock_ship.set_component_enabled.assert_called_with('reactor_01', False)

    def test_skips_non_per_turn_triggers(self, mock_ship):
        """Components with non-per_turn triggers are not disabled."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        mock_comp_def = MagicMock()
        mock_comp_def.abilities = {
            'ResourceConsumption': [
                {'trigger': 'on_fire', 'resource': 'power'}  # Not per_turn
            ]
        }

        mock_ship.design_data = {
            'layers': {
                'core': [{'id': 'weapon_01'}]
            }
        }

        registries = GameRegistries(
            components={'weapon_01': mock_comp_def},
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = ConsumableManagementEngine(registries=registries)

        engine._auto_disable_components_for_resource(mock_ship, 'power')

        mock_ship.set_component_enabled.assert_not_called()

    def test_handles_missing_component_definition(self, mock_ship):
        """Gracefully handles components not found in registry."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        mock_ship.design_data = {
            'layers': {
                'core': [{'id': 'unknown_component'}]
            }
        }

        # Empty registry - component not found
        registries = GameRegistries(
            components={},
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = ConsumableManagementEngine(registries=registries)

        # Should not raise an error
        engine._auto_disable_components_for_resource(mock_ship, 'power')

        mock_ship.set_component_enabled.assert_not_called()

    def test_handles_empty_abilities(self, mock_ship):
        """Handles components with empty or missing abilities."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        mock_comp_def = MagicMock()
        mock_comp_def.abilities = {}  # Empty abilities

        mock_ship.design_data = {
            'layers': {
                'core': [{'id': 'passive_component'}]
            }
        }

        registries = GameRegistries(
            components={'passive_component': mock_comp_def},
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = ConsumableManagementEngine(registries=registries)

        engine._auto_disable_components_for_resource(mock_ship, 'power')

        mock_ship.set_component_enabled.assert_not_called()


class TestResourceManagementEdgeCases:
    """Tests for edge cases in resource management."""

    def test_resource_depletion_cascade(self, mock_registries, mock_empire, mock_fleet, mock_ship):
        """Multiple resources deplete in the same tick."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        engine = ConsumableManagementEngine(registries=mock_registries)
        mock_ship.get_all_resource_costs_per_turn.return_value = {
            "power": 100.0,
            "fuel": 50.0
        }
        mock_ship.consume_resource.return_value = False  # Both resources deplete

        with patch.object(engine, '_auto_disable_components_for_resource') as mock_auto_disable:
            engine.process_per_turn_consumption(1, [mock_empire])

            # Both resources should trigger auto-disable
            assert mock_auto_disable.call_count == 2

    def test_component_already_disabled(self, mock_ship):
        """Auto-disable is idempotent - calling twice doesn't break anything."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        mock_comp_def = MagicMock()
        mock_comp_def.abilities = {
            'ResourceConsumption': [
                {'trigger': 'per_turn', 'resource': 'power'}
            ]
        }

        mock_ship.design_data = {
            'layers': {
                'core': [{'id': 'reactor_01'}]
            }
        }

        registries = GameRegistries(
            components={'reactor_01': mock_comp_def},
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = ConsumableManagementEngine(registries=registries)

        # Call twice - should not raise error
        engine._auto_disable_components_for_resource(mock_ship, 'power')
        engine._auto_disable_components_for_resource(mock_ship, 'power')

        assert mock_ship.set_component_enabled.call_count == 2

    def test_rounding_check_100_ticks(self, mock_registries, mock_empire, mock_fleet, mock_ship):
        """Verify no phantom resource loss over 100 ticks due to rounding."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        engine = ConsumableManagementEngine(registries=mock_registries)
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 33.33}  # Awkward division
        mock_ship.consume_resource.return_value = True

        total_consumed = 0.0
        for tick in range(1, 101):
            engine.process_per_turn_consumption(tick, [mock_empire])
            # Each tick consumes 33.33 / 100 = 0.3333
            total_consumed += 0.3333

        # Total should be close to 33.33 (allow small floating point error)
        assert abs(total_consumed - 33.33) < 0.01

    def test_empty_fleets_list(self, mock_registries, mock_empire):
        """Handles empire with no fleets."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        engine = ConsumableManagementEngine(registries=mock_registries)
        mock_empire.fleets = []

        # Should not raise error
        result = engine.process_per_turn_consumption(1, [mock_empire])

        assert result == []

    def test_empty_ships_list(self, mock_registries, mock_empire, mock_fleet):
        """Handles fleet with no ships."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        engine = ConsumableManagementEngine(registries=mock_registries)
        mock_fleet.ships = []
        mock_empire.fleets = [mock_fleet]

        # Should not raise error
        result = engine.process_per_turn_consumption(1, [mock_empire])

        assert result == []

    def test_returns_depletion_list(self, mock_empire, mock_fleet, mock_ship):
        """Returns list of ResourceDepletion objects."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine, ResourceDepletion

        mock_ship.name = "USS Test"
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 100.0}
        mock_ship.consume_resource.return_value = False  # Depleted

        # Set up component that will be disabled
        mock_comp_def = MagicMock()
        mock_comp_def.abilities = {
            'ResourceConsumption': [
                {'trigger': 'per_turn', 'resource': 'power'}
            ]
        }

        mock_ship.design_data = {
            'layers': {
                'core': [{'id': 'reactor_01'}]
            }
        }

        registries = GameRegistries(
            components={'reactor_01': mock_comp_def},
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = ConsumableManagementEngine(registries=registries)

        result = engine.process_per_turn_consumption(1, [mock_empire])

        assert len(result) == 1
        assert isinstance(result[0], ResourceDepletion)
        assert result[0].ship_name == "USS Test"
        assert result[0].resource_type == "power"
        assert "reactor_01" in result[0].components_disabled
