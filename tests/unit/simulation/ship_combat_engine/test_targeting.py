"""
Tests for ShipCombatEngine target selection and firing solutions.

Tests target selection logic and firing solution calculations.
"""

import pytest
from unittest.mock import MagicMock

from game.core.math import Vector2


class TestTargetSelection:
    """Tests for target selection logic."""

    def test_select_target_returns_valid_enemy(self):
        """select_target returns an enemy ship from candidates."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Create enemy candidate
        enemy = MagicMock()
        enemy.is_alive = True
        enemy.team_id = 1
        enemy.position = Vector2(100, 0)

        target = engine.select_target([enemy])
        assert target is enemy

    def test_select_target_excludes_friendlies(self):
        """select_target does not return friendly ships."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Create friendly ship
        friendly = MagicMock()
        friendly.is_alive = True
        friendly.team_id = 0  # Same team

        target = engine.select_target([friendly])
        assert target is None

    def test_select_target_excludes_dead_ships(self):
        """select_target does not return dead ships."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Create dead enemy
        dead_enemy = MagicMock()
        dead_enemy.is_alive = False
        dead_enemy.team_id = 1

        target = engine.select_target([dead_enemy])
        assert target is None

    def test_select_target_returns_closest_enemy(self):
        """select_target returns the closest valid enemy."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Create multiple enemies at different distances
        far_enemy = MagicMock()
        far_enemy.is_alive = True
        far_enemy.team_id = 1
        far_enemy.position = Vector2(200, 0)

        close_enemy = MagicMock()
        close_enemy.is_alive = True
        close_enemy.team_id = 1
        close_enemy.position = Vector2(50, 0)

        target = engine.select_target([far_enemy, close_enemy])
        assert target is close_enemy


class TestFiringSolutionCalculation:
    """Tests for firing solution calculation."""

    def test_calculate_firing_solution_beam_weapon(self):
        """Firing solution for beam weapon aims directly at target."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Create target
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.velocity = Vector2(0, 0)

        # Create beam weapon component
        comp = MagicMock()
        comp.has_ability = lambda name: name in ['WeaponAbility', 'BeamWeaponAbility']
        comp.get_ability = MagicMock(return_value=None)

        aim_pos, aim_vec = engine.calculate_firing_solution(comp, target)

        assert aim_pos.x == 100
        assert aim_pos.y == 0
        assert aim_vec.x == 100
        assert aim_vec.y == 0

    def test_calculate_firing_solution_projectile_weapon(self):
        """Firing solution for projectile weapon leads the target."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Create moving target
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.velocity = Vector2(10, 0)  # Moving right

        # Create projectile weapon component
        proj_ability = MagicMock()
        proj_ability.projectile_speed = 500  # 500 units/tick * 100 = 5 units/tick

        comp = MagicMock()
        comp.has_ability = lambda name: name == 'ProjectileWeaponAbility'
        comp.get_ability = lambda name: proj_ability if name == 'ProjectileWeaponAbility' else None

        aim_pos, aim_vec = engine.calculate_firing_solution(comp, target)

        # Aim position should be ahead of current position (leading target)
        assert aim_pos.x >= target.position.x
