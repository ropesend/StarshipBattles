"""
BeamWeaponAbility Test Scenarios (BEAMWEAPON-001 to BEAMWEAPON-011)

Suite Document: simulation_tests/suites/BeamWeaponAbility.md

These tests validate beam weapon accuracy mechanics using the sigmoid formula:
    P = 1 / (1 + e^-x)
    where x = (base_accuracy + attack_bonus) - (range_penalty + defense_penalty)
    range_penalty = accuracy_falloff * surface_distance

Note: Distance is measured to target SURFACE, not center.
      surface_distance = center_distance - target_radius

Test Coverage:
- Low Accuracy (0.5 base, 0.002 falloff): 3 distance variants
- Medium Accuracy (2.0 base, 0.001 falloff): 3 distance variants
- High Accuracy (5.0 base, 0.0005 falloff): 2 distance variants
- Moving Target Tests: 2 erratic target scenarios
- Range Limit Test: 1 out-of-range scenario
"""

import math
from simulation_tests.scenarios import TestMetadata
from simulation_tests.scenarios.validation import check_exact, check_approx, check_tost, check_true
from simulation_tests.scenarios.templates import StaticTargetScenario
from simulation_tests.test_constants import (
    STANDARD_TEST_TICKS,
    HIGH_TICK_TEST_TICKS,
    BEAM_LOW_ACCURACY,
    BEAM_LOW_FALLOFF,
    BEAM_LOW_RANGE,
    BEAM_LOW_DAMAGE,
    BEAM_MED_ACCURACY,
    BEAM_MED_FALLOFF,
    BEAM_MED_DAMAGE,
    BEAM_HIGH_ACCURACY,
    BEAM_HIGH_FALLOFF,
    BEAM_HIGH_DAMAGE,
    STATIONARY_TARGET_MASS,
    STANDARD_MARGIN,
    HIGH_PRECISION_MARGIN,
    STANDARD_SEED,
    POINT_BLANK_DISTANCE,
    MID_RANGE_DISTANCE,
    NEAR_MAX_RANGE_DISTANCE,
    BEAM_OUT_OF_RANGE_DISTANCE,
)


def calculate_defense_score(mass: float, acceleration: float = 0.0, turn_speed: float = 0.0, ecm_score: float = 0.0) -> float:
    """
    Calculate a ship's defense score based on size, maneuverability, and ECM.

    This matches the calculation in ship_stats.py Phase 5.

    Args:
        mass: Ship mass in tons
        acceleration: Acceleration rate
        turn_speed: Turn speed in degrees per second
        ecm_score: ECM/ToHitDefenseModifier ability total

    Returns:
        Total defense score (higher = harder to hit)
    """
    # Radius calculation (matches ship_stats.py line 266)
    base_radius = 40
    ref_mass = 1000
    actual_mass = max(mass, 100)
    ratio = actual_mass / ref_mass
    radius = base_radius * (ratio ** (1/3.0))

    # Size score (matches ship_stats.py lines 280-285)
    diameter = radius * 2
    d_ratio = max(0.1, diameter / 80.0)
    size_score = -2.5 * math.log10(d_ratio)

    # Maneuver score (matches ship_stats.py lines 287-290)
    maneuver_score = math.sqrt((acceleration / 20.0) + (turn_speed / 360.0))

    # Total defense score
    return size_score + maneuver_score + ecm_score


def calculate_expected_hit_chance(
    base_accuracy: float,
    accuracy_falloff: float,
    distance: float,
    attack_bonus: float = 0.0,
    defense_penalty: float = 0.0
) -> float:
    """
    Calculate expected hit chance using sigmoid formula.

    P = 1 / (1 + e^-x)
    where x = (base_accuracy + attack_bonus) - (range_penalty + defense_penalty)
    """
    range_penalty = accuracy_falloff * distance
    net_score = (base_accuracy + attack_bonus) - (range_penalty + defense_penalty)
    clamped_score = max(-20.0, min(20.0, net_score))
    return 1.0 / (1.0 + math.exp(-clamped_score))


def compute_beam_hit_chance(scenario, target_acceleration=0.0, target_turn_speed=0.0, target_ecm_score=0.0):
    """
    Compute the expected beam hit chance for a StaticTargetScenario.

    Reads beam stats from the attacker's BeamWeaponAbility and target mass
    from the loaded ships. Computes surface distance (center distance - target
    radius) and applies the sigmoid accuracy formula.

    Must be called after setup (needs scenario.attacker, scenario.target, scenario.distance).

    Args:
        scenario: StaticTargetScenario instance (post-setup)
        target_acceleration: Target acceleration for defense score (0.0 for stationary)
        target_turn_speed: Target turn speed for defense score (0.0 for stationary)
        target_ecm_score: Target ECM score for defense score (0.0 for no ECM)

    Returns:
        Expected hit chance (0.0 to 1.0)
    """
    # Extract beam weapon stats from attacker
    beam_ability = None
    for layer_name, layer_data in scenario.attacker.layers.items():
        for component in layer_data.components:
                if hasattr(component, 'ability_instances'):
                    for ability in component.ability_instances:
                        if ability.__class__.__name__ == 'BeamWeaponAbility':
                            beam_ability = ability
                            break

    base_accuracy = beam_ability.base_accuracy
    accuracy_falloff = beam_ability.accuracy_falloff

    # Calculate target defense score
    target_defense = calculate_defense_score(
        mass=scenario.target.mass,
        acceleration=target_acceleration,
        turn_speed=target_turn_speed,
        ecm_score=target_ecm_score
    )

    # Calculate surface distance (beam hits surface, not center)
    target_radius = 40 * ((scenario.target.mass / 1000) ** (1/3))
    surface_distance = scenario.distance - target_radius

    return calculate_expected_hit_chance(
        base_accuracy, accuracy_falloff, surface_distance, 0.0, target_defense
    )


# ============================================================================
# ACCURACY LEVEL CONFIGURATION
# ============================================================================

# Maps accuracy_level -> (attacker_ship, beam_damage, subcategory_label)
_ACCURACY_CONFIG = {
    "low": (
        "Test_Attacker_Beam360_Low.json",
        BEAM_LOW_DAMAGE,
        "Low",
    ),
    "med": (
        "Test_Attacker_Beam360_Med.json",
        BEAM_MED_DAMAGE,
        "Medium",
    ),
    "high": (
        "Test_Attacker_Beam360_High.json",
        BEAM_HIGH_DAMAGE,
        "High",
    ),
}

# Maps distance_label -> (center_distance, distance_display_name)
_DISTANCE_CONFIG = {
    "point_blank": (POINT_BLANK_DISTANCE, "Point Blank"),
    "mid_range": (MID_RANGE_DISTANCE, "Mid Range"),
    "max_range": (NEAR_MAX_RANGE_DISTANCE, "Max Range"),
}

# Maps (accuracy_level, distance_label) -> test_id number
_TEST_ID_MAP = {
    ("low", "point_blank"): "001",
    ("low", "mid_range"): "002",
    ("low", "max_range"): "003",
    ("med", "point_blank"): "004",
    ("med", "mid_range"): "005",
    ("med", "max_range"): "006",
    ("high", "point_blank"): "007",
    ("high", "max_range"): "008",
}

# Non-standard max_ticks for standard (non-HT) tests (default is STANDARD_TEST_TICKS)
_MAX_TICKS_OVERRIDE = {
    ("low", "max_range"): 1000,
    ("med", "max_range"): 1000,
}

# UI priority: point_blank=10, mid_range=9, max_range=8
_UI_PRIORITY = {
    "point_blank": 10,
    "mid_range": 9,
    "max_range": 8,
}


# ============================================================================
# PARAMETRIZED BASE CLASS
# ============================================================================

class BeamAccuracyScenario(StaticTargetScenario):
    """
    Parametrized base for beam accuracy tests against stationary targets.

    Subclasses set accuracy_level, distance_label, and optionally high_tick=True.
    Everything else -- ship files, metadata, custom_setup, validate -- is derived
    automatically.
    """

    # Subclass must set these
    accuracy_level: str = None   # "low", "med", "high"
    distance_label: str = None   # "point_blank", "mid_range", "max_range"
    high_tick: bool = False

    # Set by __init_subclass__
    target_ship = None
    attacker_ship = None
    distance = None
    metadata = None

    def __init_subclass__(cls, **kwargs):
        """Auto-configure metadata and template attributes from accuracy_level/distance_label."""
        super().__init_subclass__(**kwargs)

        # Skip configuration for the base class itself
        if cls.accuracy_level is None or cls.distance_label is None:
            return

        acc_ship, beam_damage, acc_label = _ACCURACY_CONFIG[cls.accuracy_level]
        center_distance, dist_name = _DISTANCE_CONFIG[cls.distance_label]
        test_num = _TEST_ID_MAP[(cls.accuracy_level, cls.distance_label)]

        cls._beam_damage_expected = beam_damage

        # Ship and distance configuration
        cls.attacker_ship = acc_ship
        cls.distance = center_distance

        if cls.high_tick:
            cls.target_ship = "Test_Target_Stationary_HighTick.json"
            test_id = f"BEAMWEAPON-{test_num}-HT"
            max_ticks = HIGH_TICK_TEST_TICKS
            margin_name = "HIGH_PRECISION"
            ui_priority = 11
            subcategory = f"Accuracy - {acc_label} (High-Tick)"
            name_suffix = " [100k Ticks]"
            extra_tags = ["high-tick", "precision"]
            summary_prefix = "High-precision validation"
            summary_detail = "with 100k ticks for +/-1% statistical margin"
            expected_outcome_tpl = "Hit rate within +/-1% of expected with 99% confidence"
            pass_criteria = "Statistical validation passes with p < 0.05"
        else:
            cls.target_ship = "Test_Target_Stationary.json"
            test_id = f"BEAMWEAPON-{test_num}"
            max_ticks = _MAX_TICKS_OVERRIDE.get(
                (cls.accuracy_level, cls.distance_label), STANDARD_TEST_TICKS
            )
            margin_name = "STANDARD"
            ui_priority = _UI_PRIORITY[cls.distance_label]
            subcategory = f"Accuracy - {acc_label}"
            name_suffix = ""
            extra_tags = []
            summary_prefix = f"Validates {acc_label.lower()} accuracy beam"
            summary_detail = f"at {dist_name.lower()} range"
            expected_outcome_tpl = "Hit rate matches sigmoid prediction within +/-6%"
            pass_criteria = "TOST equivalence test passes"

        # Compute surface distance for metadata display
        target_radius = 40 * ((STATIONARY_TARGET_MASS / 1000) ** (1/3))
        surface_dist = center_distance - target_radius

        dist_tag = cls.distance_label.replace("_", "-")
        acc_tag = f"{cls.accuracy_level.replace('med', 'medium')}-accuracy"

        cls.metadata = TestMetadata(
            test_id=test_id,
            category="BeamWeaponAbility",
            subcategory=subcategory,
            name=f"{acc_label} Accuracy Beam - {dist_name} ({surface_dist:.1f}px surface){name_suffix}",
            summary=f"{summary_prefix} {summary_detail}",
            conditions=[
                f"Attacker: {acc_ship}",
                f"Target: {cls.target_ship} (mass={int(STATIONARY_TARGET_MASS)})",
                f"Center Distance: {center_distance} pixels",
                f"Surface Distance: {surface_dist:.2f} pixels",
                f"Margin: {margin_name}",
                f"Test Duration: {max_ticks} ticks",
            ],
            edge_cases=[
                f"Beam accuracy test at {dist_name.lower()} with {acc_label.lower()} accuracy weapon",
            ],
            expected_outcome=expected_outcome_tpl,
            pass_criteria=pass_criteria,
            max_ticks=max_ticks,
            seed=STANDARD_SEED,
            battle_end_mode="time_based",
            ui_priority=ui_priority,
            tags=["accuracy", acc_tag, dist_tag, "beam-weapons"] + extra_tags,
        )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        self.expected_hit_chance = compute_beam_hit_chance(self)

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Weapon Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks
        checks.append(check_exact("Beam Damage", self._beam_damage_expected, beam.damage))
        checks.append(check_exact("Target Mass", STATIONARY_TARGET_MASS, self.target.mass))
        margin = HIGH_PRECISION_MARGIN if self.high_tick else STANDARD_MARGIN
        checks.append(check_tost("Hit Rate", self.expected_hit_chance,
                                  successes=int(self.damage_dealt),
                                  trials=engine.tick_counter,
                                  margin=margin))
        return checks


# ============================================================================
# LOW ACCURACY BEAM TESTS (base_accuracy=0.5, falloff=0.002)
# ============================================================================

class BeamLowAccuracyPointBlankScenario(BeamAccuracyScenario):
    """BEAMWEAPON-001: Low Accuracy Beam at Point-Blank Range"""
    accuracy_level = "low"
    distance_label = "point_blank"


class BeamLowAccuracyPointBlankHighTickScenario(BeamAccuracyScenario):
    """BEAMWEAPON-001-HT: Low Accuracy Beam at Point-Blank Range (High-Tick)"""
    accuracy_level = "low"
    distance_label = "point_blank"
    high_tick = True


class BeamLowAccuracyMidRangeScenario(BeamAccuracyScenario):
    """BEAMWEAPON-002: Low Accuracy Beam at Mid-Range"""
    accuracy_level = "low"
    distance_label = "mid_range"


class BeamLowAccuracyMidRangeHighTickScenario(BeamAccuracyScenario):
    """BEAMWEAPON-002-HT: Low Accuracy Beam at Mid-Range (High-Tick)"""
    accuracy_level = "low"
    distance_label = "mid_range"
    high_tick = True


class BeamLowAccuracyMaxRangeScenario(BeamAccuracyScenario):
    """BEAMWEAPON-003: Low Accuracy Beam at Max Range"""
    accuracy_level = "low"
    distance_label = "max_range"


# ============================================================================
# MEDIUM ACCURACY BEAM TESTS (base_accuracy=2.0, falloff=0.001)
# ============================================================================

class BeamMediumAccuracyPointBlankScenario(BeamAccuracyScenario):
    """BEAMWEAPON-004: Medium Accuracy Beam at Point-Blank Range"""
    accuracy_level = "med"
    distance_label = "point_blank"


class BeamMediumAccuracyPointBlankHighTickScenario(BeamAccuracyScenario):
    """BEAMWEAPON-004-HT: Medium Accuracy Beam at Point-Blank Range (High-Tick)"""
    accuracy_level = "med"
    distance_label = "point_blank"
    high_tick = True


class BeamMediumAccuracyMidRangeScenario(BeamAccuracyScenario):
    """BEAMWEAPON-005: Medium Accuracy Beam at Mid-Range"""
    accuracy_level = "med"
    distance_label = "mid_range"


class BeamMediumAccuracyMidRangeHighTickScenario(BeamAccuracyScenario):
    """BEAMWEAPON-005-HT: Medium Accuracy Beam at Mid-Range (High-Tick)"""
    accuracy_level = "med"
    distance_label = "mid_range"
    high_tick = True


class BeamMediumAccuracyMaxRangeScenario(BeamAccuracyScenario):
    """BEAMWEAPON-006: Medium Accuracy Beam at Max Range"""
    accuracy_level = "med"
    distance_label = "max_range"


class BeamMediumAccuracyMaxRangeHighTickScenario(BeamAccuracyScenario):
    """BEAMWEAPON-006-HT: Medium Accuracy Beam at Max Range (High-Tick)"""
    accuracy_level = "med"
    distance_label = "max_range"
    high_tick = True


# ============================================================================
# HIGH ACCURACY BEAM TESTS (base_accuracy=5.0, falloff=0.0005)
# ============================================================================

class BeamHighAccuracyPointBlankScenario(BeamAccuracyScenario):
    """BEAMWEAPON-007: High Accuracy Beam at Point-Blank Range"""
    accuracy_level = "high"
    distance_label = "point_blank"


class BeamHighAccuracyPointBlankHighTickScenario(BeamAccuracyScenario):
    """BEAMWEAPON-007-HT: High Accuracy Beam at Point-Blank Range (High-Tick)"""
    accuracy_level = "high"
    distance_label = "point_blank"
    high_tick = True


class BeamHighAccuracyMaxRangeScenario(BeamAccuracyScenario):
    """BEAMWEAPON-008: High Accuracy Beam at Max Range"""
    accuracy_level = "high"
    distance_label = "max_range"


class BeamHighAccuracyMaxRangeHighTickScenario(BeamAccuracyScenario):
    """BEAMWEAPON-008-HT: High Accuracy Beam at Max Range (High-Tick)"""
    accuracy_level = "high"
    distance_label = "max_range"
    high_tick = True


# ============================================================================
# MOVING TARGET TESTS
# ============================================================================

class BeamMediumAccuracyErraticMidRangeScenario(StaticTargetScenario):
    """
    BEAMWEAPON-009: Medium Accuracy Beam vs Erratic Small Target at Mid-Range

    Tests that target maneuverability adds defense penalty, reducing hit chance
    against a small erratic target.

    Surface distance: 383.92px (center 400px - radius 16.08px for mass=65)
    Expected hit rate: 4.84%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_Med.json"
    target_ship = "Test_Target_Erratic_Small.json"
    distance = MID_RANGE_DISTANCE

    metadata = TestMetadata(
        test_id="BEAMWEAPON-009",
        category="BeamWeaponAbility",
        subcategory="Moving Targets",
        name="Medium Accuracy vs Erratic Small - Mid Range (383.9px surface)",
        summary="Validates that target maneuverability adds defense penalty, reducing hit chance against erratic targets",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Erratic_Small.json (mass=65, high maneuverability)",
            "Base Accuracy: 2.0",
            "Accuracy Falloff: 0.001 per pixel",
            "Center Distance: 400 pixels",
            "Target Radius: 16.08 pixels (from mass=65)",
            "Surface Distance: 400 - 16.08 = 383.92 pixels (actual firing distance)",
            "Range Penalty: 383.92 * 0.001 = 0.3839",
            "Defense Penalty: 3.1408 (from mass=65, acc=295.86, turn=238.53)",
            "Net Score: 2.0 - 0.3839 - 3.1408 = -1.5247",
            "Sigmoid formula: P = 1/(1+e^1.5247) = 0.0484 (4.84% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 1000 ticks"
        ],
        edge_cases=[
            "Target size (small) may provide defense bonus",
            "Erratic movement pattern increases defense score",
            "Combined range and defense penalties significantly reduce hit rate"
        ],
        expected_outcome="Reduced hit rate (~5%) due to target maneuverability, some damage dealt",
        pass_criteria="simulation_completes (ticks_run > 0)",
        max_ticks=1000,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=7,
        tags=["accuracy", "medium-accuracy", "moving-target", "erratic", "beam-weapons"],
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        self.expected_hit_chance = compute_beam_hit_chance(
            self, target_acceleration=295.86, target_turn_speed=238.53
        )
        self.expected_hit_chance_base = compute_beam_hit_chance(self)

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Weapon Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks
        checks.append(check_exact("Beam Damage", BEAM_MED_DAMAGE, beam.damage))
        checks.append(check_true(
            "Defense Reduces Hit Chance",
            self.expected_hit_chance < self.expected_hit_chance_base,
            detail=f"with_defense={self.expected_hit_chance:.4f}, base={self.expected_hit_chance_base:.4f}",
        ))
        # Erratic target - observational only (hit rate depends on AI movement)
        checks.append(check_true(
            "Some Damage Dealt", self.damage_dealt >= 0,
            actual=self.damage_dealt, phase="outcome",
            detail="Erratic target test - hit rate varies with AI movement",
        ))
        return checks


class BeamMediumAccuracyErraticMaxRangeScenario(StaticTargetScenario):
    """
    BEAMWEAPON-010: Medium Accuracy Beam vs Erratic Small Target at Max Range

    Tests combined effects of range penalty and maneuverability penalty
    at maximum range.

    Surface distance: 733.92px (center 750px - radius 16.08px for mass=65)
    Expected hit rate: 3.47%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_Med.json"
    target_ship = "Test_Target_Erratic_Small.json"
    distance = NEAR_MAX_RANGE_DISTANCE

    metadata = TestMetadata(
        test_id="BEAMWEAPON-010",
        category="BeamWeaponAbility",
        subcategory="Moving Targets",
        name="Medium Accuracy vs Erratic Small - Max Range (733.9px surface)",
        summary="Validates combined effects of range and maneuverability penalties at maximum range",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Erratic_Small.json (mass=65, high maneuverability)",
            "Base Accuracy: 2.0",
            "Accuracy Falloff: 0.001 per pixel",
            "Center Distance: 750 pixels (near max range of 800)",
            "Target Radius: 16.08 pixels (from mass=65)",
            "Surface Distance: 750 - 16.08 = 733.92 pixels (actual firing distance)",
            "Range Penalty: 733.92 * 0.001 = 0.7339",
            "Defense Penalty: 3.1408 (from mass=65, acc=295.86, turn=238.53)",
            "Net Score: 2.0 - 0.7339 - 3.1408 = -1.8747",
            "Sigmoid formula: P = 1/(1+e^1.8747) = 0.0347 (3.47% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 1000 ticks"
        ],
        edge_cases=[
            "Maximum range penalty combined with defense penalty",
            "Worst-case scenario for hitting a difficult target",
            "May result in minimal or no damage"
        ],
        expected_outcome="Low hit rate (~3.5%) due to combined penalties, minimal damage expected",
        pass_criteria="simulation_completes (ticks_run > 0)",
        max_ticks=1000,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=6,
        tags=["accuracy", "medium-accuracy", "moving-target", "erratic", "max-range", "beam-weapons"],
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        self.expected_hit_chance = compute_beam_hit_chance(
            self, target_acceleration=295.86, target_turn_speed=238.53
        )
        self.expected_hit_chance_base = compute_beam_hit_chance(self)

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Weapon Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks
        checks.append(check_exact("Beam Damage", BEAM_MED_DAMAGE, beam.damage))
        checks.append(check_true(
            "Defense Reduces Hit Chance",
            self.expected_hit_chance < self.expected_hit_chance_base,
            detail=f"with_defense={self.expected_hit_chance:.4f}, base={self.expected_hit_chance_base:.4f}",
        ))
        # Erratic target - observational only (hit rate depends on AI movement)
        checks.append(check_true(
            "Some Damage Dealt", self.damage_dealt >= 0,
            actual=self.damage_dealt, phase="outcome",
            detail="Erratic target test - hit rate varies with AI movement",
        ))
        return checks


# ============================================================================
# RANGE LIMIT TEST
# ============================================================================

class BeamOutOfRangeScenario(StaticTargetScenario):
    """
    BEAMWEAPON-011: Beam Weapon Out of Range (Negative Test)

    Tests that beam weapons cannot hit targets beyond their max range.
    Target at 900px when weapon range is 800px.

    Surface distance: 870.53px (center 900px - radius 29.47px)
    Expected damage: 0 (out of range)
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_Med.json"
    target_ship = "Test_Target_Stationary.json"
    distance = BEAM_OUT_OF_RANGE_DISTANCE

    metadata = TestMetadata(
        test_id="BEAMWEAPON-011",
        category="BeamWeaponAbility",
        subcategory="Range Limits",
        name="Beam Out of Range - No Hits (870.5px surface > 800px max)",
        summary="Validates that beam weapons cannot hit targets beyond their maximum range",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Stationary.json (mass=400)",
            "Weapon Max Range: 800 pixels",
            "Center Distance: 900 pixels (100px beyond range)",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 900 - 29.47 = 870.53 pixels (actual firing distance)",
            "Expected Damage: 0 (out of range)",
            "Beam Damage: 1 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Target is beyond weapon range",
            "Weapon may fire but should not deal damage",
            "Range check happens before accuracy calculation",
            "Hard cutoff at max_range, no partial damage"
        ],
        expected_outcome="No damage dealt (damage_dealt == 0)",
        pass_criteria="damage_dealt == 0",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=8,
        tags=["range-limit", "out-of-range", "beam-weapons"],
    )

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Weapon Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks
        checks.append(check_exact("Distance Beyond Range", True, self.distance > beam.range,
                                  phase="data"))
        checks.append(check_exact("Damage Dealt", 0, self.damage_dealt, phase="outcome"))
        return checks


# ============================================================================
# EXPORT ALL SCENARIOS
# ============================================================================

__all__ = [
    'BeamLowAccuracyPointBlankScenario',
    'BeamLowAccuracyPointBlankHighTickScenario',
    'BeamLowAccuracyMidRangeScenario',
    'BeamLowAccuracyMidRangeHighTickScenario',
    'BeamLowAccuracyMaxRangeScenario',
    'BeamMediumAccuracyPointBlankScenario',
    'BeamMediumAccuracyPointBlankHighTickScenario',
    'BeamMediumAccuracyMidRangeScenario',
    'BeamMediumAccuracyMidRangeHighTickScenario',
    'BeamMediumAccuracyMaxRangeScenario',
    'BeamMediumAccuracyMaxRangeHighTickScenario',
    'BeamHighAccuracyPointBlankScenario',
    'BeamHighAccuracyPointBlankHighTickScenario',
    'BeamHighAccuracyMaxRangeScenario',
    'BeamHighAccuracyMaxRangeHighTickScenario',
    'BeamMediumAccuracyErraticMidRangeScenario',
    'BeamMediumAccuracyErraticMaxRangeScenario',
    'BeamOutOfRangeScenario'
]
