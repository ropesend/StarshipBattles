"""
Tests for individual target evaluation rule types.

This test file covers:
- Distance rules (nearest, farthest, distance)
- Mass/Size rules (mass, largest, smallest)
- Speed rules (fastest, slowest)
- HP rules (most_damaged, least_damaged)
- Strength rules (strongest, weakest)
- Has weapons rule
- PDC arc rule
- Least armor rule
"""
import pytest
import pygame
from unittest.mock import MagicMock
from game.ai.target_evaluator import TargetEvaluator
from game.core.constants import AttackType, LayerType


# =============================================================================
# Test: Nearest Rule
# =============================================================================

class TestNearestRule:
    """Tests for the 'nearest' rule type."""

    def test_nearest_closer_gets_higher_score(self, ship, target):
        """Closer targets should get higher scores."""
        near_target = MagicMock()
        near_target.position = pygame.math.Vector2(50, 0)

        far_target = MagicMock()
        far_target.position = pygame.math.Vector2(200, 0)

        rules = [{'type': 'nearest', 'weight': 1}]

        score_near = TargetEvaluator.evaluate(ship, near_target, rules)
        score_far = TargetEvaluator.evaluate(ship, far_target, rules)

        assert score_near > score_far

    def test_nearest_with_factor(self, ship, target):
        """Nearest rule should work with factor instead of weight."""
        rules = [{'type': 'nearest', 'factor': -0.5}]

        score = TargetEvaluator.evaluate(ship, target, rules)

        # dist=100, factor=-0.5 => val = 100 * (-0.5) = -50
        assert score == 100 * -0.5

    def test_nearest_zero_distance(self, ship, target):
        """Zero distance should give score of 0."""
        target.position = pygame.math.Vector2(0, 0)
        rules = [{'type': 'nearest', 'weight': 1}]

        score = TargetEvaluator.evaluate(ship, target, rules)

        assert score == 0


# =============================================================================
# Test: Farthest Rule
# =============================================================================

class TestFarthestRule:
    """Tests for the 'farthest' rule type."""

    def test_farthest_farther_gets_higher_score(self, ship):
        """Farther targets should get higher scores."""
        near_target = MagicMock()
        near_target.position = pygame.math.Vector2(50, 0)

        far_target = MagicMock()
        far_target.position = pygame.math.Vector2(200, 0)

        rules = [{'type': 'farthest', 'weight': 1}]

        score_near = TargetEvaluator.evaluate(ship, near_target, rules)
        score_far = TargetEvaluator.evaluate(ship, far_target, rules)

        assert score_far > score_near

    def test_farthest_with_factor(self, ship, target):
        """Farthest rule should work with factor."""
        rules = [{'type': 'farthest', 'factor': 0.5}]

        score = TargetEvaluator.evaluate(ship, target, rules)

        # dist=100, factor=0.5 => val = 100 * 0.5 = 50
        assert score == 100 * 0.5


# =============================================================================
# Test: Distance Rule
# =============================================================================

class TestDistanceRule:
    """Tests for the 'distance' rule type."""

    def test_distance_rule_applies_factor(self, ship, target):
        """Distance rule should multiply by factor."""
        rules = [{'type': 'distance', 'factor': 2.0}]

        score = TargetEvaluator.evaluate(ship, target, rules)

        # dist=100, factor=2 => 200
        assert score == 200


# =============================================================================
# Test: Mass/Size Rules
# =============================================================================

class TestMassRules:
    """Tests for mass-related rules (mass, largest, smallest)."""

    def test_mass_rule_larger_gets_higher_score(self, ship):
        """Larger mass should get higher score with mass rule."""
        small = MagicMock()
        small.position = pygame.math.Vector2(100, 0)
        small.mass = 500

        large = MagicMock()
        large.position = pygame.math.Vector2(100, 0)
        large.mass = 5000

        rules = [{'type': 'mass', 'weight': 1}]

        score_small = TargetEvaluator.evaluate(ship, small, rules)
        score_large = TargetEvaluator.evaluate(ship, large, rules)

        assert score_large > score_small

    def test_largest_same_as_mass(self, ship, target):
        """'largest' should behave same as 'mass'."""
        rules_mass = [{'type': 'mass', 'weight': 1}]
        rules_largest = [{'type': 'largest', 'weight': 1}]

        score_mass = TargetEvaluator.evaluate(ship, target, rules_mass)
        score_largest = TargetEvaluator.evaluate(ship, target, rules_largest)

        assert score_mass == score_largest

    def test_smallest_smaller_gets_higher_score(self, ship):
        """Smaller mass should get higher score with smallest rule."""
        small = MagicMock()
        small.position = pygame.math.Vector2(100, 0)
        small.mass = 500

        large = MagicMock()
        large.position = pygame.math.Vector2(100, 0)
        large.mass = 5000

        rules = [{'type': 'smallest', 'weight': 1}]

        score_small = TargetEvaluator.evaluate(ship, small, rules)
        score_large = TargetEvaluator.evaluate(ship, large, rules)

        assert score_small > score_large

    def test_missing_mass_uses_default(self, ship, target):
        """Missing mass attribute should use default of 100."""
        del target.mass
        rules = [{'type': 'mass', 'weight': 1}]

        score = TargetEvaluator.evaluate(ship, target, rules)

        assert score == 100


# =============================================================================
# Test: Speed Rules
# =============================================================================

class TestSpeedRules:
    """Tests for speed-related rules (fastest, slowest)."""

    def test_fastest_higher_speed_gets_higher_score(self, ship):
        """Faster targets should get higher score with fastest rule."""
        slow = MagicMock()
        slow.position = pygame.math.Vector2(100, 0)
        slow.velocity = pygame.math.Vector2(5, 0)

        fast = MagicMock()
        fast.position = pygame.math.Vector2(100, 0)
        fast.velocity = pygame.math.Vector2(50, 0)

        rules = [{'type': 'fastest', 'weight': 1}]

        score_slow = TargetEvaluator.evaluate(ship, slow, rules)
        score_fast = TargetEvaluator.evaluate(ship, fast, rules)

        assert score_fast > score_slow

    def test_slowest_lower_speed_gets_higher_score(self, ship):
        """Slower targets should get higher score with slowest rule."""
        slow = MagicMock()
        slow.position = pygame.math.Vector2(100, 0)
        slow.velocity = pygame.math.Vector2(5, 0)

        fast = MagicMock()
        fast.position = pygame.math.Vector2(100, 0)
        fast.velocity = pygame.math.Vector2(50, 0)

        rules = [{'type': 'slowest', 'weight': 1}]

        score_slow = TargetEvaluator.evaluate(ship, slow, rules)
        score_fast = TargetEvaluator.evaluate(ship, fast, rules)

        assert score_slow > score_fast

    def test_missing_velocity_uses_zero(self, ship, target):
        """Missing velocity should use zero vector."""
        del target.velocity
        rules = [{'type': 'fastest', 'weight': 1}]

        score = TargetEvaluator.evaluate(ship, target, rules)

        # Speed 0 * weight 1 = 0
        assert score == 0


# =============================================================================
# Test: HP Rules
# =============================================================================

class TestHPRules:
    """Tests for HP-related rules (most_damaged, least_damaged)."""

    def test_most_damaged_lower_hp_gets_higher_score(self, ship):
        """Lower HP% should get higher score with most_damaged rule."""
        damaged = MagicMock()
        damaged.position = pygame.math.Vector2(100, 0)
        comp_damaged = MagicMock()
        comp_damaged.max_hp = 100
        comp_damaged.current_hp = 10
        damaged.get_all_components = MagicMock(return_value=[comp_damaged])

        healthy = MagicMock()
        healthy.position = pygame.math.Vector2(100, 0)
        comp_healthy = MagicMock()
        comp_healthy.max_hp = 100
        comp_healthy.current_hp = 90
        healthy.get_all_components = MagicMock(return_value=[comp_healthy])

        rules = [{'type': 'most_damaged', 'weight': 1}]

        score_damaged = TargetEvaluator.evaluate(ship, damaged, rules)
        score_healthy = TargetEvaluator.evaluate(ship, healthy, rules)

        assert score_damaged > score_healthy

    def test_least_damaged_higher_hp_gets_higher_score(self, ship):
        """Higher HP% should get higher score with least_damaged rule."""
        damaged = MagicMock()
        damaged.position = pygame.math.Vector2(100, 0)
        comp_damaged = MagicMock()
        comp_damaged.max_hp = 100
        comp_damaged.current_hp = 10
        damaged.get_all_components = MagicMock(return_value=[comp_damaged])

        healthy = MagicMock()
        healthy.position = pygame.math.Vector2(100, 0)
        comp_healthy = MagicMock()
        comp_healthy.max_hp = 100
        comp_healthy.current_hp = 90
        healthy.get_all_components = MagicMock(return_value=[comp_healthy])

        rules = [{'type': 'least_damaged', 'weight': 1}]

        score_damaged = TargetEvaluator.evaluate(ship, damaged, rules)
        score_healthy = TargetEvaluator.evaluate(ship, healthy, rules)

        assert score_healthy > score_damaged


# =============================================================================
# Test: Strongest/Weakest Rules
# =============================================================================

class TestStrengthRules:
    """Tests for strength rules (strongest, weakest)."""

    def test_strongest_uses_mass(self, ship):
        """Strongest should favor higher mass."""
        weak = MagicMock()
        weak.position = pygame.math.Vector2(100, 0)
        weak.mass = 500

        strong = MagicMock()
        strong.position = pygame.math.Vector2(100, 0)
        strong.mass = 5000

        rules = [{'type': 'strongest', 'weight': 1}]

        score_weak = TargetEvaluator.evaluate(ship, weak, rules)
        score_strong = TargetEvaluator.evaluate(ship, strong, rules)

        assert score_strong > score_weak

    def test_weakest_uses_inverse_mass(self, ship):
        """Weakest should favor lower mass."""
        weak = MagicMock()
        weak.position = pygame.math.Vector2(100, 0)
        weak.mass = 500

        strong = MagicMock()
        strong.position = pygame.math.Vector2(100, 0)
        strong.mass = 5000

        rules = [{'type': 'weakest', 'weight': 1}]

        score_weak = TargetEvaluator.evaluate(ship, weak, rules)
        score_strong = TargetEvaluator.evaluate(ship, strong, rules)

        assert score_weak > score_strong


# =============================================================================
# Test: Has Weapons Rule
# =============================================================================

class TestHasWeaponsRule:
    """Tests for 'has_weapons' rule."""

    def test_has_weapons_target_with_weapons_scores_higher(self, ship):
        """Target with weapons should score higher."""
        armed = MagicMock()
        armed.position = pygame.math.Vector2(100, 0)
        armed.get_components_by_ability = MagicMock(return_value=[MagicMock()])

        unarmed = MagicMock()
        unarmed.position = pygame.math.Vector2(100, 0)
        unarmed.get_components_by_ability = MagicMock(return_value=[])

        rules = [{'type': 'has_weapons', 'weight': 100}]

        score_armed = TargetEvaluator.evaluate(ship, armed, rules)
        score_unarmed = TargetEvaluator.evaluate(ship, unarmed, rules)

        assert score_armed > score_unarmed

    def test_has_weapons_required_fails_without_weapons(self, ship):
        """Required has_weapons should return -inf for unarmed targets."""
        unarmed = MagicMock()
        unarmed.position = pygame.math.Vector2(100, 0)
        unarmed.get_components_by_ability = MagicMock(return_value=[])

        rules = [{'type': 'has_weapons', 'weight': 100, 'required': True}]

        score = TargetEvaluator.evaluate(ship, unarmed, rules)

        assert score == -float('inf')


# =============================================================================
# Test: PDC Arc Rule
# =============================================================================

class TestPDCArcRule:
    """Tests for 'pdc_arc' and 'missiles_in_pdc_arc' rules."""

    def test_pdc_arc_non_missile_is_neutral(self, ship, target):
        """Non-missile targets should get neutral (0) score."""
        target.type = 'ship'
        rules = [{'type': 'pdc_arc', 'weight': 100}]

        score = TargetEvaluator.evaluate(ship, target, rules)

        assert score == 0

    def test_pdc_arc_missile_in_arc_scores_high(self, ship):
        """Missile in PDC arc should get high score."""
        missile = MagicMock()
        missile.position = pygame.math.Vector2(100, 0)
        missile.type = AttackType.MISSILE

        # Setup PDC weapon on ship
        comp = MagicMock()
        comp.has_pdc_ability = MagicMock(return_value=True)
        weapon_ab = MagicMock()
        weapon_ab.range = 200
        weapon_ab.facing_angle = 0
        weapon_ab.firing_arc = 90
        comp.get_ability = MagicMock(return_value=weapon_ab)

        ship.get_components_by_ability = MagicMock(return_value=[comp])

        rules = [{'type': 'pdc_arc', 'weight': 100}]

        score = TargetEvaluator.evaluate(ship, missile, rules)

        assert score == 100

    def test_pdc_arc_required_missile_out_of_arc(self, ship):
        """Required pdc_arc should return -inf for missile out of arc."""
        missile = MagicMock()
        missile.position = pygame.math.Vector2(-100, 0)  # Behind ship
        missile.type = AttackType.MISSILE

        # Setup PDC weapon facing forward
        comp = MagicMock()
        comp.has_pdc_ability = MagicMock(return_value=True)
        weapon_ab = MagicMock()
        weapon_ab.range = 200
        weapon_ab.facing_angle = 0
        weapon_ab.firing_arc = 90  # Only covers front 90 degrees
        comp.get_ability = MagicMock(return_value=weapon_ab)

        ship.get_components_by_ability = MagicMock(return_value=[comp])

        rules = [{'type': 'pdc_arc', 'weight': 100, 'required': True}]

        score = TargetEvaluator.evaluate(ship, missile, rules)

        assert score == -float('inf')


# =============================================================================
# Test: Least Armor Rule
# =============================================================================

class TestLeastArmorRule:
    """Tests for 'least_armor' rule."""

    def test_least_armor_lower_hp_scores_higher(self, ship):
        """Target with less armor HP should score higher."""
        low_armor = MagicMock()
        low_armor.position = pygame.math.Vector2(100, 0)
        armor_comp1 = MagicMock()
        armor_comp1.hp = 100
        low_armor.get_components_by_layer = MagicMock(return_value=[armor_comp1])

        high_armor = MagicMock()
        high_armor.position = pygame.math.Vector2(100, 0)
        armor_comp2 = MagicMock()
        armor_comp2.hp = 1000
        high_armor.get_components_by_layer = MagicMock(return_value=[armor_comp2])

        rules = [{'type': 'least_armor', 'weight': 1}]

        score_low = TargetEvaluator.evaluate(ship, low_armor, rules)
        score_high = TargetEvaluator.evaluate(ship, high_armor, rules)

        assert score_low > score_high


# =============================================================================
# TCG-FND-018: Speed Rule with Factor-Based Scoring
# =============================================================================

class TestSpeedRulesFactorBased:
    """TCG-FND-018: Tests for _eval_speed_rule with factor-based scoring.

    The finding notes potential logic issues when using factor instead of weight
    for 'slowest' rules. These tests verify the correct behavior.

    Current implementation:
        fastest: val = speed * (weight if weight > 0 else factor)
        slowest: val = -speed * (weight if weight > 0 else -factor)

    When weight=0 and factor is used for 'slowest':
        val = -speed * -factor = speed * factor

    This means faster targets get HIGHER scores for 'slowest' with factor,
    which is INCORRECT behavior. These tests document this.
    """

    def test_slowest_with_weight_slower_is_higher(self, ship):
        """slowest rule with weight correctly prefers slower targets."""
        slow = MagicMock()
        slow.position = pygame.math.Vector2(100, 0)
        slow.velocity = pygame.math.Vector2(5, 0)  # speed = 5

        fast = MagicMock()
        fast.position = pygame.math.Vector2(100, 0)
        fast.velocity = pygame.math.Vector2(50, 0)  # speed = 50

        rules = [{'type': 'slowest', 'weight': 1}]

        score_slow = TargetEvaluator.evaluate(ship, slow, rules)
        score_fast = TargetEvaluator.evaluate(ship, fast, rules)

        # With weight: slow gets -5, fast gets -50
        # Less negative (slower) should be higher
        assert score_slow > score_fast
        assert score_slow == -5
        assert score_fast == -50

    def test_slowest_with_factor_documents_behavior(self, ship):
        """Document slowest rule behavior when using factor (weight=0).

        With the current implementation:
        - slowest with factor uses: val = -speed * -factor = speed * factor
        - This makes FASTER targets score HIGHER, which contradicts 'slowest' intent

        This test documents the actual behavior as-is. If this is a bug, fixing
        it would require changing _eval_speed_rule to use -factor for slowest.
        """
        slow = MagicMock()
        slow.position = pygame.math.Vector2(100, 0)
        slow.velocity = pygame.math.Vector2(5, 0)  # speed = 5

        fast = MagicMock()
        fast.position = pygame.math.Vector2(100, 0)
        fast.velocity = pygame.math.Vector2(50, 0)  # speed = 50

        rules = [{'type': 'slowest', 'weight': 0, 'factor': 1}]

        score_slow = TargetEvaluator.evaluate(ship, slow, rules)
        score_fast = TargetEvaluator.evaluate(ship, fast, rules)

        # With current implementation: val = -speed * -factor
        # slow: -5 * -1 = 5
        # fast: -50 * -1 = 50
        # BUG: Fast target gets HIGHER score despite 'slowest' rule
        assert score_slow == 5, "Expected: -speed * -factor = speed * factor"
        assert score_fast == 50, "Expected: -speed * -factor = speed * factor"

        # Document: This is likely a BUG - faster should not score higher for 'slowest'
        # The correct behavior would be: slower target scores higher
        # If this assertion fails after a fix, the bug has been corrected
        assert score_fast > score_slow, "Current behavior: fast > slow (likely a bug)"

    def test_fastest_with_weight_faster_is_higher(self, ship):
        """fastest rule with weight correctly prefers faster targets."""
        slow = MagicMock()
        slow.position = pygame.math.Vector2(100, 0)
        slow.velocity = pygame.math.Vector2(5, 0)

        fast = MagicMock()
        fast.position = pygame.math.Vector2(100, 0)
        fast.velocity = pygame.math.Vector2(50, 0)

        rules = [{'type': 'fastest', 'weight': 1}]

        score_slow = TargetEvaluator.evaluate(ship, slow, rules)
        score_fast = TargetEvaluator.evaluate(ship, fast, rules)

        # With weight: slow gets 5, fast gets 50
        assert score_fast > score_slow
        assert score_slow == 5
        assert score_fast == 50

    def test_fastest_with_factor_faster_is_higher(self, ship):
        """fastest rule with factor also correctly prefers faster targets."""
        slow = MagicMock()
        slow.position = pygame.math.Vector2(100, 0)
        slow.velocity = pygame.math.Vector2(5, 0)

        fast = MagicMock()
        fast.position = pygame.math.Vector2(100, 0)
        fast.velocity = pygame.math.Vector2(50, 0)

        rules = [{'type': 'fastest', 'weight': 0, 'factor': 1}]

        score_slow = TargetEvaluator.evaluate(ship, slow, rules)
        score_fast = TargetEvaluator.evaluate(ship, fast, rules)

        # With factor: slow gets 5, fast gets 50
        assert score_fast > score_slow

    def test_slowest_with_negative_factor(self, ship):
        """slowest with negative factor should work correctly."""
        slow = MagicMock()
        slow.position = pygame.math.Vector2(100, 0)
        slow.velocity = pygame.math.Vector2(5, 0)

        fast = MagicMock()
        fast.position = pygame.math.Vector2(100, 0)
        fast.velocity = pygame.math.Vector2(50, 0)

        # Using negative factor to compensate for the double negation
        rules = [{'type': 'slowest', 'weight': 0, 'factor': -1}]

        score_slow = TargetEvaluator.evaluate(ship, slow, rules)
        score_fast = TargetEvaluator.evaluate(ship, fast, rules)

        # With factor=-1: val = -speed * -(-1) = -speed
        # slow: -5, fast: -50
        # Now slower target correctly scores higher
        assert score_slow > score_fast, "With negative factor, slower should score higher"

    def test_stationary_target_zero_speed(self, ship):
        """Stationary target (speed=0) should get score of 0."""
        stationary = MagicMock()
        stationary.position = pygame.math.Vector2(100, 0)
        stationary.velocity = pygame.math.Vector2(0, 0)

        rules_fastest = [{'type': 'fastest', 'weight': 1}]
        rules_slowest = [{'type': 'slowest', 'weight': 1}]

        score_fastest = TargetEvaluator.evaluate(ship, stationary, rules_fastest)
        score_slowest = TargetEvaluator.evaluate(ship, stationary, rules_slowest)

        assert score_fastest == 0
        assert score_slowest == 0
