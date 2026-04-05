"""
Accuracy Additive Modifier Scenarios (MOD-ACC-001 through MOD-ACC-004)

Dedicated test scenarios for the accuracy_add modifier (test_accuracy_boost).
Uses StaticTargetScenario for stat validation and ComparisonScenario for
A/B combat outcome comparisons.

Modifier formula: accuracy_add = param * 0.5 (operation: add)
Base component: test_beam_med_acc_1dmg (base_accuracy=2.0)

Test Coverage:
- MOD-ACC-001: Accuracy boost applied (param=2 -> +1.0 -> total 3.0)
- MOD-ACC-002: Baseline without modifier (accuracy stays at 2.0)
- MOD-ACC-003: Accuracy boost formula math verification (data-only)
- MOD-ACC-004: Comparison — boosted accuracy vs baseline at mid-range
"""

from simulation_tests.scenarios.base import TestMetadata
from simulation_tests.scenarios.templates import StaticTargetScenario, ComparisonScenario
from simulation_tests.scenarios.validation import check_exact, check_approx, check_true
from simulation_tests.test_constants import (
    STANDARD_SEED,
    POINT_BLANK_DISTANCE,
    MID_RANGE_DISTANCE,
    MODIFIER_TEST_TICKS,
    MOD_BASE_BEAM_ACCURACY,
)

# Ship filenames
ACC_BOOST_ATTACKER_SHIP = "Test_Attacker_Beam_AccBoost.json"
BASELINE_BEAM_SHIP = "Test_Attacker_Beam360_Med.json"
STATIONARY_TARGET = "Test_Target_Stationary.json"

# Modifier parameters
ACC_BOOST_PARAM = 2           # value field in ship JSON modifier
ACC_BOOST_FORMULA_FACTOR = 0.5  # from modifiers.json: param * 0.5
ACC_BOOST_ADDEND = ACC_BOOST_PARAM * ACC_BOOST_FORMULA_FACTOR  # 1.0

# Expected accuracy values
ACC_EXPECTED_BOOSTED = MOD_BASE_BEAM_ACCURACY + ACC_BOOST_ADDEND  # 2.0 + 1.0 = 3.0
ACC_EXPECTED_BASELINE = MOD_BASE_BEAM_ACCURACY                     # 2.0


# ============================================================================
# MOD-ACC-001: Accuracy Boost Applied (param=2 -> +1.0 -> total 3.0)
# ============================================================================

class ModAcc001_AccuracyBoostAppliedScenario(StaticTargetScenario):
    """
    MOD-ACC-001: Verify test_accuracy_boost(2) adds 1.0 to base_accuracy.

    Setup: Medium accuracy beam with accuracy_add modifier (param=2) at
    point-blank vs stationary target.
    Data check: beam.base_accuracy == 3.0 (2.0 + 2*0.5)
    Outcome check: damage_dealt > 0 (weapon fires and hits)
    """
    metadata = TestMetadata(
        test_id="MOD-ACC-001",
        category="AccuracyAdditive",
        subcategory="Basic Effect",
        name="Accuracy boost applied (param=2)",
        summary="Verify test_accuracy_boost(2) adds 1.0 to base_accuracy (2.0 -> 3.0)",
        conditions=[
            f"Base beam accuracy: {MOD_BASE_BEAM_ACCURACY}",
            f"Modifier param: {ACC_BOOST_PARAM} (formula: param * {ACC_BOOST_FORMULA_FACTOR})",
            f"Expected addend: {ACC_BOOST_ADDEND}",
            f"Expected modified accuracy: {ACC_EXPECTED_BOOSTED}",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
        ],
        edge_cases=["Additive modifier uses add operation, not multiply"],
        expected_outcome=f"beam.base_accuracy == {ACC_EXPECTED_BOOSTED}, damage dealt to target",
        pass_criteria=f"beam.base_accuracy == {ACC_EXPECTED_BOOSTED} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "accuracy_add"],
    )

    attacker_ship = ACC_BOOST_ATTACKER_SHIP
    target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_beam_accuracy = beam.base_accuracy
        else:
            self.actual_beam_accuracy = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_accuracy'] = MOD_BASE_BEAM_ACCURACY
        self.results['modifier_param'] = ACC_BOOST_PARAM
        self.results['expected_accuracy'] = ACC_EXPECTED_BOOSTED
        self.results['actual_accuracy'] = self.actual_beam_accuracy

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: beam weapon loaded
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true(
            "Beam Weapon Loaded", beam is not None, phase="precondition",
        ))
        if beam is None:
            return checks

        # Data: verify modified accuracy value
        checks.append(check_approx(
            "Modified Beam Accuracy", ACC_EXPECTED_BOOSTED,
            self.actual_beam_accuracy or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Outcome: damage was dealt
        checks.append(check_true(
            "Damage Dealt", self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-ACC-002: Baseline Without Modifier (accuracy stays at 2.0)
# ============================================================================

class ModAcc002_BaselineNoModifierScenario(StaticTargetScenario):
    """
    MOD-ACC-002: Verify unmodified beam has base_accuracy == 2.0.

    Setup: Medium accuracy beam with no modifier at point-blank vs
    stationary target.
    Data check: beam.base_accuracy == 2.0 (identity baseline)
    Outcome check: damage_dealt > 0 (weapon fires and hits)

    This establishes the identity baseline to prove MOD-ACC-001 actually
    changes the accuracy value (not that 3.0 was the base all along).
    """
    metadata = TestMetadata(
        test_id="MOD-ACC-002",
        category="AccuracyAdditive",
        subcategory="Boundary",
        name="Baseline without modifier (identity)",
        summary="Verify unmodified beam retains base_accuracy of 2.0",
        conditions=[
            f"Base beam accuracy: {MOD_BASE_BEAM_ACCURACY}",
            "No modifier applied",
            f"Expected accuracy: {ACC_EXPECTED_BASELINE} (unchanged)",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
        ],
        edge_cases=["Absence of modifier must not alter base_accuracy"],
        expected_outcome=f"beam.base_accuracy == {ACC_EXPECTED_BASELINE}, damage dealt to target",
        pass_criteria=f"beam.base_accuracy == {ACC_EXPECTED_BASELINE} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "accuracy_add", "baseline"],
    )

    attacker_ship = BASELINE_BEAM_SHIP
    target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_beam_accuracy = beam.base_accuracy
        else:
            self.actual_beam_accuracy = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_accuracy'] = MOD_BASE_BEAM_ACCURACY
        self.results['expected_accuracy'] = ACC_EXPECTED_BASELINE
        self.results['actual_accuracy'] = self.actual_beam_accuracy

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: beam weapon loaded
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true(
            "Beam Weapon Loaded", beam is not None, phase="precondition",
        ))
        if beam is None:
            return checks

        # Data: verify unmodified accuracy value
        checks.append(check_approx(
            "Unmodified Beam Accuracy", ACC_EXPECTED_BASELINE,
            self.actual_beam_accuracy or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Outcome: damage was dealt
        checks.append(check_true(
            "Damage Dealt", self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-ACC-003: Accuracy Boost Formula Math Verification
# ============================================================================

class ModAcc003_FormulaVerificationScenario(StaticTargetScenario):
    """
    MOD-ACC-003: Verify the additive formula math in detail.

    Setup: Beam with accuracy_add modifier (param=2) at point-blank.
    Data checks:
    - Base accuracy (before modifier): 2.0
    - Modifier addend: param(2) * 0.5 = 1.0
    - Final accuracy: 2.0 + 1.0 = 3.0
    - Addend equals expected value exactly

    This test focuses on the formula decomposition to catch bugs where
    the formula factor, param value, or add operation is wrong.
    """
    metadata = TestMetadata(
        test_id="MOD-ACC-003",
        category="AccuracyAdditive",
        subcategory="Basic Effect",
        name="Additive formula math verification",
        summary=(
            f"Verify formula: base({MOD_BASE_BEAM_ACCURACY}) + "
            f"param({ACC_BOOST_PARAM}) * {ACC_BOOST_FORMULA_FACTOR} = {ACC_EXPECTED_BOOSTED}"
        ),
        conditions=[
            f"Base beam accuracy: {MOD_BASE_BEAM_ACCURACY}",
            f"Modifier param: {ACC_BOOST_PARAM}",
            f"Formula factor: {ACC_BOOST_FORMULA_FACTOR}",
            f"Expected addend: {ACC_BOOST_ADDEND}",
            f"Expected final accuracy: {ACC_EXPECTED_BOOSTED}",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
        ],
        edge_cases=[
            "Addend must equal param * formula_factor exactly",
            "Final accuracy must equal base + addend exactly",
            "Operation is 'add', not 'multiply'",
        ],
        expected_outcome=(
            f"base_accuracy == {ACC_EXPECTED_BOOSTED}, "
            f"addend == {ACC_BOOST_ADDEND}"
        ),
        pass_criteria=(
            f"base_accuracy == {ACC_EXPECTED_BOOSTED} AND "
            f"addend == {ACC_BOOST_ADDEND} AND damage_dealt > 0"
        ),
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "accuracy_add", "formula"],
    )

    attacker_ship = ACC_BOOST_ATTACKER_SHIP
    target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_beam_accuracy = beam.base_accuracy
            self.actual_base_accuracy = beam._base_accuracy
        else:
            self.actual_beam_accuracy = None
            self.actual_base_accuracy = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_accuracy_raw'] = self.actual_base_accuracy
        self.results['accuracy_after_modifier'] = self.actual_beam_accuracy
        self.results['expected_addend'] = ACC_BOOST_ADDEND
        if self.actual_base_accuracy is not None and self.actual_beam_accuracy is not None:
            self.results['actual_addend'] = self.actual_beam_accuracy - self.actual_base_accuracy
        else:
            self.results['actual_addend'] = None

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: beam weapon loaded
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true(
            "Beam Weapon Loaded", beam is not None, phase="precondition",
        ))
        if beam is None:
            return checks

        # Data: verify raw base accuracy (before modifier)
        checks.append(check_approx(
            "Raw Base Accuracy (pre-modifier)", MOD_BASE_BEAM_ACCURACY,
            self.actual_base_accuracy or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Data: verify the addend (modifier contribution)
        actual_addend = self.results.get('actual_addend', 0.0)
        checks.append(check_approx(
            "Modifier Addend (param * factor)", ACC_BOOST_ADDEND,
            actual_addend if actual_addend is not None else 0.0, tolerance=0.001,
            phase="data",
        ))

        # Data: verify final accuracy (base + addend)
        checks.append(check_approx(
            "Final Accuracy (base + addend)", ACC_EXPECTED_BOOSTED,
            self.actual_beam_accuracy or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Outcome: damage was dealt
        checks.append(check_true(
            "Damage Dealt", self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-ACC-004: Boosted Accuracy vs Baseline at Mid-Range
# ============================================================================

class ModAcc004_BoostVsBaselineScenario(ComparisonScenario):
    """
    MOD-ACC-004: Compare combat outcome of accuracy-boosted beam vs baseline.

    Baseline: Medium accuracy beam (base_accuracy=2.0, no modifier).
    Variant: Same beam with test_accuracy_boost(2) (base_accuracy=3.0).
    Both fire at mid-range (400px) against stationary targets.

    Higher accuracy means higher hit rate at range, so the variant should
    deal more total damage. This confirms the additive accuracy modifier
    translates into a measurable combat improvement.
    """
    metadata = TestMetadata(
        test_id="MOD-ACC-004",
        category="AccuracyAdditive",
        subcategory="Combat Outcome",
        name="Boosted accuracy vs baseline at mid-range",
        summary=(
            f"Verify accuracy boost ({ACC_EXPECTED_BASELINE} -> {ACC_EXPECTED_BOOSTED}) "
            f"produces more hits at mid-range ({MID_RANGE_DISTANCE}px)"
        ),
        conditions=[
            f"Baseline: medium-accuracy beam, accuracy={ACC_EXPECTED_BASELINE} (no modifier)",
            f"Variant: same beam with test_accuracy_boost({ACC_BOOST_PARAM}), "
            f"accuracy={ACC_EXPECTED_BOOSTED}",
            f"Distance: {MID_RANGE_DISTANCE} (mid-range, where accuracy matters)",
            f"Duration: {MODIFIER_TEST_TICKS} ticks",
            "Same seed for both battles",
        ],
        edge_cases=[
            "At mid-range, range penalty reduces effective accuracy",
            "Higher base_accuracy overcomes more range penalty -> more hits",
        ],
        expected_outcome="Variant deals more damage than baseline (higher accuracy -> more hits)",
        pass_criteria="variant_damage > baseline_damage",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "accuracy_add", "comparison"],
    )

    baseline_attacker_ship = BASELINE_BEAM_SHIP
    baseline_target_ship = STATIONARY_TARGET
    variant_attacker_ship = ACC_BOOST_ATTACKER_SHIP
    variant_target_ship = STATIONARY_TARGET
    distance = MID_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify variant has boosted accuracy
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true(
            "Variant Beam Weapon Loaded", beam is not None, phase="data",
        ))
        if beam:
            checks.append(check_approx(
                "Variant Beam Accuracy", ACC_EXPECTED_BOOSTED,
                beam.base_accuracy, tolerance=0.001,
                phase="data",
            ))

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

        # Outcome: accuracy boost produces more damage
        checks.append(check_true(
            "Accuracy Boost Increases Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"baseline={self.baseline_damage_dealt}, "
                   f"variant={self.variant_damage_dealt}, "
                   f"delta=+{self.variant_damage_dealt - self.baseline_damage_dealt}",
            phase="outcome",
        ))

        return checks
