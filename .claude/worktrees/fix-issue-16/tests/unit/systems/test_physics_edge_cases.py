"""
Unit tests for PhysicsBody floating point edge cases.

Tests zero velocity, very small velocity preservation,
large force handling, zero mass protection, and drag reduction.
"""
import pytest

from game.core.math import Vector2
from game.engine.physics import PhysicsBody


class TestPhysicsBodyVelocity:
    """Tests for velocity edge cases."""

    def test_zero_velocity_stays_zero(self):
        """No force means velocity remains 0."""
        body = PhysicsBody(x=100, y=100)
        body.velocity = Vector2(0, 0)

        # Update several times with no force
        for _ in range(10):
            body.update()

        assert body.velocity.x == 0
        assert body.velocity.y == 0

    def test_very_small_velocity_not_lost(self):
        """Very small velocity (1e-10) is preserved after update."""
        body = PhysicsBody(x=0, y=0)
        body.velocity = Vector2(1e-10, 1e-10)
        body.drag = 0  # Disable drag to test pure preservation

        body.update()

        # Velocity should still be non-zero
        assert body.velocity.x != 0
        assert body.velocity.y != 0

    def test_large_force_velocity_reasonable(self):
        """Very large force doesn't produce infinity."""
        body = PhysicsBody(x=0, y=0)
        body.mass = 1.0

        # Apply a very large force
        large_force = Vector2(1e15, 1e15)
        body.apply_force(large_force)
        body.update()

        # Velocity should be large but finite
        import math
        assert math.isfinite(body.velocity.x)
        assert math.isfinite(body.velocity.y)
        assert body.velocity.x > 0
        assert body.velocity.y > 0


class TestPhysicsBodyMass:
    """Tests for mass handling."""

    def test_zero_mass_handling(self):
        """Division by zero is protected when mass is 0."""
        body = PhysicsBody(x=0, y=0)
        body.mass = 0  # Zero mass

        # Applying force should not crash
        body.apply_force(Vector2(100, 100))
        body.update()

        # With zero mass, force is not applied (if mass > 0 check)
        # Based on code: if self.mass > 0: self.acceleration += force / mass
        # So with mass=0, acceleration should remain 0
        assert body.velocity.x == 0
        assert body.velocity.y == 0

    def test_very_small_mass_large_acceleration(self):
        """Very small mass produces large but finite acceleration."""
        body = PhysicsBody(x=0, y=0)
        body.mass = 1e-10

        body.apply_force(Vector2(1, 0))
        body.update()

        import math
        assert math.isfinite(body.velocity.x)
        # Acceleration = force / mass = 1 / 1e-10 = 1e10
        # Velocity should be very large
        assert body.velocity.x > 0


class TestPhysicsBodyDrag:
    """Tests for drag behavior."""

    def test_drag_reduces_velocity(self):
        """After many ticks, velocity approaches 0 due to drag."""
        body = PhysicsBody(x=0, y=0)
        body.velocity = Vector2(1000, 0)
        body.drag = 0.5  # 50% drag per tick

        initial_speed = body.velocity.length()

        # Update many times
        for _ in range(100):
            body.update()

        # Velocity should be much smaller
        final_speed = body.velocity.length()
        assert final_speed < initial_speed * 0.01  # Less than 1% of original

    def test_drag_over_1_clamped(self):
        """Drag values over 1 are effectively clamped (no velocity reversal)."""
        body = PhysicsBody(x=0, y=0)
        body.velocity = Vector2(100, 0)
        body.drag = 1.5  # Over 1

        body.update()

        # Should not reverse velocity (clamped in code: if drag > 1: drag = 1)
        assert body.velocity.x >= 0

    def test_angular_drag_reduces_rotation(self):
        """Angular drag reduces angular velocity over time."""
        body = PhysicsBody(x=0, y=0)
        body.angular_velocity = 100  # degrees per second
        body.angular_drag = 0.5

        initial_angular = body.angular_velocity

        for _ in range(20):
            body.update()

        # Should be much smaller
        assert abs(body.angular_velocity) < abs(initial_angular) * 0.01
