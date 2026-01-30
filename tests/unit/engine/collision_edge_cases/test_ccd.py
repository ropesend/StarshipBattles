"""Tests for Continuous Collision Detection (CCD) and projectile collisions.

Covers:
- High velocity collision (tunneling prevention)
- Zero and near-zero relative velocity
- Near-miss scenarios
- CCD time clamping
- Team and state filtering
"""
import pytest
from unittest.mock import MagicMock
from pygame.math import Vector2


# =============================================================================
# Test: High Velocity Collisions (Tunneling Prevention)
# =============================================================================


class TestHighVelocityCollision:
    """Tests for high-velocity collision detection (anti-tunneling)."""

    def test_high_velocity_detects_collision(self, projectile_manager, mock_grid, mock_target_ship):
        """High-velocity projectile should detect collision via CCD."""
        # Target at (100, 0) with radius 20
        mock_grid.query_radius.return_value = [mock_target_ship]

        proj = MagicMock()
        proj.position = Vector2(200, 0)  # Will be at this position after update
        proj.velocity = Vector2(200, 0)  # Moving 200 units per tick
        proj.radius = 2
        proj.damage = 50
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = None
        proj.distance_traveled = 100
        proj.target = None
        proj.status = 'active'

        # Previous position was (0, 0), passing through ship at (100, 0)
        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        # CCD should detect the collision
        mock_target_ship.take_damage.assert_called()
        assert proj.is_alive is False
        assert proj.status == 'hit'

    def test_very_high_velocity_no_tunneling(self, projectile_manager, mock_grid, mock_target_ship):
        """Extremely high velocity should still detect collision."""
        mock_grid.query_radius.return_value = [mock_target_ship]

        proj = MagicMock()
        proj.position = Vector2(10000, 0)  # Way past the target
        proj.velocity = Vector2(10000, 0)  # Massive velocity
        proj.radius = 1
        proj.damage = 100
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = None
        proj.distance_traveled = 5000
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        # Should still hit (CCD prevents tunneling)
        mock_target_ship.take_damage.assert_called()

    def test_high_velocity_narrow_miss(self, projectile_manager, mock_grid, mock_target_ship):
        """High velocity projectile narrowly missing should not hit."""
        # Target at (100, 0) with radius 20
        # Projectile passes at y=25 (outside radius)
        mock_target_ship.position = Vector2(100, 0)
        mock_target_ship.radius = 20
        mock_grid.query_radius.return_value = [mock_target_ship]

        proj = MagicMock()
        proj.position = Vector2(200, 25)  # At y=25
        proj.velocity = Vector2(200, 0)  # Moving horizontally
        proj.radius = 2
        proj.damage = 50
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = None
        proj.distance_traveled = 100
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        # Should miss (y=25 > radius 20 + tolerance)
        mock_target_ship.take_damage.assert_not_called()


# =============================================================================
# Test: Zero and Near-Zero Relative Velocity
# =============================================================================


class TestStaticRelativeMotion:
    """Tests for static or near-zero relative velocity."""

    def test_zero_relative_velocity_inside_radius(self, projectile_manager, mock_grid, mock_target_ship):
        """Objects with zero relative velocity inside collision radius should hit."""
        # Both moving at same velocity
        mock_target_ship.position = Vector2(100, 0)
        mock_target_ship.velocity = Vector2(10, 0)  # Same velocity as projectile
        mock_target_ship.radius = 20
        mock_grid.query_radius.return_value = [mock_target_ship]

        proj = MagicMock()
        proj.position = Vector2(110, 0)  # 10 units from target center
        proj.velocity = Vector2(10, 0)  # Same velocity
        proj.radius = 2
        proj.damage = 25
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = None
        proj.distance_traveled = 50
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        # Distance (10) < radius (20) -> hit
        mock_target_ship.take_damage.assert_called()

    def test_zero_relative_velocity_outside_radius(self, projectile_manager, mock_grid, mock_target_ship):
        """Objects with zero relative velocity outside radius should miss."""
        mock_target_ship.position = Vector2(100, 0)
        mock_target_ship.velocity = Vector2(10, 0)
        mock_target_ship.radius = 20
        mock_grid.query_radius.return_value = [mock_target_ship]

        proj = MagicMock()
        proj.position = Vector2(150, 0)  # 50 units from target center
        proj.velocity = Vector2(10, 0)  # Same velocity
        proj.radius = 2
        proj.damage = 25
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = None
        proj.distance_traveled = 50
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        # Distance (50) > radius (20) -> miss
        mock_target_ship.take_damage.assert_not_called()


# =============================================================================
# Test: Near-Miss Scenarios
# =============================================================================


class TestNearMissScenarios:
    """Tests for near-miss collision detection."""

    def test_grazing_hit(self, projectile_manager, mock_grid, mock_target_ship):
        """Projectile grazing the edge should hit."""
        mock_target_ship.position = Vector2(100, 0)
        mock_target_ship.radius = 20
        mock_grid.query_radius.return_value = [mock_target_ship]

        proj = MagicMock()
        # Projectile passes at y=19 (just inside radius 20)
        proj.position = Vector2(200, 19)
        proj.velocity = Vector2(200, 0)
        proj.radius = 2
        proj.damage = 30
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = None
        proj.distance_traveled = 100
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        # With tolerance, this should hit
        mock_target_ship.take_damage.assert_called()

    def test_barely_miss(self, projectile_manager, mock_grid, mock_target_ship):
        """Projectile barely missing should not hit."""
        mock_target_ship.position = Vector2(100, 0)
        mock_target_ship.radius = 20
        mock_grid.query_radius.return_value = [mock_target_ship]

        proj = MagicMock()
        # Projectile passes at y=30 (well outside radius 20 + tolerance)
        proj.position = Vector2(200, 30)
        proj.velocity = Vector2(200, 0)
        proj.radius = 2
        proj.damage = 30
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = None
        proj.distance_traveled = 100
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        mock_target_ship.take_damage.assert_not_called()

    def test_perpendicular_approach_miss(self, projectile_manager, mock_grid, mock_target_ship):
        """Perpendicular approach missing should not hit."""
        mock_target_ship.position = Vector2(100, 0)
        mock_target_ship.radius = 20
        mock_grid.query_radius.return_value = [mock_target_ship]

        proj = MagicMock()
        # Moving vertically, but starting at x=150 (50 units from target)
        proj.position = Vector2(150, 50)
        proj.velocity = Vector2(0, -50)
        proj.radius = 2
        proj.damage = 30
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = None
        proj.distance_traveled = 25
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        mock_target_ship.take_damage.assert_not_called()


# =============================================================================
# Test: CCD Time Clamping
# =============================================================================


class TestCCDTimeClamping:
    """Tests for CCD time parameter clamping."""

    def test_collision_at_start_of_frame(self, projectile_manager, mock_grid, mock_target_ship):
        """Collision at t=0 (start of frame) should be detected."""
        mock_target_ship.position = Vector2(10, 0)
        mock_target_ship.radius = 20
        mock_grid.query_radius.return_value = [mock_target_ship]

        proj = MagicMock()
        # Already inside collision radius at start
        proj.position = Vector2(20, 0)  # After velocity (10, 0)
        proj.velocity = Vector2(10, 0)  # Prev pos was (10, 0)
        proj.radius = 2
        proj.damage = 40
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = None
        proj.distance_traveled = 10
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        mock_target_ship.take_damage.assert_called()

    def test_collision_at_end_of_frame(self, projectile_manager, mock_grid, mock_target_ship):
        """Collision at t=1 (end of frame) should be detected."""
        mock_target_ship.position = Vector2(100, 0)
        mock_target_ship.radius = 20
        mock_grid.query_radius.return_value = [mock_target_ship]

        proj = MagicMock()
        # Will be at (90, 0) at end of frame, right at edge of radius
        proj.position = Vector2(90, 0)  # After velocity (90, 0)
        proj.velocity = Vector2(90, 0)  # Prev pos was (0, 0)
        proj.radius = 2
        proj.damage = 40
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = None
        proj.distance_traveled = 90
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        mock_target_ship.take_damage.assert_called()


# =============================================================================
# Test: Team and State Filtering
# =============================================================================


class TestCollisionFiltering:
    """Tests for collision filtering (team, alive state)."""

    def test_same_team_no_collision(self, projectile_manager, mock_grid, mock_target_ship):
        """Projectiles should not hit same-team ships."""
        mock_target_ship.team_id = 0  # Same team as projectile
        mock_grid.query_radius.return_value = [mock_target_ship]

        proj = MagicMock()
        proj.position = Vector2(100, 0)  # Right on target
        proj.velocity = Vector2(10, 0)
        proj.radius = 2
        proj.damage = 50
        proj.is_alive = True
        proj.team_id = 0  # Same team
        proj.type = 'projectile'
        proj.source_weapon = None
        proj.distance_traveled = 50
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        mock_target_ship.take_damage.assert_not_called()

    def test_dead_ship_no_collision(self, projectile_manager, mock_grid, mock_target_ship):
        """Projectiles should not collide with dead ships."""
        mock_target_ship.is_alive = False
        mock_grid.query_radius.return_value = [mock_target_ship]

        proj = MagicMock()
        proj.position = Vector2(100, 0)
        proj.velocity = Vector2(10, 0)
        proj.radius = 2
        proj.damage = 50
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = None
        proj.distance_traveled = 50
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        mock_target_ship.take_damage.assert_not_called()

    def test_dead_projectile_skipped(self, projectile_manager, mock_grid, mock_target_ship):
        """Dead projectiles should not be processed."""
        mock_grid.query_radius.return_value = [mock_target_ship]

        proj = MagicMock()
        proj.position = Vector2(100, 0)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = False  # Already dead
        proj.team_id = 0
        proj.type = 'projectile'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        # Should skip collision check entirely
        mock_target_ship.take_damage.assert_not_called()
