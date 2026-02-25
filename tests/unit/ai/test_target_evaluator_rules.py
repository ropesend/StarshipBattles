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

        # Give target a .name attribute (Ships use .name as identifier, not .id)
        mock_target.name = 'target_ship'

        # But cache says it has weapons (keyed by .name)
        cache = {mock_target.name: {'has_weapons': True}}

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
        armor_comp.current_hp = 500  # Fixed: Component uses current_hp, not hp
        heavy_armor.get_components_by_layer = MagicMock(return_value=[armor_comp])
        heavy_armor.get_components_by_ability = MagicMock(return_value=[])

        light_armor = MagicMock()
        light_armor.id = 'light'
        light_armor.position = Vector2(100, 0)
        light_comp = MagicMock()
        light_comp.current_hp = 100  # Fixed: Component uses current_hp, not hp
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

    @staticmethod
    def _make_mock_missile(position, missile_type=AttackType.MISSILE):
        """Create a mock missile that satisfies IProjectile protocol."""
        missile = MagicMock()
        missile.position = position
        missile.is_alive = True
        missile.team_id = 1
        missile.radius = 5.0
        missile.type = missile_type
        return missile

    def test_pdc_arc_missile_in_arc(self, mock_ship, mock_stat_helpers):
        """pdc_arc rule scores missiles in arc highly."""
        missile = self._make_mock_missile(Vector2(100, 0))

        rules = [{'type': 'pdc_arc', 'weight': 500}]

        score = TargetEvaluator.evaluate(
            mock_ship, missile, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(500.0)

    def test_pdc_arc_missile_not_in_arc(self, mock_ship):
        """pdc_arc rule penalizes missiles not in arc."""
        missile = self._make_mock_missile(Vector2(100, 0))

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
        missile = self._make_mock_missile(Vector2(100, 0), AttackType.MISSILE)

        rules = [{'type': 'pdc_arc', 'weight': 500}]

        score = TargetEvaluator.evaluate(
            mock_ship, missile, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == pytest.approx(500.0)

    def test_missiles_in_pdc_arc_same_as_pdc_arc(self, mock_ship, mock_stat_helpers):
        """missiles_in_pdc_arc behaves same as pdc_arc."""
        missile = self._make_mock_missile(Vector2(100, 0))

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

    # DELETED: test_missing_velocity_attribute
    # PROJ-192: This test was invalid - PhysicsBody always has velocity attribute.
    # The getattr fallback pattern has been replaced with direct attribute access.

    # DELETED: test_missing_mass_attribute
    # PROJ-192: This test was invalid - PhysicsBody always has mass attribute.
    # The getattr fallback pattern has been replaced with direct attribute access.


# =============================================================================
# MIGRATED FROM: tests/unit/ai/target_evaluator/test_evaluation_rules.py
# =============================================================================

class TestMigratedDistanceEdgeCases:
    """Migrated distance edge cases from test_evaluation_rules.py."""

    def test_nearest_zero_distance(self, mock_ship, mock_stat_helpers):
        """Zero distance should give score of 0."""
        target = MagicMock()
        target.id = 'at_origin'
        target.position = Vector2(0, 0)  # Same as ship
        target.get_components_by_ability = MagicMock(return_value=[])
        target.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': 'nearest', 'weight': 1}]

        score = TargetEvaluator.evaluate(
            mock_ship, target, rules,
            stat_helpers=mock_stat_helpers
        )

        assert score == 0


class TestMigratedMassBehaviorEquivalence:
    """Migrated mass behavior equivalence tests from test_evaluation_rules.py."""

    def test_largest_same_as_mass(self, mock_ship, mock_target, mock_stat_helpers):
        """'largest' should behave same as 'mass'."""
        rules_mass = [{'type': 'mass', 'weight': 1}]
        rules_largest = [{'type': 'largest', 'weight': 1}]

        score_mass = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules_mass,
            stat_helpers=mock_stat_helpers
        )
        score_largest = TargetEvaluator.evaluate(
            mock_ship, mock_target, rules_largest,
            stat_helpers=mock_stat_helpers
        )

        assert score_mass == score_largest


class TestMigratedStrengthRules:
    """Migrated strength rules tests from test_evaluation_rules.py."""

    def test_strongest_uses_mass(self, mock_ship, mock_stat_helpers):
        """Strongest should favor higher mass."""
        weak = MagicMock()
        weak.id = 'weak'
        weak.position = Vector2(100, 0)
        weak.mass = 500
        weak.get_components_by_ability = MagicMock(return_value=[])
        weak.get_components_by_layer = MagicMock(return_value=[])

        strong = MagicMock()
        strong.id = 'strong'
        strong.position = Vector2(100, 0)
        strong.mass = 5000
        strong.get_components_by_ability = MagicMock(return_value=[])
        strong.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': 'strongest', 'weight': 1}]

        score_weak = TargetEvaluator.evaluate(
            mock_ship, weak, rules, stat_helpers=mock_stat_helpers
        )
        score_strong = TargetEvaluator.evaluate(
            mock_ship, strong, rules, stat_helpers=mock_stat_helpers
        )

        assert score_strong > score_weak

    def test_weakest_uses_inverse_mass(self, mock_ship, mock_stat_helpers):
        """Weakest should favor lower mass."""
        weak = MagicMock()
        weak.id = 'weak'
        weak.position = Vector2(100, 0)
        weak.mass = 500
        weak.get_components_by_ability = MagicMock(return_value=[])
        weak.get_components_by_layer = MagicMock(return_value=[])

        strong = MagicMock()
        strong.id = 'strong'
        strong.position = Vector2(100, 0)
        strong.mass = 5000
        strong.get_components_by_ability = MagicMock(return_value=[])
        strong.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': 'weakest', 'weight': 1}]

        score_weak = TargetEvaluator.evaluate(
            mock_ship, weak, rules, stat_helpers=mock_stat_helpers
        )
        score_strong = TargetEvaluator.evaluate(
            mock_ship, strong, rules, stat_helpers=mock_stat_helpers
        )

        assert score_weak > score_strong


class TestMigratedPDCArcRequired:
    """Migrated PDC arc required flag test from test_evaluation_rules.py."""

    def test_pdc_arc_required_missile_out_of_arc(self, mock_ship):
        """Required pdc_arc should return -inf for missile out of arc."""
        missile = MagicMock()
        missile.id = 'missile_out'
        missile.position = Vector2(-100, 0)  # Behind ship
        missile.type = AttackType.MISSILE

        # Helper that returns False for out of arc
        helpers = {
            'get_hp_percent': lambda x: 1.0,
            'is_in_pdc_arc': lambda ship, target: False
        }

        rules = [{'type': 'pdc_arc', 'weight': 100, 'required': True}]

        score = TargetEvaluator.evaluate(
            mock_ship, missile, rules,
            stat_helpers=helpers
        )

        assert score == float('-inf')


# =============================================================================
# TCG-FND-018: Speed Rule with Factor-Based Scoring
# MIGRATED FROM: tests/unit/ai/target_evaluator/test_evaluation_rules.py
# CRITICAL: Bug-documenting tests - preserve all comments
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

    def test_slowest_with_weight_slower_is_higher(self, mock_ship, mock_stat_helpers):
        """slowest rule with weight correctly prefers slower targets."""
        slow = MagicMock()
        slow.id = 'slow'
        slow.position = Vector2(100, 0)
        slow.velocity = Vector2(5, 0)  # speed = 5
        slow.get_components_by_ability = MagicMock(return_value=[])
        slow.get_components_by_layer = MagicMock(return_value=[])

        fast = MagicMock()
        fast.id = 'fast'
        fast.position = Vector2(100, 0)
        fast.velocity = Vector2(50, 0)  # speed = 50
        fast.get_components_by_ability = MagicMock(return_value=[])
        fast.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': 'slowest', 'weight': 1}]

        score_slow = TargetEvaluator.evaluate(
            mock_ship, slow, rules, stat_helpers=mock_stat_helpers
        )
        score_fast = TargetEvaluator.evaluate(
            mock_ship, fast, rules, stat_helpers=mock_stat_helpers
        )

        # With weight: slow gets -5, fast gets -50
        # Less negative (slower) should be higher
        assert score_slow > score_fast
        assert score_slow == -5
        assert score_fast == -50

    def test_slowest_with_factor_documents_behavior(self, mock_ship, mock_stat_helpers):
        """Document slowest rule behavior when using factor (weight=0).

        With the current implementation:
        - slowest with factor uses: val = -speed * -factor = speed * factor
        - This makes FASTER targets score HIGHER, which contradicts 'slowest' intent

        This test documents the actual behavior as-is. If this is a bug, fixing
        it would require changing _eval_speed_rule to use -factor for slowest.
        """
        slow = MagicMock()
        slow.id = 'slow'
        slow.position = Vector2(100, 0)
        slow.velocity = Vector2(5, 0)  # speed = 5
        slow.get_components_by_ability = MagicMock(return_value=[])
        slow.get_components_by_layer = MagicMock(return_value=[])

        fast = MagicMock()
        fast.id = 'fast'
        fast.position = Vector2(100, 0)
        fast.velocity = Vector2(50, 0)  # speed = 50
        fast.get_components_by_ability = MagicMock(return_value=[])
        fast.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': 'slowest', 'weight': 0, 'factor': 1}]

        score_slow = TargetEvaluator.evaluate(
            mock_ship, slow, rules, stat_helpers=mock_stat_helpers
        )
        score_fast = TargetEvaluator.evaluate(
            mock_ship, fast, rules, stat_helpers=mock_stat_helpers
        )

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

    def test_fastest_with_weight_faster_is_higher(self, mock_ship, mock_stat_helpers):
        """fastest rule with weight correctly prefers faster targets."""
        slow = MagicMock()
        slow.id = 'slow'
        slow.position = Vector2(100, 0)
        slow.velocity = Vector2(5, 0)
        slow.get_components_by_ability = MagicMock(return_value=[])
        slow.get_components_by_layer = MagicMock(return_value=[])

        fast = MagicMock()
        fast.id = 'fast'
        fast.position = Vector2(100, 0)
        fast.velocity = Vector2(50, 0)
        fast.get_components_by_ability = MagicMock(return_value=[])
        fast.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': 'fastest', 'weight': 1}]

        score_slow = TargetEvaluator.evaluate(
            mock_ship, slow, rules, stat_helpers=mock_stat_helpers
        )
        score_fast = TargetEvaluator.evaluate(
            mock_ship, fast, rules, stat_helpers=mock_stat_helpers
        )

        # With weight: slow gets 5, fast gets 50
        assert score_fast > score_slow
        assert score_slow == 5
        assert score_fast == 50

    def test_fastest_with_factor_faster_is_higher(self, mock_ship, mock_stat_helpers):
        """fastest rule with factor also correctly prefers faster targets."""
        slow = MagicMock()
        slow.id = 'slow'
        slow.position = Vector2(100, 0)
        slow.velocity = Vector2(5, 0)
        slow.get_components_by_ability = MagicMock(return_value=[])
        slow.get_components_by_layer = MagicMock(return_value=[])

        fast = MagicMock()
        fast.id = 'fast'
        fast.position = Vector2(100, 0)
        fast.velocity = Vector2(50, 0)
        fast.get_components_by_ability = MagicMock(return_value=[])
        fast.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': 'fastest', 'weight': 0, 'factor': 1}]

        score_slow = TargetEvaluator.evaluate(
            mock_ship, slow, rules, stat_helpers=mock_stat_helpers
        )
        score_fast = TargetEvaluator.evaluate(
            mock_ship, fast, rules, stat_helpers=mock_stat_helpers
        )

        # With factor: slow gets 5, fast gets 50
        assert score_fast > score_slow

    def test_slowest_with_negative_factor(self, mock_ship, mock_stat_helpers):
        """slowest with negative factor should work correctly."""
        slow = MagicMock()
        slow.id = 'slow'
        slow.position = Vector2(100, 0)
        slow.velocity = Vector2(5, 0)
        slow.get_components_by_ability = MagicMock(return_value=[])
        slow.get_components_by_layer = MagicMock(return_value=[])

        fast = MagicMock()
        fast.id = 'fast'
        fast.position = Vector2(100, 0)
        fast.velocity = Vector2(50, 0)
        fast.get_components_by_ability = MagicMock(return_value=[])
        fast.get_components_by_layer = MagicMock(return_value=[])

        # Using negative factor to compensate for the double negation
        rules = [{'type': 'slowest', 'weight': 0, 'factor': -1}]

        score_slow = TargetEvaluator.evaluate(
            mock_ship, slow, rules, stat_helpers=mock_stat_helpers
        )
        score_fast = TargetEvaluator.evaluate(
            mock_ship, fast, rules, stat_helpers=mock_stat_helpers
        )

        # With factor=-1: val = -speed * -(-1) = -speed
        # slow: -5, fast: -50
        # Now slower target correctly scores higher
        assert score_slow > score_fast, "With negative factor, slower should score higher"

    def test_stationary_target_zero_speed(self, mock_ship, mock_stat_helpers):
        """Stationary target (speed=0) should get score of 0."""
        stationary = MagicMock()
        stationary.id = 'stationary'
        stationary.position = Vector2(100, 0)
        stationary.velocity = Vector2(0, 0)
        stationary.get_components_by_ability = MagicMock(return_value=[])
        stationary.get_components_by_layer = MagicMock(return_value=[])

        rules_fastest = [{'type': 'fastest', 'weight': 1}]
        rules_slowest = [{'type': 'slowest', 'weight': 1}]

        score_fastest = TargetEvaluator.evaluate(
            mock_ship, stationary, rules_fastest, stat_helpers=mock_stat_helpers
        )
        score_slowest = TargetEvaluator.evaluate(
            mock_ship, stationary, rules_slowest, stat_helpers=mock_stat_helpers
        )

        assert score_fastest == 0
        assert score_slowest == 0
