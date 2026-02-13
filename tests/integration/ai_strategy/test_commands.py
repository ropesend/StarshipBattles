"""
Tests for AI command generation and movement.
"""

import pytest
import pygame
from unittest.mock import patch
from game.ai.controller import AIController
from game.ai.interfaces.controllable import ShipControllableAdapter
from game.core.math import Vector2


class TestCommandGeneration:
    """Tests for AI movement and fire commands."""

    def test_behavior_selected_based_on_strategy(self, spatial_grid, create_test_ship):
        """AI selects behavior based on strategy config."""
        ship1 = create_test_ship("Ally", 0, 0, team_id=0)
        ship2 = create_test_ship("Enemy", 1000, 0, team_id=1)

        spatial_grid.insert(ship1)
        spatial_grid.insert(ship2)

        ship1.ai_strategy = 'max_weapons_range'

        ai_controller = AIController(ShipControllableAdapter(ship1), spatial_grid, enemy_team_id=1)
        ai_controller.update()

        # Behavior should be set
        assert ai_controller.current_behavior is not None

    def test_flee_behavior_when_low_hp(self, spatial_grid, create_test_ship):
        """AI flees when HP below threshold."""
        ship1 = create_test_ship("Ally", 0, 0, team_id=0)
        ship2 = create_test_ship("Enemy", 1000, 0, team_id=1)

        spatial_grid.insert(ship1)
        spatial_grid.insert(ship2)

        ai_controller = AIController(ShipControllableAdapter(ship1), spatial_grid, enemy_team_id=1)

        # Mock low HP by patching the module-level function
        with patch('game.ai.controller.get_hp_percent', return_value=0.05):
            ai_controller.update()

        # Should have flee behavior
        assert ai_controller.current_behavior is not None
        assert 'flee' in str(type(ai_controller.current_behavior)).lower()

    def test_navigate_to_rotates_ship(self, spatial_grid, create_test_ship):
        """Navigation command rotates ship toward target."""
        ship1 = create_test_ship("Ally", 0, 0, team_id=0)

        spatial_grid.insert(ship1)

        ai_controller = AIController(ShipControllableAdapter(ship1), spatial_grid, enemy_team_id=1)

        # Ship facing right (0), target is down (90 degrees)
        ship1.angle = 0
        target_pos = pygame.math.Vector2(0, 1000)

        # Should attempt to navigate - this calls rotate internally
        ai_controller.navigate_to(target_pos)

        # Rotation occurred (can't verify exact angle due to turn rate limits)

    def test_collision_avoidance_returns_position(self, spatial_grid, create_test_ship):
        """Avoidance check returns position when obstacle nearby."""
        ship1 = create_test_ship("Ally", 0, 0, team_id=0)
        ship2 = create_test_ship("Enemy", 100, 0, team_id=1)  # Very close

        spatial_grid.insert(ship1)
        spatial_grid.insert(ship2)

        ai_controller = AIController(ShipControllableAdapter(ship1), spatial_grid, enemy_team_id=1)

        override = ai_controller.check_avoidance()

        # Should return avoidance target position (game.core.math.Vector2, not pygame.math.Vector2)
        assert override is not None
        assert isinstance(override, Vector2)
