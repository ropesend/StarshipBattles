"""
Reload Multiplier Modifier Test Scenarios (MOD-RELOAD-001 to MOD-RELOAD-004)

These tests validate the reload_mult modifier using a beam weapon with
reload=0.1 (fires once every ~10 ticks).  The test_reload_boost modifier
uses formula 1.0/param, so param=2 yields reload_mult=0.5, halving reload
from 10.0 to 5.0.

Test Coverage:
- MOD-RELOAD-001: Static + dynamic check that reload is halved (boosted ship)
- MOD-RELOAD-002: Identity baseline — no modifier, reload stays at 10.0
- MOD-RELOAD-003: Comparison — variant deals more damage (fires 2x as often)
- MOD-RELOAD-004: Comparison — variant fires roughly 2x more shots
"""

from simulation_tests.scenarios.base import TestMetadata
from simulation_tests.scenarios.templates import StaticTargetScenario, ComparisonScenario
from simulation_tests.scenarios.validation import check_exact, check_approx, check_true
from simulation_tests.test_constants import (
    STANDARD_SEED,
    POINT_BLANK_DISTANCE,
    MODIFIER_TEST_TICKS,
)

# =============================================================================
# CONSTANTS
# =============================================================================

RELOAD_BASE = 0.1           # base reload of test_beam_med_acc_1dmg_reload10 (0.1 seconds = ~10 ticks)
RELOAD_BOOST_PARAM = 2      # test_reload_boost(value=2)
RELOAD_EXPECTED = 0.05      # 0.1 * (1.0 / 2) = 0.05 seconds (~5 ticks)

RELOAD_BOOST_ATTACKER = "Test_Attacker_Beam_ReloadBoost.json"
RELOAD_BASE_ATTACKER = "Test_Attacker_Beam_ReloadBase.json"
RELOAD_TARGET = "Test_Target_Stationary.json"


# =============================================================================
# MOD-RELOAD-001: Reload Halved (Boosted Ship)
# =============================================================================

class ReloadBoostAttributeScenario(StaticTargetScenario):
    """
    MOD-RELOAD-001: Verify test_reload_boost halves beam reload time.

    Setup: Beam with reload=0.1 + test_reload_boost(value=2) at point-blank.
    Static check: beam.reload_time == 5.0
    Dynamic check: damage_dealt > 0 (weapon fires and hits)
    """
    metadata = TestMetadata(
        test_id="MOD-RELOAD-001",
        category="Modifiers",
        subcategory="Reload Multiplier",
        name="Reload halved by modifier (10.0 -> 5.0)",
        summary="Verify test_reload_boost(value=2) halves reload from 10.0 to 5.0",
        conditions=[
            f"Base beam reload: {RELOAD_BASE}",
            f"Reload boost param: {RELOAD_BOOST_PARAM} (reload_mult = 0.5)",
            f"Expected modified reload: {RELOAD_EXPECTED}",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
        ],
        edge_cases=[],
        expected_outcome=f"beam.reload_time == {RELOAD_EXPECTED}, damage_dealt > 0",
        pass_criteria=f"beam.reload_time == {RELOAD_EXPECTED} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=30,
        tags=["modifier", "reload_mult"],
    )

    attacker_ship = RELOAD_BOOST_ATTACKER
    target_ship = RELOAD_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_reload_time = beam.reload_time
        else:
            self.actual_reload_time = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_reload'] = RELOAD_BASE
        self.results['reload_boost_param'] = RELOAD_BOOST_PARAM
        self.results['expected_reload'] = RELOAD_EXPECTED
        self.results['actual_reload_time'] = self.actual_reload_time

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true(
            "Beam Weapon Loaded", beam is not None, phase="precondition",
        ))
        if beam is None:
            return checks

        # Data: reload attribute is correctly halved
        checks.append(check_approx(
            "Modified Reload Time", RELOAD_EXPECTED,
            self.actual_reload_time or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Outcome: weapon fired and dealt damage
        checks.append(check_true(
            "Damage Dealt", self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# =============================================================================
# MOD-RELOAD-002: Identity Baseline (No Modifier)
# =============================================================================

class ReloadBaselineAttributeScenario(StaticTargetScenario):
    """
    MOD-RELOAD-002: Verify unmodified beam keeps reload == 10.0.

    Setup: Beam with reload=0.1 and no modifier at point-blank.
    Static check: beam.reload_time == 10.0
    Dynamic check: damage_dealt > 0 (weapon fires, just slower)
    """
    metadata = TestMetadata(
        test_id="MOD-RELOAD-002",
        category="Modifiers",
        subcategory="Reload Multiplier",
        name="Reload unmodified baseline (10.0)",
        summary="Verify beam reload stays at 10.0 with no modifier applied",
        conditions=[
            f"Base beam reload: {RELOAD_BASE}",
            "No modifier applied",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
        ],
        edge_cases=[],
        expected_outcome=f"beam.reload_time == {RELOAD_BASE}, damage_dealt > 0",
        pass_criteria=f"beam.reload_time == {RELOAD_BASE} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=31,
        tags=["modifier", "reload_mult"],
    )

    attacker_ship = RELOAD_BASE_ATTACKER
    target_ship = RELOAD_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_reload_time = beam.reload_time
        else:
            self.actual_reload_time = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_reload'] = RELOAD_BASE
        self.results['expected_reload'] = RELOAD_BASE
        self.results['actual_reload_time'] = self.actual_reload_time

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true(
            "Beam Weapon Loaded", beam is not None, phase="precondition",
        ))
        if beam is None:
            return checks

        # Data: reload attribute is unchanged
        checks.append(check_approx(
            "Unmodified Reload Time", RELOAD_BASE,
            self.actual_reload_time or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Outcome: weapon fired and dealt damage
        checks.append(check_true(
            "Damage Dealt", self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# =============================================================================
# MOD-RELOAD-003: Boosted Ship Deals More Damage
# =============================================================================

class ReloadBoostMoreDamageScenario(ComparisonScenario):
    """
    MOD-RELOAD-003: Boosted reload fires more often, dealing more damage.

    Baseline: reload=0.1 (no modifier)
    Variant:  reload=0.05  (test_reload_boost, value=2)

    The variant fires ~2x as often over the same duration, so it should
    deal significantly more damage.
    """
    metadata = TestMetadata(
        test_id="MOD-RELOAD-003",
        category="Modifiers",
        subcategory="Reload Multiplier",
        name="Reload boost increases total damage",
        summary="Boosted reload (5.0) deals more damage than base (10.0) over same duration",
        conditions=[
            f"Baseline attacker: {RELOAD_BASE_ATTACKER} (reload={RELOAD_BASE})",
            f"Variant attacker: {RELOAD_BOOST_ATTACKER} (reload={RELOAD_EXPECTED})",
            f"Target: {RELOAD_TARGET} (stationary)",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
        ],
        edge_cases=[],
        expected_outcome="Variant damage > baseline damage",
        pass_criteria="variant_damage_dealt > baseline_damage_dealt",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=32,
        tags=["modifier", "reload_mult"],
    )

    baseline_attacker_ship = RELOAD_BASE_ATTACKER
    baseline_target_ship = RELOAD_TARGET
    variant_attacker_ship = RELOAD_BOOST_ATTACKER
    variant_target_ship = RELOAD_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both battles dealt some damage
        checks.append(check_true(
            "Baseline Dealt Damage", self.baseline_damage_dealt > 0,
            actual=self.baseline_damage_dealt, phase="precondition",
        ))
        checks.append(check_true(
            "Variant Dealt Damage", self.variant_damage_dealt > 0,
            actual=self.variant_damage_dealt, phase="precondition",
        ))

        # Outcome: variant dealt more damage than baseline
        checks.append(check_true(
            "Boosted Reload Deals More Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            actual=f"baseline={self.baseline_damage_dealt}, variant={self.variant_damage_dealt}",
            phase="outcome",
        ))
        return checks


# =============================================================================
# MOD-RELOAD-004: Boosted Ship Fires ~2x More Shots
# =============================================================================

class ReloadBoostMoreShotsScenario(ComparisonScenario):
    """
    MOD-RELOAD-004: Boosted reload fires roughly 2x as many shots.

    Baseline: reload=0.1 (no modifier)
    Variant:  reload=0.05  (test_reload_boost, value=2)

    With halved reload time, the variant should fire approximately twice
    as many shots over the same number of ticks.
    """
    metadata = TestMetadata(
        test_id="MOD-RELOAD-004",
        category="Modifiers",
        subcategory="Reload Multiplier",
        name="Reload boost doubles shot count",
        summary="Boosted reload (5.0) fires ~2x more shots than base (10.0)",
        conditions=[
            f"Baseline attacker: {RELOAD_BASE_ATTACKER} (reload={RELOAD_BASE})",
            f"Variant attacker: {RELOAD_BOOST_ATTACKER} (reload={RELOAD_EXPECTED})",
            f"Target: {RELOAD_TARGET} (stationary)",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
        ],
        edge_cases=[],
        expected_outcome="Variant shots_fired ~2x baseline shots_fired",
        pass_criteria="variant_shots / baseline_shots between 1.5 and 2.5",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=33,
        tags=["modifier", "reload_mult"],
    )

    baseline_attacker_ship = RELOAD_BASE_ATTACKER
    baseline_target_ship = RELOAD_TARGET
    variant_attacker_ship = RELOAD_BOOST_ATTACKER
    variant_target_ship = RELOAD_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)

        # Precondition: both ships fired
        checks.append(check_true(
            "Baseline Fired Shots", baseline_shots > 0,
            actual=baseline_shots, phase="precondition",
        ))
        checks.append(check_true(
            "Variant Fired Shots", variant_shots > 0,
            actual=variant_shots, phase="precondition",
        ))

        # Outcome: variant fires more shots
        checks.append(check_true(
            "Variant Fires More Shots",
            variant_shots > baseline_shots,
            actual=f"baseline={baseline_shots}, variant={variant_shots}",
            phase="outcome",
        ))

        # Outcome: shot ratio is approximately 2x (between 1.5 and 2.5)
        if baseline_shots > 0:
            ratio = variant_shots / baseline_shots
            checks.append(check_approx(
                "Shot Count Ratio (~2x)", 2.0, ratio, tolerance=0.5,
                phase="outcome",
            ))
        else:
            checks.append(check_true(
                "Shot Count Ratio (~2x)", False,
                actual="Cannot compute ratio — baseline fired 0 shots",
                phase="outcome",
            ))

        return checks
