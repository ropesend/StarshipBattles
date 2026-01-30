"""Tests for lead calculation (projectile intercept).

This module tests the quadratic intercept algorithm used for
projectile targeting in combat.
"""

import math
import pytest


class MockVector:
    """Simple 2D vector for testing lead calculations."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __sub__(self, other: "MockVector") -> "MockVector":
        return MockVector(self.x - other.x, self.y - other.y)

    def dot(self, other: "MockVector") -> float:
        return self.x * other.x + self.y * other.y

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"


def solve_lead(
    shooter_pos: MockVector,
    shooter_vel: MockVector,
    target_pos: MockVector,
    target_vel: MockVector,
    projectile_speed: float,
) -> float:
    """Calculate time to intercept using quadratic formula.

    Args:
        shooter_pos: Shooter position
        shooter_vel: Shooter velocity
        target_pos: Target position
        target_vel: Target velocity
        projectile_speed: Speed of projectile

    Returns:
        Time to intercept (0 if no solution)
    """
    D = target_pos - shooter_pos
    V = target_vel - shooter_vel

    a_q = V.dot(V) - projectile_speed**2
    b_q = 2 * V.dot(D)
    c_q = D.dot(D)

    t = 0
    if a_q == 0:
        if b_q != 0:
            t = -c_q / b_q
    else:
        disc = b_q * b_q - 4 * a_q * c_q
        if disc >= 0:
            t1 = (-b_q + math.sqrt(disc)) / (2 * a_q)
            t2 = (-b_q - math.sqrt(disc)) / (2 * a_q)
            ts = [x for x in [t1, t2] if x > 0]
            if ts:
                t = min(ts)

    return t


class TestLeadCalculation:
    """Tests for the lead calculation algorithm."""

    def test_static_target_direct_shot(self):
        """Static target at distance 100 with speed 100 should take 1.0 seconds."""
        shooter_pos = MockVector(0, 0)
        shooter_vel = MockVector(0, 0)
        target_pos = MockVector(100, 0)
        target_vel = MockVector(0, 0)
        projectile_speed = 100

        t = solve_lead(shooter_pos, shooter_vel, target_pos, target_vel, projectile_speed)

        assert t == pytest.approx(1.0), f"Expected 1.0, got {t}"

    def test_moving_target_perpendicular(self):
        """Moving target at 90 degrees should have positive intercept time.

        When target moves perpendicular at same speed as projectile,
        the quadratic has no positive solution (projectile can't catch up).
        Using a slower perpendicular velocity allows intercept.
        """
        shooter_pos = MockVector(0, 0)
        shooter_vel = MockVector(0, 0)
        target_pos = MockVector(100, 0)
        target_vel = MockVector(0, 50)  # Moving perpendicular at half speed
        projectile_speed = 100

        t = solve_lead(shooter_pos, shooter_vel, target_pos, target_vel, projectile_speed)

        # Should have a positive intercept time
        assert t > 0, f"Expected positive intercept time, got {t}"
        # Due to geometry, time should be greater than 1.0
        assert t > 1.0, f"Moving target should take longer than static target"

    def test_target_moving_away_fast(self):
        """Target moving away faster than projectile should have no solution."""
        shooter_pos = MockVector(0, 0)
        shooter_vel = MockVector(0, 0)
        target_pos = MockVector(100, 0)
        target_vel = MockVector(200, 0)  # Moving away faster than projectile
        projectile_speed = 100

        t = solve_lead(shooter_pos, shooter_vel, target_pos, target_vel, projectile_speed)

        # No intercept possible
        assert t == 0, f"Expected no intercept (0), got {t}"

    def test_target_moving_toward(self):
        """Target moving toward shooter should have faster intercept."""
        shooter_pos = MockVector(0, 0)
        shooter_vel = MockVector(0, 0)
        target_pos = MockVector(100, 0)
        target_vel = MockVector(-50, 0)  # Moving toward shooter
        projectile_speed = 100

        t = solve_lead(shooter_pos, shooter_vel, target_pos, target_vel, projectile_speed)

        # Should be faster than static target
        assert 0 < t < 1.0, f"Expected time < 1.0 for approaching target, got {t}"

    def test_both_moving_same_direction(self):
        """Both moving in same direction should account for relative velocity."""
        shooter_pos = MockVector(0, 0)
        shooter_vel = MockVector(50, 0)
        target_pos = MockVector(100, 0)
        target_vel = MockVector(50, 0)  # Same velocity as shooter
        projectile_speed = 100

        t = solve_lead(shooter_pos, shooter_vel, target_pos, target_vel, projectile_speed)

        # Relative velocity is 0, so it's like a static target
        assert t == pytest.approx(1.0), f"Expected 1.0 for matched velocities, got {t}"
