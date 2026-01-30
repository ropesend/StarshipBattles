"""
Tests for target evaluation integration scenarios.

This test file covers:
- Required flag behavior
- Multiple rules combination
- Custom stat helpers
- Default stat helpers
- Edge cases
- Threat assessment scenarios
"""
import pytest
import pygame
from unittest.mock import MagicMock
from game.ai.target_evaluator import TargetEvaluator
from game.core.constants import AttackType


# =============================================================================
# Test: Required Flag
# =============================================================================

class TestRequiredFlag:
    """Tests for the 'required' flag behavior."""

    def test_required_true_fails_returns_neg_inf(self, ship):
        """Failed required rule should return -inf."""
        target = MagicMock()
        target.position = pygame.math.Vector2(100, 0)
        target.get_components_by_ability = MagicMock(return_value=[])

        rules = [{'type': 'has_weapons', 'required': True, 'weight': 100}]

        score = TargetEvaluator.evaluate(ship, target, rules)

        assert score == -float('inf')

    def test_required_false_does_not_fail(self, ship):
        """Non-required rule failure should not return -inf."""
        target = MagicMock()
        target.position = pygame.math.Vector2(100, 0)
        target.get_components_by_ability = MagicMock(return_value=[])

        rules = [{'type': 'has_weapons', 'required': False, 'weight': 100}]

        score = TargetEvaluator.evaluate(ship, target, rules)

        assert score != -float('inf')


# =============================================================================
# Test: Multiple Rules
# =============================================================================

class TestMultipleRules:
    """Tests for combining multiple rules."""

    def test_multiple_rules_additive(self, ship, target):
        """Multiple rules should add their scores."""
        rules = [
            {'type': 'nearest', 'weight': 1},  # -100
            {'type': 'mass', 'weight': 0.1}     # 100
        ]

        score = TargetEvaluator.evaluate(ship, target, rules)

        # -100 + 100 = 0
        assert score == -100 + 100

    def test_required_rule_early_terminates(self, ship):
        """A failing required rule should prevent other rules from counting."""
        target = MagicMock()
        target.position = pygame.math.Vector2(100, 0)
        target.get_components_by_ability = MagicMock(return_value=[])

        rules = [
            {'type': 'has_weapons', 'required': True, 'weight': 100},
            {'type': 'nearest', 'weight': 1000}  # Would give huge score
        ]

        score = TargetEvaluator.evaluate(ship, target, rules)

        assert score == -float('inf')


# =============================================================================
# Test: Custom Stat Helpers
# =============================================================================

class TestCustomStatHelpers:
    """Tests for custom stat helper functions."""

    def test_custom_get_hp_percent(self, ship, target):
        """Custom HP percent function should be used."""
        custom_helpers = {
            'get_hp_percent': lambda t: 0.25,  # Always returns 25%
            'is_in_pdc_arc': lambda s, t: True
        }

        rules = [{'type': 'most_damaged', 'weight': 1}]

        score = TargetEvaluator.evaluate(ship, target, rules, stat_helpers=custom_helpers)

        # val = -0.25 * 1 * 100 = -25
        assert score == -25

    def test_custom_is_in_pdc_arc(self, ship):
        """Custom PDC arc function should be used."""
        missile = MagicMock()
        missile.position = pygame.math.Vector2(-1000, -1000)  # Very far away
        missile.type = AttackType.MISSILE

        custom_helpers = {
            'get_hp_percent': lambda t: 1.0,
            'is_in_pdc_arc': lambda s, t: True  # Always returns True
        }

        rules = [{'type': 'pdc_arc', 'weight': 100}]

        score = TargetEvaluator.evaluate(ship, missile, rules, stat_helpers=custom_helpers)

        assert score == 100


# =============================================================================
# Test: Default Stat Helpers
# =============================================================================

class TestDefaultStatHelpers:
    """Tests for default stat helper implementations."""

    def test_default_get_hp_percent_no_components(self):
        """Default get_hp_percent should return 1.0 for no components."""
        target = MagicMock()
        target.get_all_components = MagicMock(return_value=[])

        result = TargetEvaluator._default_get_hp_percent(target)

        assert result == 1.0

    def test_default_get_hp_percent_calculates_correctly(self):
        """Default get_hp_percent should calculate HP correctly."""
        target = MagicMock()
        comp1 = MagicMock()
        comp1.max_hp = 100
        comp1.current_hp = 50

        comp2 = MagicMock()
        comp2.max_hp = 100
        comp2.current_hp = 25

        target.get_all_components = MagicMock(return_value=[comp1, comp2])

        result = TargetEvaluator._default_get_hp_percent(target)

        # (50 + 25) / (100 + 100) = 0.375
        assert result == 0.375

    def test_default_is_in_pdc_arc_no_pdc_weapons(self, ship, target):
        """Default is_in_pdc_arc should return False with no PDC weapons."""
        ship.get_components_by_ability = MagicMock(return_value=[])

        result = TargetEvaluator._default_is_in_pdc_arc(ship, target)

        assert result == False


# =============================================================================
# Test: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_rules_returns_zero(self, ship, target):
        """Empty rules list should return score of 0."""
        score = TargetEvaluator.evaluate(ship, target, [])

        assert score == 0

    def test_unknown_rule_type_ignored(self, ship, target):
        """Unknown rule types should be silently ignored."""
        rules = [{'type': 'unknown_rule_xyz', 'weight': 1000}]

        score = TargetEvaluator.evaluate(ship, target, rules)

        assert score == 0

    def test_missing_weight_uses_zero(self, ship, target):
        """Missing weight should default to 0."""
        rules = [{'type': 'nearest'}]  # No weight specified

        score = TargetEvaluator.evaluate(ship, target, rules)

        # weight=0 means val = dist * factor (factor default 1) = 100
        assert score == 100

    def test_missing_factor_uses_one(self, ship, target):
        """Missing factor should default to 1."""
        rules = [{'type': 'distance'}]  # No factor specified

        score = TargetEvaluator.evaluate(ship, target, rules)

        # factor=1 => 100 * 1 = 100
        assert score == 100

    def test_same_position_zero_distance(self, ship, target):
        """Same position should have zero distance."""
        target.position = pygame.math.Vector2(0, 0)
        rules = [{'type': 'distance', 'factor': 1}]

        score = TargetEvaluator.evaluate(ship, target, rules)

        assert score == 0

    def test_negative_weight(self, ship, target):
        """Negative weight should work correctly."""
        rules = [{'type': 'mass', 'weight': -1}]

        score = TargetEvaluator.evaluate(ship, target, rules)

        # weight <= 0 uses factor instead, so mass * factor (default 1)
        assert score == 1000

    def test_very_large_distance(self, ship):
        """Very large distances should work."""
        far_target = MagicMock()
        far_target.position = pygame.math.Vector2(1000000, 1000000)

        rules = [{'type': 'nearest', 'weight': 1}]

        score = TargetEvaluator.evaluate(ship, far_target, rules)

        # Should be negative and large
        assert score < -1000000


# =============================================================================
# Test: Threat Assessment
# =============================================================================

class TestThreatAssessment:
    """Tests for threat assessment scenarios."""

    def test_armed_damaged_target_high_priority(self, ship):
        """Armed and damaged targets should be high priority with appropriate rules."""
        target = MagicMock()
        target.position = pygame.math.Vector2(100, 0)
        target.get_components_by_ability = MagicMock(return_value=[MagicMock()])

        comp = MagicMock()
        comp.max_hp = 100
        comp.current_hp = 20
        target.get_all_components = MagicMock(return_value=[comp])

        rules = [
            {'type': 'has_weapons', 'weight': 100},
            {'type': 'most_damaged', 'weight': 1}
        ]

        score = TargetEvaluator.evaluate(ship, target, rules)

        # has_weapons: 100
        # most_damaged: -0.2 * 1 * 100 = -20
        # total: 80
        assert score == 80

    def test_close_fast_target_high_threat(self, ship):
        """Close fast targets should be high threat with appropriate rules."""
        target = MagicMock()
        target.position = pygame.math.Vector2(50, 0)
        target.velocity = pygame.math.Vector2(100, 0)

        rules = [
            {'type': 'nearest', 'weight': 1},
            {'type': 'fastest', 'weight': 0.5}
        ]

        score = TargetEvaluator.evaluate(ship, target, rules)

        # nearest: -50
        # fastest: 100 * 0.5 = 50
        # total: 0
        assert score == 0
