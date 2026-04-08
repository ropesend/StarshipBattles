"""
ShieldRegeneratingArmor (SRA) Test Scenarios (SRA-001 to SRA-005)

These tests validate the ShieldRegeneratingArmor ability using A/B comparison
battles. SRA absorbs overflow damage (after shields and emissive armor) and
recharges shields by the absorbed amount.

Damage pipeline: Shields → Emissive Armor → SRA → Hull layers.
SRA only activates when damage overflows past shields. Absorbed damage is
converted to shield HP (capped at max_shields). The absorption is "free" —
does not cost the SRA component's HP.

Stacking: intra-group MAX, inter-group SUM (standard ability stacking).

All tests use guaranteed-hit beams for deterministic damage counts.

Expected behaviors:
- SRA recharges shields after they deplete, reducing hull damage
- Shield cap prevents SRA from overfilling shields beyond max_shields
- SRA effect stops when the component is destroyed
- Same-group stacking: MAX (no extra benefit)
- Different-group stacking: SUM (additive)
"""

from combat_lab.scenarios import TestMetadata
from combat_lab.scenarios.templates import ComparisonScenario
from combat_lab.scenarios.validation import check_exact, check_true
from combat_lab.test_constants import (
    POINT_BLANK_DISTANCE,
    STANDARD_SEED,
    SRA_TEST_TICKS,
    SRA_VALUE,
    SRA_SMALL_SHIELD_CAP,
)


# =============================================================================
# COMMON SHIP REFERENCES
# =============================================================================

ATTACKER_10DMG = "Test_Attacker_Beam_10dmg_Guaranteed.json"
ATTACKER_50DMG = "Test_Attacker_Beam_50dmg_Guaranteed.json"


# =============================================================================
# SRA-001: Basic Shield Recharge
# =============================================================================

class SRABasicRechargeScenario(ComparisonScenario):
    """
    SRA-001: SRA Recharges Shields, Reducing Hull Damage

    Battle A: Shield (200) + NO SRA → shields deplete, hull takes rest
    Battle B: Shield (200) + SRA (15) → shields deplete, SRA recharges,
              shields re-absorb, hull takes less

    With 10 dmg/tick: shields absorb 20 hits. Then each overflow hit:
    SRA absorbs min(15, remaining) and recharges shields. Remaining
    damage hits hull. The recharged shields absorb part of the next hit.
    """

    metadata = TestMetadata(
        test_id="SRA-001",
        category="ShieldRegeneratingArmor",
        subcategory="Basic Effect",
        name="SRA Recharges Shields, Reducing Hull Damage",
        summary="SRA recharges shields after depletion, reducing total hull damage",
        conditions=[
            f"Attacker: {ATTACKER_10DMG} (10 dmg, guaranteed hit, fires every tick)",
            "Target (no SRA): Test_Target_Shield_NoSRA.json (shield 200, no SRA)",
            "Target (with SRA): Test_Target_SRA.json (shield 200 + SRA 15)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {SRA_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "SRA only activates after shields deplete",
            "Shield recharge creates a recurring absorption cycle",
        ],
        expected_outcome="Variant takes less hull damage (SRA absorbs + recharges shields).",
        pass_criteria="variant_damage < baseline_damage",
        max_ticks=SRA_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["sra", "shield-regen", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_50DMG
    baseline_target_ship = "Test_Target_Shield_NoSRA.json"
    variant_attacker_ship = ATTACKER_50DMG
    variant_target_ship = "Test_Target_SRA.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline took hull damage
        checks.append(check_true(
            "Baseline Took Hull Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: SRA variant took less damage
        checks.append(check_true(
            "SRA Reduced Hull Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: variant shields are partially recharged (SRA fed them)
        checks.append(check_true(
            "Shields Recharged By SRA",
            self.target.current_shields > 0,
            detail=f"shields={self.target.current_shields}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# SRA-002: Shield Cap — Small Shield Not Overfilled
# =============================================================================

class SRAShieldCapScenario(ComparisonScenario):
    """
    SRA-002: Shield Cap Prevents Overfilling

    Battle A: Shield (200) + SRA (15) → SRA recharges up to 15
    Battle B: Shield (10) + SRA (15) → SRA recharges 15 but capped at 10

    The small shield can hold max 10 HP. Even though SRA absorbs 15, shields
    only recharge to min(max_shields, current + absorption) = 10.
    """

    metadata = TestMetadata(
        test_id="SRA-002",
        category="ShieldRegeneratingArmor",
        subcategory="Shield Cap",
        name="Small Shield Not Overfilled By SRA",
        summary=f"SRA({SRA_VALUE}) can't fill shield beyond max ({SRA_SMALL_SHIELD_CAP})",
        conditions=[
            f"Attacker: {ATTACKER_10DMG} (1 dmg, guaranteed hit)",
            f"Baseline: shield(200) + SRA({SRA_VALUE})",
            f"Variant: shield({SRA_SMALL_SHIELD_CAP}) + SRA({SRA_VALUE})",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {SRA_TEST_TICKS} ticks",
        ],
        edge_cases=[
            f"SRA recharges {SRA_VALUE} but shield max is {SRA_SMALL_SHIELD_CAP}",
            "Excess absorption beyond shield cap is wasted",
        ],
        expected_outcome="Variant takes more damage (smaller shield = less protection per cycle).",
        pass_criteria="variant_damage > baseline_damage",
        max_ticks=SRA_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["sra", "shield-cap", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_50DMG
    baseline_target_ship = "Test_Target_SRA.json"
    variant_attacker_ship = ATTACKER_50DMG
    variant_target_ship = "Test_Target_SRA_SmallShield.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify variant shield cap
        checks.append(check_exact(
            "Variant Max Shields",
            float(SRA_SMALL_SHIELD_CAP), self.target.max_shields,
        ))

        # Outcome: smaller shield = more hull damage
        checks.append(check_true(
            "Small Shield Takes More Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# SRA-003: Effect Stops When Component Destroyed
# =============================================================================

class SRADestroyedStopsEffectScenario(ComparisonScenario):
    """
    SRA-003: SRA Effect Stops When Component Is Destroyed

    Battle A: Indestructible SRA (1B HP in ARMOR) → effect works full test
    Battle B: Destructible SRA (50 HP in ARMOR, hit first) → SRA destroyed,
              effect stops, hull takes more damage afterward

    Uses 10-dmg beam to destroy the SRA component faster.
    """

    metadata = TestMetadata(
        test_id="SRA-003",
        category="ShieldRegeneratingArmor",
        subcategory="Destruction",
        name="SRA Effect Stops When Component Destroyed",
        summary="Destroying the SRA component stops the recharge effect",
        conditions=[
            f"Attacker: {ATTACKER_10DMG} (10 dmg, guaranteed hit)",
            "Baseline: indestructible SRA (1B HP) → effect works full test",
            "Variant: destructible SRA (50 HP in ARMOR) → destroyed, effect stops",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {SRA_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "SRA in ARMOR layer (outermost) is hit first",
            "After destruction, SRA value drops to 0 on recalculate_stats()",
        ],
        expected_outcome="Variant takes more damage (SRA destroyed early, no more recharge).",
        pass_criteria="variant_damage > baseline_damage",
        max_ticks=SRA_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["sra", "destruction", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_50DMG
    baseline_target_ship = "Test_Target_SRA_Indestructible.json"
    variant_attacker_ship = ATTACKER_50DMG
    variant_target_ship = "Test_Target_SRA_Destructible.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Outcome: destructible SRA variant takes more damage
        checks.append(check_true(
            "Destroyed SRA = More Hull Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# SRA-004: Same Group Does Not Stack (MAX)
# =============================================================================

class SRASameGroupNoStackScenario(ComparisonScenario):
    """
    SRA-004: Same Group Does Not Stack (Intra-Group MAX)

    Battle A: 1x SRA(15, SRA_A) → value = 15
    Battle B: 2x SRA(15, SRA_A) → MAX(15,15) = 15 (no extra benefit)

    Both should take identical damage.
    """

    metadata = TestMetadata(
        test_id="SRA-004",
        category="ShieldRegeneratingArmor",
        subcategory="Stacking",
        name="Same Group Does Not Stack",
        summary="Two SRA in same stack_group = MAX (no extra benefit)",
        conditions=[
            f"Attacker: {ATTACKER_10DMG} (1 dmg, guaranteed hit)",
            "Baseline: 1x SRA(15, SRA_A)",
            "Variant: 2x SRA(15, SRA_A)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {SRA_TEST_TICKS} ticks",
        ],
        edge_cases=["Intra-group MAX: duplicate has no benefit"],
        expected_outcome="Both take identical damage.",
        pass_criteria="baseline_damage == variant_damage",
        max_ticks=SRA_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["sra", "stacking", "same-group", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_50DMG
    baseline_target_ship = "Test_Target_SRA.json"
    variant_attacker_ship = ATTACKER_50DMG
    variant_target_ship = "Test_Target_SRA_2x_SameGroup.json"
    distance = POINT_BLANK_DISTANCE
    expect_different_damage = False  # Same-group MAX means identical damage

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: variant SRA value should equal baseline (MAX, not SUM)
        checks.append(check_exact(
            "Variant SRA Value (MAX)",
            float(SRA_VALUE), self.target.shield_regenerating_armor,
        ))

        # Outcome: identical damage
        checks.append(check_exact(
            "Same Damage (No Stack Benefit)",
            self.baseline_damage_dealt, self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# SRA-005: Different Groups Stack Additively (SUM)
# =============================================================================

class SRADiffGroupStackScenario(ComparisonScenario):
    """
    SRA-005: Different Groups Stack Additively (Inter-Group SUM)

    Battle A: 1x SRA(15, SRA_A) → value = 15
    Battle B: SRA(15, SRA_A) + SRA(15, SRA_B) → SUM = 30

    Variant has double SRA value, absorbing more and recharging more shields.
    """

    metadata = TestMetadata(
        test_id="SRA-005",
        category="ShieldRegeneratingArmor",
        subcategory="Stacking",
        name="Different Groups Stack Additively",
        summary="SRA in different stack_groups SUM (double absorption + recharge)",
        conditions=[
            f"Attacker: {ATTACKER_10DMG} (1 dmg, guaranteed hit)",
            "Baseline: 1x SRA(15, SRA_A)",
            "Variant: SRA(15, SRA_A) + SRA(15, SRA_B) = 30",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {SRA_TEST_TICKS} ticks",
        ],
        edge_cases=["Inter-group SUM: different groups add together"],
        expected_outcome="Variant takes less damage (double SRA = double absorption).",
        pass_criteria="variant_damage < baseline_damage",
        max_ticks=SRA_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["sra", "stacking", "diff-group", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_50DMG
    baseline_target_ship = "Test_Target_SRA.json"
    variant_attacker_ship = ATTACKER_50DMG
    variant_target_ship = "Test_Target_SRA_2x_DiffGroup.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: variant SRA value should be double (SUM)
        checks.append(check_exact(
            "Variant SRA Value (SUM)",
            float(SRA_VALUE * 2), self.target.shield_regenerating_armor,
        ))

        # Outcome: double SRA = less hull damage
        checks.append(check_true(
            "Double SRA = Less Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        return checks
