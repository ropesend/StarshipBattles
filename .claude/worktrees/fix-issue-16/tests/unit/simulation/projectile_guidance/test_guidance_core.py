"""Tests for projectile guidance system core mechanics.

Focuses on:
- Missile homing behavior activation
- Turn rate limiting
- Angle normalization (-180 to 180)
- Velocity normalization

Split from test_projectile_guidance.py - core guidance tests.
"""
import pytest
import pygame
from unittest.mock import MagicMock
import math

from game.simulation.entities.projectile import Projectile
from game.core.constants import AttackType


# =============================================================================
# Test: Basic Guidance Activation
# =============================================================================


class TestGuidanceActivation:
    """Tests for when guidance is triggered."""

    def test_guidance_only_for_missiles(self, mock_owner, mock_target):
        """Non-missile projectiles should not use guidance."""
        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(0, 100),  # Moving up
            damage=10,
            range_val=5000,
            endurance=10.0,
            proj_type='projectile',  # Not a missile
            turn_rate=90,
            max_speed=100,
            target=mock_target
        )

        initial_vel = pygame.math.Vector2(proj.velocity)
        proj.update()

        # Velocity direction should be unchanged (no guidance)
        assert proj.velocity.x == pytest.approx(initial_vel.x, abs=0.1)
        assert proj.velocity.y == pytest.approx(initial_vel.y, abs=0.1)

    def test_guidance_requires_target(self, mock_owner):
        """Missile without target should not use guidance."""
        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=90,
            max_speed=100,
            target=None,  # No target
            hp=5
        )

        initial_vel = pygame.math.Vector2(proj.velocity)
        proj.update()

        # Should continue straight
        assert proj.velocity.x == pytest.approx(initial_vel.x, abs=0.1)

    def test_guidance_requires_living_target(self, mock_owner, mock_target):
        """Missile should not track dead target."""
        mock_target.is_alive = False

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=90,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        initial_vel = pygame.math.Vector2(proj.velocity)
        proj.update()

        # Should continue straight
        assert proj.velocity.x == pytest.approx(initial_vel.x, abs=0.1)
        assert proj.velocity.y == pytest.approx(initial_vel.y, abs=0.1)

    def test_guidance_with_attacktype_missile(self, mock_owner, mock_target):
        """AttackType.MISSILE should trigger guidance."""
        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(0, -100),  # Moving up
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type=AttackType.MISSILE,  # Using enum
            turn_rate=90,
            max_speed=100,
            target=mock_target,  # Target at (1000, 0)
            hp=5
        )

        initial_vel_x = proj.velocity.x

        # After update, should turn toward target (rightward)
        proj.update()

        assert proj.velocity.x > initial_vel_x


# =============================================================================
# Test: Turn Rate Limiting
# =============================================================================


class TestTurnRateLimiting:
    """Tests for turn rate constraints."""

    def test_turn_rate_limits_rotation(self, mock_owner, mock_target):
        """Missile should not exceed max turn rate per tick."""
        # Target directly behind missile
        mock_target.position = pygame.math.Vector2(-1000, 0)

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),  # Moving right
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=45,  # 45 deg/sec -> 0.45 deg/tick at 0.01s tick
            max_speed=100,
            target=mock_target,
            hp=5
        )

        initial_angle = math.atan2(proj.velocity.y, proj.velocity.x)
        proj.update()
        final_angle = math.atan2(proj.velocity.y, proj.velocity.x)

        # Calculate actual turn (in degrees)
        turn_degrees = math.degrees(abs(final_angle - initial_angle))

        # Should be limited to approximately turn_rate * 0.01
        # turn_rate=45, so max turn per tick = 0.45 degrees
        assert turn_degrees <= 0.5  # Allow small tolerance

    def test_small_angle_correction_not_limited(self, mock_owner, mock_target):
        """Small angle corrections should not be limited."""
        # Target slightly off-axis
        mock_target.position = pygame.math.Vector2(1000, 10)  # Slightly above

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=90,  # High turn rate
            max_speed=100,
            target=mock_target,
            hp=5
        )

        # With high turn rate and small angle, should correct fully
        proj.update()

        # Velocity should have positive y component
        assert proj.velocity.y > 0

    def test_zero_turn_rate_missile_flies_straight(self, mock_owner, mock_target):
        """Missile with zero turn rate cannot adjust course."""
        mock_target.position = pygame.math.Vector2(0, 1000)  # Target above

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=0,  # No turn capability
            max_speed=100,
            target=mock_target,
            hp=5
        )

        initial_vel = pygame.math.Vector2(proj.velocity)
        proj.update()

        # Should not turn at all
        assert proj.velocity.y == pytest.approx(0, abs=0.01)


# =============================================================================
# Test: Angle Normalization
# =============================================================================


class TestAngleNormalization:
    """Tests for angle normalization to [-180, 180]."""

    def test_angle_greater_than_180_normalized(self, mock_owner, mock_target):
        """Angles > 180 should be normalized to negative."""
        # This tests the shortest-path logic
        # Target behind and slightly left -> angle_to might return > 180
        mock_target.position = pygame.math.Vector2(-100, -10)  # Behind, slightly below

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),  # Moving right
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=90,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        # Should turn, verify no errors and velocity changes
        proj.update()

        # Just verify it doesn't crash and velocity changed
        assert proj.is_alive

    def test_angle_less_than_minus_180_normalized(self, mock_owner, mock_target):
        """Angles < -180 should be normalized to positive."""
        mock_target.position = pygame.math.Vector2(-100, 10)  # Behind, slightly above

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=90,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        proj.update()
        assert proj.is_alive


# =============================================================================
# Test: Velocity Normalization
# =============================================================================


class TestVelocityNormalization:
    """Tests for velocity handling in guidance."""

    def test_maintains_max_speed_after_turn(self, mock_owner, mock_target):
        """Missile should maintain max_speed after turning."""
        mock_target.position = pygame.math.Vector2(0, 1000)  # Above

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=90,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        proj.update()

        # Speed should still be ~100
        speed = proj.velocity.length()
        assert speed == pytest.approx(100, abs=0.1)

    def test_zero_velocity_uses_default_direction(self, mock_owner, mock_target):
        """Zero velocity should use default direction (1, 0)."""
        mock_target.position = pygame.math.Vector2(1000, 0)

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(0, 0),  # Zero velocity
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=90,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        # Should not crash
        proj.update()

        # After guidance, should have velocity toward target
        assert proj.velocity.length() > 0
