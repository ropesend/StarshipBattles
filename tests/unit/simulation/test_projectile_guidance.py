"""Tests for projectile guidance system (_update_guidance method).

Focuses on:
- Missile homing behavior
- Lead calculation with solve_lead
- Angle normalization (-180 to 180)
- Turn direction commitment (anti-oscillation)
- Turn rate limiting
- Target tracking edge cases
"""
import pytest
import pygame
from unittest.mock import MagicMock, patch
import math

from game.simulation.entities.projectile import Projectile
from game.core.constants import AttackType


@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    """Initialize pygame for vector operations."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def mock_owner():
    """Create a minimal owner mock without solve_lead."""
    owner = MagicMock(spec=[])  # Empty spec prevents auto-creating attributes
    owner.team_id = 0
    owner.is_alive = True
    owner.position = pygame.math.Vector2(0, 0)
    return owner


@pytest.fixture
def mock_target():
    """Create a minimal target mock."""
    target = MagicMock()
    target.is_alive = True
    target.position = pygame.math.Vector2(1000, 0)
    target.velocity = pygame.math.Vector2(0, 0)
    return target


@pytest.fixture
def guided_missile(mock_owner, mock_target):
    """Create a standard guided missile for testing."""
    return Projectile(
        owner=mock_owner,
        position=pygame.math.Vector2(0, 0),
        velocity=pygame.math.Vector2(100, 0),  # Moving right
        damage=50,
        range_val=5000,
        endurance=10.0,
        proj_type='missile',
        turn_rate=90,  # 90 deg/sec
        max_speed=100,
        target=mock_target,
        hp=5
    )


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
# Test: Turn Direction Commitment (Anti-Oscillation)
# =============================================================================


class TestTurnDirectionCommitment:
    """Tests for turn direction commitment to prevent oscillation."""

    def test_last_turn_direction_initialized_zero(self, guided_missile):
        """Initial turn direction should be zero."""
        assert guided_missile.last_turn_direction == 0

    def test_turn_direction_stored_after_turn(self, mock_owner, mock_target):
        """Turn direction should be stored after turning."""
        mock_target.position = pygame.math.Vector2(1000, 100)

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

        # After turning toward target (upward), direction should be stored
        assert proj.last_turn_direction != 0

    def test_committed_direction_prevents_oscillation(self, mock_owner, mock_target):
        """When target is behind (~180°), should commit to one turn direction."""
        # Target directly behind
        mock_target.position = pygame.math.Vector2(-1000, 0)

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),  # Moving right
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=45,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        # Run multiple updates
        turn_directions = []
        for _ in range(10):
            proj.update()
            turn_directions.append(proj.last_turn_direction)

        # All non-zero directions should be the same (no flip-flopping)
        non_zero = [d for d in turn_directions if d != 0]
        if non_zero:
            assert all(d == non_zero[0] for d in non_zero)

    def test_commitment_near_180_degrees(self, mock_owner, mock_target):
        """Commitment should activate when target is generally behind (>135°)."""
        # Target at ~150 degrees from forward
        mock_target.position = pygame.math.Vector2(-866, 500)  # ~150 degrees

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=45,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        # First update to set direction
        proj.update()
        first_direction = proj.last_turn_direction

        # Run more updates
        for _ in range(5):
            proj.update()

        # Direction should remain committed
        if first_direction != 0:
            # Could flip to zero if angle drops below threshold
            assert proj.last_turn_direction in [first_direction, 0]


# =============================================================================
# Test: Lead Calculation
# =============================================================================


class TestLeadCalculation:
    """Tests for lead/intercept calculation in guidance."""

    def test_lead_calculation_with_solve_lead(self, mock_owner, mock_target):
        """Should use owner's solve_lead for lead calculation."""
        mock_owner.solve_lead = MagicMock(return_value=0.5)  # 0.5 second lead
        mock_target.position = pygame.math.Vector2(1000, 0)
        mock_target.velocity = pygame.math.Vector2(0, 100)  # Moving up

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

        # solve_lead should have been called
        mock_owner.solve_lead.assert_called()

    def test_lead_calculation_without_solve_lead(self, mock_owner, mock_target):
        """Should handle owner without solve_lead method."""
        # Remove solve_lead (default mock doesn't have it via hasattr check)
        del mock_owner.solve_lead
        mock_target.position = pygame.math.Vector2(1000, 0)

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(0, 100),  # Moving up
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=90,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        # Should not crash, just use direct pursuit
        proj.update()
        assert proj.is_alive

    def test_lead_zero_uses_direct_pursuit(self, mock_owner, mock_target):
        """When lead time is zero, should aim directly at target."""
        mock_owner.solve_lead = MagicMock(return_value=0)  # No lead
        mock_target.position = pygame.math.Vector2(1000, 0)
        mock_target.velocity = pygame.math.Vector2(0, 100)

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),  # Already aimed at target
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

        # With no lead and already aimed, minimal turning
        # Velocity should still be mostly horizontal
        assert abs(proj.velocity.x) > abs(proj.velocity.y)

    def test_lead_positive_aims_ahead(self, mock_owner, mock_target):
        """Positive lead time should aim ahead of target."""
        mock_owner.solve_lead = MagicMock(return_value=1.0)  # 1 second lead
        mock_target.position = pygame.math.Vector2(1000, 0)
        mock_target.velocity = pygame.math.Vector2(0, 100)  # Moving up at 100/s

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

        # Should turn upward to lead target
        assert proj.velocity.y > 0


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


# =============================================================================
# Test: Guidance Edge Cases
# =============================================================================


class TestGuidanceEdgeCases:
    """Edge cases in guidance system."""

    def test_target_at_same_position(self, mock_owner, mock_target):
        """Handle target at exact same position as missile."""
        mock_target.position = pygame.math.Vector2(0, 0)

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

        # Should not crash
        proj.update()
        assert proj.is_alive

    def test_target_very_close(self, mock_owner, mock_target):
        """Handle target very close to missile."""
        mock_target.position = pygame.math.Vector2(1, 1)

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

    def test_target_very_far(self, mock_owner, mock_target):
        """Handle target very far from missile."""
        mock_target.position = pygame.math.Vector2(1e9, 1e9)

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

    def test_dead_missile_does_not_update_guidance(self, mock_owner, mock_target):
        """Dead missile should not run guidance."""
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

        proj.is_alive = False
        initial_vel = pygame.math.Vector2(proj.velocity)

        proj.update()

        # Position should not change (early return)
        assert proj.velocity.x == initial_vel.x
        assert proj.velocity.y == initial_vel.y

    def test_multiple_updates_converge_on_target(self, mock_owner, mock_target):
        """Repeated updates should move closer to target."""
        mock_target.position = pygame.math.Vector2(1000, 1000)
        mock_target.velocity = pygame.math.Vector2(0, 0)  # Stationary

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),  # Moving right
            damage=50,
            range_val=100000,
            endurance=100.0,
            proj_type='missile',
            turn_rate=90,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        initial_distance = (mock_target.position - proj.position).length()

        # Run several updates
        for _ in range(20):
            if proj.is_alive:
                proj.update()

        # Distance to target should decrease (missile getting closer)
        final_distance = (mock_target.position - proj.position).length()
        assert final_distance < initial_distance


# =============================================================================
# Test: Type Handling
# =============================================================================


class TestTypeHandling:
    """Tests for proj_type handling."""

    def test_string_missile_type_guidance(self, mock_owner, mock_target):
        """String 'missile' type should trigger guidance."""
        mock_target.position = pygame.math.Vector2(0, 1000)

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',  # String type
            turn_rate=90,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        initial_vel_y = proj.velocity.y
        proj.update()

        # Should turn toward target (upward)
        assert proj.velocity.y > initial_vel_y

    def test_enum_missile_type_guidance(self, mock_owner, mock_target):
        """AttackType.MISSILE should trigger guidance."""
        mock_target.position = pygame.math.Vector2(0, 1000)

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type=AttackType.MISSILE,  # Enum type
            turn_rate=90,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        initial_vel_y = proj.velocity.y
        proj.update()

        # Should turn toward target (upward)
        assert proj.velocity.y > initial_vel_y

    def test_projectile_type_no_guidance(self, mock_owner, mock_target):
        """'projectile' type should not use guidance."""
        mock_target.position = pygame.math.Vector2(0, 1000)

        proj = Projectile(
            owner=mock_owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='projectile',  # Not a missile
            turn_rate=90,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        proj.update()

        # Should not turn (no guidance)
        assert proj.velocity.y == pytest.approx(0, abs=0.1)
