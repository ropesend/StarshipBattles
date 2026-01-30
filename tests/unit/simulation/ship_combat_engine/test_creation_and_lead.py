"""
Tests for ShipCombatEngine creation and lead calculation.

Tests instantiation and interception/lead time calculations.
"""

import pytest
from unittest.mock import MagicMock

from game.core.math import Vector2


class TestShipCombatEngineCreation:
    """Tests for ShipCombatEngine instantiation."""

    def test_combat_engine_can_be_created(self):
        """ShipCombatEngine can be instantiated with a ship."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        engine = ShipCombatEngine(ship)
        assert engine is not None
        assert engine._ship is ship

    def test_combat_engine_stores_ship_reference(self):
        """ShipCombatEngine stores reference to its ship."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.position = Vector2(0, 0)

        engine = ShipCombatEngine(ship)
        assert engine._ship is ship


class TestSolveLeadCalculation:
    """Tests for lead/interception calculation."""

    def test_solve_lead_stationary_target(self):
        """Lead calculation for stationary target returns direct time-to-target."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Target at (100, 0), stationary, projectile speed 10
        target_pos = Vector2(100, 0)
        target_vel = Vector2(0, 0)
        proj_speed = 10.0

        t = engine.solve_lead(ship.position, ship.velocity, target_pos, target_vel, proj_speed)

        # Time should be distance / speed = 100 / 10 = 10
        assert abs(t - 10.0) < 0.1

    def test_solve_lead_moving_target(self):
        """Lead calculation for moving target returns intercept time."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Target moving right at 10 u/s at (100, 0)
        target_pos = Vector2(100, 0)
        target_vel = Vector2(10, 0)
        proj_speed = 20.0

        t = engine.solve_lead(ship.position, ship.velocity, target_pos, target_vel, proj_speed)

        # t should be ~10.0 based on quadratic solution
        assert t > 0
        assert abs(t - 10.0) < 0.5

    def test_solve_lead_no_solution(self):
        """Lead calculation returns 0 when target cannot be intercepted."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Target moving away faster than projectile
        target_pos = Vector2(100, 0)
        target_vel = Vector2(100, 0)  # Moving away at 100 u/s
        proj_speed = 10.0  # Only 10 u/s

        t = engine.solve_lead(ship.position, ship.velocity, target_pos, target_vel, proj_speed)

        assert t == 0
