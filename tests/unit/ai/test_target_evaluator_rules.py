"""
Comprehensive tests for TargetEvaluator rule types.

TCG-FND-002: Tests for all 14 rule types with various weight/factor combinations
including edge values (0, negative, very large).

Rule types covered:
- Distance: nearest, farthest, distance
- Mass: mass, largest, smallest, strongest, weakest
- Speed: fastest, slowest
- Damage: most_damaged, least_damaged
- Capability: has_weapons, least_armor, pdc_arc, missiles_in_pdc_arc
"""
import pytest
from unittest.mock import MagicMock

from game.ai.target_evaluator import TargetEvaluator
from game.core.math import Vector2
from game.core.constants import AttackType


@pytest.fixture
def mock_ship():
    """Create a mock ship for targeting tests."""
    ship = MagicMock()
    ship.id = 'ship_1'
    ship.get_position = MagicMock(return_value=Vector2(0, 0))
    ship.position = Vector2(0, 0)
    ship.mass = 100
    ship.velocity = Vector2(0, 0)
    return ship


@pytest.fixture
def mock_target():
    """Create a mock target for evaluation."""
    target = MagicMock()
    target.id = 'target_1'
    target.get_position = MagicMock(return_value=Vector2(100, 0))
    target.position = Vector2(100, 0)
    target.mass = 50
    target.velocity = Vector2(10, 0)  # Moving
    target.type = 'ship'
    target.hp = 75
    target.max_hp = 100
    target.get_components_by_ability = MagicMock(return_value=[])
    target.get_components_by_layer = MagicMock(return_value=[])
    return target


@pytest.fixture
def mock_stat_helpers():
    """Create mock stat helper functions."""
    return {
        'get_hp_percent': lambda x: getattr(x, 'hp', 100) / getattr(x, 'max_hp', 100),
        'is_in_pdc_arc': lambda ship, target: True
    }


# =============================================================================
# DISTANCE RULES: nearest, farthest, distance
# =============================================================================

class TestDistanceRules:
    """Tests for distance-based rules."""

    @pytest.mark.parametrize("weight,factor,expected_approx", [
        (1, 1, -100.0),    # Weight > 0: -dist * weight = -100
        (2, 1, -200.0),    # Higher weight
        (0, 1, 100.0),     # Weight = 0: dist * factor = 100
        (0, 2, 200.0),     # Weight = 0: dist * factor = 200
        (0, -1, -100.0),   # Weight = 0: negative factor
        (0, 0, 0.0),       # Both zero
    ])
    def test_nearest_rule_weight_factor_combinations(
        self, mock_ship, mock_target, mock_stat_helpers, weight, factor, expected_approx
    ):
        """Nearest rule with various weight/factor combinations."""
        rules = [{'type': 'nearest', 'weight': weight, 'factor': factor}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(expected_approx)

    @pytest.mark.parametrize("weight,factor,expected_approx", [
        (1, 1, 100.0),     # Weight > 0: dist * weight = 100
        (2, 1, 200.0),     # Higher weight
        (0, 1, 100.0),     # Weight = 0: dist * factor = 100
        (0, 2, 200.0),     # Weight = 0: dist * factor = 200
        (0, -1, -100.0),   # Weight = 0: negative factor
    ])
    def test_farthest_rule_weight_factor_combinations(
        self, mock_ship, mock_target, mock_stat_helpers, weight, factor, expected_approx
    ):
        """Farthest rule with various weight/factor combinations."""
        rules = [{'type': 'farthest', 'weight': weight, 'factor': factor}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(expected_approx)

    @pytest.mark.parametrize("weight,factor,expected_approx", [
        (0, 1, 100.0),     # distance type always uses factor
        (0, 0.5, 50.0),
        (0, -1, -100.0),
        (5, 1, 100.0),     # Weight ignored for 'distance' type
    ])
    def test_distance_rule_factor_only(
        self, mock_ship, mock_target, mock_stat_helpers, weight, factor, expected_approx
    ):
        """Distance rule uses factor regardless of weight."""
        rules = [{'type': 'distance', 'weight': weight, 'factor': factor}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(expected_approx)

    def test_distance_cache_improves_performance(self, mock_ship, mock_target, mock_stat_helpers):
        """Distance cache is used when provided."""
        rules = [{'type': 'nearest', 'weight': 1}]

        # Cached distance different from actual
        cache = {mock_target: 50.0}

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers,
            distance_cache=cache
        )

        # Should use cached value 50, not actual 100
        assert score == pytest.approx(-50.0)


# =============================================================================
# MASS RULES: mass, largest, smallest, strongest, weakest
# =============================================================================

class TestMassRules:
    """Tests for mass/size-based rules."""

    @pytest.mark.parametrize("weight,factor,expected_approx", [
        (1, 1, 50.0),      # Weight > 0: mass * weight = 50
        (2, 1, 100.0),     # Higher weight
        (0, 1, 50.0),      # Weight = 0: mass * factor = 50
        (0, 2, 100.0),     # Weight = 0: mass * factor = 100
        (0, 0, 0.0),       # Both zero
    ])
    def test_mass_rule_weight_factor_combinations(
        self, mock_ship, mock_target, mock_stat_helpers, weight, factor, expected_approx
    ):
        """Mass rule with various weight/factor combinations."""
        rules = [{'type': 'mass', 'weight': weight, 'factor': factor}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(expected_approx)

    @pytest.mark.parametrize("rule_type", ['mass', 'largest', 'strongest'])
    def test_large_mass_rules_prefer_bigger(
        self, mock_ship, mock_stat_helpers, rule_type
    ):
        """mass/largest/strongest rules prefer higher mass targets."""
        small_target = MagicMock()
        small_target.id = 'small'
        small_target.position = Vector2(100, 0)
        small_target.mass = 50
        small_target.get_components_by_ability = MagicMock(return_value=[])
        small_target.get_components_by_layer = MagicMock(return_value=[])

        big_target = MagicMock()
        big_target.id = 'big'
        big_target.position = Vector2(100, 0)
        big_target.mass = 200
        big_target.get_components_by_ability = MagicMock(return_value=[])
        big_target.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': rule_type, 'weight': 1}]

        small_score = TargetEvaluator.evaluate(
            mock_ship, small_target, rules, stat_helpers=mock_stat_helpers
        )
        big_score = TargetEvaluator.evaluate(
            mock_ship, big_target, rules, stat_helpers=mock_stat_helpers
        )

        assert big_score > small_score

    @pytest.mark.parametrize("rule_type", ['smallest', 'weakest'])
    def test_small_mass_rules_prefer_smaller(
        self, mock_ship, mock_stat_helpers, rule_type
    ):
        """smallest/weakest rules prefer lower mass targets."""
        small_target = MagicMock()
        small_target.id = 'small'
        small_target.position = Vector2(100, 0)
        small_target.mass = 50
        small_target.get_components_by_ability = MagicMock(return_value=[])
        small_target.get_components_by_layer = MagicMock(return_value=[])

        big_target = MagicMock()
        big_target.id = 'big'
        big_target.position = Vector2(100, 0)
        big_target.mass = 200
        big_target.get_components_by_ability = MagicMock(return_value=[])
        big_target.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': rule_type, 'weight': 1}]

        small_score = TargetEvaluator.evaluate(
            mock_ship, small_target, rules, stat_helpers=mock_stat_helpers
        )
        big_score = TargetEvaluator.evaluate(
            mock_ship, big_target, rules, stat_helpers=mock_stat_helpers
        )

        assert small_score > big_score

    @pytest.mark.parametrize("weight,factor,expected_approx", [
        (1, 1, -50.0),     # Weight > 0: -mass * weight = -50
        (2, 1, -100.0),    # Higher weight
        (0, 1, 50.0),      # Weight = 0: mass * factor (factor should be negative for intended use)
        (0, -1, -50.0),    # Weight = 0: negative factor
    ])
    def test_smallest_rule_weight_factor_combinations(
        self, mock_ship, mock_target, mock_stat_helpers, weight, factor, expected_approx
    ):
        """Smallest rule with various weight/factor combinations."""
        rules = [{'type': 'smallest', 'weight': weight, 'factor': factor}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(expected_approx)


# =============================================================================
# SPEED RULES: fastest, slowest
# =============================================================================

class TestSpeedRules:
    """Tests for speed-based rules."""

    def test_fastest_rule_prefers_higher_velocity(self, mock_ship, mock_stat_helpers):
        """Fastest rule prefers targets with higher velocity magnitude."""
        slow_target = MagicMock()
        slow_target.id = 'slow'
        slow_target.position = Vector2(100, 0)
        slow_target.velocity = Vector2(10, 0)  # Speed 10
        slow_target.get_components_by_ability = MagicMock(return_value=[])
        slow_target.get_components_by_layer = MagicMock(return_value=[])

        fast_target = MagicMock()
        fast_target.id = 'fast'
        fast_target.position = Vector2(100, 0)
        fast_target.velocity = Vector2(50, 0)  # Speed 50
        fast_target.get_components_by_ability = MagicMock(return_value=[])
        fast_target.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': 'fastest', 'weight': 1}]

        slow_score = TargetEvaluator.evaluate(
            mock_ship, slow_target, rules, stat_helpers=mock_stat_helpers
        )
        fast_score = TargetEvaluator.evaluate(
            mock_ship, fast_target, rules, stat_helpers=mock_stat_helpers
        )

        assert fast_score > slow_score

    def test_slowest_rule_prefers_lower_velocity(self, mock_ship, mock_stat_helpers):
        """Slowest rule prefers targets with lower velocity magnitude."""
        slow_target = MagicMock()
        slow_target.id = 'slow'
        slow_target.position = Vector2(100, 0)
        slow_target.velocity = Vector2(10, 0)  # Speed 10
        slow_target.get_components_by_ability = MagicMock(return_value=[])
        slow_target.get_components_by_layer = MagicMock(return_value=[])

        fast_target = MagicMock()
        fast_target.id = 'fast'
        fast_target.position = Vector2(100, 0)
        fast_target.velocity = Vector2(50, 0)  # Speed 50
        fast_target.get_components_by_ability = MagicMock(return_value=[])
        fast_target.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': 'slowest', 'weight': 1}]

        slow_score = TargetEvaluator.evaluate(
            mock_ship, slow_target, rules, stat_helpers=mock_stat_helpers
        )
        fast_score = TargetEvaluator.evaluate(
            mock_ship, fast_target, rules, stat_helpers=mock_stat_helpers
        )

        assert slow_score > fast_score

    @pytest.mark.parametrize("weight,factor,expected_approx", [
        (1, 1, 10.0),      # Weight > 0: speed * weight = 10
        (0, 1, 10.0),      # Weight = 0: speed * factor = 10
        (0, 2, 20.0),      # Weight = 0: speed * factor = 20
    ])
    def test_fastest_rule_weight_factor(
        self, mock_ship, mock_target, mock_stat_helpers, weight, factor, expected_approx
    ):
        """Fastest rule with weight/factor combinations."""
        rules = [{'type': 'fastest', 'weight': weight, 'factor': factor}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(expected_approx)

    @pytest.mark.parametrize("weight,factor,expected_approx", [
        (1, 1, -10.0),     # Weight > 0: -speed * weight = -10
        (0, 1, 10.0),      # Weight = 0: -speed * (-factor) = 10
    ])
    def test_slowest_rule_weight_factor(
        self, mock_ship, mock_target, mock_stat_helpers, weight, factor, expected_approx
    ):
        """Slowest rule with weight/factor combinations."""
        rules = [{'type': 'slowest', 'weight': weight, 'factor': factor}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(expected_approx)

    def test_speed_rule_stationary_target(self, mock_ship, mock_stat_helpers):
        """Speed rules handle stationary targets (velocity = 0)."""
        stationary = MagicMock()
        stationary.id = 'stationary'
        stationary.position = Vector2(100, 0)
        stationary.velocity = Vector2(0, 0)  # Speed 0
        stationary.get_components_by_ability = MagicMock(return_value=[])
        stationary.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': 'fastest', 'weight': 1}]

        score = TargetEvaluator.evaluate(
            mock_ship, stationary, rules, stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(0.0)


# =============================================================================
# DAMAGE RULES: most_damaged, least_damaged
# =============================================================================

class TestDamageRules:
    """Tests for damage-based rules."""

    def test_most_damaged_prefers_lower_hp(self, mock_ship, mock_stat_helpers):
        """most_damaged rule prefers targets with lower HP percentage."""
        healthy = MagicMock()
        healthy.id = 'healthy'
        healthy.position = Vector2(100, 0)
        healthy.hp = 90
        healthy.max_hp = 100
        healthy.get_components_by_ability = MagicMock(return_value=[])
        healthy.get_components_by_layer = MagicMock(return_value=[])

        damaged = MagicMock()
        damaged.id = 'damaged'
        damaged.position = Vector2(100, 0)
        damaged.hp = 30
        damaged.max_hp = 100
        damaged.get_components_by_ability = MagicMock(return_value=[])
        damaged.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': 'most_damaged', 'weight': 1}]

        healthy_score = TargetEvaluator.evaluate(
            mock_ship, healthy, rules, stat_helpers=mock_stat_helpers
        )
        damaged_score = TargetEvaluator.evaluate(
            mock_ship, damaged, rules, stat_helpers=mock_stat_helpers
        )

        assert damaged_score > healthy_score

    def test_least_damaged_prefers_higher_hp(self, mock_ship, mock_stat_helpers):
        """least_damaged rule prefers targets with higher HP percentage."""
        healthy = MagicMock()
        healthy.id = 'healthy'
        healthy.position = Vector2(100, 0)
        healthy.hp = 90
        healthy.max_hp = 100
        healthy.get_components_by_ability = MagicMock(return_value=[])
        healthy.get_components_by_layer = MagicMock(return_value=[])

        damaged = MagicMock()
        damaged.id = 'damaged'
        damaged.position = Vector2(100, 0)
        damaged.hp = 30
        damaged.max_hp = 100
        damaged.get_components_by_ability = MagicMock(return_value=[])
        damaged.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': 'least_damaged', 'weight': 1}]

        healthy_score = TargetEvaluator.evaluate(
            mock_ship, healthy, rules, stat_helpers=mock_stat_helpers
        )
        damaged_score = TargetEvaluator.evaluate(
            mock_ship, damaged, rules, stat_helpers=mock_stat_helpers
        )

        assert healthy_score > damaged_score

    @pytest.mark.parametrize("weight,factor", [
        (0, 0),
        (0, 1),
        (1, 0),
    ])
    def test_damage_rules_with_zero_values(
        self, mock_ship, mock_target, mock_stat_helpers, weight, factor
    ):
        """Damage rules handle zero weight/factor without error."""
        rules = [{'type': 'most_damaged', 'weight': weight, 'factor': factor}]

        # Should not raise
        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert isinstance(score, float)


# =============================================================================
# CAPABILITY RULES: has_weapons, least_armor, pdc_arc, missiles_in_pdc_arc
# =============================================================================

class TestCapabilityRules:
    """Tests for capability-based rules."""

    def test_has_weapons_with_weapons(self, mock_ship, mock_target, mock_stat_helpers):
        """has_weapons rule scores armed targets higher."""
        weapon = MagicMock()
        mock_target.get_components_by_ability = MagicMock(return_value=[weapon])

        rules = [{'type': 'has_weapons', 'weight': 100}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(100.0)

    def test_has_weapons_without_weapons(self, mock_ship, mock_target, mock_stat_helpers):
        """has_weapons rule gives 0 for unarmed targets."""
        mock_target.get_components_by_ability = MagicMock(return_value=[])

        rules = [{'type': 'has_weapons', 'weight': 100}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(0.0)

    def test_has_weapons_required_flag_rejects_unarmed(
        self, mock_ship, mock_target, mock_stat_helpers
    ):
        """has_weapons with required=True rejects unarmed targets."""
        mock_target.get_components_by_ability = MagicMock(return_value=[])

        rules = [{'type': 'has_weapons', 'weight': 100, 'required': True}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == float('-inf')

    def test_has_weapons_uses_capability_cache(
        self, mock_ship, mock_target, mock_stat_helpers
    ):
        """has_weapons uses capability cache when available."""
        # Target has no weapons according to get_components_by_ability
        mock_target.get_components_by_ability = MagicMock(return_value=[])

        # But cache says it has weapons
        cache = {mock_target.id: {'has_weapons': True}}

        rules = [{'type': 'has_weapons', 'weight': 100}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers,
            ship_capabilities_cache=cache
        )

        # Should use cached value
        assert score == pytest.approx(100.0)

    def test_least_armor_rule(self, mock_ship, mock_stat_helpers):
        """least_armor rule prefers targets with less armor HP."""
        # Mock LayerType.ARMOR
        from game.core.constants import LayerType

        heavy_armor = MagicMock()
        heavy_armor.id = 'heavy'
        heavy_armor.position = Vector2(100, 0)
        armor_comp = MagicMock()
        armor_comp.hp = 500
        heavy_armor.get_components_by_layer = MagicMock(return_value=[armor_comp])
        heavy_armor.get_components_by_ability = MagicMock(return_value=[])

        light_armor = MagicMock()
        light_armor.id = 'light'
        light_armor.position = Vector2(100, 0)
        light_comp = MagicMock()
        light_comp.hp = 100
        light_armor.get_components_by_layer = MagicMock(return_value=[light_comp])
        light_armor.get_components_by_ability = MagicMock(return_value=[])

        rules = [{'type': 'least_armor', 'weight': 1}]

        heavy_score = TargetEvaluator.evaluate(
            mock_ship, heavy_armor, rules, stat_helpers=mock_stat_helpers
        )
        light_score = TargetEvaluator.evaluate(
            mock_ship, light_armor, rules, stat_helpers=mock_stat_helpers
        )

        assert light_score > heavy_score


class TestPDCArcRules:
    """Tests for PDC arc rules."""

    def test_pdc_arc_missile_in_arc(self, mock_ship, mock_stat_helpers):
        """pdc_arc rule scores missiles in arc highly."""
        missile = MagicMock()
        missile.id = 'missile_1'
        missile.position = Vector2(100, 0)
        missile.type = 'missile'

        rules = [{'type': 'pdc_arc', 'weight': 500}]

        score = TargetEvaluator.evaluate(
            mock_ship, missile, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(500.0)

    def test_pdc_arc_missile_not_in_arc(self, mock_ship):
        """pdc_arc rule penalizes missiles not in arc."""
        missile = MagicMock()
        missile.id = 'missile_1'
        missile.position = Vector2(100, 0)
        missile.type = 'missile'

        # Not in arc
        helpers = {
            'get_hp_percent': lambda x: 1.0,
            'is_in_pdc_arc': lambda ship, target: False
        }

        rules = [{'type': 'pdc_arc', 'weight': 500}]

        score = TargetEvaluator.evaluate(
            mock_ship, missile, rules,
            stat_helpers=helpers
        )

        # Strong penalty
        assert score == pytest.approx(-999999)

    def test_pdc_arc_non_missile_passes_through(self, mock_ship, mock_target, mock_stat_helpers):
        """pdc_arc rule passes through for non-missiles."""
        mock_target.type = 'ship'

        rules = [{'type': 'pdc_arc', 'weight': 500}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        # Non-missile gets 0, passes through
        assert score == 0

    def test_pdc_arc_required_non_missile(self, mock_ship, mock_target, mock_stat_helpers):
        """pdc_arc required rule still passes non-missiles."""
        mock_target.type = 'ship'

        rules = [{'type': 'pdc_arc', 'weight': 500, 'required': True}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        # Non-missile passes through even with required
        assert score == 0

    def test_pdc_arc_attack_type_enum(self, mock_ship, mock_stat_helpers):
        """pdc_arc rule handles AttackType.MISSILE enum."""
        missile = MagicMock()
        missile.id = 'missile_1'
        missile.position = Vector2(100, 0)
        missile.type = AttackType.MISSILE

        rules = [{'type': 'pdc_arc', 'weight': 500}]

        score = TargetEvaluator.evaluate(
            mock_ship, missile, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(500.0)

    def test_missiles_in_pdc_arc_same_as_pdc_arc(self, mock_ship, mock_stat_helpers):
        """missiles_in_pdc_arc behaves same as pdc_arc."""
        missile = MagicMock()
        missile.id = 'missile_1'
        missile.position = Vector2(100, 0)
        missile.type = 'missile'

        rules = [{'type': 'missiles_in_pdc_arc', 'weight': 500}]

        score = TargetEvaluator.evaluate(
            mock_ship, missile, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(500.0)


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEvaluatorEdgeCases:
    """Edge case tests for TargetEvaluator."""

    def test_very_large_weight(self, mock_ship, mock_target, mock_stat_helpers):
        """Large weight values work correctly."""
        rules = [{'type': 'nearest', 'weight': 1000000}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(-100000000.0)

    def test_negative_weight_treated_as_zero(self, mock_ship, mock_target, mock_stat_helpers):
        """Negative weight falls through to factor logic."""
        rules = [{'type': 'nearest', 'weight': -1, 'factor': 1}]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        # weight <= 0, uses factor: dist * factor = 100
        assert score == pytest.approx(100.0)

    def test_mixed_rule_types(self, mock_ship, mock_target, mock_stat_helpers):
        """Multiple different rule types combine correctly."""
        weapon = MagicMock()
        mock_target.get_components_by_ability = MagicMock(return_value=[weapon])

        rules = [
            {'type': 'nearest', 'weight': 1},   # -100
            {'type': 'mass', 'weight': 1},      # +50
            {'type': 'has_weapons', 'weight': 100},  # +100
        ]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        # -100 + 50 + 100 = 50
        assert score == pytest.approx(50.0)

    def test_unknown_rule_type_ignored(self, mock_ship, mock_target, mock_stat_helpers):
        """Unknown rule types don't affect score."""
        rules = [
            {'type': 'unknown_rule', 'weight': 1000},
            {'type': 'nearest', 'weight': 1},  # -100
        ]

        score = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules,
            stat_helpers=mock_stat_helpers
        )

        # Unknown rule contributes 0
        assert score == pytest.approx(-100.0)

    def test_missing_velocity_attribute(self, mock_ship, mock_stat_helpers):
        """Speed rules handle missing velocity with default."""
        no_velocity = MagicMock(spec=['id', 'position'])
        no_velocity.id = 'no_vel'
        no_velocity.position = Vector2(100, 0)
        # No velocity attribute

        rules = [{'type': 'fastest', 'weight': 1}]

        # Should use default Vector2(0, 0), giving speed 0
        score = TargetEvaluator.evaluate(
            mock_ship, no_velocity, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(0.0)

    def test_missing_mass_attribute(self, mock_ship, mock_stat_helpers):
        """Mass rules handle missing mass with default 100."""
        no_mass = MagicMock(spec=['id', 'position'])
        no_mass.id = 'no_mass'
        no_mass.position = Vector2(100, 0)
        # No mass attribute

        rules = [{'type': 'mass', 'weight': 1}]

        # Should use default mass 100
        score = TargetEvaluator.evaluate(
            mock_ship, no_mass, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(100.0)
