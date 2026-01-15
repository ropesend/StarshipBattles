"""
Propulsion Test Scenarios (PROP-001 to PROP-004)

These tests validate the core propulsion physics for engines and thrusters.
Propulsion is foundational for all combat tests, so these are high priority.

Physics Constants (from ship_stats.py):
- K_SPEED = 25 (speed multiplier)
- K_THRUST = 2500 (thrust constant for acceleration)
- Formula: max_speed = (thrust * K_SPEED) / mass
- Formula: acceleration = (thrust * K_THRUST) / mass²
"""

import pygame
from simulation_tests.scenarios import TestScenario, TestMetadata
from simulation_tests.scenarios.templates import PropulsionScenario


# Physics constants (must match ship_stats.py)
K_SPEED = 25
K_THRUST = 2500


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
        tags=["propulsion", "engine", "acceleration", "foundational"]
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
            "Test 3 ships: LowMass (40), MedMass (1040), HighMass (10040)",
            "All ships have same engine thrust: 500",
            "Formula: max_speed = (500 * 25) / mass",
            "Expected speeds: 312.5, 12.0, 1.25 px/s",
            "Speed should scale inversely with mass"
        ],
        edge_cases=[
            "Wide mass range (40x to 10000x)",
            "Linear inverse relationship (speed ∝ 1/mass)"
        ],
        expected_outcome="Speed decreases linearly as mass increases (inverse proportionality)",
        pass_criteria="speed ratio matches inverse mass ratio within 5%",
        max_ticks=200,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=9,
        tags=["propulsion", "engine", "mass", "scaling", "foundational"]
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

        # Pass if ratio matches within 5% and ordering is correct
        ratio_matches = ratio_error < 0.05
        self.results['ratio_matches'] = ratio_matches

        return ratio_matches and speed_ordering_correct


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
        tags=["propulsion", "thruster", "turn_rate", "foundational"]
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
        K_TURN = 25000
        raw_turn_rate = 5.0  # From test_thruster_std component
        mass = self.ship.mass
        expected_turn_speed = (raw_turn_rate * K_TURN) / (mass ** 1.5)

        self.expected_turn_speed = expected_turn_speed

    def verify(self, battle_engine) -> bool:
        """Check if the test passed."""
        # Call parent to calculate and store all standard results
        try:
            super().verify(battle_engine)
        except NotImplementedError:
            pass  # Expected - parent raises this for subclasses to override

        actual_turn_speed = self.ship.turn_speed

        # Add scenario-specific result fields
        self.results['mass'] = self.ship.mass
        self.results['raw_turn_rate'] = 5.0  # Known from component
        self.results['expected_turn_speed'] = self.expected_turn_speed
        self.results['actual_turn_speed'] = actual_turn_speed
        self.results['has_positive_turn_speed'] = actual_turn_speed > 0

        # Check if matches formula within 1%
        if self.expected_turn_speed > 0:
            error = abs(actual_turn_speed - self.expected_turn_speed) / self.expected_turn_speed
            self.results['error_percent'] = error * 100
            matches_formula = error < 0.01
        else:
            matches_formula = False

        self.results['matches_formula'] = matches_formula

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
        tags=["propulsion", "thruster", "rotation", "physics"]
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


# Export all scenarios for registry discovery
__all__ = [
    'PropEngineAccelerationScenario',
    'PropThrustMassRatioScenario',
    'PropThrusterTurnRateScenario',
    'PropThrusterRotationScenario'
]
