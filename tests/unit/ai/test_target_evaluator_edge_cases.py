"""
Unit tests for TargetEvaluator edge cases.

Tests cover:
- Zero weight rules
- Required flag behavior
- Empty rules handling
- Position edge cases
- Distance cache usage
"""
import pytest
from unittest.mock import MagicMock

from game.ai.target_evaluator import TargetEvaluator
from game.core.math import Vector2


@pytest.fixture
def mock_ship():
    """Create a mock ship for targeting tests."""
    ship = MagicMock()
    ship.id = 'ship_1'
    ship.get_position = MagicMock(return_value=Vector2(0, 0))
    ship.position = Vector2(0, 0)
    ship.mass = 100
    ship.velocity = Vector2(0, 0)
    ship.type = 'ship'
    ship.get_components_by_ability = MagicMock(return_value=[])
    ship.get_components_by_layer = MagicMock(return_value=[])
    return ship


@pytest.fixture
def mock_target():
    """Create a mock target for evaluation."""
    target = MagicMock()
    target.id = 'target_1'
    target.get_position = MagicMock(return_value=Vector2(100, 0))
    target.position = Vector2(100, 0)
    target.mass = 50
    target.velocity = Vector2(0, 0)
    target.type = 'ship'
    target.get_components_by_ability = MagicMock(return_value=[])
    target.get_components_by_layer = MagicMock(return_value=[])
    return target


@pytest.fixture
def mock_stat_helpers():
    """Create mock stat helper functions."""
    return {
        'get_hp_percent': lambda x: 0.75,
        'is_in_pdc_arc': lambda ship, target: True
    }


class TestEvaluateZeroWeight:
    """Tests for zero weight rules behavior."""

    def test_zero_weight_nearest_rule(self, mock_ship, mock_target, mock_stat_helpers):
        """Zero weight 'nearest' rule uses factor instead."""
        rules = [{'type': 'nearest', 'weight': 0, 'factor': 1}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        # With weight=0, uses factor. Distance is 100, so score = 100 * 1 = 100
        assert score == pytest.approx(100.0)

    def test_zero_weight_mass_rule(self, mock_ship, mock_target, mock_stat_helpers):
        """Zero weight 'mass' rule uses factor instead."""
        rules = [{'type': 'mass', 'weight': 0, 'factor': 2}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        # With weight=0, uses factor. Mass is 50, so score = 50 * 2 = 100
        assert score == pytest.approx(100.0)


class TestEvaluateRequiredFlag:
    """Tests for required flag behavior."""

    def test_required_flag_rejects_when_not_met(self, mock_ship, mock_target, mock_stat_helpers):
        """Required rule with failed condition returns -inf."""
        # has_weapons rule with required=True, target has no weapons
        mock_target.get_components_by_ability = MagicMock(return_value=[])

        rules = [{'type': 'has_weapons', 'weight': 100, 'required': True}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == float('-inf')

    def test_required_flag_accepts_when_met(self, mock_ship, mock_target, mock_stat_helpers):
        """Required rule with met condition allows scoring."""
        # has_weapons rule with required=True, target HAS weapons
        mock_weapon = MagicMock()
        mock_target.get_components_by_ability = MagicMock(return_value=[mock_weapon])

        rules = [{'type': 'has_weapons', 'weight': 100, 'required': True}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        # Should have positive score
        assert score > 0
        assert score != float('-inf')

    def test_non_required_continues_on_failure(self, mock_ship, mock_target, mock_stat_helpers):
        """Non-required rule continues evaluation even when condition fails."""
        mock_target.get_components_by_ability = MagicMock(return_value=[])

        # has_weapons without required flag
        rules = [
            {'type': 'has_weapons', 'weight': 100, 'required': False},
            {'type': 'nearest', 'weight': 10}
        ]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        # Should not be -inf
        assert score != float('-inf')


class TestEvaluateEmptyRules:
    """Tests for empty rules handling."""

    def test_empty_rules_returns_zero(self, mock_ship, mock_target, mock_stat_helpers):
        """No rules returns base score of 0."""
        rules = []

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == 0


class TestEvaluateDistanceCache:
    """Tests for distance cache usage."""

    def test_distance_cache_used_when_provided(self, mock_ship, mock_target, mock_stat_helpers):
        """Pre-computed distance cache is used instead of recalculating."""
        rules = [{'type': 'nearest', 'weight': 1}]

        # Provide cached distance of 50 (different from actual 100)
        distance_cache = {mock_target: 50.0}

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers,
            distance_cache=distance_cache
        )

        # With weight=1 and nearest, score = -dist * weight = -50
        assert score == pytest.approx(-50.0)

    def test_distance_calculated_when_cache_missing(self, mock_ship, mock_target, mock_stat_helpers):
        """Distance is calculated when target not in cache."""
        rules = [{'type': 'nearest', 'weight': 1}]

        # Cache doesn't include this target
        distance_cache = {}

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers,
            distance_cache=distance_cache
        )

        # Should calculate actual distance (100) and use it
        # nearest with weight=1: score = -dist * weight = -100
        assert score == pytest.approx(-100.0)


class TestEvaluateCapabilitiesCache:
    """Tests for ship capabilities cache usage."""

    def test_capabilities_cache_used_for_has_weapons(self, mock_ship, mock_target, mock_stat_helpers):
        """Pre-computed capabilities cache is used for has_weapons check."""
        rules = [{'type': 'has_weapons', 'weight': 100}]

        # Provide cached has_weapons = True
        capabilities_cache = {mock_target.id: {'has_weapons': True}}

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers,
            ship_capabilities_cache=capabilities_cache
        )

        # Should use cached value and return positive score
        assert score == pytest.approx(100.0)


class TestEvaluateMissileRules:
    """Tests for PDC arc rules with missiles."""

    def test_pdc_arc_non_missile_passes_through(self, mock_ship, mock_target, mock_stat_helpers):
        """PDC arc rule passes through for non-missile targets."""
        mock_target.type = 'ship'  # Not a missile

        rules = [{'type': 'pdc_arc', 'weight': 100, 'required': True}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        # Non-missile should pass through (score 0, not -inf)
        assert score == 0
        assert score != float('-inf')

    def test_pdc_arc_missile_in_arc(self, mock_ship, mock_target, mock_stat_helpers):
        """PDC arc rule scores missile in arc."""
        mock_target.type = 'missile'
        mock_stat_helpers['is_in_pdc_arc'] = lambda ship, target: True

        rules = [{'type': 'pdc_arc', 'weight': 500}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(500.0)

    def test_pdc_arc_missile_not_in_arc_required(self, mock_ship, mock_target, mock_stat_helpers):
        """PDC arc required rule rejects missile not in arc."""
        mock_target.type = 'missile'
        mock_stat_helpers['is_in_pdc_arc'] = lambda ship, target: False

        rules = [{'type': 'pdc_arc', 'weight': 500, 'required': True}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == float('-inf')


class TestEvaluateMultipleRules:
    """Tests for multiple rules combination."""

    def test_scores_accumulate(self, mock_ship, mock_target, mock_stat_helpers):
        """Multiple rules accumulate scores."""
        mock_weapon = MagicMock()
        mock_target.get_components_by_ability = MagicMock(return_value=[mock_weapon])

        rules = [
            {'type': 'nearest', 'weight': 1},     # -100
            {'type': 'mass', 'weight': 1},        # +50
            {'type': 'has_weapons', 'weight': 100}  # +100
        ]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        # -100 + 50 + 100 = 50
        assert score == pytest.approx(50.0)

    def test_required_short_circuits(self, mock_ship, mock_target, mock_stat_helpers):
        """Required rule failure short-circuits remaining rules."""
        # First rule passes, second (required) fails
        mock_target.get_components_by_ability = MagicMock(return_value=[])

        rules = [
            {'type': 'nearest', 'weight': 1},
            {'type': 'has_weapons', 'weight': 100, 'required': True},
            {'type': 'mass', 'weight': 1000}  # Would add a lot, but won't be reached
        ]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == float('-inf')


class TestEvaluateDefaultStatHelpers:
    """Tests for default stat helpers usage."""

    def test_uses_default_helpers_when_none_provided(self, mock_ship, mock_target):
        """Evaluate uses default stat helpers when not provided."""
        rules = [{'type': 'most_damaged', 'weight': 100}]

        # Mock the HP for the target
        mock_target.hp = 50
        mock_target.max_hp = 100

        # Should not crash - uses default get_hp_percent
        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules
        )

        assert isinstance(score, float)
