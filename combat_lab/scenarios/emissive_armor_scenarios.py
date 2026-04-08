"""
EmissiveArmor Test Scenarios (EMISSIVE-001 to EMISSIVE-005)

These tests validate the EmissiveArmor ability using A/B comparison
battles. EmissiveArmor provides flat damage reduction per hit on
damage that overflows past shields.

Damage pipeline: Shields → EmissiveArmor → ShieldRegeneratingArmor → Hull.

Stacking: intra-group MAX, inter-group SUM (standard ability stacking).
Two EmissiveArmor(5) in the same stack_group = MAX(5,5) = 5.
Two EmissiveArmor(5) in different stack_groups = SUM(5,5) = 10.

All tests use guaranteed-hit beams for deterministic damage counts.

Expected behaviors:
- Low damage (≤ armor value) is completely blocked
- High damage (> armor value) is reduced by armor value
- Same-group stacking: MAX (no extra benefit)
- Different-group stacking: SUM (additive)
- Negative values reduce total armor (penalty)
"""

from combat_lab.scenarios import TestMetadata
from combat_lab.scenarios.templates import ComparisonScenario
from combat_lab.scenarios.validation import check_exact, check_true
from combat_lab.test_constants import (
    POINT_BLANK_DISTANCE,
    STANDARD_SEED,
    EMISSIVE_TEST_TICKS,
    EMISSIVE_ARMOR_VALUE,
    EMISSIVE_HIGH_BEAM_DAMAGE,
    EMISSIVE_EXACT_BEAM_DAMAGE,
)


# =============================================================================
# COMMON SHIP REFERENCES
# =============================================================================

ATTACKER_1DMG = "Test_Attacker_Beam_Guaranteed.json"
ATTACKER_10DMG = "Test_Attacker_Beam_10dmg_Guaranteed.json"
NO_ARMOR_TARGET = "Test_Target_Stationary.json"
EMISSIVE_TARGET = "Test_Target_EmissiveArmor.json"


# =============================================================================
# EMISSIVE-001: Blocks Low Damage Completely
# =============================================================================

class EmissiveBlocksLowDamageScenario(ComparisonScenario):
    """
    EMISSIVE-001: Blocks Low Damage Completely

    Battle A: Target without emissive armor — all 1-dmg hits land
    Battle B: Target with EmissiveArmor(5) — 1-dmg hits reduced to 0

    EmissiveArmor(5) subtracts 5 from each hit. A 1-damage beam hit
    becomes max(0, 1-5) = 0 damage. Target takes zero hull damage.
    """

    metadata = TestMetadata(
        test_id="EMISSIVE-001",
        category="EmissiveArmor",
        subcategory="Basic Effect",
        name="EmissiveArmor Blocks Low Damage",
        summary="EmissiveArmor(5) completely blocks 1-damage beam hits",
        conditions=[
            f"Attacker: {ATTACKER_1DMG} (1 dmg, guaranteed hit, fires every tick)",
            f"Target (no armor): {NO_ARMOR_TARGET} (extreme HP, no emissive armor)",
            f"Target (with armor): {EMISSIVE_TARGET} (EmissiveArmor {EMISSIVE_ARMOR_VALUE})",
            f"Distance: {POINT_BLANK_DISTANCE} pixels (point blank)",
            f"Test Duration: {EMISSIVE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            f"1 damage < {EMISSIVE_ARMOR_VALUE} armor → damage reduced to 0",
            "Target should take absolutely zero damage",
        ],
        expected_outcome="Variant takes zero damage. Baseline takes ~500 damage.",
        pass_criteria="variant_damage_dealt == 0, baseline_damage_dealt > 0",
        max_ticks=EMISSIVE_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["emissive-armor", "blocks", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_1DMG
    baseline_target_ship = NO_ARMOR_TARGET
    variant_attacker_ship = ATTACKER_1DMG
    variant_target_ship = EMISSIVE_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify emissive armor value
        checks.append(check_exact(
            "Emissive Armor Value", EMISSIVE_ARMOR_VALUE,
            self.target.emissive_armor,
        ))

        # Precondition: baseline took damage (beam fired)
        checks.append(check_true(
            "Baseline Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: variant took zero damage
        checks.append(check_exact(
            "Zero Damage With Armor", 0.0, self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# EMISSIVE-002: Reduces High Damage (Partial Reduction)
# =============================================================================

class EmissiveReducesHighDamageScenario(ComparisonScenario):
    """
    EMISSIVE-002: Reduces High Damage (Partial Reduction)

    Battle A: Target without emissive armor — all 10-dmg hits land fully
    Battle B: Target with EmissiveArmor(5) — each 10-dmg hit reduced to 5

    EmissiveArmor(5) subtracts 5 from each hit. A 10-damage beam hit
    becomes max(0, 10-5) = 5 damage. Target takes half the baseline damage.
    """

    metadata = TestMetadata(
        test_id="EMISSIVE-002",
        category="EmissiveArmor",
        subcategory="Basic Effect",
        name="EmissiveArmor Reduces High Damage",
        summary=f"EmissiveArmor({EMISSIVE_ARMOR_VALUE}) reduces {EMISSIVE_HIGH_BEAM_DAMAGE}-damage "
                f"hits by {EMISSIVE_ARMOR_VALUE}",
        conditions=[
            f"Attacker: {ATTACKER_10DMG} ({EMISSIVE_HIGH_BEAM_DAMAGE} dmg, guaranteed hit)",
            f"Target (no armor): {NO_ARMOR_TARGET} (extreme HP)",
            f"Target (with armor): {EMISSIVE_TARGET} (EmissiveArmor {EMISSIVE_ARMOR_VALUE})",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {EMISSIVE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            f"{EMISSIVE_HIGH_BEAM_DAMAGE} damage > {EMISSIVE_ARMOR_VALUE} armor → partial reduction",
            f"Each hit reduced by exactly {EMISSIVE_ARMOR_VALUE}",
        ],
        expected_outcome=f"Variant damage = baseline × "
                         f"({EMISSIVE_HIGH_BEAM_DAMAGE - EMISSIVE_ARMOR_VALUE}/{EMISSIVE_HIGH_BEAM_DAMAGE})",
        pass_criteria="variant_damage_dealt == baseline_damage_dealt / 2",
        max_ticks=EMISSIVE_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["emissive-armor", "reduction", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_10DMG
    baseline_target_ship = NO_ARMOR_TARGET
    variant_attacker_ship = ATTACKER_10DMG
    variant_target_ship = EMISSIVE_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify emissive armor and beam damage
        checks.append(check_exact(
            "Emissive Armor Value", EMISSIVE_ARMOR_VALUE,
            self.target.emissive_armor,
        ))

        # Precondition: baseline took damage
        checks.append(check_true(
            "Baseline Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Precondition: variant also took damage (armor < beam damage)
        checks.append(check_true(
            "Variant Took Damage",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
        ))

        # Outcome: exact damage ratio
        # Each hit: baseline = 10, variant = 10 - 5 = 5, ratio = 0.5
        expected_ratio = (EMISSIVE_HIGH_BEAM_DAMAGE - EMISSIVE_ARMOR_VALUE) / EMISSIVE_HIGH_BEAM_DAMAGE
        actual_ratio = self.variant_damage_dealt / self.baseline_damage_dealt
        checks.append(check_exact(
            "Damage Reduction Ratio",
            expected_ratio, actual_ratio,
            phase="outcome",
        ))

        return checks


# =============================================================================
# EMISSIVE-003: Same Group Does Not Stack
# =============================================================================

class EmissiveSameGroupNoStackScenario(ComparisonScenario):
    """
    EMISSIVE-003: Same Group Does Not Stack (Intra-Group MAX)

    Battle A: 1x EmissiveArmor(5, group_a) → 5 reduction
    Battle B: 2x EmissiveArmor(5, group_a) → MAX(5,5) = still 5

    Two components in the same stack_group produce the same protection
    as one. Both targets should take identical damage.
    """

    metadata = TestMetadata(
        test_id="EMISSIVE-003",
        category="EmissiveArmor",
        subcategory="Stacking",
        name="Same Group Does Not Stack",
        summary="Two EmissiveArmor in same stack_group = MAX (no extra benefit)",
        conditions=[
            f"Attacker: {ATTACKER_10DMG} ({EMISSIVE_HIGH_BEAM_DAMAGE} dmg, guaranteed hit)",
            "Target (1x armor): Test_Target_EmissiveArmor_GroupA.json (1x EmissiveArmor 5, group_a)",
            "Target (2x same group): Test_Target_EmissiveArmor_2x_SameGroup.json (2x EmissiveArmor 5, both group_a)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {EMISSIVE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Intra-group MAX: two identical values in same group = no extra benefit",
        ],
        expected_outcome="Both targets take identical damage (2x same group = 1x).",
        pass_criteria="baseline_damage_dealt == variant_damage_dealt",
        max_ticks=EMISSIVE_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["emissive-armor", "stacking", "same-group", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_10DMG
    baseline_target_ship = "Test_Target_EmissiveArmor_GroupA.json"
    variant_attacker_ship = ATTACKER_10DMG
    variant_target_ship = "Test_Target_EmissiveArmor_2x_SameGroup.json"
    distance = POINT_BLANK_DISTANCE
    expect_different_damage = False  # Same-group MAX means identical damage

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify both have same emissive armor value (MAX = 5)
        checks.append(check_exact(
            "Variant Emissive Armor", EMISSIVE_ARMOR_VALUE,
            self.target.emissive_armor,
        ))

        # Precondition: both took damage
        checks.append(check_true(
            "Baseline Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: identical damage (same group MAX = no extra benefit)
        checks.append(check_exact(
            "Same Damage (No Stack Benefit)",
            self.baseline_damage_dealt, self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# EMISSIVE-004: Different Groups Stack Additively
# =============================================================================

class EmissiveDiffGroupStackScenario(ComparisonScenario):
    """
    EMISSIVE-004: Different Groups Stack Additively (Inter-Group SUM)

    Battle A: 1x EmissiveArmor(5, group_a) → 5 reduction
    Battle B: EmissiveArmor(5, group_a) + EmissiveArmor(5, group_b) → SUM(5,5) = 10

    Two components in different stack_groups sum their values, providing
    double the protection.
    """

    metadata = TestMetadata(
        test_id="EMISSIVE-004",
        category="EmissiveArmor",
        subcategory="Stacking",
        name="Different Groups Stack Additively",
        summary="EmissiveArmor in different stack_groups SUM (double protection)",
        conditions=[
            f"Attacker: {ATTACKER_10DMG} ({EMISSIVE_HIGH_BEAM_DAMAGE} dmg, guaranteed hit)",
            "Target (1 group): Test_Target_EmissiveArmor_GroupA.json (EmissiveArmor 5, group_a)",
            "Target (2 groups): Test_Target_EmissiveArmor_2x_DiffGroup.json "
            "(EmissiveArmor 5 group_a + EmissiveArmor 5 group_b = 10 total)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {EMISSIVE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            f"Inter-group SUM: 5 + 5 = 10 total reduction",
            f"With {EMISSIVE_HIGH_BEAM_DAMAGE} dmg beam: 10 - 10 = 0 damage per hit",
        ],
        expected_outcome="Variant takes zero damage (10 armor = 10 damage beam). "
                         "Baseline takes reduced damage (5 armor vs 10 damage).",
        pass_criteria="variant_damage_dealt == 0, baseline_damage_dealt > 0",
        max_ticks=EMISSIVE_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["emissive-armor", "stacking", "diff-group", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_10DMG
    baseline_target_ship = "Test_Target_EmissiveArmor_GroupA.json"
    variant_attacker_ship = ATTACKER_10DMG
    variant_target_ship = "Test_Target_EmissiveArmor_2x_DiffGroup.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify variant has double emissive armor (SUM = 10)
        checks.append(check_exact(
            "Variant Emissive Armor (Stacked)",
            EMISSIVE_ARMOR_VALUE * 2,
            self.target.emissive_armor,
        ))

        # Precondition: baseline took damage (5 armor vs 10 damage = 5 per hit)
        checks.append(check_true(
            "Baseline Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: variant took zero damage (10 armor = 10 damage beam)
        checks.append(check_exact(
            "Variant Zero Damage (Full Block)",
            0.0, self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# EMISSIVE-005: Negative Value Reduces Protection
# =============================================================================

class EmissiveNegativeValueScenario(ComparisonScenario):
    """
    EMISSIVE-005: Negative Value Reduces Protection

    Battle A: EmissiveArmor(5, group_a) → 5 reduction
    Battle B: EmissiveArmor(5, group_a) + EmissiveArmor(-3, group_b) → SUM(5,-3) = 2

    A negative EmissiveArmor value in a different group reduces the total
    protection. Variant has only 2 damage reduction vs baseline's 5.
    """

    metadata = TestMetadata(
        test_id="EMISSIVE-005",
        category="EmissiveArmor",
        subcategory="Negative Value",
        name="Negative EmissiveArmor Reduces Protection",
        summary="EmissiveArmor(-3) in different group reduces total armor from 5 to 2",
        conditions=[
            f"Attacker: {ATTACKER_10DMG} ({EMISSIVE_HIGH_BEAM_DAMAGE} dmg, guaranteed hit)",
            "Target (5 armor): Test_Target_EmissiveArmor_GroupA.json (EmissiveArmor 5, group_a)",
            "Target (net 2 armor): Test_Target_EmissiveArmor_Negative.json "
            "(EmissiveArmor 5 group_a + EmissiveArmor -3 group_b = 2 net)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {EMISSIVE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Negative ability value is valid and reduces total",
            "Net emissive armor = 5 + (-3) = 2",
        ],
        expected_outcome="Variant takes more damage than baseline (2 armor vs 5 armor).",
        pass_criteria="variant_damage_dealt > baseline_damage_dealt",
        max_ticks=EMISSIVE_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["emissive-armor", "negative", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_10DMG
    baseline_target_ship = "Test_Target_EmissiveArmor_GroupA.json"
    variant_attacker_ship = ATTACKER_10DMG
    variant_target_ship = "Test_Target_EmissiveArmor_Negative.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify variant has reduced armor (5 + (-3) = 2)
        checks.append(check_exact(
            "Variant Emissive Armor (Net)",
            EMISSIVE_ARMOR_VALUE - 3,
            self.target.emissive_armor,
        ))

        # Precondition: both took damage
        checks.append(check_true(
            "Baseline Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: variant took more damage (less protection)
        checks.append(check_true(
            "Negative Armor Increased Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: exact damage ratio
        # Baseline: each hit = 10 - 5 = 5 damage
        # Variant: each hit = 10 - 2 = 8 damage
        # Ratio = 8/5 = 1.6
        expected_ratio = (EMISSIVE_HIGH_BEAM_DAMAGE - (EMISSIVE_ARMOR_VALUE - 3)) / \
                         (EMISSIVE_HIGH_BEAM_DAMAGE - EMISSIVE_ARMOR_VALUE)
        actual_ratio = self.variant_damage_dealt / self.baseline_damage_dealt
        checks.append(check_exact(
            "Damage Increase Ratio",
            expected_ratio, actual_ratio,
            phase="outcome",
        ))

        return checks


# =============================================================================
# EMISSIVE-006: Three Components Same Group Still MAX
# =============================================================================

class EmissiveThreeSameGroupScenario(ComparisonScenario):
    """
    EMISSIVE-006: Three Components Same Group Still MAX (Intra-Group MAX)

    Battle A: 1x EmissiveArmor(5, group_a) → 5 reduction
    Battle B: 3x EmissiveArmor(5, group_a) → MAX(5,5,5) = still 5

    Three components in the same stack_group produce the same protection
    as one. Both targets should take identical damage.
    """

    metadata = TestMetadata(
        test_id="EMISSIVE-006",
        category="EmissiveArmor",
        subcategory="Stacking",
        name="Three Same-Group Components Do Not Stack",
        summary="Three EmissiveArmor in same stack_group = MAX (no extra benefit over one)",
        conditions=[
            f"Attacker: {ATTACKER_10DMG} ({EMISSIVE_HIGH_BEAM_DAMAGE} dmg, guaranteed hit)",
            "Target (1x armor): Test_Target_EmissiveArmor_GroupA.json (1x EmissiveArmor 5, group_a)",
            "Target (3x same group): Test_Target_EmissiveArmor_3x_SameGroup.json (3x EmissiveArmor 5, all group_a)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {EMISSIVE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Intra-group MAX: three identical values in same group = no extra benefit",
            "Extends EMISSIVE-003 (2x) to 3 components",
        ],
        expected_outcome="Both targets take identical damage (3x same group = 1x).",
        pass_criteria="baseline_damage_dealt == variant_damage_dealt",
        max_ticks=EMISSIVE_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["emissive-armor", "stacking", "same-group", "three-component", "comparison"],
    )

    baseline_attacker_ship = ATTACKER_10DMG
    baseline_target_ship = "Test_Target_EmissiveArmor_GroupA.json"
    variant_attacker_ship = ATTACKER_10DMG
    variant_target_ship = "Test_Target_EmissiveArmor_3x_SameGroup.json"
    distance = POINT_BLANK_DISTANCE
    expect_different_damage = False  # Same-group MAX means identical damage

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify variant has same emissive armor value (MAX = 5)
        checks.append(check_exact(
            "Variant Emissive Armor", EMISSIVE_ARMOR_VALUE,
            self.target.emissive_armor,
        ))

        # Precondition: both took damage
        checks.append(check_true(
            "Baseline Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: identical damage (same group MAX = no extra benefit)
        checks.append(check_exact(
            "Same Damage (3x No Stack Benefit)",
            self.baseline_damage_dealt, self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# EMISSIVE-007: Damage Exactly Equals Emissive Value
# =============================================================================

class EmissiveExactDamageBlockScenario(ComparisonScenario):
    """
    EMISSIVE-007: Damage Exactly Equals Emissive Value → 0 Hull Damage

    Battle A: Target without emissive armor — all 5-dmg hits land
    Battle B: Target with EmissiveArmor(5) — 5-dmg hits reduced to 0

    EmissiveArmor(5) subtracts 5 from each hit. A 5-damage beam hit
    becomes max(0, 5-5) = 0 damage. This is the boundary condition.
    """

    metadata = TestMetadata(
        test_id="EMISSIVE-007",
        category="EmissiveArmor",
        subcategory="Boundary",
        name="Damage Exactly Equals Emissive Value",
        summary=f"EmissiveArmor({EMISSIVE_ARMOR_VALUE}) blocks {EMISSIVE_EXACT_BEAM_DAMAGE}-damage hits exactly (boundary case)",
        conditions=[
            f"Attacker: Test_Attacker_Beam_5dmg_Guaranteed.json ({EMISSIVE_EXACT_BEAM_DAMAGE} dmg, guaranteed hit)",
            f"Target (no armor): {NO_ARMOR_TARGET} (extreme HP, no emissive armor)",
            f"Target (with armor): {EMISSIVE_TARGET} (EmissiveArmor {EMISSIVE_ARMOR_VALUE})",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {EMISSIVE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            f"{EMISSIVE_EXACT_BEAM_DAMAGE} damage == {EMISSIVE_ARMOR_VALUE} armor → damage reduced to exactly 0",
            "Boundary condition: not less than, not greater than, exactly equal",
        ],
        expected_outcome="Variant takes zero damage. Baseline takes full damage.",
        pass_criteria="variant_damage_dealt == 0, baseline_damage_dealt > 0",
        max_ticks=EMISSIVE_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["emissive-armor", "boundary", "exact-match", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Beam_5dmg_Guaranteed.json"
    baseline_target_ship = NO_ARMOR_TARGET
    variant_attacker_ship = "Test_Attacker_Beam_5dmg_Guaranteed.json"
    variant_target_ship = EMISSIVE_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify emissive armor value
        checks.append(check_exact(
            "Emissive Armor Value", EMISSIVE_ARMOR_VALUE,
            self.target.emissive_armor,
        ))

        # Precondition: baseline took damage (beam fired)
        checks.append(check_true(
            "Baseline Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: variant took zero damage (damage == armor, boundary case)
        checks.append(check_exact(
            "Zero Damage At Boundary", 0.0, self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks
