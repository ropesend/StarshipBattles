import pytest
import pygame
import json
from unittest.mock import MagicMock, patch
from game.ai.strategy_manager import StrategyManager, get_default_strategy_manager
from game.ai.target_evaluator import TargetEvaluator
from tests.fixtures.paths import get_unit_test_data_dir


@pytest.fixture
def strategy_system_setup():
    # Setup StrategyManager with test data
    manager = get_default_strategy_manager()
    manager.clear()
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


class TestResolveStrategyFallbackChain:
    """TCG-FND-013: Tests for StrategyManager.resolve_strategy() default fallback chain.

    Tests verify that:
    - Valid strategy with valid policies works
    - Strategy referencing missing targeting policy falls back to default
    - Strategy referencing missing movement policy falls back to default
    - Missing strategy falls back to full defaults
    """

    @pytest.fixture
    def isolated_manager(self):
        """Create an isolated StrategyManager with minimal test data."""
        manager = StrategyManager()

        # Manually set up test data instead of loading from files
        manager.targeting_policies = {
            'valid_targeting': {'name': 'ValidTargeting', 'rules': [{'type': 'nearest', 'weight': 50}]}
        }
        manager.movement_policies = {
            'valid_movement': {'behavior': 'charge', 'engage_distance': 100}
        }
        manager.strategies = {
            'valid_strategy': {
                'name': 'ValidStrategy',
                'targeting_policy': 'valid_targeting',
                'movement_policy': 'valid_movement'
            },
            'strategy_missing_targeting': {
                'name': 'MissingTargeting',
                'targeting_policy': 'nonexistent_targeting_policy',
                'movement_policy': 'valid_movement'
            },
            'strategy_missing_movement': {
                'name': 'MissingMovement',
                'targeting_policy': 'valid_targeting',
                'movement_policy': 'nonexistent_movement_policy'
            },
            'strategy_missing_both': {
                'name': 'MissingBoth',
                'targeting_policy': 'typo_targeting',
                'movement_policy': 'typo_movement'
            }
        }
        manager._loaded = True

        yield manager

    def test_resolve_valid_strategy_with_valid_policies(self, isolated_manager):
        """Valid strategy with valid policies returns expected data."""
        resolved = isolated_manager.resolve_strategy('valid_strategy')

        assert resolved['definition']['name'] == 'ValidStrategy'
        assert resolved['targeting']['name'] == 'ValidTargeting'
        assert resolved['movement']['behavior'] == 'charge'

    def test_resolve_strategy_with_missing_targeting_policy_uses_default(self, isolated_manager):
        """Strategy referencing typo'd targeting policy falls back to default."""
        resolved = isolated_manager.resolve_strategy('strategy_missing_targeting')

        # Definition should be the strategy itself
        assert resolved['definition']['name'] == 'MissingTargeting'

        # Targeting should be the DEFAULT, not the nonexistent one
        assert resolved['targeting']['name'] == 'Default'
        assert resolved['targeting']['rules'] == [{'type': 'nearest', 'weight': 100}]

        # Movement should still be valid
        assert resolved['movement']['behavior'] == 'charge'

    def test_resolve_strategy_with_missing_movement_policy_uses_default(self, isolated_manager):
        """Strategy referencing typo'd movement policy falls back to default."""
        resolved = isolated_manager.resolve_strategy('strategy_missing_movement')

        # Definition should be the strategy itself
        assert resolved['definition']['name'] == 'MissingMovement'

        # Targeting should be valid
        assert resolved['targeting']['name'] == 'ValidTargeting'

        # Movement should be the DEFAULT
        assert resolved['movement']['behavior'] == 'kite'
        assert resolved['movement']['avoid_collisions'] is True

    def test_resolve_strategy_with_both_policies_missing_uses_defaults(self, isolated_manager):
        """Strategy referencing both typo'd policies falls back to defaults for both."""
        resolved = isolated_manager.resolve_strategy('strategy_missing_both')

        # Definition should be the strategy itself
        assert resolved['definition']['name'] == 'MissingBoth'

        # Both should be defaults
        assert resolved['targeting']['name'] == 'Default'
        assert resolved['movement']['behavior'] == 'kite'

    def test_resolve_missing_strategy_uses_full_defaults(self, isolated_manager):
        """Completely missing strategy falls back to default strategy and default policies."""
        resolved = isolated_manager.resolve_strategy('completely_nonexistent_strategy')

        # Definition should be the default strategy
        assert resolved['definition']['name'] == 'Default'
        assert resolved['definition']['targeting_policy'] == 'standard'
        assert resolved['definition']['movement_policy'] == 'kite_max'

        # Policies should also be defaults (since 'standard' and 'kite_max' don't exist)
        assert resolved['targeting']['name'] == 'Default'
        assert resolved['movement']['behavior'] == 'kite'

    def test_default_policy_names_documented(self, isolated_manager):
        """Verify that default policy objects contain expected field names.

        This documents the contract for what fields default policies must have.
        """
        defaults = isolated_manager.defaults

        # Default targeting must have 'name' and 'rules'
        assert 'name' in defaults['targeting']
        assert 'rules' in defaults['targeting']

        # Default movement must have 'behavior'
        assert 'behavior' in defaults['movement']

        # Default strategy must have policy references
        assert 'targeting_policy' in defaults['strategy']
        assert 'movement_policy' in defaults['strategy']
