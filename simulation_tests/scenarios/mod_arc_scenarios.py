"""
Arc Set Modifier Test Scenarios (MOD-ARC-001 through MOD-ARC-005)

Test scenarios that validate the arc_set modifier's effect on beam weapon firing arc.
The test_turret modifier uses arc_set with formula 'param' and operation 'set', which
directly sets the firing arc to the parameter value, overriding the base arc.

Test Coverage:
- MOD-ARC-001: Arc set to 180° — target ahead within arc, damage dealt
- MOD-ARC-002: Unmodified beam (360° arc identity) — damage dealt
- MOD-ARC-003: Arc set to 90° — target ahead within narrow arc, damage dealt
- MOD-ARC-004: Comparison — 360° vs 180° arc, both hit target ahead
- MOD-ARC-005: Set semantics — confirms 'set' overrides base (180, not multiplied)
"""

from simulation_tests.scenarios.base import TestMetadata
from simulation_tests.scenarios.templates import StaticTargetScenario, ComparisonScenario
from simulation_tests.scenarios.validation import check_exact, check_approx, check_true
from simulation_tests.test_constants import (
    STANDARD_SEED,
    MODIFIER_TEST_TICKS,
    TURRET180_ATTACKER_SHIP,
    TURRET_ARC_PARAM,
    MOD_BASE_BEAM_ARC,
    MOD_EXPECTED_ARC,
    POINT_BLANK_DISTANCE,
)


# Ship filenames
UNMODIFIED_BEAM_SHIP = "Test_Attacker_Beam360_Med.json"
ARC90_ATTACKER_SHIP = "Test_Attacker_Beam_Arc90.json"
STATIONARY_TARGET = "Test_Target_Stationary.json"

# Arc90 constants (no test_constants entry for this ship)
ARC90_PARAM = 90


# ============================================================================
# MOD-ARC-001: Arc Set 180° — Target Ahead, Within Arc
# ============================================================================

class ArcSet180InArcScenario(StaticTargetScenario):
    """
    MOD-ARC-001: Verify arc_set modifier sets beam firing arc to 180° and
    target directly ahead is hit.

    Setup: Beam with test_turret(value=180), target at 100px (directly ahead).
    Data check: beam.firing_arc == 180
    Outcome check: damage_dealt > 0
    """
    metadata = TestMetadata(
        test_id="MOD-ARC-001",
        category="ArcSet",
        subcategory="Basic Effect",
        name="Arc set 180° — target ahead (in arc)",
        summary="Verify test_turret(180) sets beam firing arc to 180°; target ahead takes damage",
        conditions=[
            f"Base beam firing arc: {MOD_BASE_BEAM_ARC}°",
            f"Arc set parameter: {TURRET_ARC_PARAM}°",
            f"Expected modified arc: {MOD_EXPECTED_ARC}°",
            f"Target at {POINT_BLANK_DISTANCE}px (directly ahead, within 180° forward arc)",
        ],
        edge_cases=[],
        expected_outcome=f"Beam firing_arc = {MOD_EXPECTED_ARC}, damage is dealt",
        pass_criteria=f"beam.firing_arc == {MOD_EXPECTED_ARC} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=40,
        tags=["modifier", "arc_set"],
    )

    attacker_ship = TURRET180_ATTACKER_SHIP
    target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_firing_arc = beam.firing_arc
        else:
            self.actual_firing_arc = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_arc'] = MOD_BASE_BEAM_ARC
        self.results['expected_firing_arc'] = MOD_EXPECTED_ARC
        self.results['actual_firing_arc'] = self.actual_firing_arc
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
            "Center Distance", float(POINT_BLANK_DISTANCE), center_distance,
            tolerance=0.01, phase="precondition",
        ))

        # Data: firing arc is set to 180°
        checks.append(check_exact(
            "Modified Firing Arc", MOD_EXPECTED_ARC,
            self.actual_firing_arc or 0, phase="data",
        ))

        # Data: base arc was 360° (sanity)
        checks.append(check_exact(
            "Base Beam Arc", MOD_BASE_BEAM_ARC,
            self.results.get('base_arc', 0), phase="data",
        ))

        # Outcome: damage dealt (target ahead, within 180° arc)
        checks.append(check_true(
            "Damage Dealt (Target in Arc)",
            self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-ARC-002: Unmodified Beam — Identity Check (arc=360)
# ============================================================================

class ArcIdentityScenario(StaticTargetScenario):
    """
    MOD-ARC-002: Verify unmodified beam has base firing arc of 360°.

    Setup: Standard beam (no modifier) at 100px distance.
    Data check: beam.firing_arc == 360 (no modifier applied)
    Outcome check: damage_dealt > 0 (target within arc and range)
    """
    metadata = TestMetadata(
        test_id="MOD-ARC-002",
        category="ArcSet",
        subcategory="Boundary",
        name="Unmodified beam — arc identity (360°)",
        summary="Verify unmodified beam retains base firing arc of 360°; target at 100px takes damage",
        conditions=[
            f"Base beam firing arc: {MOD_BASE_BEAM_ARC}°",
            "No arc modifier applied",
            f"Target at {POINT_BLANK_DISTANCE}px (within range and full arc)",
        ],
        edge_cases=["Confirms baseline before testing modifier effects"],
        expected_outcome=f"Beam firing_arc = {MOD_BASE_BEAM_ARC}, damage dealt",
        pass_criteria=f"beam.firing_arc == {MOD_BASE_BEAM_ARC} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=41,
        tags=["modifier", "arc_set"],
    )

    attacker_ship = UNMODIFIED_BEAM_SHIP
    target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_firing_arc = beam.firing_arc
        else:
            self.actual_firing_arc = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_arc'] = MOD_BASE_BEAM_ARC
        self.results['actual_firing_arc'] = self.actual_firing_arc
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
            "Center Distance", float(POINT_BLANK_DISTANCE), center_distance,
            tolerance=0.01, phase="precondition",
        ))

        # Data: firing arc is unmodified (base value)
        checks.append(check_exact(
            "Unmodified Firing Arc", MOD_BASE_BEAM_ARC,
            self.actual_firing_arc or 0, phase="data",
        ))

        # Outcome: damage dealt (target within full arc)
        checks.append(check_true(
            "Damage Dealt at 100px",
            self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-ARC-003: Arc Set 90° — Target Ahead, Within Narrow Arc
# ============================================================================

class ArcSet90InArcScenario(StaticTargetScenario):
    """
    MOD-ARC-003: Verify arc_set modifier sets beam firing arc to 90° and
    target directly ahead is hit.

    Setup: Beam with test_turret(value=90), target at 100px (directly ahead).
    Data check: beam.firing_arc == 90
    Outcome check: damage_dealt > 0
    """
    metadata = TestMetadata(
        test_id="MOD-ARC-003",
        category="ArcSet",
        subcategory="Basic Effect",
        name="Arc set 90° — target ahead (in narrow arc)",
        summary="Verify test_turret(90) sets beam firing arc to 90°; target ahead takes damage",
        conditions=[
            f"Base beam firing arc: {MOD_BASE_BEAM_ARC}°",
            f"Arc set parameter: {ARC90_PARAM}°",
            f"Expected modified arc: {ARC90_PARAM}°",
            f"Target at {POINT_BLANK_DISTANCE}px (directly ahead, within 90° forward arc)",
        ],
        edge_cases=["Narrow arc — target must be within ±45° of ship heading"],
        expected_outcome=f"Beam firing_arc = {ARC90_PARAM}, damage is dealt",
        pass_criteria=f"beam.firing_arc == {ARC90_PARAM} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=42,
        tags=["modifier", "arc_set"],
    )

    attacker_ship = ARC90_ATTACKER_SHIP
    target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_firing_arc = beam.firing_arc
        else:
            self.actual_firing_arc = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_arc'] = MOD_BASE_BEAM_ARC
        self.results['expected_firing_arc'] = ARC90_PARAM
        self.results['actual_firing_arc'] = self.actual_firing_arc
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
            "Center Distance", float(POINT_BLANK_DISTANCE), center_distance,
            tolerance=0.01, phase="precondition",
        ))

        # Data: firing arc is set to 90°
        checks.append(check_exact(
            "Modified Firing Arc", ARC90_PARAM,
            self.actual_firing_arc or 0, phase="data",
        ))

        # Outcome: damage dealt (target ahead, within 90° arc)
        checks.append(check_true(
            "Damage Dealt (Target in Narrow Arc)",
            self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-ARC-004: Comparison — 360° vs 180° Arc (Both Hit Target Ahead)
# ============================================================================

class ArcSetComparisonScenario(ComparisonScenario):
    """
    MOD-ARC-004: Compare unmodified beam (360° arc) vs arc-set beam (180° arc).
    Both should deal damage since target is directly ahead.

    Baseline: Unmodified beam (arc=360) at 100px — target ahead.
    Variant: Arc-set beam (arc=180) at 100px — target ahead.
    Both deal damage; data checks confirm arc values differ.
    """
    metadata = TestMetadata(
        test_id="MOD-ARC-004",
        category="ArcSet",
        subcategory="Combat Outcome",
        name="Comparison: 360° arc vs 180° arc (target ahead)",
        summary="Both unmodified (360°) and arc-set (180°) beams hit target directly ahead; arcs differ",
        conditions=[
            f"Baseline: unmodified beam (arc={MOD_BASE_BEAM_ARC}°) at {POINT_BLANK_DISTANCE}px",
            f"Variant: arc-set beam (arc={MOD_EXPECTED_ARC}°) at {POINT_BLANK_DISTANCE}px",
            "Target directly ahead — within both arcs",
        ],
        edge_cases=[],
        expected_outcome="Both deal damage; variant arc is 180° not 360°",
        pass_criteria="both deal damage AND variant_arc == 180 AND baseline_arc == 360",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=43,
        tags=["modifier", "arc_set", "comparison"],
    )

    baseline_attacker_ship = UNMODIFIED_BEAM_SHIP
    baseline_target_ship = STATIONARY_TARGET
    variant_attacker_ship = TURRET180_ATTACKER_SHIP
    variant_target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE
    expect_different_damage = False

    def configure_baseline(self, engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.results['baseline_firing_arc'] = beam.firing_arc

    def configure_variant(self, engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.results['variant_firing_arc'] = beam.firing_arc

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: baseline arc is 360°
        baseline_arc = self.results.get('baseline_firing_arc', None)
        checks.append(check_exact(
            "Baseline Firing Arc", MOD_BASE_BEAM_ARC,
            baseline_arc or 0, phase="data",
        ))

        # Data: variant arc is 180°
        variant_arc = self.results.get('variant_firing_arc', None)
        checks.append(check_exact(
            "Variant Firing Arc", MOD_EXPECTED_ARC,
            variant_arc or 0, phase="data",
        ))

        # Outcome: baseline deals damage (target ahead, full arc)
        checks.append(check_true(
            "Baseline Damage Dealt",
            self.baseline_damage_dealt > 0,
            actual=self.baseline_damage_dealt, phase="outcome",
        ))

        # Outcome: variant deals damage (target ahead, within 180° arc)
        checks.append(check_true(
            "Variant Damage Dealt",
            self.variant_damage_dealt > 0,
            actual=self.variant_damage_dealt, phase="outcome",
        ))

        # Outcome: both fired shots
        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_true(
            "Baseline Shots Fired", baseline_shots > 0,
            actual=baseline_shots, phase="outcome",
        ))
        checks.append(check_true(
            "Variant Shots Fired", variant_shots > 0,
            actual=variant_shots, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-ARC-005: Set Semantics — Override, Not Multiply
# ============================================================================

class ArcSetSemanticsScenario(StaticTargetScenario):
    """
    MOD-ARC-005: Verify 'set' operation overrides base arc rather than
    multiplying or adding.

    Base arc is 360°. test_turret(180) uses operation='set', so the result
    must be exactly 180° — NOT 360*180, NOT 360+180, NOT 360-180.

    This is a data-level edge case confirming set semantics.
    """
    metadata = TestMetadata(
        test_id="MOD-ARC-005",
        category="ArcSet",
        subcategory="Boundary",
        name="Set semantics — override, not multiply",
        summary="Confirm arc_set 'set' operation overrides base 360° to exactly 180° (not multiplied/added)",
        conditions=[
            f"Base beam firing arc: {MOD_BASE_BEAM_ARC}°",
            f"test_turret(value={TURRET_ARC_PARAM}) with operation='set'",
            "Expected: firing_arc == 180 (direct override)",
            "NOT: 360 * 180 (multiply) or 360 + 180 (add) or 360 - 180 (subtract)",
        ],
        edge_cases=[
            "set operation must produce exactly the parameter value",
            "base value is irrelevant when operation is 'set'",
        ],
        expected_outcome=f"Beam firing_arc = {MOD_EXPECTED_ARC} (exact override)",
        pass_criteria=f"beam.firing_arc == {MOD_EXPECTED_ARC} AND firing_arc != base*param AND damage > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=44,
        tags=["modifier", "arc_set"],
    )

    attacker_ship = TURRET180_ATTACKER_SHIP
    target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_firing_arc = beam.firing_arc
        else:
            self.actual_firing_arc = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_arc'] = MOD_BASE_BEAM_ARC
        self.results['turret_param'] = TURRET_ARC_PARAM
        self.results['expected_firing_arc'] = MOD_EXPECTED_ARC
        self.results['actual_firing_arc'] = self.actual_firing_arc
        # Store values that would result from wrong operations
        self.results['if_multiplied'] = MOD_BASE_BEAM_ARC * TURRET_ARC_PARAM
        self.results['if_added'] = MOD_BASE_BEAM_ARC + TURRET_ARC_PARAM

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: beam weapon exists
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Weapon Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks

        arc = self.actual_firing_arc or 0

        # Data: firing arc is exactly the set parameter value
        checks.append(check_exact(
            "Firing Arc (Set Override)", MOD_EXPECTED_ARC,
            arc, phase="data",
        ))

        # Data: arc is NOT the result of multiplication (360 * 180 = 64800)
        checks.append(check_true(
            "Not Multiplied",
            arc != MOD_BASE_BEAM_ARC * TURRET_ARC_PARAM,
            detail=f"arc={arc}, base*param={MOD_BASE_BEAM_ARC * TURRET_ARC_PARAM}",
            phase="data",
        ))

        # Data: arc is NOT the result of addition (360 + 180 = 540)
        checks.append(check_true(
            "Not Added",
            arc != MOD_BASE_BEAM_ARC + TURRET_ARC_PARAM,
            detail=f"arc={arc}, base+param={MOD_BASE_BEAM_ARC + TURRET_ARC_PARAM}",
            phase="data",
        ))

        # Outcome: damage dealt (target ahead, within 180° arc)
        checks.append(check_true(
            "Damage Dealt (Confirms Weapon Functional)",
            self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks
