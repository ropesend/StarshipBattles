"""
Tests for ShipCombatEngine integration with real ships.
"""

import pytest
from unittest.mock import MagicMock

from game.core.math import Vector2
from game.simulation.combat.combat_events import CombatEventType
from game.simulation.entities.ship_combat_engine import ShipCombatEngine


class TestCombatEngineDelegation:
    """Focused tests for ShipCombatEngine subsystem delegation."""

    def test_select_target_delegates_with_owned_ship(self):
        ship = MagicMock()
        candidates = [MagicMock(), MagicMock()]
        selected = candidates[1]
        targeting = MagicMock()
        targeting.select_target.return_value = selected

        engine = ShipCombatEngine(ship)
        engine._targeting_system = targeting

        result = engine.select_target(candidates)

        assert result is selected
        targeting.select_target.assert_called_once_with(ship, candidates)

    def test_calculate_firing_solution_delegates_with_owned_ship(self):
        ship = MagicMock()
        component = MagicMock()
        target = MagicMock()
        solution = (Vector2(10, 20), Vector2(1, 0))
        targeting = MagicMock()
        targeting.calculate_firing_solution.return_value = solution

        engine = ShipCombatEngine(ship)
        engine._targeting_system = targeting

        result = engine.calculate_firing_solution(component, target)

        assert result == solution
        targeting.calculate_firing_solution.assert_called_once_with(ship, component, target)


class TestCombatEngineDamageEvents:
    """Focused tests for ShipCombatEngine damage event coordination."""

    def test_take_damage_emits_ship_destroyed_when_damage_kills_ship(self):
        ship = MagicMock()
        ship.is_alive = True
        event_bus = MagicMock()
        damage_calculator = MagicMock()
        context = object()

        def kill_ship(*_args):
            ship.is_alive = False

        damage_calculator.apply_damage.side_effect = kill_ship
        engine = ShipCombatEngine(ship)
        engine._damage_calculator = damage_calculator
        engine._event_bus = event_bus

        engine.take_damage(75, context)

        damage_calculator.apply_damage.assert_called_once_with(ship, 75, context, event_bus)
        event_bus.emit.assert_called_once()
        event = event_bus.emit.call_args.args[0]
        assert event.event_type is CombatEventType.SHIP_DESTROYED
        assert event.target_ship is ship
        assert event.context is context
        assert event.was_lethal is True


class TestCombatEngineIntegration:
    """Integration tests with real Ship objects."""

    def test_engine_works_with_real_ship(self, armed_ship):
        """ShipCombatEngine works with actual Ship instance."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        engine = ShipCombatEngine(armed_ship)
        assert engine is not None
        assert engine._ship is armed_ship

    def test_engine_fire_weapons_no_target(self, armed_ship):
        """fire_weapons returns empty when no target set."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        armed_ship.current_target = None
        engine = ShipCombatEngine(armed_ship)
        attacks = engine.fire_weapons()

        assert attacks == []
