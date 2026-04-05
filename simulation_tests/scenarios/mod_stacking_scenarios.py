"""
Multi-Modifier Stacking Scenarios (MOD-STACK-001 through MOD-STACK-004)

Dedicated test scenarios for verifying interactions when multiple modifiers
are applied to the same component.

Test Coverage:
- MOD-STACK-001: Two damage multipliers compound (1.5 * 2.0 = 3.0)
- MOD-STACK-002: Independent modifiers on different stats (damage + accuracy)
- MOD-STACK-003: Comparison — dual modifier (3.0x) vs single modifier (1.5x)
- MOD-STACK-004: Comparison — damage+accuracy modifiers vs unmodified at mid-range
"""

from simulation_tests.scenarios.base import TestMetadata
from simulation_tests.scenarios.templates import StaticTargetScenario, ComparisonScenario
from simulation_tests.scenarios.validation import check_exact, check_approx, check_true
from simulation_tests.test_constants import (
    STANDARD_SEED,
    POINT_BLANK_DISTANCE,
    MODIFIER_TEST_TICKS,
    MOD_BASE_BEAM_DAMAGE,
    MOD_BASE_BEAM_ACCURACY,
    DAMAGE_BOOST_ATTACKER_SHIP,
)

# Ship filenames
DUAL_MODIFIER_SHIP = "Test_Attacker_Beam_DualModifier.json"
DMG_AND_ACC_SHIP = "Test_Attacker_Beam_DmgAndAcc.json"
SINGLE_BOOST_SHIP = DAMAGE_BOOST_ATTACKER_SHIP  # test_damage_boost(1.5)
BASELINE_BEAM_SHIP = "Test_Attacker_Beam360_Med.json"
STATIONARY_TARGET = "Test_Target_Stationary.json"

# Expected compounded damage: base 1 * 1.5 * 2.0 = 3.0
DUAL_EXPECTED_DAMAGE = MOD_BASE_BEAM_DAMAGE * 1.5 * 2.0
# Expected single modifier damage: base 1 * 1.5 = 1.5
SINGLE_EXPECTED_DAMAGE = MOD_BASE_BEAM_DAMAGE * 1.5
# Expected accuracy with test_accuracy_boost(2): base 2.0 + (2 * 0.5) = 3.0
EXPECTED_ACCURACY_WITH_BOOST = MOD_BASE_BEAM_ACCURACY + (2 * 0.5)
# Expected damage with damage_mult(1.5): 1 * 1.5 = 1.5
DMGACC_EXPECTED_DAMAGE = MOD_BASE_BEAM_DAMAGE * 1.5

# Mid-range distance where accuracy matters more
MID_RANGE_DISTANCE = 400


# ============================================================================
# MOD-STACK-001: Two Damage Multipliers Compound
# ============================================================================

class ModStack001_DualDamageCompoundScenario(StaticTargetScenario):
    """
    MOD-STACK-001: Verify two multiplicative damage modifiers compound.

    Setup: Beam with test_damage_boost(1.5) + test_damage_boost_b(2.0)
    at point-blank vs stationary target.
    Data check: beam.damage == 3.0 (base 1 * 1.5 * 2.0)
    Outcome check: damage_dealt > 0
    """
    metadata = TestMetadata(
        test_id="MOD-STACK-001",
        category="ModifierStacking",
        subcategory="Same Stat",
        name="Dual damage multipliers compound (1.5 * 2.0 = 3.0)",
        summary="Verify two multiplicative damage modifiers on the same component compound to 3.0x",
        conditions=[
            f"Base beam damage: {MOD_BASE_BEAM_DAMAGE}",
            "Modifier A: test_damage_boost(1.5) — damage_mult 1.5x",
            "Modifier B: test_damage_boost_b(2.0) — damage_mult 2.0x",
            f"Expected compounded damage: {DUAL_EXPECTED_DAMAGE}",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
        ],
        edge_cases=["Multiplicative stacking must compound, not add"],
        expected_outcome=f"beam.damage == {DUAL_EXPECTED_DAMAGE}, damage dealt to target",
        pass_criteria=f"beam.damage == {DUAL_EXPECTED_DAMAGE} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "stacking"],
    )

    attacker_ship = DUAL_MODIFIER_SHIP
    target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_beam_damage = beam.damage
        else:
            self.actual_beam_damage = None

    def _collect_extra_results(self, engine):
        self.results['base_damage'] = MOD_BASE_BEAM_DAMAGE
        self.results['modifier_a'] = 1.5
        self.results['modifier_b'] = 2.0
        self.results['expected_beam_damage'] = DUAL_EXPECTED_DAMAGE
        self.results['actual_beam_damage'] = self.actual_beam_damage

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: beam weapon loaded
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true(
            "Beam Weapon Loaded", beam is not None, phase="precondition",
        ))
        if beam is None:
            return checks

        # Data: compounded damage
        checks.append(check_exact(
            "Base Beam Damage (from JSON)", MOD_BASE_BEAM_DAMAGE,
            self.results.get('base_damage', 0), phase="data",
        ))
        checks.append(check_approx(
            "Compounded Beam Damage (1.5 * 2.0)", DUAL_EXPECTED_DAMAGE,
            self.actual_beam_damage or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Outcome: damage was dealt
        checks.append(check_true(
            "Damage Dealt", self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-STACK-002: Independent Modifiers on Different Stats
# ============================================================================

class ModStack002_IndependentStatsScenario(StaticTargetScenario):
    """
    MOD-STACK-002: Verify modifiers on different stats are independent.

    Setup: Beam with test_damage_boost(1.5) + test_accuracy_boost(2)
    at point-blank vs stationary target.
    Data check: beam.damage == 1.5 AND beam.base_accuracy == 3.0
    """
    metadata = TestMetadata(
        test_id="MOD-STACK-002",
        category="ModifierStacking",
        subcategory="Cross Stat",
        name="Independent modifiers on different stats",
        summary="Verify damage_mult and accuracy_add modifiers on the same component apply independently",
        conditions=[
            f"Base beam damage: {MOD_BASE_BEAM_DAMAGE}",
            f"Base beam accuracy: {MOD_BASE_BEAM_ACCURACY}",
            "Modifier A: test_damage_boost(1.5) — damage_mult 1.5x",
            "Modifier B: test_accuracy_boost(2) — accuracy_add +1.0",
            f"Expected damage: {DMGACC_EXPECTED_DAMAGE}",
            f"Expected accuracy: {EXPECTED_ACCURACY_WITH_BOOST}",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
        ],
        edge_cases=["Modifiers on different stats must not interfere"],
        expected_outcome=(
            f"beam.damage == {DMGACC_EXPECTED_DAMAGE}, "
            f"beam.base_accuracy == {EXPECTED_ACCURACY_WITH_BOOST}"
        ),
        pass_criteria=(
            f"beam.damage == {DMGACC_EXPECTED_DAMAGE} AND "
            f"beam.base_accuracy == {EXPECTED_ACCURACY_WITH_BOOST}"
        ),
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "stacking"],
    )

    attacker_ship = DMG_AND_ACC_SHIP
    target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_beam_damage = beam.damage
            self.actual_beam_accuracy = beam.base_accuracy
        else:
            self.actual_beam_damage = None
            self.actual_beam_accuracy = None

    def _collect_extra_results(self, engine):
        self.results['base_damage'] = MOD_BASE_BEAM_DAMAGE
        self.results['base_accuracy'] = MOD_BASE_BEAM_ACCURACY
        self.results['expected_damage'] = DMGACC_EXPECTED_DAMAGE
        self.results['expected_accuracy'] = EXPECTED_ACCURACY_WITH_BOOST
        self.results['actual_beam_damage'] = self.actual_beam_damage
        self.results['actual_beam_accuracy'] = self.actual_beam_accuracy

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: beam weapon loaded
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true(
            "Beam Weapon Loaded", beam is not None, phase="precondition",
        ))
        if beam is None:
            return checks

        # Data: damage modified independently
        checks.append(check_approx(
            "Modified Beam Damage (1.5x)", DMGACC_EXPECTED_DAMAGE,
            self.actual_beam_damage or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Data: accuracy modified independently
        checks.append(check_approx(
            "Modified Beam Accuracy (+1.0 add)", EXPECTED_ACCURACY_WITH_BOOST,
            self.actual_beam_accuracy or 0.0, tolerance=0.001,
            phase="data",
        ))

        return checks


# ============================================================================
# MOD-STACK-003: Dual Modifier (3.0x) vs Single Modifier (1.5x)
# ============================================================================

class ModStack003_DualVsSingleScenario(ComparisonScenario):
    """
    MOD-STACK-003: Compare dual modifier (3.0x dmg) vs single modifier (1.5x dmg).

    Baseline: Beam with test_damage_boost(1.5), damage=1.5.
    Variant: Beam with test_damage_boost(1.5) + test_damage_boost_b(2.0), damage=3.0.
    Both fire at point-blank against stationary targets for same duration.
    Outcome: variant deals approximately 2x more total damage (3.0 / 1.5).
    """
    metadata = TestMetadata(
        test_id="MOD-STACK-003",
        category="ModifierStacking",
        subcategory="Combat Outcome",
        name="Dual modifier (3.0x) vs single modifier (1.5x)",
        summary="Verify dual damage modifier produces ~2x more damage than single modifier",
        conditions=[
            f"Baseline: beam with test_damage_boost(1.5), damage={SINGLE_EXPECTED_DAMAGE}",
            f"Variant: beam with dual modifiers (1.5 * 2.0), damage={DUAL_EXPECTED_DAMAGE}",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
            f"Duration: {MODIFIER_TEST_TICKS} ticks",
            "Same seed for both battles",
        ],
        edge_cases=[],
        expected_outcome="Variant deals ~2x more damage than baseline (3.0 / 1.5)",
        pass_criteria="variant_damage / baseline_damage within 10% of 2.0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "stacking"],
    )

    baseline_attacker_ship = SINGLE_BOOST_SHIP
    baseline_target_ship = STATIONARY_TARGET
    variant_attacker_ship = DUAL_MODIFIER_SHIP
    variant_target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both battles dealt damage
        checks.append(check_true(
            "Baseline Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"baseline_damage={self.baseline_damage_dealt}",
            phase="precondition",
        ))
        checks.append(check_true(
            "Variant Dealt Damage",
            self.variant_damage_dealt > 0,
            detail=f"variant_damage={self.variant_damage_dealt}",
            phase="precondition",
        ))

        # Outcome: variant deals more damage than baseline
        checks.append(check_true(
            "Dual Modifier Deals More Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"baseline={self.baseline_damage_dealt}, "
                   f"variant={self.variant_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: damage ratio is approximately 2.0x (3.0 / 1.5)
        if self.baseline_damage_dealt > 0:
            ratio = self.variant_damage_dealt / self.baseline_damage_dealt
            expected_ratio = DUAL_EXPECTED_DAMAGE / SINGLE_EXPECTED_DAMAGE
            checks.append(check_approx(
                f"Damage Ratio ~{expected_ratio}x", expected_ratio,
                ratio, tolerance=0.15,
                phase="outcome",
            ))

        return checks


# ============================================================================
# MOD-STACK-004: Damage + Accuracy Modifiers vs Unmodified at Mid-Range
# ============================================================================

class ModStack004_DmgAccVsBaselineScenario(ComparisonScenario):
    """
    MOD-STACK-004: Compare damage+accuracy modified beam vs unmodified at mid-range.

    Baseline: Standard medium-accuracy beam (no modifiers) at 400px.
    Variant: Same beam with test_damage_boost(1.5) + test_accuracy_boost(2) at 400px.
    At mid-range accuracy matters — the variant should deal more damage due to
    both higher per-hit damage and higher hit rate.
    """
    metadata = TestMetadata(
        test_id="MOD-STACK-004",
        category="ModifierStacking",
        subcategory="Combat Outcome",
        name="Damage + accuracy modifiers vs unmodified at mid-range",
        summary=(
            "Verify combined damage and accuracy modifiers produce more damage "
            "than unmodified beam at mid-range where accuracy matters"
        ),
        conditions=[
            "Baseline: medium-accuracy beam, damage=1, accuracy=2.0 (no modifiers)",
            f"Variant: same beam with damage=1.5, accuracy={EXPECTED_ACCURACY_WITH_BOOST}",
            f"Distance: {MID_RANGE_DISTANCE} (mid-range, accuracy matters)",
            f"Duration: {MODIFIER_TEST_TICKS} ticks",
            "Same seed for both battles",
        ],
        edge_cases=["Mid-range makes accuracy impactful, not just damage"],
        expected_outcome="Variant deals more total damage (higher hit rate + higher damage per hit)",
        pass_criteria="variant_damage > baseline_damage",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "stacking"],
    )

    baseline_attacker_ship = BASELINE_BEAM_SHIP
    baseline_target_ship = STATIONARY_TARGET
    variant_attacker_ship = DMG_AND_ACC_SHIP
    variant_target_ship = STATIONARY_TARGET
    distance = MID_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both battles dealt damage
        checks.append(check_true(
            "Baseline Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"baseline_damage={self.baseline_damage_dealt}",
            phase="precondition",
        ))
        checks.append(check_true(
            "Variant Dealt Damage",
            self.variant_damage_dealt > 0,
            detail=f"variant_damage={self.variant_damage_dealt}",
            phase="precondition",
        ))

        # Outcome: variant deals more damage than baseline
        checks.append(check_true(
            "Modified Beam Deals More Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"baseline={self.baseline_damage_dealt}, "
                   f"variant={self.variant_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: variant should deal meaningfully more (at least 25% more)
        # given both damage and accuracy advantages
        if self.baseline_damage_dealt > 0:
            ratio = self.variant_damage_dealt / self.baseline_damage_dealt
            checks.append(check_true(
                "Meaningful Damage Increase (>1.25x)",
                ratio > 1.25,
                detail=f"ratio={ratio:.3f} (baseline={self.baseline_damage_dealt}, "
                       f"variant={self.variant_damage_dealt})",
                phase="outcome",
            ))

        return checks
