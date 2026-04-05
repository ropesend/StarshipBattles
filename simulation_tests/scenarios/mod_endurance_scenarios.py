"""
Endurance Multiplier Modifier Test Scenarios (MOD-ENDUR-001 through MOD-ENDUR-003)

Test scenarios that validate the endurance_mult modifier's effect on seeker weapon
endurance. The test_endurance_boost modifier multiplies endurance with formula param.
Base component test_seeker_slow has endurance=10.0 seconds.

Test Coverage:
- MOD-ENDUR-001: Endurance boost value=2 (2x) — seeker.endurance == 20.0, damage dealt
- MOD-ENDUR-002: Unmodified seeker (identity) — seeker.endurance == 10.0, damage dealt
- MOD-ENDUR-003: Comparison: unmodified vs boosted at point blank — both deal damage,
                 endurance stats differ
"""

from simulation_tests.scenarios.base import TestMetadata
from simulation_tests.scenarios.templates import StaticTargetScenario, ComparisonScenario
from simulation_tests.scenarios.validation import check_approx, check_true
from simulation_tests.test_constants import (
    POINT_BLANK_DISTANCE,
    STANDARD_SEED,
    MODIFIER_TEST_TICKS,
)


# Ship references
ENDURANCE_BOOST_ATTACKER = "Test_Attacker_Seeker_EndurBoost.json"
ENDURANCE_BASE_ATTACKER = "Test_Attacker_Seeker_EndurBase.json"
STATIONARY_TARGET = "Test_Target_Stationary.json"

# Constants
BASE_ENDURANCE = 10.0       # test_seeker_slow base endurance (seconds)
ENDURANCE_BOOST_VALUE = 2   # modifier value=2 → multiplier of 2x
EXPECTED_ENDURANCE = 20.0   # 10.0 * 2 = 20.0


# ============================================================================
# MOD-ENDUR-001: Endurance Boost — seeker.endurance == 20.0
# ============================================================================

class EnduranceBoostScenario(StaticTargetScenario):
    """
    MOD-ENDUR-001: Verify endurance_mult modifier doubles seeker endurance.

    Setup: Seeker with test_endurance_boost(value=2), target at point blank.
    Data check: seeker.endurance == 20.0 (10.0 * 2)
    Outcome check: damage_dealt > 0
    """
    metadata = TestMetadata(
        test_id="MOD-ENDUR-001",
        category="EnduranceMultiplier",
        subcategory="Basic Effect",
        name="Endurance boost 2x — seeker.endurance == 20.0",
        summary="Verify test_endurance_boost(2) doubles seeker endurance to 20.0; target takes damage",
        conditions=[
            f"Base seeker endurance: {BASE_ENDURANCE}s",
            f"Endurance multiplier: {ENDURANCE_BOOST_VALUE}x",
            f"Expected modified endurance: {EXPECTED_ENDURANCE}s",
            f"Target at {POINT_BLANK_DISTANCE}px (point blank)",
        ],
        edge_cases=[],
        expected_outcome=f"Seeker endurance = {EXPECTED_ENDURANCE}, damage is dealt",
        pass_criteria=f"seeker.endurance == {EXPECTED_ENDURANCE} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=30,
        tags=["modifier", "endurance_mult"],
    )

    attacker_ship = ENDURANCE_BOOST_ATTACKER
    target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        seeker = self.get_ability(self.attacker, 'SeekerWeaponAbility')
        if seeker:
            self.actual_endurance = seeker.endurance
        else:
            self.actual_endurance = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_endurance'] = BASE_ENDURANCE
        self.results['expected_endurance'] = EXPECTED_ENDURANCE
        self.results['actual_endurance'] = self.actual_endurance
        self.results['distance'] = self.distance

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: seeker weapon exists
        seeker = self.get_ability(self.attacker, 'SeekerWeaponAbility')
        checks.append(check_true(
            "Seeker Weapon Loaded", seeker is not None, phase="precondition",
        ))
        if seeker is None:
            return checks

        # Precondition: distance is correct
        center_distance = (self.target.position - self.attacker.position).length()
        checks.append(check_approx(
            "Center Distance", float(POINT_BLANK_DISTANCE), center_distance,
            tolerance=0.01, phase="precondition",
        ))

        # Data: seeker endurance is modified correctly
        checks.append(check_approx(
            "Modified Seeker Endurance", EXPECTED_ENDURANCE,
            self.actual_endurance or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Outcome: damage dealt (seeker reaches target at point blank)
        checks.append(check_true(
            "Damage Dealt",
            self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-ENDUR-002: Unmodified Seeker — Identity Check (endurance=10.0)
# ============================================================================

class EnduranceIdentityScenario(StaticTargetScenario):
    """
    MOD-ENDUR-002: Verify unmodified seeker has base endurance of 10.0s.

    Setup: Standard seeker (no modifier) at point blank.
    Data check: seeker.endurance == 10.0 (identity, no modifier applied)
    Outcome check: damage_dealt > 0
    """
    metadata = TestMetadata(
        test_id="MOD-ENDUR-002",
        category="EnduranceMultiplier",
        subcategory="Boundary",
        name="Unmodified seeker — endurance identity (10.0s)",
        summary="Verify unmodified seeker retains base endurance of 10.0s; target takes damage",
        conditions=[
            f"Base seeker endurance: {BASE_ENDURANCE}s",
            "No endurance modifier applied",
            f"Target at {POINT_BLANK_DISTANCE}px (point blank)",
        ],
        edge_cases=["Verifies no modifier at all — pure base value"],
        expected_outcome=f"Seeker endurance = {BASE_ENDURANCE}, damage dealt",
        pass_criteria=f"seeker.endurance == {BASE_ENDURANCE} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=31,
        tags=["modifier", "endurance_mult"],
    )

    attacker_ship = ENDURANCE_BASE_ATTACKER
    target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        seeker = self.get_ability(self.attacker, 'SeekerWeaponAbility')
        if seeker:
            self.actual_endurance = seeker.endurance
        else:
            self.actual_endurance = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_endurance'] = BASE_ENDURANCE
        self.results['actual_endurance'] = self.actual_endurance
        self.results['distance'] = self.distance

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: seeker weapon exists
        seeker = self.get_ability(self.attacker, 'SeekerWeaponAbility')
        checks.append(check_true(
            "Seeker Weapon Loaded", seeker is not None, phase="precondition",
        ))
        if seeker is None:
            return checks

        # Precondition: distance is correct
        center_distance = (self.target.position - self.attacker.position).length()
        checks.append(check_approx(
            "Center Distance", float(POINT_BLANK_DISTANCE), center_distance,
            tolerance=0.01, phase="precondition",
        ))

        # Data: seeker endurance is unmodified (base value)
        checks.append(check_approx(
            "Unmodified Seeker Endurance", BASE_ENDURANCE,
            self.actual_endurance or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Outcome: damage dealt (target at point blank)
        checks.append(check_true(
            "Damage Dealt",
            self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-ENDUR-003: Comparison — Unmodified vs Boosted at Point Blank
# ============================================================================

class EnduranceBoostComparisonScenario(ComparisonScenario):
    """
    MOD-ENDUR-003: Compare unmodified seeker (endurance=10.0s) vs endurance-boosted
    seeker (endurance=20.0s) at point blank.

    Both seekers should reach and damage the target at point blank distance.
    The key validation is that the endurance stat differs between baseline and
    variant, confirming the modifier is applied.

    Baseline: Unmodified seeker (endurance=10.0s) at point blank — deals damage.
    Variant: Endurance-boosted seeker (endurance=20.0s) at point blank — deals damage.
    """
    metadata = TestMetadata(
        test_id="MOD-ENDUR-003",
        category="EnduranceMultiplier",
        subcategory="Combat Outcome",
        name="Comparison: unmodified vs endurance-boosted seeker",
        summary="Both seekers deal damage at point blank; variant has 2x endurance stat",
        conditions=[
            f"Baseline: unmodified seeker (endurance={BASE_ENDURANCE}s) at {POINT_BLANK_DISTANCE}px",
            f"Variant: endurance-boosted seeker (endurance={EXPECTED_ENDURANCE}s) at {POINT_BLANK_DISTANCE}px",
            "Both targets are stationary at point blank range",
        ],
        edge_cases=[],
        expected_outcome="Both deal damage; variant seeker has doubled endurance stat",
        pass_criteria=(
            f"baseline_damage > 0 AND variant_damage > 0 AND "
            f"variant_endurance == {EXPECTED_ENDURANCE} AND "
            f"baseline_endurance == {BASE_ENDURANCE}"
        ),
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=32,
        tags=["modifier", "endurance_mult", "comparison"],
    )

    baseline_attacker_ship = ENDURANCE_BASE_ATTACKER
    baseline_target_ship = STATIONARY_TARGET
    variant_attacker_ship = ENDURANCE_BOOST_ATTACKER
    variant_target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE
    # Both seekers deal damage at point blank — total damage may be similar
    expect_different_damage = False

    def configure_baseline(self, engine):
        """Capture baseline seeker endurance after ship is loaded."""
        seeker = self.get_ability(self.attacker, 'SeekerWeaponAbility')
        self.baseline_endurance = seeker.endurance if seeker else None

    def configure_variant(self, engine):
        """Capture variant seeker endurance after ship is loaded."""
        seeker = self.get_ability(self.attacker, 'SeekerWeaponAbility')
        self.variant_endurance = seeker.endurance if seeker else None

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: baseline endurance is base value
        checks.append(check_approx(
            "Baseline Seeker Endurance", BASE_ENDURANCE,
            self.baseline_endurance or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Data: variant endurance is boosted value
        checks.append(check_approx(
            "Variant Seeker Endurance", EXPECTED_ENDURANCE,
            self.variant_endurance or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Outcome: baseline deals damage (seeker reaches at point blank)
        checks.append(check_true(
            "Baseline Damage Dealt",
            self.baseline_damage_dealt > 0,
            actual=self.baseline_damage_dealt, phase="outcome",
        ))

        # Outcome: variant deals damage (seeker reaches at point blank)
        checks.append(check_true(
            "Variant Damage Dealt",
            self.variant_damage_dealt > 0,
            actual=self.variant_damage_dealt, phase="outcome",
        ))

        return checks
