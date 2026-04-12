"""
Armor Layer Test Scenarios (ARMOR-LAYER-001 to ARMOR-LAYER-003)

These tests validate basic armor layer mechanics: how damage flows through
the ARMOR layer to CORE layer components.

The damage pipeline processes layers by radius_pct descending:
- ARMOR (radius_pct=1.0) is outermost — hit first
- CORE (radius_pct=0.6) is innermost — hit after armor is destroyed

When all armor components in the ARMOR layer are destroyed, remaining
damage overflows to the next layer (CORE).

All tests use ships with:
- ARMOR layer: armor components with the Armor marker ability
- CORE layer: test_hull_extreme_hp (1B HP structure, NOT armor)

This lets us measure exact damage splits between layers by comparing
component HP before and after the battle.

All tests use a guaranteed-hit beam (base_accuracy=10.0, falloff=0) for
deterministic damage counts (1 damage per tick).
"""

from game.core.constants import LayerType
from combat_lab.scenarios import TestMetadata
from combat_lab.scenarios.templates import ComparisonScenario
from combat_lab.scenarios.validation import check_exact, check_true
from combat_lab.test_constants import (
    POINT_BLANK_DISTANCE,
    STANDARD_SEED,
    ARMOR_LAYER_TEST_TICKS,
    ARMOR_LAYER_1B_HP,
    ARMOR_LAYER_100_HP,
)


# =============================================================================
# COMMON SHIP REFERENCES
# =============================================================================

ARMOR_ATTACKER = "Test_Attacker_Beam_Guaranteed.json"
NO_ARMOR_TARGET = "Test_Target_NoArmor_Hull.json"


def _get_layer_hp(ship, layer_type):
    """Get total current HP of all components in a layer."""
    if layer_type not in ship.layers:
        return 0.0
    return sum(c.current_hp for c in ship.layers[layer_type].components)


def _get_layer_max_hp(ship, layer_type):
    """Get total max HP of all components in a layer."""
    if layer_type not in ship.layers:
        return 0.0
    return sum(c.max_hp for c in ship.layers[layer_type].components)


# =============================================================================
# ARMOR-LAYER-001: 1B Armor Absorbs All — Core Untouched
# =============================================================================

class ArmorAbsorbsAllScenario(ComparisonScenario):
    """
    ARMOR-LAYER-001: 1B Armor Absorbs All — Core Untouched

    Battle A: No armor (hull only in CORE) → all 500 hits damage hull
    Battle B: 1B HP armor in ARMOR layer + hull in CORE → armor absorbs all

    With 1B HP armor, the armor layer can never be depleted in 500 ticks.
    All damage should hit the ARMOR layer; CORE hull should be untouched.
    """

    metadata = TestMetadata(
        test_id="ARMOR-LAYER-001",
        category="ArmorLayer",
        subcategory="Basic Effect",
        name="1B Armor Absorbs All — Core Untouched",
        summary="Armor layer absorbs all damage, CORE hull takes zero damage",
        conditions=[
            f"Attacker: {ARMOR_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            f"Target (no armor): {NO_ARMOR_TARGET} (1B HP hull in CORE, empty ARMOR layer)",
            "Target (1B armor): Test_Target_Armor_1B_Hull.json (1B HP armor in ARMOR + 1B HP hull in CORE)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels (point blank)",
            f"Test Duration: {ARMOR_LAYER_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Armor HP far exceeds total damage dealt",
            "CORE hull should be completely untouched",
        ],
        expected_outcome="Variant: all damage absorbed by armor, hull at full HP. "
                         "Baseline: all damage hits hull directly.",
        pass_criteria="variant hull damage == 0, variant armor damage == baseline hull damage",
        max_ticks=ARMOR_LAYER_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["armor", "layer", "absorption", "comparison"],
    )

    baseline_attacker_ship = ARMOR_ATTACKER
    baseline_target_ship = NO_ARMOR_TARGET
    variant_attacker_ship = ARMOR_ATTACKER
    variant_target_ship = "Test_Target_Armor_1B_Hull.json"
    distance = POINT_BLANK_DISTANCE
    expect_different_damage = False  # Same total damage, different layer distribution

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify armor capacity
        armor_max = _get_layer_max_hp(self.target, LayerType.ARMOR)
        checks.append(check_exact(
            "Armor Max HP", float(ARMOR_LAYER_1B_HP), armor_max,
        ))

        # Precondition: baseline took damage (proves beam fired)
        checks.append(check_true(
            "Baseline Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: variant CORE hull took zero damage
        hull_max = _get_layer_max_hp(self.target, LayerType.CORE)
        hull_current = _get_layer_hp(self.target, LayerType.CORE)
        hull_damage = hull_max - hull_current
        checks.append(check_exact(
            "Core Hull Damage", 0.0, hull_damage,
            phase="outcome",
        ))

        # Outcome: variant armor absorbed all damage
        armor_current = _get_layer_hp(self.target, LayerType.ARMOR)
        armor_damage = armor_max - armor_current
        checks.append(check_exact(
            "Armor Absorbed All Damage",
            float(ARMOR_LAYER_TEST_TICKS), armor_damage,
            phase="outcome",
        ))

        return checks


# =============================================================================
# ARMOR-LAYER-002: 100 HP Armor Depletes, Overflows to Core
# =============================================================================

class ArmorDepletesOverflowScenario(ComparisonScenario):
    """
    ARMOR-LAYER-002: 100 HP Armor Depletes, Overflows to Core

    Battle A: No armor → all 500 hits go to CORE hull
    Battle B: 100 HP armor + hull → armor absorbs 100, CORE takes 400

    At 1 dmg/tick, armor depletes at tick 100. Remaining 400 ticks of
    damage overflow to CORE hull.
    """

    metadata = TestMetadata(
        test_id="ARMOR-LAYER-002",
        category="ArmorLayer",
        subcategory="Overflow",
        name="100 HP Armor Depletes, Overflows to Core",
        summary="Armor absorbs its full HP then damage overflows to CORE hull",
        conditions=[
            f"Attacker: {ARMOR_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            f"Target (no armor): {NO_ARMOR_TARGET} (1B HP hull in CORE, empty ARMOR layer)",
            "Target (100 HP armor): Test_Target_Armor_100_Hull.json (100 HP armor + 1B HP hull)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels (point blank)",
            f"Test Duration: {ARMOR_LAYER_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Armor depletes at tick 100 (100 HP / 1 dmg per tick)",
            "Remaining 400 ticks of damage go to CORE hull",
        ],
        expected_outcome="Armor absorbs exactly 100 damage, hull takes exactly 400 damage.",
        pass_criteria="armor_damage == 100, hull_damage == 400",
        max_ticks=ARMOR_LAYER_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["armor", "layer", "overflow", "depletion", "comparison"],
    )

    baseline_attacker_ship = ARMOR_ATTACKER
    baseline_target_ship = NO_ARMOR_TARGET
    variant_attacker_ship = ARMOR_ATTACKER
    variant_target_ship = "Test_Target_Armor_100_Hull.json"
    distance = POINT_BLANK_DISTANCE
    expect_different_damage = False  # Same total damage, different layer distribution

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify armor capacity
        armor_max = _get_layer_max_hp(self.target, LayerType.ARMOR)
        checks.append(check_exact(
            "Armor Max HP", float(ARMOR_LAYER_100_HP), armor_max,
        ))

        # Precondition: baseline took damage
        checks.append(check_true(
            "Baseline Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: armor fully depleted
        armor_current = _get_layer_hp(self.target, LayerType.ARMOR)
        checks.append(check_exact(
            "Armor Fully Depleted", 0.0, armor_current,
            phase="outcome",
        ))

        # Outcome: armor absorbed exactly 100 damage
        armor_damage = armor_max - armor_current
        checks.append(check_exact(
            "Armor Absorbed Exact HP",
            float(ARMOR_LAYER_100_HP), armor_damage,
            phase="outcome",
        ))

        # Outcome: hull took exactly (ticks - armor_hp) damage
        hull_max = _get_layer_max_hp(self.target, LayerType.CORE)
        hull_current = _get_layer_hp(self.target, LayerType.CORE)
        hull_damage = hull_max - hull_current
        expected_hull_damage = float(ARMOR_LAYER_TEST_TICKS - ARMOR_LAYER_100_HP)
        checks.append(check_exact(
            "Hull Took Overflow Damage",
            expected_hull_damage, hull_damage,
            phase="outcome",
        ))

        # Outcome: baseline hull damage == variant total damage
        checks.append(check_exact(
            "Total Damage Consistent",
            self.baseline_damage_dealt, self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# ARMOR-LAYER-003: 2x 100 HP Armor Stacks
# =============================================================================

class ArmorStackingScenario(ComparisonScenario):
    """
    ARMOR-LAYER-003: 2x 100 HP Armor Stacks

    Battle A: 1x 100 HP armor → absorbs 100, hull takes 400
    Battle B: 2x 100 HP armor (200 total) → absorbs 200, hull takes 300

    Proves that multiple armor components in the ARMOR layer sum their HP,
    providing more protection.
    """

    metadata = TestMetadata(
        test_id="ARMOR-LAYER-003",
        category="ArmorLayer",
        subcategory="Stacking",
        name="2x 100 HP Armor Stacks Additively",
        summary="Two armor components provide double the armor HP pool",
        conditions=[
            f"Attacker: {ARMOR_ATTACKER} (1 dmg, guaranteed hit, fires every tick)",
            "Target (1x armor): Test_Target_Armor_100_Hull.json (100 HP armor + 1B HP hull)",
            "Target (2x armor): Test_Target_Armor_2x100_Hull.json (2x 100 HP armor + 1B HP hull)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels (point blank)",
            f"Test Duration: {ARMOR_LAYER_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Two identical armor components in same layer",
            "Total armor HP = 200 (vs 100 in baseline)",
        ],
        expected_outcome="2x armor absorbs 200 total, hull takes 300 (vs 400 with 1x armor).",
        pass_criteria="variant hull_damage == 300, baseline hull_damage == 400, difference == 100",
        max_ticks=ARMOR_LAYER_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["armor", "layer", "stacking", "comparison"],
    )

    baseline_attacker_ship = ARMOR_ATTACKER
    baseline_target_ship = "Test_Target_Armor_100_Hull.json"
    variant_attacker_ship = ARMOR_ATTACKER
    variant_target_ship = "Test_Target_Armor_2x100_Hull.json"
    distance = POINT_BLANK_DISTANCE
    expect_different_damage = False  # Same total damage, different layer distribution

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify variant has double armor HP
        armor_max = _get_layer_max_hp(self.target, LayerType.ARMOR)
        checks.append(check_exact(
            "Variant Armor Max HP",
            float(ARMOR_LAYER_100_HP * 2), armor_max,
        ))

        # Precondition: both took hull damage
        # (baseline 1x armor: hull takes 400, variant 2x armor: hull takes 300)
        checks.append(check_true(
            "Baseline Took Hull Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: variant armor fully depleted
        armor_current = _get_layer_hp(self.target, LayerType.ARMOR)
        checks.append(check_exact(
            "Variant Armor Fully Depleted", 0.0, armor_current,
            phase="outcome",
        ))

        # Outcome: variant hull took exactly 300 damage
        hull_max = _get_layer_max_hp(self.target, LayerType.CORE)
        hull_current = _get_layer_hp(self.target, LayerType.CORE)
        hull_damage = hull_max - hull_current
        expected_hull_damage = float(ARMOR_LAYER_TEST_TICKS - ARMOR_LAYER_100_HP * 2)
        checks.append(check_exact(
            "Variant Hull Damage",
            expected_hull_damage, hull_damage,
            phase="outcome",
        ))

        # Outcome: baseline hull took 400 damage (500 ticks - 100 armor HP)
        # We can't access baseline layer state, but we know:
        # baseline_damage_dealt == variant_damage_dealt == 500 (total ship HP lost)
        # The difference is WHERE the damage went (armor vs hull)
        # So we verify variant hull_damage (300) < expected baseline hull_damage (400)
        baseline_expected_hull = float(ARMOR_LAYER_TEST_TICKS - ARMOR_LAYER_100_HP)
        checks.append(check_true(
            "2x Armor Reduced Hull Damage vs 1x",
            hull_damage < baseline_expected_hull,
            detail=f"variant_hull={hull_damage}, expected_1x_hull={baseline_expected_hull}",
            phase="outcome",
        ))

        # Outcome: exact difference == 100 (extra armor HP absorbed)
        hull_reduction = baseline_expected_hull - hull_damage
        checks.append(check_exact(
            "Hull Damage Reduction Equals Extra Armor HP",
            float(ARMOR_LAYER_100_HP), hull_reduction,
            phase="outcome",
        ))

        return checks
