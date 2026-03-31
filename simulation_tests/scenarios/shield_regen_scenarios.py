"""
ShieldRegeneration Test Scenarios (SHIELD-REGEN-001 to SHIELD-REGEN-006)

These tests validate the ShieldRegeneration ability using A/B comparison
battles.  Each test compares a target with shield regen against a baseline
to prove the regeneration caused the observed difference.

ShieldRegeneration is passive: every tick, if current_shields < max_shields
and shield_regen_rate > 0, the ship regenerates (rate / 100) HP per tick.
If a ResourceConsumption ability is attached, energy is consumed per tick
and regen only occurs when energy is available.

Stacking: all ShieldRegeneration abilities sum their rates additively.
Two 10/sec components = 20/sec total.

All tests use a guaranteed-hit beam (base_accuracy=10.0, falloff=0) for
deterministic damage counts (1 damage per tick = 100 damage per second).

Expected behaviors:
- Regen extends shield life, reducing hull damage vs no-regen baseline
- Regen rate > damage rate → hull takes zero damage
- Multiple regen components stack additively
- Resource-dependent regen stops when energy depletes
"""

from simulation_tests.scenarios import TestMetadata
from simulation_tests.scenarios.templates import ComparisonScenario
from simulation_tests.scenarios.validation import check_exact, check_true
from simulation_tests.test_constants import (
    POINT_BLANK_DISTANCE,
    STANDARD_SEED,
    SHIELD_CAPACITY,
    SHIELD_REGEN_RATE,
    SHIELD_REGEN_TEST_TICKS,
    SHIELD_REGEN_RATE_200,
    SHIELD_REGEN_RATE_5,
    SHIELD_REGEN_ENERGY_COST,
    SHIELD_REGEN_SMALL_BATTERY,
)


# =============================================================================
# COMMON SHIP REFERENCES
# =============================================================================

REGEN_ATTACKER = "Test_Attacker_Beam_Guaranteed.json"
UNSHIELDED_TARGET = "Test_Target_Stationary.json"


# =============================================================================
# SHIELD-REGEN-001: Regen Reduces Net Damage
# =============================================================================

class RegenReducesNetDamageScenario(ComparisonScenario):
    """
    SHIELD-REGEN-001: Regen Reduces Net Damage

    Battle A: Target with 200 HP shield, NO regen → shield depletes after 200 ticks
    Battle B: Target with 200 HP shield + 10/sec regen → shield lasts longer

    At 1 dmg/tick, net shield drain with regen = 1 - 0.1 = 0.9/tick.
    Shield lasts ~222 ticks (vs 200 without regen), so variant takes ~22
    fewer hull hits.
    """

    metadata = TestMetadata(
        test_id="SHIELD-REGEN-001",
        category="ShieldRegeneration",
        subcategory="Basic Effect",
        name="Regen Reduces Net Damage",
        summary="Shield regen extends shield life, reducing hull damage",
        conditions=[
            f"Attacker: {REGEN_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            "Target (no regen): Test_Target_Shield_NoRegen.json (200 HP shield, extreme armor)",
            "Target (with regen): Test_Target_Shield_Regen.json (200 HP shield + 10/sec regen)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels (point blank)",
            f"Test Duration: {SHIELD_REGEN_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Regen rate (10/sec = 0.1/tick) is less than damage rate (1/tick)",
            "Shield still depletes, but later than without regen",
        ],
        expected_outcome="Variant takes less hull damage than baseline because regen "
                         "extends shield life by ~22 ticks.",
        pass_criteria="variant_damage_dealt < baseline_damage_dealt",
        max_ticks=SHIELD_REGEN_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["shield", "regen", "shield-regeneration", "comparison"],
    )

    baseline_attacker_ship = REGEN_ATTACKER
    baseline_target_ship = "Test_Target_Shield_NoRegen.json"
    variant_attacker_ship = REGEN_ATTACKER
    variant_target_ship = "Test_Target_Shield_Regen.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify shield capacity on both targets
        checks.append(check_exact(
            "Shield Capacity", float(SHIELD_CAPACITY),
            self.target.max_shields,
        ))

        # Data: verify regen rate on variant
        checks.append(check_true(
            "Variant Has Regen",
            self.target.shield_regen_rate > 0,
            detail=f"regen_rate={self.target.shield_regen_rate}",
        ))

        # Precondition: baseline took hull damage
        checks.append(check_true(
            "Baseline Took Hull Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Precondition: variant also took hull damage (regen < damage rate)
        checks.append(check_true(
            "Variant Took Hull Damage",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
        ))

        # Outcome: regen reduced hull damage
        checks.append(check_true(
            "Regen Reduced Hull Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: quantify the benefit — should be ~22 fewer hits
        damage_reduction = self.baseline_damage_dealt - self.variant_damage_dealt
        checks.append(check_true(
            "Damage Reduction > 0",
            damage_reduction > 0,
            detail=f"reduction={damage_reduction}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# SHIELD-REGEN-002: Regen Exceeds Damage — Hull Takes Zero
# =============================================================================

class RegenExceedsDamageScenario(ComparisonScenario):
    """
    SHIELD-REGEN-002: Regen Exceeds Damage — Hull Takes Zero

    Battle A: Unshielded target → all hits damage armor
    Battle B: Target with 200 HP shield + 200/sec regen → regen outpaces damage

    At 1 dmg/tick, regen = 2.0/tick > damage. Shields never deplete,
    hull takes zero damage.
    """

    metadata = TestMetadata(
        test_id="SHIELD-REGEN-002",
        category="ShieldRegeneration",
        subcategory="Basic Effect",
        name="Regen Exceeds Damage — Hull Takes Zero",
        summary="When regen outpaces incoming damage, hull is never touched",
        conditions=[
            f"Attacker: {REGEN_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            f"Target (no shield): {UNSHIELDED_TARGET} (extreme armor only)",
            "Target (high regen): Test_Target_Shield_Regen_200.json "
            f"(200 HP shield + {SHIELD_REGEN_RATE_200}/sec regen)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels (point blank)",
            f"Test Duration: {SHIELD_REGEN_TEST_TICKS} ticks",
        ],
        edge_cases=[
            f"Regen rate ({SHIELD_REGEN_RATE_200}/sec = 2.0/tick) exceeds damage rate (1/tick)",
            "Shields should never fully deplete",
        ],
        expected_outcome="Variant takes zero hull damage. Shields remain above zero.",
        pass_criteria="variant_damage_dealt == 0, shields still up",
        max_ticks=SHIELD_REGEN_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["shield", "regen", "zero-damage", "shield-regeneration", "comparison"],
    )

    baseline_attacker_ship = REGEN_ATTACKER
    baseline_target_ship = UNSHIELDED_TARGET
    variant_attacker_ship = REGEN_ATTACKER
    variant_target_ship = "Test_Target_Shield_Regen_200.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline took damage (proves beam is firing)
        checks.append(check_true(
            "Baseline Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: variant hull took zero damage
        checks.append(check_exact(
            "Zero Hull Damage", 0.0, self.variant_damage_dealt,
            phase="outcome",
        ))

        # Outcome: shields still up
        checks.append(check_true(
            "Shields Still Active",
            self.target.current_shields > 0,
            detail=f"shields={self.target.current_shields}/{self.target.max_shields}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# SHIELD-REGEN-003: Stacking — Two Regen Components Sum
# =============================================================================

class RegenStackingScenario(ComparisonScenario):
    """
    SHIELD-REGEN-003: Stacking — Two Regen Components Sum

    Battle A: Target with 200 HP shield + 1x regen (10/sec)
    Battle B: Target with 200 HP shield + 2x regen (10/sec each = 20/sec total)

    1x regen: net drain = 1 - 0.1 = 0.9/tick, shield lasts ~222 ticks
    2x regen: net drain = 1 - 0.2 = 0.8/tick, shield lasts ~250 ticks
    Variant should take ~28 fewer hull hits.
    """

    metadata = TestMetadata(
        test_id="SHIELD-REGEN-003",
        category="ShieldRegeneration",
        subcategory="Stacking",
        name="Two Regen Components Stack Additively",
        summary="Two regen components sum their rates, providing more protection",
        conditions=[
            f"Attacker: {REGEN_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            "Target (1x regen): Test_Target_Shield_Regen.json (200 HP shield + 10/sec regen)",
            "Target (2x regen): Test_Target_Shield_Regen_2x.json (200 HP shield + 2x 10/sec regen)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels (point blank)",
            f"Test Duration: {SHIELD_REGEN_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Both regen components are the same type (test_shield_regen_10)",
            "Total regen = 20/sec, still less than 100 damage/sec from beam",
        ],
        expected_outcome="2x regen variant takes less hull damage than 1x regen baseline.",
        pass_criteria="variant_damage_dealt < baseline_damage_dealt",
        max_ticks=SHIELD_REGEN_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["shield", "regen", "stacking", "shield-regeneration", "comparison"],
    )

    baseline_attacker_ship = REGEN_ATTACKER
    baseline_target_ship = "Test_Target_Shield_Regen.json"
    variant_attacker_ship = REGEN_ATTACKER
    variant_target_ship = "Test_Target_Shield_Regen_2x.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify variant has double regen rate
        checks.append(check_exact(
            "Variant Regen Rate", SHIELD_REGEN_RATE * 2,
            self.target.shield_regen_rate,
        ))

        # Precondition: both took hull damage
        checks.append(check_true(
            "Baseline Took Hull Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))
        checks.append(check_true(
            "Variant Took Hull Damage",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
        ))

        # Outcome: 2x regen = less hull damage
        checks.append(check_true(
            "2x Regen Reduced Hull Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# SHIELD-REGEN-004: Resource — Full Energy (Control)
# =============================================================================

class RegenWithFullEnergyScenario(ComparisonScenario):
    """
    SHIELD-REGEN-004: Resource — Full Energy (Control)

    Battle A: Target with shield + energy-cost regen (5/sec, 5 energy/sec)
              + large battery (100k energy, lasts far beyond test)
    Battle B: Target with shield + free regen (5/sec, no cost)

    With sufficient energy, powered regen should perform identically to
    free regen. Both should produce the same hull damage.
    """

    metadata = TestMetadata(
        test_id="SHIELD-REGEN-004",
        category="ShieldRegeneration",
        subcategory="Resource Consumption",
        name="Regen With Full Energy (Control)",
        summary="Energy-powered regen with sufficient battery performs like free regen",
        conditions=[
            f"Attacker: {REGEN_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            "Target (powered regen): Test_Target_Shield_Regen_Energy.json "
            f"(200 HP shield + {SHIELD_REGEN_RATE_5}/sec regen @ {SHIELD_REGEN_ENERGY_COST} energy/sec + 100k battery)",
            "Target (free regen): Test_Target_Shield_Regen_5_Free.json "
            f"(200 HP shield + {SHIELD_REGEN_RATE_5}/sec regen, no cost)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels (point blank)",
            f"Test Duration: {SHIELD_REGEN_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Battery has far more energy than needed — regen never interrupted",
        ],
        expected_outcome="Both targets take the same hull damage (powered regen = free regen).",
        pass_criteria="baseline_damage_dealt == variant_damage_dealt",
        max_ticks=SHIELD_REGEN_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["shield", "regen", "energy", "resource", "shield-regeneration", "comparison"],
    )

    baseline_attacker_ship = REGEN_ATTACKER
    baseline_target_ship = "Test_Target_Shield_Regen_Energy.json"
    variant_attacker_ship = REGEN_ATTACKER
    variant_target_ship = "Test_Target_Shield_Regen_5_Free.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: both targets have same regen rate
        checks.append(check_exact(
            "Variant Regen Rate", SHIELD_REGEN_RATE_5,
            self.target.shield_regen_rate,
        ))

        # Precondition: both took damage (regen < damage rate)
        checks.append(check_true(
            "Baseline Took Hull Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: identical damage (powered with full energy = free)
        checks.append(check_exact(
            "Same Hull Damage",
            self.baseline_damage_dealt, self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# SHIELD-REGEN-005: Resource — No Energy (Regen Disabled)
# =============================================================================

class RegenWithNoEnergyScenario(ComparisonScenario):
    """
    SHIELD-REGEN-005: Resource — No Energy (Regen Disabled)

    Battle A: Target with shield + energy-cost regen + NO battery
    Battle B: Target with shield + NO regen at all

    Without energy, the regen component cannot function. Both targets
    should take the same hull damage, proving energy-starved regen = no regen.
    """

    metadata = TestMetadata(
        test_id="SHIELD-REGEN-005",
        category="ShieldRegeneration",
        subcategory="Resource Consumption",
        name="Regen Without Energy Is Disabled",
        summary="Energy-starved regen provides no benefit — same damage as no regen",
        conditions=[
            f"Attacker: {REGEN_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            "Target (no battery): Test_Target_Shield_Regen_NoBattery.json "
            f"(200 HP shield + {SHIELD_REGEN_RATE_5}/sec regen @ {SHIELD_REGEN_ENERGY_COST} energy/sec, NO battery)",
            "Target (no regen): Test_Target_Shield_NoRegen.json (200 HP shield, no regen)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels (point blank)",
            f"Test Duration: {SHIELD_REGEN_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Regen component exists but has no energy to operate",
        ],
        expected_outcome="Both targets take the same hull damage.",
        pass_criteria="baseline_damage_dealt == variant_damage_dealt",
        max_ticks=SHIELD_REGEN_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["shield", "regen", "energy", "starved", "shield-regeneration", "comparison"],
    )

    baseline_attacker_ship = REGEN_ATTACKER
    baseline_target_ship = "Test_Target_Shield_Regen_NoBattery.json"
    variant_attacker_ship = REGEN_ATTACKER
    variant_target_ship = "Test_Target_Shield_NoRegen.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both took hull damage
        checks.append(check_true(
            "Baseline Took Hull Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: energy-starved regen = no regen (same damage)
        checks.append(check_exact(
            "Same Hull Damage (Starved = No Regen)",
            self.baseline_damage_dealt, self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# SHIELD-REGEN-006: Resource — Half Energy (Regen Stops Mid-Battle)
# =============================================================================

class RegenStopsMidBattleScenario(ComparisonScenario):
    """
    SHIELD-REGEN-006: Resource — Half Energy (Regen Stops Mid-Battle)

    Battle A: Target with shield + regen + large battery (energy lasts full test)
    Battle B: Target with shield + regen + small battery (energy depletes ~halfway)

    The small battery (25 energy at 5 energy/sec cost) lasts ~500 ticks.
    In a 1000-tick test, the variant loses regen at tick ~500, taking more
    hull damage in the second half.
    """

    metadata = TestMetadata(
        test_id="SHIELD-REGEN-006",
        category="ShieldRegeneration",
        subcategory="Resource Consumption",
        name="Regen Stops When Energy Depletes Mid-Battle",
        summary="Limited battery causes regen to stop mid-battle, increasing hull damage",
        conditions=[
            f"Attacker: {REGEN_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            "Target (full battery): Test_Target_Shield_Regen_Energy.json "
            f"(200 HP shield + {SHIELD_REGEN_RATE_5}/sec regen + 100k battery)",
            "Target (small battery): Test_Target_Shield_Regen_SmallBattery.json "
            f"(200 HP shield + {SHIELD_REGEN_RATE_5}/sec regen + {SHIELD_REGEN_SMALL_BATTERY} energy)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels (point blank)",
            "Test Duration: 1000 ticks (small battery depletes ~halfway)",
        ],
        edge_cases=[
            f"Small battery ({SHIELD_REGEN_SMALL_BATTERY} energy) runs out at ~tick 500",
            "Regen stops when energy depletes, shield drains faster afterward",
        ],
        expected_outcome="Variant takes more hull damage than baseline because regen "
                         "stops mid-battle when energy runs out.",
        pass_criteria="variant_damage_dealt > baseline_damage_dealt",
        max_ticks=1000,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["shield", "regen", "energy", "depletion", "shield-regeneration", "comparison"],
    )

    baseline_attacker_ship = REGEN_ATTACKER
    baseline_target_ship = "Test_Target_Shield_Regen_Energy.json"
    variant_attacker_ship = REGEN_ATTACKER
    variant_target_ship = "Test_Target_Shield_Regen_SmallBattery.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both took hull damage
        checks.append(check_true(
            "Baseline Took Hull Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))
        checks.append(check_true(
            "Variant Took Hull Damage",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
        ))

        # Precondition: variant's energy depleted
        variant_energy = self.target.resources.get_resource("energy")
        checks.append(check_true(
            "Variant Energy Depleted",
            variant_energy is not None and variant_energy.current_value < 1.0,
            detail=f"energy={variant_energy.current_value if variant_energy else 'N/A'}",
        ))

        # Outcome: variant took more damage (regen stopped mid-battle)
        checks.append(check_true(
            "Energy Depletion Increased Hull Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        return checks
