"""
Tests for AI response to changing battle conditions and strategy resolution.
"""

import pytest
import pygame
from unittest.mock import patch
from game.ai.controller import AIController
from game.ai.interfaces.controllable import ShipControllableAdapter


class TestAIResponse:
    """Tests for AI adapting to changing battle conditions."""

    def test_retargets_when_target_dies(self, spatial_grid, create_test_ship):
        """AI finds new target when current dies."""
        ship1 = create_test_ship("Ally", 0, 0, team_id=0)
        enemy1 = create_test_ship("Enemy1", 500, 0, team_id=1)
        enemy2 = create_test_ship("Enemy2", 1000, 0, team_id=1)

        spatial_grid.insert(ship1)
        spatial_grid.insert(enemy1)
        spatial_grid.insert(enemy2)

        ai_controller = AIController(ShipControllableAdapter(ship1), spatial_grid, enemy_team_id=1)

        # First update - targets enemy1 (closer)
        ai_controller.update()
        first_target = ship1.current_target
        assert first_target == enemy1

        # Kill enemy1
        enemy1.is_alive = False

        # Next update - should retarget to enemy2
        ai_controller.update()
        assert ship1.current_target == enemy2

    def test_transitions_strategy_on_damage(self, spatial_grid, create_test_ship):
        """AI may switch strategy when damaged."""
        ship1 = create_test_ship("Ally", 0, 0, team_id=0)
        enemy = create_test_ship("Enemy", 1000, 0, team_id=1)

        spatial_grid.insert(ship1)
        spatial_grid.insert(enemy)

        ai_controller = AIController(ShipControllableAdapter(ship1), spatial_grid, enemy_team_id=1)

        # Normal update - mock full HP
        with patch('game.ai.controller.get_hp_percent', return_value=1.0):
            ai_controller.update()
            normal_behavior = str(type(ai_controller.current_behavior))

        # Damaged update - should potentially switch to flee
        with patch('game.ai.controller.get_hp_percent', return_value=0.05):
            ai_controller.update()
            damaged_behavior = str(type(ai_controller.current_behavior))

        # Behavior should have changed
        assert 'flee' in damaged_behavior.lower()


class TestStrategyResolution:
    """Tests for strategy configuration resolution."""

    def test_resolves_strategy_from_manager(self, spatial_grid, create_test_ship):
        """AI resolves strategy from StrategyManager."""
        ship1 = create_test_ship("Ally", 0, 0, team_id=0)

        spatial_grid.insert(ship1)

        ship1.ai_strategy = 'max_weapons_range'

        ai_controller = AIController(ShipControllableAdapter(ship1), spatial_grid, enemy_team_id=1)
        resolved = ai_controller.get_resolved_strategy()

        assert resolved is not None
        assert 'targeting' in resolved
        assert 'movement' in resolved

    # NOTE: test_default_strategy_if_not_set was deleted in PROJ-192 Phase 3.
    # Ship ALWAYS has ai_strategy (set in __init__), so testing fallback behavior
    # for missing attribute was testing an impossible scenario.

    def test_engage_distance_multiplier(self, spatial_grid, create_test_ship):
        """AI calculates engage distance correctly."""
        ship1 = create_test_ship("Ally", 0, 0, team_id=0)

        spatial_grid.insert(ship1)

        ai_controller = AIController(ShipControllableAdapter(ship1), spatial_grid, enemy_team_id=1)

        # Test various engage distance configs
        assert ai_controller.get_engage_distance_multiplier({'engage_distance': 'max_range'}) == 1.0
        assert ai_controller.get_engage_distance_multiplier({'engage_distance': 'ram'}) == 0.0
        assert ai_controller.get_engage_distance_multiplier({'engage_distance': 0.5}) == 0.5


class TestSecondaryTargets:
    """Tests for multiplex tracking (multiple targets)."""

    def test_no_secondary_targets_by_default(self, spatial_grid, create_test_ship):
        """Ships with max_targets=1 have no secondary targets."""
        ship1 = create_test_ship("Ally", 0, 0, team_id=0)
        enemy1 = create_test_ship("Enemy1", 500, 0, team_id=1)
        enemy2 = create_test_ship("Enemy2", 600, 0, team_id=1)

        spatial_grid.insert(ship1)
        spatial_grid.insert(enemy1)
        spatial_grid.insert(enemy2)

        ship1.max_targets = 1

        ai_controller = AIController(ShipControllableAdapter(ship1), spatial_grid, enemy_team_id=1)
        ai_controller.update()

        assert ship1.secondary_targets == []

    def test_finds_secondary_targets_if_capable(self, spatial_grid, create_test_ship):
        """Ships with max_targets>1 acquire secondary targets."""
        ship1 = create_test_ship("Ally", 0, 0, team_id=0)
        enemy1 = create_test_ship("Enemy1", 500, 0, team_id=1)
        enemy2 = create_test_ship("Enemy2", 600, 0, team_id=1)

        spatial_grid.insert(ship1)
        spatial_grid.insert(enemy1)
        spatial_grid.insert(enemy2)

        ship1.max_targets = 3

        ai_controller = AIController(ShipControllableAdapter(ship1), spatial_grid, enemy_team_id=1)
        ai_controller.update()

        # Should have primary + secondary
        assert ship1.current_target is not None
        assert len(ship1.secondary_targets) == 1

    def test_secondary_excludes_primary(self, spatial_grid, create_test_ship):
        """Secondary targets don't include primary target."""
        ship1 = create_test_ship("Ally", 0, 0, team_id=0)
        enemy1 = create_test_ship("Enemy1", 500, 0, team_id=1)
        enemy2 = create_test_ship("Enemy2", 600, 0, team_id=1)
        enemy3 = create_test_ship("Enemy3", 700, 0, team_id=1)

        spatial_grid.insert(ship1)
        spatial_grid.insert(enemy1)
        spatial_grid.insert(enemy2)
        spatial_grid.insert(enemy3)

        ship1.max_targets = 3

        ai_controller = AIController(ShipControllableAdapter(ship1), spatial_grid, enemy_team_id=1)
        ai_controller.update()

        # Primary should not be in secondary list
        assert ship1.current_target not in ship1.secondary_targets
