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
from simulation_tests.scenarios import (
    TestMetadata,
    ExactMatchRule,
    DeterministicMatchRule,
    StatisticalTestRule
)
from simulation_tests.scenarios.templates import StaticTargetScenario
from simulation_tests.test_constants import (
    POINT_BLANK_DISTANCE,
    MID_RANGE_DISTANCE,
    STANDARD_TEST_TICKS,
    HIGH_TICK_TEST_TICKS,
    BEAM_LOW_ACCURACY,
    BEAM_LOW_FALLOFF,
    BEAM_LOW_RANGE,
    BEAM_LOW_DAMAGE,
    BEAM_MED_ACCURACY,
    BEAM_MED_FALLOFF,
    BEAM_MED_RANGE,
    BEAM_HIGH_ACCURACY,
    BEAM_HIGH_FALLOFF,
    BEAM_HIGH_RANGE,
    STATIONARY_TARGET_MASS,
    STANDARD_MARGIN,
    HIGH_PRECISION_MARGIN,
    STANDARD_SEED
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


# ============================================================================
# LOW ACCURACY BEAM TESTS (base_accuracy=0.5, falloff=0.002)
# ============================================================================

class BeamLowAccuracyPointBlankScenario(StaticTargetScenario):
    """
    BEAMWEAPON-001: Low Accuracy Beam at Point-Blank Range

    Tests that a low accuracy beam weapon (0.5 base) hits consistently
    at point-blank range where range penalty is minimal.

    Surface distance: 20.53px (center 50px - radius 29.47px)
    Expected hit rate: 53.18%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_Low.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 50

    metadata = TestMetadata(
        test_id="BEAMWEAPON-001",
        category="BeamWeaponAbility",
        subcategory="Accuracy - Low",
        name="Low Accuracy Beam - Point Blank (20.5px surface)",
        summary="Validates low accuracy beam (0.5 base) hits consistently at point-blank range with minimal range penalty",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Low.json",
            "Target: Test_Target_Stationary.json (mass=400)",
            "Base Accuracy: 0.5",
            "Accuracy Falloff: 0.002 per pixel",
            "Center Distance: 50 pixels",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 50 - 29.47 = 20.53 pixels (actual firing distance)",
            "Range Penalty: 20.53 * 0.002 = 0.0411",
            "Defense Penalty: 0.3316 (from mass=400 size score)",
            "Net Score: 0.5 - 0.0411 - 0.3316 = 0.1273",
            "Beam Damage: 1 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Minimal range penalty at close range",
            "Target size affects defense score",
            "Sigmoid formula: P = 1/(1+e^-0.1273) = 0.5318 (53.18% hit rate)"
        ],
        expected_outcome="Hit rate ~53% with damage > 0 after 500 ticks",
        pass_criteria="damage_dealt > 0",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full 500 ticks regardless of ship status
        ui_priority=10,
        tags=["accuracy", "low-accuracy", "point-blank", "beam-weapons"],
        validation_rules=[
            # Exact match validations - comparing test metadata to component data
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_LOW_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_LOW_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=STATIONARY_TARGET_MASS
            ),
            # Layer 1: Formula validation - verify expected hit chance calculation is correct
            # Uses 1e-4 tolerance to account for display rounding (0.5318 vs 0.5317890...)
            DeterministicMatchRule(
                name='Expected Hit Chance',
                path='results.expected_hit_chance',
                expected=0.5318,
                tolerance=1e-4,
                description='P = 1/(1+e^-0.1273) from sigmoid formula with net_score = 0.5 - 0.0411 - 0.3316'
            ),
            # Layer 2: Statistical validation - validates actual test outcomes using TOST equivalence testing
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.5318,  # At surface distance 20.53px (not 50px center distance)
                equivalence_margin=STANDARD_MARGIN,  # ±6% margin for 500-tick test (99% confidence, ~1% failure rate)
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits'
            )
        ],
        outcome_metrics={
            'primary_metric': 'hit_rate',
            'measurements': {
                'ticks_run': {
                    'description': 'Number of simulation ticks (opportunities to fire)',
                    'unit': 'ticks'
                },
                'damage_dealt': {
                    'description': 'Total HP damage dealt to target (1 damage per hit)',
                    'unit': 'hp'
                },
                'hit_rate': {
                    'formula': 'damage_dealt / ticks_run',
                    'description': 'Actual hit rate (shots that connected)',
                    'unit': 'percentage',
                    'expected': 0.5318,  # At surface distance (20.53px) not center distance (50px)
                    'tolerance': 0.05  # p-value threshold
                },
                'expected_hit_rate': {
                    'description': 'Expected hit rate at surface distance (20.53px from mass=400 radius)',
                    'unit': 'percentage',
                    'value': 0.5318
                }
            }
        }
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=STATIONARY_TARGET_MASS,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        # Beam weapons hit the target SURFACE, not center
        # Distance to surface = center_distance - target_radius
        target_mass = STATIONARY_TARGET_MASS
        target_radius = 40 * ((target_mass / 1000) ** (1/3))  # ≈ 29.24px
        center_distance = POINT_BLANK_DISTANCE  # Ships positioned 50px apart
        surface_distance = center_distance - target_radius  # ≈ 20.76px

        # Calculate expected hit chance using SURFACE distance (what combat system uses)
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_LOW_ACCURACY, BEAM_LOW_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if damage was dealt."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if any damage was dealt
        return self.damage_dealt > 0


class BeamLowAccuracyPointBlankHighTickScenario(StaticTargetScenario):
    """
    BEAMWEAPON-001-HT: Low Accuracy Beam at Point-Blank Range (High-Tick Version)

    High-precision validation test with 100,000 ticks for precise statistical validation.
    Uses ±1% equivalence margin with 99% confidence (SE ≈ 0.16%).
    Run occasionally for deep validation before releases.

    Surface distance: 20.53px (center 50px - radius 29.47px for mass=400)
    Expected hit rate: 53.18%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_Low.json"
    target_ship = "Test_Target_Stationary_HighTick.json"
    distance = 50

    metadata = TestMetadata(
        test_id="BEAMWEAPON-001-HT",
        category="BeamWeaponAbility",
        subcategory="Accuracy - Low (High-Tick)",
        name="Low Accuracy Beam - Point Blank (20.5px surface) [100k Ticks]",
        summary="High-precision validation of low accuracy beam with 100k ticks for ±1% statistical margin",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Low.json",
            "Target: Test_Target_Stationary_HighTick.json (1B HP, mass=400 - now identical to standard)",
            "Base Accuracy: 0.5",
            "Accuracy Falloff: 0.002 per pixel",
            "Center Distance: 50 pixels",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 50 - 29.47 = 20.53 pixels (actual firing distance)",
            "Range Penalty: 20.53 * 0.002 = 0.0411",
            "Defense Penalty: 0.3316 (from mass=400 size score - now identical to standard)",
            "Net Score: 0.5 - 0.0411 - 0.3316 = 0.1273",
            "Beam Damage: 1 per hit",
            "Test Duration: 100,000 ticks (HIGH-TICK)"
        ],
        edge_cases=[
            "Ultra-high sample size (100k ticks)",
            "Standard Error: ~0.16% (very precise)",
            "Can detect deviations as small as ±1%",
            "Sigmoid formula: P = 1/(1+e^-0.1273) = 0.5318 (53.18% hit rate)"
        ],
        expected_outcome="Hit rate within ±1% of expected (53.18%) with 99% confidence",
        pass_criteria="Statistical validation passes with p < 0.05",
        max_ticks=HIGH_TICK_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full 100k ticks
        ui_priority=11,  # Show right after regular version
        tags=["accuracy", "low-accuracy", "point-blank", "beam-weapons", "high-tick", "precision"],
        validation_rules=[
            # Exact match validations
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_LOW_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_LOW_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=400.0  # Standard target mass (zero-mass component architecture)
            ),
            # Statistical validation with tight ±1% margin
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.5318,  # At surface distance 20.53px (now identical to standard test with mass=400)
                equivalence_margin=HIGH_PRECISION_MARGIN,  # ±1% margin for 100k-tick test (SE ≈ 0.16%, 99% confidence)
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits (100k samples)'
            )
        ],
        outcome_metrics={
            'primary_metric': 'hit_rate',
            'measurements': {
                'ticks_run': {
                    'description': 'Number of simulation ticks (100,000 high-precision samples)',
                    'unit': 'ticks'
                },
                'damage_dealt': {
                    'description': 'Total HP damage dealt to target (1 damage per hit)',
                    'unit': 'hp'
                },
                'hit_rate': {
                    'formula': 'damage_dealt / ticks_run',
                    'description': 'Actual hit rate (shots that connected)',
                    'unit': 'percentage',
                    'expected': 0.5318,  # At surface distance (20.53px) - now identical to standard test
                    'tolerance': 0.05  # p-value threshold
                },
                'expected_hit_rate': {
                    'description': 'Expected hit rate at surface distance (20.53px from mass=400 radius)',
                    'unit': 'percentage',
                    'value': 0.5318
                }
            }
        }
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary - now identical to standard)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        # Beam weapons hit the target SURFACE, not center
        # Distance to surface = center_distance - target_radius
        target_mass = 400.0
        target_radius = 40 * ((target_mass / 1000) ** (1/3))  # ≈ 29.47px (mass=400)
        center_distance = POINT_BLANK_DISTANCE  # Ships positioned 50px apart
        surface_distance = center_distance - target_radius  # ≈ 20.53px

        # Calculate expected hit chance using SURFACE distance (what combat system uses)
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_LOW_ACCURACY, BEAM_LOW_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if damage was dealt."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if any damage was dealt
        return self.damage_dealt > 0


class BeamLowAccuracyMidRangeScenario(StaticTargetScenario):
    """
    BEAMWEAPON-002: Low Accuracy Beam at Mid-Range

    Tests that a low accuracy beam weapon (0.5 base) maintains reasonable
    accuracy at mid-range (400px) with moderate range penalty.

    Surface distance: 370.53px (center 400px - radius 29.47px)
    Expected hit rate: 36.07%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_Low.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 400

    metadata = TestMetadata(
        test_id="BEAMWEAPON-002",
        category="BeamWeaponAbility",
        subcategory="Accuracy - Low",
        name="Low Accuracy Beam - Mid Range (370.5px surface)",
        summary="Validates low accuracy beam performance at mid-range with moderate accuracy degradation",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Low.json",
            "Target: Test_Target_Stationary.json (mass=400)",
            "Base Accuracy: 0.5",
            "Accuracy Falloff: 0.002 per pixel",
            "Center Distance: 400 pixels",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 400 - 29.47 = 370.53 pixels (actual firing distance)",
            "Range Penalty: 370.53 * 0.002 = 0.7411",
            "Defense Penalty: 0.3316 (from mass=400 size score)",
            "Net Score: 0.5 - 0.7411 - 0.3316 = -0.5727",
            "Sigmoid formula: P = 1/(1+e^0.5727) ≈ 0.3607 (36.07% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Moderate range penalty reduces accuracy significantly",
            "Net score is negative but still has decent hit chance"
        ],
        expected_outcome="Moderate hit rate (~36%) with some damage dealt",
        pass_criteria="simulation_completes (ticks_run > 0)",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=9,
        tags=["accuracy", "low-accuracy", "mid-range", "beam-weapons"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_LOW_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_LOW_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=STATIONARY_TARGET_MASS
            ),
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.3607,
                equivalence_margin=STANDARD_MARGIN,
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits'
            )
        ]
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=STATIONARY_TARGET_MASS,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = STATIONARY_TARGET_MASS
        target_radius = 40 * ((target_mass / 1000) ** (1/3))
        center_distance = MID_RANGE_DISTANCE
        surface_distance = center_distance - target_radius

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_LOW_ACCURACY, BEAM_LOW_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if simulation completed."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if simulation completed (may or may not deal damage)
        return battle_engine.tick_counter > 0


class BeamLowAccuracyMidRangeHighTickScenario(StaticTargetScenario):
    """
    BEAMWEAPON-002-HT: Low Accuracy Beam at Mid-Range (High-Tick Version)

    High-precision validation test with 100,000 ticks for precise statistical validation.
    Uses ±1% equivalence margin with 99% confidence (SE ≈ 0.16%).
    Run occasionally for deep validation before releases.

    Surface distance: 370.53px (center 400px - radius 29.47px for mass=400)
    Expected hit rate: 36.07%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_Low.json"
    target_ship = "Test_Target_Stationary_HighTick.json"
    distance = 400

    metadata = TestMetadata(
        test_id="BEAMWEAPON-002-HT",
        category="BeamWeaponAbility",
        subcategory="Accuracy - Low (High-Tick)",
        name="Low Accuracy Beam - Mid Range (370.5px surface) [100k Ticks]",
        summary="High-precision validation with 100k ticks for ±1% statistical margin",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Low.json",
            "Target: Test_Target_Stationary_HighTick.json (1B HP, mass=400 - now identical to standard)",
            "Base Accuracy: 0.5",
            "Accuracy Falloff: 0.002 per pixel",
            "Center Distance: 400 pixels",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 400 - 29.47 = 370.53 pixels (actual firing distance)",
            "Range Penalty: 370.53 * 0.002 = 0.7411",
            "Defense Penalty: 0.3316 (from mass=400 size score - now identical to standard)",
            "Net Score: 0.5 - 0.7411 - 0.3316 = -0.5727",
            "Sigmoid formula: P = 1/(1+e^0.5727) ≈ 0.3607 (36.07% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 100,000 ticks (HIGH-TICK)"
        ],
        edge_cases=[
            "Ultra-high sample size (100k ticks)",
            "Standard Error: ~0.16% (very precise)",
            "Can detect deviations as small as ±1%",
            "Moderate range penalty reduces accuracy significantly"
        ],
        expected_outcome="Hit rate within ±1% of expected (36.07%) with 99% confidence",
        pass_criteria="Statistical validation passes with p < 0.05",
        max_ticks=HIGH_TICK_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full 100k ticks
        ui_priority=11,  # Show right after regular version
        tags=["accuracy", "low-accuracy", "mid-range", "beam-weapons", "high-tick", "precision"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_LOW_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_LOW_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=400.0  # Standard target mass (zero-mass component architecture)
            ),
            # Statistical validation with tight ±1% margin
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.3607,  # At surface distance 370.53px (now identical to standard test with mass=400)
                equivalence_margin=HIGH_PRECISION_MARGIN,  # ±1% margin for 100k-tick test (SE ≈ 0.16%, 99% confidence)
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits (100k samples)'
            )
        ],
        outcome_metrics={
            'primary_metric': 'hit_rate',
            'measurements': {
                'ticks_run': {
                    'description': 'Number of simulation ticks (100,000 high-precision samples)',
                    'unit': 'ticks'
                },
                'damage_dealt': {
                    'description': 'Total HP damage dealt to target (1 damage per hit)',
                    'unit': 'hp'
                },
                'hit_rate': {
                    'formula': 'damage_dealt / ticks_run',
                    'description': 'Actual hit rate (shots that connected)',
                    'unit': 'percentage',
                    'expected': 0.3607,  # At surface distance (370.53px) - now identical to standard test
                    'tolerance': 0.05  # p-value threshold
                },
                'expected_hit_rate': {
                    'description': 'Expected hit rate at surface distance (370.53px from mass=400 radius)',
                    'unit': 'percentage',
                    'value': 0.3607
                }
            }
        }
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary - now identical to standard)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = 400.0
        target_radius = 40 * ((target_mass / 1000) ** (1/3))  # ≈ 29.47px (mass=400)
        center_distance = MID_RANGE_DISTANCE
        surface_distance = center_distance - target_radius  # ≈ 370.53px

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_LOW_ACCURACY, BEAM_LOW_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if simulation completed."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if simulation completed
        return battle_engine.tick_counter > 0


class BeamLowAccuracyMaxRangeScenario(StaticTargetScenario):
    """
    BEAMWEAPON-003: Low Accuracy Beam at Max Range

    Tests that a low accuracy beam weapon (0.5 base) has heavily degraded
    accuracy at max range (750px) with high range penalty.

    Surface distance: 720.53px (center 750px - radius 29.47px)
    Expected hit rate: 21.86%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_Low.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 750

    metadata = TestMetadata(
        test_id="BEAMWEAPON-003",
        category="BeamWeaponAbility",
        subcategory="Accuracy - Low",
        name="Low Accuracy Beam - Max Range (720.5px surface)",
        summary="Validates low accuracy beam has heavily degraded accuracy at max range with high range penalty",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Low.json",
            "Target: Test_Target_Stationary.json (mass=400)",
            "Base Accuracy: 0.5",
            "Accuracy Falloff: 0.002 per pixel",
            "Center Distance: 750 pixels (near max range of 800)",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 750 - 29.47 = 720.53 pixels (actual firing distance)",
            "Range Penalty: 720.53 * 0.002 = 1.4411",
            "Defense Penalty: 0.3316 (from mass=400 size score)",
            "Net Score: 0.5 - 1.4411 - 0.3316 = -1.2727",
            "Sigmoid formula: P = 1/(1+e^1.2727) ≈ 0.2186 (21.86% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 1000 ticks"
        ],
        edge_cases=[
            "High range penalty at extreme distance",
            "Low probability but not impossible",
            "Extended test duration to allow for hits"
        ],
        expected_outcome="Low hit rate (~22%) with possible damage dealt",
        pass_criteria="simulation_completes (ticks_run > 0)",
        max_ticks=1000,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=8,
        tags=["accuracy", "low-accuracy", "max-range", "beam-weapons"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_LOW_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_LOW_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=STATIONARY_TARGET_MASS
            ),
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.2186,
                equivalence_margin=STANDARD_MARGIN,
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits'
            )
        ]
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=STATIONARY_TARGET_MASS,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = STATIONARY_TARGET_MASS
        target_radius = 40 * ((target_mass / 1000) ** (1/3))
        center_distance = 750.0
        surface_distance = center_distance - target_radius

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_LOW_ACCURACY, BEAM_LOW_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if simulation completed."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if simulation completed
        return battle_engine.tick_counter > 0


# ============================================================================
# MEDIUM ACCURACY BEAM TESTS (base_accuracy=2.0, falloff=0.001)
# ============================================================================

class BeamMediumAccuracyPointBlankScenario(StaticTargetScenario):
    """
    BEAMWEAPON-004: Medium Accuracy Beam at Point-Blank Range

    Tests that a medium accuracy beam weapon (2.0 base) hits very consistently
    at point-blank range (50px).

    Surface distance: 20.53px (center 50px - radius 29.47px)
    Expected hit rate: 83.85%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_Med.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 50

    metadata = TestMetadata(
        test_id="BEAMWEAPON-004",
        category="BeamWeaponAbility",
        subcategory="Accuracy - Medium",
        name="Medium Accuracy Beam - Point Blank (20.5px surface)",
        summary="Validates medium accuracy beam (2.0 base) hits very consistently at point-blank range",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Stationary.json (mass=400)",
            "Base Accuracy: 2.0",
            "Accuracy Falloff: 0.001 per pixel",
            "Center Distance: 50 pixels",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 50 - 29.47 = 20.53 pixels (actual firing distance)",
            "Range Penalty: 20.53 * 0.001 = 0.0205",
            "Defense Penalty: 0.3316 (from mass=400 size score)",
            "Net Score: 2.0 - 0.0205 - 0.3316 = 1.6479",
            "Sigmoid formula: P = 1/(1+e^-1.6479) ≈ 0.8385 (83.85% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Very high net score results in near-perfect accuracy",
            "Should deal significant damage quickly"
        ],
        expected_outcome="Very high hit rate (~84%) with significant damage dealt",
        pass_criteria="damage_dealt > 0",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=10,
        tags=["accuracy", "medium-accuracy", "point-blank", "beam-weapons"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_MED_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_MED_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=STATIONARY_TARGET_MASS
            ),
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.8385,
                equivalence_margin=STANDARD_MARGIN,
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits'
            )
        ]
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=STATIONARY_TARGET_MASS,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = STATIONARY_TARGET_MASS
        target_radius = 40 * ((target_mass / 1000) ** (1/3))
        center_distance = POINT_BLANK_DISTANCE
        surface_distance = center_distance - target_radius

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_MED_ACCURACY, BEAM_MED_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if significant damage was dealt."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if damage was dealt
        return self.damage_dealt > 0


class BeamMediumAccuracyPointBlankHighTickScenario(StaticTargetScenario):
    """
    BEAMWEAPON-004-HT: Medium Accuracy Beam at Point-Blank Range (High-Tick Version)

    High-precision validation test with 100,000 ticks for precise statistical validation.
    Uses ±1% equivalence margin with 99% confidence (SE ≈ 0.16%).
    Run occasionally for deep validation before releases.

    Surface distance: 20.53px (center 50px - radius 29.47px for mass=400)
    Expected hit rate: 83.85%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_Med.json"
    target_ship = "Test_Target_Stationary_HighTick.json"
    distance = 50

    metadata = TestMetadata(
        test_id="BEAMWEAPON-004-HT",
        category="BeamWeaponAbility",
        subcategory="Accuracy - Medium (High-Tick)",
        name="Medium Accuracy Beam - Point Blank (20.5px surface) [100k Ticks]",
        summary="High-precision validation with 100k ticks for ±1% statistical margin",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Stationary_HighTick.json (1B HP, mass=400 - now identical to standard)",
            "Base Accuracy: 2.0",
            "Accuracy Falloff: 0.001 per pixel",
            "Center Distance: 50 pixels",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 50 - 29.47 = 20.53 pixels (actual firing distance)",
            "Range Penalty: 20.53 * 0.001 = 0.0205",
            "Defense Penalty: 0.3316 (from mass=400 size score - now identical to standard)",
            "Net Score: 2.0 - 0.0205 - 0.3316 = 1.6479",
            "Sigmoid formula: P = 1/(1+e^-1.6479) ≈ 0.8385 (83.85% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 100,000 ticks (HIGH-TICK)"
        ],
        edge_cases=[
            "Ultra-high sample size (100k ticks)",
            "Standard Error: ~0.16% (very precise)",
            "Can detect deviations as small as ±1%",
            "Very high net score results in near-perfect accuracy"
        ],
        expected_outcome="Hit rate within ±1% of expected (83.85%) with 99% confidence",
        pass_criteria="Statistical validation passes with p < 0.05",
        max_ticks=HIGH_TICK_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full 100k ticks
        ui_priority=11,  # Show right after regular version
        tags=["accuracy", "medium-accuracy", "point-blank", "beam-weapons", "high-tick", "precision"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_MED_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_MED_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=400.0  # Standard target mass (zero-mass component architecture)
            ),
            # Statistical validation with tight ±1% margin
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.8385,  # At surface distance 20.53px (now identical to standard test with mass=400)
                equivalence_margin=HIGH_PRECISION_MARGIN,  # ±1% margin for 100k-tick test (SE ≈ 0.16%, 99% confidence)
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits (100k samples)'
            )
        ],
        outcome_metrics={
            'primary_metric': 'hit_rate',
            'measurements': {
                'ticks_run': {
                    'description': 'Number of simulation ticks (100,000 high-precision samples)',
                    'unit': 'ticks'
                },
                'damage_dealt': {
                    'description': 'Total HP damage dealt to target (1 damage per hit)',
                    'unit': 'hp'
                },
                'hit_rate': {
                    'formula': 'damage_dealt / ticks_run',
                    'description': 'Actual hit rate (shots that connected)',
                    'unit': 'percentage',
                    'expected': 0.8385,  # At surface distance (20.53px) - now identical to standard test
                    'tolerance': 0.05  # p-value threshold
                },
                'expected_hit_rate': {
                    'description': 'Expected hit rate at surface distance (20.53px from mass=400 radius)',
                    'unit': 'percentage',
                    'value': 0.8385
                }
            }
        }
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary - now identical to standard)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = 400.0
        target_radius = 40 * ((target_mass / 1000) ** (1/3))  # ≈ 29.47px (mass=400)
        center_distance = POINT_BLANK_DISTANCE
        surface_distance = center_distance - target_radius  # ≈ 20.53px

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_MED_ACCURACY, BEAM_MED_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if damage was dealt."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if damage was dealt
        return self.damage_dealt > 0


class BeamMediumAccuracyMidRangeScenario(StaticTargetScenario):
    """
    BEAMWEAPON-005: Medium Accuracy Beam at Mid-Range

    Tests that a medium accuracy beam weapon (2.0 base) maintains high
    accuracy at mid-range (400px).

    Surface distance: 370.53px (center 400px - radius 29.47px)
    Expected hit rate: 78.55%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_Med.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 400

    metadata = TestMetadata(
        test_id="BEAMWEAPON-005",
        category="BeamWeaponAbility",
        subcategory="Accuracy - Medium",
        name="Medium Accuracy Beam - Mid Range (370.5px surface)",
        summary="Validates medium accuracy beam maintains high accuracy at mid-range",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Stationary.json (mass=400)",
            "Base Accuracy: 2.0",
            "Accuracy Falloff: 0.001 per pixel",
            "Center Distance: 400 pixels",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 400 - 29.47 = 370.53 pixels (actual firing distance)",
            "Range Penalty: 370.53 * 0.001 = 0.3705",
            "Defense Penalty: 0.3316 (from mass=400 size score)",
            "Net Score: 2.0 - 0.3705 - 0.3316 = 1.2979",
            "Sigmoid formula: P = 1/(1+e^-1.2979) ≈ 0.7855 (78.55% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Moderate range penalty but still high net score",
            "Should maintain good hit rate at distance"
        ],
        expected_outcome="High hit rate (~79%) with damage dealt",
        pass_criteria="damage_dealt > 0",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=9,
        tags=["accuracy", "medium-accuracy", "mid-range", "beam-weapons"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_MED_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_MED_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=STATIONARY_TARGET_MASS
            ),
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.7855,
                equivalence_margin=STANDARD_MARGIN,
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits'
            )
        ]
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=STATIONARY_TARGET_MASS,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = STATIONARY_TARGET_MASS
        target_radius = 40 * ((target_mass / 1000) ** (1/3))
        center_distance = MID_RANGE_DISTANCE
        surface_distance = center_distance - target_radius

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_MED_ACCURACY, BEAM_MED_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if damage was dealt."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if damage was dealt
        return self.damage_dealt > 0


class BeamMediumAccuracyMidRangeHighTickScenario(StaticTargetScenario):
    """
    BEAMWEAPON-005-HT: Medium Accuracy Beam at Mid-Range (High-Tick Version)

    High-precision validation test with 100,000 ticks for precise statistical validation.
    Uses ±1% equivalence margin with 99% confidence (SE ≈ 0.16%).
    Run occasionally for deep validation before releases.

    Surface distance: 370.53px (center 400px - radius 29.47px for mass=400)
    Expected hit rate: 80.98%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_Med.json"
    target_ship = "Test_Target_Stationary_HighTick.json"
    distance = 400

    metadata = TestMetadata(
        test_id="BEAMWEAPON-005-HT",
        category="BeamWeaponAbility",
        subcategory="Accuracy - Medium (High-Tick)",
        name="Medium Accuracy Beam - Mid Range (370.5px surface) [100k Ticks]",
        summary="High-precision validation with 100k ticks for ±1% statistical margin",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Stationary_HighTick.json (1B HP, mass=400 - now identical to standard)",
            "Base Accuracy: 2.0",
            "Accuracy Falloff: 0.001 per pixel",
            "Center Distance: 400 pixels",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 400 - 29.47 = 370.53 pixels (actual firing distance)",
            "Range Penalty: 366.26 * 0.001 = 0.3663",
            "Defense Penalty: 0.3316 (from mass=400 size score - now identical to standard)",
            "Net Score: 2.0 - 0.3663 - 0.1849 = 1.4488",
            "Sigmoid formula: P = 1/(1+e^-1.4488) ≈ 0.8098 (80.98% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 100,000 ticks (HIGH-TICK)"
        ],
        edge_cases=[
            "Ultra-high sample size (100k ticks)",
            "Standard Error: ~0.16% (very precise)",
            "Can detect deviations as small as ±1%",
            "Moderate range penalty but still high net score"
        ],
        expected_outcome="Hit rate within ±1% of expected (80.98%) with 99% confidence",
        pass_criteria="Statistical validation passes with p < 0.05",
        max_ticks=HIGH_TICK_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full 100k ticks
        ui_priority=11,  # Show right after regular version
        tags=["accuracy", "medium-accuracy", "mid-range", "beam-weapons", "high-tick", "precision"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_MED_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_MED_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=400.0  # Standard target mass (zero-mass component architecture)
            ),
            # Statistical validation with tight ±1% margin
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.7855,  # At surface distance 370.53px (now identical to standard test with mass=400)
                equivalence_margin=HIGH_PRECISION_MARGIN,  # ±1% margin for 100k-tick test (SE ≈ 0.16%, 99% confidence)
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits (100k samples)'
            )
        ],
        outcome_metrics={
            'primary_metric': 'hit_rate',
            'measurements': {
                'ticks_run': {
                    'description': 'Number of simulation ticks (100,000 high-precision samples)',
                    'unit': 'ticks'
                },
                'damage_dealt': {
                    'description': 'Total HP damage dealt to target (1 damage per hit)',
                    'unit': 'hp'
                },
                'hit_rate': {
                    'formula': 'damage_dealt / ticks_run',
                    'description': 'Actual hit rate (shots that connected)',
                    'unit': 'percentage',
                    'expected': 0.7855,  # At surface distance (370.53px) - now identical to standard test
                    'tolerance': 0.05  # p-value threshold
                },
                'expected_hit_rate': {
                    'description': 'Expected hit rate at surface distance (370.53px from mass=400 radius)',
                    'unit': 'percentage',
                    'value': 0.7855
                }
            }
        }
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary - now identical to standard)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = 400.0
        target_radius = 40 * ((target_mass / 1000) ** (1/3))  # ≈ 29.47px (mass=400)
        center_distance = MID_RANGE_DISTANCE
        surface_distance = center_distance - target_radius  # ≈ 370.53px

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_MED_ACCURACY, BEAM_MED_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if damage was dealt."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if damage was dealt
        return self.damage_dealt > 0


class BeamMediumAccuracyMaxRangeScenario(StaticTargetScenario):
    """
    BEAMWEAPON-006: Medium Accuracy Beam at Max Range

    Tests that a medium accuracy beam weapon (2.0 base) maintains reasonable
    accuracy even at max range (750px).

    Surface distance: 720.53px (center 750px - radius 29.47px)
    Expected hit rate: 72.07%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_Med.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 750

    metadata = TestMetadata(
        test_id="BEAMWEAPON-006",
        category="BeamWeaponAbility",
        subcategory="Accuracy - Medium",
        name="Medium Accuracy Beam - Max Range (720.5px surface)",
        summary="Validates medium accuracy beam maintains reasonable accuracy at max range",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Stationary.json (mass=400)",
            "Base Accuracy: 2.0",
            "Accuracy Falloff: 0.001 per pixel",
            "Center Distance: 750 pixels (near max range of 800)",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 750 - 29.47 = 720.53 pixels (actual firing distance)",
            "Range Penalty: 720.53 * 0.001 = 0.7205",
            "Defense Penalty: 0.3316 (from mass=400 size score)",
            "Net Score: 2.0 - 0.7205 - 0.3316 = 0.9479",
            "Sigmoid formula: P = 1/(1+e^-0.9479) ≈ 0.7207 (72.07% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 1000 ticks"
        ],
        edge_cases=[
            "High range penalty but medium accuracy compensates",
            "Should still hit regularly at max range"
        ],
        expected_outcome="Good hit rate (~72%) with damage dealt",
        pass_criteria="simulation_completes (ticks_run > 0)",
        max_ticks=1000,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=8,
        tags=["accuracy", "medium-accuracy", "max-range", "beam-weapons"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_MED_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_MED_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=STATIONARY_TARGET_MASS
            ),
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.7207,
                equivalence_margin=STANDARD_MARGIN,
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits'
            )
        ]
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=STATIONARY_TARGET_MASS,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = STATIONARY_TARGET_MASS
        target_radius = 40 * ((target_mass / 1000) ** (1/3))
        center_distance = 750.0
        surface_distance = center_distance - target_radius

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_MED_ACCURACY, BEAM_MED_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if simulation completed."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if simulation completed
        return battle_engine.tick_counter > 0


class BeamMediumAccuracyMaxRangeHighTickScenario(StaticTargetScenario):
    """
    BEAMWEAPON-006-HT: Medium Accuracy Beam at Max Range (High-Tick Version)

    High-precision validation test with 100,000 ticks for precise statistical validation.
    Uses ±1% equivalence margin with 99% confidence (SE ≈ 0.16%).
    Run occasionally for deep validation before releases.

    Surface distance: 720.53px (center 750px - radius 29.47px for mass=400)
    Expected hit rate: 75.00%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_Med.json"
    target_ship = "Test_Target_Stationary_HighTick.json"
    distance = 750

    metadata = TestMetadata(
        test_id="BEAMWEAPON-006-HT",
        category="BeamWeaponAbility",
        subcategory="Accuracy - Medium (High-Tick)",
        name="Medium Accuracy Beam - Max Range (720.5px surface) [100k Ticks]",
        summary="High-precision validation with 100k ticks for ±1% statistical margin",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Stationary_HighTick.json (1B HP, mass=400 - now identical to standard)",
            "Base Accuracy: 2.0",
            "Accuracy Falloff: 0.001 per pixel",
            "Center Distance: 750 pixels (near max range of 800)",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 750 - 29.47 = 720.53 pixels (actual firing distance)",
            "Range Penalty: 720.53 * 0.001 = 0.7163",
            "Defense Penalty: 0.3316 (from mass=400 size score - now identical to standard)",
            "Net Score: 2.0 - 0.7163 - 0.1849 = 1.0988",
            "Sigmoid formula: P = 1/(1+e^-1.0988) ≈ 0.7500 (75.00% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 100,000 ticks (HIGH-TICK)"
        ],
        edge_cases=[
            "Ultra-high sample size (100k ticks)",
            "Standard Error: ~0.16% (very precise)",
            "Can detect deviations as small as ±1%",
            "High range penalty but medium accuracy compensates"
        ],
        expected_outcome="Hit rate within ±1% of expected (75.00%) with 99% confidence",
        pass_criteria="Statistical validation passes with p < 0.05",
        max_ticks=HIGH_TICK_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full 100k ticks
        ui_priority=11,  # Show right after regular version
        tags=["accuracy", "medium-accuracy", "max-range", "beam-weapons", "high-tick", "precision"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_MED_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_MED_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=400.0  # Standard target mass (zero-mass component architecture)
            ),
            # Statistical validation with tight ±1% margin
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.7207,  # At surface distance 720.53px (now identical to standard test with mass=400)
                equivalence_margin=HIGH_PRECISION_MARGIN,  # ±1% margin for 100k-tick test (SE ≈ 0.16%, 99% confidence)
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits (100k samples)'
            )
        ],
        outcome_metrics={
            'primary_metric': 'hit_rate',
            'measurements': {
                'ticks_run': {
                    'description': 'Number of simulation ticks (100,000 high-precision samples)',
                    'unit': 'ticks'
                },
                'damage_dealt': {
                    'description': 'Total HP damage dealt to target (1 damage per hit)',
                    'unit': 'hp'
                },
                'hit_rate': {
                    'formula': 'damage_dealt / ticks_run',
                    'description': 'Actual hit rate (shots that connected)',
                    'unit': 'percentage',
                    'expected': 0.7207,  # At surface distance (720.53px) - now identical to standard test
                    'tolerance': 0.05  # p-value threshold
                },
                'expected_hit_rate': {
                    'description': 'Expected hit rate at surface distance (720.53px from mass=400 radius)',
                    'unit': 'percentage',
                    'value': 0.7207
                }
            }
        }
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary - now identical to standard)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = 400.0
        target_radius = 40 * ((target_mass / 1000) ** (1/3))  # ≈ 29.47px (mass=400)
        center_distance = 750.0
        surface_distance = center_distance - target_radius  # ≈ 720.53px

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_MED_ACCURACY, BEAM_MED_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if simulation completed."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if simulation completed
        return battle_engine.tick_counter > 0


# ============================================================================
# HIGH ACCURACY BEAM TESTS (base_accuracy=5.0, falloff=0.0005)
# ============================================================================

class BeamHighAccuracyPointBlankScenario(StaticTargetScenario):
    """
    BEAMWEAPON-007: High Accuracy Beam at Point-Blank Range

    Tests that a high accuracy beam weapon (5.0 base) has near-perfect
    accuracy at point-blank range (50px).

    Surface distance: 20.53px (center 50px - radius 29.47px)
    Expected hit rate: 99.06%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_High.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 50

    metadata = TestMetadata(
        test_id="BEAMWEAPON-007",
        category="BeamWeaponAbility",
        subcategory="Accuracy - High",
        name="High Accuracy Beam - Point Blank (20.5px surface)",
        summary="Validates high accuracy beam (5.0 base) has near-perfect accuracy at point-blank range",
        conditions=[
            "Attacker: Test_Attacker_Beam360_High.json",
            "Target: Test_Target_Stationary.json (mass=400)",
            "Base Accuracy: 5.0",
            "Accuracy Falloff: 0.0005 per pixel",
            "Center Distance: 50 pixels",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 50 - 29.47 = 20.53 pixels (actual firing distance)",
            "Range Penalty: 20.53 * 0.0005 = 0.0103",
            "Defense Penalty: 0.3316 (from mass=400 size score)",
            "Net Score: 5.0 - 0.0103 - 0.3316 = 4.6581",
            "Sigmoid formula: P = 1/(1+e^-4.6581) ≈ 0.9906 (99.06% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Extremely high net score results in near-100% accuracy",
            "Should hit almost every shot"
        ],
        expected_outcome="Near-perfect hit rate (~99%+) with consistent damage",
        pass_criteria="damage_dealt > 0",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=10,
        tags=["accuracy", "high-accuracy", "point-blank", "beam-weapons"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_HIGH_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_HIGH_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=STATIONARY_TARGET_MASS
            ),
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.9906,
                equivalence_margin=STANDARD_MARGIN,
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits'
            )
        ]
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=STATIONARY_TARGET_MASS,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = STATIONARY_TARGET_MASS
        target_radius = 40 * ((target_mass / 1000) ** (1/3))
        center_distance = POINT_BLANK_DISTANCE
        surface_distance = center_distance - target_radius

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_HIGH_ACCURACY, BEAM_HIGH_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if damage was dealt."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if damage was dealt
        return self.damage_dealt > 0


class BeamHighAccuracyPointBlankHighTickScenario(StaticTargetScenario):
    """
    BEAMWEAPON-007-HT: High Accuracy Beam at Point-Blank Range (High-Tick Version)

    High-precision validation test with 100,000 ticks for precise statistical validation.
    Uses ±1% equivalence margin with 99% confidence (SE ≈ 0.16%).
    Run occasionally for deep validation before releases.

    Surface distance: 20.53px (center 50px - radius 29.47px for mass=400)
    Expected hit rate: 99.06%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_High.json"
    target_ship = "Test_Target_Stationary_HighTick.json"
    distance = 50

    metadata = TestMetadata(
        test_id="BEAMWEAPON-007-HT",
        category="BeamWeaponAbility",
        subcategory="Accuracy - High (High-Tick)",
        name="High Accuracy Beam - Point Blank (20.5px surface) [100k Ticks]",
        summary="High-precision validation with 100k ticks for ±1% statistical margin",
        conditions=[
            "Attacker: Test_Attacker_Beam360_High.json",
            "Target: Test_Target_Stationary_HighTick.json (1B HP, mass=400 - now identical to standard)",
            "Base Accuracy: 5.0",
            "Accuracy Falloff: 0.0005 per pixel",
            "Center Distance: 50 pixels",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 50 - 29.47 = 20.53 pixels (actual firing distance)",
            "Range Penalty: 20.53 * 0.0005 = 0.0103",
            "Defense Penalty: 0.3316 (from mass=400 size score - now identical to standard)",
            "Net Score: 5.0 - 0.0103 - 0.3316 = 4.6581",
            "Sigmoid formula: P = 1/(1+e^-4.6581) ≈ 0.9906 (99.06% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 100,000 ticks (HIGH-TICK)"
        ],
        edge_cases=[
            "Ultra-high sample size (100k ticks)",
            "Standard Error: ~0.16% (very precise)",
            "Can detect deviations as small as ±1%",
            "Extremely high net score results in near-100% accuracy"
        ],
        expected_outcome="Hit rate within ±1% of expected (99.06%) with 99% confidence",
        pass_criteria="Statistical validation passes with p < 0.05",
        max_ticks=HIGH_TICK_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full 100k ticks
        ui_priority=11,  # Show right after regular version
        tags=["accuracy", "high-accuracy", "point-blank", "beam-weapons", "high-tick", "precision"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_HIGH_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_HIGH_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=400.0  # Standard target mass (zero-mass component architecture)
            ),
            # Statistical validation with tight ±1% margin
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.9906,  # At surface distance 20.53px (now identical to standard test with mass=400)
                equivalence_margin=HIGH_PRECISION_MARGIN,  # ±1% margin for 100k-tick test (SE ≈ 0.16%, 99% confidence)
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits (100k samples)'
            )
        ],
        outcome_metrics={
            'primary_metric': 'hit_rate',
            'measurements': {
                'ticks_run': {
                    'description': 'Number of simulation ticks (100,000 high-precision samples)',
                    'unit': 'ticks'
                },
                'damage_dealt': {
                    'description': 'Total HP damage dealt to target (1 damage per hit)',
                    'unit': 'hp'
                },
                'hit_rate': {
                    'formula': 'damage_dealt / ticks_run',
                    'description': 'Actual hit rate (shots that connected)',
                    'unit': 'percentage',
                    'expected': 0.9906,  # At surface distance (20.53px) - now identical to standard test
                    'tolerance': 0.05  # p-value threshold
                },
                'expected_hit_rate': {
                    'description': 'Expected hit rate at surface distance (20.53px from mass=400 radius)',
                    'unit': 'percentage',
                    'value': 0.9906
                }
            }
        }
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary - now identical to standard)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = 400.0
        target_radius = 40 * ((target_mass / 1000) ** (1/3))  # ≈ 29.47px (mass=400)
        center_distance = POINT_BLANK_DISTANCE
        surface_distance = center_distance - target_radius  # ≈ 20.53px

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_HIGH_ACCURACY, BEAM_HIGH_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if damage was dealt."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if damage was dealt
        return self.damage_dealt > 0


class BeamHighAccuracyMaxRangeScenario(StaticTargetScenario):
    """
    BEAMWEAPON-008: High Accuracy Beam at Max Range

    Tests that a high accuracy beam weapon (5.0 base) maintains excellent
    accuracy even at max range (750px).

    Surface distance: 720.53px (center 750px - radius 29.47px)
    Expected hit rate: 98.66%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_High.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 750

    metadata = TestMetadata(
        test_id="BEAMWEAPON-008",
        category="BeamWeaponAbility",
        subcategory="Accuracy - High",
        name="High Accuracy Beam - Max Range (720.5px surface)",
        summary="Validates high accuracy beam maintains excellent accuracy at max range",
        conditions=[
            "Attacker: Test_Attacker_Beam360_High.json",
            "Target: Test_Target_Stationary.json (mass=400)",
            "Base Accuracy: 5.0",
            "Accuracy Falloff: 0.0005 per pixel",
            "Center Distance: 750 pixels (near max range of 800)",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 750 - 29.47 = 720.53 pixels (actual firing distance)",
            "Range Penalty: 720.53 * 0.0005 = 0.3603",
            "Defense Penalty: 0.3316 (from mass=400 size score)",
            "Net Score: 5.0 - 0.3603 - 0.3316 = 4.3081",
            "Sigmoid formula: P = 1/(1+e^-4.3081) ≈ 0.9866 (98.66% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Low accuracy falloff means high accuracy is barely affected by range",
            "Should hit almost every shot even at max range"
        ],
        expected_outcome="Near-perfect hit rate (~99%+) with consistent damage",
        pass_criteria="damage_dealt > 0",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=9,
        tags=["accuracy", "high-accuracy", "max-range", "beam-weapons"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_HIGH_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_HIGH_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=STATIONARY_TARGET_MASS
            ),
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.9866,
                equivalence_margin=STANDARD_MARGIN,
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits'
            )
        ]
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=STATIONARY_TARGET_MASS,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = STATIONARY_TARGET_MASS
        target_radius = 40 * ((target_mass / 1000) ** (1/3))
        center_distance = 750.0
        surface_distance = center_distance - target_radius

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_HIGH_ACCURACY, BEAM_HIGH_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if damage was dealt."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if damage was dealt
        return self.damage_dealt > 0


class BeamHighAccuracyMaxRangeHighTickScenario(StaticTargetScenario):
    """
    BEAMWEAPON-008-HT: High Accuracy Beam at Max Range (High-Tick Version)

    High-precision validation test with 100,000 ticks for precise statistical validation.
    Uses ±1% equivalence margin with 99% confidence (SE ≈ 0.16%).
    Run occasionally for deep validation before releases.

    Surface distance: 720.53px (center 750px - radius 29.47px for mass=400)
    Expected hit rate: 98.66%
    """

    # Template configuration
    attacker_ship = "Test_Attacker_Beam360_High.json"
    target_ship = "Test_Target_Stationary_HighTick.json"
    distance = 750

    metadata = TestMetadata(
        test_id="BEAMWEAPON-008-HT",
        category="BeamWeaponAbility",
        subcategory="Accuracy - High (High-Tick)",
        name="High Accuracy Beam - Max Range (720.5px surface) [100k Ticks]",
        summary="High-precision validation with 100k ticks for ±1% statistical margin",
        conditions=[
            "Attacker: Test_Attacker_Beam360_High.json",
            "Target: Test_Target_Stationary_HighTick.json (1B HP, mass=400 - now identical to standard)",
            "Base Accuracy: 5.0",
            "Accuracy Falloff: 0.0005 per pixel",
            "Center Distance: 750 pixels (near max range of 800)",
            "Target Radius: 29.47 pixels (from mass=400)",
            "Surface Distance: 750 - 29.47 = 720.53 pixels (actual firing distance)",
            "Range Penalty: 720.53 * 0.0005 = 0.3603",
            "Defense Penalty: 0.3316 (from mass=400 size score - now identical to standard)",
            "Net Score: 5.0 - 0.3603 - 0.3316 = 4.3081",
            "Sigmoid formula: P = 1/(1+e^-4.3081) ≈ 0.9866 (98.66% hit rate)",
            "Beam Damage: 1 per hit",
            "Test Duration: 100,000 ticks (HIGH-TICK)"
        ],
        edge_cases=[
            "Ultra-high sample size (100k ticks)",
            "Standard Error: ~0.16% (very precise)",
            "Can detect deviations as small as ±1%",
            "Low accuracy falloff means high accuracy is barely affected by range"
        ],
        expected_outcome="Hit rate within ±1% of expected (98.66%) with 99% confidence",
        pass_criteria="Statistical validation passes with p < 0.05",
        max_ticks=HIGH_TICK_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",  # Run for full 100k ticks
        ui_priority=11,  # Show right after regular version
        tags=["accuracy", "high-accuracy", "max-range", "beam-weapons", "high-tick", "precision"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_HIGH_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_HIGH_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=400.0  # Standard target mass (zero-mass component architecture)
            ),
            # Statistical validation with tight ±1% margin
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.9866,  # At surface distance 720.53px (now identical to standard test with mass=400)
                equivalence_margin=HIGH_PRECISION_MARGIN,  # ±1% margin for 100k-tick test (SE ≈ 0.16%, 99% confidence)
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits (100k samples)'
            )
        ],
        outcome_metrics={
            'primary_metric': 'hit_rate',
            'measurements': {
                'ticks_run': {
                    'description': 'Number of simulation ticks (100,000 high-precision samples)',
                    'unit': 'ticks'
                },
                'damage_dealt': {
                    'description': 'Total HP damage dealt to target (1 damage per hit)',
                    'unit': 'hp'
                },
                'hit_rate': {
                    'formula': 'damage_dealt / ticks_run',
                    'description': 'Actual hit rate (shots that connected)',
                    'unit': 'percentage',
                    'expected': 0.9866,  # At surface distance (720.53px) - now identical to standard test
                    'tolerance': 0.05  # p-value threshold
                },
                'expected_hit_rate': {
                    'description': 'Expected hit rate at surface distance (720.53px from mass=400 radius)',
                    'unit': 'percentage',
                    'value': 0.9866
                }
            }
        }
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=400, stationary - now identical to standard)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = 400.0
        target_radius = 40 * ((target_mass / 1000) ** (1/3))  # ≈ 29.47px (mass=400)
        center_distance = 750.0
        surface_distance = center_distance - target_radius  # ≈ 720.53px

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_HIGH_ACCURACY, BEAM_HIGH_FALLOFF, surface_distance, 0.0, target_defense)

    def verify(self, battle_engine) -> bool:
        """Check if damage was dealt."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if damage was dealt
        return self.damage_dealt > 0


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
    distance = 400

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
            "Sigmoid formula: P = 1/(1+e^1.5247) ≈ 0.0484 (4.84% hit rate)",
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
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=7,
        tags=["accuracy", "medium-accuracy", "moving-target", "erratic", "beam-weapons"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_MED_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_MED_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=65.0
            ),
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.0484,
                equivalence_margin=STANDARD_MARGIN,
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits'
            )
        ]
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=65, high maneuverability)
        target_defense = calculate_defense_score(
            mass=65.0,
            acceleration=295.86,
            turn_speed=238.53,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = 65.0
        target_radius = 40 * ((target_mass / 1000) ** (1/3))
        center_distance = MID_RANGE_DISTANCE
        surface_distance = center_distance - target_radius

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_MED_ACCURACY, BEAM_MED_FALLOFF, surface_distance, 0.0, target_defense)
        self.expected_hit_chance_base = calculate_expected_hit_chance(BEAM_MED_ACCURACY, BEAM_MED_FALLOFF, surface_distance)

    def verify(self, battle_engine) -> bool:
        """Check if simulation completed."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance
        self.results['expected_hit_chance_base'] = self.expected_hit_chance_base

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if simulation completed
        return battle_engine.tick_counter > 0


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
    distance = 750

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
            "Sigmoid formula: P = 1/(1+e^1.8747) ≈ 0.0347 (3.47% hit rate)",
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
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=6,
        tags=["accuracy", "medium-accuracy", "moving-target", "erratic", "max-range", "beam-weapons"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_MED_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_MED_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=65.0
            ),
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.0347,
                equivalence_margin=STANDARD_MARGIN,
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = number of hits'
            )
        ]
    )

    def custom_setup(self, battle_engine):
        """Calculate test-specific expected hit chance."""
        # Calculate target defense score (mass=65, high maneuverability)
        target_defense = calculate_defense_score(
            mass=65.0,
            acceleration=295.86,
            turn_speed=238.53,
            ecm_score=0.0
        )

        # Calculate target radius (for surface distance calculation)
        target_mass = 65.0
        target_radius = 40 * ((target_mass / 1000) ** (1/3))
        center_distance = 750.0
        surface_distance = center_distance - target_radius

        # Calculate expected hit chance using SURFACE distance
        self.expected_hit_chance = calculate_expected_hit_chance(BEAM_MED_ACCURACY, BEAM_MED_FALLOFF, surface_distance, 0.0, target_defense)
        self.expected_hit_chance_base = calculate_expected_hit_chance(BEAM_MED_ACCURACY, BEAM_MED_FALLOFF, surface_distance)

    def verify(self, battle_engine) -> bool:
        """Check if simulation completed."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['expected_hit_chance'] = self.expected_hit_chance
        self.results['expected_hit_chance_base'] = self.expected_hit_chance_base

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if simulation completed
        return battle_engine.tick_counter > 0


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
    distance = 900

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
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=8,
        tags=["range-limit", "out-of-range", "beam-weapons"],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_MED_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_MED_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=STATIONARY_TARGET_MASS
            )
        ]
    )

    def verify(self, battle_engine) -> bool:
        """Check that no damage was dealt."""
        # Calculate damage dealt (template stores initial_hp automatically)
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store all standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Store test-specific results
        self.results['distance'] = 900
        self.results['weapon_max_range'] = 800

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if NO damage was dealt (out of range)
        return self.damage_dealt == 0


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
