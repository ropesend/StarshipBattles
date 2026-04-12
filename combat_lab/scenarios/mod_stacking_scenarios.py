"""
Multi-Modifier Stacking Scenarios (MOD-STACK-001 through MOD-STACK-005)

Behavioral simulation tests for modifier stacking interactions. When multiple
modifiers are applied to the same component, they interact according to their
operation type:
  - Two 'multiply' modifiers on the SAME stat COMPOUND: 1.5x * 2.0x = 3.0x
  - Two modifiers on DIFFERENT stats are INDEPENDENT: damage and accuracy
    don't interfere with each other
  - Combined effects produce CALCULABLE combat outcomes: total_damage =
    hits * damage_per_hit, where hits depend on accuracy and damage depends
    on damage_mult

Ship Files:
- Test_Attacker_Beam_DualModifier.json — test_beam_med_acc_1dmg
  + test_damage_boost(1.5) + test_damage_boost_b(2.0), dmg 1*1.5*2.0=3.0
- Test_Attacker_Beam_DmgAndAcc.json — test_beam_med_acc_1dmg
  + test_damage_boost(1.5) + test_accuracy_boost(2), dmg->1.5 + acc->3.0
- Test_Attacker_Beam_DamageBoost.json — test_beam_med_acc_1dmg
  + test_damage_boost(1.5), dmg 1->1.5
- Test_Attacker_Beam360_Med.json — test_beam_med_acc_1dmg (no modifier)
- Test_Target_Stationary.json — test_armor_extreme_hp (1B HP, stationary)

Test Coverage:
- MOD-STACK-001: Stat gate — compound damage 1.5*2.0=3.0, substantial damage dealt
- MOD-STACK-002: Independent stats — damage AND accuracy both correct, damage proves both active
- MOD-STACK-003: Compound ratio — dual(3.0x) vs single(1.5x) = 2.0x damage ratio
- MOD-STACK-004: Combined effect — dmg+acc at mid-range with calculated expected ratio
- MOD-STACK-005: Compound vs additive proof — ratio is 3.0x (compound), not 3.5x (additive)
"""

from combat_lab.scenarios.base import TestMetadata
from combat_lab.scenarios.templates import StaticTargetScenario, ComparisonScenario
from combat_lab.scenarios.validation import check_approx, check_true
from combat_lab.scenarios.beam_scenarios import (
    calculate_expected_hit_chance,
    calculate_defense_score,
)
from combat_lab.test_constants import (
    STANDARD_SEED,
    POINT_BLANK_DISTANCE,
    MID_RANGE_DISTANCE,
    MODIFIER_TEST_TICKS,
    MOD_BASE_BEAM_DAMAGE,
    MOD_BASE_BEAM_ACCURACY,
    DAMAGE_BOOST_ATTACKER_SHIP,
)

# =============================================================================
# COMMON SHIP REFERENCES
# =============================================================================

# test_beam_med_acc_1dmg + test_damage_boost(1.5) + test_damage_boost_b(2.0), dmg 1*1.5*2.0=3.0
DUAL_MODIFIER_SHIP = "Test_Attacker_Beam_DualModifier.json"
# test_beam_med_acc_1dmg + test_damage_boost(1.5) + test_accuracy_boost(2), dmg->1.5 + acc->3.0
DMG_AND_ACC_SHIP = "Test_Attacker_Beam_DmgAndAcc.json"
# test_beam_med_acc_1dmg + test_damage_boost(1.5), dmg 1->1.5
SINGLE_BOOST_SHIP = DAMAGE_BOOST_ATTACKER_SHIP
# test_beam_med_acc_1dmg (no modifier, baseline)
BASELINE_SHIP = "Test_Attacker_Beam360_Med.json"
# test_armor_extreme_hp (1B HP, stationary)
TARGET_SHIP = "Test_Target_Stationary.json"

# =============================================================================
# STACKING CONSTANTS
# =============================================================================

BASE_DAMAGE = MOD_BASE_BEAM_DAMAGE          # 1
BASE_ACCURACY = MOD_BASE_BEAM_ACCURACY      # 2.0
ACCURACY_FALLOFF = 0.001                    # from test_beam_med_acc_1dmg
TARGET_MASS = 400.0

# Compound damage: 1 * 1.5 * 2.0 = 3.0 (NOT 1 * (1.5 + 2.0) = 3.5)
DUAL_EXPECTED_DAMAGE = BASE_DAMAGE * 1.5 * 2.0     # 3.0
SINGLE_EXPECTED_DAMAGE = BASE_DAMAGE * 1.5          # 1.5
ADDITIVE_WOULD_BE = BASE_DAMAGE * (1.5 + 2.0)      # 3.5 (wrong if someone adds instead of compounds)

# Independent stats
EXPECTED_ACCURACY_WITH_BOOST = BASE_ACCURACY + (2 * 0.5)  # 3.0
DMGACC_EXPECTED_DAMAGE = BASE_DAMAGE * 1.5                 # 1.5

# Calculated expected combined ratio at mid-range (400px)
_TARGET_DEFENSE = calculate_defense_score(TARGET_MASS)
_TARGET_RADIUS = 40.0 * ((TARGET_MASS / 1000.0) ** (1.0 / 3.0))
_SURFACE_DIST_MID = MID_RANGE_DISTANCE - _TARGET_RADIUS

P_BASELINE_MID = calculate_expected_hit_chance(
    BASE_ACCURACY, ACCURACY_FALLOFF, _SURFACE_DIST_MID, 0.0, _TARGET_DEFENSE
)  # ~78.5%
P_DMGACC_MID = calculate_expected_hit_chance(
    EXPECTED_ACCURACY_WITH_BOOST, ACCURACY_FALLOFF, _SURFACE_DIST_MID, 0.0, _TARGET_DEFENSE
)  # ~90.9%

# Combined ratio: (variant_hits * variant_dmg) / (baseline_hits * baseline_dmg)
# = (P_dmgacc * 1.5) / (P_baseline * 1.0)
EXPECTED_COMBINED_RATIO = (P_DMGACC_MID * DMGACC_EXPECTED_DAMAGE) / (P_BASELINE_MID * BASE_DAMAGE)

TEST_TICKS = MODIFIER_TEST_TICKS  # 500
RATIO_TOLERANCE = 0.15


# =============================================================================
# MOD-STACK-001: Stat Gate — Compound Damage
# =============================================================================

class ModStack001_CompoundStatGateScenario(StaticTargetScenario):
    """
    MOD-STACK-001: Verify two damage multipliers compound correctly.

    beam.damage == 1 * 1.5 * 2.0 = 3.0 (compound multiply).
    Weapon fires and deals substantial damage at point-blank.
    """
    metadata = TestMetadata(
        test_id="MOD-STACK-001",
        category="ModifierStacking",
        subcategory="ModifierStacking",
        name="Stat gate — compound damage (1.5 * 2.0 = 3.0)",
        summary=f"Verify two multiplicative modifiers compound to {DUAL_EXPECTED_DAMAGE} (not {ADDITIVE_WOULD_BE})",
        conditions=[
            f"Attacker: {DUAL_MODIFIER_SHIP} (test_beam_med_acc_1dmg + test_damage_boost(1.5) + test_damage_boost_b(2.0))",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Expected: {BASE_DAMAGE} * 1.5 * 2.0 = {DUAL_EXPECTED_DAMAGE} (compound), NOT {BASE_DAMAGE} * (1.5+2.0) = {ADDITIVE_WOULD_BE} (additive)",
            f"Distance: {POINT_BLANK_DISTANCE}px",
        ],
        edge_cases=["Multiplicative stacking compounds, not adds"],
        expected_outcome=f"beam.damage == {DUAL_EXPECTED_DAMAGE}, damage > 10",
        pass_criteria=f"damage == {DUAL_EXPECTED_DAMAGE} AND damage > 10",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "stacking", "compound"],
    )

    attacker_ship = DUAL_MODIFIER_SHIP
    target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        self.actual_damage = beam.damage if beam else None

    def _collect_extra_results(self, battle_engine):
        self.results['expected_damage'] = DUAL_EXPECTED_DAMAGE
        self.results['actual_damage'] = self.actual_damage

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks

        # Data: compound damage correct
        checks.append(check_approx(
            "Compound Damage (1.5 * 2.0)", DUAL_EXPECTED_DAMAGE,
            self.actual_damage or 0.0, tolerance=0.001, phase="data",
        ))

        # Outcome: substantial damage dealt
        checks.append(check_true(
            "Substantial Damage Dealt", self.damage_dealt > 10,
            detail=f"damage={self.damage_dealt}", phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-STACK-002: Independent Stats — Both Active in Combat
# =============================================================================

class ModStack002_IndependentStatsScenario(ComparisonScenario):
    """
    MOD-STACK-002: Verify modifiers on different stats are independent.

    Baseline: unmodified beam (dmg=1, acc=2.0)
    Variant: beam with damage_boost(1.5) + accuracy_boost(2) (dmg=1.5, acc=3.0)

    At mid-range, the variant should deal more damage from BOTH higher damage
    per hit AND higher hit rate. This proves both modifiers are active in combat,
    not just that the attributes were set correctly.
    """
    metadata = TestMetadata(
        test_id="MOD-STACK-002",
        category="ModifierStacking",
        subcategory="ModifierStacking",
        name="Independent stats — both modifiers active in combat",
        summary=(
            f"Damage+accuracy modifiers independently improve combat outcome at {MID_RANGE_DISTANCE}px"
        ),
        conditions=[
            f"Baseline: {BASELINE_SHIP} (test_beam_med_acc_1dmg, dmg={BASE_DAMAGE}, acc={BASE_ACCURACY}, no modifiers)",
            f"Variant: {DMG_AND_ACC_SHIP} (test_beam_med_acc_1dmg + test_damage_boost(1.5) + test_accuracy_boost(2), dmg={DMGACC_EXPECTED_DAMAGE}, acc={EXPECTED_ACCURACY_WITH_BOOST})",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {MID_RANGE_DISTANCE}px (mid-range, accuracy affects hit rate)",
        ],
        edge_cases=["Modifiers on different stats must not interfere"],
        expected_outcome="Variant deals substantially more damage (higher dmg per hit + more hits)",
        pass_criteria="variant deals more damage AND both stat values correct",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "stacking", "independent"],
    )

    baseline_attacker_ship = BASELINE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = DMG_AND_ACC_SHIP
    variant_target_ship = TARGET_SHIP
    distance = MID_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify both modifiers applied on variant
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            checks.append(check_approx(
                "Variant Damage", DMGACC_EXPECTED_DAMAGE,
                beam.damage, tolerance=0.001, phase="data",
            ))
            checks.append(check_approx(
                "Variant Accuracy", EXPECTED_ACCURACY_WITH_BOOST,
                beam.base_accuracy, tolerance=0.001, phase="data",
            ))

        # Precondition: both dealt substantial damage
        checks.append(check_true(
            "Baseline Dealt Damage", self.baseline_damage_dealt > 10,
            detail=f"damage={self.baseline_damage_dealt}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Dealt Damage", self.variant_damage_dealt > 10,
            detail=f"damage={self.variant_damage_dealt}", phase="precondition",
        ))

        # Outcome: variant deals more (both modifiers contributing)
        checks.append(check_true(
            "Combined Modifiers Increase Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=(
                f"baseline={self.baseline_damage_dealt}, "
                f"variant={self.variant_damage_dealt}"
            ),
            phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-STACK-003: Compound Ratio — Dual vs Single
# =============================================================================

class ModStack003_CompoundRatioScenario(ComparisonScenario):
    """
    MOD-STACK-003: Prove dual compound modifier produces expected damage ratio.

    Baseline: 1.5x damage (single modifier)
    Variant: 3.0x damage (two modifiers compounded: 1.5 * 2.0)
    Expected ratio: 3.0 / 1.5 = 2.0x

    Since both have identical hit rates (same accuracy, same distance),
    the damage ratio exactly equals the damage-per-hit ratio.
    """
    metadata = TestMetadata(
        test_id="MOD-STACK-003",
        category="ModifierStacking",
        subcategory="ModifierStacking",
        name="Compound ratio — dual(3.0x) vs single(1.5x) = 2.0x",
        summary=f"Damage ratio ≈ {DUAL_EXPECTED_DAMAGE}/{SINGLE_EXPECTED_DAMAGE} = {DUAL_EXPECTED_DAMAGE / SINGLE_EXPECTED_DAMAGE}x",
        conditions=[
            f"Baseline: {SINGLE_BOOST_SHIP} (test_beam_med_acc_1dmg + test_damage_boost(1.5), dmg={SINGLE_EXPECTED_DAMAGE})",
            f"Variant: {DUAL_MODIFIER_SHIP} (test_beam_med_acc_1dmg + test_damage_boost(1.5) + test_damage_boost_b(2.0), dmg={DUAL_EXPECTED_DAMAGE})",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px (identical hit rates)",
        ],
        edge_cases=["Ratio is deterministic — same hits, different damage per hit"],
        expected_outcome=f"Damage ratio ≈ {DUAL_EXPECTED_DAMAGE / SINGLE_EXPECTED_DAMAGE}x",
        pass_criteria=f"ratio within ±{RATIO_TOLERANCE} of {DUAL_EXPECTED_DAMAGE / SINGLE_EXPECTED_DAMAGE}",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "stacking", "compound", "ratio"],
    )

    baseline_attacker_ship = SINGLE_BOOST_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = DUAL_MODIFIER_SHIP
    variant_target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both dealt substantial damage
        checks.append(check_true(
            "Baseline Dealt Damage", self.baseline_damage_dealt > 10,
            detail=f"damage={self.baseline_damage_dealt}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Dealt Damage", self.variant_damage_dealt > 10,
            detail=f"damage={self.variant_damage_dealt}", phase="precondition",
        ))

        # Outcome: damage ratio matches expected compound ratio
        expected_ratio = DUAL_EXPECTED_DAMAGE / SINGLE_EXPECTED_DAMAGE  # 2.0
        if self.baseline_damage_dealt > 0:
            ratio = self.variant_damage_dealt / self.baseline_damage_dealt
            checks.append(check_approx(
                f"Damage Ratio ≈ {expected_ratio}x", expected_ratio,
                ratio, tolerance=RATIO_TOLERANCE, phase="outcome",
            ))

        return checks


# =============================================================================
# MOD-STACK-004: Combined Effect at Mid-Range (Calculated)
# =============================================================================

class ModStack004_CombinedEffectScenario(ComparisonScenario):
    """
    MOD-STACK-004: Prove combined damage+accuracy effect matches calculated expectation.

    At mid-range (400px):
    - Baseline: dmg=1.0, acc=2.0 → hit_rate ≈ {P_BASELINE_MID:.1%}
    - Variant: dmg=1.5, acc=3.0 → hit_rate ≈ {P_DMGACC_MID:.1%}
    - Expected ratio: (variant_hits * 1.5) / (baseline_hits * 1.0) ≈ {EXPECTED_COMBINED_RATIO:.2f}x

    This is the most multifactorial test: damage_mult AND accuracy_add
    interact through the sigmoid hit-chance formula to produce a combined
    combat improvement greater than either modifier alone.
    """
    metadata = TestMetadata(
        test_id="MOD-STACK-004",
        category="ModifierStacking",
        subcategory="ModifierStacking",
        name=f"Combined effect at {MID_RANGE_DISTANCE}px — calculated ratio ≈ {EXPECTED_COMBINED_RATIO:.2f}x",
        summary=(
            f"Damage(1.5x) + accuracy(+1.0) at {MID_RANGE_DISTANCE}px: "
            f"expected ratio ≈ {EXPECTED_COMBINED_RATIO:.2f}x "
            f"(hit rates: {P_BASELINE_MID:.1%} vs {P_DMGACC_MID:.1%}, damage: {BASE_DAMAGE} vs {DMGACC_EXPECTED_DAMAGE})"
        ),
        conditions=[
            f"Baseline: {BASELINE_SHIP} (dmg={BASE_DAMAGE}, acc={BASE_ACCURACY}, hit rate ≈ {P_BASELINE_MID:.4f})",
            f"Variant: {DMG_AND_ACC_SHIP} (dmg={DMGACC_EXPECTED_DAMAGE}, acc={EXPECTED_ACCURACY_WITH_BOOST}, hit rate ≈ {P_DMGACC_MID:.4f})",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, stationary, mass={TARGET_MASS})",
            f"Distance: {MID_RANGE_DISTANCE}px, defense_score={_TARGET_DEFENSE:.4f}",
            f"Combined ratio: ({P_DMGACC_MID:.4f} * {DMGACC_EXPECTED_DAMAGE}) / ({P_BASELINE_MID:.4f} * {BASE_DAMAGE}) = {EXPECTED_COMBINED_RATIO:.4f}",
        ],
        edge_cases=[
            "Tests interaction of two different modifier types through the combat system",
            "Accuracy boosts hit rate via sigmoid, damage boosts per-hit damage linearly",
        ],
        expected_outcome=f"Damage ratio ≈ {EXPECTED_COMBINED_RATIO:.2f}x",
        pass_criteria=f"ratio within ±{RATIO_TOLERANCE + 0.05} of {EXPECTED_COMBINED_RATIO:.2f}",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "stacking", "combined", "multifactorial"],
    )

    baseline_attacker_ship = BASELINE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = DMG_AND_ACC_SHIP
    variant_target_ship = TARGET_SHIP
    distance = MID_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both dealt substantial damage
        checks.append(check_true(
            "Baseline Dealt Damage", self.baseline_damage_dealt > 10,
            detail=f"damage={self.baseline_damage_dealt}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Dealt Damage", self.variant_damage_dealt > 10,
            detail=f"damage={self.variant_damage_dealt}", phase="precondition",
        ))

        # Outcome: combined ratio matches calculated expectation
        if self.baseline_damage_dealt > 0:
            ratio = self.variant_damage_dealt / self.baseline_damage_dealt
            checks.append(check_approx(
                f"Combined Ratio ≈ {EXPECTED_COMBINED_RATIO:.2f}x",
                EXPECTED_COMBINED_RATIO,
                ratio, tolerance=RATIO_TOLERANCE + 0.05, phase="outcome",
            ))

        return checks


# =============================================================================
# MOD-STACK-005: Compound vs Additive Proof
# =============================================================================

class ModStack005_CompoundNotAdditiveScenario(ComparisonScenario):
    """
    MOD-STACK-005: Prove stacking is COMPOUND (multiply), not ADDITIVE (sum).

    If modifiers compounded: 1 * 1.5 * 2.0 = 3.0 → ratio vs base = 3.0x
    If modifiers added:      1 * (1.5 + 2.0) = 3.5 → ratio vs base = 3.5x

    By measuring the damage ratio against an unmodified baseline, we can
    distinguish compound from additive stacking. The ratio should be ≈ 3.0,
    NOT ≈ 3.5.
    """
    metadata = TestMetadata(
        test_id="MOD-STACK-005",
        category="ModifierStacking",
        subcategory="ModifierStacking",
        name="Compound vs additive — ratio is 3.0x not 3.5x",
        summary=(
            f"Dual modifier vs unmodified: ratio ≈ {DUAL_EXPECTED_DAMAGE}x (compound), "
            f"not ≈ {ADDITIVE_WOULD_BE}x (if additive)"
        ),
        conditions=[
            f"Baseline: {BASELINE_SHIP} (test_beam_med_acc_1dmg, no modifier, dmg={BASE_DAMAGE})",
            f"Variant: {DUAL_MODIFIER_SHIP} (test_beam_med_acc_1dmg + test_damage_boost(1.5) + test_damage_boost_b(2.0), dmg={DUAL_EXPECTED_DAMAGE})",
            f"If compound: ratio = {DUAL_EXPECTED_DAMAGE}/{BASE_DAMAGE} = {DUAL_EXPECTED_DAMAGE / BASE_DAMAGE}x",
            f"If additive: ratio would be {ADDITIVE_WOULD_BE}/{BASE_DAMAGE} = {ADDITIVE_WOULD_BE / BASE_DAMAGE}x",
        ],
        edge_cases=[
            "This test FAILS if someone changes stacking from compound to additive",
            "Distinguishes 3.0x (correct) from 3.5x (wrong) with tight tolerance",
        ],
        expected_outcome=f"Damage ratio ≈ {DUAL_EXPECTED_DAMAGE / BASE_DAMAGE}x (compound)",
        pass_criteria=f"ratio closer to {DUAL_EXPECTED_DAMAGE}x than {ADDITIVE_WOULD_BE}x",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "stacking", "compound_vs_additive"],
    )

    baseline_attacker_ship = BASELINE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = DUAL_MODIFIER_SHIP
    variant_target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both dealt substantial damage
        checks.append(check_true(
            "Baseline Dealt Damage", self.baseline_damage_dealt > 10,
            detail=f"damage={self.baseline_damage_dealt}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Dealt Damage", self.variant_damage_dealt > 10,
            detail=f"damage={self.variant_damage_dealt}", phase="precondition",
        ))

        if self.baseline_damage_dealt > 0:
            ratio = self.variant_damage_dealt / self.baseline_damage_dealt
            compound_ratio = DUAL_EXPECTED_DAMAGE / BASE_DAMAGE   # 3.0
            additive_ratio = ADDITIVE_WOULD_BE / BASE_DAMAGE      # 3.5

            # Outcome: ratio matches compound (3.0x), not additive (3.5x)
            checks.append(check_approx(
                f"Ratio ≈ {compound_ratio}x (compound)", compound_ratio,
                ratio, tolerance=RATIO_TOLERANCE, phase="outcome",
            ))

            # Outcome: ratio is NOT close to additive value
            distance_to_compound = abs(ratio - compound_ratio)
            distance_to_additive = abs(ratio - additive_ratio)
            checks.append(check_true(
                "Closer to Compound than Additive",
                distance_to_compound < distance_to_additive,
                detail=(
                    f"ratio={ratio:.3f}, "
                    f"distance_to_compound={distance_to_compound:.3f}, "
                    f"distance_to_additive={distance_to_additive:.3f}"
                ),
                phase="outcome",
            ))

        return checks
