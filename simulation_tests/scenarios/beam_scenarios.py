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
    MID_TICK_TEST_TICKS,
    MID_PRECISION_MARGIN,
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

            # High-variance tests (low accuracy) need full 100k ticks for ±1% margin.
            # Stable tests (med/high accuracy, hit rate > 75%) use 10k ticks with ±3% margin.
            _HIGH_VARIANCE_HT_TESTS = {"001", "002"}
            if test_num in _HIGH_VARIANCE_HT_TESTS:
                max_ticks = HIGH_TICK_TEST_TICKS
                cls._ht_margin = HIGH_PRECISION_MARGIN
                margin_name = "HIGH_PRECISION"
                name_suffix = " [100k Ticks]"
                summary_detail = "with 100k ticks for +/-1% statistical margin"
                expected_outcome_tpl = "Hit rate within +/-1% of expected with 99% confidence"
            else:
                max_ticks = MID_TICK_TEST_TICKS
                cls._ht_margin = MID_PRECISION_MARGIN
                margin_name = "MID_PRECISION"
                name_suffix = " [10k Ticks]"
                summary_detail = "with 10k ticks for +/-3% statistical margin"
                expected_outcome_tpl = "Hit rate within +/-3% of expected with 99% confidence"

            ui_priority = 11
            subcategory = f"Accuracy - {acc_label} (High-Tick)"
            extra_tags = ["high-tick", "precision"]
            summary_prefix = "High-precision validation"
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
        margin = getattr(self, '_ht_margin', HIGH_PRECISION_MARGIN) if self.high_tick else STANDARD_MARGIN
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


class BeamLowAccuracyMaxRangeHighTickScenario(BeamAccuracyScenario):
    """BEAMWEAPON-003-HT: Low Accuracy Beam at Max Range (High-Tick)"""
    accuracy_level = "low"
    distance_label = "max_range"
    high_tick = True


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

class BeamErraticMidRangeComparisonScenario(ComparisonScenario):
    """
    BEAMWEAPON-009: Defense Penalty — Erratic vs Stationary at Mid Range

    Compares damage dealt to a stationary target vs an erratic small target
    at mid range. The erratic target's maneuverability adds a defense penalty,
    significantly reducing the hit rate.

    Baseline: Medium accuracy beam vs stationary target at 400px
    Variant: Same beam vs erratic small target at 400px
    """

    metadata = TestMetadata(
        test_id="BEAMWEAPON-009",
        category="BeamWeaponAbility",
        subcategory="Moving Targets",
        name="Defense Penalty — Erratic vs Stationary at Mid Range",
        summary="Erratic target takes less damage than stationary due to maneuverability defense penalty",
        conditions=[
            "Baseline: Med accuracy beam vs stationary target at 400px",
            "Variant: Same beam vs erratic small target (mass=65) at 400px",
            "Defense penalty from maneuverability reduces hit rate significantly",
        ],
        edge_cases=[
            "Small erratic target combines size and movement defense bonuses",
        ],
        expected_outcome="Erratic target takes significantly less damage than stationary",
        pass_criteria="variant_damage < baseline_damage, both > 0",
        max_ticks=1000,
        seed=STANDARD_SEED,
        ui_priority=7,
        tags=["accuracy", "defense-penalty", "moving-target", "erratic", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Beam360_Med.json"
    baseline_target_ship = "Test_Target_Stationary.json"
    variant_attacker_ship = "Test_Attacker_Beam360_Med.json"
    variant_target_ship = "Test_Target_Erratic_Small.json"
    distance = MID_RANGE_DISTANCE
    force_fire = True

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Outcome: erratic target should take less damage than stationary
        checks.append(check_true(
            "Erratic Target Takes Less Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"stationary={self.baseline_damage_dealt}, erratic={self.variant_damage_dealt}",
        ))
        # Both should take some damage (beam is in range)
        checks.append(check_true(
            "Stationary Target Took Damage",
            self.baseline_damage_dealt > 0,
            actual=self.baseline_damage_dealt,
        ))
        checks.append(check_true(
            "Erratic Target Took Some Damage",
            self.variant_damage_dealt > 0,
            actual=self.variant_damage_dealt,
        ))
        # Defense penalty should reduce damage by at least 50%
        if self.baseline_damage_dealt > 0:
            reduction = 1.0 - (self.variant_damage_dealt / self.baseline_damage_dealt)
            checks.append(check_true(
                "Defense Penalty Reduces Damage >50%",
                reduction > 0.5,
                actual=f"{reduction:.1%}",
                detail="erratic movement should dodge most shots",
            ))
        return checks


class BeamErraticMaxRangeComparisonScenario(ComparisonScenario):
    """
    BEAMWEAPON-010: Defense Penalty — Erratic vs Stationary at Max Range

    Same as 009 but at near-max range, combining range penalty with
    maneuverability penalty for maximum difficulty.

    Baseline: Medium accuracy beam vs stationary target at 750px
    Variant: Same beam vs erratic small target at 750px
    """

    metadata = TestMetadata(
        test_id="BEAMWEAPON-010",
        category="BeamWeaponAbility",
        subcategory="Moving Targets",
        name="Defense Penalty — Erratic vs Stationary at Max Range",
        summary="Combined range and maneuverability penalties at near-max range",
        conditions=[
            "Baseline: Med accuracy beam vs stationary target at 750px",
            "Variant: Same beam vs erratic small target (mass=65) at 750px",
            "Range penalty + defense penalty = very low hit rate on variant",
        ],
        edge_cases=[
            "Near-max range already reduces hit rate; defense penalty compounds",
        ],
        expected_outcome="Erratic target takes much less damage than stationary at max range",
        pass_criteria="variant_damage < baseline_damage, both >= 0",
        max_ticks=1000,
        seed=STANDARD_SEED,
        ui_priority=6,
        tags=["accuracy", "defense-penalty", "moving-target", "erratic", "max-range", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Beam360_Med.json"
    baseline_target_ship = "Test_Target_Stationary.json"
    variant_attacker_ship = "Test_Attacker_Beam360_Med.json"
    variant_target_ship = "Test_Target_Erratic_Small.json"
    distance = NEAR_MAX_RANGE_DISTANCE
    force_fire = True
    expect_different_damage = True

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Outcome: erratic target should take less damage than stationary
        checks.append(check_true(
            "Erratic Target Takes Less Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"stationary={self.baseline_damage_dealt}, erratic={self.variant_damage_dealt}",
        ))
        # Stationary should take some damage (beam is in range at 750px)
        checks.append(check_true(
            "Stationary Target Took Damage",
            self.baseline_damage_dealt > 0,
            actual=self.baseline_damage_dealt,
        ))
        # Erratic should also take some damage (weapon still fires)
        checks.append(check_true(
            "Erratic Target Took Some Damage",
            self.variant_damage_dealt > 0,
            actual=self.variant_damage_dealt,
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

BEAM_RES_TEST_TICKS = 500
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

    Battle A: Beam + 100k energy (fires all 500 ticks)
    Battle B: Beam + 250 energy (fires ~250 ticks then stops)

    Proves that a beam weapon fires until energy depletes, then stops.
    """

    metadata = TestMetadata(
        test_id="BEAMWEAPON-RES-002",
        category="BeamWeaponAbility",
        subcategory="Resource Dependency",
        name="Beam Stops At 50% Energy",
        summary="Beam fires ~250 shots with 250 energy then stops",
        conditions=[
            f"Attacker (full energy): {BEAM_RES_ATTACKER_FULL}",
            f"Attacker (half energy): {BEAM_RES_ATTACKER_HALF} (250 energy = 250 shots)",
            f"Target: {BEAM_RES_TARGET} (stationary, extreme HP armor)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {BEAM_RES_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Weapon fires until energy runs out, then silently stops",
            "Damage should be roughly half of full-energy baseline",
        ],
        expected_outcome="Half-energy attacker deals ~250 damage (half of baseline ~500).",
        pass_criteria="variant damage < baseline, variant damage > 0, variant shots ≈ 250",
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

        # Outcome: half-energy fired approximately 250 shots
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        checks.append(check_exact(
            "Half-Energy Shots Fired", 250, variant_shots,
            phase="outcome",
        ))

        # Outcome: half-energy fired fewer shots than full-energy baseline
        checks.append(check_true(
            "Half-Energy Fired Fewer Shots",
            variant_shots < baseline_shots,
            detail=f"variant={variant_shots}, baseline={baseline_shots}",
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
