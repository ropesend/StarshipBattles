"""
Damage Pipeline Integration Test Scenarios (PIPELINE-001 to PIPELINE-005, PIPELINE-007)

These tests validate the full damage pipeline and pairwise defense combinations.
Individual defenses are tested in isolation elsewhere; these tests verify the
chain works correctly when multiple defenses are active simultaneously.

Damage pipeline order: Shields -> EmissiveArmor -> ShieldRegeneratingArmor -> Hull layers.

Each test uses ComparisonScenario (A/B) with guaranteed-hit beams for
deterministic results.

Test matrix:
- PIPELINE-001: Shield + Emissive (pairwise)
- PIPELINE-002: Shield + SRA recharge cycle (pairwise)
- PIPELINE-003: Emissive + SRA without shields (pairwise)
- PIPELINE-004: Full pipeline vs no defenses
- PIPELINE-005: Full pipeline with vs without shield regen
- PIPELINE-007: SRA cap overflow with high-damage beam
"""

from combat_lab.scenarios import TestMetadata
from combat_lab.scenarios.templates import ComparisonScenario
from combat_lab.scenarios.validation import check_true
from combat_lab.test_constants import (
    POINT_BLANK_DISTANCE,
    STANDARD_SEED,
    STANDARD_TEST_TICKS,
    EMISSIVE_ARMOR_VALUE,
    SRA_VALUE,
)


# =============================================================================
# COMMON SHIP REFERENCES
# =============================================================================

ATTACKER_1DMG = "Test_Attacker_Beam_Guaranteed.json"
ATTACKER_10DMG = "Test_Attacker_Beam_10dmg_Guaranteed.json"
ATTACKER_30DMG = "Test_Attacker_Beam_30dmg_Guaranteed.json"
ATTACKER_50DMG = "Test_Attacker_Beam_50dmg_Guaranteed.json"

PIPELINE_TEST_TICKS = STANDARD_TEST_TICKS  # 500 ticks


# =============================================================================
# PIPELINE-001: Shield + Emissive Armor
# =============================================================================

class PipelineShieldEmissiveScenario(ComparisonScenario):
    """
    PIPELINE-001: Shield + Emissive Armor Combination

    Baseline: shield(100) only — after 100 ticks shields deplete, hull takes
              full 10 dmg/hit for remaining ticks.
    Variant:  shield(100) + emissive(5) — after shields deplete, emissive
              reduces each 10-dmg hit to 5 dmg.

    Uses 10-dmg beam so damage exceeds emissive value (5) after shields fall.
    After shield depletion at tick ~10:
    - Baseline: 10 dmg/hit to hull
    - Variant:  5 dmg/hit to hull (emissive blocks 5)
    Variant should take roughly half the hull damage of baseline.
    """

    metadata = TestMetadata(
        test_id="PIPELINE-001",
        category="DamagePipeline",
        subcategory="Pairwise",
        name="Shield + Emissive Armor Reduces Hull Damage",
        summary="Emissive armor reduces overflow damage after shields deplete",
        conditions=[
            f"Attacker: {ATTACKER_10DMG} (10 dmg, guaranteed hit, fires every tick)",
            "Baseline target: shield(100) only (Test_Target_Shield_100.json)",
            f"Variant target: shield(100) + emissive({EMISSIVE_ARMOR_VALUE})",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {PIPELINE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Emissive only activates on overflow damage (not while shields hold)",
            "Emissive reduces per-hit, not per-tick",
        ],
        expected_outcome="Variant takes less hull damage (emissive reduces each post-shield hit by 5).",
        pass_criteria="variant_damage < baseline_damage, both > 0",
        max_ticks=PIPELINE_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["pipeline", "shield", "emissive", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_10DMG
    baseline_target_ship = "Test_Target_Shield_100.json"
    variant_attacker_ship = ATTACKER_10DMG
    variant_target_ship = "Test_Target_Pipeline_Shield100_Emissive5.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline took hull damage (shields depleted)
        checks.append(check_true(
            "Baseline Took Hull Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Precondition: variant also took hull damage (shields also deplete)
        checks.append(check_true(
            "Variant Took Hull Damage",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
        ))

        # Outcome: emissive reduces hull damage
        checks.append(check_true(
            "Emissive Reduced Hull Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# PIPELINE-002: Shield + SRA Recharge Cycle
# =============================================================================

class PipelineShieldSRAScenario(ComparisonScenario):
    """
    PIPELINE-002: Shield + SRA Recharge Cycle

    Baseline: shield(10) only — depletes in 10 ticks (1 dmg/tick), then all
              damage goes to hull.
    Variant:  shield(10) + SRA(15) — after shields deplete, SRA absorbs
              overflow and recharges shields, creating a recurring cycle.

    With 1 dmg/tick beam and SRA(15):
    - Shield absorbs first 10 hits
    - Hit 11: overflow 1 dmg, SRA absorbs 1 and recharges 1 shield HP
    - Next hit: shield absorbs 1 again, cycle repeats
    - Result: SRA + shield cycle absorbs nearly all damage
    """

    metadata = TestMetadata(
        test_id="PIPELINE-002",
        category="DamagePipeline",
        subcategory="Pairwise",
        name="Shield + SRA Recharge Cycle",
        summary="SRA recharges shields after depletion, creating a damage absorption cycle",
        conditions=[
            f"Attacker: {ATTACKER_1DMG} (1 dmg, guaranteed hit, fires every tick)",
            "Baseline target: shield(10) only",
            f"Variant target: shield(10) + SRA({SRA_VALUE})",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {PIPELINE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "SRA recharges shields creating recurring absorption",
            "1 dmg/tick means SRA absorbs all overflow (1 < 15)",
        ],
        expected_outcome="Variant takes much less hull damage (SRA absorbs + recharges shields).",
        pass_criteria="variant_damage < baseline_damage",
        max_ticks=PIPELINE_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["pipeline", "shield", "sra", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_1DMG
    baseline_target_ship = "Test_Target_Pipeline_Shield10_Only.json"
    variant_attacker_ship = ATTACKER_1DMG
    variant_target_ship = "Test_Target_SRA_SmallShield.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline took hull damage
        checks.append(check_true(
            "Baseline Took Hull Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: SRA variant took less damage
        checks.append(check_true(
            "SRA Recharge Reduced Hull Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# PIPELINE-003: Emissive + SRA (No Shields)
# =============================================================================

class PipelineEmissiveSRAScenario(ComparisonScenario):
    """
    PIPELINE-003: Emissive Armor + SRA Without Shields

    Tests that emissive reduces damage BEFORE SRA processes it.

    Baseline: SRA(15) only — 10 dmg hits hull, SRA absorbs all 10 (but has
              no shields to recharge), 0 leaks to hull.
    Variant:  emissive(5) + SRA(15) — emissive reduces 10 to 5, then SRA
              absorbs remaining 5, 0 leaks to hull.

    Both should take 0 hull damage with a 10-dmg beam (SRA absorbs all
    post-emissive damage in both cases). But the SRA absorbs LESS per hit
    in the variant (5 vs 10), proving emissive acts before SRA.

    Since both produce 0 hull damage, we verify the pipeline order by
    checking SRA with a beam that exceeds SRA capacity:
    - Actually, SRA(15) absorbs up to 15 per hit, so 10 dmg is always
      fully absorbed by SRA alone.

    Better approach: use a beam that exceeds SRA(15) absorption.
    With 10-dmg beam and SRA(15), all damage is absorbed by SRA.
    So hull damage is 0 for both. We can't differentiate.

    Revised: Baseline = emissive(5) only (no SRA). Variant = emissive(5) + SRA(15).
    With 10-dmg beam:
    - Baseline: emissive reduces to 5, 5 hits hull every tick
    - Variant: emissive reduces to 5, SRA absorbs 5, 0 hits hull
    This proves SRA handles post-emissive overflow.
    """

    metadata = TestMetadata(
        test_id="PIPELINE-003",
        category="DamagePipeline",
        subcategory="Pairwise",
        name="Emissive + SRA Layered Defense (No Shields)",
        summary="Emissive reduces damage before SRA absorbs the remainder",
        conditions=[
            f"Attacker: {ATTACKER_10DMG} (10 dmg, guaranteed hit, fires every tick)",
            f"Baseline target: emissive({EMISSIVE_ARMOR_VALUE}) only (no SRA, no shield)",
            f"Variant target: emissive({EMISSIVE_ARMOR_VALUE}) + SRA({SRA_VALUE}) (no shield)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {PIPELINE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "No shields — damage goes directly to emissive then SRA",
            "SRA has no shields to recharge (absorbs but wastes recharge)",
            "Emissive reduces 10 to 5, SRA absorbs remaining 5",
        ],
        expected_outcome="Baseline takes hull damage (5/hit), variant takes zero (SRA absorbs all post-emissive).",
        pass_criteria="baseline_damage > 0 AND variant_damage < baseline_damage",
        max_ticks=PIPELINE_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["pipeline", "emissive", "sra", "no-shields", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_10DMG
    baseline_target_ship = "Test_Target_EmissiveArmor.json"
    variant_attacker_ship = ATTACKER_10DMG
    variant_target_ship = "Test_Target_Pipeline_Emissive5_SRA15.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline took hull damage (emissive only reduces, doesn't block all)
        checks.append(check_true(
            "Baseline Took Hull Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt} (emissive reduces 10 to 5, 5/hit to hull)",
        ))

        # Outcome: SRA absorbs all post-emissive damage
        checks.append(check_true(
            "SRA Absorbed Post-Emissive Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# PIPELINE-004: Full Pipeline vs No Defenses
# =============================================================================

class PipelineFullVsNoneScenario(ComparisonScenario):
    """
    PIPELINE-004: Full Pipeline vs No Defenses

    Baseline: no defenses at all (extreme hull only) — takes 10 dmg/hit
    Variant:  shield(100) + emissive(5) + SRA(15) — full chain

    With 10-dmg beam:
    - Baseline: 10 * 500 = 5000 total hull damage
    - Variant: shields absorb first 10 hits (100 HP), then emissive reduces
      to 5, SRA absorbs 5 and recharges 5 shields. Recurring cycle means
      dramatically less hull damage.
    """

    metadata = TestMetadata(
        test_id="PIPELINE-004",
        category="DamagePipeline",
        subcategory="Full Chain",
        name="Full Pipeline vs No Defenses",
        summary="Full defense chain (shield + emissive + SRA) drastically reduces damage",
        conditions=[
            f"Attacker: {ATTACKER_10DMG} (10 dmg, guaranteed hit, fires every tick)",
            "Baseline target: no defenses (Test_Target_Stationary.json)",
            "Variant target: shield(100) + emissive(5) + SRA(15)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {PIPELINE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "All three defenses active simultaneously",
            "SRA recharges shields, extending shield absorption cycles",
        ],
        expected_outcome="Variant takes drastically less damage than undefended baseline.",
        pass_criteria="variant_damage < baseline_damage AND baseline_damage > 0",
        max_ticks=PIPELINE_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["pipeline", "full-chain", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_10DMG
    baseline_target_ship = "Test_Target_Stationary.json"
    variant_attacker_ship = ATTACKER_10DMG
    variant_target_ship = "Test_Target_Pipeline_Full.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline took substantial hull damage
        checks.append(check_true(
            "Baseline Took Hull Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: full pipeline drastically reduces damage
        checks.append(check_true(
            "Full Pipeline Reduced Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: variant should take less than half the baseline damage
        # (shield absorbs 100, then emissive+SRA cycle absorbs most of the rest)
        checks.append(check_true(
            "Damage Reduction > 50%",
            self.variant_damage_dealt < self.baseline_damage_dealt * 0.5,
            detail=(
                f"variant={self.variant_damage_dealt}, "
                f"threshold={self.baseline_damage_dealt * 0.5:.0f} (50% of baseline)"
            ),
            phase="outcome",
        ))

        return checks


# =============================================================================
# PIPELINE-005: Full Pipeline With vs Without Shield Regen
# =============================================================================

class PipelineFullRegenScenario(ComparisonScenario):
    """
    PIPELINE-005: Full Pipeline + Shield Regeneration

    Baseline: shield(100) + emissive(5) + SRA(15) — full pipeline, no regen
    Variant:  shield(100) + emissive(5) + SRA(15) + regen(10/s) — with regen

    Uses 50-dmg beam so damage overflows past all defenses (emissive reduces
    50 to 45, SRA absorbs 15, 30 leaks to hull). Shield regen restores shield
    HP between hits, meaning shields absorb more total damage over 500 ticks,
    reducing hull damage.

    With 10-dmg beam, emissive(5)+SRA(15) fully blocks all post-shield overflow
    so there is no difference for regen to improve. The 50-dmg beam ensures
    hull damage occurs in both scenarios.
    """

    metadata = TestMetadata(
        test_id="PIPELINE-005",
        category="DamagePipeline",
        subcategory="Full Chain",
        name="Shield Regen Extends Full Pipeline Protection",
        summary="Adding shield regen to the full pipeline reduces hull damage further",
        conditions=[
            f"Attacker: {ATTACKER_50DMG} (50 dmg, guaranteed hit, fires every tick)",
            "Baseline target: shield(100) + emissive(5) + SRA(15) (no regen)",
            "Variant target: shield(100) + emissive(5) + SRA(15) + regen(10/s)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {PIPELINE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Regen restores shields between hits, reducing overflow frequency",
            "SRA and regen both contribute to shield HP (different mechanisms)",
            "50 dmg beam overflows past emissive(5) + SRA(15) = 20 absorption",
        ],
        expected_outcome="Variant takes less hull damage (regen extends shield life).",
        pass_criteria="variant_damage < baseline_damage",
        max_ticks=PIPELINE_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["pipeline", "full-chain", "regen", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_50DMG
    baseline_target_ship = "Test_Target_Pipeline_Full.json"
    variant_attacker_ship = ATTACKER_50DMG
    variant_target_ship = "Test_Target_Pipeline_Full_Regen.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Outcome: regen variant takes less damage
        checks.append(check_true(
            "Regen Reduced Hull Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# PIPELINE-007: SRA Cap Overflow With High-Damage Beam
# =============================================================================

class PipelineSRAOverflowScenario(ComparisonScenario):
    """
    PIPELINE-007: SRA Cap Overflow (High-Damage Beam)

    Tests that when damage exceeds shield + SRA absorption, the remainder
    leaks through to hull.

    Baseline: shield(10) only
    Variant:  shield(10) + SRA(15)
    Attacker: 30 dmg/hit beam

    Per hit analysis:
    - Baseline: shield absorbs min(10, current), rest hits hull.
      First hit: shield absorbs 10, 20 to hull. Shield now at 0.
      Subsequent hits: 30 to hull each.

    - Variant: shield absorbs min(10, current), emissive=0, SRA absorbs
      min(15, overflow) and recharges min(max_shields - current, absorbed).
      First hit: shield absorbs 10, overflow 20, SRA absorbs 15 (recharges
      min(10, 0+15)=10 shields), 5 to hull.
      Second hit: shield absorbs 10, overflow 20, SRA absorbs 15 (recharges
      10), 5 to hull. Repeating cycle.

    So variant should take ~5/hit vs baseline ~30/hit (after first hit).
    Variant definitely takes damage, but much less than baseline.
    """

    metadata = TestMetadata(
        test_id="PIPELINE-007",
        category="DamagePipeline",
        subcategory="Overflow",
        name="SRA Cap Overflow With High-Damage Beam",
        summary="High-damage beam overflows SRA, but SRA still reduces total hull damage",
        conditions=[
            f"Attacker: {ATTACKER_30DMG} (30 dmg, guaranteed hit, fires every tick)",
            "Baseline target: shield(10) only",
            f"Variant target: shield(10) + SRA({SRA_VALUE})",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {PIPELINE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "30 dmg/hit exceeds shield(10) + SRA(15) total absorption",
            "SRA recharges shields but overflow still leaks to hull",
            "SRA wastes recharge when shield is already at max capacity",
        ],
        expected_outcome="Variant takes damage (SRA can't block all) but less than baseline.",
        pass_criteria="variant_damage > 0 AND variant_damage < baseline_damage",
        max_ticks=PIPELINE_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["pipeline", "sra", "overflow", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_30DMG
    baseline_target_ship = "Test_Target_Pipeline_Shield10_Only.json"
    variant_attacker_ship = ATTACKER_30DMG
    variant_target_ship = "Test_Target_SRA_SmallShield.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline took substantial hull damage
        checks.append(check_true(
            "Baseline Took Hull Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: variant also took damage (SRA can't block everything)
        checks.append(check_true(
            "Variant Took Hull Damage (Overflow)",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt} (SRA can't absorb all 30 dmg/hit)",
            phase="outcome",
        ))

        # Outcome: variant took less damage than baseline
        checks.append(check_true(
            "SRA Reduced Hull Damage Despite Overflow",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: variant should take roughly 1/6 of baseline damage
        # (baseline ~30/hit, variant ~5/hit after first cycle)
        # Use a generous bound: variant < 50% of baseline
        checks.append(check_true(
            "SRA Reduced Damage Substantially",
            self.variant_damage_dealt < self.baseline_damage_dealt * 0.50,
            detail=(
                f"variant={self.variant_damage_dealt}, "
                f"threshold={self.baseline_damage_dealt * 0.50:.0f} (50% of baseline)"
            ),
            phase="outcome",
        ))

        return checks
