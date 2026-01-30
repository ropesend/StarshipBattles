"""
Tests for per-turn resource consumption.

PROJ-50: Updated to use strict DI (registries required).
"""

import pytest
from unittest.mock import patch


class TestPerTurnResourceConsumption:
    """Tests for process_per_turn_consumption method."""

    def test_consumes_resources_each_tick(self, mock_registries, mock_empire, mock_fleet, mock_ship):
        """Resource consumption happens each tick."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine(registries=mock_registries)
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 100.0}
        mock_ship.consume_resource.return_value = True

        engine.process_per_turn_consumption(1, [mock_empire])

        # Should consume 1/100th of per-turn cost
        mock_ship.consume_resource.assert_called_once_with("power", 1.0)

    def test_skips_non_combat_ships(self, mock_registries, mock_empire, mock_fleet, mock_ship):
        """Non-combat capable ships are skipped."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine(registries=mock_registries)
        mock_ship.is_combat_capable.return_value = False
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 100.0}

        engine.process_per_turn_consumption(1, [mock_empire])

        mock_ship.consume_resource.assert_not_called()

    def test_spreads_consumption_over_100_ticks(self, mock_registries, mock_empire, mock_fleet, mock_ship):
        """Total consumption spread over 100 ticks equals per-turn cost."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine(registries=mock_registries)
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

    def test_skips_zero_cost_resources(self, mock_registries, mock_empire, mock_fleet, mock_ship):
        """Resources with zero cost are skipped."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine(registries=mock_registries)
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 0.0}

        engine.process_per_turn_consumption(1, [mock_empire])

        mock_ship.consume_resource.assert_not_called()

    def test_skips_negative_cost_resources(self, mock_registries, mock_empire, mock_fleet, mock_ship):
        """Resources with negative cost are skipped (generators produce, don't consume)."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine(registries=mock_registries)
        mock_ship.get_all_resource_costs_per_turn.return_value = {"power": -50.0}

        engine.process_per_turn_consumption(1, [mock_empire])

        mock_ship.consume_resource.assert_not_called()

    def test_handles_multiple_resource_types(self, mock_registries, mock_empire, mock_fleet, mock_ship):
        """Multiple resource types are consumed."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine(registries=mock_registries)
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
