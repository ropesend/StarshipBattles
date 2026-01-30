"""Tests for projectile guidance system behavior.

Focuses on:
- Turn direction commitment (anti-oscillation)
- Lead calculation with solve_lead
- Edge cases in guidance
- Type handling

Split from test_projectile_guidance.py - guidance behavior tests.
"""
import pytest
import pygame
from unittest.mock import MagicMock

from game.simulation.entities.projectile import Projectile
from game.core.constants import AttackType


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
