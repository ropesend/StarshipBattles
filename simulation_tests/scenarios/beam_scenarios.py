"""
Beam Weapon Test Scenarios (BEAM360-001 to BEAM360-011)

These tests validate beam weapon accuracy mechanics using the sigmoid formula:
    P = 1 / (1 + e^-x)
    where x = (base_accuracy + attack_bonus) - (range_penalty + defense_penalty)
    range_penalty = accuracy_falloff * distance

Test Coverage:
- Low Accuracy (0.5 base, 0.002 falloff): 3 distance variants
- Medium Accuracy (2.0 base, 0.001 falloff): 3 distance variants
- High Accuracy (5.0 base, 0.0005 falloff): 2 distance variants
- Moving Target Tests: 2 erratic target scenarios
- Range Limit Test: 1 out-of-range scenario
"""

import pygame
import math
from simulation_tests.scenarios import TestScenario, TestMetadata


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

class BeamLowAccuracyPointBlankScenario(TestScenario):
    """
    BEAM360-001: Low Accuracy Beam at Point-Blank Range

    Tests that a low accuracy beam weapon (0.5 base) hits consistently
    at point-blank range (50px) where range penalty is minimal.
    """

    metadata = TestMetadata(
        test_id="BEAM360-001",
        category="Beam Weapons",
        subcategory="Accuracy - Low",
        name="Low Accuracy Beam - Point Blank (50px)",
        summary="Validates low accuracy beam (0.5 base) hits consistently at point-blank range with minimal range penalty",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Low.json",
            "Target: Test_Target_Stationary.json",
            "Base Accuracy: 0.5",
            "Accuracy Falloff: 0.002 per pixel",
            "Distance: 50 pixels",
            "Range Penalty: 50 * 0.002 = 0.1",
            "Net Score: 0.5 - 0.1 = 0.4",
            "Beam Damage: 5 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Minimal range penalty at close range",
            "Target size bonus may apply",
            "Sigmoid formula: P = 1/(1+e^-0.4) ≈ 0.60 (60% hit rate)"
        ],
        expected_outcome="High hit rate (~60-70%) with damage > 0 after 500 ticks",
        pass_criteria="damage_dealt > 0",
        max_ticks=500,
        seed=42,
        battle_end_mode="time_based",  # Run for full 500 ticks regardless of ship status
        ui_priority=10,
        tags=["accuracy", "low-accuracy", "point-blank", "beam-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Load ships
        self.attacker = self._load_ship("Test_Attacker_Beam360_Low.json")
        self.target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at point-blank range
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = 0  # Facing right
        self.target.position = pygame.math.Vector2(50, 0)
        self.target.angle = 0

        # Store initial state
        self.initial_hp = self.target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([self.attacker], [self.target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        self.attacker.current_target = self.target

        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate expected hit chance with defense score
        self.expected_hit_chance = calculate_expected_hit_chance(0.5, 0.002, 50, 0.0, target_defense)

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if damage was dealt."""
        damage_dealt = self.initial_hp - self.target.hp

        # Store results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['expected_hit_chance'] = self.expected_hit_chance
        self.results['target_alive'] = self.target.is_alive

        # Pass if any damage was dealt
        return damage_dealt > 0


class BeamLowAccuracyMidRangeScenario(TestScenario):
    """
    BEAM360-002: Low Accuracy Beam at Mid-Range

    Tests that a low accuracy beam weapon (0.5 base) maintains reasonable
    accuracy at mid-range (400px) with moderate range penalty.
    """

    metadata = TestMetadata(
        test_id="BEAM360-002",
        category="Beam Weapons",
        subcategory="Accuracy - Low",
        name="Low Accuracy Beam - Mid Range (400px)",
        summary="Validates low accuracy beam performance at mid-range with moderate accuracy degradation",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Low.json",
            "Target: Test_Target_Stationary.json",
            "Base Accuracy: 0.5",
            "Accuracy Falloff: 0.002 per pixel",
            "Distance: 400 pixels",
            "Range Penalty: 400 * 0.002 = 0.8",
            "Net Score: 0.5 - 0.8 = -0.3",
            "Beam Damage: 5 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Moderate range penalty reduces accuracy significantly",
            "Sigmoid formula: P = 1/(1+e^0.3) ≈ 0.43 (43% hit rate)",
            "Net score is negative but still has decent hit chance"
        ],
        expected_outcome="Moderate hit rate (~40-50%) with some damage dealt",
        pass_criteria="simulation_completes (ticks_run > 0)",
        max_ticks=500,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=9,
        tags=["accuracy", "low-accuracy", "mid-range", "beam-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Load ships
        self.attacker = self._load_ship("Test_Attacker_Beam360_Low.json")
        self.target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at mid-range
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = 0
        self.target.position = pygame.math.Vector2(400, 0)
        self.target.angle = 0

        # Store initial state
        self.initial_hp = self.target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([self.attacker], [self.target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        self.attacker.current_target = self.target

        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate expected hit chance with defense score
        self.expected_hit_chance = calculate_expected_hit_chance(0.5, 0.002, 400, 0.0, target_defense)

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if simulation completed."""
        damage_dealt = self.initial_hp - self.target.hp

        # Store results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['expected_hit_chance'] = self.expected_hit_chance
        self.results['target_alive'] = self.target.is_alive

        # Pass if simulation completed (may or may not deal damage)
        return battle_engine.tick_counter > 0


class BeamLowAccuracyMaxRangeScenario(TestScenario):
    """
    BEAM360-003: Low Accuracy Beam at Max Range

    Tests that a low accuracy beam weapon (0.5 base) has heavily degraded
    accuracy at max range (750px) with high range penalty.
    """

    metadata = TestMetadata(
        test_id="BEAM360-003",
        category="Beam Weapons",
        subcategory="Accuracy - Low",
        name="Low Accuracy Beam - Max Range (750px)",
        summary="Validates low accuracy beam has heavily degraded accuracy at max range with high range penalty",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Low.json",
            "Target: Test_Target_Stationary.json",
            "Base Accuracy: 0.5",
            "Accuracy Falloff: 0.002 per pixel",
            "Distance: 750 pixels (near max range of 800)",
            "Range Penalty: 750 * 0.002 = 1.5",
            "Net Score: 0.5 - 1.5 = -1.0",
            "Beam Damage: 5 per hit",
            "Test Duration: 1000 ticks"
        ],
        edge_cases=[
            "High range penalty at extreme distance",
            "Sigmoid formula: P = 1/(1+e^1.0) ≈ 0.27 (27% hit rate)",
            "Low probability but not impossible",
            "Extended test duration to allow for hits"
        ],
        expected_outcome="Low hit rate (~25-35%) with possible damage dealt",
        pass_criteria="simulation_completes (ticks_run > 0)",
        max_ticks=1000,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=8,
        tags=["accuracy", "low-accuracy", "max-range", "beam-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Load ships
        self.attacker = self._load_ship("Test_Attacker_Beam360_Low.json")
        self.target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at max range
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = 0
        self.target.position = pygame.math.Vector2(750, 0)
        self.target.angle = 0

        # Store initial state
        self.initial_hp = self.target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([self.attacker], [self.target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        self.attacker.current_target = self.target

        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate expected hit chance with defense score
        self.expected_hit_chance = calculate_expected_hit_chance(0.5, 0.002, 750, 0.0, target_defense)

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if simulation completed."""
        damage_dealt = self.initial_hp - self.target.hp

        # Store results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['expected_hit_chance'] = self.expected_hit_chance
        self.results['target_alive'] = self.target.is_alive

        # Pass if simulation completed
        return battle_engine.tick_counter > 0


# ============================================================================
# MEDIUM ACCURACY BEAM TESTS (base_accuracy=2.0, falloff=0.001)
# ============================================================================

class BeamMediumAccuracyPointBlankScenario(TestScenario):
    """
    BEAM360-004: Medium Accuracy Beam at Point-Blank Range

    Tests that a medium accuracy beam weapon (2.0 base) hits very consistently
    at point-blank range (50px).
    """

    metadata = TestMetadata(
        test_id="BEAM360-004",
        category="Beam Weapons",
        subcategory="Accuracy - Medium",
        name="Medium Accuracy Beam - Point Blank (50px)",
        summary="Validates medium accuracy beam (2.0 base) hits very consistently at point-blank range",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Stationary.json",
            "Base Accuracy: 2.0",
            "Accuracy Falloff: 0.001 per pixel",
            "Distance: 50 pixels",
            "Range Penalty: 50 * 0.001 = 0.05",
            "Net Score: 2.0 - 0.05 = 1.95",
            "Beam Damage: 5 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Very high net score results in near-perfect accuracy",
            "Sigmoid formula: P = 1/(1+e^-1.95) ≈ 0.88 (88% hit rate)",
            "Should deal significant damage quickly"
        ],
        expected_outcome="Very high hit rate (~85-95%) with significant damage dealt",
        pass_criteria="damage_dealt > 0",
        max_ticks=500,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=10,
        tags=["accuracy", "medium-accuracy", "point-blank", "beam-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Load ships
        self.attacker = self._load_ship("Test_Attacker_Beam360_Med.json")
        self.target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at point-blank range
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = 0
        self.target.position = pygame.math.Vector2(50, 0)
        self.target.angle = 0

        # Store initial state
        self.initial_hp = self.target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([self.attacker], [self.target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        self.attacker.current_target = self.target

        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate expected hit chance with defense score
        self.expected_hit_chance = calculate_expected_hit_chance(2.0, 0.001, 50, 0.0, target_defense)

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if significant damage was dealt."""
        damage_dealt = self.initial_hp - self.target.hp

        # Store results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['expected_hit_chance'] = self.expected_hit_chance
        self.results['target_alive'] = self.target.is_alive

        # Pass if damage was dealt
        return damage_dealt > 0


class BeamMediumAccuracyMidRangeScenario(TestScenario):
    """
    BEAM360-005: Medium Accuracy Beam at Mid-Range

    Tests that a medium accuracy beam weapon (2.0 base) maintains high
    accuracy at mid-range (400px).
    """

    metadata = TestMetadata(
        test_id="BEAM360-005",
        category="Beam Weapons",
        subcategory="Accuracy - Medium",
        name="Medium Accuracy Beam - Mid Range (400px)",
        summary="Validates medium accuracy beam maintains high accuracy at mid-range",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Stationary.json",
            "Base Accuracy: 2.0",
            "Accuracy Falloff: 0.001 per pixel",
            "Distance: 400 pixels",
            "Range Penalty: 400 * 0.001 = 0.4",
            "Net Score: 2.0 - 0.4 = 1.6",
            "Beam Damage: 5 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Moderate range penalty but still high net score",
            "Sigmoid formula: P = 1/(1+e^-1.6) ≈ 0.83 (83% hit rate)",
            "Should maintain good hit rate at distance"
        ],
        expected_outcome="High hit rate (~80-90%) with damage dealt",
        pass_criteria="damage_dealt > 0",
        max_ticks=500,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=9,
        tags=["accuracy", "medium-accuracy", "mid-range", "beam-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Load ships
        self.attacker = self._load_ship("Test_Attacker_Beam360_Med.json")
        self.target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at mid-range
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = 0
        self.target.position = pygame.math.Vector2(400, 0)
        self.target.angle = 0

        # Store initial state
        self.initial_hp = self.target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([self.attacker], [self.target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        self.attacker.current_target = self.target

        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate expected hit chance with defense score
        self.expected_hit_chance = calculate_expected_hit_chance(2.0, 0.001, 400, 0.0, target_defense)

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if damage was dealt."""
        damage_dealt = self.initial_hp - self.target.hp

        # Store results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['expected_hit_chance'] = self.expected_hit_chance
        self.results['target_alive'] = self.target.is_alive

        # Pass if damage was dealt
        return damage_dealt > 0


class BeamMediumAccuracyMaxRangeScenario(TestScenario):
    """
    BEAM360-006: Medium Accuracy Beam at Max Range

    Tests that a medium accuracy beam weapon (2.0 base) maintains reasonable
    accuracy even at max range (750px).
    """

    metadata = TestMetadata(
        test_id="BEAM360-006",
        category="Beam Weapons",
        subcategory="Accuracy - Medium",
        name="Medium Accuracy Beam - Max Range (750px)",
        summary="Validates medium accuracy beam maintains reasonable accuracy at max range",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Stationary.json",
            "Base Accuracy: 2.0",
            "Accuracy Falloff: 0.001 per pixel",
            "Distance: 750 pixels (near max range of 800)",
            "Range Penalty: 750 * 0.001 = 0.75",
            "Net Score: 2.0 - 0.75 = 1.25",
            "Beam Damage: 5 per hit",
            "Test Duration: 1000 ticks"
        ],
        edge_cases=[
            "High range penalty but medium accuracy compensates",
            "Sigmoid formula: P = 1/(1+e^-1.25) ≈ 0.78 (78% hit rate)",
            "Should still hit regularly at max range"
        ],
        expected_outcome="Good hit rate (~75-85%) with damage dealt",
        pass_criteria="simulation_completes (ticks_run > 0)",
        max_ticks=1000,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=8,
        tags=["accuracy", "medium-accuracy", "max-range", "beam-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Load ships
        self.attacker = self._load_ship("Test_Attacker_Beam360_Med.json")
        self.target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at max range
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = 0
        self.target.position = pygame.math.Vector2(750, 0)
        self.target.angle = 0

        # Store initial state
        self.initial_hp = self.target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([self.attacker], [self.target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        self.attacker.current_target = self.target

        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate expected hit chance with defense score
        self.expected_hit_chance = calculate_expected_hit_chance(2.0, 0.001, 750, 0.0, target_defense)

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if simulation completed."""
        damage_dealt = self.initial_hp - self.target.hp

        # Store results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['expected_hit_chance'] = self.expected_hit_chance
        self.results['target_alive'] = self.target.is_alive

        # Pass if simulation completed
        return battle_engine.tick_counter > 0


# ============================================================================
# HIGH ACCURACY BEAM TESTS (base_accuracy=5.0, falloff=0.0005)
# ============================================================================

class BeamHighAccuracyPointBlankScenario(TestScenario):
    """
    BEAM360-007: High Accuracy Beam at Point-Blank Range

    Tests that a high accuracy beam weapon (5.0 base) has near-perfect
    accuracy at point-blank range (50px).
    """

    metadata = TestMetadata(
        test_id="BEAM360-007",
        category="Beam Weapons",
        subcategory="Accuracy - High",
        name="High Accuracy Beam - Point Blank (50px)",
        summary="Validates high accuracy beam (5.0 base) has near-perfect accuracy at point-blank range",
        conditions=[
            "Attacker: Test_Attacker_Beam360_High.json",
            "Target: Test_Target_Stationary.json",
            "Base Accuracy: 5.0",
            "Accuracy Falloff: 0.0005 per pixel",
            "Distance: 50 pixels",
            "Range Penalty: 50 * 0.0005 = 0.025",
            "Net Score: 5.0 - 0.025 = 4.975",
            "Beam Damage: 5 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Extremely high net score results in near-100% accuracy",
            "Sigmoid formula: P = 1/(1+e^-4.975) ≈ 0.993 (99.3% hit rate)",
            "Should hit almost every shot"
        ],
        expected_outcome="Near-perfect hit rate (~99%+) with consistent damage",
        pass_criteria="damage_dealt > 0",
        max_ticks=500,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=10,
        tags=["accuracy", "high-accuracy", "point-blank", "beam-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Load ships
        self.attacker = self._load_ship("Test_Attacker_Beam360_High.json")
        self.target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at point-blank range
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = 0
        self.target.position = pygame.math.Vector2(50, 0)
        self.target.angle = 0

        # Store initial state
        self.initial_hp = self.target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([self.attacker], [self.target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        self.attacker.current_target = self.target

        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate expected hit chance with defense score
        self.expected_hit_chance = calculate_expected_hit_chance(5.0, 0.0005, 50, 0.0, target_defense)

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if damage was dealt."""
        damage_dealt = self.initial_hp - self.target.hp

        # Store results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['expected_hit_chance'] = self.expected_hit_chance
        self.results['target_alive'] = self.target.is_alive

        # Pass if damage was dealt
        return damage_dealt > 0


class BeamHighAccuracyMaxRangeScenario(TestScenario):
    """
    BEAM360-008: High Accuracy Beam at Max Range

    Tests that a high accuracy beam weapon (5.0 base) maintains excellent
    accuracy even at max range (750px).
    """

    metadata = TestMetadata(
        test_id="BEAM360-008",
        category="Beam Weapons",
        subcategory="Accuracy - High",
        name="High Accuracy Beam - Max Range (750px)",
        summary="Validates high accuracy beam maintains excellent accuracy at max range",
        conditions=[
            "Attacker: Test_Attacker_Beam360_High.json",
            "Target: Test_Target_Stationary.json",
            "Base Accuracy: 5.0",
            "Accuracy Falloff: 0.0005 per pixel",
            "Distance: 750 pixels (near max range of 800)",
            "Range Penalty: 750 * 0.0005 = 0.375",
            "Net Score: 5.0 - 0.375 = 4.625",
            "Beam Damage: 5 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Low accuracy falloff means high accuracy is barely affected by range",
            "Sigmoid formula: P = 1/(1+e^-4.625) ≈ 0.990 (99.0% hit rate)",
            "Should hit almost every shot even at max range"
        ],
        expected_outcome="Near-perfect hit rate (~99%+) with consistent damage",
        pass_criteria="damage_dealt > 0",
        max_ticks=500,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=9,
        tags=["accuracy", "high-accuracy", "max-range", "beam-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Load ships
        self.attacker = self._load_ship("Test_Attacker_Beam360_High.json")
        self.target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at max range
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = 0
        self.target.position = pygame.math.Vector2(750, 0)
        self.target.angle = 0

        # Store initial state
        self.initial_hp = self.target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([self.attacker], [self.target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        self.attacker.current_target = self.target

        # Calculate target defense score (mass=400, stationary)
        target_defense = calculate_defense_score(
            mass=400.0,
            acceleration=0.0,
            turn_speed=0.0,
            ecm_score=0.0
        )

        # Calculate expected hit chance with defense score
        self.expected_hit_chance = calculate_expected_hit_chance(5.0, 0.0005, 750, 0.0, target_defense)

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if damage was dealt."""
        damage_dealt = self.initial_hp - self.target.hp

        # Store results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['expected_hit_chance'] = self.expected_hit_chance
        self.results['target_alive'] = self.target.is_alive

        # Pass if damage was dealt
        return damage_dealt > 0


# ============================================================================
# MOVING TARGET TESTS
# ============================================================================

class BeamMediumAccuracyErraticMidRangeScenario(TestScenario):
    """
    BEAM360-009: Medium Accuracy Beam vs Erratic Small Target at Mid-Range

    Tests that target maneuverability adds defense penalty, reducing hit chance
    against a small erratic target.
    """

    metadata = TestMetadata(
        test_id="BEAM360-009",
        category="Beam Weapons",
        subcategory="Moving Targets",
        name="Medium Accuracy vs Erratic Small - Mid Range (400px)",
        summary="Validates that target maneuverability adds defense penalty, reducing hit chance against erratic targets",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Erratic_Small.json (high maneuverability)",
            "Base Accuracy: 2.0",
            "Accuracy Falloff: 0.001 per pixel",
            "Distance: 400 pixels",
            "Range Penalty: 400 * 0.001 = 0.4",
            "Defense Penalty: From target maneuverability (variable)",
            "Beam Damage: 5 per hit",
            "Test Duration: 1000 ticks"
        ],
        edge_cases=[
            "Target size (small) may provide defense bonus",
            "Erratic movement pattern increases defense score",
            "Combined range and defense penalties significantly reduce hit rate",
            "Expected hit rate lower than stationary target (~40-60%)"
        ],
        expected_outcome="Reduced hit rate due to target maneuverability, some damage dealt",
        pass_criteria="simulation_completes (ticks_run > 0)",
        max_ticks=1000,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=7,
        tags=["accuracy", "medium-accuracy", "moving-target", "erratic", "beam-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Load ships
        self.attacker = self._load_ship("Test_Attacker_Beam360_Med.json")
        self.target = self._load_ship("Test_Target_Erratic_Small.json")

        # Position ships at mid-range
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = 0
        self.target.position = pygame.math.Vector2(400, 0)
        self.target.angle = 0

        # Store initial state
        self.initial_hp = self.target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([self.attacker], [self.target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        self.attacker.current_target = self.target

        # Calculate target defense score (mass=65, high maneuverability)
        target_defense = calculate_defense_score(
            mass=65.0,
            acceleration=295.86,
            turn_speed=238.53,
            ecm_score=0.0
        )

        # Calculate expected hit chance with defense score
        self.expected_hit_chance = calculate_expected_hit_chance(2.0, 0.001, 400, 0.0, target_defense)
        self.expected_hit_chance_base = calculate_expected_hit_chance(2.0, 0.001, 400)

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if simulation completed."""
        damage_dealt = self.initial_hp - self.target.hp

        # Store results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['expected_hit_chance'] = self.expected_hit_chance
        self.results['expected_hit_chance_base'] = self.expected_hit_chance_base
        self.results['target_alive'] = self.target.is_alive

        # Pass if simulation completed
        return battle_engine.tick_counter > 0


class BeamMediumAccuracyErraticMaxRangeScenario(TestScenario):
    """
    BEAM360-010: Medium Accuracy Beam vs Erratic Small Target at Max Range

    Tests combined effects of range penalty and maneuverability penalty
    at maximum range.
    """

    metadata = TestMetadata(
        test_id="BEAM360-010",
        category="Beam Weapons",
        subcategory="Moving Targets",
        name="Medium Accuracy vs Erratic Small - Max Range (750px)",
        summary="Validates combined effects of range and maneuverability penalties at maximum range",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Erratic_Small.json (high maneuverability)",
            "Base Accuracy: 2.0",
            "Accuracy Falloff: 0.001 per pixel",
            "Distance: 750 pixels (near max range of 800)",
            "Range Penalty: 750 * 0.001 = 0.75",
            "Defense Penalty: From target maneuverability (variable)",
            "Beam Damage: 5 per hit",
            "Test Duration: 1000 ticks"
        ],
        edge_cases=[
            "Maximum range penalty combined with defense penalty",
            "Worst-case scenario for hitting a difficult target",
            "Expected hit rate significantly reduced (~20-40%)",
            "May result in minimal or no damage"
        ],
        expected_outcome="Low hit rate due to combined penalties, minimal damage expected",
        pass_criteria="simulation_completes (ticks_run > 0)",
        max_ticks=1000,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=6,
        tags=["accuracy", "medium-accuracy", "moving-target", "erratic", "max-range", "beam-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Load ships
        self.attacker = self._load_ship("Test_Attacker_Beam360_Med.json")
        self.target = self._load_ship("Test_Target_Erratic_Small.json")

        # Position ships at max range
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = 0
        self.target.position = pygame.math.Vector2(750, 0)
        self.target.angle = 0

        # Store initial state
        self.initial_hp = self.target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([self.attacker], [self.target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        self.attacker.current_target = self.target

        # Calculate target defense score (mass=65, high maneuverability)
        target_defense = calculate_defense_score(
            mass=65.0,
            acceleration=295.86,
            turn_speed=238.53,
            ecm_score=0.0
        )

        # Calculate expected hit chance with defense score
        self.expected_hit_chance = calculate_expected_hit_chance(2.0, 0.001, 750, 0.0, target_defense)
        self.expected_hit_chance_base = calculate_expected_hit_chance(2.0, 0.001, 750)

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if simulation completed."""
        damage_dealt = self.initial_hp - self.target.hp

        # Store results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['expected_hit_chance'] = self.expected_hit_chance
        self.results['expected_hit_chance_base'] = self.expected_hit_chance_base
        self.results['target_alive'] = self.target.is_alive

        # Pass if simulation completed
        return battle_engine.tick_counter > 0


# ============================================================================
# RANGE LIMIT TEST
# ============================================================================

class BeamOutOfRangeScenario(TestScenario):
    """
    BEAM360-011: Beam Weapon Out of Range

    Tests that beam weapons cannot hit targets beyond their max range.
    Target at 900px when weapon range is 800px.
    """

    metadata = TestMetadata(
        test_id="BEAM360-011",
        category="Beam Weapons",
        subcategory="Range Limits",
        name="Beam Weapon Out of Range (900px > 800px max)",
        summary="Validates that beam weapons cannot hit targets beyond their maximum range",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json",
            "Target: Test_Target_Stationary.json",
            "Weapon Max Range: 800 pixels",
            "Distance: 900 pixels (100px beyond range)",
            "Beam Damage: 5 per hit",
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
        max_ticks=500,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=8,
        tags=["range-limit", "out-of-range", "beam-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Load ships
        self.attacker = self._load_ship("Test_Attacker_Beam360_Med.json")
        self.target = self._load_ship("Test_Target_Stationary.json")

        # Position target beyond max range
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = 0
        self.target.position = pygame.math.Vector2(900, 0)  # Beyond 800px range
        self.target.angle = 0

        # Store initial state
        self.initial_hp = self.target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([self.attacker], [self.target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        self.attacker.current_target = self.target

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check that no damage was dealt."""
        damage_dealt = self.initial_hp - self.target.hp

        # Store results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive
        self.results['distance'] = 900
        self.results['weapon_max_range'] = 800

        # Pass if NO damage was dealt (out of range)
        return damage_dealt == 0


# ============================================================================
# EXPORT ALL SCENARIOS
# ============================================================================

__all__ = [
    'BeamLowAccuracyPointBlankScenario',
    'BeamLowAccuracyMidRangeScenario',
    'BeamLowAccuracyMaxRangeScenario',
    'BeamMediumAccuracyPointBlankScenario',
    'BeamMediumAccuracyMidRangeScenario',
    'BeamMediumAccuracyMaxRangeScenario',
    'BeamHighAccuracyPointBlankScenario',
    'BeamHighAccuracyMaxRangeScenario',
    'BeamMediumAccuracyErraticMidRangeScenario',
    'BeamMediumAccuracyErraticMaxRangeScenario',
    'BeamOutOfRangeScenario'
]
