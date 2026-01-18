"""
Propulsion Test Scenarios (PROP-001 to PROP-004)

These tests validate the core propulsion physics for engines and thrusters.
Propulsion is foundational for all combat tests, so these are high priority.

Physics Constants (from game.simulation.physics_constants):
- K_SPEED = 25 (speed multiplier)
- K_THRUST = 2500 (thrust constant for acceleration)
- Formula: max_speed = (thrust * K_SPEED) / mass
- Formula: acceleration = (thrust * K_THRUST) / mass²
"""

import pygame
from game.simulation.physics_constants import K_SPEED, K_THRUST, K_TURN
from simulation_tests.scenarios import TestScenario, TestMetadata
from simulation_tests.scenarios.templates import PropulsionScenario
from simulation_tests.scenarios.validation import ExactMatchRule, DeterministicMatchRule


# Expected values for propulsion tests (calculated from physics formulas)
# Low mass ship: mass=40, thrust=500
LOW_MASS = 40
LOW_MASS_THRUST = 500
LOW_MASS_MAX_SPEED = (LOW_MASS_THRUST * K_SPEED) / LOW_MASS  # 312.5

# Medium mass ship: mass=2220, thrust=500
MED_MASS = 2220
MED_MASS_THRUST = 500
MED_MASS_MAX_SPEED = (MED_MASS_THRUST * K_SPEED) / MED_MASS  # ~5.63

# High mass ship: mass=10220, thrust=500
HIGH_MASS = 10220
HIGH_MASS_THRUST = 500
HIGH_MASS_MAX_SPEED = (HIGH_MASS_THRUST * K_SPEED) / HIGH_MASS  # ~1.22

# Thruster ship: mass=45, raw_turn_rate=5.0
THRUSTER_MASS = 45
THRUSTER_RAW_TURN_RATE = 5.0
THRUSTER_EXPECTED_TURN_SPEED = (THRUSTER_RAW_TURN_RATE * K_TURN) / (THRUSTER_MASS ** 1.5)

# No engine ship: mass=20
NO_ENGINE_MASS = 20

# Thruster-only ship: mass=25
THRUSTER_ONLY_MASS = 25
THRUSTER_ONLY_TURN_SPEED = (THRUSTER_RAW_TURN_RATE * K_TURN) / (THRUSTER_ONLY_MASS ** 1.5)


class PropEngineAccelerationScenario(PropulsionScenario):
    """
    PROP-001: Engine Provides Thrust - Ship Accelerates

    Tests that an engine component provides thrust value and that a ship
    with an engine accelerates from rest. This is the most fundamental
    propulsion test.
    """

    metadata = TestMetadata(
        test_id="PROP-001",
        category="Propulsion",
        subcategory="Engine Physics",
        name="Engine provides thrust - ship accelerates",
        summary="Validates that engine component provides thrust and ship accelerates from rest over time",
        conditions=[
            "Ship: Test_Engine_1x_LowMass (1 engine, no ballast)",
            "Engine thrust: 500",
            "Ship mass: 40 (hull 20 + engine 20)",
            "Initial velocity: 0",
            "Expected max_speed: 312.5 px/s",
            "Expected acceleration_rate: 781.25 px/s²",
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
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=10,
        tags=["propulsion", "engine", "acceleration", "foundational"],
        validation_rules=[
            # Ship configuration validation
            ExactMatchRule(
                name='Ship Mass',
                path='ship.mass',
                expected=LOW_MASS
            ),
            ExactMatchRule(
                name='Engine Thrust',
                path='ship.total_thrust',
                expected=LOW_MASS_THRUST
            ),
            # Physics formula validation
            DeterministicMatchRule(
                name='Max Speed (Formula)',
                path='ship.max_speed',
                expected=LOW_MASS_MAX_SPEED,
                description='max_speed = (thrust * K_SPEED) / mass = (500 * 25) / 40 = 312.5'
            ),
            # Test outcome validation
            DeterministicMatchRule(
                name='Initial Velocity',
                path='results.initial_velocity_magnitude',
                expected=0.0,
                description='Ship starts from rest'
            ),
        ]
    )

    # Configuration attributes
    ship_file = "Test_Engine_1x_LowMass.json"
    thrust_forward = True

    def custom_setup(self, battle_engine):
        """Verify ship stats match expectations."""
        # Template already loaded ship, positioned it, and started battle
        # Template already stored: self.start_position, self.start_velocity, self.start_angle
        # Template already calculated: self.expected_max_speed, self.expected_acceleration_rate

        expected_thrust = 500
        expected_mass = 40
        expected_max_speed = (expected_thrust * K_SPEED) / expected_mass  # 312.5

        assert abs(self.ship.total_thrust - expected_thrust) < 0.1, \
            f"Expected thrust {expected_thrust}, got {self.ship.total_thrust}"
        assert abs(self.ship.mass - expected_mass) < 0.1, \
            f"Expected mass {expected_mass}, got {self.ship.mass}"
        assert abs(self.ship.max_speed - expected_max_speed) < 0.1, \
            f"Expected max_speed {expected_max_speed}, got {self.ship.max_speed}"

    def verify(self, battle_engine) -> bool:
        """Check if the test passed."""
        # Call parent to calculate and store all standard results
        try:
            super().verify(battle_engine)
        except NotImplementedError:
            pass  # Expected - parent raises this for subclasses to override

        # Now use the calculated values
        final_velocity = self.final_velocity.length()
        initial_velocity = self.start_velocity.length()

        # Override the tuple results with scalar values for backward compatibility with tests
        self.results['initial_velocity'] = initial_velocity
        self.results['final_velocity'] = final_velocity

        # Add scenario-specific result fields
        self.results['thrust'] = self.ship.total_thrust
        self.results['mass'] = self.ship.mass
        self.results['accelerated'] = final_velocity > initial_velocity and final_velocity > 0

        # Return pass/fail logic
        return self.results['accelerated']


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
            f"Expected speeds: {LOW_MASS_MAX_SPEED:.2f}, {MED_MASS_MAX_SPEED:.4f}, {HIGH_MASS_MAX_SPEED:.4f} px/s",
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
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=9,
        tags=["propulsion", "engine", "mass", "scaling", "foundational"],
        validation_rules=[
            # Low mass ship configuration
            ExactMatchRule(
                name='Low Mass Ship - Mass',
                path='low_mass_ship.mass',
                expected=LOW_MASS
            ),
            ExactMatchRule(
                name='Low Mass Ship - Thrust',
                path='low_mass_ship.total_thrust',
                expected=LOW_MASS_THRUST
            ),
            DeterministicMatchRule(
                name='Low Mass Ship - Max Speed',
                path='low_mass_ship.max_speed',
                expected=LOW_MASS_MAX_SPEED,
                description='max_speed = (500 * 25) / 40 = 312.5'
            ),
            # Medium mass ship configuration
            ExactMatchRule(
                name='Med Mass Ship - Mass',
                path='med_mass_ship.mass',
                expected=MED_MASS
            ),
            ExactMatchRule(
                name='Med Mass Ship - Thrust',
                path='med_mass_ship.total_thrust',
                expected=MED_MASS_THRUST
            ),
            DeterministicMatchRule(
                name='Med Mass Ship - Max Speed',
                path='med_mass_ship.max_speed',
                expected=MED_MASS_MAX_SPEED,
                description=f'max_speed = (500 * 25) / {MED_MASS}'
            ),
            # High mass ship configuration
            ExactMatchRule(
                name='High Mass Ship - Mass',
                path='high_mass_ship.mass',
                expected=HIGH_MASS
            ),
            ExactMatchRule(
                name='High Mass Ship - Thrust',
                path='high_mass_ship.total_thrust',
                expected=HIGH_MASS_THRUST
            ),
            DeterministicMatchRule(
                name='High Mass Ship - Max Speed',
                path='high_mass_ship.max_speed',
                expected=HIGH_MASS_MAX_SPEED,
                description=f'max_speed = (500 * 25) / {HIGH_MASS}'
            ),
            # Speed ratio validation (inverse mass ratio)
            DeterministicMatchRule(
                name='Speed Ratio (Low/Med)',
                path='results.speed_ratio_low_med',
                expected=MED_MASS / LOW_MASS,  # Should equal mass ratio
                description='speed_ratio = low_speed / med_speed = med_mass / low_mass'
            ),
        ]
    )

    def setup(self, battle_engine):
        """Configure the test scenario."""
        # Load three ships with different mass values
        self.low_mass = self._load_ship('Test_Engine_1x_LowMass.json')
        self.med_mass = self._load_ship('Test_Engine_1x_MedMass.json')
        self.high_mass = self._load_ship('Test_Engine_1x_HighMass.json')

        # Position ships in a line
        self.low_mass.position = pygame.math.Vector2(0, 0)
        self.low_mass.velocity = pygame.math.Vector2(0, 0)
        self.low_mass.angle = 0

        self.med_mass.position = pygame.math.Vector2(0, 200)
        self.med_mass.velocity = pygame.math.Vector2(0, 0)
        self.med_mass.angle = 0

        self.high_mass.position = pygame.math.Vector2(0, 400)
        self.high_mass.velocity = pygame.math.Vector2(0, 0)
        self.high_mass.angle = 0

        # Verify all have same thrust
        assert abs(self.low_mass.total_thrust - self.med_mass.total_thrust) < 0.1, \
            "All test ships should have identical thrust"
        assert abs(self.med_mass.total_thrust - self.high_mass.total_thrust) < 0.1, \
            "All test ships should have identical thrust"

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([self.low_mass, self.med_mass, self.high_mass], [],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Store initial state
        self.initial_positions = {
            'low': self.low_mass.position.copy(),
            'med': self.med_mass.position.copy(),
            'high': self.high_mass.position.copy()
        }

    def update(self, battle_engine):
        """Called every tick during simulation."""
        # Apply thrust to all ships
        self.low_mass.thrust_forward()
        self.med_mass.thrust_forward()
        self.high_mass.thrust_forward()

    def verify(self, battle_engine) -> bool:
        """Check if the test passed."""
        # Get final velocities
        v_low = self.low_mass.velocity.length()
        v_med = self.med_mass.velocity.length()
        v_high = self.high_mass.velocity.length()

        # Store results
        self.results['low_mass'] = {
            'mass': self.low_mass.mass,
            'thrust': self.low_mass.total_thrust,
            'max_speed': self.low_mass.max_speed,
            'final_velocity': v_low,
            'distance': self.low_mass.position.distance_to(self.initial_positions['low'])
        }
        self.results['med_mass'] = {
            'mass': self.med_mass.mass,
            'thrust': self.med_mass.total_thrust,
            'max_speed': self.med_mass.max_speed,
            'final_velocity': v_med,
            'distance': self.med_mass.position.distance_to(self.initial_positions['med'])
        }
        self.results['high_mass'] = {
            'mass': self.high_mass.mass,
            'thrust': self.high_mass.total_thrust,
            'max_speed': self.high_mass.max_speed,
            'final_velocity': v_high,
            'distance': self.high_mass.position.distance_to(self.initial_positions['high'])
        }

        # Verify speed ratio matches inverse mass ratio
        # low_speed / med_speed should equal med_mass / low_mass
        speed_ratio_low_med = self.low_mass.max_speed / self.med_mass.max_speed
        mass_ratio_med_low = self.med_mass.mass / self.low_mass.mass

        ratio_error = abs(speed_ratio_low_med - mass_ratio_med_low) / mass_ratio_med_low

        self.results['speed_ratio_low_med'] = speed_ratio_low_med
        self.results['expected_ratio'] = mass_ratio_med_low
        self.results['ratio_error_percent'] = ratio_error * 100

        # Verify ordering
        speed_ordering_correct = (self.high_mass.max_speed < self.med_mass.max_speed < self.low_mass.max_speed)
        self.results['speed_ordering_correct'] = speed_ordering_correct

        # Pass if ratio matches exactly (tiny tolerance for floating point)
        # Physics is deterministic - ratio should be exact
        ratio_matches = ratio_error < 1e-9
        self.results['ratio_matches'] = ratio_matches

        # Run validation rules
        if hasattr(self.metadata, 'validation_rules') and self.metadata.validation_rules:
            self.run_validation(battle_engine)

        return ratio_matches and speed_ordering_correct

    def run_validation(self, battle_engine):
        """
        Override to add the three ships to validation context.
        """
        from simulation_tests.scenarios.validation import Validator

        if not self.metadata.validation_rules:
            return []

        # Build validation context with all three ships
        context = {
            'test_scenario': self,
            'battle_engine': battle_engine,
            'results': self.results if hasattr(self, 'results') else {},
            'metadata': self.metadata,
            # Add each ship to context
            'low_mass_ship': self._extract_ship_validation_data(self.low_mass),
            'med_mass_ship': self._extract_ship_validation_data(self.med_mass),
            'high_mass_ship': self._extract_ship_validation_data(self.high_mass),
        }

        # Run validator
        validator = Validator(self.metadata.validation_rules)
        validation_results = validator.validate(context)

        # Store in results for UI access
        if hasattr(self, 'results'):
            self.results['validation_results'] = [r.to_dict() for r in validation_results]
            self.results['validation_summary'] = validator.get_summary(validation_results)
            self.results['has_validation_failures'] = validator.has_failures(validation_results)
            self.results['has_validation_warnings'] = validator.has_warnings(validation_results)

        return validation_results


class PropThrusterTurnRateScenario(PropulsionScenario):
    """
    PROP-003: Thruster Provides Turn Rate

    Tests that ManeuveringThruster component provides turn rate and
    that turn_speed is calculated correctly according to the formula.
    """

    metadata = TestMetadata(
        test_id="PROP-003",
        category="Propulsion",
        subcategory="Thruster Physics",
        name="Thruster provides turn rate",
        summary="Validates that ManeuveringThruster component provides turn rate and turn_speed is calculated correctly",
        conditions=[
            "Ship: Test_Thruster_Simple (1 thruster only)",
            "Thruster raw turn_rate: 5.0",
            "Ship mass: 45 (hull 20 + engine 20 + thruster 5)",
            "Formula: turn_speed = (raw_turn_rate * K_TURN) / mass^1.5",
            "K_TURN = 25000",
            "Expected turn_speed calculated from formula"
        ],
        edge_cases=[
            "Minimal ship configuration (thruster + engine + hull)",
            "Turn speed scales with mass^1.5 (stronger than linear)",
            "No resource consumption"
        ],
        expected_outcome="Ship has positive turn_speed value calculated from thruster component",
        pass_criteria="turn_speed > 0 AND matches formula within 1%",
        max_ticks=50,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=8,
        tags=["propulsion", "thruster", "turn_rate", "foundational"],
        validation_rules=[
            # Ship configuration validation
            ExactMatchRule(
                name='Ship Mass',
                path='ship.mass',
                expected=THRUSTER_MASS
            ),
            # Physics formula validation - turn_speed should match exactly
            DeterministicMatchRule(
                name='Turn Speed (Formula)',
                path='ship.turn_speed',
                expected=THRUSTER_EXPECTED_TURN_SPEED,
                description=f'turn_speed = (raw_turn_rate * K_TURN) / mass^1.5 = (5.0 * 25000) / 45^1.5'
            ),
            # Test outcome validation
            DeterministicMatchRule(
                name='Expected Turn Speed',
                path='results.expected_turn_speed',
                expected=THRUSTER_EXPECTED_TURN_SPEED,
                description='Expected value stored in results'
            ),
            DeterministicMatchRule(
                name='Actual Turn Speed',
                path='results.actual_turn_speed',
                expected=THRUSTER_EXPECTED_TURN_SPEED,
                description='Actual ship turn_speed should match formula'
            ),
        ]
    )

    # Configuration attributes
    ship_file = "Test_Thruster_Simple.json"
    turn_left = True

    def custom_setup(self, battle_engine):
        """Verify ship stats match expectations."""
        # Template already loaded ship, positioned it, and started battle
        # Template already stored: self.start_position, self.start_velocity, self.start_angle
        # Template already calculated: self.expected_max_speed, self.expected_acceleration_rate

        # Store expected values
        raw_turn_rate = 5.0  # From test_thruster_std component
        mass = self.ship.mass
        expected_turn_speed = (raw_turn_rate * K_TURN) / (mass ** 1.5)

        self.expected_turn_speed = expected_turn_speed

    def verify(self, battle_engine) -> bool:
        """Check if the test passed."""
        actual_turn_speed = self.ship.turn_speed

        # Store scenario-specific result fields BEFORE calling parent
        # (parent runs validation which needs these values)
        self.results['mass'] = self.ship.mass
        self.results['raw_turn_rate'] = 5.0  # Known from component
        self.results['expected_turn_speed'] = self.expected_turn_speed
        self.results['actual_turn_speed'] = actual_turn_speed
        self.results['has_positive_turn_speed'] = actual_turn_speed > 0

        # Check if matches formula exactly (tiny tolerance for floating point)
        # Physics is deterministic - turn_speed should be exact
        if self.expected_turn_speed > 0:
            error = abs(actual_turn_speed - self.expected_turn_speed) / self.expected_turn_speed
            self.results['error_percent'] = error * 100
            matches_formula = error < 1e-9
        else:
            matches_formula = False

        self.results['matches_formula'] = matches_formula

        # Call parent to calculate and store all standard results
        # (and run validation now that our results are stored)
        try:
            super().verify(battle_engine)
        except NotImplementedError:
            pass  # Expected - parent raises this for subclasses to override

        return actual_turn_speed > 0 and matches_formula


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
            "Ship: Test_Thruster_Simple (1 thruster)",
            "Initial angle: 0 degrees",
            "Apply rotation command each tick",
            "Test duration: 100 ticks",
            "Expected: angle changes proportional to turn_speed"
        ],
        edge_cases=[
            "Starting from zero rotation",
            "Continuous rotation over multiple ticks",
            "Angle wrapping at 360 degrees"
        ],
        expected_outcome="Ship angle changes over time according to turn_speed",
        pass_criteria="abs(angle_change) > 0 AND rotation_detected",
        max_ticks=100,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=8,
        tags=["propulsion", "thruster", "rotation", "physics"],
        validation_rules=[
            # Ship configuration validation
            ExactMatchRule(
                name='Ship Mass',
                path='ship.mass',
                expected=THRUSTER_MASS
            ),
            # Physics formula validation
            DeterministicMatchRule(
                name='Turn Speed',
                path='ship.turn_speed',
                expected=THRUSTER_EXPECTED_TURN_SPEED,
                description=f'turn_speed = (raw_turn_rate * K_TURN) / mass^1.5'
            ),
            # Test outcome validation - initial angle
            DeterministicMatchRule(
                name='Initial Angle',
                path='results.initial_angle',
                expected=0.0,
                description='Ship starts facing right (0 degrees)'
            ),
        ]
    )

    # Configuration attributes
    ship_file = "Test_Thruster_Simple.json"
    turn_right = True

    def custom_setup(self, battle_engine):
        """Track angle changes during simulation."""
        # Template already loaded ship, positioned it, and started battle
        # Template already stored: self.start_position, self.start_velocity, self.start_angle
        # Template already calculated: self.expected_max_speed, self.expected_acceleration_rate

        # Track angle changes
        self.angle_history = [self.ship.angle]

    def custom_update(self, battle_engine):
        """Record angle each tick."""
        # Template already handles turn_right command
        # Just record the angle history
        self.angle_history.append(self.ship.angle)

    def verify(self, battle_engine) -> bool:
        """Check if the test passed."""
        # Call parent to calculate and store all standard results
        try:
            super().verify(battle_engine)
        except NotImplementedError:
            pass  # Expected - parent raises this for subclasses to override

        # Calculate total angle change
        angle_change = self.final_angle - self.start_angle

        # Normalize angle to [-180, 180]
        while angle_change > 180:
            angle_change -= 360
        while angle_change < -180:
            angle_change += 360

        # Add scenario-specific result fields
        self.results['turn_speed'] = self.ship.turn_speed
        self.results['angle_history_sample'] = self.angle_history[::10]  # Sample every 10 ticks

        # Check if rotation occurred
        rotation_detected = abs(angle_change) > 0.1  # At least 0.1 degree change
        self.results['rotation_detected'] = rotation_detected

        # Verify some rotation occurred and it's in the expected direction
        # Since we commanded clockwise (positive direction), angle should increase
        expected_direction_correct = angle_change > 0
        self.results['expected_direction_correct'] = expected_direction_correct

        return rotation_detected and expected_direction_correct


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
        battle_end_mode="time_based",
        ui_priority=10,
        tags=["propulsion", "engine", "negative_test", "foundational"],
        validation_rules=[
            # Ship configuration validation
            ExactMatchRule(
                name='Ship Mass',
                path='ship.mass',
                expected=NO_ENGINE_MASS
            ),
            ExactMatchRule(
                name='Total Thrust (Should be 0)',
                path='ship.total_thrust',
                expected=0
            ),
            ExactMatchRule(
                name='Max Speed (Should be 0)',
                path='ship.max_speed',
                expected=0
            ),
            # Test outcome validation - ship should not move
            DeterministicMatchRule(
                name='Final Velocity',
                path='results.final_velocity_magnitude',
                expected=0.0,
                description='Ship without engine cannot accelerate'
            ),
            DeterministicMatchRule(
                name='Distance Traveled',
                path='results.distance_traveled',
                expected=0.0,
                description='Ship should remain at initial position'
            ),
        ]
    )

    # Configuration attributes
    ship_file = "Test_No_Engine.json"
    thrust_forward = True  # Command thrust, but it should have no effect

    def custom_setup(self, battle_engine):
        """Verify ship has no engine and cannot thrust."""
        # Verify ship has zero thrust
        assert self.ship.total_thrust == 0, \
            f"Expected zero thrust, got {self.ship.total_thrust}"
        assert self.ship.max_speed == 0, \
            f"Expected zero max_speed, got {self.ship.max_speed}"

    def verify(self, battle_engine) -> bool:
        """Check that ship did not move."""
        try:
            super().verify(battle_engine)
        except NotImplementedError:
            pass

        final_velocity = self.final_velocity.length()
        distance_traveled = self.final_position.distance_to(self.start_position)

        # Store results
        self.results['initial_velocity'] = 0.0
        self.results['final_velocity'] = final_velocity
        self.results['distance_traveled'] = distance_traveled
        self.results['thrust'] = self.ship.total_thrust
        self.results['mass'] = self.ship.mass
        self.results['max_speed'] = self.ship.max_speed
        self.results['remained_stationary'] = (final_velocity < 1e-9 and distance_traveled < 1e-9)

        # Pass if ship stayed stationary
        return self.results['remained_stationary']


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
            "Ship: Test_Thruster_Only (thruster, no engine)",
            "Ship mass: 25 (hull 20 + thruster 5)",
            "Thruster raw turn_rate: 5.0",
            "No engine component (thrust = 0)",
            "Turn command applied each tick",
            "Expected: Rotation but no translation"
        ],
        edge_cases=[
            "Pure rotation without translation",
            "Thruster works independently of engine"
        ],
        expected_outcome="Ship rotates in place with zero velocity",
        pass_criteria="turn_speed > 0 AND final_velocity == 0",
        max_ticks=50,
        seed=42,
        battle_end_mode="time_based",
        ui_priority=8,
        tags=["propulsion", "thruster", "rotation", "isolated_test"],
        validation_rules=[
            # Ship configuration validation
            ExactMatchRule(
                name='Ship Mass',
                path='ship.mass',
                expected=THRUSTER_ONLY_MASS
            ),
            ExactMatchRule(
                name='Total Thrust (Should be 0)',
                path='ship.total_thrust',
                expected=0
            ),
            # Physics formula validation - turn_speed should match exactly
            DeterministicMatchRule(
                name='Turn Speed (Formula)',
                path='ship.turn_speed',
                expected=THRUSTER_ONLY_TURN_SPEED,
                description=f'turn_speed = (raw_turn_rate * K_TURN) / mass^1.5 = (5.0 * 25000) / 25^1.5'
            ),
            # Test outcome validation - ship should rotate but not translate
            DeterministicMatchRule(
                name='Final Velocity',
                path='results.final_velocity_magnitude',
                expected=0.0,
                description='Ship without engine cannot translate'
            ),
            DeterministicMatchRule(
                name='Distance Traveled',
                path='results.distance_traveled',
                expected=0.0,
                tolerance=1e-6,  # Allow tiny floating point error
                description='Ship should remain at initial position'
            ),
        ]
    )

    # Configuration attributes
    ship_file = "Test_Thruster_Only.json"
    turn_left = True
    thrust_forward = True  # Also command thrust - should have no effect

    def custom_setup(self, battle_engine):
        """Verify ship has thruster but no engine."""
        # Calculate expected turn speed
        raw_turn_rate = 5.0
        mass = self.ship.mass
        self.expected_turn_speed = (raw_turn_rate * K_TURN) / (mass ** 1.5)

        # Verify ship has zero thrust but positive turn speed
        assert self.ship.total_thrust == 0, \
            f"Expected zero thrust, got {self.ship.total_thrust}"
        assert self.ship.turn_speed > 0, \
            f"Expected positive turn_speed, got {self.ship.turn_speed}"

    def verify(self, battle_engine) -> bool:
        """Check that ship rotated but did not move."""
        try:
            super().verify(battle_engine)
        except NotImplementedError:
            pass

        final_velocity = self.final_velocity.length()
        distance_traveled = self.final_position.distance_to(self.start_position)
        angle_change = abs(self.final_angle - self.start_angle)

        # Store results
        self.results['mass'] = self.ship.mass
        self.results['total_thrust'] = self.ship.total_thrust
        self.results['expected_turn_speed'] = self.expected_turn_speed
        self.results['actual_turn_speed'] = self.ship.turn_speed
        self.results['initial_angle'] = self.start_angle
        self.results['final_angle'] = self.final_angle
        self.results['angle_change'] = angle_change
        self.results['final_velocity'] = final_velocity
        self.results['distance_traveled'] = distance_traveled
        self.results['rotated'] = angle_change > 0.1
        self.results['stayed_in_place'] = distance_traveled < 1e-6

        # Check turn_speed matches formula (exact)
        error = abs(self.ship.turn_speed - self.expected_turn_speed) / self.expected_turn_speed
        self.results['turn_speed_error_percent'] = error * 100
        self.results['turn_speed_matches'] = error < 1e-9

        # Pass if ship rotated but stayed in place
        return (self.results['rotated'] and
                self.results['stayed_in_place'] and
                self.results['turn_speed_matches'])


# Export all scenarios for registry discovery
__all__ = [
    'PropEngineAccelerationScenario',
    'PropThrustMassRatioScenario',
    'PropThrusterTurnRateScenario',
    'PropThrusterRotationScenario',
    'PropNoEngineStationaryScenario',
    'PropThrusterOnlyScenario'
]
