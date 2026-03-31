"""
ToHitAttackModifier Test Scenarios (TOHIT-ATK-001 to TOHIT-ATK-004)

These tests validate the ToHitAttackModifier ability using A/B comparison
battles.  Each test runs a baseline battle (without the modifier) and a
variant battle (with the modifier), then compares measured damage.

Stacking rules (inter-group SUM, intra-group MAX):
- Same stack_group: only the highest value counts (redundancy)
- Different stack_groups: values are summed (stacking)
- No stack_group: each component is its own group (all stack)

All tests use the low-accuracy beam (base_accuracy=0.5, falloff=0.002)
against a stationary target at mid-range (400px).  With damage=1 per hit
and no reload, damage_dealt equals the number of hits.

Expected hit rates (additive stacking + sigmoid, defense_score=0.332):
- No modifier:           36.1%
- +1.0 bonus:            60.5%
- +1.0 same group x2:    60.5%  (MAX=1.0, no change)
- +1.0 diff groups x2:   80.6%  (SUM=2.0)
- -0.5 penalty:          25.5%
"""

from simulation_tests.scenarios import TestMetadata
from simulation_tests.scenarios.templates import ComparisonScenario
from simulation_tests.scenarios.validation import check_exact, check_tost, check_true
from simulation_tests.test_constants import (
    MID_RANGE_DISTANCE,
    STANDARD_SEED,
    STANDARD_MARGIN,
    SENSOR_ATTACK_VALUE,
    TOHIT_PENALTY_VALUE,
    BEAM_LOW_ACCURACY,
    BEAM_LOW_FALLOFF,
)


# =============================================================================
# EXPECTED VALUES
# =============================================================================
# Beam: base_accuracy=0.5, falloff=0.002
# Target: mass=400, radius=29.47px, stationary, no defense
# Surface distance: 400 - 29.47 = 370.53px
# Range penalty: 0.002 * 370.53 = 0.7411

TOHIT_ATK_TEST_TICKS = 1000  # Higher tick count for statistical reliability
# Hit rates include target defense_score=0.332 (from mass=400 size component)
TOHIT_ATK_BASELINE_HIT_RATE = 0.3606       # sigmoid(0.5 - 0.7411 - 0.332)
TOHIT_ATK_SENSOR_HIT_RATE = 0.6052         # sigmoid(0.5 + 1.0 - 0.7411 - 0.332)
TOHIT_ATK_DOUBLE_SENSOR_HIT_RATE = 0.8065  # sigmoid(0.5 + 2.0 - 0.7411 - 0.332)
TOHIT_ATK_PENALTY_HIT_RATE = 0.2549        # sigmoid(0.5 - 0.5 - 0.7411 - 0.332)


# =============================================================================
# TOHIT-ATK-001: Sensor Increases Accuracy
# =============================================================================

class SensorIncreasesAccuracyScenario(ComparisonScenario):
    """
    TOHIT-ATK-001: Sensor Increases Accuracy

    Battle A: Low accuracy beam, no sensor → ~36% hit rate
    Battle B: Low accuracy beam + ToHitAttackModifier(1.0) → ~61% hit rate

    Proves that the ToHitAttackModifier ability increases the attacker's
    hit probability via the sigmoid formula.
    """

    metadata = TestMetadata(
        test_id="TOHIT-ATK-001",
        category="ToHitAttackModifier",
        subcategory="Basic Effect",
        name="Sensor Increases Accuracy",
        summary="Compares measured hit rate: no sensor vs +1.0 sensor",
        conditions=[
            "Attacker (no sensor): Test_Attacker_Beam360_Low.json",
            "Attacker (with sensor): Test_Attacker_Beam360_Low_Sensor.json (+1.0 attack bonus)",
            "Target: Test_Target_Stationary.json (stationary, no defense modifiers)",
            f"Distance: {MID_RANGE_DISTANCE} pixels (mid range)",
            f"Beam: base_accuracy={BEAM_LOW_ACCURACY}, falloff={BEAM_LOW_FALLOFF}",
            f"Test Duration: {TOHIT_ATK_TEST_TICKS} ticks per battle",
        ],
        edge_cases=[
            "Sensor bonus is additive in sigmoid net_score",
            "Both battles use identical seed for fair comparison",
        ],
        expected_outcome=f"Baseline ~{TOHIT_ATK_BASELINE_HIT_RATE:.0%}, "
                         f"Variant ~{TOHIT_ATK_SENSOR_HIT_RATE:.0%}",
        pass_criteria="variant_damage > baseline_damage, hit rates match sigmoid predictions",
        max_ticks=TOHIT_ATK_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["tohit", "sensor", "attack-modifier", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Beam360_Low.json"
    baseline_target_ship = "Test_Target_Stationary.json"
    variant_attacker_ship = "Test_Attacker_Beam360_Low_Sensor.json"
    variant_target_ship = "Test_Target_Stationary.json"
    distance = MID_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify sensor is present on variant
        sensor = self.get_ability(self.attacker, 'ToHitAttackModifier')
        checks.append(check_exact(
            "Sensor Attack Value", SENSOR_ATTACK_VALUE,
            sensor.value if sensor else 0.0,
        ))

        # Precondition: both battles dealt damage
        checks.append(check_true(
            "Baseline Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: sensor increases measured damage
        checks.append(check_true(
            "Sensor Increases Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"baseline={self.baseline_damage_dealt}, "
                   f"variant={self.variant_damage_dealt}, "
                   f"delta=+{self.variant_damage_dealt - self.baseline_damage_dealt}",
            phase="outcome",
        ))

        # Statistical: hit rates match expected values
        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_tost(
            "Baseline Hit Rate",
            TOHIT_ATK_BASELINE_HIT_RATE,
            int(self.baseline_damage_dealt),
            baseline_shots,
            margin=STANDARD_MARGIN,
            phase="outcome",
        ))
        checks.append(check_tost(
            "Variant Hit Rate",
            TOHIT_ATK_SENSOR_HIT_RATE,
            int(self.variant_damage_dealt),
            variant_shots,
            margin=STANDARD_MARGIN,
            phase="outcome",
        ))

        return checks


# =============================================================================
# TOHIT-ATK-002: Same Stacking Group Does Not Stack
# =============================================================================

class SameGroupDoesNotStackScenario(ComparisonScenario):
    """
    TOHIT-ATK-002: Same Stacking Group Does Not Stack

    Battle A: Low accuracy beam + 1 sensor (group_a) → ~61% hit rate
    Battle B: Low accuracy beam + 2 sensors (both group_a) → ~61% hit rate

    Proves that intra-group MAX applies: two identical sensors in the same
    stacking group provide no additional benefit over one.
    """

    metadata = TestMetadata(
        test_id="TOHIT-ATK-002",
        category="ToHitAttackModifier",
        subcategory="Stacking Rules",
        name="Same Group Does Not Stack",
        summary="Two sensors in the same stacking group provide no additional benefit",
        conditions=[
            "Attacker (1 sensor): Test_Attacker_Beam360_Low_SensorA.json (1x group_a)",
            "Attacker (2 sensors): Test_Attacker_Beam360_Low_2xSensorA.json (2x group_a)",
            "Target: Test_Target_Stationary.json (stationary, no defense modifiers)",
            f"Distance: {MID_RANGE_DISTANCE} pixels",
            f"Test Duration: {TOHIT_ATK_TEST_TICKS} ticks per battle",
        ],
        edge_cases=[
            "Intra-group MAX: MAX(1.0, 1.0) = 1.0",
            "Redundant sensors in same group provide no stacking benefit",
        ],
        expected_outcome=f"Both battles ~{TOHIT_ATK_SENSOR_HIT_RATE:.0%} (identical — same group MAX)",
        pass_criteria="variant_damage ≈ baseline_damage",
        max_ticks=TOHIT_ATK_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["tohit", "sensor", "stacking", "same-group", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Beam360_Low_SensorA.json"
    baseline_target_ship = "Test_Target_Stationary.json"
    variant_attacker_ship = "Test_Attacker_Beam360_Low_2xSensorA.json"
    variant_target_ship = "Test_Target_Stationary.json"
    distance = MID_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both battles dealt damage
        checks.append(check_true(
            "Baseline Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: damage should be identical (same seed, same effective bonus)
        checks.append(check_exact(
            "Same Group No Extra Damage",
            self.baseline_damage_dealt,
            self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# TOHIT-ATK-003: Different Stacking Groups Stack Additively
# =============================================================================

class DifferentGroupsStackScenario(ComparisonScenario):
    """
    TOHIT-ATK-003: Different Stacking Groups Stack Additively

    Battle A: Low accuracy beam + 1 sensor (group_a) → ~61% hit rate
    Battle B: Low accuracy beam + sensor_a + sensor_b → ~81% hit rate

    Proves that inter-group SUM applies: sensors from different stacking
    groups combine additively (1.0 + 1.0 = 2.0 total bonus).
    """

    metadata = TestMetadata(
        test_id="TOHIT-ATK-003",
        category="ToHitAttackModifier",
        subcategory="Stacking Rules",
        name="Different Groups Stack Additively",
        summary="Sensors from different stacking groups combine additively",
        conditions=[
            "Attacker (1 group): Test_Attacker_Beam360_Low_SensorA.json (group_a only)",
            "Attacker (2 groups): Test_Attacker_Beam360_Low_SensorAB.json (group_a + group_b)",
            "Target: Test_Target_Stationary.json (stationary, no defense modifiers)",
            f"Distance: {MID_RANGE_DISTANCE} pixels",
            f"Test Duration: {TOHIT_ATK_TEST_TICKS} ticks per battle",
        ],
        edge_cases=[
            "Inter-group SUM: 1.0 + 1.0 = 2.0 total bonus",
            "Higher bonus → higher net_score → higher sigmoid output",
        ],
        expected_outcome=f"Baseline ~{TOHIT_ATK_SENSOR_HIT_RATE:.0%} (1 group), "
                         f"Variant ~{TOHIT_ATK_DOUBLE_SENSOR_HIT_RATE:.0%} (2 groups summed)",
        pass_criteria="variant_damage > baseline_damage",
        max_ticks=TOHIT_ATK_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["tohit", "sensor", "stacking", "different-groups", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Beam360_Low_SensorA.json"
    baseline_target_ship = "Test_Target_Stationary.json"
    variant_attacker_ship = "Test_Attacker_Beam360_Low_SensorAB.json"
    variant_target_ship = "Test_Target_Stationary.json"
    distance = MID_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both dealt damage
        checks.append(check_true(
            "Baseline Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: variant (2 groups) should deal more damage than baseline (1 group)
        checks.append(check_true(
            "Additional Group Increases Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"baseline={self.baseline_damage_dealt}, "
                   f"variant={self.variant_damage_dealt}, "
                   f"delta=+{self.variant_damage_dealt - self.baseline_damage_dealt}",
            phase="outcome",
        ))

        # Statistical: variant hit rate matches 2.0 bonus expectation
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_tost(
            "Variant Hit Rate (2 groups)",
            TOHIT_ATK_DOUBLE_SENSOR_HIT_RATE,
            int(self.variant_damage_dealt),
            variant_shots,
            margin=STANDARD_MARGIN,
            phase="outcome",
        ))

        return checks


# =============================================================================
# TOHIT-ATK-004: Negative Modifier Reduces Accuracy
# =============================================================================

class NegativeModifierReducesAccuracyScenario(ComparisonScenario):
    """
    TOHIT-ATK-004: Negative Modifier Reduces Accuracy

    Battle A: Low accuracy beam, no modifier → ~36% hit rate
    Battle B: Low accuracy beam + ToHitAttackModifier(-0.5) → ~25% hit rate

    Proves that negative ToHitAttackModifier values reduce hit probability.
    """

    metadata = TestMetadata(
        test_id="TOHIT-ATK-004",
        category="ToHitAttackModifier",
        subcategory="Basic Effect",
        name="Negative Modifier Reduces Accuracy",
        summary="Negative ToHitAttackModifier reduces measured hit rate",
        conditions=[
            "Attacker (no modifier): Test_Attacker_Beam360_Low.json",
            "Attacker (penalty): Test_Attacker_Beam360_Low_Penalty.json (-0.5 attack penalty)",
            "Target: Test_Target_Stationary.json (stationary, no defense modifiers)",
            f"Distance: {MID_RANGE_DISTANCE} pixels",
            f"Test Duration: {TOHIT_ATK_TEST_TICKS} ticks per battle",
        ],
        edge_cases=[
            "Negative value subtracts from net_score in sigmoid",
            "Hit rate should decrease, not increase",
        ],
        expected_outcome=f"Baseline ~{TOHIT_ATK_BASELINE_HIT_RATE:.0%}, "
                         f"Variant ~{TOHIT_ATK_PENALTY_HIT_RATE:.0%} (penalty reduces accuracy)",
        pass_criteria="variant_damage < baseline_damage",
        max_ticks=TOHIT_ATK_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["tohit", "penalty", "negative", "attack-modifier", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Beam360_Low.json"
    baseline_target_ship = "Test_Target_Stationary.json"
    variant_attacker_ship = "Test_Attacker_Beam360_Low_Penalty.json"
    variant_target_ship = "Test_Target_Stationary.json"
    distance = MID_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify penalty is present on variant
        penalty = self.get_ability(self.attacker, 'ToHitAttackModifier')
        checks.append(check_exact(
            "Penalty Value", TOHIT_PENALTY_VALUE,
            penalty.value if penalty else 0.0,
        ))

        # Precondition: both battles dealt damage
        checks.append(check_true(
            "Baseline Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))
        checks.append(check_true(
            "Variant Dealt Damage",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
        ))

        # Outcome: penalty reduces measured damage
        checks.append(check_true(
            "Penalty Reduces Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"baseline={self.baseline_damage_dealt}, "
                   f"variant={self.variant_damage_dealt}, "
                   f"delta={self.variant_damage_dealt - self.baseline_damage_dealt}",
            phase="outcome",
        ))

        # Statistical: hit rates match expected values
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_tost(
            "Variant Hit Rate (penalty)",
            TOHIT_ATK_PENALTY_HIT_RATE,
            int(self.variant_damage_dealt),
            variant_shots,
            margin=STANDARD_MARGIN,
            phase="outcome",
        ))

        return checks
