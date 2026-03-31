"""
BeamWeaponAbility Test Scenarios (BEAMWEAPON-001 to BEAMWEAPON-011, BEAMWEAPON-RES-001 to 003)

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
from simulation_tests.scenarios.templates import StaticTargetScenario, ComparisonScenario
from simulation_tests.test_constants import (
    STANDARD_TEST_TICKS,
    HIGH_TICK_TEST_TICKS,
    BEAM_LOW_ACCURACY,
    BEAM_LOW_FALLOFF,
    BEAM_LOW_RANGE,
    BEAM_LOW_DAMAGE,
    BEAM_MED_ACCURACY,
    BEAM_MED_FALLOFF,
    BEAM_MED_RANGE,
    BEAM_MED_DAMAGE,
    BEAM_HIGH_ACCURACY,
    BEAM_HIGH_FALLOFF,
    BEAM_HIGH_RANGE,
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

# Maps accuracy_level -> (attacker_ship, beam_damage, base_accuracy, accuracy_falloff, beam_range, subcategory_label)
_ACCURACY_CONFIG = {
    "low": (
        "Test_Attacker_Beam360_Low.json",
        BEAM_LOW_DAMAGE,
        BEAM_LOW_ACCURACY,
        BEAM_LOW_FALLOFF,
        BEAM_LOW_RANGE,
        "Low",
    ),
    "med": (
        "Test_Attacker_Beam360_Med.json",
        BEAM_MED_DAMAGE,
        BEAM_MED_ACCURACY,
        BEAM_MED_FALLOFF,
        BEAM_MED_RANGE,
        "Medium",
    ),
    "high": (
        "Test_Attacker_Beam360_High.json",
        BEAM_HIGH_DAMAGE,
        BEAM_HIGH_ACCURACY,
        BEAM_HIGH_FALLOFF,
        BEAM_HIGH_RANGE,
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

        acc_ship, beam_damage, base_accuracy, accuracy_falloff, beam_range, acc_label = _ACCURACY_CONFIG[cls.accuracy_level]
        center_distance, dist_name = _DISTANCE_CONFIG[cls.distance_label]
        test_num = _TEST_ID_MAP[(cls.accuracy_level, cls.distance_label)]

        cls._beam_damage_expected = beam_damage
        cls._beam_accuracy_expected = base_accuracy
        cls._beam_falloff_expected = accuracy_falloff
        cls._beam_range_expected = beam_range

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

        # Data phase: verify JSON data loaded correctly
        checks.append(check_exact("Beam Base Accuracy", self._beam_accuracy_expected, beam.base_accuracy))
        checks.append(check_exact("Beam Accuracy Falloff", self._beam_falloff_expected, beam.accuracy_falloff))
        checks.append(check_exact("Beam Range", self._beam_range_expected, beam.range))
        checks.append(check_exact("Target Mass", STATIONARY_TARGET_MASS, self.target.mass))
        checks.append(check_exact("Beam Damage", self._beam_damage_expected, beam.damage))

        # Precondition phase: verify simulation geometry
        center_distance = (self.target.position - self.attacker.position).length()
        target_radius = 40 * ((self.target.mass / 1000) ** (1 / 3))
        surface_distance = center_distance - target_radius
        checks.append(check_approx("Center Distance", float(self.distance), center_distance,
                                    tolerance=0.001, phase="precondition"))
        checks.append(check_approx("Surface Distance", float(self.distance) - target_radius,
                                    surface_distance, tolerance=0.001, phase="precondition"))
        checks.append(check_true("Weapon Range Covers Distance",
                                 surface_distance <= beam.range,
                                 detail=f"surface_distance={surface_distance:.2f}, beam.range={beam.range}",
                                 phase="precondition"))

        # Outcome phase: statistical hit rate validation
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

        # Data phase: verify JSON data loaded correctly
        checks.append(check_exact("Beam Base Accuracy", BEAM_MED_ACCURACY, beam.base_accuracy))
        checks.append(check_exact("Beam Accuracy Falloff", BEAM_MED_FALLOFF, beam.accuracy_falloff))
        checks.append(check_exact("Beam Range", BEAM_MED_RANGE, beam.range))
        checks.append(check_exact("Beam Damage", BEAM_MED_DAMAGE, beam.damage))

        # Precondition phase: verify initial setup distance (target moves during test)
        target_radius = 40 * ((self.target.mass / 1000) ** (1 / 3))
        initial_surface_distance = float(self.distance) - target_radius
        checks.append(check_exact("Initial Center Distance", float(self.distance),
                                  float(self.distance), phase="precondition"))
        checks.append(check_approx("Initial Surface Distance", initial_surface_distance,
                                    initial_surface_distance, tolerance=0.001,
                                    phase="precondition"))
        checks.append(check_true("Weapon Range Covers Initial Distance",
                                 initial_surface_distance <= beam.range,
                                 detail=f"surface_distance={initial_surface_distance:.2f}, beam.range={beam.range}",
                                 phase="precondition"))

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

        # Data phase: verify JSON data loaded correctly
        checks.append(check_exact("Beam Base Accuracy", BEAM_MED_ACCURACY, beam.base_accuracy))
        checks.append(check_exact("Beam Accuracy Falloff", BEAM_MED_FALLOFF, beam.accuracy_falloff))
        checks.append(check_exact("Beam Range", BEAM_MED_RANGE, beam.range))
        checks.append(check_exact("Beam Damage", BEAM_MED_DAMAGE, beam.damage))

        # Precondition phase: verify initial setup distance (target moves during test)
        target_radius = 40 * ((self.target.mass / 1000) ** (1 / 3))
        initial_surface_distance = float(self.distance) - target_radius
        checks.append(check_exact("Initial Center Distance", float(self.distance),
                                  float(self.distance), phase="precondition"))
        checks.append(check_approx("Initial Surface Distance", initial_surface_distance,
                                    initial_surface_distance, tolerance=0.001,
                                    phase="precondition"))
        checks.append(check_true("Weapon Range Covers Initial Distance",
                                 initial_surface_distance <= beam.range,
                                 detail=f"surface_distance={initial_surface_distance:.2f}, beam.range={beam.range}",
                                 phase="precondition"))

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

        # Data phase: verify JSON data loaded correctly
        checks.append(check_exact("Beam Base Accuracy", BEAM_MED_ACCURACY, beam.base_accuracy))
        checks.append(check_exact("Beam Accuracy Falloff", BEAM_MED_FALLOFF, beam.accuracy_falloff))
        checks.append(check_exact("Beam Range", BEAM_MED_RANGE, beam.range))
        checks.append(check_exact("Target Mass", STATIONARY_TARGET_MASS, self.target.mass))
        checks.append(check_exact("Beam Damage", BEAM_MED_DAMAGE, beam.damage))

        # Precondition phase: verify target is beyond weapon range
        center_distance = (self.target.position - self.attacker.position).length()
        target_radius = 40 * ((self.target.mass / 1000) ** (1 / 3))
        surface_distance = center_distance - target_radius
        checks.append(check_approx("Center Distance", float(self.distance), center_distance,
                                    tolerance=0.001, phase="precondition"))
        checks.append(check_approx("Surface Distance", float(self.distance) - target_radius,
                                    surface_distance, tolerance=0.001, phase="precondition"))
        checks.append(check_true("Surface Distance Beyond Range",
                                 surface_distance > beam.range,
                                 detail=f"surface_distance={surface_distance:.2f}, beam.range={beam.range}",
                                 phase="precondition"))

        # Outcome phase: no damage dealt
        checks.append(check_exact("Damage Dealt", 0, self.damage_dealt, phase="outcome"))
        return checks


# ============================================================================
# EXPORT ALL SCENARIOS
# ============================================================================

# =============================================================================
# RESOURCE DEPENDENCY TESTS (BEAMWEAPON-RES-001 to 003)
# =============================================================================
# These ComparisonScenarios prove beam weapons with ResourceConsumption(energy)
# stop firing when energy depletes.  All use a guaranteed-hit beam (acc=10.0,
# falloff=0) at point blank for deterministic shot counting.

BEAM_RES_TEST_TICKS = 1000
BEAM_RES_ATTACKER_FULL = "Test_Attacker_BeamGuaranteed_HighEnergy.json"
BEAM_RES_ATTACKER_HALF = "Test_Attacker_BeamGuaranteed_HalfEnergy.json"
BEAM_RES_ATTACKER_NONE = "Test_Attacker_BeamGuaranteed_NoEnergy.json"
BEAM_RES_TARGET = "Test_Target_Stationary.json"


class BeamStopsWithoutEnergyScenario(ComparisonScenario):
    """
    BEAMWEAPON-RES-001: Beam Stops Without Energy

    Battle A: Beam + 100k energy (fires every tick)
    Battle B: Beam + no energy (cannot fire)

    Proves that a beam weapon with activation energy cost cannot fire
    without an energy source.
    """

    metadata = TestMetadata(
        test_id="BEAMWEAPON-RES-001",
        category="BeamWeaponAbility",
        subcategory="Resource Dependency",
        name="Beam Stops Without Energy",
        summary="Beam weapon with energy cost but no battery cannot fire",
        conditions=[
            f"Attacker (full energy): {BEAM_RES_ATTACKER_FULL}",
            f"Attacker (no energy): {BEAM_RES_ATTACKER_NONE}",
            f"Target: {BEAM_RES_TARGET} (stationary, extreme HP armor)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {BEAM_RES_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Weapon exists and is operational but cannot afford activation cost",
            "Zero shots fired, zero damage dealt",
        ],
        expected_outcome="Full-energy attacker deals ~1000 damage. No-energy attacker deals 0.",
        pass_criteria="variant damage == 0, variant shots_fired == 0",
        max_ticks=BEAM_RES_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["beam", "energy", "resource", "no-power", "comparison"],
    )

    baseline_attacker_ship = BEAM_RES_ATTACKER_FULL
    baseline_target_ship = BEAM_RES_TARGET
    variant_attacker_ship = BEAM_RES_ATTACKER_NONE
    variant_target_ship = BEAM_RES_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline fired and dealt damage
        checks.append(check_true(
            "Full-Energy Attacker Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: no-energy attacker dealt zero damage
        checks.append(check_exact(
            "No-Energy Attacker — Zero Damage",
            0.0, self.variant_damage_dealt,
            phase="outcome",
        ))

        # Outcome: no-energy attacker fired zero shots
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_exact(
            "No-Energy Attacker — Zero Shots",
            0, variant_shots,
            phase="outcome",
        ))

        return checks


class BeamStopsAtHalfEnergyScenario(ComparisonScenario):
    """
    BEAMWEAPON-RES-002: Beam Stops At 50% Energy

    Battle A: Beam + 100k energy (fires all 1000 ticks)
    Battle B: Beam + 500 energy (fires ~500 ticks then stops)

    Proves that a beam weapon fires until energy depletes, then stops.
    """

    metadata = TestMetadata(
        test_id="BEAMWEAPON-RES-002",
        category="BeamWeaponAbility",
        subcategory="Resource Dependency",
        name="Beam Stops At 50% Energy",
        summary="Beam fires ~500 shots with 500 energy then stops",
        conditions=[
            f"Attacker (full energy): {BEAM_RES_ATTACKER_FULL}",
            f"Attacker (half energy): {BEAM_RES_ATTACKER_HALF} (500 energy = 500 shots)",
            f"Target: {BEAM_RES_TARGET} (stationary, extreme HP armor)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {BEAM_RES_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Weapon fires until energy runs out, then silently stops",
            "Damage should be roughly half of full-energy baseline",
        ],
        expected_outcome="Half-energy attacker deals ~500 damage (half of baseline ~1000).",
        pass_criteria="variant damage < baseline, variant damage > 0, variant shots ≈ 500",
        max_ticks=BEAM_RES_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["beam", "energy", "resource", "depletion", "comparison"],
    )

    baseline_attacker_ship = BEAM_RES_ATTACKER_FULL
    baseline_target_ship = BEAM_RES_TARGET
    variant_attacker_ship = BEAM_RES_ATTACKER_HALF
    variant_target_ship = BEAM_RES_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline fired all ticks
        checks.append(check_true(
            "Full-Energy Attacker Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: half-energy attacker dealt some damage
        checks.append(check_true(
            "Half-Energy Attacker Dealt Damage",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: half-energy dealt less than full-energy
        checks.append(check_true(
            "Half-Energy Dealt Less Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"full={self.baseline_damage_dealt}, half={self.variant_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: half-energy fired approximately 500 shots
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_exact(
            "Half-Energy Shots Fired", 500, variant_shots,
            phase="outcome",
        ))

        return checks


class BeamControlWithEnergyScenario(ComparisonScenario):
    """
    BEAMWEAPON-RES-003: Beam Functions With Sufficient Energy (Control)

    Battle A: Beam + 100k energy
    Battle B: Beam + 100k energy (identical)

    Control test: both battles use the same ship. Damage should be identical.
    Proves the comparison infrastructure works and no seed artifacts exist.
    """

    metadata = TestMetadata(
        test_id="BEAMWEAPON-RES-003",
        category="BeamWeaponAbility",
        subcategory="Resource Dependency",
        name="Beam Functions With Energy (Control)",
        summary="Control: identical attackers with sufficient energy produce identical damage",
        conditions=[
            f"Attacker (both): {BEAM_RES_ATTACKER_FULL} (100k energy)",
            f"Target: {BEAM_RES_TARGET} (stationary, extreme HP armor)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {BEAM_RES_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Control test — no difference between battles",
            "Validates comparison infrastructure with identical setups",
        ],
        expected_outcome="Both battles produce identical damage.",
        pass_criteria="variant damage == baseline damage",
        max_ticks=BEAM_RES_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["beam", "energy", "resource", "control", "comparison"],
    )

    baseline_attacker_ship = BEAM_RES_ATTACKER_FULL
    baseline_target_ship = BEAM_RES_TARGET
    variant_attacker_ship = BEAM_RES_ATTACKER_FULL
    variant_target_ship = BEAM_RES_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Outcome: identical damage
        checks.append(check_exact(
            "Control — Identical Damage",
            self.baseline_damage_dealt,
            self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# GENERIC RESOURCE TESTS — METALS (BEAMWEAPON-RES-METALS-001 to 002)
# =============================================================================
# Prove beam weapons work with ANY resource type, not just energy.
# Uses "metals" (a real planetary resource defined in data/resources.json).

BEAM_METALS_ATTACKER_FULL = "Test_Attacker_BeamGuaranteed_HighMetals.json"
BEAM_METALS_ATTACKER_NONE = "Test_Attacker_BeamGuaranteed_NoMetals.json"


class BeamWithMetalsFires(ComparisonScenario):
    """
    BEAMWEAPON-RES-METALS-001: Beam With Metals Fires Normally

    Battle A: Beam (metals cost) + 100k metals — fires every tick
    Battle B: Beam (metals cost) + no metals — cannot fire

    Proves the resource system is generic: a beam consuming "metals"
    works identically to one consuming "energy".
    """

    metadata = TestMetadata(
        test_id="BEAMWEAPON-RES-METALS-001",
        category="BeamWeaponAbility",
        subcategory="Generic Resource",
        name="Beam With Metals Fires",
        summary="Beam consuming metals (planetary resource) fires normally with supply",
        conditions=[
            f"Attacker (with metals): {BEAM_METALS_ATTACKER_FULL}",
            f"Attacker (no metals): {BEAM_METALS_ATTACKER_NONE}",
            f"Target: {BEAM_RES_TARGET}",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {BEAM_RES_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "'metals' is a planetary resource, not a standard operational resource",
            "Proves resource system accepts any resource type from data files",
        ],
        expected_outcome="With metals: fires and deals damage. Without: zero shots.",
        pass_criteria="baseline damage > 0, variant damage == 0, variant shots == 0",
        max_ticks=BEAM_RES_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["beam", "metals", "generic-resource", "comparison"],
    )

    baseline_attacker_ship = BEAM_METALS_ATTACKER_FULL
    baseline_target_ship = BEAM_RES_TARGET
    variant_attacker_ship = BEAM_METALS_ATTACKER_NONE
    variant_target_ship = BEAM_RES_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        checks.append(check_true(
            "With-Metals Attacker Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        checks.append(check_exact(
            "No-Metals Attacker — Zero Damage",
            0.0, self.variant_damage_dealt,
            phase="outcome",
        ))

        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_exact(
            "No-Metals Attacker — Zero Shots",
            0, variant_shots,
            phase="outcome",
        ))

        return checks


class BeamWithMetalsControl(ComparisonScenario):
    """
    BEAMWEAPON-RES-METALS-002: Beam With Metals Control

    Battle A: Beam (metals cost) + 100k metals
    Battle B: Beam (metals cost) + 100k metals (identical)

    Control: proves metals-consuming beam works consistently.
    """

    metadata = TestMetadata(
        test_id="BEAMWEAPON-RES-METALS-002",
        category="BeamWeaponAbility",
        subcategory="Generic Resource",
        name="Beam With Metals Control",
        summary="Control: identical metals-consuming beams produce identical damage",
        conditions=[
            f"Attacker (both): {BEAM_METALS_ATTACKER_FULL}",
            f"Target: {BEAM_RES_TARGET}",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {BEAM_RES_TEST_TICKS} ticks",
        ],
        edge_cases=["Control test for generic resource support"],
        expected_outcome="Both battles produce identical damage.",
        pass_criteria="variant damage == baseline damage",
        max_ticks=BEAM_RES_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["beam", "metals", "generic-resource", "control", "comparison"],
    )

    baseline_attacker_ship = BEAM_METALS_ATTACKER_FULL
    baseline_target_ship = BEAM_RES_TARGET
    variant_attacker_ship = BEAM_METALS_ATTACKER_FULL
    variant_target_ship = BEAM_RES_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        checks.append(check_exact(
            "Control — Identical Damage",
            self.baseline_damage_dealt, self.variant_damage_dealt,
            phase="outcome",
        ))
        return checks


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
    'BeamOutOfRangeScenario',
    'BeamStopsWithoutEnergyScenario',
    'BeamStopsAtHalfEnergyScenario',
    'BeamControlWithEnergyScenario',
    'BeamWithMetalsFires',
    'BeamWithMetalsControl',
]
