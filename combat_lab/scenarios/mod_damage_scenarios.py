"""
Damage Multiplier Modifier Scenarios (MOD-DMG-001 through MOD-DMG-005)

Behavioral simulation tests for the damage_mult modifier. The damage multiplier
scales per-hit damage linearly — a 1.5x modifier on a 1-damage beam produces
1.5 damage per hit. Since both baseline and variant fire at the same rate and
hit at the same rate (same accuracy, same target, same distance), the total
damage ratio should exactly match the multiplier value.

This is more deterministic than accuracy tests: the damage ratio is independent
of RNG because both ships have identical hit chances.

Base component: test_beam_med_acc_1dmg (damage=1, accuracy=2.0, falloff=0.001, reload=0)

Ship Files:
- Test_Attacker_Beam_DamageBoost.json — test_beam_med_acc_1dmg
  + test_damage_boost(1.5), dmg 1->1.5
- Test_Attacker_Beam_DmgBoost_Min.json — test_beam_med_acc_1dmg
  + test_damage_boost(1.0), dmg 1->1.0 (identity)
- Test_Attacker_Beam_DmgBoost_Max.json — test_beam_med_acc_1dmg
  + test_damage_boost(10.0), dmg 1->10.0
- Test_Attacker_Beam_DmgPenalty.json — test_beam_med_acc_1dmg
  + test_damage_penalty(0.5), dmg 1->0.5
- Test_Attacker_Beam360_Med.json — test_beam_med_acc_1dmg
  (no modifier, dmg=1, baseline)
- Test_Target_Stationary.json — test_armor_extreme_hp (1B HP, stationary)

Test Coverage:
- MOD-DMG-001: Stat gate — damage boosted (1->1.5), weapon fires and hits
- MOD-DMG-002: Damage ratio — 1.5x boost produces exactly 1.5x total damage
- MOD-DMG-003: Extreme ratio — 10.0x vs 1.0x produces exactly 10.0x total damage
- MOD-DMG-004: Negative penalty — 0.5x damage reduces total damage by half
- MOD-DMG-005: Range-independent — damage ratio holds at mid-range (same hits, scaled damage)
"""

from combat_lab.scenarios.base import TestMetadata
from combat_lab.scenarios.templates import StaticTargetScenario, ComparisonScenario
from combat_lab.scenarios.validation import check_approx, check_true
from combat_lab.test_constants import (
    STANDARD_SEED,
    POINT_BLANK_DISTANCE,
    MID_RANGE_DISTANCE,
    MODIFIER_TEST_TICKS,
    MOD_BASE_BEAM_DAMAGE,
    DAMAGE_BOOST_PARAM,
    MOD_EXPECTED_DAMAGE,
    DAMAGE_BOOST_ATTACKER_SHIP,
)

# =============================================================================
# COMMON SHIP REFERENCES
# =============================================================================

# test_beam_med_acc_1dmg + test_damage_boost(1.5), dmg 1->1.5
BOOST_SHIP = DAMAGE_BOOST_ATTACKER_SHIP
# test_beam_med_acc_1dmg + test_damage_boost(1.0), dmg 1->1.0 (identity)
IDENTITY_SHIP = "Test_Attacker_Beam_DmgBoost_Min.json"
# test_beam_med_acc_1dmg + test_damage_boost(10.0), dmg 1->10.0
MAX_SHIP = "Test_Attacker_Beam_DmgBoost_Max.json"
# test_beam_med_acc_1dmg + test_damage_penalty(0.5), dmg 1->0.5
PENALTY_SHIP = "Test_Attacker_Beam_DmgPenalty.json"
# test_beam_med_acc_1dmg (no modifier, dmg=1)
BASELINE_SHIP = "Test_Attacker_Beam360_Med.json"
# test_armor_extreme_hp (1B HP, stationary)
TARGET_SHIP = "Test_Target_Stationary.json"

# =============================================================================
# DAMAGE CONSTANTS
# =============================================================================

BASE_DAMAGE = MOD_BASE_BEAM_DAMAGE      # 1
BOOSTED_DAMAGE = MOD_EXPECTED_DAMAGE    # 1.5
MAX_DAMAGE = BASE_DAMAGE * 10.0         # 10.0
IDENTITY_DAMAGE = BASE_DAMAGE * 1.0     # 1.0
PENALIZED_DAMAGE = BASE_DAMAGE * 0.5    # 0.5

PENALTY_PARAM = 0.5
TEST_TICKS = MODIFIER_TEST_TICKS        # 500

# Damage ratio tolerance: since both ships fire at the same rate and have
# the same hit chance, the ratio should be very precise. Tolerance accounts
# for rounding of fractional damage per hit.
RATIO_TOLERANCE = 0.1


# =============================================================================
# MOD-DMG-001: Stat Gate — Damage Boosted
# =============================================================================

class ModDmg001_StatGateScenario(StaticTargetScenario):
    """
    MOD-DMG-001: Quick sanity — damage modifier applied correctly.

    Boosted beam at point-blank: beam.damage == 1.5 (1 * 1.5), fires and
    hits with substantial damage. Confirms modifier loaded before behavioral tests.
    """
    metadata = TestMetadata(
        test_id="MOD-DMG-001",
        category="DamageMultiplier",
        subcategory="DamageMultiplier",
        name="Stat gate — damage boosted (1->1.5)",
        summary=f"Verify test_damage_boost({DAMAGE_BOOST_PARAM}) sets beam damage to {BOOSTED_DAMAGE}; weapon fires and hits",
        conditions=[
            f"Attacker: {BOOST_SHIP} (test_beam_med_acc_1dmg + test_damage_boost({DAMAGE_BOOST_PARAM}), dmg {BASE_DAMAGE}->{BOOSTED_DAMAGE})",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px (point-blank)",
        ],
        edge_cases=["Multiplicative modifier on damage attribute"],
        expected_outcome=f"beam.damage == {BOOSTED_DAMAGE}, substantial damage dealt",
        pass_criteria=f"damage == {BOOSTED_DAMAGE} AND damage_dealt > 10",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "damage_mult", "stat_gate"],
    )

    attacker_ship = BOOST_SHIP
    target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        self.actual_damage = beam.damage if beam else None

    def _collect_extra_results(self, outcome, telemetry=None):
        self.results['expected_damage'] = BOOSTED_DAMAGE
        self.results['actual_damage'] = self.actual_damage

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks

        # Data: damage modifier applied
        checks.append(check_approx(
            "Boosted Beam Damage", BOOSTED_DAMAGE,
            self.actual_damage or 0.0, tolerance=0.001, phase="data",
        ))

        # Outcome: substantial damage dealt (not just "damage > 0")
        checks.append(check_true(
            "Substantial Damage Dealt", self.damage_dealt > 10,
            detail=f"damage={self.damage_dealt}", phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-DMG-002: Damage Ratio — 1.5x Boost
# =============================================================================

class ModDmg002_BoostRatioScenario(ComparisonScenario):
    """
    MOD-DMG-002: Prove 1.5x damage boost produces exactly 1.5x total damage.

    Both ships fire at the same rate (reload=0) and have the same accuracy.
    The ONLY difference is damage per hit (1.0 vs 1.5). So the total damage
    ratio should be exactly 1.5x, independent of how many hits occurred.
    """
    metadata = TestMetadata(
        test_id="MOD-DMG-002",
        category="DamageMultiplier",
        subcategory="DamageMultiplier",
        name="Damage ratio — 1.5x boost produces 1.5x total damage",
        summary=f"Baseline (dmg={BASE_DAMAGE}) vs boosted (dmg={BOOSTED_DAMAGE}) at point-blank; ratio ≈ {DAMAGE_BOOST_PARAM}x",
        conditions=[
            f"Baseline: {BASELINE_SHIP} (test_beam_med_acc_1dmg, no modifier, dmg={BASE_DAMAGE})",
            f"Variant: {BOOST_SHIP} (test_beam_med_acc_1dmg + test_damage_boost({DAMAGE_BOOST_PARAM}), dmg={BOOSTED_DAMAGE})",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px (point-blank)",
            f"Same seed, same hit rate → damage ratio = damage_per_hit ratio = {DAMAGE_BOOST_PARAM}x",
        ],
        edge_cases=[
            "Damage ratio is deterministic (same hits, scaled damage)",
            "Both ships use reload=0 (fire every tick) with identical accuracy",
        ],
        expected_outcome=f"Damage ratio ≈ {DAMAGE_BOOST_PARAM}x",
        pass_criteria=f"ratio within ±{RATIO_TOLERANCE} of {DAMAGE_BOOST_PARAM}",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "damage_mult", "ratio", "behavioral"],
    )

    baseline_attacker_ship = BASELINE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = BOOST_SHIP
    variant_target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
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

        # Outcome: damage ratio matches modifier value
        if self.baseline_damage_dealt > 0:
            ratio = self.variant_damage_dealt / self.baseline_damage_dealt
            checks.append(check_approx(
                f"Damage Ratio ≈ {DAMAGE_BOOST_PARAM}x", DAMAGE_BOOST_PARAM,
                ratio, tolerance=RATIO_TOLERANCE, phase="outcome",
            ))

        return checks


# =============================================================================
# MOD-DMG-003: Extreme Ratio — 10x vs 1x
# =============================================================================

class ModDmg003_ExtremeRatioScenario(ComparisonScenario):
    """
    MOD-DMG-003: Prove 10.0x vs 1.0x produces exactly 10.0x total damage.

    Tests linearity at extremes. Both beams have identical hit rates;
    damage ratio should precisely match the multiplier ratio.
    """
    metadata = TestMetadata(
        test_id="MOD-DMG-003",
        category="DamageMultiplier",
        subcategory="DamageMultiplier",
        name="Extreme ratio — 10.0x vs 1.0x = 10.0x damage ratio",
        summary=f"Identity (dmg={IDENTITY_DAMAGE}) vs max (dmg={MAX_DAMAGE}); ratio ≈ 10.0x",
        conditions=[
            f"Baseline: {IDENTITY_SHIP} (test_beam_med_acc_1dmg + test_damage_boost(1.0), dmg={IDENTITY_DAMAGE})",
            f"Variant: {MAX_SHIP} (test_beam_med_acc_1dmg + test_damage_boost(10.0), dmg={MAX_DAMAGE})",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px (point-blank)",
        ],
        edge_cases=["Tests linearity at modifier max value"],
        expected_outcome="Damage ratio ≈ 10.0x",
        pass_criteria="ratio within ±0.5 of 10.0",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "damage_mult", "extreme", "behavioral"],
    )

    baseline_attacker_ship = IDENTITY_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = MAX_SHIP
    variant_target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Precondition: both dealt damage
        checks.append(check_true(
            "Baseline Dealt Damage", self.baseline_damage_dealt > 10,
            detail=f"damage={self.baseline_damage_dealt}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Dealt Damage", self.variant_damage_dealt > 10,
            detail=f"damage={self.variant_damage_dealt}", phase="precondition",
        ))

        # Outcome: damage ratio ≈ 10.0x
        expected_ratio = MAX_DAMAGE / IDENTITY_DAMAGE  # 10.0
        if self.baseline_damage_dealt > 0:
            ratio = self.variant_damage_dealt / self.baseline_damage_dealt
            checks.append(check_approx(
                "Damage Ratio ≈ 10.0x", expected_ratio,
                ratio, tolerance=0.5, phase="outcome",
            ))

        return checks


# =============================================================================
# MOD-DMG-004: Negative Penalty — 0.5x Damage
# =============================================================================

class ModDmg004_PenaltyScenario(ComparisonScenario):
    """
    MOD-DMG-004: Prove damage penalty reduces total damage by half.

    Baseline (dmg=1.0) vs penalized (dmg=0.5). Same hit rate, half the
    damage per hit → total damage ratio ≈ 0.5x. Tests modifier bidirectionality.
    """
    metadata = TestMetadata(
        test_id="MOD-DMG-004",
        category="DamageMultiplier",
        subcategory="DamageMultiplier",
        name="Negative penalty — 0.5x damage halves total damage",
        summary=f"Baseline (dmg={BASE_DAMAGE}) vs penalized (dmg={PENALIZED_DAMAGE}); ratio ≈ {PENALTY_PARAM}x",
        conditions=[
            f"Baseline: {BASELINE_SHIP} (test_beam_med_acc_1dmg, no modifier, dmg={BASE_DAMAGE})",
            f"Variant: {PENALTY_SHIP} (test_beam_med_acc_1dmg + test_damage_penalty({PENALTY_PARAM}), dmg={PENALIZED_DAMAGE})",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px (point-blank)",
        ],
        edge_cases=[
            "Penalty modifier uses damage_mult with value < 1.0",
            "Tests bidirectionality: modifier works for reduction, not just boost",
        ],
        expected_outcome=f"Penalized damage ≈ {PENALTY_PARAM}x of baseline",
        pass_criteria=f"ratio within ±{RATIO_TOLERANCE} of {PENALTY_PARAM}",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "damage_mult", "penalty", "behavioral"],
    )

    baseline_attacker_ship = BASELINE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = PENALTY_SHIP
    variant_target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Data: verify penalty applied
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            checks.append(check_approx(
                "Penalized Beam Damage", PENALIZED_DAMAGE,
                beam.damage, tolerance=0.001, phase="data",
            ))

        # Precondition: both dealt damage
        checks.append(check_true(
            "Baseline Dealt Damage", self.baseline_damage_dealt > 10,
            detail=f"damage={self.baseline_damage_dealt}", phase="precondition",
        ))
        checks.append(check_true(
            "Penalized Dealt Damage", self.variant_damage_dealt > 5,
            detail=f"damage={self.variant_damage_dealt}", phase="precondition",
        ))

        # Outcome: damage ratio ≈ 0.5x (penalty halves damage)
        if self.baseline_damage_dealt > 0:
            ratio = self.variant_damage_dealt / self.baseline_damage_dealt
            checks.append(check_approx(
                f"Damage Ratio ≈ {PENALTY_PARAM}x", PENALTY_PARAM,
                ratio, tolerance=RATIO_TOLERANCE, phase="outcome",
            ))

        # Outcome: penalty deals LESS damage
        checks.append(check_true(
            "Penalty Reduces Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=(
                f"baseline={self.baseline_damage_dealt}, "
                f"penalized={self.variant_damage_dealt}"
            ),
            phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-DMG-005: Range-Independent — Ratio Holds at Mid-Range
# =============================================================================

class ModDmg005_RangeIndependentScenario(ComparisonScenario):
    """
    MOD-DMG-005: Prove damage ratio is range-independent.

    At mid-range (400px), both beams have lower hit rates than at point-blank
    (same accuracy penalty from distance). But the RATIO of total damage
    should still be ~1.5x because damage per hit is the only difference.

    This distinguishes damage_mult from accuracy_add — accuracy affects the
    sigmoid curve differently at different ranges, but damage_mult scales
    linearly regardless of range.
    """
    metadata = TestMetadata(
        test_id="MOD-DMG-005",
        category="DamageMultiplier",
        subcategory="DamageMultiplier",
        name=f"Range-independent — ratio holds at {MID_RANGE_DISTANCE}px",
        summary=(
            f"Damage ratio ≈ {DAMAGE_BOOST_PARAM}x at mid-range ({MID_RANGE_DISTANCE}px), "
            f"proving damage_mult is range-independent"
        ),
        conditions=[
            f"Baseline: {BASELINE_SHIP} (test_beam_med_acc_1dmg, no modifier, dmg={BASE_DAMAGE})",
            f"Variant: {BOOST_SHIP} (test_beam_med_acc_1dmg + test_damage_boost({DAMAGE_BOOST_PARAM}), dmg={BOOSTED_DAMAGE})",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {MID_RANGE_DISTANCE}px (mid-range, reduced hit rate but same ratio)",
        ],
        edge_cases=[
            "At mid-range, fewer hits occur but ratio is unchanged",
            "Distinguishes damage_mult from accuracy_add (which IS range-dependent)",
        ],
        expected_outcome=f"Damage ratio ≈ {DAMAGE_BOOST_PARAM}x even at mid-range",
        pass_criteria=f"ratio within ±{RATIO_TOLERANCE} of {DAMAGE_BOOST_PARAM}",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "damage_mult", "range_independent", "behavioral"],
    )

    baseline_attacker_ship = BASELINE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = BOOST_SHIP
    variant_target_ship = TARGET_SHIP
    distance = MID_RANGE_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Precondition: both dealt substantial damage at mid-range
        checks.append(check_true(
            "Baseline Dealt Damage at Range", self.baseline_damage_dealt > 10,
            detail=f"damage={self.baseline_damage_dealt}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Dealt Damage at Range", self.variant_damage_dealt > 10,
            detail=f"damage={self.variant_damage_dealt}", phase="precondition",
        ))

        # Outcome: ratio still matches modifier value at mid-range
        if self.baseline_damage_dealt > 0:
            ratio = self.variant_damage_dealt / self.baseline_damage_dealt
            checks.append(check_approx(
                f"Mid-Range Damage Ratio ≈ {DAMAGE_BOOST_PARAM}x",
                DAMAGE_BOOST_PARAM,
                ratio, tolerance=RATIO_TOLERANCE, phase="outcome",
            ))

        return checks
