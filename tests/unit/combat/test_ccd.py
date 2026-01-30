"""Tests for Continuous Collision Detection (CCD).

This module tests the CCD algorithm used to detect high-speed
projectile collisions that might otherwise "tunnel" through targets.
"""

import math
from typing import Tuple

import pytest


class Vector:
    """Simple 2D vector for testing CCD."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar)

    def dot(self, other: "Vector") -> float:
        return self.x * other.x + self.y * other.y

    def length_sq(self) -> float:
        return self.x**2 + self.y**2

    def length(self) -> float:
        return math.sqrt(self.length_sq())

    def __repr__(self) -> str:
        return f"({self.x:.1f}, {self.y:.1f})"


def check_collision(
    p_pos: Vector,
    p_vel: Vector,
    s_pos: Vector,
    s_vel: Vector,
    radius: float,
    dt: float,
) -> Tuple[bool, float]:
    """Check for collision between projectile and ship using CCD.

    Uses closest point of approach (CPA) algorithm to detect collisions
    even when projectile travels faster than target radius per frame.

    Args:
        p_pos: Projectile position
        p_vel: Projectile velocity
        s_pos: Ship position
        s_vel: Ship velocity
        radius: Ship collision radius
        dt: Time step

    Returns:
        Tuple of (hit, time_of_closest_approach)
    """
    # Relative Motion
    D = p_pos - s_pos
    V = p_vel - s_vel

    # t_cpa = -(D . V) / (V . V)
    v_sq = V.length_sq()
    if v_sq == 0:
        # Parallel/Static relative motion
        dist = D.length()
        return dist <= radius, 0

    t = -(D.dot(V)) / v_sq

    # Clamp t to segment [0, dt]
    t_clamped = max(0, min(t, dt))

    # Position at t
    p_at_t = p_pos + p_vel * t_clamped
    s_at_t = s_pos + s_vel * t_clamped

    dist_sq = (p_at_t - s_at_t).length_sq()

    hit = dist_sq <= (radius**2)
    return hit, t_clamped


class TestContinuousCollisionDetection:
    """Tests for the CCD algorithm."""

    def test_tunneling_detection(self):
        """High-speed projectile should still hit target via CCD.

        Scenario:
        - Ship at (100, 0), Radius 40
        - Projectile starts at (0, 0), moving at 20000 units/sec
        - dt = 0.016 (60 FPS) -> moves 320 units per frame
        - Without CCD, projectile would pass through ship
        """
        s_pos = Vector(100, 0)
        s_vel = Vector(0, 0)
        s_rad = 40

        p_pos = Vector(0, 0)
        p_vel = Vector(20000, 0)
        dt = 0.016

        hit, t = check_collision(p_pos, p_vel, s_pos, s_vel, s_rad, dt)

        assert hit is True, "CCD should detect tunneling projectile"
        assert 0 < t < dt, f"Collision time should be within frame, got {t}"

    def test_miss_off_target(self):
        """High-speed projectile should miss if trajectory doesn't intersect.

        Scenario:
        - Ship at (100, 0), Radius 40
        - Projectile at (0, 100), moving horizontally
        - y=100 is greater than radius 40, so should miss
        """
        s_pos = Vector(100, 0)
        s_vel = Vector(0, 0)
        s_rad = 40

        p_pos = Vector(0, 100)  # y=100 is > radius 40
        p_vel = Vector(20000, 0)
        dt = 0.016

        hit, t = check_collision(p_pos, p_vel, s_pos, s_vel, s_rad, dt)

        assert hit is False, "Should miss when projectile path doesn't intersect"

    def test_stationary_collision(self):
        """Stationary projectile within radius should collide."""
        s_pos = Vector(100, 0)
        s_vel = Vector(0, 0)
        s_rad = 40

        p_pos = Vector(90, 0)  # 10 units from center, within radius
        p_vel = Vector(0, 0)  # Stationary
        dt = 0.016

        hit, t = check_collision(p_pos, p_vel, s_pos, s_vel, s_rad, dt)

        assert hit is True, "Stationary projectile within radius should hit"
        assert t == 0, "Time should be 0 for stationary collision"

    def test_stationary_miss(self):
        """Stationary projectile outside radius should not collide."""
        s_pos = Vector(100, 0)
        s_vel = Vector(0, 0)
        s_rad = 40

        p_pos = Vector(0, 0)  # 100 units from center, outside radius
        p_vel = Vector(0, 0)  # Stationary
        dt = 0.016

        hit, t = check_collision(p_pos, p_vel, s_pos, s_vel, s_rad, dt)

        assert hit is False, "Stationary projectile outside radius should miss"

    def test_both_moving_same_direction(self):
        """Objects moving same direction maintain relative distance."""
        s_pos = Vector(100, 0)
        s_vel = Vector(100, 0)  # Moving right
        s_rad = 40

        p_pos = Vector(0, 0)  # 100 units behind
        p_vel = Vector(100, 0)  # Same velocity
        dt = 0.016

        hit, t = check_collision(p_pos, p_vel, s_pos, s_vel, s_rad, dt)

        assert hit is False, "Parallel motion at same velocity should not collide"

    def test_catching_up_collision(self):
        """Faster projectile catching up to slower target should hit."""
        s_pos = Vector(50, 0)
        s_vel = Vector(100, 0)  # Moving right at 100
        s_rad = 40

        p_pos = Vector(0, 0)  # 50 units behind
        p_vel = Vector(200, 0)  # Moving right at 200 (catching up)
        dt = 1.0  # Large dt to ensure catch-up

        hit, t = check_collision(p_pos, p_vel, s_pos, s_vel, s_rad, dt)

        assert hit is True, "Faster projectile should catch slower target"

    def test_edge_collision(self):
        """Projectile passing exactly at edge of radius should hit."""
        s_pos = Vector(100, 0)
        s_vel = Vector(0, 0)
        s_rad = 40

        # Projectile will pass at y=40 (exactly at radius)
        p_pos = Vector(0, 40)
        p_vel = Vector(1000, 0)
        dt = 0.2

        hit, t = check_collision(p_pos, p_vel, s_pos, s_vel, s_rad, dt)

        assert hit is True, "Projectile at edge of radius should hit"
