"""
Comprehensive tests for game/ai/target_evaluator.py

This test file covers:
- Evaluation rules (all rule types)
- Priority calculations
- Threat assessment
- Target selection edge cases
- Required flag behavior
- Custom stat helpers
"""
import pytest
import pygame
from unittest.mock import MagicMock
from game.ai.target_evaluator import TargetEvaluator
from game.core.constants import AttackType


# =============================================================================
# Fixtures
# =============================================================================

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
def target():
    """Create a mock target for testing."""
    t = MagicMock()
    t.position = pygame.math.Vector2(100, 0)
    t.mass = 1000
    t.velocity = pygame.math.Vector2(10, 0)
    t.type = 'ship'
    return t


@pytest.fixture
def target_with_hp():
    """Create a target with HP components."""
    t = MagicMock()
    t.position = pygame.math.Vector2(100, 0)
    t.mass = 1000
    t.velocity = pygame.math.Vector2(0, 0)
    t.type = 'ship'

    comp = MagicMock()
    comp.max_hp = 100
    comp.current_hp = 50
    t.get_all_components = MagicMock(return_value=[comp])

    return t


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
        from game.simulation.components.component_constants import LayerType

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
