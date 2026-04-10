"""
Tests for ShipCombatEngine integration with real ships.
"""

import pytest


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
