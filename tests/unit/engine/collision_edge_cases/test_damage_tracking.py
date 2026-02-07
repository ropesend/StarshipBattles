"""Tests for damage calculation and shot tracking during collisions.

Covers:
- Damage calculation with source weapons
- Shot hit/miss tracking on weapons
"""
import pytest
from unittest.mock import MagicMock
from pygame.math import Vector2


# =============================================================================
# Test: Damage Calculation
# =============================================================================


class TestDamageCalculation:
    """Tests for damage calculation during collision."""

    def test_source_weapon_damage_formula(self, projectile_manager, mock_grid, mock_target_ship):
        """Damage should use source weapon formula when available."""
        mock_grid.query_radius.return_value = [mock_target_ship]

        mock_weapon_ability = MagicMock()
        mock_weapon_ability.get_damage.return_value = 75  # Custom damage

        mock_weapon = MagicMock()
        mock_weapon.get_ability.return_value = mock_weapon_ability

        proj = MagicMock()
        proj.position = Vector2(100, 0)
        proj.velocity = Vector2(10, 0)
        proj.radius = 2
        proj.damage = 50  # Base damage
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = mock_weapon  # Has source weapon
        proj.distance_traveled = 50
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        # Should use weapon formula damage (75), not base damage (50)
        mock_target_ship.combat_engine.take_damage.assert_called_with(75)

    def test_no_source_weapon_uses_base_damage(self, projectile_manager, mock_grid, mock_target_ship):
        """Without source weapon, should use base damage."""
        mock_grid.query_radius.return_value = [mock_target_ship]

        proj = MagicMock()
        proj.position = Vector2(100, 0)
        proj.velocity = Vector2(10, 0)
        proj.radius = 2
        proj.damage = 35  # Base damage
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = None  # No source weapon
        proj.distance_traveled = 50
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        mock_target_ship.combat_engine.take_damage.assert_called_with(35)


# =============================================================================
# Test: Shot Tracking
# =============================================================================


class TestShotTracking:
    """Tests for hit/miss tracking on weapons."""

    def test_hit_increments_shots_hit(self, projectile_manager, mock_grid, mock_target_ship):
        """Hitting target should increment source weapon's shots_hit."""
        mock_grid.query_radius.return_value = [mock_target_ship]

        mock_weapon = MagicMock()
        mock_weapon.get_ability.return_value = None  # No special ability
        # Remove shots_hit so it tests creation
        del mock_weapon.shots_hit

        proj = MagicMock()
        proj.position = Vector2(100, 0)
        proj.velocity = Vector2(10, 0)
        proj.radius = 2
        proj.damage = 20
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = mock_weapon
        proj.distance_traveled = 50
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        # shots_hit should be created and set to 1
        assert mock_weapon.shots_hit == 1

    def test_multiple_hits_accumulate(self, projectile_manager, mock_grid, mock_target_ship):
        """Multiple hits should accumulate shots_hit."""
        mock_grid.query_radius.return_value = [mock_target_ship]

        mock_weapon = MagicMock()
        mock_weapon.shots_hit = 5  # Already has hits
        mock_weapon.get_ability.return_value = None

        proj = MagicMock()
        proj.position = Vector2(100, 0)
        proj.velocity = Vector2(10, 0)
        proj.radius = 2
        proj.damage = 20
        proj.is_alive = True
        proj.team_id = 0
        proj.type = 'projectile'
        proj.source_weapon = mock_weapon
        proj.distance_traveled = 50
        proj.target = None
        proj.status = 'active'

        projectile_manager.add_projectile(proj)
        projectile_manager.update(mock_grid)

        assert mock_weapon.shots_hit == 6
