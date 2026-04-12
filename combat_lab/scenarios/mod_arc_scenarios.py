"""
Arc Set Modifier Test Scenarios (MOD-ARC-001 through MOD-ARC-005)

Behavioral simulation tests for the arc_set modifier. The test_turret modifier
uses 'set' operation to directly override the weapon's base firing arc. The arc
is centered on the ship's heading — a 90° arc means ±45° from the direction
the ship faces.

The key behavioral test: a weapon with a restricted arc CANNOT fire at targets
outside that arc. By rotating the attacker to face AWAY from the target (heading
180° while target is at 0°), only omnidirectional (360°) weapons can fire. This
proves the arc actually restricts weapon operation in combat.

Ship positioning:
  - Attacker at (0,0), target at (distance, 0) — target is to the RIGHT
  - Attacker heading 0° → facing target (within any forward arc)
  - Attacker heading 180° → facing AWAY from target (outside narrow arcs)

Ship Files:
- Test_Attacker_Beam_Turret180.json — test_beam_med_acc_1dmg(arc=360)
  + test_turret(param=180), arc 360->180 (set operation)
- Test_Attacker_Beam_Arc90.json — test_beam_med_acc_1dmg(arc=360)
  + test_turret(param=90), arc 360->90 (set operation)
- Test_Attacker_Beam360_Med.json — test_beam_med_acc_1dmg(arc=360),
  no modifier (baseline)
- Test_Target_Stationary.json — test_armor_extreme_hp(1B HP, stationary)

Test Coverage:
- MOD-ARC-001: Stat gate — arc set to 180°, target ahead, weapon fires
- MOD-ARC-002: Forward target — both 360° and 90° hit (target within ±45°)
- MOD-ARC-003: Target outside arc — attacker facing away, 90° arc, 0 damage (behavioral)
- MOD-ARC-004: Arc restriction — 360° hits target behind, 90° does not (binary comparison)
- MOD-ARC-005: Set semantics — 'set' overrides base (180, not 360*180 or 360+180)
"""

from combat_lab.scenarios.base import TestMetadata
from combat_lab.scenarios.templates import StaticTargetScenario, ComparisonScenario
from combat_lab.scenarios.validation import check_exact, check_approx, check_true
from combat_lab.test_constants import (
    STANDARD_SEED,
    MODIFIER_TEST_TICKS,
    TURRET180_ATTACKER_SHIP,
    TURRET_ARC_PARAM,
    MOD_BASE_BEAM_ARC,
    MOD_EXPECTED_ARC,
    POINT_BLANK_DISTANCE,
)

# =============================================================================
# COMMON SHIP REFERENCES
# =============================================================================

# test_beam_med_acc_1dmg(arc=360) + test_turret(param=180), arc->180
TURRET180_SHIP = TURRET180_ATTACKER_SHIP
# test_beam_med_acc_1dmg(arc=360) + test_turret(param=90), arc->90
ARC90_SHIP = "Test_Attacker_Beam_Arc90.json"
# test_beam_med_acc_1dmg(arc=360), no modifier
OMNIDIRECTIONAL_SHIP = "Test_Attacker_Beam360_Med.json"
# test_armor_extreme_hp (1B HP, stationary)
TARGET_SHIP = "Test_Target_Stationary.json"

# =============================================================================
# ARC CONSTANTS
# =============================================================================

BASE_ARC = MOD_BASE_BEAM_ARC        # 360
ARC_180 = MOD_EXPECTED_ARC          # 180
ARC_90 = 90
FACING_FORWARD = 0.0                # heading 0° = facing right (toward target)
FACING_AWAY = 180.0                 # heading 180° = facing left (away from target)
TEST_TICKS = MODIFIER_TEST_TICKS    # 500


# =============================================================================
# MOD-ARC-001: Stat Gate — Arc Set to 180°
# =============================================================================

class ModArc001_StatGateScenario(StaticTargetScenario):
    """
    MOD-ARC-001: Quick sanity — arc modifier applied, target ahead is hit.

    Attacker faces forward (0°), target directly ahead. Arc=180° (±90°).
    Target is at 0° relative to heading → well within arc → weapon fires.
    """
    metadata = TestMetadata(
        test_id="MOD-ARC-001",
        category="ArcSet",
        subcategory="ArcSet",
        name="Stat gate — arc set to 180° (target ahead)",
        summary=f"Verify test_turret({TURRET_ARC_PARAM}) sets arc to {ARC_180}°; target ahead takes damage",
        conditions=[
            f"Attacker: {TURRET180_SHIP} (test_beam_med_acc_1dmg + test_turret(param={TURRET_ARC_PARAM}), arc {BASE_ARC}->{ARC_180})",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px, attacker heading {FACING_FORWARD}° (facing target)",
        ],
        edge_cases=["Set operation overrides base arc"],
        expected_outcome=f"beam.firing_arc == {ARC_180}, damage > 10",
        pass_criteria=f"firing_arc == {ARC_180} AND damage > 10",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "arc_set", "stat_gate"],
    )

    attacker_ship = TURRET180_SHIP
    target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        self.actual_arc = beam.firing_arc if beam else None

    def _collect_extra_results(self, battle_engine):
        self.results['expected_arc'] = ARC_180
        self.results['actual_arc'] = self.actual_arc

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks

        # Data: arc modifier applied
        checks.append(check_exact(
            "Modified Firing Arc", ARC_180,
            self.actual_arc or 0, phase="data",
        ))

        # Outcome: weapon fired and hit
        checks.append(check_true(
            "Substantial Damage Dealt", self.damage_dealt > 10,
            detail=f"damage={self.damage_dealt}", phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-ARC-002: Forward Target — Both 360° and 90° Hit
# =============================================================================

class ModArc002_ForwardTargetScenario(ComparisonScenario):
    """
    MOD-ARC-002: Both omnidirectional and narrow arc hit a forward target.

    Attacker faces forward (0°), target directly ahead. Even a 90° arc
    (±45°) covers 0° → weapon fires. Both deal comparable damage since
    the arc doesn't affect hit chance, only whether the weapon can fire.
    """
    metadata = TestMetadata(
        test_id="MOD-ARC-002",
        category="ArcSet",
        subcategory="ArcSet",
        name="Forward target — 360° and 90° both hit",
        summary="Both omnidirectional (360°) and narrow (90°) arcs hit target directly ahead",
        conditions=[
            f"Baseline: {OMNIDIRECTIONAL_SHIP} (test_beam_med_acc_1dmg, arc={BASE_ARC}°, heading={FACING_FORWARD}°)",
            f"Variant: {ARC90_SHIP} (test_beam_med_acc_1dmg + test_turret({ARC_90}), arc={ARC_90}°, heading={FACING_FORWARD}°)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px, target at 0° from heading (within ±45°)",
        ],
        edge_cases=["Narrow arc still fires at forward targets"],
        expected_outcome="Both deal comparable damage (same hit rate, same damage per hit)",
        pass_criteria="both damage > 10, damage ratio ≈ 1.0",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "arc_set", "forward"],
    )

    baseline_attacker_ship = OMNIDIRECTIONAL_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = ARC90_SHIP
    variant_target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE
    expect_different_damage = False  # Both hit same target at same rate

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify arc values
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            checks.append(check_exact(
                "Variant Arc", ARC_90, beam.firing_arc, phase="data",
            ))

        # Outcome: both dealt substantial damage
        checks.append(check_true(
            "Baseline (360°) Dealt Damage", self.baseline_damage_dealt > 10,
            detail=f"damage={self.baseline_damage_dealt}", phase="outcome",
        ))
        checks.append(check_true(
            "Variant (90°) Dealt Damage", self.variant_damage_dealt > 10,
            detail=f"damage={self.variant_damage_dealt}", phase="outcome",
        ))

        # Outcome: comparable damage (arc doesn't affect hit rate)
        if self.baseline_damage_dealt > 0:
            ratio = self.variant_damage_dealt / self.baseline_damage_dealt
            checks.append(check_approx(
                "Damage Ratio ≈ 1.0 (arc doesn't affect damage)", 1.0,
                ratio, tolerance=0.15, phase="outcome",
            ))

        return checks


# =============================================================================
# MOD-ARC-003: Target Outside Arc — 0 Damage (Behavioral)
# =============================================================================

class ModArc003_TargetOutsideArcScenario(StaticTargetScenario):
    """
    MOD-ARC-003: Weapon with 90° arc CANNOT fire at target behind it.

    Attacker heading 180° (facing LEFT), target at (distance, 0) to the RIGHT.
    Target is at 0° but weapon arc is centered on 180° ± 45° (135° to 225°).
    Target at 0° is 180° away from weapon center → far outside ±45° arc.

    This is the core behavioral test: arc actually prevents the weapon from
    firing, resulting in 0 shots and 0 damage.
    """
    metadata = TestMetadata(
        test_id="MOD-ARC-003",
        category="ArcSet",
        subcategory="ArcSet",
        name="Target outside arc — attacker facing away, 0 damage",
        summary="Attacker facing away (180°) with 90° arc cannot fire at target behind it → 0 damage",
        conditions=[
            f"Attacker: {ARC90_SHIP} (test_beam_med_acc_1dmg + test_turret({ARC_90}), arc={ARC_90}°)",
            f"Attacker heading: {FACING_AWAY}° (facing LEFT, away from target)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, at ({POINT_BLANK_DISTANCE}, 0) = to the RIGHT)",
            f"Angular offset: target at 0°, weapon arc centered on 180° ± 45° → target is 180° outside arc",
        ],
        edge_cases=[
            "This is the critical behavioral test — arc MUST prevent firing",
            "0 shots fired, not just 0 hits (weapon should not attempt to fire)",
        ],
        expected_outcome="0 damage dealt, 0 shots fired",
        pass_criteria="damage_dealt == 0 AND shots_fired == 0",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "arc_set", "outside_arc", "behavioral"],
    )

    attacker_ship = ARC90_SHIP
    target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE
    attacker_angle = FACING_AWAY  # Face LEFT, away from target

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks

        # Data: arc is 90° (narrow)
        checks.append(check_exact(
            "Firing Arc", ARC_90, beam.firing_arc, phase="data",
        ))

        # Precondition: attacker is facing away from target
        checks.append(check_approx(
            "Attacker Heading (away from target)", FACING_AWAY,
            self.attacker.angle, tolerance=1.0, phase="precondition",
        ))

        # Outcome: weapon did NOT fire (target outside arc)
        shots = self.results.get('attacker_total_shots_fired', 0)
        checks.append(check_exact(
            "Zero Shots Fired", 0, shots, phase="outcome",
        ))
        checks.append(check_exact(
            "Zero Damage Dealt", 0.0, float(self.damage_dealt), phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-ARC-004: Arc Restriction — 360° Hits, 90° Does Not (Binary)
# =============================================================================

class ModArc004_ArcRestrictionScenario(ComparisonScenario):
    """
    MOD-ARC-004: Prove arc restriction prevents firing in combat.

    Both ships face AWAY from target (heading 180°). The omnidirectional
    (360°) beam still fires because 360° covers all directions. The narrow
    (90°) beam cannot fire because the target is 180° outside its ±45° arc.

    This is the binary comparison: same target, same distance, same heading —
    the ONLY difference is the arc. One fires, one doesn't.
    """
    metadata = TestMetadata(
        test_id="MOD-ARC-004",
        category="ArcSet",
        subcategory="ArcSet",
        name="Arc restriction — 360° hits behind, 90° does not (binary)",
        summary="Both face away from target. 360° fires (omnidirectional). 90° cannot (target outside ±45°).",
        conditions=[
            f"Baseline: {OMNIDIRECTIONAL_SHIP} (test_beam_med_acc_1dmg, arc={BASE_ARC}°, heading={FACING_AWAY}°)",
            f"Variant: {ARC90_SHIP} (test_beam_med_acc_1dmg + test_turret({ARC_90}), arc={ARC_90}°, heading={FACING_AWAY}°)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, at ({POINT_BLANK_DISTANCE}, 0))",
            f"Both attackers heading {FACING_AWAY}° (facing away from target)",
        ],
        edge_cases=[
            "360° arc is omnidirectional — fires regardless of heading",
            "90° arc (±45° from heading 180°) covers 135°-225° — target at 0° is outside",
        ],
        expected_outcome=f"Baseline (360°): damage > 0. Variant (90°): 0 damage.",
        pass_criteria="baseline_damage > 0 AND variant_damage == 0",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "arc_set", "restriction", "binary"],
    )

    baseline_attacker_ship = OMNIDIRECTIONAL_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = ARC90_SHIP
    variant_target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE
    attacker_angle = FACING_AWAY  # Both face away from target

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Outcome: omnidirectional beam fires and hits
        checks.append(check_true(
            "Baseline (360°) Dealt Damage",
            self.baseline_damage_dealt > 10,
            detail=f"damage={self.baseline_damage_dealt}", phase="outcome",
        ))

        # Outcome: narrow arc beam cannot fire
        checks.append(check_exact(
            "Variant (90°) Zero Damage", 0.0,
            float(self.variant_damage_dealt), phase="outcome",
        ))

        # Outcome: variant fired zero shots
        v_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_exact(
            "Variant Zero Shots", 0, v_shots, phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-ARC-005: Set Semantics — Override, Not Multiply
# =============================================================================

class ModArc005_SetSemanticsScenario(StaticTargetScenario):
    """
    MOD-ARC-005: Verify 'set' operation overrides base arc.

    Base arc is 360°. test_turret(180) uses operation='set', so the result
    must be exactly 180° — NOT 360*180 (64800), NOT 360+180 (540).
    This confirms the 'set' operation semantics vs 'multiply' or 'add'.
    """
    metadata = TestMetadata(
        test_id="MOD-ARC-005",
        category="ArcSet",
        subcategory="ArcSet",
        name="Set semantics — override, not multiply/add",
        summary=f"Confirm 'set' produces exactly {ARC_180}° (not {BASE_ARC}*{TURRET_ARC_PARAM}={BASE_ARC * TURRET_ARC_PARAM} or {BASE_ARC}+{TURRET_ARC_PARAM}={BASE_ARC + TURRET_ARC_PARAM})",
        conditions=[
            f"Attacker: {TURRET180_SHIP} (test_beam_med_acc_1dmg + test_turret(param={TURRET_ARC_PARAM}), operation='set')",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px",
            f"Expected: arc={ARC_180} (exact), NOT {BASE_ARC}*{TURRET_ARC_PARAM} or {BASE_ARC}+{TURRET_ARC_PARAM}",
        ],
        edge_cases=[
            "'set' operation must produce exactly the parameter value",
            "base value is irrelevant when operation is 'set'",
        ],
        expected_outcome=f"firing_arc == {ARC_180} (exact override)",
        pass_criteria=f"firing_arc == {ARC_180} AND != {BASE_ARC * TURRET_ARC_PARAM} AND != {BASE_ARC + TURRET_ARC_PARAM}",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "arc_set", "set_semantics"],
    )

    attacker_ship = TURRET180_SHIP
    target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        self.actual_arc = beam.firing_arc if beam else None

    def _collect_extra_results(self, battle_engine):
        self.results['actual_arc'] = self.actual_arc
        self.results['if_multiplied'] = BASE_ARC * TURRET_ARC_PARAM
        self.results['if_added'] = BASE_ARC + TURRET_ARC_PARAM

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks

        arc = self.actual_arc or 0

        # Data: arc is exactly the set value
        checks.append(check_exact(
            "Firing Arc (Set Override)", ARC_180, arc, phase="data",
        ))

        # Data: NOT the result of multiplication
        checks.append(check_true(
            "Not Multiplied (360*180=64800)",
            arc != BASE_ARC * TURRET_ARC_PARAM,
            detail=f"arc={arc}, base*param={BASE_ARC * TURRET_ARC_PARAM}",
            phase="data",
        ))

        # Data: NOT the result of addition
        checks.append(check_true(
            "Not Added (360+180=540)",
            arc != BASE_ARC + TURRET_ARC_PARAM,
            detail=f"arc={arc}, base+param={BASE_ARC + TURRET_ARC_PARAM}",
            phase="data",
        ))

        # Outcome: weapon still functional
        checks.append(check_true(
            "Damage Dealt", self.damage_dealt > 10,
            detail=f"damage={self.damage_dealt}", phase="outcome",
        ))

        return checks
