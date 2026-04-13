"""
ShieldProjection Test Scenarios (SHIELD-PROJ-001 to SHIELD-PROJ-007)

These tests validate the ShieldProjection ability using A/B comparison
battles.  Each test compares a shielded target against an unshielded
baseline to prove the shield caused the observed protection.

Damage pipeline: Shields -> Emissive Armor -> ShieldRegeneratingArmor -> Hull.
Shield absorption: absorbed = min(current_shields, damage).
If damage exceeds remaining shields, overflow hits hull in the same event.

Shield stacking: all ShieldProjection components SUM their capacity
values additively (no stack_group concept).

All tests use a guaranteed-hit beam (base_accuracy=10.0, falloff=0) for
deterministic damage counts.

Expected behaviors:
- Shield absorbs damage before hull is touched
- Shield depletion causes overflow to hull
- Multiple shield components combine additively
- A single hit can deplete shield AND damage hull in one event
"""

from combat_lab.scenarios import TestMetadata
from combat_lab.scenarios.templates import ComparisonScenario
from combat_lab.scenarios.validation import check_exact, check_true
from combat_lab.test_constants import (
    POINT_BLANK_DISTANCE,
    STANDARD_SEED,
    SHIELD_PROJ_1B_CAPACITY,
    SHIELD_PROJ_100_CAPACITY,
    SHIELD_PROJ_SINGLE_SHOT_DAMAGE,
    SHIELD_PROJ_TEST_TICKS,
    SHIELD_PROJ_SINGLE_SHOT_TICKS,
    SHIELD_PROJ_LARGE_BATTERY,
    SHIELD_PROJ_SMALL_BATTERY,
)


# =============================================================================
# COMMON SHIP REFERENCES
# =============================================================================

SHIELD_ATTACKER = "Test_Attacker_Beam_Guaranteed.json"
SHIELD_ATTACKER_SINGLE_SHOT = "Test_Attacker_Beam150_SingleShot.json"
UNSHIELDED_TARGET = "Test_Target_Stationary.json"


# =============================================================================
# SHIELD-PROJ-001: Shield Absorbs Damage
# =============================================================================

class ShieldAbsorbsDamageComparisonScenario(ComparisonScenario):
    """
    SHIELD-PROJ-001: Shield Absorbs Damage

    Battle A: Unshielded target — all hits damage armor
    Battle B: Target with 1B HP shield — shield absorbs all, armor untouched

    Proves that ShieldProjection prevents damage from reaching hull components.
    """

    metadata = TestMetadata(
        test_id="SHIELD-PROJ-001",
        category="ShieldProjection",
        subcategory="Basic Effect",
        name="Shield Absorbs Damage",
        summary="Shield absorbs all beam damage, armor is untouched",
        conditions=[
            f"Attacker: {SHIELD_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            f"Target (no shield): {UNSHIELDED_TARGET} (extreme armor only)",
            f"Target (with shield): Test_Target_Shield_1B.json (1B HP shield + extreme armor)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels (point blank)",
            f"Test Duration: {SHIELD_PROJ_TEST_TICKS} ticks per battle",
        ],
        edge_cases=[
            "Shield capacity far exceeds total damage dealt",
            "Armor HP should be completely unchanged in shielded battle",
        ],
        expected_outcome="Shielded target: zero armor damage, shield reduced. "
                         "Unshielded target: armor takes all damage.",
        pass_criteria="variant armor damage == 0, variant shield decreased, baseline took damage",
        max_ticks=SHIELD_PROJ_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["shield", "absorption", "shield-projection", "comparison"],
    )

    baseline_attacker_ship = SHIELD_ATTACKER
    baseline_target_ship = UNSHIELDED_TARGET
    variant_attacker_ship = SHIELD_ATTACKER
    variant_target_ship = "Test_Target_Shield_1B.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Data: verify shield capacity on variant
        checks.append(check_exact(
            "Shield Capacity", SHIELD_PROJ_1B_CAPACITY,
            self.target.max_shields,
        ))

        # Precondition: baseline target took damage
        checks.append(check_true(
            "Unshielded Target Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: shielded target took zero armor damage
        checks.append(check_exact(
            "Shielded Armor Damage", 0.0, self.variant_damage_dealt,
            phase="outcome",
        ))

        # Outcome: shield was reduced
        shield_absorbed = self.target.max_shields - self.target.current_shields
        checks.append(check_true(
            "Shield Absorbed Damage",
            shield_absorbed > 0,
            detail=f"absorbed={shield_absorbed}, remaining={self.target.current_shields}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# SHIELD-PROJ-002: Shield Depletion Overflows to Armor
# =============================================================================

class ShieldDepletionOverflowScenario(ComparisonScenario):
    """
    SHIELD-PROJ-002: Shield Depletion Overflows to Armor

    Battle A: Unshielded target — all 1000 hits damage armor
    Battle B: Target with 100 HP shield — first ~100 absorbed, rest hit armor

    Proves that once shields are depleted, subsequent damage reaches hull.
    The damage difference between battles equals the shield capacity.
    """

    metadata = TestMetadata(
        test_id="SHIELD-PROJ-002",
        category="ShieldProjection",
        subcategory="Depletion",
        name="Shield Depletion Overflows to Armor",
        summary="100 HP shield absorbs first 100 hits, then damage overflows to armor",
        conditions=[
            f"Attacker: {SHIELD_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            f"Target (no shield): {UNSHIELDED_TARGET} (extreme armor only)",
            f"Target (100 HP shield): Test_Target_Shield_100.json (100 HP shield + extreme armor)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels (point blank)",
            f"Test Duration: {SHIELD_PROJ_TEST_TICKS} ticks per battle",
        ],
        edge_cases=[
            "Shield depletes mid-test, damage then flows to hull",
            "Damage difference should equal shield capacity",
        ],
        expected_outcome=f"Shielded target takes ~{SHIELD_PROJ_100_CAPACITY} less armor damage "
                         f"than unshielded target",
        pass_criteria="variant shield == 0, damage_difference == shield_capacity",
        max_ticks=SHIELD_PROJ_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["shield", "depletion", "overflow", "shield-projection", "comparison"],
    )

    baseline_attacker_ship = SHIELD_ATTACKER
    baseline_target_ship = UNSHIELDED_TARGET
    variant_attacker_ship = SHIELD_ATTACKER
    variant_target_ship = "Test_Target_Shield_100.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Data: verify shield capacity on variant
        checks.append(check_exact(
            "Shield Capacity", SHIELD_PROJ_100_CAPACITY,
            self.target.max_shields,
        ))

        # Precondition: both targets took damage
        checks.append(check_true(
            "Unshielded Target Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))
        checks.append(check_true(
            "Shielded Target Took Armor Damage",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
        ))

        # Outcome: shield fully depleted
        checks.append(check_exact(
            "Shield Depleted", 0.0, self.target.current_shields,
            phase="outcome",
        ))

        # Outcome: damage difference equals shield capacity
        damage_diff = self.baseline_damage_dealt - self.variant_damage_dealt
        checks.append(check_exact(
            "Damage Difference Equals Shield Capacity",
            float(SHIELD_PROJ_100_CAPACITY), damage_diff,
            phase="outcome",
        ))

        return checks


# =============================================================================
# SHIELD-PROJ-003: Multiple Shields Stack Additively
# =============================================================================

class MultipleShieldsStackScenario(ComparisonScenario):
    """
    SHIELD-PROJ-003: Multiple Shields Stack Additively

    Battle A: Target with 1x 100 HP shield (100 total)
    Battle B: Target with 2x 100 HP shield (200 total)

    Proves that multiple ShieldProjection components sum their capacities.
    The variant should absorb ~100 more damage before armor is hit.
    """

    metadata = TestMetadata(
        test_id="SHIELD-PROJ-003",
        category="ShieldProjection",
        subcategory="Stacking",
        name="Multiple Shields Stack Additively",
        summary="Two 100 HP shields combine to 200 HP total, absorbing more damage",
        conditions=[
            f"Attacker: {SHIELD_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            "Target (1 shield): Test_Target_Shield_100.json (100 HP shield)",
            "Target (2 shields): Test_Target_Shield_2x100.json (2x 100 HP = 200 HP total)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels (point blank)",
            f"Test Duration: {SHIELD_PROJ_TEST_TICKS} ticks per battle",
        ],
        edge_cases=[
            "ShieldProjection has no stack_group — always sums additively",
            "Two identical components should give exactly 2x capacity",
        ],
        expected_outcome="2-shield target absorbs ~100 more damage than 1-shield target",
        pass_criteria="variant max_shields == 200, variant took less armor damage than baseline",
        max_ticks=SHIELD_PROJ_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["shield", "stacking", "additive", "shield-projection", "comparison"],
    )

    baseline_attacker_ship = SHIELD_ATTACKER
    baseline_target_ship = "Test_Target_Shield_100.json"
    variant_attacker_ship = SHIELD_ATTACKER
    variant_target_ship = "Test_Target_Shield_2x100.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Data: verify variant has double shield capacity
        checks.append(check_exact(
            "Variant Shield Capacity", SHIELD_PROJ_100_CAPACITY * 2,
            self.target.max_shields,
        ))

        # Precondition: both targets took armor damage (shields depleted in both)
        checks.append(check_true(
            "Single Shield Target Took Armor Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))
        checks.append(check_true(
            "Double Shield Target Took Armor Damage",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
        ))

        # Outcome: both shields depleted
        checks.append(check_exact(
            "Variant Shields Depleted", 0.0, self.target.current_shields,
            phase="outcome",
        ))

        # Outcome: double-shield absorbed more damage
        checks.append(check_true(
            "Double Shield Absorbed More",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"single={self.baseline_damage_dealt}, "
                   f"double={self.variant_damage_dealt}, "
                   f"extra_absorbed={self.baseline_damage_dealt - self.variant_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: damage difference equals the extra shield capacity (100)
        damage_diff = self.baseline_damage_dealt - self.variant_damage_dealt
        checks.append(check_exact(
            "Extra Absorption Equals Added Capacity",
            float(SHIELD_PROJ_100_CAPACITY), damage_diff,
            phase="outcome",
        ))

        return checks


# =============================================================================
# SHIELD-PROJ-004: Single-Hit Overflow
# =============================================================================

class SingleHitOverflowScenario(ComparisonScenario):
    """
    SHIELD-PROJ-004: Single-Hit Overflow

    Battle A: Unshielded target — single 150-damage hit goes entirely to armor
    Battle B: Target with 100 HP shield — shield absorbs 100, armor takes 50

    Proves that a single hit exceeding shield capacity correctly splits:
    shield absorbs up to capacity, remainder damages armor in the same event.
    """

    metadata = TestMetadata(
        test_id="SHIELD-PROJ-004",
        category="ShieldProjection",
        subcategory="Single-Hit Overflow",
        name="Single-Hit Overflow",
        summary="One 150-damage hit vs 100 HP shield: shield absorbs 100, 50 overflows to armor",
        conditions=[
            f"Attacker: {SHIELD_ATTACKER_SINGLE_SHOT} (150 dmg, guaranteed hit, 999s reload)",
            f"Target (no shield): {UNSHIELDED_TARGET} (extreme armor only)",
            "Target (100 HP shield): Test_Target_Shield_100.json (100 HP shield + extreme armor)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels (point blank)",
            f"Test Duration: {SHIELD_PROJ_SINGLE_SHOT_TICKS} ticks",
            "Weapon fires exactly once (999s reload exceeds test duration)",
        ],
        edge_cases=[
            "Single hit: damage (150) > shield capacity (100)",
            "Shield absorbs 100, armor takes 50 in the same damage event",
            "Shield drops to 0, not below 0",
        ],
        expected_outcome="Baseline: 150 armor damage. Variant: 50 armor damage, shield at 0.",
        pass_criteria="variant shield == 0, baseline damage == 150, variant damage == 50",
        max_ticks=SHIELD_PROJ_SINGLE_SHOT_TICKS,
        seed=STANDARD_SEED,
        tags=["shield", "overflow", "single-hit", "shield-projection", "comparison"],
    )

    baseline_attacker_ship = SHIELD_ATTACKER_SINGLE_SHOT
    baseline_target_ship = UNSHIELDED_TARGET
    variant_attacker_ship = SHIELD_ATTACKER_SINGLE_SHOT
    variant_target_ship = "Test_Target_Shield_100.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Data: verify shield capacity and weapon damage
        checks.append(check_exact(
            "Shield Capacity", SHIELD_PROJ_100_CAPACITY,
            self.target.max_shields,
        ))
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            checks.append(check_exact(
                "Beam Damage", SHIELD_PROJ_SINGLE_SHOT_DAMAGE, beam.damage,
            ))

        # Precondition: weapon fired exactly once in each battle
        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_exact(
            "Baseline Shots Fired", 1, baseline_shots,
            phase="precondition",
        ))
        checks.append(check_exact(
            "Variant Shots Fired", 1, variant_shots,
            phase="precondition",
        ))

        # Outcome: baseline took full 150 to armor
        checks.append(check_exact(
            "Baseline Armor Damage", float(SHIELD_PROJ_SINGLE_SHOT_DAMAGE),
            self.baseline_damage_dealt,
            phase="outcome",
        ))

        # Outcome: variant shield fully depleted
        checks.append(check_exact(
            "Shield Depleted", 0.0, self.target.current_shields,
            phase="outcome",
        ))

        # Outcome: variant armor took only the overflow (150 - 100 = 50)
        expected_overflow = SHIELD_PROJ_SINGLE_SHOT_DAMAGE - SHIELD_PROJ_100_CAPACITY
        checks.append(check_exact(
            "Variant Armor Damage (overflow)", float(expected_overflow),
            self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# SHIELD-PROJ-005: Shield With Sufficient Energy Functions Normally
# =============================================================================

class ShieldWithSufficientEnergyScenario(ComparisonScenario):
    """
    SHIELD-PROJ-005: Shield With Sufficient Energy Functions Normally

    Battle A: Unshielded target — all damage hits armor
    Battle B: Target with 100 HP energy shield + large battery (15 energy, lasts 1500 ticks)

    Proves that a shield component with ResourceConsumption(energy) works
    normally when sufficient energy is available. The shield absorbs its
    full capacity before armor takes damage.
    """

    metadata = TestMetadata(
        test_id="SHIELD-PROJ-005",
        category="ShieldProjection",
        subcategory="Energy Consumption",
        name="Shield With Sufficient Energy",
        summary="Energy-consuming shield with adequate battery functions normally",
        conditions=[
            f"Attacker: {SHIELD_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            f"Target (no shield): {UNSHIELDED_TARGET} (extreme armor only)",
            "Target (energy shield): Test_Target_Shield_100_LargeBattery.json "
            f"(100 HP shield, 1.0 energy/sec, {SHIELD_PROJ_LARGE_BATTERY} energy battery)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {SHIELD_PROJ_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Shield has energy cost but battery is sufficient for full test",
            "Behavior should be identical to a free shield",
        ],
        expected_outcome=f"Shield absorbs {SHIELD_PROJ_100_CAPACITY} damage, "
                         f"armor takes ~{SHIELD_PROJ_TEST_TICKS - SHIELD_PROJ_100_CAPACITY} less "
                         f"than unshielded",
        pass_criteria="variant took ~100 less armor damage than baseline, shield depleted",
        max_ticks=SHIELD_PROJ_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["shield", "energy", "battery", "shield-projection", "comparison"],
    )

    baseline_attacker_ship = SHIELD_ATTACKER
    baseline_target_ship = UNSHIELDED_TARGET
    variant_attacker_ship = SHIELD_ATTACKER
    variant_target_ship = "Test_Target_Shield_100_LargeBattery.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Data: verify shield and energy
        checks.append(check_exact(
            "Shield Capacity", SHIELD_PROJ_100_CAPACITY,
            self.target.max_shields,
        ))

        # Precondition: baseline took damage
        checks.append(check_true(
            "Unshielded Target Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: shield depleted (all 100 HP absorbed)
        checks.append(check_exact(
            "Shield Depleted", 0.0, self.target.current_shields,
            phase="outcome",
        ))

        # Outcome: damage difference equals shield capacity
        damage_diff = self.baseline_damage_dealt - self.variant_damage_dealt
        checks.append(check_exact(
            "Shield Absorbed Full Capacity",
            float(SHIELD_PROJ_100_CAPACITY), damage_diff,
            phase="outcome",
        ))

        return checks


# =============================================================================
# SHIELD-PROJ-005B: Powered 1B Shield — Zero Armor Damage
# =============================================================================

class ShieldWithEnergyZeroDamageScenario(ComparisonScenario):
    """
    SHIELD-PROJ-005B: Powered 1B Shield — Zero Armor Damage

    Battle A: Unshielded target — all damage hits armor
    Battle B: Target with 1B HP energy shield + large battery

    The 1B shield never depletes from 1000 ticks of 1-damage hits, and the
    battery lasts the full test.  The variant should take zero armor damage.
    """

    metadata = TestMetadata(
        test_id="SHIELD-PROJ-005B",
        category="ShieldProjection",
        subcategory="Energy Consumption",
        name="Powered 1B Shield — Zero Armor Damage",
        summary="1B energy shield with sufficient battery absorbs all damage, armor untouched",
        conditions=[
            f"Attacker: {SHIELD_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            f"Target (no shield): {UNSHIELDED_TARGET} (extreme armor only)",
            "Target (powered 1B shield): Test_Target_Shield_1B_LargeBattery.json "
            f"(1B HP shield, 1.0 energy/sec, {SHIELD_PROJ_LARGE_BATTERY} energy battery)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {SHIELD_PROJ_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "1B shield capacity far exceeds total damage",
            "Battery sufficient for full test duration",
            "Armor should be completely untouched",
        ],
        expected_outcome="Variant: zero armor damage. Baseline: ~1000 armor damage.",
        pass_criteria="variant armor damage == 0, baseline took damage",
        max_ticks=SHIELD_PROJ_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["shield", "energy", "battery", "zero-damage", "shield-projection", "comparison"],
    )

    baseline_attacker_ship = SHIELD_ATTACKER
    baseline_target_ship = UNSHIELDED_TARGET
    variant_attacker_ship = SHIELD_ATTACKER
    variant_target_ship = "Test_Target_Shield_1B_LargeBattery.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline took damage
        checks.append(check_true(
            "Unshielded Target Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: powered 1B shield — zero armor damage
        checks.append(check_exact(
            "Zero Armor Damage",
            0.0, self.variant_damage_dealt,
            phase="outcome",
        ))

        # Outcome: shield absorbed all hits
        shield_absorbed = self.target.max_shields - self.target.current_shields
        checks.append(check_true(
            "Shield Absorbed All Damage",
            shield_absorbed > 0,
            detail=f"absorbed={shield_absorbed}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# SHIELD-PROJ-006: Shield Fails When Energy Depletes Mid-Battle
# =============================================================================

class ShieldFailsOnEnergyDepletionScenario(ComparisonScenario):
    """
    SHIELD-PROJ-006: Shield Fails When Energy Depletes Mid-Battle

    Battle A: Target with 1B shield + large battery (energy lasts full test)
    Battle B: Target with 1B shield + small battery (energy depletes at tick ~500)

    Uses the 1B shield so it never depletes from damage alone.  The only
    reason the shield stops protecting is energy depletion.  The variant
    should take more armor damage because its shield deactivates halfway.
    """

    metadata = TestMetadata(
        test_id="SHIELD-PROJ-006",
        category="ShieldProjection",
        subcategory="Energy Consumption",
        name="Shield Fails When Energy Depletes",
        summary="Shield deactivates mid-battle when battery runs out, armor takes remaining damage",
        conditions=[
            f"Attacker: {SHIELD_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            "Target (full power): Test_Target_Shield_1B_LargeBattery.json "
            f"(1B shield, 1.0 energy/sec, {SHIELD_PROJ_LARGE_BATTERY} energy battery)",
            "Target (low power): Test_Target_Shield_1B_SmallBattery.json "
            f"(1B shield, 1.0 energy/sec, {SHIELD_PROJ_SMALL_BATTERY} energy battery)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {SHIELD_PROJ_TEST_TICKS} ticks",
            f"Small battery depletes at tick ~{SHIELD_PROJ_SMALL_BATTERY * 100}",
        ],
        edge_cases=[
            "Shield deactivates mid-battle when energy runs out",
            "1B shield capacity — never depletes from damage, only from power loss",
            "Armor absorbs damage only after energy depletion",
        ],
        expected_outcome="Full-power target: 0 armor damage. "
                         "Low-power target: ~500 armor damage (unprotected for last ~500 ticks).",
        pass_criteria="baseline armor damage == 0, variant armor damage > 0",
        max_ticks=SHIELD_PROJ_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["shield", "energy", "depletion", "shield-projection", "comparison"],
    )

    baseline_attacker_ship = SHIELD_ATTACKER
    baseline_target_ship = "Test_Target_Shield_1B_LargeBattery.json"
    variant_attacker_ship = SHIELD_ATTACKER
    variant_target_ship = "Test_Target_Shield_1B_SmallBattery.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Outcome: baseline (full power) took zero armor damage
        checks.append(check_exact(
            "Full-Power Shield — Zero Armor Damage",
            0.0, self.baseline_damage_dealt,
            phase="outcome",
        ))

        # Outcome: variant (low power) took armor damage after energy depleted
        checks.append(check_true(
            "Low-Power Shield — Armor Took Damage",
            self.variant_damage_dealt > 0,
            detail=f"armor_damage={self.variant_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: variant took substantially less damage than a fully unshielded target
        # would (shield protected for ~500 ticks)
        checks.append(check_true(
            "Shield Protected Before Depletion",
            self.variant_damage_dealt < SHIELD_PROJ_TEST_TICKS * 0.75,
            detail=f"damage={self.variant_damage_dealt}, "
                   f"max_possible={SHIELD_PROJ_TEST_TICKS}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# SHIELD-PROJ-007: Shield Without Energy Never Activates
# =============================================================================

class ShieldWithoutEnergyScenario(ComparisonScenario):
    """
    SHIELD-PROJ-007: Shield Without Energy Never Activates

    Battle A: Unshielded target — all damage hits armor
    Battle B: Target with 100 HP energy shield but NO battery

    The shield requires energy to operate but has none. It should provide
    negligible protection — at most 1 tick of leakage before the engine
    detects starvation and deactivates the component.

    Note: There is a 1-tick initialization delay: shields start at max_shields
    before the first component.update() detects starvation. This means the
    shield may absorb 1 hit on tick 1 before being deactivated.
    """

    metadata = TestMetadata(
        test_id="SHIELD-PROJ-007",
        category="ShieldProjection",
        subcategory="Energy Consumption",
        name="Shield Without Energy Never Activates",
        summary="Shield with energy requirement but no battery provides negligible protection",
        conditions=[
            f"Attacker: {SHIELD_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            f"Target (no shield): {UNSHIELDED_TARGET} (extreme armor only)",
            "Target (unpowered shield): Test_Target_Shield_100_NoBattery.json "
            "(100 HP shield, 1.0 energy/sec, NO battery)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {SHIELD_PROJ_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Shield component exists but cannot operate without energy",
            "1-tick initialization delay: shield may absorb 1 hit before deactivation",
        ],
        expected_outcome="Unpowered shield provides at most 1 tick of protection",
        pass_criteria="variant damage >= baseline damage - 1",
        max_ticks=SHIELD_PROJ_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["shield", "energy", "no-power", "shield-projection", "comparison"],
    )

    baseline_attacker_ship = SHIELD_ATTACKER
    baseline_target_ship = UNSHIELDED_TARGET
    variant_attacker_ship = SHIELD_ATTACKER
    variant_target_ship = "Test_Target_Shield_100_NoBattery.json"
    distance = POINT_BLANK_DISTANCE
    expect_different_damage = False  # Energy-starved shields = same as unshielded

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline took damage
        checks.append(check_true(
            "Unshielded Target Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: unpowered shield provided at most 1 tick of protection
        # (1-tick delay: shields initialize before first component.update())
        damage_diff = self.baseline_damage_dealt - self.variant_damage_dealt
        checks.append(check_true(
            "Unpowered Shield — Negligible Protection",
            damage_diff <= 1,
            detail=f"baseline={self.baseline_damage_dealt}, "
                   f"variant={self.variant_damage_dealt}, "
                   f"diff={damage_diff} (max allowed: 1)",
            phase="outcome",
        ))

        return checks


# =============================================================================
# GENERIC RESOURCE TESTS — METALS (SHIELD-PROJ-METALS-001 to 002)
# =============================================================================
# Prove shields work with ANY resource type, not just energy.
# Uses "metals" (a real planetary resource defined in data/resources.json).

SHIELD_METALS_TARGET_FULL = "Test_Target_Shield_100_HighMetals.json"
SHIELD_METALS_TARGET_NONE = "Test_Target_Shield_100_NoMetals.json"


class ShieldWithMetalsProtects(ComparisonScenario):
    """
    SHIELD-PROJ-METALS-001: Shield With Metals Protects

    Battle A: Unshielded target — all damage hits armor
    Battle B: Target with 100 HP metals-consuming shield + 100k metals

    Proves the resource system is generic: a shield consuming "metals"
    works identically to one consuming "energy".
    """

    metadata = TestMetadata(
        test_id="SHIELD-PROJ-METALS-001",
        category="ShieldProjection",
        subcategory="Generic Resource",
        name="Shield With Metals Protects",
        summary="Shield consuming metals (planetary resource) functions normally with supply",
        conditions=[
            f"Attacker: {SHIELD_ATTACKER} (guaranteed-hit beam, 1 dmg/tick)",
            f"Target (no shield): {UNSHIELDED_TARGET}",
            f"Target (metals shield): {SHIELD_METALS_TARGET_FULL} (100 HP shield, 1.0 metals/sec)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {SHIELD_PROJ_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "'metals' is a planetary resource, not a standard operational resource",
            "Shield with constant metals consumption should function like energy shield",
        ],
        expected_outcome="Metals shield absorbs 100 damage, variant takes less armor damage.",
        pass_criteria="variant took less damage than baseline, shield depleted",
        max_ticks=SHIELD_PROJ_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["shield", "metals", "generic-resource", "shield-projection", "comparison"],
    )

    baseline_attacker_ship = SHIELD_ATTACKER
    baseline_target_ship = UNSHIELDED_TARGET
    variant_attacker_ship = SHIELD_ATTACKER
    variant_target_ship = SHIELD_METALS_TARGET_FULL
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline took damage
        checks.append(check_true(
            "Unshielded Target Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: metals shield absorbed damage
        checks.append(check_true(
            "Metals Shield Reduced Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"unshielded={self.baseline_damage_dealt}, "
                   f"shielded={self.variant_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: shield depleted
        checks.append(check_exact(
            "Shield Depleted", 0.0, self.target.current_shields,
            phase="outcome",
        ))

        # Outcome: damage difference equals shield capacity
        damage_diff = self.baseline_damage_dealt - self.variant_damage_dealt
        checks.append(check_exact(
            "Shield Absorbed Full Capacity",
            float(SHIELD_PROJ_100_CAPACITY), damage_diff,
            phase="outcome",
        ))

        return checks


class ShieldWithoutMetalsNoProtection(ComparisonScenario):
    """
    SHIELD-PROJ-METALS-002: Shield Without Metals Provides No Protection

    Battle A: Unshielded target — all damage hits armor
    Battle B: Target with metals-consuming shield but NO metals storage

    Proves that a shield consuming a planetary resource correctly deactivates
    when that resource is unavailable.
    """

    metadata = TestMetadata(
        test_id="SHIELD-PROJ-METALS-002",
        category="ShieldProjection",
        subcategory="Generic Resource",
        name="Shield Without Metals — No Protection",
        summary="Shield consuming metals but with no supply provides negligible protection",
        conditions=[
            f"Attacker: {SHIELD_ATTACKER} (guaranteed-hit beam, 1 dmg/tick)",
            f"Target (no shield): {UNSHIELDED_TARGET}",
            f"Target (unpowered metals shield): {SHIELD_METALS_TARGET_NONE}",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {SHIELD_PROJ_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Shield requires metals but has none — should not function",
            "1-tick initialization delay may allow 1 hit of absorption",
        ],
        expected_outcome="Unpowered metals shield provides at most 1 tick of protection.",
        pass_criteria="damage_diff <= 1",
        max_ticks=SHIELD_PROJ_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["shield", "metals", "generic-resource", "no-power", "shield-projection", "comparison"],
    )

    baseline_attacker_ship = SHIELD_ATTACKER
    baseline_target_ship = UNSHIELDED_TARGET
    variant_attacker_ship = SHIELD_ATTACKER
    variant_target_ship = SHIELD_METALS_TARGET_NONE
    distance = POINT_BLANK_DISTANCE
    expect_different_damage = False  # Resource-starved shields = same as unshielded

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        checks.append(check_true(
            "Unshielded Target Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: unpowered metals shield provided at most 1 tick of protection
        damage_diff = self.baseline_damage_dealt - self.variant_damage_dealt
        checks.append(check_true(
            "Unpowered Metals Shield — Negligible Protection",
            damage_diff <= 1,
            detail=f"baseline={self.baseline_damage_dealt}, "
                   f"variant={self.variant_damage_dealt}, "
                   f"diff={damage_diff} (max allowed: 1)",
            phase="outcome",
        ))

        return checks
