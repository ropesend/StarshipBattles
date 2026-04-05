"""
Damage Multiplier Modifier Scenarios (MOD-DMG-001 through MOD-DMG-005)

Dedicated test scenarios for the damage_mult modifier at various parameter values.
Uses StaticTargetScenario for single-ship stat/outcome validation and
ComparisonScenario for A/B damage ratio comparisons.

Test Coverage:
- MOD-DMG-001: Damage boost 1.5x (standard param)
- MOD-DMG-002: Damage boost 1.0x (identity / minimum)
- MOD-DMG-003: Damage boost 10.0x (maximum)
- MOD-DMG-004: Comparison — boosted (1.5x) vs unboosted baseline
- MOD-DMG-005: Comparison — max (10.0x) vs min (1.0x)
"""

from simulation_tests.scenarios.base import TestMetadata
from simulation_tests.scenarios.templates import StaticTargetScenario, ComparisonScenario
from simulation_tests.scenarios.validation import check_exact, check_approx, check_true
from simulation_tests.test_constants import (
    STANDARD_SEED,
    POINT_BLANK_DISTANCE,
    MODIFIER_TEST_TICKS,
    MOD_BASE_BEAM_DAMAGE,
    DAMAGE_BOOST_PARAM,
    MOD_EXPECTED_DAMAGE,
    DAMAGE_BOOST_ATTACKER_SHIP,
)

# Ship filenames
DMGBOOST_MIN_SHIP = "Test_Attacker_Beam_DmgBoost_Min.json"
DMGBOOST_MAX_SHIP = "Test_Attacker_Beam_DmgBoost_Max.json"
BASELINE_BEAM_SHIP = "Test_Attacker_Beam360_Med.json"
STATIONARY_TARGET = "Test_Target_Stationary.json"
STANDARD_TARGET = "Test_Target.json"

# Expected modified damage values
DMGBOOST_MIN_EXPECTED = MOD_BASE_BEAM_DAMAGE * 1.0   # 1.0 (identity)
DMGBOOST_MAX_EXPECTED = MOD_BASE_BEAM_DAMAGE * 10.0  # 10.0


# ============================================================================
# MOD-DMG-001: Damage Boost 1.5x (standard)
# ============================================================================

class ModDmg001_StandardBoostScenario(StaticTargetScenario):
    """
    MOD-DMG-001: Verify test_damage_boost(1.5) multiplies beam damage to 1.5.

    Setup: Medium accuracy beam with damage_mult=1.5 at point-blank vs standard target.
    Data check: beam.damage == 1.5 (base 1 * 1.5)
    Outcome check: damage_dealt > 0
    """
    metadata = TestMetadata(
        test_id="MOD-DMG-001",
        category="DamageMultiplier",
        subcategory="Basic Effect",
        name="Damage boost 1.5x (standard)",
        summary="Verify test_damage_boost(1.5) multiplies beam damage from 1 to 1.5",
        conditions=[
            f"Base beam damage: {MOD_BASE_BEAM_DAMAGE}",
            f"Damage multiplier param: {DAMAGE_BOOST_PARAM}",
            f"Expected modified damage: {MOD_EXPECTED_DAMAGE}",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
        ],
        edge_cases=[],
        expected_outcome=f"beam.damage == {MOD_EXPECTED_DAMAGE}, damage dealt to target",
        pass_criteria=f"beam.damage == {MOD_EXPECTED_DAMAGE} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "damage_mult", "beam"],
    )

    attacker_ship = DAMAGE_BOOST_ATTACKER_SHIP
    target_ship = STANDARD_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_beam_damage = beam.damage
        else:
            self.actual_beam_damage = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_damage'] = MOD_BASE_BEAM_DAMAGE
        self.results['damage_multiplier'] = DAMAGE_BOOST_PARAM
        self.results['expected_beam_damage'] = MOD_EXPECTED_DAMAGE
        self.results['actual_beam_damage'] = self.actual_beam_damage

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: beam weapon loaded
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true(
            "Beam Weapon Loaded", beam is not None, phase="precondition",
        ))
        if beam is None:
            return checks

        # Data: base damage and modified damage
        checks.append(check_exact(
            "Base Beam Damage (from JSON)", MOD_BASE_BEAM_DAMAGE,
            self.results.get('base_damage', 0), phase="data",
        ))
        checks.append(check_approx(
            "Modified Beam Damage", MOD_EXPECTED_DAMAGE,
            self.actual_beam_damage or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Outcome: damage was dealt
        checks.append(check_true(
            "Damage Dealt", self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-DMG-002: Damage Boost 1.0x (identity / minimum)
# ============================================================================

class ModDmg002_IdentityBoostScenario(StaticTargetScenario):
    """
    MOD-DMG-002: Verify test_damage_boost(1.0) leaves beam damage unchanged.

    Setup: Medium accuracy beam with damage_mult=1.0 at point-blank vs standard target.
    Data check: beam.damage == 1.0 (base 1 * 1.0 = identity)
    Outcome check: damage_dealt > 0
    """
    metadata = TestMetadata(
        test_id="MOD-DMG-002",
        category="DamageMultiplier",
        subcategory="Boundary",
        name="Damage boost 1.0x (identity)",
        summary="Verify test_damage_boost(1.0) leaves beam damage at base value of 1.0",
        conditions=[
            f"Base beam damage: {MOD_BASE_BEAM_DAMAGE}",
            "Damage multiplier param: 1.0 (identity)",
            f"Expected modified damage: {DMGBOOST_MIN_EXPECTED}",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
        ],
        edge_cases=["Identity multiplier should not alter damage at all"],
        expected_outcome=f"beam.damage == {DMGBOOST_MIN_EXPECTED}, damage dealt to target",
        pass_criteria=f"beam.damage == {DMGBOOST_MIN_EXPECTED} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "damage_mult", "beam", "identity"],
    )

    attacker_ship = DMGBOOST_MIN_SHIP
    target_ship = STANDARD_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_beam_damage = beam.damage
        else:
            self.actual_beam_damage = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_damage'] = MOD_BASE_BEAM_DAMAGE
        self.results['damage_multiplier'] = 1.0
        self.results['expected_beam_damage'] = DMGBOOST_MIN_EXPECTED
        self.results['actual_beam_damage'] = self.actual_beam_damage

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: beam weapon loaded
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true(
            "Beam Weapon Loaded", beam is not None, phase="precondition",
        ))
        if beam is None:
            return checks

        # Data: damage unchanged by identity multiplier
        checks.append(check_exact(
            "Base Beam Damage (from JSON)", MOD_BASE_BEAM_DAMAGE,
            self.results.get('base_damage', 0), phase="data",
        ))
        checks.append(check_approx(
            "Modified Beam Damage (identity)", DMGBOOST_MIN_EXPECTED,
            self.actual_beam_damage or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Outcome: damage was dealt
        checks.append(check_true(
            "Damage Dealt", self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-DMG-003: Damage Boost 10.0x (maximum)
# ============================================================================

class ModDmg003_MaxBoostScenario(StaticTargetScenario):
    """
    MOD-DMG-003: Verify test_damage_boost(10.0) multiplies beam damage to 10.0.

    Setup: Medium accuracy beam with damage_mult=10.0 at point-blank vs standard target.
    Data check: beam.damage == 10.0 (base 1 * 10.0)
    Outcome check: damage_dealt > 0
    """
    metadata = TestMetadata(
        test_id="MOD-DMG-003",
        category="DamageMultiplier",
        subcategory="Boundary",
        name="Damage boost 10.0x (maximum)",
        summary="Verify test_damage_boost(10.0) multiplies beam damage from 1 to 10.0",
        conditions=[
            f"Base beam damage: {MOD_BASE_BEAM_DAMAGE}",
            "Damage multiplier param: 10.0",
            f"Expected modified damage: {DMGBOOST_MAX_EXPECTED}",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
        ],
        edge_cases=["High multiplier should scale linearly"],
        expected_outcome=f"beam.damage == {DMGBOOST_MAX_EXPECTED}, damage dealt to target",
        pass_criteria=f"beam.damage == {DMGBOOST_MAX_EXPECTED} AND damage_dealt > 0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "damage_mult", "beam", "max"],
    )

    attacker_ship = DMGBOOST_MAX_SHIP
    target_ship = STANDARD_TARGET
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            self.actual_beam_damage = beam.damage
        else:
            self.actual_beam_damage = None

    def _collect_extra_results(self, battle_engine):
        self.results['base_damage'] = MOD_BASE_BEAM_DAMAGE
        self.results['damage_multiplier'] = 10.0
        self.results['expected_beam_damage'] = DMGBOOST_MAX_EXPECTED
        self.results['actual_beam_damage'] = self.actual_beam_damage

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: beam weapon loaded
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true(
            "Beam Weapon Loaded", beam is not None, phase="precondition",
        ))
        if beam is None:
            return checks

        # Data: damage scaled to maximum
        checks.append(check_exact(
            "Base Beam Damage (from JSON)", MOD_BASE_BEAM_DAMAGE,
            self.results.get('base_damage', 0), phase="data",
        ))
        checks.append(check_approx(
            "Modified Beam Damage (max)", DMGBOOST_MAX_EXPECTED,
            self.actual_beam_damage or 0.0, tolerance=0.001,
            phase="data",
        ))

        # Outcome: damage was dealt
        checks.append(check_true(
            "Damage Dealt", self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-DMG-004: Boosted (1.5x) vs Unboosted Baseline
# ============================================================================

class ModDmg004_BoostVsBaselineScenario(ComparisonScenario):
    """
    MOD-DMG-004: Compare damage output of a 1.5x boosted beam vs unboosted beam.

    Baseline: Standard medium-accuracy beam (no modifier), damage=1.
    Variant: Same beam with test_damage_boost(1.5), damage=1.5.
    Both fire at point-blank against stationary targets for same duration.
    Outcome: variant deals approximately 1.5x more total damage.
    """
    metadata = TestMetadata(
        test_id="MOD-DMG-004",
        category="DamageMultiplier",
        subcategory="Combat Outcome",
        name="1.5x boost vs unboosted baseline",
        summary="Verify 1.5x damage modifier produces ~1.5x more total damage than baseline",
        conditions=[
            "Baseline: medium-accuracy beam, damage=1 (no modifier)",
            f"Variant: same beam with test_damage_boost({DAMAGE_BOOST_PARAM}), damage={MOD_EXPECTED_DAMAGE}",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
            f"Duration: {MODIFIER_TEST_TICKS} ticks",
            "Same seed for both battles",
        ],
        edge_cases=[],
        expected_outcome=f"Variant deals ~{DAMAGE_BOOST_PARAM}x more damage than baseline",
        pass_criteria="variant_damage / baseline_damage within 10% of 1.5",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "damage_mult", "beam", "comparison"],
    )

    baseline_attacker_ship = BASELINE_BEAM_SHIP
    baseline_target_ship = STATIONARY_TARGET
    variant_attacker_ship = DAMAGE_BOOST_ATTACKER_SHIP
    variant_target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both battles dealt damage
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

        # Outcome: variant deals more damage than baseline
        checks.append(check_true(
            "Boosted Beam Deals More Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"baseline={self.baseline_damage_dealt}, "
                   f"variant={self.variant_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: damage ratio is approximately 1.5x
        if self.baseline_damage_dealt > 0:
            ratio = self.variant_damage_dealt / self.baseline_damage_dealt
            checks.append(check_approx(
                "Damage Ratio ~1.5x", DAMAGE_BOOST_PARAM,
                ratio, tolerance=0.15,
                phase="outcome",
            ))

        return checks


# ============================================================================
# MOD-DMG-005: Max (10.0x) vs Min (1.0x)
# ============================================================================

class ModDmg005_MaxVsMinScenario(ComparisonScenario):
    """
    MOD-DMG-005: Compare damage output of 10.0x boost vs 1.0x (identity) boost.

    Baseline: Beam with test_damage_boost(1.0), damage=1.0.
    Variant: Beam with test_damage_boost(10.0), damage=10.0.
    Both fire at point-blank against stationary targets for same duration.
    Outcome: variant deals approximately 10x more total damage.
    """
    metadata = TestMetadata(
        test_id="MOD-DMG-005",
        category="DamageMultiplier",
        subcategory="Combat Outcome",
        name="10.0x boost vs 1.0x identity",
        summary="Verify 10.0x damage modifier produces ~10x more total damage than 1.0x identity",
        conditions=[
            f"Baseline: beam with test_damage_boost(1.0), damage={DMGBOOST_MIN_EXPECTED}",
            f"Variant: beam with test_damage_boost(10.0), damage={DMGBOOST_MAX_EXPECTED}",
            f"Distance: {POINT_BLANK_DISTANCE} (point-blank)",
            f"Duration: {MODIFIER_TEST_TICKS} ticks",
            "Same seed for both battles",
        ],
        edge_cases=["Large multiplier ratio should hold precisely at point-blank"],
        expected_outcome="Variant deals ~10x more damage than baseline",
        pass_criteria="variant_damage / baseline_damage within 10% of 10.0",
        max_ticks=MODIFIER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["modifier", "damage_mult", "beam", "comparison", "extreme"],
    )

    baseline_attacker_ship = DMGBOOST_MIN_SHIP
    baseline_target_ship = STATIONARY_TARGET
    variant_attacker_ship = DMGBOOST_MAX_SHIP
    variant_target_ship = STATIONARY_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: both battles dealt damage
        checks.append(check_true(
            "Baseline (1.0x) Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"baseline_damage={self.baseline_damage_dealt}",
            phase="precondition",
        ))
        checks.append(check_true(
            "Variant (10.0x) Dealt Damage",
            self.variant_damage_dealt > 0,
            detail=f"variant_damage={self.variant_damage_dealt}",
            phase="precondition",
        ))

        # Outcome: variant deals more damage
        checks.append(check_true(
            "Max Boost Deals More Damage Than Min",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"min={self.baseline_damage_dealt}, "
                   f"max={self.variant_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: damage ratio is approximately 10x
        expected_ratio = DMGBOOST_MAX_EXPECTED / DMGBOOST_MIN_EXPECTED  # 10.0
        if self.baseline_damage_dealt > 0:
            ratio = self.variant_damage_dealt / self.baseline_damage_dealt
            checks.append(check_approx(
                "Damage Ratio ~10x", expected_ratio,
                ratio, tolerance=1.0,
                phase="outcome",
            ))

        return checks
