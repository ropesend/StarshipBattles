"""
Consumption Multiplier Modifier Test Scenarios (MOD-CONSUME-001 to MOD-CONSUME-004)

These tests validate that the consumption_mult modifier correctly reduces
per-shot resource costs for weapons:
- MOD-CONSUME-001: Modified weapon fires and deals damage (smoke test)
- MOD-CONSUME-002: Modified weapon deals ~2x more damage than unmodified
- MOD-CONSUME-003: Modified weapon fires ~2x more shots than unmodified
- MOD-CONSUME-004: Consumption increase (2x) — weapon fires fewer shots

Key Mechanics:
- test_consumption_reduction modifier: consumption_mult *= param (0.5)
- Base weapon: test_beam_rapid_1dmg_energy_consumption (10 energy/shot, damage=1, reload=0)
- Storage: test_storage_energy_250 (250 energy)
- Base: 250 / 10 = 25 shots before depletion
- Modified (0.5x): 250 / 5 = 50 shots before depletion

Ship Files:
- Test_Attacker_Beam_ConsumptionReduction.json — test_beam_rapid_1dmg_energy_consumption (10 energy/shot) + test_consumption_reduction (value=0.5) + test_storage_energy_250
- Test_Attacker_Beam_ConsumptionBase.json — test_beam_rapid_1dmg_energy_consumption (10 energy/shot) + test_storage_energy_250 (no modifier)
- Test_Attacker_Beam_ConsumptionIncrease.json — test_beam_rapid_1dmg_energy_consumption (10 energy/shot) + test_consumption_increase (value=2) + test_storage_energy_250
- Test_Target_Stationary.json — test_armor_extreme_hp (1B HP, stationary)
"""

from combat_lab.scenarios import TestMetadata
from combat_lab.scenarios.templates import StaticTargetScenario, ComparisonScenario
from combat_lab.scenarios.validation import check_exact, check_approx, check_true


# =============================================================================
# EXPECTED VALUES FOR CONSUMPTION MODIFIER TESTS
# =============================================================================

# Shared constants
TARGET_SHIP = "Test_Target_Stationary.json"
DISTANCE = 100
MAX_TICKS = 500
SEED = 42

# Base weapon stats
BASE_ENERGY_PER_SHOT = 10
DAMAGE_PER_HIT = 1
INITIAL_ENERGY = 250.0

# Derived expectations
BASE_EXPECTED_SHOTS = int(INITIAL_ENERGY / BASE_ENERGY_PER_SHOT)  # 25
MODIFIER_PARAM = 0.5
MODIFIED_ENERGY_PER_SHOT = BASE_ENERGY_PER_SHOT * MODIFIER_PARAM  # 5.0
MODIFIED_EXPECTED_SHOTS = int(INITIAL_ENERGY / MODIFIED_ENERGY_PER_SHOT)  # 50

# Ship files
# test_beam_rapid_1dmg_energy_consumption (10 energy/shot) + test_storage_energy_250 (no modifier)
BASE_SHIP = "Test_Attacker_Beam_ConsumptionBase.json"
# test_beam_rapid_1dmg_energy_consumption (10 energy/shot) + test_consumption_reduction (value=0.5) + test_storage_energy_250
MODIFIED_SHIP = "Test_Attacker_Beam_ConsumptionReduction.json"


# ============================================================================
# MOD-CONSUME-001: SMOKE TEST — MODIFIED WEAPON FIRES AND DEALS DAMAGE
# ============================================================================

class ConsumptionModifierSmokeScenario(StaticTargetScenario):
    """
    MOD-CONSUME-001: Consumption Modifier Smoke Test

    Verifies that a weapon with a 0.5x consumption modifier fires and deals
    damage. The modified weapon should fire more than 25 shots (unmodified
    limit) as proof that the modifier is active.
    """

    metadata = TestMetadata(
        test_id="MOD-CONSUME-001",
        category="ConsumptionMultiplier",
        subcategory="ConsumptionMultiplier",
        name="Consumption Modifier Smoke Test",
        summary="Weapon with 0.5x consumption modifier fires and deals damage beyond unmodified limit",
        conditions=[
            f"Attacker: {MODIFIED_SHIP} (test_beam_rapid_1dmg_energy_consumption {BASE_ENERGY_PER_SHOT} energy/shot + test_consumption_reduction value={MODIFIER_PARAM} + test_storage_energy_250)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Modified energy cost: {MODIFIED_ENERGY_PER_SHOT}/shot ({BASE_ENERGY_PER_SHOT} * {MODIFIER_PARAM})",
            f"Distance: {DISTANCE}px (point blank)",
        ],
        edge_cases=[
            f"Unmodified weapon would fire {BASE_EXPECTED_SHOTS} shots",
            f"Modified weapon should fire {MODIFIED_EXPECTED_SHOTS} shots",
            "Modifier applied via consumption_mult formula",
        ],
        expected_outcome=f"Weapon fires ~{MODIFIED_EXPECTED_SHOTS} shots, dealing ~{MODIFIED_EXPECTED_SHOTS} damage",
        pass_criteria=f"damage_dealt > {BASE_EXPECTED_SHOTS} (proves modifier is active)",
        max_ticks=MAX_TICKS,
        seed=SEED,
        tags=["modifier", "consumption_mult"],
    )

    attacker_ship = MODIFIED_SHIP
    target_ship = TARGET_SHIP
    distance = DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        shots_fired = self.results.get('attacker_total_shots_fired', 0)

        # Data: verify initial energy
        energy_res = self.attacker.resources.get_resource("energy")
        initial_energy = energy_res.max_value if energy_res else 0
        checks.append(check_exact(
            "Initial Energy", INITIAL_ENERGY, initial_energy,
        ))

        # Precondition: weapon fired
        checks.append(check_true(
            "Weapon Fired",
            shots_fired > 0,
            detail=f"shots_fired={shots_fired}",
        ))

        # Precondition: damage dealt
        checks.append(check_true(
            "Damage Dealt",
            self.damage_dealt > 0,
            detail=f"damage_dealt={self.damage_dealt}",
        ))

        # Outcome: modifier is active — damage near expected modified shot count
        checks.append(check_approx(
            "Damage Near Modified Expectation", float(MODIFIED_EXPECTED_SHOTS),
            float(self.damage_dealt), tolerance=5,
            phase="outcome",
        ))

        return checks


# ============================================================================
# MOD-CONSUME-002: COMPARISON — MODIFIED DEALS MORE DAMAGE
# ============================================================================

class ConsumptionModifierDamageComparisonScenario(ComparisonScenario):
    """
    MOD-CONSUME-002: Consumption Modifier Doubles Damage Output

    Compares baseline (no modifier, 10 energy/shot) vs variant (0.5x modifier,
    5 energy/shot). Both start with 250 energy. Baseline fires ~25 shots,
    variant fires ~50 shots. With damage=1 per hit at point blank, variant
    should deal approximately 2x the damage.
    """

    metadata = TestMetadata(
        test_id="MOD-CONSUME-002",
        category="ConsumptionMultiplier",
        subcategory="ConsumptionMultiplier",
        name="Consumption Modifier Doubles Damage",
        summary="0.5x consumption modifier allows weapon to fire longer, dealing ~2x damage",
        conditions=[
            f"Baseline: {BASE_SHIP} (test_beam_rapid_1dmg_energy_consumption {BASE_ENERGY_PER_SHOT} energy/shot + test_storage_energy_250, no modifier)",
            f"Variant: {MODIFIED_SHIP} (test_beam_rapid_1dmg_energy_consumption + test_consumption_reduction value={MODIFIER_PARAM} + test_storage_energy_250)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Baseline: {INITIAL_ENERGY} / {BASE_ENERGY_PER_SHOT} = ~{BASE_EXPECTED_SHOTS} shots; Variant: {INITIAL_ENERGY} / {MODIFIED_ENERGY_PER_SHOT} = ~{MODIFIED_EXPECTED_SHOTS} shots",
            f"Distance: {DISTANCE}px (point blank)",
        ],
        edge_cases=[
            "Both ships identical except for consumption modifier",
            "At point blank, beam accuracy is 100% — damage == shots fired",
            "Energy fully depletes for both ships within test duration",
        ],
        expected_outcome=f"Baseline ~{BASE_EXPECTED_SHOTS} damage, Variant ~{MODIFIED_EXPECTED_SHOTS} damage",
        pass_criteria="variant_damage ≈ 2x baseline_damage",
        max_ticks=MAX_TICKS,
        seed=SEED,
        tags=["modifier", "consumption_mult", "comparison"],
    )

    baseline_attacker_ship = BASE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = MODIFIED_SHIP
    variant_target_ship = TARGET_SHIP
    distance = DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both battles dealt damage
        checks.append(check_true(
            "Baseline Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"baseline_damage={self.baseline_damage_dealt}",
        ))
        checks.append(check_true(
            "Variant Dealt Damage",
            self.variant_damage_dealt > 0,
            detail=f"variant_damage={self.variant_damage_dealt}",
        ))

        # Outcome: baseline damage ≈ 25
        checks.append(check_approx(
            "Baseline Damage", BASE_EXPECTED_SHOTS, self.baseline_damage_dealt,
            tolerance=2, phase="outcome",
        ))

        # Outcome: variant damage ≈ 50
        checks.append(check_approx(
            "Variant Damage", MODIFIED_EXPECTED_SHOTS, self.variant_damage_dealt,
            tolerance=2, phase="outcome",
        ))

        # Outcome: variant dealt more damage than baseline
        checks.append(check_true(
            "Variant Deals More Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        return checks


# ============================================================================
# MOD-CONSUME-003: COMPARISON — MODIFIED FIRES MORE SHOTS
# ============================================================================

class ConsumptionModifierShotsComparisonScenario(ComparisonScenario):
    """
    MOD-CONSUME-003: Consumption Modifier Doubles Shots Fired

    Same setup as MOD-CONSUME-002 but explicitly checks shot counts.
    Baseline fires ~25 shots (250 energy / 10 per shot), variant fires
    ~50 shots (250 energy / 5 per shot). Variant should fire ~2x shots.
    """

    metadata = TestMetadata(
        test_id="MOD-CONSUME-003",
        category="ConsumptionMultiplier",
        subcategory="ConsumptionMultiplier",
        name="Consumption Modifier Doubles Shots Fired",
        summary="0.5x consumption modifier allows weapon to fire ~2x more shots before energy depletion",
        conditions=[
            f"Baseline: {BASE_SHIP} (test_beam_rapid_1dmg_energy_consumption {BASE_ENERGY_PER_SHOT} energy/shot + test_storage_energy_250, no modifier)",
            f"Variant: {MODIFIED_SHIP} (test_beam_rapid_1dmg_energy_consumption + test_consumption_reduction value={MODIFIER_PARAM} + test_storage_energy_250)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Baseline: {INITIAL_ENERGY} / {BASE_ENERGY_PER_SHOT} = ~{BASE_EXPECTED_SHOTS} shots; Variant: {INITIAL_ENERGY} / {MODIFIED_ENERGY_PER_SHOT} = ~{MODIFIED_EXPECTED_SHOTS} shots",
            f"Distance: {DISTANCE}px (point blank)",
        ],
        edge_cases=[
            "Shot count measured via per-weapon stats (shots_fired)",
            "Both weapons have reload=0 (fire every tick while energy available)",
            "Energy depletion is the only limiting factor",
        ],
        expected_outcome=f"Baseline ~{BASE_EXPECTED_SHOTS} shots, Variant ~{MODIFIED_EXPECTED_SHOTS} shots",
        pass_criteria=f"variant_shots ≈ 2x baseline_shots",
        max_ticks=MAX_TICKS,
        seed=SEED,
        tags=["modifier", "consumption_mult", "comparison"],
    )

    baseline_attacker_ship = BASE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = MODIFIED_SHIP
    variant_target_ship = TARGET_SHIP
    distance = DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)

        # Precondition: both fired
        checks.append(check_true(
            "Baseline Fired",
            baseline_shots > 0,
            detail=f"baseline_shots={baseline_shots}",
        ))
        checks.append(check_true(
            "Variant Fired",
            variant_shots > 0,
            detail=f"variant_shots={variant_shots}",
        ))

        # Outcome: baseline shots ≈ 25
        checks.append(check_approx(
            "Baseline Shots", BASE_EXPECTED_SHOTS, baseline_shots,
            tolerance=2, phase="outcome",
        ))

        # Outcome: variant shots ≈ 50
        checks.append(check_approx(
            "Variant Shots", MODIFIED_EXPECTED_SHOTS, variant_shots,
            tolerance=2, phase="outcome",
        ))

        # Outcome: variant fired more shots
        checks.append(check_true(
            "Variant Fires More Shots",
            variant_shots > baseline_shots,
            detail=f"variant={variant_shots}, baseline={baseline_shots}",
            phase="outcome",
        ))

        # Outcome: ratio ≈ 2x
        ratio = variant_shots / baseline_shots if baseline_shots > 0 else 0
        checks.append(check_approx(
            "Shot Ratio (~2x)", 2.0, ratio,
            tolerance=0.2, phase="outcome",
        ))

        return checks


# ============================================================================
# MOD-CONSUME-004: CONSUMPTION INCREASE — WEAPON FIRES FEWER SHOTS
# ============================================================================

# Consumption increase constants
INCREASE_MODIFIER_PARAM = 2
INCREASED_ENERGY_PER_SHOT = BASE_ENERGY_PER_SHOT * INCREASE_MODIFIER_PARAM  # 20.0
INCREASED_EXPECTED_SHOTS = int(INITIAL_ENERGY / INCREASED_ENERGY_PER_SHOT)  # 12
INCREASED_SHIP = "Test_Attacker_Beam_ConsumptionIncrease.json"


class ConsumptionIncreaseScenario(ComparisonScenario):
    """
    MOD-CONSUME-004: Consumption increase — weapon fires fewer shots.

    Compares baseline (no modifier, 10 energy/shot, ~25 shots) vs variant
    (2x consumption modifier, 20 energy/shot, ~12 shots). Both start with
    250 energy. The increased consumption means the variant fires roughly
    half the shots.
    """

    metadata = TestMetadata(
        test_id="MOD-CONSUME-004",
        category="ConsumptionMultiplier",
        subcategory="ConsumptionMultiplier",
        name="Consumption Increase — weapon fires fewer shots",
        summary="2x consumption modifier doubles energy cost, halving shots fired (~12 vs ~25)",
        conditions=[
            f"Baseline: {BASE_SHIP} (test_beam_rapid_1dmg_energy_consumption {BASE_ENERGY_PER_SHOT} energy/shot + test_storage_energy_250, no modifier)",
            f"Variant: {INCREASED_SHIP} (test_beam_rapid_1dmg_energy_consumption + test_consumption_increase value={INCREASE_MODIFIER_PARAM} + test_storage_energy_250)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Baseline: {INITIAL_ENERGY} / {BASE_ENERGY_PER_SHOT} = ~{BASE_EXPECTED_SHOTS} shots; Variant: {INITIAL_ENERGY} / {INCREASED_ENERGY_PER_SHOT} = ~{INCREASED_EXPECTED_SHOTS} shots",
            f"Distance: {DISTANCE}px (point blank)",
        ],
        edge_cases=[
            "Both ships identical except for consumption modifier",
            "250 / 20 = 12.5 — fractional shot means ~12 full shots",
            "Penalty modifier increases cost rather than reducing it",
        ],
        expected_outcome=f"Baseline ~{BASE_EXPECTED_SHOTS} damage, Variant ~{INCREASED_EXPECTED_SHOTS} damage",
        pass_criteria=f"variant_damage < baseline_damage AND variant_damage ≈ {INCREASED_EXPECTED_SHOTS} AND baseline_damage ≈ {BASE_EXPECTED_SHOTS}",
        max_ticks=MAX_TICKS,
        seed=SEED,
        tags=["modifier", "consumption_mult", "penalty"],
    )

    baseline_attacker_ship = BASE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = INCREASED_SHIP
    variant_target_ship = TARGET_SHIP
    distance = DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both dealt damage
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

        # Outcome: variant deals less damage than baseline
        checks.append(check_true(
            "Variant Deals Less Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: variant damage ≈ 12 (250 / 20 = 12.5, truncated to ~12)
        checks.append(check_approx(
            "Variant Damage", float(INCREASED_EXPECTED_SHOTS),
            float(self.variant_damage_dealt), tolerance=3,
            phase="outcome",
        ))

        # Outcome: baseline damage ≈ 25
        checks.append(check_approx(
            "Baseline Damage", float(BASE_EXPECTED_SHOTS),
            float(self.baseline_damage_dealt), tolerance=3,
            phase="outcome",
        ))

        return checks


# ============================================================================
# EXPORT ALL SCENARIOS
# ============================================================================

__all__ = [
    'ConsumptionModifierSmokeScenario',
    'ConsumptionModifierDamageComparisonScenario',
    'ConsumptionModifierShotsComparisonScenario',
    'ConsumptionIncreaseScenario',
]
