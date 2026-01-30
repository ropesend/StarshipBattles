import pytest
import pygame
import json
from unittest.mock import MagicMock, patch
from game.ai.strategy_manager import StrategyManager
from game.ai.target_evaluator import TargetEvaluator
from tests.fixtures.paths import get_unit_test_data_dir


@pytest.fixture
def strategy_system_setup():
    # Setup StrategyManager with test data
    # Reset singleton to get a fresh instance
    StrategyManager.reset()
    manager = StrategyManager.instance()
    # Point to unit_tests/data which we populated earlier
    unit_test_data_dir = get_unit_test_data_dir()
    manager.load_data(
        str(unit_test_data_dir),
        targeting_file="test_targeting_policies.json",
        movement_file="test_movement_policies.json",
        strategy_file="test_combat_strategies.json"
    )
    # Mark as loaded to prevent ensure_loaded() from overwriting with production data
    manager._loaded = True

    yield {'manager': manager}

    pygame.quit()


class TestStrategySystem:
    """Tests for AI strategy system data loading and strategy selection."""

    def test_load_data(self, strategy_system_setup):
        """Verify data loading from test files."""
        manager = strategy_system_setup['manager']
        # Check if test policies loaded
        assert 'test_policy_1' in manager.targeting_policies
        assert 'test_move_kite' in manager.movement_policies
        assert 'test_strat_simple' in manager.strategies

        strat = manager.get_strategy('test_strat_simple')
        assert strat['name'] == "Test Strategy Simple"

    def test_resolve_strategy(self, strategy_system_setup):
        """Verify strategy resolution links policies correctly."""
        manager = strategy_system_setup['manager']
        resolved = manager.resolve_strategy('test_strat_simple')
        assert resolved['definition']['name'] == "Test Strategy Simple"
        assert resolved['targeting']['name'] == "Test Policy 1"
        assert resolved['movement']['behavior'] == "kite"

    def test_target_evaluator_nearest(self, strategy_system_setup):
        """Verify 'nearest' rule scoring."""
        # Mock ships
        me = MagicMock()
        me.position = pygame.math.Vector2(0, 0)

        target_near = MagicMock()
        target_near.position = pygame.math.Vector2(100, 0)

        target_far = MagicMock()
        target_far.position = pygame.math.Vector2(500, 0)

        rules = [{'type': 'nearest', 'weight': 100}]

        # Lower distance should act as penalty if we subtract dist*weight?
        # In current logic: val = -dist * weight. So closer (smaller dist) is less negative (higher score).

        score_near = TargetEvaluator.evaluate(me, target_near, rules)
        score_far = TargetEvaluator.evaluate(me, target_far, rules)

        assert score_near > score_far, "Closer target should have higher score"

    def test_target_evaluator_complex(self, strategy_system_setup):
        """Verify complex rule interactions."""
        me = MagicMock()
        me.position = pygame.math.Vector2(0, 0)

        # Target 1: Far but has weapons
        # Mock Ship helper methods used by TargetEvaluator
        t1 = MagicMock(spec=['position', 'mass', 'get_components_by_ability'])
        t1.position = pygame.math.Vector2(1000, 0)
        t1.mass = 100
        # Mock has_weapons logic: get_components_by_ability returns a component
        c1 = MagicMock()
        c1.damage = 10
        c1.has_ability = lambda name: name == 'WeaponAbility'
        t1.get_components_by_ability.return_value = [c1]

        # Target 2: Near but no weapons
        t2 = MagicMock(spec=['position', 'mass', 'get_components_by_ability'])
        t2.position = pygame.math.Vector2(100, 0)
        t2.mass = 100
        t2.get_components_by_ability.return_value = []

        # Rules: has_weapons (1000) > distance (factor -1)
        # T1 score ~= 1000 - 1000 = 0
        # T2 score ~= 0 - 100 = -100
        # T1 should win

        rules = [
            {"type": "has_weapons", "weight": 1000},
            {"type": "distance", "factor": -1}
        ]

        score_t1 = TargetEvaluator.evaluate(me, t1, rules)
        score_t2 = TargetEvaluator.evaluate(me, t2, rules)

        assert score_t1 > score_t2, "Target with weapons should be preferred despite distance"
