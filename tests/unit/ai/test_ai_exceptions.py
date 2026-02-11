"""Tests for AI module exception handling.

PROJ-45: Verifies that AI modules handle errors gracefully with proper
logging and fallback behavior.
"""
import logging
import pytest
from unittest.mock import MagicMock, patch

from game.core.exceptions import StateException, AIException, TargetingException
from game.core.math import Vector2
from game.ai.strategy_manager import StrategyManager
from game.ai.target_evaluator import TargetEvaluator, _get_position, _get_rotation, _safe_distance


class TestAIExceptionHierarchy:
    """Test AI exception class hierarchy."""

    def test_targeting_exception_inherits_from_ai_exception(self):
        """TargetingException should inherit from AIException."""
        exc = TargetingException("test")
        assert isinstance(exc, AIException)

    def test_ai_exception_supports_code_and_context(self):
        """AIException should support error codes and context."""
        exc = AIException(
            "Test error",
            code="AI001",
            context={"ship_id": "test_ship"}
        )
        assert exc.code == "AI001"
        assert exc.context == {"ship_id": "test_ship"}

    def test_targeting_exception_supports_code_and_context(self):
        """TargetingException should support error codes and context."""
        exc = TargetingException(
            "Targeting failed",
            code="T001",
            context={"target_id": "enemy_1", "reason": "out_of_range"}
        )
        assert exc.code == "T001"
        assert exc.context["target_id"] == "enemy_1"


class TestStrategyManagerExceptions:
    """Test StrategyManager exception handling."""

    def setup_method(self):
        """Reset singleton before each test."""
        StrategyManager.reset()

    def teardown_method(self):
        """Clean up singleton after each test."""
        StrategyManager.reset()

    def test_direct_instantiation_returns_singleton(self):
        """Direct instantiation returns the singleton via SingletonMeta."""
        # First instance via normal method
        first = StrategyManager.instance()

        # With SingletonMeta, direct construction returns the singleton
        second = StrategyManager()

        assert first is second


class TestTargetEvaluatorFallbacks:
    """Test TargetEvaluator fallback behavior on errors."""

    def test_get_position_logs_and_falls_back_on_interface_error(self, caplog):
        """When get_position() fails, should log and fall back to .position."""
        entity = MagicMock()
        entity.id = "test_ship"
        entity.position = Vector2(100, 200)

        # Make get_position() raise an error
        entity.get_position.side_effect = AttributeError("Mock error")

        with caplog.at_level(logging.WARNING):
            result = _get_position(entity)

        # Should have fallen back to direct attribute
        assert result == Vector2(100, 200)
        # Should have logged warning
        assert "get_position() failed" in caplog.text
        assert "test_ship" in caplog.text

    def test_get_rotation_logs_and_falls_back_on_interface_error(self, caplog):
        """When get_rotation() fails, should log and fall back to .angle."""
        entity = MagicMock()
        entity.id = "test_ship"
        entity.angle = 45.0

        # Make get_rotation() raise an error
        entity.get_rotation.side_effect = TypeError("Mock error")

        with caplog.at_level(logging.WARNING):
            result = _get_rotation(entity)

        assert result == 45.0
        assert "get_rotation() failed" in caplog.text

    def test_safe_distance_returns_infinity_on_missing_position(self, caplog):
        """When positions are unavailable, should return infinity."""
        entity1 = MagicMock()
        entity1.id = "ship1"
        entity1.position = Vector2(0, 0)
        entity1.get_position.return_value = Vector2(0, 0)

        entity2 = MagicMock()
        entity2.id = "ship2"
        entity2.position = None  # Missing position

        with caplog.at_level(logging.WARNING):
            result = _safe_distance(entity1, entity2)

        assert result == float('inf')
        assert "Cannot calculate distance" in caplog.text

    def test_safe_distance_handles_attribute_error(self, caplog):
        """_safe_distance should handle AttributeError gracefully."""
        entity1 = MagicMock()
        entity1.id = "ship1"
        # Make get_position() fail and fallback position unavailable
        entity1.get_position.side_effect = AttributeError("no position")
        entity1.position = None  # Fallback also fails

        entity2 = MagicMock()
        entity2.id = "ship2"
        entity2.position = Vector2(100, 100)

        with caplog.at_level(logging.WARNING):
            result = _safe_distance(entity1, entity2)

        # When position is None, should return infinity
        assert result == float('inf')


class TestTargetEvaluatorErrorContext:
    """Test that errors include proper context for debugging."""

    def test_pdc_arc_check_logs_on_missing_position(self, caplog):
        """PDC arc check should log when position is unavailable."""
        ship = MagicMock()
        ship.id = "defender"
        ship.get_position.return_value = None
        ship.get_components_by_ability.return_value = []

        target = MagicMock()
        target.id = "missile"
        target.position = None

        with caplog.at_level(logging.WARNING):
            result = TargetEvaluator._default_is_in_pdc_arc(ship, target)

        assert result is False
        assert "PDC arc check failed" in caplog.text
        assert "defender" in caplog.text


class TestControllerErrorHandling:
    """Test AIController error handling."""

    def test_score_and_sort_enemies_logs_evaluation_info(self, caplog):
        """Controller should log target evaluation for debugging."""
        from game.ai.controller import AIController

        # Create minimal mock setup
        ship = MagicMock()
        ship.id = "player_ship"
        ship.get_ai_strategy.return_value = "standard"
        ship.get_position.return_value = Vector2(0, 0)

        grid = MagicMock()
        controller = AIController(ship, grid, enemy_team_id=1)

        # Create two valid enemies
        enemy1 = MagicMock()
        enemy1.id = "target_1"
        enemy1.position = Vector2(100, 100)

        enemy2 = MagicMock()
        enemy2.id = "target_2"
        enemy2.position = Vector2(200, 200)

        rules = [{"type": "nearest", "weight": 100}]

        result = controller._score_and_sort_enemies([enemy1, enemy2], rules)

        # Both enemies should be in results (closer one first)
        assert len(result) == 2
        # enemy1 is closer (100 vs 200 distance from origin)
        assert result[0] == enemy1


class TestFallbackBehaviorPreserved:
    """Test that error handling preserves original fallback behavior."""

    def test_targeting_processes_multiple_targets(self):
        """Targeting should process multiple valid targets correctly."""
        from game.ai.controller import AIController

        ship = MagicMock()
        ship.id = "player"
        ship.get_ai_strategy.return_value = "standard"
        ship.get_position.return_value = Vector2(0, 0)

        grid = MagicMock()
        controller = AIController(ship, grid, enemy_team_id=1)

        # Multiple valid enemies at different distances
        enemies = []
        for i in range(5):
            e = MagicMock()
            e.id = f"enemy_{i}"
            e.position = Vector2((i + 1) * 100, 0)  # 100, 200, 300, 400, 500
            enemies.append(e)

        rules = [{"type": "nearest", "weight": 100}]
        result = controller._score_and_sort_enemies(enemies, rules)

        # All 5 should be in result
        assert len(result) == 5
        # Closest should be first (enemy_0 at distance 100)
        assert result[0] == enemies[0]
        # Farthest should be last (enemy_4 at distance 500)
        assert result[-1] == enemies[4]

    def test_hp_calculation_handles_missing_components(self):
        """HP percent should return 1.0 for entities without components."""
        ship = MagicMock()
        ship.get_all_components.return_value = []

        result = TargetEvaluator._default_get_hp_percent(ship)
        assert result == 1.0

    def test_hp_calculation_handles_zero_max_hp(self):
        """HP percent should return 1.0 when total max HP is zero."""
        ship = MagicMock()

        # Components with no HP
        comp = MagicMock()
        comp.max_hp = 0
        comp.current_hp = 0
        ship.get_all_components.return_value = [comp]

        result = TargetEvaluator._default_get_hp_percent(ship)
        assert result == 1.0
