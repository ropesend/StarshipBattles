"""
Range Multiplier Modifier Test Scenarios (MOD-RANGE-001 through MOD-RANGE-005)

Test scenarios that validate the range_mult modifier's effect on beam weapon range.
The test_range_boost modifier uses the formula 2^param (exponential), applied to
the base beam range of 800px.

Test Coverage:
- MOD-RANGE-001: Range boost param=1 (2x), target at 1200px (in range) — damage dealt
- MOD-RANGE-002: Unmodified beam (identity), target at 400px — range == 800
- MOD-RANGE-003: Range boost param=1 (2x), target at 900px (beyond base, within modified)
- MOD-RANGE-004: Comparison: unmodified (out of range at 1200) vs boosted (in range at 1200)
- MOD-RANGE-005: Range boost param=1 (2x), target at 1700px (beyond modified range) — no damage
"""

from simulation_tests.scenarios.base import TestMetadata
from simulation_tests.scenarios.templates import StaticTargetScenario, ComparisonScenario
from simulation_tests.scenarios.validation import check_exact, check_approx, check_true
from simulation_tests.test_constants import (
    STANDARD_SEED,
    MODIFIER_TEST_TICKS,
    RANGE_BOOST_ATTACKER_SHIP,
    MOD_BASE_BEAM_RANGE,
    MOD_EXPECTED_RANGE,
    RANGE_BOOST_PARAM,
)


# Unmodified beam ship (no modifiers, range=800)
UNMODIFIED_BEAM_SHIP = "Test_Attacker_Beam360_Med.json"
# Standard stationary target with extreme HP
STATIONARY_TARGET = "Test_Target_Stationary.json"


# ============================================================================
# MOD-RANGE-001: Range Boost — In Range at 1200px
# ============================================================================

class RangeBoostInRangeScenario(StaticTargetScenario):
    """
    MOD-RANGE-001: Verify range_mult modifier doubles beam range and target at
    1200px (beyond base 800, within modified 1600) is hit.

    Setup: Beam with test_range_boost(value=1), target at 1200px.
    Data check: beam.range == 1600
    Outcome check: damage_dealt > 0
    """
    metadata = TestMetadata(
        test_id="MOD-RANGE-001",
        category="RangeMultiplier",
        subcategory="Basic Effect",
        name="Range boost 2x — target at 1200px (in range)",
        summary="Verify test_range_boost(1) doubles beam range to 1600; target at 1200px takes damage",
        conditions=[
            f"Base beam range: {MOD_BASE_BEAM_RANGE}",
            f"Range multiplier: 2^{RANGE_BOOST_PARAM} = 2x",
            f"Expected modified range: {MOD_EXPECTED_RANGE}",
            "Target at 1200px (beyond base 800, within modified 1600)",
        ],
        edge_cases=[],
        expected_outcome=f"Beam range = {MOD_EXPECTED_RANGE}, damage is dealt at 1200px",
        pass_criteria=f"beam.range == {MOD_EXPECTED_RANGE} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=30,
        tags=["modifier", "range_mult"],
    )

    attacker_ship = RANGE_BOOST_ATTACKER_SHIP
    target_ship = STATIONARY_TARGET
    distance = 1200

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_beam_range = beam.range
        else:
            self.actual_beam_range = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_range'] = MOD_BASE_BEAM_RANGE
        self.results['expected_beam_range'] = MOD_EXPECTED_RANGE
        self.results['actual_beam_range'] = self.actual_beam_range
        self.results['distance'] = self.distance

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: beam weapon exists
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Weapon Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks

        # Precondition: distance is correct
        center_distance = (self.target.position - self.attacker.position).length()
        checks.append(check_approx(
            "Center Distance", 1200.0, center_distance,
            tolerance=0.01, phase="precondition",
        ))

        # Data: beam range is modified correctly
        checks.append(check_exact(
            "Base Beam Range", MOD_BASE_BEAM_RANGE,
            self.results.get('base_range', 0), phase="data",
        ))
        checks.append(check_approx(
            "Modified Beam Range", float(MOD_EXPECTED_RANGE),
            self.actual_beam_range or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Outcome: damage dealt (target is within modified range)
        checks.append(check_true(
            "Damage Dealt at 1200px",
            self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-RANGE-002: Unmodified Beam — Identity Check (range=800)
# ============================================================================

class RangeIdentityScenario(StaticTargetScenario):
    """
    MOD-RANGE-002: Verify unmodified beam has base range of 800px.

    Setup: Standard beam (no modifier) at 400px distance.
    Data check: beam.range == 800 (identity, no modifier applied)
    Outcome check: damage_dealt > 0 (target well within range)
    """
    metadata = TestMetadata(
        test_id="MOD-RANGE-002",
        category="RangeMultiplier",
        subcategory="Boundary",
        name="Unmodified beam — range identity (800px)",
        summary="Verify unmodified beam retains base range of 800px; target at 400px takes damage",
        conditions=[
            f"Base beam range: {MOD_BASE_BEAM_RANGE}",
            "No range modifier applied",
            "Target at 400px (well within base range)",
        ],
        edge_cases=["2^0 = 1x would be identity; here we verify no modifier at all"],
        expected_outcome=f"Beam range = {MOD_BASE_BEAM_RANGE}, damage dealt at 400px",
        pass_criteria=f"beam.range == {MOD_BASE_BEAM_RANGE} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=31,
        tags=["modifier", "range_mult"],
    )

    attacker_ship = UNMODIFIED_BEAM_SHIP
    target_ship = STATIONARY_TARGET
    distance = 400

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_beam_range = beam.range
        else:
            self.actual_beam_range = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_range'] = MOD_BASE_BEAM_RANGE
        self.results['actual_beam_range'] = self.actual_beam_range
        self.results['distance'] = self.distance

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: beam weapon exists
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Weapon Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks

        # Precondition: distance is correct
        center_distance = (self.target.position - self.attacker.position).length()
        checks.append(check_approx(
            "Center Distance", 400.0, center_distance,
            tolerance=0.01, phase="precondition",
        ))

        # Data: beam range is unmodified (base value)
        checks.append(check_exact(
            "Unmodified Beam Range", MOD_BASE_BEAM_RANGE,
            self.actual_beam_range or 0, phase="data",
        ))

        # Outcome: damage dealt (target well within range)
        checks.append(check_true(
            "Damage Dealt at 400px",
            self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-RANGE-003: Range Boost — Beyond Base, Within Modified (900px)
# ============================================================================

class RangeBoostBeyondBaseScenario(StaticTargetScenario):
    """
    MOD-RANGE-003: Verify range-boosted beam hits target at 900px (beyond base 800,
    within modified 1600).

    Setup: Beam with test_range_boost(value=1), target at 900px.
    Data check: beam.range == 1600
    Outcome check: damage_dealt > 0
    """
    metadata = TestMetadata(
        test_id="MOD-RANGE-003",
        category="RangeMultiplier",
        subcategory="Basic Effect",
        name="Range boost 2x — target at 900px (beyond base range)",
        summary="Verify range-boosted beam hits at 900px, confirming extended range beyond base 800",
        conditions=[
            f"Base beam range: {MOD_BASE_BEAM_RANGE}",
            f"Modified range: {MOD_EXPECTED_RANGE} (2^{RANGE_BOOST_PARAM} = 2x)",
            "Target at 900px (beyond base 800, within modified 1600)",
        ],
        edge_cases=["900px is just beyond the base 800px cutoff"],
        expected_outcome="Beam hits target at 900px thanks to range modifier",
        pass_criteria=f"beam.range == {MOD_EXPECTED_RANGE} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=32,
        tags=["modifier", "range_mult"],
    )

    attacker_ship = RANGE_BOOST_ATTACKER_SHIP
    target_ship = STATIONARY_TARGET
    distance = 900

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_beam_range = beam.range
        else:
            self.actual_beam_range = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_range'] = MOD_BASE_BEAM_RANGE
        self.results['expected_beam_range'] = MOD_EXPECTED_RANGE
        self.results['actual_beam_range'] = self.actual_beam_range
        self.results['distance'] = self.distance

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: beam weapon exists
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Weapon Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks

        # Precondition: distance is correct
        center_distance = (self.target.position - self.attacker.position).length()
        checks.append(check_approx(
            "Center Distance", 900.0, center_distance,
            tolerance=0.01, phase="precondition",
        ))

        # Data: beam range is modified correctly
        checks.append(check_approx(
            "Modified Beam Range", float(MOD_EXPECTED_RANGE),
            self.actual_beam_range or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Outcome: damage dealt (target within modified range)
        checks.append(check_true(
            "Damage Dealt at 900px",
            self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-RANGE-004: Comparison — Unmodified vs Boosted at 1200px
# ============================================================================

class RangeBoostComparisonScenario(ComparisonScenario):
    """
    MOD-RANGE-004: Compare unmodified beam (out of range at 1200px) vs range-boosted
    beam (in range at 1200px).

    Baseline: Unmodified beam (range=800) at 1200px — expects 0 damage.
    Variant: Range-boosted beam (range=1600) at 1200px — expects > 0 damage.
    """
    metadata = TestMetadata(
        test_id="MOD-RANGE-004",
        category="RangeMultiplier",
        subcategory="Combat Outcome",
        name="Comparison: unmodified vs range-boosted at 1200px",
        summary="Unmodified beam deals 0 damage at 1200px (out of range); boosted beam deals damage",
        conditions=[
            f"Baseline: unmodified beam (range={MOD_BASE_BEAM_RANGE}) at 1200px",
            f"Variant: range-boosted beam (range={MOD_EXPECTED_RANGE}) at 1200px",
            "1200px is beyond base range but within modified range",
        ],
        edge_cases=[],
        expected_outcome="Baseline deals 0 damage, variant deals > 0 damage",
        pass_criteria="baseline_damage_dealt == 0 AND variant_damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=33,
        tags=["modifier", "range_mult", "comparison"],
    )

    baseline_attacker_ship = UNMODIFIED_BEAM_SHIP
    baseline_target_ship = STATIONARY_TARGET
    variant_attacker_ship = RANGE_BOOST_ATTACKER_SHIP
    variant_target_ship = STATIONARY_TARGET
    distance = 1200

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline beam has unmodified range
        baseline_range = self.results.get('base_range', None)
        # We need to read from the variant attacker since baseline ran internally
        # Instead, verify via damage results

        # Outcome: baseline deals 0 damage (out of range)
        checks.append(check_exact(
            "Baseline Damage (Out of Range)", 0,
            self.baseline_damage_dealt, phase="outcome",
        ))

        # Outcome: variant deals > 0 damage (in range)
        checks.append(check_true(
            "Variant Damage Dealt (In Range)",
            self.variant_damage_dealt > 0,
            actual=self.variant_damage_dealt, phase="outcome",
        ))

        # Outcome: baseline fired 0 shots
        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        checks.append(check_exact(
            "Baseline Shots Fired", 0, baseline_shots, phase="outcome",
        ))

        # Outcome: variant fired shots
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_true(
            "Variant Shots Fired",
            variant_shots > 0,
            actual=variant_shots, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-RANGE-005: Range Boost — Out of Range at 1700px
# ============================================================================

class RangeBoostOutOfRangeScenario(StaticTargetScenario):
    """
    MOD-RANGE-005: Verify range-boosted beam cannot hit target at 1700px
    (beyond modified range of 1600).

    Setup: Beam with test_range_boost(value=1), target at 1700px.
    Data check: beam.range == 1600
    Outcome check: damage_dealt == 0, shots_fired == 0
    """
    metadata = TestMetadata(
        test_id="MOD-RANGE-005",
        category="RangeMultiplier",
        subcategory="Boundary",
        name="Range boost 2x — target at 1700px (out of range)",
        summary="Verify range-boosted beam (1600px range) cannot hit target at 1700px",
        conditions=[
            f"Modified range: {MOD_EXPECTED_RANGE} (2^{RANGE_BOOST_PARAM} = 2x)",
            "Target at 1700px (beyond modified range of 1600)",
        ],
        edge_cases=["Target just beyond modified max range"],
        expected_outcome="No damage dealt, no shots fired",
        pass_criteria="damage_dealt == 0 AND shots_fired == 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=34,
        tags=["modifier", "range_mult", "out-of-range"],
    )

    attacker_ship = RANGE_BOOST_ATTACKER_SHIP
    target_ship = STATIONARY_TARGET
    distance = 1700

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_beam_range = beam.range
        else:
            self.actual_beam_range = None

    def _collect_extra_results(self, battle_engine):
        self.results['expected_beam_range'] = MOD_EXPECTED_RANGE
        self.results['actual_beam_range'] = self.actual_beam_range
        self.results['distance'] = self.distance

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: beam weapon exists
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Weapon Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks

        # Precondition: distance is correct
        center_distance = (self.target.position - self.attacker.position).length()
        checks.append(check_approx(
            "Center Distance", 1700.0, center_distance,
            tolerance=0.01, phase="precondition",
        ))

        # Data: beam range is modified but still less than distance
        checks.append(check_approx(
            "Modified Beam Range", float(MOD_EXPECTED_RANGE),
            self.actual_beam_range or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Precondition: verify target is beyond weapon range (surface distance)
        target_radius = 40 * ((self.target.mass / 1000) ** (1 / 3))
        surface_distance = center_distance - target_radius
        checks.append(check_true(
            "Surface Distance Beyond Modified Range",
            surface_distance > (self.actual_beam_range or 0),
            detail=f"surface_distance={surface_distance:.2f}, beam.range={self.actual_beam_range}",
            phase="precondition",
        ))

        # Outcome: no damage dealt
        checks.append(check_exact(
            "Damage Dealt", 0, self.damage_dealt, phase="outcome",
        ))

        # Outcome: no shots fired
        attacker_shots = self.results.get('attacker_total_shots_fired', 0)
        checks.append(check_exact(
            "Shots Fired", 0, attacker_shots, phase="outcome",
        ))
        return checks
