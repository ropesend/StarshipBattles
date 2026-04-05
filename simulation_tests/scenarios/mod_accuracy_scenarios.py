"""
Accuracy Additive Modifier Scenarios (MOD-ACC-001 through MOD-ACC-005)

Behavioral simulation tests for the accuracy_add modifier (test_accuracy_boost
and test_accuracy_penalty). Tests validate that the modifier changes measured
combat hit rates at various distances, matching the sigmoid hit-chance formula:

    P = 1 / (1 + e^-x)
    x = base_accuracy - (falloff * surface_distance + defense_score)

The accuracy_add modifier adds to base_accuracy via the 'add' operation,
shifting the sigmoid curve and changing hit probability at every distance.
The effect is nonlinear: +1.0 accuracy matters more at long range (where
the sigmoid is steep) than at point-blank (where it's already near 1.0).

Ship Files:
- Test_Attacker_Beam_AccBoost.json — test_beam_med_acc_1dmg(acc=2.0, falloff=0.001)
  + test_accuracy_boost(param=2), accuracy 2.0 + 2*0.5 = 3.0
- Test_Attacker_Beam_AccPenalty.json — test_beam_med_acc_1dmg(acc=2.0, falloff=0.001)
  + test_accuracy_penalty(param=2), accuracy 2.0 + 2*(-0.5) = 1.0
- Test_Attacker_Beam360_Med.json — test_beam_med_acc_1dmg(acc=2.0, falloff=0.001),
  no modifier (baseline)
- Test_Target_Stationary.json — test_armor_extreme_hp(1B HP, mass=400, stationary)

Test Coverage:
- MOD-ACC-001: Stat gate — modifier applied correctly (base_accuracy == 3.0)
- MOD-ACC-002: Mid-range comparison — boosted vs baseline with calculated expected hit rates
- MOD-ACC-003: Range-dependent effect — modifier's impact grows at longer distance
- MOD-ACC-004: Negative penalty — accuracy_penalty reduces hit rate at mid-range
- MOD-ACC-005: Long-range effectiveness — boosted beam ~87.5% vs baseline ~72.1%
"""
from simulation_tests.scenarios.base import TestMetadata
from simulation_tests.scenarios.templates import StaticTargetScenario, ComparisonScenario
from simulation_tests.scenarios.validation import check_approx, check_tost, check_true
from simulation_tests.scenarios.beam_scenarios import (
    calculate_expected_hit_chance,
    calculate_defense_score,
)
from simulation_tests.test_constants import (
    STANDARD_SEED,
    POINT_BLANK_DISTANCE,
    MID_RANGE_DISTANCE,
    MODIFIER_TEST_TICKS,
    STANDARD_MARGIN,
    MOD_BASE_BEAM_ACCURACY,
)

# =============================================================================
# COMMON SHIP REFERENCES
# =============================================================================

# test_beam_med_acc_1dmg(acc=2.0, falloff=0.001) + test_accuracy_boost(param=2)
# accuracy = 2.0 + (2 * 0.5) = 3.0
ACC_BOOST_SHIP = "Test_Attacker_Beam_AccBoost.json"
# test_beam_med_acc_1dmg(acc=2.0, falloff=0.001) + test_accuracy_penalty(param=2)
# accuracy = 2.0 + (2 * -0.5) = 1.0
ACC_PENALTY_SHIP = "Test_Attacker_Beam_AccPenalty.json"
# test_beam_med_acc_1dmg(acc=2.0, falloff=0.001), no modifier
BASELINE_SHIP = "Test_Attacker_Beam360_Med.json"
# test_armor_extreme_hp (1B HP, mass=400, stationary)
TARGET_SHIP = "Test_Target_Stationary.json"

# =============================================================================
# BEAM & TARGET CONSTANTS (from component JSON)
# =============================================================================

BASE_ACCURACY = MOD_BASE_BEAM_ACCURACY  # 2.0
ACCURACY_FALLOFF = 0.001                # from test_beam_med_acc_1dmg
BOOSTED_ACCURACY = 3.0                  # 2.0 + (2 * 0.5)
PENALIZED_ACCURACY = 1.0               # 2.0 + (2 * -0.5)
TARGET_MASS = 400.0                     # stationary target mass
LONG_RANGE_DISTANCE = 750               # near max range (800)

# =============================================================================
# CALCULATED EXPECTED HIT RATES
# =============================================================================

# Target defense score (stationary, no ECM, no maneuver)
_TARGET_DEFENSE = calculate_defense_score(TARGET_MASS)
# Target radius for surface distance calculation
_TARGET_RADIUS = 40.0 * ((TARGET_MASS / 1000.0) ** (1.0 / 3.0))


def _expected_p(accuracy: float, center_distance: float) -> float:
    """Calculate expected hit probability for given accuracy and center distance."""
    surface_dist = center_distance - _TARGET_RADIUS
    return calculate_expected_hit_chance(
        accuracy, ACCURACY_FALLOFF, surface_dist, 0.0, _TARGET_DEFENSE
    )


# Pre-calculate expected hit rates for documentation and validation
P_BASELINE_MID = _expected_p(BASE_ACCURACY, MID_RANGE_DISTANCE)        # ~78.5%
P_BOOSTED_MID = _expected_p(BOOSTED_ACCURACY, MID_RANGE_DISTANCE)      # ~90.9%
P_PENALTY_MID = _expected_p(PENALIZED_ACCURACY, MID_RANGE_DISTANCE)    # ~57.4%
P_BASELINE_LONG = _expected_p(BASE_ACCURACY, LONG_RANGE_DISTANCE)      # ~72.1%
P_BOOSTED_LONG = _expected_p(BOOSTED_ACCURACY, LONG_RANGE_DISTANCE)    # ~87.5%
P_BASELINE_PB = _expected_p(BASE_ACCURACY, POINT_BLANK_DISTANCE)       # ~83.2%
P_BOOSTED_PB = _expected_p(BOOSTED_ACCURACY, POINT_BLANK_DISTANCE)     # ~93.1%


# =============================================================================
# MOD-ACC-001: Stat Check Gate
# =============================================================================

class ModAcc001_StatGateScenario(StaticTargetScenario):
    """
    MOD-ACC-001: Verify accuracy modifier is applied correctly.

    Quick sanity gate: beam.base_accuracy == 3.0 after modifier,
    weapon fires and hits at point-blank with expected hit rate.
    """
    metadata = TestMetadata(
        test_id="MOD-ACC-001",
        category="AccuracyAdditive",
        subcategory="AccuracyAdditive",
        name="Stat gate — modifier applied (accuracy 2.0→3.0)",
        summary="Verify test_accuracy_boost(2) sets beam base_accuracy to 3.0; hits at point-blank",
        conditions=[
            f"Attacker: {ACC_BOOST_SHIP} (test_beam_med_acc_1dmg + test_accuracy_boost(param=2), accuracy 2.0→3.0)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary, mass={TARGET_MASS})",
            f"Distance: {POINT_BLANK_DISTANCE}px (point-blank)",
            f"Expected hit rate: {P_BOOSTED_PB:.1%} (sigmoid with defense_score={_TARGET_DEFENSE:.4f})",
        ],
        edge_cases=["Additive modifier uses 'add' operation, not 'multiply'"],
        expected_outcome=f"beam.base_accuracy == {BOOSTED_ACCURACY}, hit rate ≈ {P_BOOSTED_PB:.1%}",
        pass_criteria=f"base_accuracy == {BOOSTED_ACCURACY} AND hit_rate passes TOST at {P_BOOSTED_PB:.4f}",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "accuracy_add", "stat_gate"],
    )

    attacker_ship = ACC_BOOST_SHIP
    target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        self.actual_accuracy = beam.base_accuracy if beam else None

    def _collect_extra_results(self, battle_engine):
        self.results['expected_accuracy'] = BOOSTED_ACCURACY
        self.results['actual_accuracy'] = self.actual_accuracy
        self.results['expected_hit_rate'] = P_BOOSTED_PB

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks

        # Data: modifier applied correctly
        checks.append(check_approx(
            "Modified Beam Accuracy", BOOSTED_ACCURACY,
            self.actual_accuracy or 0.0, tolerance=0.001, phase="data",
        ))

        # Outcome: hit rate matches sigmoid prediction
        shots = self.results.get('attacker_total_shots_fired', 0)
        hits = self.damage_dealt  # damage=1 per hit, so damage == hits
        if shots > 0:
            checks.append(check_tost(
                "Hit Rate at Point-Blank", P_BOOSTED_PB,
                int(hits), shots, margin=STANDARD_MARGIN, phase="outcome",
            ))

        return checks


# =============================================================================
# MOD-ACC-002: Mid-Range Statistical Comparison
# =============================================================================

class ModAcc002_MidRangeComparisonScenario(ComparisonScenario):
    """
    MOD-ACC-002: Compare hit rates at mid-range (400px).

    Baseline (acc=2.0): expected ~78.5% hit rate
    Variant (acc=3.0): expected ~90.9% hit rate

    Both hit rates validated with check_tost. Damage ratio should
    approximate the hit-rate ratio (~1.16x).
    """
    metadata = TestMetadata(
        test_id="MOD-ACC-002",
        category="AccuracyAdditive",
        subcategory="AccuracyAdditive",
        name="Mid-range statistical comparison (400px)",
        summary=(
            f"Baseline (acc={BASE_ACCURACY}) ≈ {P_BASELINE_MID:.1%} vs "
            f"boosted (acc={BOOSTED_ACCURACY}) ≈ {P_BOOSTED_MID:.1%} at {MID_RANGE_DISTANCE}px"
        ),
        conditions=[
            f"Baseline: {BASELINE_SHIP} (test_beam_med_acc_1dmg, no modifier, accuracy={BASE_ACCURACY})",
            f"Variant: {ACC_BOOST_SHIP} (test_beam_med_acc_1dmg + test_accuracy_boost(param=2), accuracy={BOOSTED_ACCURACY})",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary, mass={TARGET_MASS})",
            f"Distance: {MID_RANGE_DISTANCE}px (mid-range)",
            f"Expected baseline P: {P_BASELINE_MID:.4f}, variant P: {P_BOOSTED_MID:.4f}",
            f"Defense score: {_TARGET_DEFENSE:.4f}, surface distance: {MID_RANGE_DISTANCE - _TARGET_RADIUS:.1f}px",
        ],
        edge_cases=[
            "Mid-range tests accuracy in the steeper part of the sigmoid",
            "Both ships have damage=1 and reload=0, so damage_dealt == hits",
        ],
        expected_outcome=(
            f"Baseline ≈ {P_BASELINE_MID:.1%} hit rate, "
            f"Variant ≈ {P_BOOSTED_MID:.1%} hit rate, "
            f"damage ratio ≈ {P_BOOSTED_MID / P_BASELINE_MID:.2f}x"
        ),
        pass_criteria="Both hit rates pass TOST within ±10% margin",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "accuracy_add", "comparison", "statistical"],
    )

    baseline_attacker_ship = BASELINE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = ACC_BOOST_SHIP
    variant_target_ship = TARGET_SHIP
    distance = MID_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both battles dealt damage
        checks.append(check_true(
            "Baseline Dealt Damage", self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Dealt Damage", self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}", phase="precondition",
        ))

        # Outcome: statistical validation of both hit rates
        b_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        v_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        b_hits = self.baseline_damage_dealt  # damage=1 per hit
        v_hits = self.variant_damage_dealt

        if b_shots > 0:
            checks.append(check_tost(
                "Baseline Hit Rate", P_BASELINE_MID,
                int(b_hits), b_shots, margin=STANDARD_MARGIN, phase="outcome",
            ))
        if v_shots > 0:
            checks.append(check_tost(
                "Variant Hit Rate", P_BOOSTED_MID,
                int(v_hits), v_shots, margin=STANDARD_MARGIN, phase="outcome",
            ))

        # Outcome: variant deals more damage than baseline
        checks.append(check_true(
            "Boosted Accuracy Increases Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=(
                f"baseline={self.baseline_damage_dealt} ({b_hits}/{b_shots} shots), "
                f"variant={self.variant_damage_dealt} ({v_hits}/{v_shots} shots)"
            ),
            phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-ACC-003: Range-Dependent Effect (modifier matters more at range)
# =============================================================================

class ModAcc003_RangeDependentEffectScenario(ComparisonScenario):
    """
    MOD-ACC-003: Prove accuracy modifier's combat impact grows with distance.

    At long range (750px) the sigmoid curve is steeper, so +1.0 accuracy
    produces a larger relative improvement than at point-blank:
    - Point-blank: boosted/baseline ratio ≈ 93.1% / 83.2% = 1.12x
    - Long-range:  boosted/baseline ratio ≈ 87.5% / 72.1% = 1.21x

    This test fires at long range and verifies the damage ratio exceeds
    the point-blank ratio, proving the nonlinear sigmoid interaction.
    """
    _PB_RATIO = P_BOOSTED_PB / P_BASELINE_PB  # ~1.12

    metadata = TestMetadata(
        test_id="MOD-ACC-003",
        category="AccuracyAdditive",
        subcategory="AccuracyAdditive",
        name="Range-dependent effect — modifier matters more at 750px",
        summary=(
            f"At {LONG_RANGE_DISTANCE}px, damage ratio (boosted/baseline) should exceed "
            f"point-blank ratio of {P_BOOSTED_PB / P_BASELINE_PB:.2f}x"
        ),
        conditions=[
            f"Baseline: {BASELINE_SHIP} (test_beam_med_acc_1dmg, accuracy={BASE_ACCURACY})",
            f"Variant: {ACC_BOOST_SHIP} (test_beam_med_acc_1dmg + test_accuracy_boost(param=2), accuracy={BOOSTED_ACCURACY})",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {LONG_RANGE_DISTANCE}px (long range)",
            f"Expected baseline P: {P_BASELINE_LONG:.4f}, variant P: {P_BOOSTED_LONG:.4f}",
            f"Long-range ratio: {P_BOOSTED_LONG / P_BASELINE_LONG:.3f}x vs point-blank ratio: {P_BOOSTED_PB / P_BASELINE_PB:.3f}x",
        ],
        edge_cases=[
            "Tests sigmoid nonlinearity: same +1.0 accuracy has different impact at different ranges",
            "Proves the modifier provides increasing value as range increases",
        ],
        expected_outcome=(
            f"Long-range damage ratio ≈ {P_BOOSTED_LONG / P_BASELINE_LONG:.2f}x, "
            f"exceeding point-blank ratio ≈ {P_BOOSTED_PB / P_BASELINE_PB:.2f}x"
        ),
        pass_criteria="damage_ratio > point_blank_ratio",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "accuracy_add", "range_dependent", "sigmoid"],
    )

    baseline_attacker_ship = BASELINE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = ACC_BOOST_SHIP
    variant_target_ship = TARGET_SHIP
    distance = LONG_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both battles dealt meaningful damage
        checks.append(check_true(
            "Baseline Dealt Damage", self.baseline_damage_dealt > 10,
            detail=f"damage={self.baseline_damage_dealt}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Dealt Damage", self.variant_damage_dealt > 10,
            detail=f"damage={self.variant_damage_dealt}", phase="precondition",
        ))

        # Outcome: statistical validation at long range
        b_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        v_shots = self.results.get('variant_attacker_total_shots_fired', 0)

        if b_shots > 0:
            checks.append(check_tost(
                "Baseline Hit Rate at Long Range", P_BASELINE_LONG,
                int(self.baseline_damage_dealt), b_shots,
                margin=STANDARD_MARGIN, phase="outcome",
            ))
        if v_shots > 0:
            checks.append(check_tost(
                "Variant Hit Rate at Long Range", P_BOOSTED_LONG,
                int(self.variant_damage_dealt), v_shots,
                margin=STANDARD_MARGIN, phase="outcome",
            ))

        # Outcome: damage ratio exceeds point-blank ratio
        if self.baseline_damage_dealt > 0:
            actual_ratio = self.variant_damage_dealt / self.baseline_damage_dealt
            checks.append(check_true(
                "Long-Range Ratio Exceeds Point-Blank Ratio",
                actual_ratio > self._PB_RATIO,
                detail=(
                    f"long_range_ratio={actual_ratio:.3f}, "
                    f"point_blank_ratio={self._PB_RATIO:.3f}"
                ),
                phase="outcome",
            ))

        return checks


# =============================================================================
# MOD-ACC-004: Negative Penalty Reduces Hit Rate
# =============================================================================

class ModAcc004_NegativePenaltyScenario(ComparisonScenario):
    """
    MOD-ACC-004: Verify negative accuracy modifier reduces hit rate.

    Baseline (acc=2.0): expected ~78.5% hit rate at 400px
    Variant (acc=1.0): expected ~57.4% hit rate at 400px

    The penalty modifier (test_accuracy_penalty, param=2, accuracy_add = -1.0)
    reduces base_accuracy from 2.0 to 1.0, measurably degrading hit rate.
    """
    metadata = TestMetadata(
        test_id="MOD-ACC-004",
        category="AccuracyAdditive",
        subcategory="AccuracyAdditive",
        name="Negative penalty reduces hit rate at mid-range",
        summary=(
            f"Penalty (acc={PENALIZED_ACCURACY}) ≈ {P_PENALTY_MID:.1%} vs "
            f"baseline (acc={BASE_ACCURACY}) ≈ {P_BASELINE_MID:.1%} at {MID_RANGE_DISTANCE}px"
        ),
        conditions=[
            f"Baseline: {BASELINE_SHIP} (test_beam_med_acc_1dmg, no modifier, accuracy={BASE_ACCURACY})",
            f"Variant: {ACC_PENALTY_SHIP} (test_beam_med_acc_1dmg + test_accuracy_penalty(param=2), accuracy={PENALIZED_ACCURACY})",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary, mass={TARGET_MASS})",
            f"Distance: {MID_RANGE_DISTANCE}px (mid-range)",
            f"Expected baseline P: {P_BASELINE_MID:.4f}, penalty P: {P_PENALTY_MID:.4f}",
        ],
        edge_cases=[
            "Negative accuracy_add tests modifier bidirectionality",
            "Penalty reduces net_score, shifting sigmoid left → lower hit rate",
        ],
        expected_outcome=(
            f"Baseline ≈ {P_BASELINE_MID:.1%} hit rate, "
            f"Penalty ≈ {P_PENALTY_MID:.1%} hit rate"
        ),
        pass_criteria="Both hit rates pass TOST; penalty_damage < baseline_damage",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "accuracy_add", "negative", "penalty"],
    )

    baseline_attacker_ship = BASELINE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = ACC_PENALTY_SHIP
    variant_target_ship = TARGET_SHIP
    distance = MID_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify penalty was applied
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            checks.append(check_approx(
                "Penalized Beam Accuracy", PENALIZED_ACCURACY,
                beam.base_accuracy, tolerance=0.001, phase="data",
            ))

        # Precondition: both dealt damage
        checks.append(check_true(
            "Baseline Dealt Damage", self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}", phase="precondition",
        ))
        checks.append(check_true(
            "Penalty Dealt Damage", self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}", phase="precondition",
        ))

        # Outcome: statistical validation of both hit rates
        b_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        v_shots = self.results.get('variant_attacker_total_shots_fired', 0)

        if b_shots > 0:
            checks.append(check_tost(
                "Baseline Hit Rate", P_BASELINE_MID,
                int(self.baseline_damage_dealt), b_shots,
                margin=STANDARD_MARGIN, phase="outcome",
            ))
        if v_shots > 0:
            checks.append(check_tost(
                "Penalty Hit Rate", P_PENALTY_MID,
                int(self.variant_damage_dealt), v_shots,
                margin=STANDARD_MARGIN, phase="outcome",
            ))

        # Outcome: penalty reduces damage
        checks.append(check_true(
            "Penalty Reduces Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=(
                f"baseline={self.baseline_damage_dealt}, "
                f"penalty={self.variant_damage_dealt}"
            ),
            phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-ACC-005: Long-Range Effectiveness
# =============================================================================

class ModAcc005_LongRangeEffectivenessScenario(ComparisonScenario):
    """
    MOD-ACC-005: Validate hit rates at long range (750px).

    At 750px the baseline beam hits ~72.1% while the boosted beam
    hits ~87.5%. Both rates are validated statistically with check_tost.
    This tests the modifier's effectiveness near the weapon's max range
    where accuracy degradation from distance is most severe.
    """
    metadata = TestMetadata(
        test_id="MOD-ACC-005",
        category="AccuracyAdditive",
        subcategory="AccuracyAdditive",
        name=f"Long-range effectiveness ({LONG_RANGE_DISTANCE}px)",
        summary=(
            f"Baseline ≈ {P_BASELINE_LONG:.1%} vs boosted ≈ {P_BOOSTED_LONG:.1%} "
            f"at {LONG_RANGE_DISTANCE}px near max range"
        ),
        conditions=[
            f"Baseline: {BASELINE_SHIP} (test_beam_med_acc_1dmg, accuracy={BASE_ACCURACY})",
            f"Variant: {ACC_BOOST_SHIP} (test_beam_med_acc_1dmg + test_accuracy_boost(param=2), accuracy={BOOSTED_ACCURACY})",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {LONG_RANGE_DISTANCE}px (near max range of 800px)",
            f"Expected baseline P: {P_BASELINE_LONG:.4f}, variant P: {P_BOOSTED_LONG:.4f}",
        ],
        edge_cases=[
            f"At {LONG_RANGE_DISTANCE}px, range penalty is significant",
            "Tests that accuracy boost still provides meaningful advantage near max range",
        ],
        expected_outcome=(
            f"Baseline ≈ {P_BASELINE_LONG:.1%}, "
            f"Variant ≈ {P_BOOSTED_LONG:.1%}, "
            f"ratio ≈ {P_BOOSTED_LONG / P_BASELINE_LONG:.2f}x"
        ),
        pass_criteria="Both hit rates pass TOST within margin",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "accuracy_add", "long_range", "statistical"],
    )

    baseline_attacker_ship = BASELINE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = ACC_BOOST_SHIP
    variant_target_ship = TARGET_SHIP
    distance = LONG_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both dealt meaningful damage
        checks.append(check_true(
            "Baseline Dealt Damage", self.baseline_damage_dealt > 10,
            detail=f"damage={self.baseline_damage_dealt}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Dealt Damage", self.variant_damage_dealt > 10,
            detail=f"damage={self.variant_damage_dealt}", phase="precondition",
        ))

        # Outcome: statistical validation of both hit rates
        b_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        v_shots = self.results.get('variant_attacker_total_shots_fired', 0)

        if b_shots > 0:
            checks.append(check_tost(
                "Baseline Hit Rate at Long Range", P_BASELINE_LONG,
                int(self.baseline_damage_dealt), b_shots,
                margin=STANDARD_MARGIN, phase="outcome",
            ))
        if v_shots > 0:
            checks.append(check_tost(
                "Variant Hit Rate at Long Range", P_BOOSTED_LONG,
                int(self.variant_damage_dealt), v_shots,
                margin=STANDARD_MARGIN, phase="outcome",
            ))

        # Outcome: variant deals more damage
        checks.append(check_true(
            "Boosted Accuracy Effective at Long Range",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=(
                f"baseline={self.baseline_damage_dealt}, "
                f"variant={self.variant_damage_dealt}"
            ),
            phase="outcome",
        ))

        return checks
