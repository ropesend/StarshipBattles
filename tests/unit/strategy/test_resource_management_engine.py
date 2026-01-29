"""
Unit tests for the ResourceManagementEngine.

Tests per-turn resource consumption and auto-disable functionality.
PROJ-36: Extracted from TurnEngine to handle resource management.
"""

import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from typing import List


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_ship():
    """Create a mock ship with resource consumption capabilities."""
    ship = MagicMock()
    ship.name = "Test Ship"
    ship.is_combat_capable = MagicMock(return_value=True)
    ship.get_all_resource_costs_per_turn = MagicMock(return_value={})
    ship.consume_resource = MagicMock(return_value=True)
    ship.set_component_enabled = MagicMock()
    ship.design_data = {'layers': {}}
    return ship


@pytest.fixture
def mock_fleet(mock_ship):
    """Create a mock fleet with ships."""
    fleet = MagicMock()
    fleet.id = 1
    fleet.ships = [mock_ship]
    return fleet


@pytest.fixture
def mock_empire(mock_fleet):
    """Create a mock empire."""
    empire = MagicMock()
    empire.id = 0
    empire.name = "Test Empire"
    empire.fleets = [mock_fleet]
    return empire


# =============================================================================
# Test: ResourceManagementEngine Initialization
# =============================================================================


class TestResourceManagementEngineInit:
    """Tests for ResourceManagementEngine initialization."""

    def test_engine_can_be_created(self):
        """ResourceManagementEngine can be instantiated."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()

        assert engine is not None

    def test_engine_is_stateless(self):
        """ResourceManagementEngine should be stateless."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()

        # Engine should have no significant state
        # (no instance variables beyond methods)
        assert not hasattr(engine, '_state') or engine._state is None


# =============================================================================
# Test: ResourceDepletion Dataclass
# =============================================================================


class TestResourceDepletion:
    """Tests for ResourceDepletion dataclass."""

    def test_resource_depletion_can_be_created(self):
        """ResourceDepletion can be instantiated."""
        from game.strategy.engine.resource_management_engine import ResourceDepletion

        depletion = ResourceDepletion(
            ship_name="Test Ship",
            resource_type="power",
            components_disabled=["reactor_01"]
        )

        assert depletion.ship_name == "Test Ship"
        assert depletion.resource_type == "power"
        assert depletion.components_disabled == ["reactor_01"]

    def test_resource_depletion_empty_components(self):
        """ResourceDepletion with no components disabled."""
        from game.strategy.engine.resource_management_engine import ResourceDepletion

        depletion = ResourceDepletion(
            ship_name="Test Ship",
            resource_type="fuel",
            components_disabled=[]
        )

        assert depletion.components_disabled == []


# =============================================================================
# Test: Per-Turn Resource Consumption
# =============================================================================


class TestPerTurnResourceConsumption:
    """Tests for process_per_turn_consumption method."""

    def test_consumes_resources_each_tick(self, mock_empire, mock_fleet, mock_ship):
        """Resource consumption happens each tick."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 100.0}
        mock_ship.consume_resource.return_value = True

        engine.process_per_turn_consumption(1, [mock_empire])

        # Should consume 1/100th of per-turn cost
        mock_ship.consume_resource.assert_called_once_with("power", 1.0)

    def test_skips_non_combat_ships(self, mock_empire, mock_fleet, mock_ship):
        """Non-combat capable ships are skipped."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()
        mock_ship.is_combat_capable.return_value = False
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 100.0}

        engine.process_per_turn_consumption(1, [mock_empire])

        mock_ship.consume_resource.assert_not_called()

    def test_spreads_consumption_over_100_ticks(self, mock_empire, mock_fleet, mock_ship):
        """Total consumption spread over 100 ticks equals per-turn cost."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 100.0}
        mock_ship.consume_resource.return_value = True

        # Process all 100 ticks
        for tick in range(1, 101):
            engine.process_per_turn_consumption(tick, [mock_empire])

        # Should have consumed 100 times at 1.0 each = 100.0 total
        assert mock_ship.consume_resource.call_count == 100
        # Each call should be for 1.0 (100.0 / 100 ticks)
        for call in mock_ship.consume_resource.call_args_list:
            assert call[0] == ("power", 1.0)

    def test_skips_zero_cost_resources(self, mock_empire, mock_fleet, mock_ship):
        """Resources with zero cost are skipped."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 0.0}

        engine.process_per_turn_consumption(1, [mock_empire])

        mock_ship.consume_resource.assert_not_called()

    def test_skips_negative_cost_resources(self, mock_empire, mock_fleet, mock_ship):
        """Resources with negative cost are skipped (generators produce, don't consume)."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": -50.0}

        engine.process_per_turn_consumption(1, [mock_empire])

        mock_ship.consume_resource.assert_not_called()

    def test_handles_multiple_resource_types(self, mock_empire, mock_fleet, mock_ship):
        """Multiple resource types are consumed."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()
        mock_ship.get_all_resource_costs_per_turn.return_value = {
            "power": 100.0,
            "fuel": 50.0,
            "ammunition": 25.0
        }
        mock_ship.consume_resource.return_value = True

        engine.process_per_turn_consumption(1, [mock_empire])

        assert mock_ship.consume_resource.call_count == 3
        calls = {call[0][0]: call[0][1] for call in mock_ship.consume_resource.call_args_list}
        assert calls["power"] == 1.0
        assert calls["fuel"] == 0.5
        assert calls["ammunition"] == 0.25


# =============================================================================
# Test: Auto-Disable Components
# =============================================================================


class TestAutoDisableComponents:
    """Tests for auto-disable on resource depletion."""

    def test_auto_disables_on_depletion(self, mock_empire, mock_fleet, mock_ship):
        """Components are disabled when resources deplete."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 100.0}
        mock_ship.consume_resource.return_value = False  # Resource depleted

        with patch.object(engine, '_auto_disable_components_for_resource') as mock_auto_disable:
            engine.process_per_turn_consumption(1, [mock_empire])

            mock_auto_disable.assert_called_once_with(mock_ship, "power")

    def test_finds_components_with_per_turn_trigger(self, mock_ship):
        """Finds components with per_turn ResourceConsumption trigger."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()

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

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get.return_value = mock_comp_def

            engine._auto_disable_components_for_resource(mock_ship, 'power')

            mock_ship.set_component_enabled.assert_called_with('reactor_01', False)

    def test_disables_matching_resource_type(self, mock_ship):
        """Only disables components consuming the depleted resource type."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()

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

        def get_comp(comp_id):
            if comp_id == 'power_comp':
                return mock_power_comp
            return mock_fuel_comp

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get.side_effect = get_comp

            # Deplete power - only power_comp should be disabled
            engine._auto_disable_components_for_resource(mock_ship, 'power')

            # Check that only power_comp was disabled
            calls = mock_ship.set_component_enabled.call_args_list
            assert len(calls) == 1
            assert calls[0][0] == ('power_comp', False)

    def test_handles_list_format_components(self, mock_ship):
        """Handles layer format where components is a simple list."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()

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

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get.return_value = mock_comp_def

            engine._auto_disable_components_for_resource(mock_ship, 'power')

            mock_ship.set_component_enabled.assert_called_with('reactor_01', False)

    def test_handles_string_component_id(self, mock_ship):
        """Handles components specified as strings instead of dicts."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()

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

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get.return_value = mock_comp_def

            engine._auto_disable_components_for_resource(mock_ship, 'power')

            mock_ship.set_component_enabled.assert_called_with('reactor_01', False)

    def test_skips_non_per_turn_triggers(self, mock_ship):
        """Components with non-per_turn triggers are not disabled."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()

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

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get.return_value = mock_comp_def

            engine._auto_disable_components_for_resource(mock_ship, 'power')

            mock_ship.set_component_enabled.assert_not_called()

    def test_handles_missing_component_definition(self, mock_ship):
        """Gracefully handles components not found in registry."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()

        mock_ship.design_data = {
            'layers': {
                'core': [{'id': 'unknown_component'}]
            }
        }

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get.return_value = None

            # Should not raise an error
            engine._auto_disable_components_for_resource(mock_ship, 'power')

            mock_ship.set_component_enabled.assert_not_called()

    def test_handles_empty_abilities(self, mock_ship):
        """Handles components with empty or missing abilities."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()

        mock_comp_def = MagicMock()
        mock_comp_def.abilities = {}  # Empty abilities

        mock_ship.design_data = {
            'layers': {
                'core': [{'id': 'passive_component'}]
            }
        }

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get.return_value = mock_comp_def

            engine._auto_disable_components_for_resource(mock_ship, 'power')

            mock_ship.set_component_enabled.assert_not_called()


# =============================================================================
# Test: Edge Cases and Robustness
# =============================================================================


class TestResourceManagementEdgeCases:
    """Tests for edge cases in resource management."""

    def test_resource_depletion_cascade(self, mock_empire, mock_fleet, mock_ship):
        """Multiple resources deplete in the same tick."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()
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
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()

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

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get.return_value = mock_comp_def

            # Call twice - should not raise error
            engine._auto_disable_components_for_resource(mock_ship, 'power')
            engine._auto_disable_components_for_resource(mock_ship, 'power')

            assert mock_ship.set_component_enabled.call_count == 2

    def test_rounding_check_100_ticks(self, mock_empire, mock_fleet, mock_ship):
        """Verify no phantom resource loss over 100 ticks due to rounding."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 33.33}  # Awkward division
        mock_ship.consume_resource.return_value = True

        total_consumed = 0.0
        for tick in range(1, 101):
            engine.process_per_turn_consumption(tick, [mock_empire])
            # Each tick consumes 33.33 / 100 = 0.3333
            total_consumed += 0.3333

        # Total should be close to 33.33 (allow small floating point error)
        assert abs(total_consumed - 33.33) < 0.01

    def test_empty_fleets_list(self, mock_empire):
        """Handles empire with no fleets."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()
        mock_empire.fleets = []

        # Should not raise error
        result = engine.process_per_turn_consumption(1, [mock_empire])

        assert result == []

    def test_empty_ships_list(self, mock_empire, mock_fleet):
        """Handles fleet with no ships."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()
        mock_fleet.ships = []
        mock_empire.fleets = [mock_fleet]

        # Should not raise error
        result = engine.process_per_turn_consumption(1, [mock_empire])

        assert result == []

    def test_returns_depletion_list(self, mock_empire, mock_fleet, mock_ship):
        """Returns list of ResourceDepletion objects."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine, ResourceDepletion

        engine = ResourceManagementEngine()
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

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get.return_value = mock_comp_def

            result = engine.process_per_turn_consumption(1, [mock_empire])

            assert len(result) == 1
            assert isinstance(result[0], ResourceDepletion)
            assert result[0].ship_name == "USS Test"
            assert result[0].resource_type == "power"
            assert "reactor_01" in result[0].components_disabled
