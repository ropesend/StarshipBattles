"""
Propulsion Test Scenarios (PROP-001 to PROP-006)

These tests validate the core propulsion physics for engines and thrusters.
Propulsion is foundational for all combat tests, so these are high priority.

Physics Constants (from game.simulation.physics_constants):
- K_SPEED = 25 (speed multiplier)
- K_THRUST = 2500 (thrust constant for acceleration)
- K_TURN = 25000 (turn rate constant)
- Formula: max_speed = (thrust * K_SPEED) / mass
- Formula: acceleration = (thrust * K_THRUST) / mass²
- Formula: turn_speed = (raw_turn_rate * K_TURN) / mass^1.5

Expected Values Architecture:
- Each test defines EXPECTED values that must match the actual .json data
- Pre-run validation compares expected vs actual BEFORE test execution
- Tests cannot run if data mismatches are detected
- This ensures tests stay in sync with ship/component data files
"""

import pygame
from game.simulation.physics_constants import K_SPEED, K_THRUST, K_TURN
from combat_lab.scenarios import TestScenario, TestMetadata
from combat_lab.scenarios.templates import PropulsionScenario
from combat_lab.scenarios.validation import check_exact, check_approx, check_true


# =============================================================================
# EXPECTED VALUES FOR PROPULSION TESTS
# =============================================================================
# These values MUST match the actual .json ship/component data files.
# If a mismatch is detected, the test will be blocked from running.
#
# Data source: combat_lab/data/ships/*.json
#              combat_lab/data/components.json
# =============================================================================

# -----------------------------------------------------------------------------
# PROP-001: Low Mass Engine Ship (Test_Engine_1x_LowMass.json)
# Hull: hull_test_s (mass=400), Engine: test_engine_no_fuel (thrust=500, mass=0)
# -----------------------------------------------------------------------------
PROP001_SHIP_FILE = "Test_Engine_1x_LowMass.json"
PROP001_HULL_MASS = 400       # hull_test_s mass from components.json
PROP001_ENGINE_MASS = 0       # Zero-mass component architecture
PROP001_TOTAL_MASS = PROP001_HULL_MASS + PROP001_ENGINE_MASS  # 400
PROP001_ENGINE_THRUST = 500   # test_engine_no_fuel thrust

# Calculated values using physics formulas
PROP001_MAX_SPEED = (PROP001_ENGINE_THRUST * K_SPEED) / PROP001_TOTAL_MASS  # 31.25
PROP001_ACCELERATION = (PROP001_ENGINE_THRUST * K_THRUST) / (PROP001_TOTAL_MASS ** 2)  # 7.8125
PROP001_MAX_TICKS = 100  # Test duration

# Predicted test outcomes
# Ship starts at 0, accelerates at PROP001_ACCELERATION until reaching PROP001_MAX_SPEED
# Then travels at max speed for remaining ticks
PROP001_EXPECTED_FINAL_SPEED = PROP001_MAX_SPEED  # 31.25 (ship reaches max speed)

# Distance calculation with acceleration phase:
# - Ticks to reach max speed: max_speed / acceleration = 31.25 / 7.8125 = 4 ticks
# - Distance during acceleration (discrete sum): sum of speeds 0, 7.8125, 15.625, 23.4375 = 46.875 px
#   Then at tick 4, speed becomes 31.25 (capped at max)
# - Remaining ticks at max speed: 100 - 4 = 96 ticks
# - Distance at max speed: 31.25 * 96 = 3000 px
# - Plus tick 4 travel at max speed: 31.25 px
# - Total: 46.875 + 31.25 + 3000 = 3078.125 px
PROP001_TICKS_TO_MAX_SPEED = int(PROP001_MAX_SPEED / PROP001_ACCELERATION)  # 4
PROP001_ACCEL_DISTANCE = sum(PROP001_ACCELERATION * t for t in range(PROP001_TICKS_TO_MAX_SPEED))  # 46.875
PROP001_CRUISE_TICKS = PROP001_MAX_TICKS - PROP001_TICKS_TO_MAX_SPEED  # 96
PROP001_CRUISE_DISTANCE = PROP001_MAX_SPEED * PROP001_CRUISE_TICKS  # 3000
PROP001_EXPECTED_DISTANCE = PROP001_ACCEL_DISTANCE + PROP001_MAX_SPEED + PROP001_CRUISE_DISTANCE  # 3078.125 px

# -----------------------------------------------------------------------------
# PROP-001c: Dual Engine Ship (Test_Engine_2x.json)
# Hull: hull_test_s (mass=400), 2× test_engine_no_fuel (thrust=500 each, stacks to 1000)
# Tests CombatPropulsion ability stacking
# -----------------------------------------------------------------------------
PROP001C_SHIP_FILE = "Test_Engine_2x.json"
PROP001C_HULL_MASS = 400       # hull_test_s mass
PROP001C_ENGINE_COUNT = 2      # Two engines
PROP001C_ENGINE_THRUST_EACH = 500  # Each engine's thrust
PROP001C_TOTAL_THRUST = PROP001C_ENGINE_COUNT * PROP001C_ENGINE_THRUST_EACH  # 1000
PROP001C_TOTAL_MASS = PROP001C_HULL_MASS  # 400 (zero-mass components)

# Calculated values using physics formulas (2x thrust = 2x speed, 2x acceleration)
PROP001C_MAX_SPEED = (PROP001C_TOTAL_THRUST * K_SPEED) / PROP001C_TOTAL_MASS  # 62.5
PROP001C_ACCELERATION = (PROP001C_TOTAL_THRUST * K_THRUST) / (PROP001C_TOTAL_MASS ** 2)  # 15.625
PROP001C_MAX_TICKS = 100  # Same duration as PROP-001

# Predicted test outcomes for dual engines:
# - Ship starts at 0, accelerates at 15.625 until reaching max_speed 62.5
# - Ticks to reach max speed: 62.5 / 15.625 = 4 ticks (same as PROP-001!)
# - Distance during acceleration: sum of speeds 0, 15.625, 31.25, 46.875 = 93.75 px
# - Remaining ticks at max speed: 100 - 4 = 96 ticks
# - Distance at max speed: 62.5 * 96 = 6000 px
# - Plus tick 4 travel at max speed: 62.5 px
# - Total: 93.75 + 62.5 + 6000 = 6156.25 px
PROP001C_EXPECTED_FINAL_SPEED = PROP001C_MAX_SPEED  # 62.5
PROP001C_TICKS_TO_MAX_SPEED = int(PROP001C_MAX_SPEED / PROP001C_ACCELERATION)  # 4
PROP001C_ACCEL_DISTANCE = sum(PROP001C_ACCELERATION * t for t in range(PROP001C_TICKS_TO_MAX_SPEED))  # 93.75
PROP001C_CRUISE_TICKS = PROP001C_MAX_TICKS - PROP001C_TICKS_TO_MAX_SPEED  # 96
PROP001C_CRUISE_DISTANCE = PROP001C_MAX_SPEED * PROP001C_CRUISE_TICKS  # 6000
PROP001C_EXPECTED_DISTANCE = PROP001C_ACCEL_DISTANCE + PROP001C_MAX_SPEED + PROP001C_CRUISE_DISTANCE  # 6156.25 px

# -----------------------------------------------------------------------------
# PROP-002: Multi-ship mass comparison
# From actual ship files: Low=400, Med=3000, High=11000
# -----------------------------------------------------------------------------
PROP002_LOW_SHIP_FILE = "Test_Engine_1x_LowMass.json"
PROP002_MED_SHIP_FILE = "Test_Engine_1x_MedMass.json"
PROP002_HIGH_SHIP_FILE = "Test_Engine_1x_HighMass.json"

PROP002_LOW_MASS = 400        # hull_test_s(400)
PROP002_MED_MASS = 3000       # hull_test_m(1000) + 2×mass_sim_1k
PROP002_HIGH_MASS = 11000     # hull_test_m(1000) + 10×mass_sim_1k
PROP002_THRUST = 500          # All ships have same engine

PROP002_LOW_MAX_SPEED = (PROP002_THRUST * K_SPEED) / PROP002_LOW_MASS    # 31.25
PROP002_MED_MAX_SPEED = (PROP002_THRUST * K_SPEED) / PROP002_MED_MASS    # 4.1667
PROP002_HIGH_MAX_SPEED = (PROP002_THRUST * K_SPEED) / PROP002_HIGH_MASS  # 1.1364

# -----------------------------------------------------------------------------
# PROP-003: Thruster Provides Turn Rate (Test_Thruster_Simple.json)
# Hull: hull_test_s (mass=400), Engine: test_engine_no_fuel, Thruster: test_thruster_std
# Zero-mass component architecture: only hull contributes to mass
# -----------------------------------------------------------------------------
PROP003_SHIP_FILE = "Test_Thruster_Simple.json"
PROP003_TOTAL_MASS = 400      # hull_test_s only (zero-mass components)
PROP003_THRUST = 500          # test_engine_no_fuel thrust
PROP003_RAW_TURN_RATE = 5.0   # test_thruster_std turn_rate
PROP003_MAX_SPEED = 31.25     # (500 * 25) / 400
PROP003_TURN_SPEED = 15.625   # (5.0 * 25000) / 400^1.5 = 15.625
PROP003_MAX_TICKS = 50        # Test duration

# Angle prediction for PROP-003:
# - turn_speed is degrees per 100 ticks
# - degrees_per_tick = turn_speed / 100 = 0.15625
# - Ship starts at 0 degrees, turns left (counter-clockwise = negative rotation)
# - Angle decreases: 0 -> -7.8125 -> wraps to 360 - 7.8125 = 352.1875 degrees
# - Expected angle after 50 ticks = 360 - 7.8125 = 352.1875 degrees
PROP003_DEGREES_PER_TICK = PROP003_TURN_SPEED / 100.0  # 0.15625
PROP003_STARTING_ANGLE = 0.0
PROP003_EXPECTED_ANGLE_CHANGE = PROP003_DEGREES_PER_TICK * PROP003_MAX_TICKS  # 7.8125 (magnitude)
PROP003_EXPECTED_FINAL_ANGLE = 360.0 - PROP003_EXPECTED_ANGLE_CHANGE  # 352.1875 (wrapped)

# -----------------------------------------------------------------------------
# PROP-001b: No Engine ship (Test_No_Engine.json)
# Hull: hull_test_s (mass=400), no engine, no thruster
# -----------------------------------------------------------------------------
PROP001B_SHIP_FILE = "Test_No_Engine.json"
PROP001B_TOTAL_MASS = 400     # hull only
PROP001B_THRUST = 0           # No engine
PROP001B_MAX_SPEED = 0        # Cannot move
PROP001B_TURN_SPEED = 0       # No thruster

# -----------------------------------------------------------------------------
# PROP-003b: Thruster Only ship (Test_Thruster_Only.json)
# Hull: hull_test_s (mass=400), thruster only, no engine
# Expected turn_speed from JSON: 15.625
# -----------------------------------------------------------------------------
PROP003B_SHIP_FILE = "Test_Thruster_Only.json"
PROP003B_TOTAL_MASS = 400     # hull only
PROP003B_THRUST = 0           # No engine
PROP003B_RAW_TURN_RATE = 5.0  # test_thruster_std
PROP003B_MAX_SPEED = 0        # No engine
PROP003B_TURN_SPEED = 15.625  # (5.0 * 25000) / 400^1.5 = 15.625
PROP003B_MAX_TICKS = 50       # Test duration

# Angle prediction for PROP-003b:
# - Same turn_speed as PROP-003 (15.625 deg/100 ticks)
# - Ship turns left (CCW) for 50 ticks
# - Expected final angle: 360 - 7.8125 = 352.1875°
PROP003B_DEGREES_PER_TICK = PROP003B_TURN_SPEED / 100.0  # 0.15625
PROP003B_STARTING_ANGLE = 0.0
PROP003B_EXPECTED_ANGLE_CHANGE = PROP003B_DEGREES_PER_TICK * PROP003B_MAX_TICKS  # 7.8125
PROP003B_EXPECTED_FINAL_ANGLE = 360.0 - PROP003B_EXPECTED_ANGLE_CHANGE  # 352.1875 (CCW wrap)

# -----------------------------------------------------------------------------
# PROP-004: Turn Rate Allows Rotation (Test_Thruster_Simple.json)
# Uses same ship as PROP-003 but runs for 100 ticks and turns RIGHT (CW)
# -----------------------------------------------------------------------------
PROP004_SHIP_FILE = PROP003_SHIP_FILE  # Test_Thruster_Simple.json
PROP004_TOTAL_MASS = PROP003_TOTAL_MASS  # 400
PROP004_TURN_SPEED = PROP003_TURN_SPEED  # 15.625
PROP004_MAX_TICKS = 100       # Test duration

# Angle prediction for PROP-004:
# - turn_speed is 15.625 deg/100 ticks
# - Ship turns RIGHT (clockwise = positive rotation)
# - Expected angle after 100 ticks = 15.625°
PROP004_DEGREES_PER_TICK = PROP004_TURN_SPEED / 100.0  # 0.15625
PROP004_STARTING_ANGLE = 0.0
PROP004_EXPECTED_ANGLE_CHANGE = PROP004_DEGREES_PER_TICK * PROP004_MAX_TICKS  # 15.625
PROP004_EXPECTED_FINAL_ANGLE = PROP004_STARTING_ANGLE + PROP004_EXPECTED_ANGLE_CHANGE  # 15.625 (CW)

# -----------------------------------------------------------------------------
# PROP-004b: Dual Thruster Ship (Test_Thruster_2x.json)
# Hull: hull_test_s (mass=400), 1× engine, 2× test_thruster_std (turn_rate=5.0 each, stacks to 10.0)
# Tests ManeuveringThruster ability stacking
# -----------------------------------------------------------------------------
PROP004B_SHIP_FILE = "Test_Thruster_2x.json"
PROP004B_TOTAL_MASS = 400      # hull_test_s only (zero-mass components)
PROP004B_THRUSTER_COUNT = 2    # Two thrusters
PROP004B_RAW_TURN_RATE_EACH = 5.0  # Each thruster's raw turn rate
PROP004B_TOTAL_RAW_TURN_RATE = PROP004B_THRUSTER_COUNT * PROP004B_RAW_TURN_RATE_EACH  # 10.0
PROP004B_MAX_TICKS = 100       # Same duration as PROP-004

# Calculated values using physics formulas (2x raw_turn_rate = 2x turn_speed)
PROP004B_TURN_SPEED = (PROP004B_TOTAL_RAW_TURN_RATE * K_TURN) / (PROP004B_TOTAL_MASS ** 1.5)  # 31.25

# Angle prediction for PROP-004b:
# - turn_speed is 31.25 deg/100 ticks (2x the single thruster)
# - Ship turns RIGHT (clockwise = positive rotation) for 100 ticks
# - Expected angle after 100 ticks = 31.25°
PROP004B_DEGREES_PER_TICK = PROP004B_TURN_SPEED / 100.0  # 0.3125
PROP004B_STARTING_ANGLE = 0.0
PROP004B_EXPECTED_ANGLE_CHANGE = PROP004B_DEGREES_PER_TICK * PROP004B_MAX_TICKS  # 31.25
PROP004B_EXPECTED_FINAL_ANGLE = PROP004B_STARTING_ANGLE + PROP004B_EXPECTED_ANGLE_CHANGE  # 31.25 (CW)

# -----------------------------------------------------------------------------
# PROP-005: Mass Affects Turn Rate comparison
# Low mass: Test_Thruster_Simple.json (hull_test_s = 400)
# High mass: Test_Thruster_HighMass.json (hull_test_m + 2×mass_sim_1k = 3000)
# Both use same thruster (test_thruster_std, raw_turn_rate=5.0)
# Formula: turn_speed = (raw_turn_rate * K_TURN) / mass^1.5
# -----------------------------------------------------------------------------
PROP005_LOW_SHIP_FILE = "Test_Thruster_Simple.json"
PROP005_HIGH_SHIP_FILE = "Test_Thruster_HighMass.json"
PROP005_RAW_TURN_RATE = 5.0   # test_thruster_std for both ships
PROP005_MAX_TICKS = 50        # Test duration

PROP005_LOW_MASS = 400        # hull_test_s
PROP005_HIGH_MASS = 3000      # hull_test_m(1000) + 2×mass_sim_1k(1000) = 3000

# Calculate expected turn speeds using formula
PROP005_LOW_TURN_SPEED = (PROP005_RAW_TURN_RATE * K_TURN) / (PROP005_LOW_MASS ** 1.5)   # 15.625
PROP005_HIGH_TURN_SPEED = (PROP005_RAW_TURN_RATE * K_TURN) / (PROP005_HIGH_MASS ** 1.5)  # 0.7608

# Expected ratio: low_turn_speed / high_turn_speed = (high_mass / low_mass)^1.5
PROP005_EXPECTED_RATIO = (PROP005_HIGH_MASS / PROP005_LOW_MASS) ** 1.5  # 20.54

# Angle predictions for PROP-005:
# - Both ships turn RIGHT (clockwise = positive rotation) for 50 ticks
# - Low mass ship: 0.15625°/tick × 50 = 7.8125°
# - High mass ship: 0.007608°/tick × 50 = 0.3804°
PROP005_LOW_DEGREES_PER_TICK = PROP005_LOW_TURN_SPEED / 100.0  # 0.15625
PROP005_HIGH_DEGREES_PER_TICK = PROP005_HIGH_TURN_SPEED / 100.0  # 0.007608
PROP005_STARTING_ANGLE = 0.0
PROP005_LOW_EXPECTED_ANGLE_CHANGE = PROP005_LOW_DEGREES_PER_TICK * PROP005_MAX_TICKS  # 7.8125
PROP005_HIGH_EXPECTED_ANGLE_CHANGE = PROP005_HIGH_DEGREES_PER_TICK * PROP005_MAX_TICKS  # 0.3804
PROP005_LOW_EXPECTED_FINAL_ANGLE = PROP005_STARTING_ANGLE + PROP005_LOW_EXPECTED_ANGLE_CHANGE  # 7.8125 (CW)
PROP005_HIGH_EXPECTED_FINAL_ANGLE = PROP005_STARTING_ANGLE + PROP005_HIGH_EXPECTED_ANGLE_CHANGE  # 0.3804 (CW)


class PropEngineAccelerationScenario(PropulsionScenario):
    """
    PROP-001: Engine Provides Thrust - Ship Accelerates

    Tests that an engine component provides thrust value and that a ship
    with an engine accelerates from rest. This is the most fundamental
    propulsion test.

    Pre-Run Validation:
    - Data values from .json files are validated against expected values
    - Calculated physics values are validated against formulas
    - Test will not run if any validation fails
    """

    metadata = TestMetadata(
        test_id="PROP-001",
        category="Propulsion",
        subcategory="Engine Physics",
        name="Engine provides thrust - ship accelerates",
        summary="Validates that engine component provides thrust and ship accelerates from rest over time",
        conditions=[
            # These are now generated from data_expectations and setup_conditions
            # Kept for backward compatibility but will be replaced by structured data
            f"Ship: {PROP001_SHIP_FILE}",
            f"Engine thrust: {PROP001_ENGINE_THRUST}",
            f"Ship mass: {PROP001_TOTAL_MASS} (hull {PROP001_HULL_MASS} + engine {PROP001_ENGINE_MASS})",
            "Initial velocity: 0",
            f"Expected max_speed: {PROP001_MAX_SPEED} px/s",
            f"Expected acceleration_rate: {PROP001_ACCELERATION} px/s²",
            "Test duration: 100 ticks"
        ],
        edge_cases=[
            "Starting from complete rest (velocity = 0)",
            "Minimal ship configuration (engine + hull only)",
            "No fuel consumption (test_engine_no_fuel)"
        ],
        expected_outcome="Ship velocity increases from 0 to positive value over 100 ticks",
        pass_criteria="final_velocity > initial_velocity AND final_velocity > 0",
        max_ticks=100,
        seed=42,
        ui_priority=10,
        tags=["propulsion", "engine", "acceleration", "foundational"],
    )

    # Configuration attributes
    ship_file = PROP001_SHIP_FILE
    thrust_forward = True

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        checks.extend(self._propulsion_data_checks(PROP001_TOTAL_MASS, PROP001_ENGINE_THRUST))
        # Precondition
        checks.append(check_approx("Starting Angle", 0.0, self.start_angle, phase="precondition"))
        checks.append(check_approx("Starting Position X", 0.0, self.start_position.x, phase="precondition"))
        checks.append(check_approx("Starting Position Y", 0.0, self.start_position.y, phase="precondition"))
        checks.extend(self._propulsion_outcome_checks(PROP001_MAX_SPEED, PROP001_EXPECTED_FINAL_SPEED, PROP001_EXPECTED_DISTANCE))
        return checks


class PropDualEngineScenario(PropulsionScenario):
    """
    PROP-001c: Dual Engines - Ability Stacking

    Tests that CombatPropulsion abilities from multiple engines stack additively.
    Two engines with 500 thrust each should provide 1000 total thrust, resulting
    in 2x max_speed and 2x acceleration compared to a single engine.
    """

    metadata = TestMetadata(
        test_id="PROP-001c",
        category="Propulsion",
        subcategory="Engine Physics",
        name="Dual engines stack thrust",
        summary="Validates that CombatPropulsion abilities from multiple engines stack additively",
        conditions=[
            f"Ship: Test_Engine_2x (2× test_engine_no_fuel)",
            f"Ship mass: {PROP001C_TOTAL_MASS} (hull_test_s, zero-mass components)",
            f"Engine count: {PROP001C_ENGINE_COUNT}",
            f"Thrust per engine: {PROP001C_ENGINE_THRUST_EACH}",
            f"Total thrust: {PROP001C_TOTAL_THRUST} (stacked)",
            f"Formula: max_speed = (thrust × K_SPEED) / mass"
        ],
        edge_cases=[
            "Multiple identical engines",
            "Thrust values stack additively",
            "2x thrust = 2x max_speed (same mass)"
        ],
        expected_outcome=f"Ship reaches {PROP001C_MAX_SPEED} max_speed (2× single engine) and travels {PROP001C_EXPECTED_DISTANCE:.2f} px",
        pass_criteria=f"max_speed = {PROP001C_MAX_SPEED} AND distance = {PROP001C_EXPECTED_DISTANCE:.2f}",
        max_ticks=PROP001C_MAX_TICKS,
        seed=42,
        ui_priority=9,
        tags=["propulsion", "engine", "stacking", "ability"],
    )

    # Configuration attributes
    ship_file = PROP001C_SHIP_FILE
    thrust_forward = True

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        checks.extend(self._propulsion_data_checks(PROP001C_TOTAL_MASS, PROP001C_TOTAL_THRUST))
        # Precondition
        checks.append(check_approx("Starting Angle", 0.0, self.start_angle, phase="precondition"))
        checks.append(check_approx("Starting Position X", 0.0, self.start_position.x, phase="precondition"))
        checks.append(check_approx("Starting Position Y", 0.0, self.start_position.y, phase="precondition"))
        checks.extend(self._propulsion_outcome_checks(PROP001C_MAX_SPEED, PROP001C_EXPECTED_FINAL_SPEED, PROP001C_EXPECTED_DISTANCE))
        return checks


class PropThrustMassRatioScenario(TestScenario):
    """
    PROP-002: Thrust/Mass Ratio Affects Max Speed

    Tests that the speed formula max_speed = (thrust * K_SPEED) / mass
    correctly scales with mass. Ships with same thrust but different
    mass should have proportionally different speeds.
    """

    metadata = TestMetadata(
        test_id="PROP-002",
        category="Propulsion",
        subcategory="Engine Physics",
        name="Thrust/mass ratio affects max speed",
        summary="Validates that max_speed scales inversely with mass according to formula: max_speed = (thrust * K_SPEED) / mass",
        conditions=[
            "Test 3 ships: LowMass (40), MedMass (2220), HighMass (10220)",
            "All ships have same engine thrust: 500",
            "Formula: max_speed = (500 * 25) / mass",
            f"Expected speeds: {PROP002_LOW_MAX_SPEED:.2f}, {PROP002_MED_MAX_SPEED:.4f}, {PROP002_HIGH_MAX_SPEED:.4f} px/s",
            "Speed should scale inversely with mass"
        ],
        edge_cases=[
            "Wide mass range (40x to 10000x)",
            "Linear inverse relationship (speed ∝ 1/mass)"
        ],
        expected_outcome="Speed decreases linearly as mass increases (inverse proportionality)",
        pass_criteria="speed ratio matches inverse mass ratio exactly (1e-9 tolerance)",
        max_ticks=200,
        seed=42,
        ui_priority=9,
        tags=["propulsion", "engine", "mass", "scaling", "foundational"],
    )

    _SHIP_FILES = [
        ("low", "Test_Engine_1x_LowMass.json", (0, 0)),
        ("med", "Test_Engine_1x_MedMass.json", (0, 200)),
        ("high", "Test_Engine_1x_HighMass.json", (0, 400)),
    ]

    def to_spec(self, registries=None):
        """PROJ-269: compile to a single-team 3-ship BattleSpec."""
        from game.core.math import Vector2
        from game.simulation.battle_spec import ( BattleSpec, CombatPolicies, EntryVector,
            ShipSpec, SquadronSpec, TaskForceSpec, TeamSpec,
        )
        from game.simulation.combat.boundary import UnboundedRegion
        from game.simulation.combat.formation import FormationShape, FormationSpec
        from game.simulation.combat.modifier_stack import ModifierStack
        from game.simulation.combat.telemetry import TelemetryLevel

        _ = registries
        ships = tuple(
            ShipSpec(
                instance_id=f"{self.metadata.test_id}:{role}",
                design_id=filename,
                theme_id="Federation",
                name=f"{self.metadata.test_id}-{role}",
                position=Vector2(float(x), float(y)),
                angle=0.0,
                velocity=Vector2(0.0, 0.0),
                components=(),
                scenario_role=role,
            )
            for role, filename, (x, y) in self._SHIP_FILES
        )
        formation = FormationSpec(
            shape=FormationShape.CUSTOM,
            spacing=200.0,
            custom_positions=tuple(
                Vector2(float(x), float(y)) for _, _, (x, y) in self._SHIP_FILES
            ),
        )
        team = TeamSpec(
            team_id=0,
            name="Propulsion",
            entry_vector=EntryVector(origin=Vector2(0.0, 0.0), facing=0.0),
            fleet_hierarchy=(
                TaskForceSpec(
                    task_force_id="tf-prop",
                    formation=formation,
                    policies=CombatPolicies(),
                    squadrons=(
                        SquadronSpec(
                            squadron_id="sq-prop",
                            policies=CombatPolicies(),
                            ships=ships,
                        ),
                    ),
                ),
            ),
        )
        return BattleSpec(
            seed=self.metadata.seed,
            telemetry_level=TelemetryLevel.DETAILED,
            boundary=UnboundedRegion(),
            end_condition=self._create_end_condition(),
            absolute_max_ticks=max(self.metadata.max_ticks * 10, 1000),
            teams=(team,),
            modifier_stack=ModifierStack.empty(),
            post_battle_hook=None,
        )

    def wire_ships(self, ships_by_role, *, engine=None, initial_state=None):
        """PROJ-269: cache per-ship refs + assign test_straight_line policy."""
        _ = engine, initial_state
        self.low_mass = ships_by_role["low"]
        self.med_mass = ships_by_role["med"]
        self.high_mass = ships_by_role["high"]
        for ship in (self.low_mass, self.med_mass, self.high_mass):
            ship.movement_policy = "test_straight_line"
        # Sanity-check all ships share identical thrust (legacy assertion).
        assert abs(self.low_mass.total_thrust - self.med_mass.total_thrust) < 0.1, \
            "All test ships should have identical thrust"
        assert abs(self.med_mass.total_thrust - self.high_mass.total_thrust) < 0.1, \
            "All test ships should have identical thrust"
        self.initial_positions = {
            "low": self.low_mass.position.copy(),
            "med": self.med_mass.position.copy(),
            "high": self.high_mass.position.copy(),
        }


    def collect_results(self, outcome, telemetry=None):
        """Populate measurement attributes for the three ships."""
        self.results['ticks_run'] = outcome.duration_ticks

    def validate(self, outcome, telemetry=None) -> list:
        checks = []
        ticks = self.results.get('ticks_run', 0)
        checks.append(check_true("Simulation Ran", ticks > 0, actual=ticks))

        # Data: verify all ships have same thrust
        checks.append(check_exact("Low Mass Ship Mass", PROP002_LOW_MASS, self.low_mass.mass))
        checks.append(check_exact("Med Mass Ship Mass", PROP002_MED_MASS, self.med_mass.mass))
        checks.append(check_exact("High Mass Ship Mass", PROP002_HIGH_MASS, self.high_mass.mass))
        checks.append(check_exact("Low Mass Thrust", PROP002_THRUST, self.low_mass.total_thrust))
        checks.append(check_exact("Med Mass Thrust", PROP002_THRUST, self.med_mass.total_thrust))
        checks.append(check_exact("High Mass Thrust", PROP002_THRUST, self.high_mass.total_thrust))

        # Outcome: verify max speeds match formula
        checks.append(check_approx("Low Mass Max Speed", PROP002_LOW_MAX_SPEED, self.low_mass.max_speed))
        checks.append(check_approx("Med Mass Max Speed", PROP002_MED_MAX_SPEED, self.med_mass.max_speed))
        checks.append(check_approx("High Mass Max Speed", PROP002_HIGH_MAX_SPEED, self.high_mass.max_speed))

        # Outcome: verify speed ordering (low mass = highest speed)
        ordering_correct = (self.high_mass.max_speed < self.med_mass.max_speed < self.low_mass.max_speed)
        checks.append(check_true("Speed Ordering", ordering_correct,
                                 detail="Expected: high_mass < med_mass < low_mass", phase="outcome"))

        # Outcome: verify speed ratio matches inverse mass ratio
        speed_ratio = self.low_mass.max_speed / self.med_mass.max_speed
        mass_ratio = self.med_mass.mass / self.low_mass.mass
        checks.append(check_approx("Speed/Mass Ratio", mass_ratio, speed_ratio))

        return checks


class PropThrusterTurnRateScenario(PropulsionScenario):
    """
    PROP-003: Thruster Provides Turn Rate

    Tests that ManeuveringThruster component provides turn rate and
    that turn_speed is calculated correctly according to the formula.
    Also verifies ship rotates to the predicted angle over test duration.
    """

    metadata = TestMetadata(
        test_id="PROP-003",
        category="Propulsion",
        subcategory="Thruster Physics",
        name="Thruster provides turn rate",
        summary="Validates that ManeuveringThruster component provides turn rate and turn_speed is calculated correctly",
        conditions=[
            f"Ship: Test_Thruster_Simple (hull + engine + thruster)",
            f"Ship mass: {PROP003_TOTAL_MASS} (hull_test_s, zero-mass components)",
            f"Thruster raw turn_rate: {PROP003_RAW_TURN_RATE}",
            f"Formula: turn_speed = (raw_turn_rate × K_TURN) / mass^1.5",
            f"K_TURN = {K_TURN}",
            f"Expected turn_speed: {PROP003_TURN_SPEED}"
        ],
        edge_cases=[
            "Minimal ship configuration (thruster + engine + hull)",
            "Turn speed scales with mass^1.5 (stronger than linear)",
            "No resource consumption"
        ],
        expected_outcome=f"Ship rotates from {PROP003_STARTING_ANGLE}° to {PROP003_EXPECTED_FINAL_ANGLE}° over {PROP003_MAX_TICKS} ticks",
        pass_criteria=f"turn_speed = {PROP003_TURN_SPEED} AND final_angle = {PROP003_EXPECTED_FINAL_ANGLE}°",
        max_ticks=PROP003_MAX_TICKS,
        seed=42,
        ui_priority=8,
        tags=["propulsion", "thruster", "turn_rate", "foundational"],
    )

    # Configuration attributes
    ship_file = PROP003_SHIP_FILE
    turn_left = True

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Ship Mass", PROP003_TOTAL_MASS, self.ship.mass))
        checks.append(check_exact("Engine Thrust", PROP003_THRUST, self.ship.total_thrust))
        checks.append(check_approx("Turn Speed", PROP003_TURN_SPEED, self.ship.turn_speed, phase="data"))
        # Precondition
        checks.append(check_approx("Starting Angle", PROP003_STARTING_ANGLE, self.start_angle, phase="precondition"))
        # Outcome
        checks.append(check_approx("Final Angle", PROP003_EXPECTED_FINAL_ANGLE, self.final_angle, tolerance=0.01))
        return checks


class PropThrusterRotationScenario(PropulsionScenario):
    """
    PROP-004: Turn Rate Allows Rotation

    Tests that a ship with a thruster can actually rotate over time
    at the expected rate. This verifies the integration of turn_speed
    into the physics simulation.
    """

    metadata = TestMetadata(
        test_id="PROP-004",
        category="Propulsion",
        subcategory="Thruster Physics",
        name="Turn rate allows rotation",
        summary="Validates that ship with thruster rotates over time at expected rate based on turn_speed",
        conditions=[
            f"Ship: Test_Thruster_Simple (hull + engine + thruster)",
            f"Ship mass: {PROP004_TOTAL_MASS} (hull_test_s, zero-mass components)",
            f"Turn speed: {PROP004_TURN_SPEED} deg/100 ticks",
            f"Turn command: right (CW) each tick for {PROP004_MAX_TICKS} ticks",
            f"Expected rotation: {PROP004_EXPECTED_ANGLE_CHANGE}°"
        ],
        edge_cases=[
            "Starting from zero rotation",
            "Continuous rotation over multiple ticks",
            "Angle wrapping at 360 degrees"
        ],
        expected_outcome=f"Ship rotates from {PROP004_STARTING_ANGLE}° to {PROP004_EXPECTED_FINAL_ANGLE}° over {PROP004_MAX_TICKS} ticks",
        pass_criteria=f"turn_speed = {PROP004_TURN_SPEED} AND final_angle = {PROP004_EXPECTED_FINAL_ANGLE}°",
        max_ticks=PROP004_MAX_TICKS,
        seed=42,
        ui_priority=8,
        tags=["propulsion", "thruster", "rotation", "physics"],
    )

    # Configuration attributes
    ship_file = PROP004_SHIP_FILE
    turn_right = True

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Ship Mass", PROP004_TOTAL_MASS, self.ship.mass))
        checks.append(check_approx("Turn Speed", PROP004_TURN_SPEED, self.ship.turn_speed, phase="data"))
        # Precondition
        checks.append(check_approx("Starting Angle", PROP004_STARTING_ANGLE, self.start_angle, phase="precondition"))
        checks.append(check_approx("Starting Position X", 0.0, self.start_position.x, phase="precondition"))
        checks.append(check_approx("Starting Position Y", 0.0, self.start_position.y, phase="precondition"))
        # Outcome
        checks.append(check_approx("Final Angle", PROP004_EXPECTED_FINAL_ANGLE, self.final_angle, tolerance=0.01))
        return checks


class PropDualThrusterScenario(PropulsionScenario):
    """
    PROP-004b: Dual Thrusters - Ability Stacking

    Tests that ManeuveringThruster abilities from multiple thrusters stack additively.
    Two thrusters with 5.0 raw_turn_rate each should provide 10.0 total raw_turn_rate,
    resulting in 2x turn_speed compared to a single thruster.
    """

    metadata = TestMetadata(
        test_id="PROP-004b",
        category="Propulsion",
        subcategory="Thruster Physics",
        name="Dual thrusters stack turn rate",
        summary="Validates that ManeuveringThruster abilities from multiple thrusters stack additively",
        conditions=[
            f"Ship: Test_Thruster_2x (1× engine + 2× test_thruster_std)",
            f"Ship mass: {PROP004B_TOTAL_MASS} (hull_test_s, zero-mass components)",
            f"Thruster count: {PROP004B_THRUSTER_COUNT}",
            f"Raw turn rate per thruster: {PROP004B_RAW_TURN_RATE_EACH}",
            f"Total raw turn rate: {PROP004B_TOTAL_RAW_TURN_RATE} (stacked)",
            f"Formula: turn_speed = (raw_turn_rate × K_TURN) / mass^1.5"
        ],
        edge_cases=[
            "Multiple identical thrusters",
            "Turn rate values stack additively",
            "2x raw_turn_rate = 2x turn_speed (same mass)"
        ],
        expected_outcome=f"Ship rotates from {PROP004B_STARTING_ANGLE}° to {PROP004B_EXPECTED_FINAL_ANGLE}° (2× single thruster)",
        pass_criteria=f"turn_speed = {PROP004B_TURN_SPEED} AND final_angle = {PROP004B_EXPECTED_FINAL_ANGLE}°",
        max_ticks=PROP004B_MAX_TICKS,
        seed=42,
        ui_priority=7,
        tags=["propulsion", "thruster", "stacking", "ability"],
    )

    # Configuration attributes
    ship_file = PROP004B_SHIP_FILE
    turn_right = True

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Ship Mass", PROP004B_TOTAL_MASS, self.ship.mass))
        checks.append(check_exact("Turn Speed", PROP004B_TURN_SPEED, self.ship.turn_speed, phase="data"))
        # Precondition
        checks.append(check_approx("Starting Angle", PROP004B_STARTING_ANGLE, self.start_angle, phase="precondition"))
        # Outcome
        checks.append(check_approx("Final Angle", PROP004B_EXPECTED_FINAL_ANGLE, self.final_angle, tolerance=0.01))
        return checks


class PropNoEngineStationaryScenario(PropulsionScenario):
    """
    PROP-001b: Ship Without Engine Does Not Move

    Tests that a ship with no engine component remains stationary.
    This is a negative test to ensure propulsion requires an engine.
    """

    metadata = TestMetadata(
        test_id="PROP-001b",
        category="Propulsion",
        subcategory="Engine Physics",
        name="Ship without engine stays stationary",
        summary="Validates that a ship with no engine cannot move, even when thrust is commanded",
        conditions=[
            "Ship: Test_No_Engine (hull only, no propulsion)",
            "Ship mass: 20 (hull only)",
            "No engine component",
            "No thruster component",
            "Thrust command applied each tick",
            "Expected: No movement"
        ],
        edge_cases=[
            "Ship with zero thrust capability",
            "Thrust commands should have no effect"
        ],
        expected_outcome="Ship remains at initial position with zero velocity",
        pass_criteria="final_velocity == 0 AND distance_traveled == 0",
        max_ticks=100,
        seed=42,
        ui_priority=10,
        tags=["propulsion", "engine", "negative_test", "foundational"],
    )

    # Configuration attributes
    ship_file = "Test_No_Engine.json"
    thrust_forward = True  # Command thrust, but it should have no effect

    def validate(self, outcome, telemetry=None) -> list:
        checks = []
        ticks = self.results.get('ticks_run', 0)
        checks.append(check_true("Simulation Ran", ticks > 0, actual=ticks))
        # Data
        checks.append(check_exact("Ship Thrust", PROP001B_THRUST, self.ship.total_thrust))
        checks.append(check_exact("Ship Max Speed", PROP001B_MAX_SPEED, self.ship.max_speed))
        # Outcome: ship must NOT move
        checks.append(check_true("Remained Stationary",
                                 self.distance_traveled < 1e-9,
                                 actual=self.distance_traveled,
                                 detail="Ship should not move without an engine",
                                 phase="outcome"))
        checks.append(check_true("Zero Final Velocity",
                                 self.final_velocity.length() < 1e-9,
                                 actual=self.final_velocity.length(),
                                 detail="Velocity should remain zero",
                                 phase="outcome"))
        return checks


class PropThrusterOnlyScenario(PropulsionScenario):
    """
    PROP-003b: Thruster Only - No Engine

    Tests that a ship with thruster but no engine can rotate but cannot translate.
    This isolates thruster testing from engine effects.
    """

    metadata = TestMetadata(
        test_id="PROP-003b",
        category="Propulsion",
        subcategory="Thruster Physics",
        name="Thruster-only ship rotates but cannot translate",
        summary="Validates that a ship with thruster but no engine can rotate but cannot move forward",
        conditions=[
            f"Ship: Test_Thruster_Only (thruster, no engine)",
            f"Ship mass: {PROP003B_TOTAL_MASS} (hull_test_s, zero-mass components)",
            f"Thruster raw turn_rate: {PROP003B_RAW_TURN_RATE}",
            f"No engine component (thrust = 0)",
            f"Turn command: left (CCW) each tick for {PROP003B_MAX_TICKS} ticks",
            f"Expected turn_speed: {PROP003B_TURN_SPEED}"
        ],
        edge_cases=[
            "Pure rotation without translation",
            "Thruster works independently of engine"
        ],
        expected_outcome=f"Ship rotates from {PROP003B_STARTING_ANGLE}° to {PROP003B_EXPECTED_FINAL_ANGLE}° with zero velocity",
        pass_criteria=f"turn_speed = {PROP003B_TURN_SPEED} AND final_angle = {PROP003B_EXPECTED_FINAL_ANGLE}° AND velocity = 0",
        max_ticks=PROP003B_MAX_TICKS,
        seed=42,
        ui_priority=8,
        tags=["propulsion", "thruster", "rotation", "isolated_test"],
    )

    # Configuration attributes
    ship_file = PROP003B_SHIP_FILE
    turn_left = True
    thrust_forward = True  # Also command thrust - should have no effect

    def validate(self, outcome, telemetry=None) -> list:
        # Don't use template preconditions — this test intentionally has
        # thrust_forward=True with no engine, so "Ship Moved" would wrongly fail.
        checks = []
        checks.append(check_true("Simulation Ran", outcome.duration_ticks > 0,
                                 actual=outcome.duration_ticks))
        # Data
        checks.append(check_exact("Ship Mass", PROP003B_TOTAL_MASS, self.ship.mass))
        checks.append(check_exact("Ship Thrust", PROP003B_THRUST, self.ship.total_thrust))
        checks.append(check_true("Has Turn Speed", self.ship.turn_speed > 0,
                                 actual=self.ship.turn_speed, phase="data"))
        # Outcome
        checks.append(check_approx("Turn Speed", PROP003B_TURN_SPEED, self.ship.turn_speed))
        checks.append(check_approx("Final Angle", PROP003B_EXPECTED_FINAL_ANGLE, self.final_angle, tolerance=0.01))
        checks.append(check_true("Zero Final Velocity",
                                 self.final_velocity.length() < 0.001,
                                 actual=self.final_velocity.length(),
                                 detail="Ship should not translate without an engine",
                                 phase="outcome"))
        return checks


class PropMassAffectsTurnRateScenario(TestScenario):
    """
    PROP-005: Mass Affects Turn Rate

    Tests that heavier ships turn slower according to the formula:
    turn_speed = (raw_turn_rate * K_TURN) / mass^1.5

    This test compares two ships with the same thruster but different masses
    to verify the turn_speed scales correctly with mass.
    """

    metadata = TestMetadata(
        test_id="PROP-005",
        category="Propulsion",
        subcategory="Thruster Physics",
        name="Mass affects turn rate",
        summary="Validates that heavier ships turn slower according to mass^1.5 formula",
        conditions=[
            f"Low mass ship: {PROP005_LOW_MASS} (Test_Thruster_Simple)",
            f"High mass ship: {PROP005_HIGH_MASS} (Test_Thruster_HighMass)",
            f"Same raw_turn_rate: {PROP005_RAW_TURN_RATE} (test_thruster_std)",
            f"Turn command: right (CW) each tick for {PROP005_MAX_TICKS} ticks",
            f"Formula: turn_speed = (raw_turn_rate × K_TURN) / mass^1.5"
        ],
        edge_cases=[
            "Ratio should match mass^1.5 exactly (deterministic)",
            "Different mass, same thruster component",
            "Verifies physics formula scales correctly"
        ],
        expected_outcome=f"Low mass: 0° → {PROP005_LOW_EXPECTED_FINAL_ANGLE:.2f}°, High mass: 0° → {PROP005_HIGH_EXPECTED_FINAL_ANGLE:.4f}°",
        pass_criteria=f"Low final_angle = {PROP005_LOW_EXPECTED_FINAL_ANGLE}° AND High final_angle = {PROP005_HIGH_EXPECTED_FINAL_ANGLE:.4f}°",
        max_ticks=PROP005_MAX_TICKS,
        seed=42,
        ui_priority=7,
        tags=["propulsion", "thruster", "mass", "turn_rate", "scaling", "foundational"],
    )

    def to_spec(self, registries=None):
        """PROJ-269: compile to a single-team 2-ship BattleSpec."""
        from game.core.math import Vector2
        from game.simulation.battle_spec import ( BattleSpec, CombatPolicies, EntryVector,
            ShipSpec, SquadronSpec, TaskForceSpec, TeamSpec,
        )
        from game.simulation.combat.boundary import UnboundedRegion
        from game.simulation.combat.formation import FormationShape, FormationSpec
        from game.simulation.combat.modifier_stack import ModifierStack
        from game.simulation.combat.telemetry import TelemetryLevel

        _ = registries
        low = ShipSpec(
            instance_id=f"{self.metadata.test_id}:low",
            design_id=PROP005_LOW_SHIP_FILE,
            theme_id="Federation",
            name=f"{self.metadata.test_id}-low",
            position=Vector2(0.0, 0.0),
            angle=0.0,
            velocity=Vector2(0.0, 0.0),
            components=(),
            scenario_role="low",
        )
        high = ShipSpec(
            instance_id=f"{self.metadata.test_id}:high",
            design_id=PROP005_HIGH_SHIP_FILE,
            theme_id="Federation",
            name=f"{self.metadata.test_id}-high",
            position=Vector2(0.0, 200.0),
            angle=0.0,
            velocity=Vector2(0.0, 0.0),
            components=(),
            scenario_role="high",
        )
        formation = FormationSpec(
            shape=FormationShape.CUSTOM,
            spacing=200.0,
            custom_positions=(Vector2(0.0, 0.0), Vector2(0.0, 200.0)),
        )
        team = TeamSpec(
            team_id=0, name="TurnRate",
            entry_vector=EntryVector(origin=Vector2(0.0, 0.0), facing=0.0),
            fleet_hierarchy=(
                TaskForceSpec(
                    task_force_id="tf-turn",
                    formation=formation,
                    policies=CombatPolicies(),
                    squadrons=(
                        SquadronSpec(
                            squadron_id="sq-turn",
                            policies=CombatPolicies(),
                            ships=(low, high),
                        ),
                    ),
                ),
            ),
        )
        return BattleSpec(
            seed=self.metadata.seed,
            telemetry_level=TelemetryLevel.DETAILED,
            boundary=UnboundedRegion(),
            end_condition=self._create_end_condition(),
            absolute_max_ticks=max(self.metadata.max_ticks * 10, 1000),
            teams=(team,),
            modifier_stack=ModifierStack.empty(),
            post_battle_hook=None,
        )

    def wire_ships(self, ships_by_role, *, engine=None, initial_state=None):
        """PROJ-269: cache per-ship refs + assign test_rotate_right policy."""
        _ = engine, initial_state
        self.low_mass_ship = ships_by_role["low"]
        self.high_mass_ship = ships_by_role["high"]
        self.low_mass_start_angle = self.low_mass_ship.angle
        self.high_mass_start_angle = self.high_mass_ship.angle
        self.low_mass_ship.movement_policy = "test_rotate_right"
        self.high_mass_ship.movement_policy = "test_rotate_right"


    def collect_results(self, outcome, telemetry=None):
        """Populate measurement attributes for the two ships."""
        self.results['ticks_run'] = outcome.duration_ticks

    def validate(self, outcome, telemetry=None) -> list:
        checks = []
        ticks = self.results.get('ticks_run', 0)
        checks.append(check_true("Simulation Ran", ticks > 0, actual=ticks))

        # Data
        checks.append(check_exact("Low Mass Ship Mass", PROP005_LOW_MASS, self.low_mass_ship.mass))
        checks.append(check_exact("High Mass Ship Mass", PROP005_HIGH_MASS, self.high_mass_ship.mass))

        # Outcome: turn speeds match formula
        checks.append(check_approx("Low Mass Turn Speed", PROP005_LOW_TURN_SPEED, self.low_mass_ship.turn_speed))
        checks.append(check_approx("High Mass Turn Speed", PROP005_HIGH_TURN_SPEED, self.high_mass_ship.turn_speed, tolerance=1e-6))

        # Outcome: final angles match predictions
        checks.append(check_approx("Low Mass Final Angle", PROP005_LOW_EXPECTED_FINAL_ANGLE, self.low_mass_ship.angle, tolerance=0.01))
        checks.append(check_approx("High Mass Final Angle", PROP005_HIGH_EXPECTED_FINAL_ANGLE, self.high_mass_ship.angle, tolerance=0.01))

        # Outcome: turn speed ratio matches mass^1.5 ratio
        if self.high_mass_ship.turn_speed > 0:
            actual_ratio = self.low_mass_ship.turn_speed / self.high_mass_ship.turn_speed
            checks.append(check_approx("Turn Speed Ratio", PROP005_EXPECTED_RATIO, actual_ratio))

        return checks


# Export all scenarios for registry discovery
__all__ = [
    'PropEngineAccelerationScenario',
    'PropDualEngineScenario',
    'PropThrustMassRatioScenario',
    'PropThrusterTurnRateScenario',
    'PropThrusterRotationScenario',
    'PropDualThrusterScenario',
    'PropNoEngineStationaryScenario',
    'PropThrusterOnlyScenario',
    'PropMassAffectsTurnRateScenario'
]
