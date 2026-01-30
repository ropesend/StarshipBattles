"""
Tests for ship capabilities caching in target evaluation.

PROJ-49 Phase 6: O(n^2) Targeting Optimization

This module tests the ship_capabilities_cache parameter added to TargetEvaluator.evaluate()
to avoid redundant component lookups across multiple targets.
"""
import pytest
import pygame
from unittest.mock import MagicMock, call

from game.ai.target_evaluator import TargetEvaluator


@pytest.fixture(autouse=True)
def pygame_init():
    """Initialize pygame for Vector2 usage."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def ship():
    """Create a mock ship for testing."""
    s = MagicMock()
    s.position = pygame.math.Vector2(0, 0)
    s.angle = 0
    s.team_id = 0
    s.get_components_by_ability = MagicMock(return_value=[])
    return s


@pytest.fixture
def target_with_weapons():
    """Create a target with weapon components."""
    t = MagicMock()
    t.id = 'target_armed'
    t.position = pygame.math.Vector2(100, 0)
    t.mass = 1000
    t.type = 'ship'

    # Mock weapon component
    weapon = MagicMock()
    weapon.has_ability = MagicMock(return_value=False)  # Not a PDC
    t.get_components_by_ability = MagicMock(return_value=[weapon])

    return t


@pytest.fixture
def target_without_weapons():
    """Create a target without weapon components."""
    t = MagicMock()
    t.id = 'target_unarmed'
    t.position = pygame.math.Vector2(100, 0)
    t.mass = 1000
    t.type = 'ship'
    t.get_components_by_ability = MagicMock(return_value=[])

    return t


class TestCapabilitiesCacheParameter:
    """Tests for ship_capabilities_cache parameter in TargetEvaluator.evaluate()."""

    def test_evaluate_accepts_capabilities_cache_parameter(self, ship, target_with_weapons):
        """TargetEvaluator.evaluate() should accept ship_capabilities_cache parameter."""
        rules = [{'type': 'nearest', 'weight': 1}]
        cache = {}

        # Should not raise
        score = TargetEvaluator.evaluate(
            ship, target_with_weapons, rules,
            distance_cache=None,
            ship_capabilities_cache=cache
        )

        assert isinstance(score, (int, float))

    def test_evaluate_works_without_capabilities_cache(self, ship, target_with_weapons):
        """TargetEvaluator.evaluate() should work when ship_capabilities_cache is None."""
        rules = [{'type': 'has_weapons', 'weight': 100}]

        # Should not raise when cache is None
        score = TargetEvaluator.evaluate(ship, target_with_weapons, rules)

        assert score == 100  # Armed target with weight=100


class TestHasWeaponsCacheUsage:
    """Tests for has_weapons rule using capabilities cache."""

    def test_has_weapons_uses_cache_when_available(self, ship, target_with_weapons):
        """has_weapons rule should use cached value instead of calling get_components_by_ability."""
        rules = [{'type': 'has_weapons', 'weight': 100}]

        # Pre-populate cache
        cache = {
            target_with_weapons.id: {
                'has_weapons': True,
                'weapon_components': [MagicMock()],
                'has_pdc': False,
                'pdc_components': [],
            }
        }

        # Reset mock call count
        target_with_weapons.get_components_by_ability.reset_mock()

        score = TargetEvaluator.evaluate(
            ship, target_with_weapons, rules,
            ship_capabilities_cache=cache
        )

        # Should NOT have called get_components_by_ability (used cache)
        target_with_weapons.get_components_by_ability.assert_not_called()
        assert score == 100

    def test_has_weapons_fallback_when_not_in_cache(self, ship, target_with_weapons):
        """has_weapons rule should fall back to component lookup when target not in cache."""
        rules = [{'type': 'has_weapons', 'weight': 100}]

        # Empty cache (target not in it)
        cache = {}

        score = TargetEvaluator.evaluate(
            ship, target_with_weapons, rules,
            ship_capabilities_cache=cache
        )

        # Should have called get_components_by_ability (cache miss)
        target_with_weapons.get_components_by_ability.assert_called()
        assert score == 100

    def test_has_weapons_cached_false_returns_zero(self, ship, target_without_weapons):
        """has_weapons rule should return 0 for cached unarmed target."""
        rules = [{'type': 'has_weapons', 'weight': 100}]

        # Cache indicates no weapons
        cache = {
            target_without_weapons.id: {
                'has_weapons': False,
                'weapon_components': [],
                'has_pdc': False,
                'pdc_components': [],
            }
        }

        score = TargetEvaluator.evaluate(
            ship, target_without_weapons, rules,
            ship_capabilities_cache=cache
        )

        # Should NOT have called get_components_by_ability (used cache)
        target_without_weapons.get_components_by_ability.assert_not_called()
        assert score == 0

    def test_has_weapons_required_cached_false_returns_neg_inf(self, ship, target_without_weapons):
        """Required has_weapons rule should return -inf for cached unarmed target."""
        rules = [{'type': 'has_weapons', 'weight': 100, 'required': True}]

        # Cache indicates no weapons
        cache = {
            target_without_weapons.id: {
                'has_weapons': False,
                'weapon_components': [],
                'has_pdc': False,
                'pdc_components': [],
            }
        }

        score = TargetEvaluator.evaluate(
            ship, target_without_weapons, rules,
            ship_capabilities_cache=cache
        )

        assert score == -float('inf')


class TestCachePerformanceBenefit:
    """Tests demonstrating performance benefit of caching."""

    def test_multiple_evaluations_with_cache_avoid_redundant_lookups(self, ship):
        """Multiple targets should share cached lookups."""
        # Create multiple targets
        targets = []
        for i in range(5):
            t = MagicMock()
            t.id = f'target_{i}'
            t.position = pygame.math.Vector2(100 * (i + 1), 0)
            t.mass = 1000
            t.type = 'ship'
            weapon = MagicMock()
            weapon.has_ability = MagicMock(return_value=False)
            t.get_components_by_ability = MagicMock(return_value=[weapon])
            targets.append(t)

        rules = [{'type': 'has_weapons', 'weight': 100}]

        # Build capabilities cache once
        cache = {}
        for t in targets:
            weapons = t.get_components_by_ability('WeaponAbility', operational_only=False)
            cache[t.id] = {
                'has_weapons': len(weapons) > 0,
                'weapon_components': weapons,
                'has_pdc': False,
                'pdc_components': [],
            }

        # Reset mock call counts
        for t in targets:
            t.get_components_by_ability.reset_mock()

        # Evaluate all targets using cache
        scores = []
        for t in targets:
            score = TargetEvaluator.evaluate(
                ship, t, rules,
                ship_capabilities_cache=cache
            )
            scores.append(score)

        # Should NOT have called get_components_by_ability on any target
        for t in targets:
            t.get_components_by_ability.assert_not_called()

        # All should have positive scores (all armed)
        assert all(s == 100 for s in scores)
