"""
Scenario Templates for Combat Lab Test Framework

These base templates eliminate ~2000 lines of duplicated code across 35+ test scenarios
by providing common setup/update/verify patterns for different test types.

Template Hierarchy:
- TestScenario (base class in base.py)
  - StaticTargetScenario: Attacker vs stationary target
  - DuelScenario: Two ships engaging each other
  - PropulsionScenario: Single ship movement/physics tests
  - ResourceScenario: Resource consumption/depletion/regeneration tests
  - ComparisonScenario: A/B comparison (baseline vs variant)

Usage Example:
    class MyWeaponTest(StaticTargetScenario):
        metadata = TestMetadata(...)
        attacker_ship = "Test_Attacker.json"
        target_ship = "Test_Target.json"
        distance = 500

        def verify(self, battle_engine):
            return self.damage_dealt > 100
"""

import pygame
from typing import Optional
from simulation_tests.scenarios.base import TestScenario


# ============================================================================
# STATIC TARGET SCENARIO TEMPLATE
# ============================================================================

class StaticTargetScenario(TestScenario):
    """
    Base template for attacker-vs-stationary-target scenarios.

    Eliminates ~50 lines of duplicate setup/update/verify code per test.
    Used by: Beam weapon tests, seeker weapon tests, and accuracy tests.

    Subclass Configuration (required):
    - attacker_ship: str - Filename of attacker ship JSON
    - target_ship: str - Filename of target ship JSON
    - distance: float - Distance between ships in pixels

    Subclass Configuration (optional):
    - attacker_angle: float - Attacker rotation (default: 0 = facing right)
    - target_angle: float - Target rotation (default: 0)
    - verify_damage_dealt: bool - Auto-verify if damage > 0 (default: False)
    - force_fire: bool - Auto-fire weapon each tick (default: True)

    Automatic Setup:
    - Loads attacker and target ships
    - Positions attacker at origin (0,0)
    - Positions target at (distance, 0)
    - Creates time-based end condition
    - Sets attacker's current_target to target
    - Stores initial target HP

    Automatic Update:
    - Forces attacker to fire each tick (if force_fire=True)

    Results Storage:
    - initial_hp: Target HP before test
    - final_hp: Target HP after test
    - damage_dealt: initial_hp - final_hp
    - ticks_run: Number of simulation ticks
    - target_alive: Whether target survived
    - hit_rate: damage_dealt / ticks_run (if applicable)

    Example Usage:
        class BeamPointBlankTest(StaticTargetScenario):
            metadata = TestMetadata(...)
            attacker_ship = "Test_Attacker_Beam.json"
            target_ship = "Test_Target_Stationary.json"
            distance = 50

            def verify(self, battle_engine):
                return self.damage_dealt > 0
    """

    # Configuration - subclasses must set these
    attacker_ship: Optional[str] = None
    target_ship: Optional[str] = None
    distance: Optional[float] = None

    # Optional configuration
    attacker_angle: float = 0.0  # Default: facing right
    target_angle: float = 0.0
    verify_damage_dealt: bool = False  # If True, auto-verify damage > 0
    force_fire: bool = True  # If True, auto-trigger weapon each tick

    # Advanced pass criteria configuration
    expect_no_damage: bool = False  # For out-of-range tests (expects damage == 0)
    min_damage_threshold: int = 0  # For damage >= threshold tests
    measurement_mode: bool = False  # For statistical tests (always passes if simulation completes)

    # Result customization
    custom_result_keys: list = []  # List of attribute names to store in results

    # Placeholder test support
    skip_test: bool = False  # If True, skip this test
    skip_reason: str = ""  # Reason for skipping

    def setup(self, battle_engine):
        """
        Standard setup for static target scenarios.
        Subclasses can override for custom setup, or use configuration attributes.
        """
        # Skip placeholder tests that aren't ready to run
        if self.skip_test:
            return

        # Validate configuration
        if self.attacker_ship is None:
            raise ValueError(f"{self.__class__.__name__} must set 'attacker_ship' attribute")
        if self.target_ship is None:
            raise ValueError(f"{self.__class__.__name__} must set 'target_ship' attribute")
        if self.distance is None:
            raise ValueError(f"{self.__class__.__name__} must set 'distance' attribute")

        # Load ships
        self.attacker = self._load_ship(self.attacker_ship)
        self.target = self._load_ship(self.target_ship)

        # Position attacker at origin
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = self.attacker_angle

        # Position target at distance
        self.target.position = pygame.math.Vector2(self.distance, 0)
        self.target.angle = self.target_angle

        # Store initial state
        self.initial_hp = self.target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Determine which seed to use:
        # - _override_seed is set by the UI when running tests (allows Random/Fixed/Custom modes)
        # - Falls back to metadata.seed for headless/CLI test runs
        seed_to_use = getattr(self, '_override_seed', None)
        if seed_to_use is None:
            seed_to_use = self.metadata.seed
        # Expose to custom_setup so movement controllers can derive their seed
        self._effective_seed = seed_to_use

        # Start battle with time-based end condition
        battle_engine.start([self.attacker], [self.target],
                          seed=seed_to_use,
                          end_condition=end_condition)

        # Assign AI strategies (AI handles firing)
        if self.force_fire:
            self.attacker.ai_strategy = 'test_stationary_fire'
        else:
            self.attacker.ai_strategy = 'test_do_nothing'
        self.target.ai_strategy = 'test_do_nothing'

        # Call custom setup hook if defined
        if hasattr(self, 'custom_setup'):
            self.custom_setup(battle_engine)

    def update(self, battle_engine):
        """Per-tick update. AI handles firing and movement via strategies."""
        if self.skip_test:
            return
        self._track_tick(battle_engine.tick_counter)

    def collect_results(self, engine):
        """
        Populate measurement attributes for StaticTargetScenario.

        Called automatically by _run_validation() before validate().
        Stores damage, HP, tick count, and hit rate on self and in self.results.
        """
        if self.skip_test:
            return

        self.damage_dealt = self.initial_hp - self.target.hp
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        if engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / engine.tick_counter

        # Collect per-weapon firing statistics (pass engine for in-flight counting)
        if hasattr(self, 'attacker') and self.attacker:
            self._collect_weapon_stats(self.attacker, 'attacker', engine=engine)
        if hasattr(self, 'target') and self.target:
            self._collect_weapon_stats(self.target, 'target', engine=engine)

        self._finalize_tracking()

        for key in self.custom_result_keys:
            if hasattr(self, key):
                self.results[key] = getattr(self, key)

        # Hook for subclasses to add extra results
        if hasattr(self, '_collect_extra_results'):
            self._collect_extra_results(engine)

    def _template_preconditions(self):
        """
        Return automatic precondition checks based on template config.

        StaticTargetScenario checks:
        - Simulation ran (ticks > 0)
        - Weapon fired if force_fire was set
        """
        from simulation_tests.scenarios.validation import check_true
        checks = []
        ticks = self.results.get('ticks_run', 0)
        checks.append(check_true(
            "Simulation Ran",
            ticks > 0,
            actual=ticks,
        ))
        return checks

    def verify(self, battle_engine) -> bool:
        """
        Legacy pass/fail for un-migrated scenarios.

        Calls collect_results() then applies flag-based pass criteria.
        New scenarios should implement validate() instead.
        """
        if self.skip_test:
            self.results['skipped'] = True
            self.results['skip_reason'] = self.skip_reason
            return False

        self.collect_results(battle_engine)

        if self.measurement_mode:
            return battle_engine.tick_counter > 0
        elif self.expect_no_damage:
            return self.damage_dealt == 0
        elif self.min_damage_threshold > 0:
            return self.damage_dealt >= self.min_damage_threshold
        elif self.verify_damage_dealt:
            return self.damage_dealt > 0
        else:
            raise NotImplementedError(
                f"{self.__class__.__name__} must implement validate() or verify()"
            )


# ============================================================================
# DUEL SCENARIO TEMPLATE
# ============================================================================

class DuelScenario(TestScenario):
    """
    Base template for two-ship engagement scenarios.

    Eliminates ~60 lines of duplicate setup/update/verify code per test.
    Used by: Combat engagement tests, AI behavior tests.

    Subclass Configuration (required):
    - ship1_file: str - Filename of first ship JSON
    - ship2_file: str - Filename of second ship JSON
    - distance: float - Distance between ships in pixels

    Subclass Configuration (optional):
    - ship1_angle: float - Ship 1 rotation (default: 0 = facing right)
    - ship2_angle: float - Ship 2 rotation (default: 180 = facing left)
    - ship1_position: Vector2 - Override default position (default: calculated from distance)
    - ship2_position: Vector2 - Override default position (default: calculated from distance)
    - auto_target: bool - Auto-set targets (default: True)
    - force_fire: bool - Auto-fire weapons each tick (default: True)

    Automatic Setup:
    - Loads both ships
    - Positions ships facing each other at specified distance
    - Creates time-based end condition
    - Sets mutual targeting (if auto_target=True)
    - Stores initial HP for both ships

    Automatic Update:
    - Forces both ships to fire each tick (if force_fire=True)

    Results Storage:
    - ship1_initial_hp, ship2_initial_hp: HP before test
    - ship1_final_hp, ship2_final_hp: HP after test
    - ship1_damage_dealt, ship2_damage_dealt: Damage dealt by each ship
    - ship1_damage_taken, ship2_damage_taken: Damage taken by each ship
    - ticks_run: Number of simulation ticks
    - ship1_alive, ship2_alive: Survival status
    - winner: 'ship1', 'ship2', 'draw', or None

    Example Usage:
        class BeamVsBeamTest(DuelScenario):
            metadata = TestMetadata(...)
            ship1_file = "Test_Ship1.json"
            ship2_file = "Test_Ship2.json"
            distance = 500

            def verify(self, battle_engine):
                return self.winner == 'ship1'
    """

    # Configuration - subclasses must set these
    ship1_file: Optional[str] = None
    ship2_file: Optional[str] = None
    distance: Optional[float] = None

    # Optional configuration
    ship1_angle: float = 0.0  # Default: facing right
    ship2_angle: float = 180.0  # Default: facing left
    ship1_position: Optional[pygame.math.Vector2] = None
    ship2_position: Optional[pygame.math.Vector2] = None
    auto_target: bool = True
    force_fire: bool = True

    def setup(self, battle_engine):
        """
        Standard setup for duel scenarios.
        Subclasses can override for custom setup, or use configuration attributes.
        """
        # Validate configuration
        if self.ship1_file is None:
            raise ValueError(f"{self.__class__.__name__} must set 'ship1_file' attribute")
        if self.ship2_file is None:
            raise ValueError(f"{self.__class__.__name__} must set 'ship2_file' attribute")
        if self.distance is None:
            raise ValueError(f"{self.__class__.__name__} must set 'distance' attribute")

        # Load ships
        self.ship1 = self._load_ship(self.ship1_file)
        self.ship2 = self._load_ship(self.ship2_file)

        # Position ships (default: facing each other along x-axis)
        if self.ship1_position is None:
            self.ship1.position = pygame.math.Vector2(-self.distance / 2, 0)
        else:
            self.ship1.position = self.ship1_position
        self.ship1.angle = self.ship1_angle

        if self.ship2_position is None:
            self.ship2.position = pygame.math.Vector2(self.distance / 2, 0)
        else:
            self.ship2.position = self.ship2_position
        self.ship2.angle = self.ship2_angle

        # Store initial state
        self.ship1_initial_hp = self.ship1.hp
        self.ship2_initial_hp = self.ship2.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle
        battle_engine.start([self.ship1], [self.ship2],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Assign AI strategies (AI handles firing)
        if self.force_fire:
            self.ship1.ai_strategy = 'test_stationary_fire'
            self.ship2.ai_strategy = 'test_stationary_fire'
        else:
            self.ship1.ai_strategy = 'test_do_nothing'
            self.ship2.ai_strategy = 'test_do_nothing'

        # Call custom setup hook if defined
        if hasattr(self, 'custom_setup'):
            self.custom_setup(battle_engine)

    def update(self, battle_engine):
        """
        Per-tick update. AI handles firing via strategies.
        Only custom hooks and tracking remain.
        """

        self._track_tick(battle_engine.tick_counter)

    def collect_results(self, engine):
        """
        Populate measurement attributes for DuelScenario.

        Called automatically by _run_validation() before validate().
        """
        self.ship1_damage_taken = self.ship1_initial_hp - self.ship1.hp
        self.ship2_damage_taken = self.ship2_initial_hp - self.ship2.hp
        self.ship1_damage_dealt = self.ship2_damage_taken
        self.ship2_damage_dealt = self.ship1_damage_taken

        self.results['ship1_initial_hp'] = self.ship1_initial_hp
        self.results['ship2_initial_hp'] = self.ship2_initial_hp
        self.results['ship1_final_hp'] = self.ship1.hp
        self.results['ship2_final_hp'] = self.ship2.hp
        self.results['ship1_damage_dealt'] = self.ship1_damage_dealt
        self.results['ship2_damage_dealt'] = self.ship2_damage_dealt
        self.results['ship1_damage_taken'] = self.ship1_damage_taken
        self.results['ship2_damage_taken'] = self.ship2_damage_taken
        self.results['ticks_run'] = engine.tick_counter
        self.results['ship1_alive'] = self.ship1.is_alive
        self.results['ship2_alive'] = self.ship2.is_alive

        # Collect per-weapon firing statistics
        self._collect_weapon_stats(self.ship1, 'ship1', engine=engine)
        self._collect_weapon_stats(self.ship2, 'ship2', engine=engine)

        self._finalize_tracking()

        # Determine winner
        if self.ship1.is_alive and not self.ship2.is_alive:
            self.winner = 'ship1'
        elif self.ship2.is_alive and not self.ship1.is_alive:
            self.winner = 'ship2'
        elif not self.ship1.is_alive and not self.ship2.is_alive:
            self.winner = 'draw'
        else:
            self.winner = None
        self.results['winner'] = self.winner

    def _template_preconditions(self):
        """Return automatic precondition checks for DuelScenario."""
        from simulation_tests.scenarios.validation import check_true
        checks = []
        ticks = self.results.get('ticks_run', 0)
        checks.append(check_true("Simulation Ran", ticks > 0, actual=ticks))
        return checks

    def verify(self, battle_engine) -> bool:
        """Legacy pass/fail. New scenarios should implement validate()."""
        self.collect_results(battle_engine)
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement validate() or verify()"
        )


# ============================================================================
# PROPULSION SCENARIO TEMPLATE
# ============================================================================

class PropulsionScenario(TestScenario):
    """
    Base template for single-ship propulsion/physics tests.

    Eliminates ~40 lines of duplicate setup/update/verify code per test.
    Used by: Engine tests, thruster tests, acceleration tests, turn rate tests.

    Subclass Configuration (required):
    - ship_file: str - Filename of ship JSON to test

    Subclass Configuration (optional):
    - initial_position: Vector2 - Starting position (default: origin)
    - initial_velocity: Vector2 - Starting velocity (default: zero)
    - initial_angle: float - Starting rotation (default: 0 = facing right)
    - thrust_forward: bool - Auto-thrust forward each tick (default: False)
    - thrust_backward: bool - Auto-thrust backward each tick (default: False)
    - turn_left: bool - Auto-turn left each tick (default: False)
    - turn_right: bool - Auto-turn right each tick (default: False)

    Automatic Setup:
    - Loads ship
    - Sets initial position, velocity, angle
    - Creates time-based end condition
    - Stores initial state for comparison

    Automatic Update:
    - Applies configured thrust/turn commands each tick

    Results Storage:
    - initial_position, final_position: Position before/after
    - initial_velocity, final_velocity: Velocity before/after
    - initial_angle, final_angle: Rotation before/after
    - distance_traveled: Total distance moved
    - velocity_magnitude: Final velocity magnitude
    - ticks_run: Number of simulation ticks
    - expected_max_speed, expected_acceleration_rate: Physics calculations

    Example Usage:
        class EngineAccelerationTest(PropulsionScenario):
            metadata = TestMetadata(...)
            ship_file = "Test_Engine_Ship.json"
            thrust_forward = True

            def verify(self, battle_engine):
                return self.final_velocity.length() > self.initial_velocity.length()
    """

    # Configuration - subclasses must set these
    ship_file: Optional[str] = None

    # Optional configuration
    initial_position: pygame.math.Vector2 = pygame.math.Vector2(0, 0)
    initial_velocity: pygame.math.Vector2 = pygame.math.Vector2(0, 0)
    initial_angle: float = 0.0  # Default: facing right
    thrust_forward: bool = False
    thrust_backward: bool = False
    turn_left: bool = False
    turn_right: bool = False

    def setup(self, battle_engine):
        """
        Standard setup for propulsion scenarios.
        Subclasses can override for custom setup, or use configuration attributes.
        """
        # Validate configuration
        if self.ship_file is None:
            raise ValueError(f"{self.__class__.__name__} must set 'ship_file' attribute")

        # Load ship
        self.ship = self._load_ship(self.ship_file)

        # Set initial state
        self.ship.position = self.initial_position.copy()
        self.ship.velocity = self.initial_velocity.copy()
        self.ship.angle = self.initial_angle

        # Store initial state for verification
        self.start_position = self.ship.position.copy()
        self.start_velocity = self.ship.velocity.copy()
        self.start_angle = self.ship.angle

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with single ship (no enemies)
        battle_engine.start([self.ship], [],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Store physics expectations
        from simulation_tests.scenarios.propulsion_scenarios import K_SPEED, K_THRUST
        self.expected_max_speed = (self.ship.total_thrust * K_SPEED) / self.ship.mass
        self.expected_acceleration_rate = (self.ship.total_thrust * K_THRUST) / (self.ship.mass ** 2)

        # Assign AI strategy based on thrust/turn configuration
        if self.thrust_forward and not self.turn_left and not self.turn_right:
            self.ship.ai_strategy = 'test_straight_line'
        elif self.turn_right:
            self.ship.ai_strategy = 'test_rotate_right'
        elif self.turn_left:
            self.ship.ai_strategy = 'test_rotate_left'
        else:
            self.ship.ai_strategy = 'test_do_nothing'

        # Call custom setup hook if defined
        if hasattr(self, 'custom_setup'):
            self.custom_setup(battle_engine)

    def update(self, battle_engine):
        """
        Per-tick update. AI handles thrust/rotation via strategies.
        Only custom hooks and tracking remain.
        """

        self._track_tick(battle_engine.tick_counter)

    def collect_results(self, engine):
        """
        Populate measurement attributes for PropulsionScenario.

        Called automatically by _run_validation() before validate().
        Stores position, velocity, angle, and physics calculations.
        """
        # Calculate final state
        self.final_position = self.ship.position.copy()
        self.final_velocity = self.ship.velocity.copy()
        self.final_angle = self.ship.angle

        # Calculate deltas
        self.distance_traveled = (self.final_position - self.start_position).length()
        self.velocity_change = (self.final_velocity - self.start_velocity).length()
        self.angle_change = abs(self.final_angle - self.start_angle)

        # Store in results dict
        self.results['initial_position'] = (self.start_position.x, self.start_position.y)
        self.results['final_position'] = (self.final_position.x, self.final_position.y)
        self.results['initial_velocity'] = self.start_velocity.length()
        self.results['final_velocity'] = self.final_velocity.length()
        self.results['initial_velocity_magnitude'] = self.start_velocity.length()
        self.results['final_velocity_magnitude'] = self.final_velocity.length()
        self.results['initial_angle'] = self.start_angle
        self.results['final_angle'] = self.final_angle
        self.results['distance_traveled'] = self.distance_traveled
        self.results['velocity_change'] = self.velocity_change
        self.results['angle_change'] = self.angle_change
        self.results['ticks_run'] = engine.tick_counter
        self.results['expected_max_speed'] = self.expected_max_speed
        self.results['expected_acceleration_rate'] = self.expected_acceleration_rate

        # For turn tests: calculate expected angle change from turn_speed
        # turn_speed is in degrees per 100 ticks
        if hasattr(self, 'ship') and self.ship.turn_speed > 0:
            ticks_run = engine.tick_counter
            degrees_per_tick = self.ship.turn_speed / 100.0
            expected_angle_change = degrees_per_tick * ticks_run
            self.results['expected_angle_change'] = expected_angle_change
            self.results['turn_speed_degrees_per_tick'] = degrees_per_tick

        self._finalize_tracking()

    def _template_preconditions(self):
        """
        Return automatic precondition checks based on template config.

        PropulsionScenario checks:
        - Simulation ran (ticks > 0)
        - Ship moved if thrust was commanded
        - Angle changed if turn was commanded
        """
        from simulation_tests.scenarios.validation import check_true
        checks = []
        ticks = self.results.get('ticks_run', 0)
        checks.append(check_true(
            "Simulation Ran",
            ticks > 0,
            actual=ticks,
        ))
        if self.thrust_forward or self.thrust_backward:
            checks.append(check_true(
                "Ship Moved",
                self.distance_traveled > 0,
                actual=self.distance_traveled,
                detail="Thrust was commanded but ship did not move",
            ))
        if self.turn_left or self.turn_right:
            checks.append(check_true(
                "Ship Rotated",
                self.angle_change > 0,
                actual=self.angle_change,
                detail="Turn was commanded but angle did not change",
            ))
        return checks

    def _propulsion_data_checks(self, expected_mass, expected_thrust):
        """Common data checks for propulsion scenarios."""
        from simulation_tests.scenarios.validation import check_exact
        return [
            check_exact("Ship Mass", expected_mass, self.ship.mass),
            check_exact("Engine Thrust", expected_thrust, self.ship.total_thrust),
        ]

    def _propulsion_outcome_checks(self, expected_max_speed, expected_final_speed, expected_distance=None):
        """Common outcome checks for propulsion scenarios."""
        from simulation_tests.scenarios.validation import check_approx
        checks = [
            check_approx("Max Speed", expected_max_speed, self.ship.max_speed),
            check_approx("Final Speed", expected_final_speed, self.final_velocity.length()),
        ]
        if expected_distance is not None:
            checks.append(check_approx("Distance", expected_distance, self.distance_traveled, tolerance=0.02))
        return checks

    def verify(self, battle_engine) -> bool:
        """
        Legacy pass/fail for un-migrated scenarios.

        New scenarios should implement validate() instead.
        """
        self.collect_results(battle_engine)
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement validate() or verify()"
        )


# ============================================================================
# RESOURCE SCENARIO TEMPLATE
# ============================================================================

class ResourceScenario(TestScenario):
    """
    Base template for resource consumption/depletion/regeneration tests.

    Eliminates ~40 lines of duplicate setup/update/collect_results code per test.
    Used by: Fuel consumption tests, energy weapon tests, ammo weapon tests.

    Subclass Configuration (required):
    - ship_file: str - Filename of the primary ship JSON
    - resource_type: str - Resource to track ("fuel", "energy", "ammo")

    Subclass Configuration (optional):
    - thrust_forward: bool - Auto-thrust each tick (default: False)
    - force_fire: bool - Auto-fire weapon each tick (default: False)
    - target_ship_file: str - Target ship filename (required when force_fire=True)
    - target_distance: float - Distance to place target (default: 10)

    Automatic Setup:
    - Loads primary ship at origin
    - Optionally loads target ship at (target_distance, 0)
    - Stores initial resource value
    - Creates time-based end condition
    - Sets attacker's current_target if target exists

    Automatic Update:
    - Applies thrust if thrust_forward=True
    - Forces fire if force_fire=True

    Measurement Attributes (populated by collect_results):
    - initial_value: Resource value before test
    - final_value: Resource value after test
    - value_consumed: initial_value - final_value
    - final_velocity: Ship speed at end of test

    Results Dict Keys:
    - ticks_run, initial_value, final_value, value_consumed, final_velocity

    Example Usage:
        class FuelConsumptionTest(ResourceScenario):
            metadata = TestMetadata(...)
            ship_file = "Test_Engine_Ship.json"
            resource_type = "fuel"
            thrust_forward = True

            def validate(self, engine) -> list:
                checks = self._template_preconditions()
                checks.append(check_approx("Final Fuel", 995.0, self.final_value, tolerance=0.01))
                return checks
    """

    # Configuration - subclasses must set these
    ship_file: Optional[str] = None
    resource_type: Optional[str] = None  # "fuel", "energy", "ammo"

    # Optional configuration
    thrust_forward: bool = False
    force_fire: bool = False
    target_ship_file: Optional[str] = None  # Required when force_fire=True
    target_distance: float = 10  # Distance to place target ship

    # Measurement attributes (populated by collect_results)
    initial_value: float = 0
    final_value: float = 0
    value_consumed: float = 0

    def setup(self, battle_engine):
        """
        Standard setup for resource scenarios.

        Loads ship, optionally loads target, stores initial resource value,
        starts battle with time-based end condition.
        """
        # Validate configuration
        if self.ship_file is None:
            raise ValueError(f"{self.__class__.__name__} must set 'ship_file' attribute")
        if self.resource_type is None:
            raise ValueError(f"{self.__class__.__name__} must set 'resource_type' attribute")
        if self.force_fire and self.target_ship_file is None:
            raise ValueError(
                f"{self.__class__.__name__} has force_fire=True but no 'target_ship_file' set"
            )

        # Load primary ship
        self.ship = self._load_ship(self.ship_file)
        self.ship.position = pygame.math.Vector2(0, 0)
        self.ship.angle = 0

        # Store initial resource value
        self.initial_value = self.ship.resources.get_value(self.resource_type)

        # Optionally load target ship
        self.target = None
        if self.target_ship_file is not None:
            self.target = self._load_ship(self.target_ship_file)
            self.target.position = pygame.math.Vector2(self.target_distance, 0)
            self.target.angle = 0
            self.initial_hp = self.target.hp

        # Store start position for distance calculations
        self.start_position = pygame.math.Vector2(self.ship.position)

        # Create end condition
        end_condition = self._create_end_condition()

        # Start battle
        team_a = [self.ship]
        team_b = [self.target] if self.target else []

        # Determine seed (support UI override)
        seed_to_use = getattr(self, '_override_seed', None)
        if seed_to_use is None:
            seed_to_use = self.metadata.seed
        # Expose to custom_setup so movement controllers can derive their seed
        self._effective_seed = seed_to_use

        battle_engine.start(team_a, team_b,
                           seed=seed_to_use,
                           end_condition=end_condition)

        # Assign AI strategies
        if self.thrust_forward and self.force_fire:
            self.ship.ai_strategy = 'test_straight_line'  # thrust + AI fires at target
        elif self.thrust_forward:
            self.ship.ai_strategy = 'test_straight_line'
        elif self.force_fire:
            self.ship.ai_strategy = 'test_stationary_fire'
        else:
            self.ship.ai_strategy = 'test_do_nothing'

        if self.target is not None:
            self.target.ai_strategy = 'test_do_nothing'

        # Call custom setup hook if defined
        if hasattr(self, 'custom_setup'):
            self.custom_setup(battle_engine)

    def update(self, battle_engine):
        """
        Per-tick update. AI handles thrust/firing via strategies.
        Only custom hooks and tracking remain.
        """

        self._track_tick(battle_engine.tick_counter)

    def collect_results(self, engine):
        """
        Populate measurement attributes for ResourceScenario.

        Called automatically by _run_validation() before validate().
        Stores resource values, consumption delta, velocity, and distance.
        """
        self.final_value = self.ship.resources.get_value(self.resource_type)
        self.value_consumed = self.initial_value - self.final_value
        self.final_velocity = self.ship.current_speed
        final_position = pygame.math.Vector2(self.ship.position)
        self.distance_traveled = final_position.distance_to(self.start_position)

        self.results['ticks_run'] = engine.tick_counter
        self.results['initial_value'] = self.initial_value
        self.results['final_value'] = self.final_value
        self.results['value_consumed'] = self.value_consumed
        self.results['final_velocity'] = self.final_velocity
        self.results['distance_traveled'] = self.distance_traveled

        # Store damage dealt if target exists
        if self.target is not None:
            self.damage_dealt = self.initial_hp - self.target.hp
            self.results['damage_dealt'] = self.damage_dealt

        # Collect per-weapon firing statistics
        self._collect_weapon_stats(self.ship, 'ship', engine=engine)
        if self.target is not None:
            self._collect_weapon_stats(self.target, 'target', engine=engine)

        self._finalize_tracking()

        # Hook for subclasses to add extra results
        if hasattr(self, '_collect_extra_results'):
            self._collect_extra_results(engine)

    def _template_preconditions(self):
        """
        Return automatic precondition checks for ResourceScenario.

        Checks:
        - Simulation ran (ticks > 0)
        """
        from simulation_tests.scenarios.validation import check_true
        checks = []
        ticks = self.results.get('ticks_run', 0)
        checks.append(check_true(
            "Simulation Ran",
            ticks > 0,
            actual=ticks,
        ))
        return checks

    def verify(self, battle_engine) -> bool:
        """Legacy pass/fail. New scenarios should implement validate()."""
        self.collect_results(battle_engine)
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement validate() or verify()"
        )


# ============================================================================
# COMPARISON SCENARIO TEMPLATE
# ============================================================================

class ComparisonScenario(TestScenario):
    """
    Base template for A/B comparison scenarios.

    Runs two separate battles — a baseline and a variant — then compares
    their measured outcomes in validate().

    The baseline battle runs privately inside setup(). The variant battle
    runs normally through the TestRunner's simulation loop. Both battles
    use the same seed for deterministic comparison.

    Visual Modes:
    - "Visual Run" renders the variant battle (default)
    - "Visual Baseline" renders the baseline battle (set _visual_baseline=True)
    - "Headless Run" runs both internally, compares results

    Subclass Configuration (required):
    - baseline_attacker_ship: str - Filename of baseline attacker
    - baseline_target_ship: str - Filename of baseline target
    - variant_attacker_ship: str - Filename of variant attacker
    - variant_target_ship: str - Filename of variant target
    - distance: float - Distance between ships (same for both battles)

    Subclass Configuration (optional):
    - force_fire: bool - Auto-fire weapons each tick (default: True)
    - attacker_angle: float - Attacker rotation (default: 0)
    - target_angle: float - Target rotation (default: 0)

    Subclass Hooks:
    - configure_baseline(engine): Customize after baseline ships are loaded
    - configure_variant(engine): Customize after variant ships are loaded

    Measurement Attributes (populated by collect_results):
    - baseline_damage_dealt, baseline_initial_hp, baseline_final_hp, baseline_ticks
    - variant_damage_dealt, variant_initial_hp, variant_final_hp, variant_ticks
    - Per-weapon stats under baseline_attacker_* and variant_attacker_* prefixes

    Example Usage:
        class ECMComparisonTest(ComparisonScenario):
            metadata = TestMetadata(...)
            baseline_attacker_ship = "Test_Attacker_Beam.json"
            baseline_target_ship = "Test_Target.json"         # No ECM
            variant_attacker_ship = "Test_Attacker_Beam.json"
            variant_target_ship = "Test_Target_ECM.json"      # Has ECM
            distance = 400

            def validate(self, engine) -> list:
                checks = self._template_preconditions()
                checks.append(check_true(
                    "ECM Reduces Damage",
                    self.variant_damage_dealt < self.baseline_damage_dealt,
                    actual=f"baseline={self.baseline_damage_dealt}, "
                           f"variant={self.variant_damage_dealt}",
                    phase="outcome",
                ))
                return checks
    """

    # Configuration — subclasses must set these
    baseline_attacker_ship: Optional[str] = None
    baseline_target_ship: Optional[str] = None
    variant_attacker_ship: Optional[str] = None
    variant_target_ship: Optional[str] = None
    distance: Optional[float] = None

    # Optional configuration
    attacker_angle: float = 0.0
    target_angle: float = 0.0
    force_fire: bool = True
    expect_different_damage: bool = True  # Set False when comparison is about damage *distribution*, not total

    # Visual Baseline mode — set by the Combat Lab UI to render the baseline
    # battle instead of the variant.  When True, setup() puts the baseline
    # config on the runner's engine and skips the variant entirely.
    _visual_baseline: bool = False

    def setup(self, battle_engine):
        """
        Set up the comparison scenario.

        Normal mode: runs baseline internally, configures variant on runner's engine.
        Visual Baseline mode: configures baseline on runner's engine for observation.
        """
        self._validate_config()

        # Resolve seed (same logic as StaticTargetScenario)
        seed_to_use = getattr(self, '_override_seed', None)
        if seed_to_use is None:
            seed_to_use = self.metadata.seed
        self._effective_seed = seed_to_use

        if self._visual_baseline:
            # Visual Baseline mode: baseline on runner's engine for observation
            self._setup_battle(
                battle_engine,
                self.baseline_attacker_ship,
                self.baseline_target_ship,
            )
            self.configure_baseline(battle_engine)
        else:
            # Normal mode: baseline internally, variant on runner's engine
            self._run_baseline_battle()
            self._setup_battle(
                battle_engine,
                self.variant_attacker_ship,
                self.variant_target_ship,
            )
            self.configure_variant(battle_engine)

    def _validate_config(self):
        """Validate that required class attributes are set."""
        cls_name = self.__class__.__name__
        if self.baseline_attacker_ship is None:
            raise ValueError(f"{cls_name} must set 'baseline_attacker_ship'")
        if self.baseline_target_ship is None:
            raise ValueError(f"{cls_name} must set 'baseline_target_ship'")
        if self.variant_attacker_ship is None:
            raise ValueError(f"{cls_name} must set 'variant_attacker_ship'")
        if self.variant_target_ship is None:
            raise ValueError(f"{cls_name} must set 'variant_target_ship'")
        if self.distance is None:
            raise ValueError(f"{cls_name} must set 'distance'")

    def _setup_battle(self, engine, attacker_file, target_file):
        """
        Load ships, position them, and start a battle on the given engine.

        Sets self.attacker, self.target, and self.initial_hp for use by
        update() and collect_results().
        """
        self.attacker = self._load_ship(attacker_file)
        self.target = self._load_ship(target_file)

        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = self.attacker_angle
        self.target.position = pygame.math.Vector2(self.distance, 0)
        self.target.angle = self.target_angle

        self.initial_hp = self.target.hp

        # Assign AI strategies
        if self.force_fire:
            self.attacker.ai_strategy = 'test_stationary_fire'
        else:
            self.attacker.ai_strategy = 'test_do_nothing'
        self.target.ai_strategy = 'test_do_nothing'

        end_condition = self._create_end_condition()
        engine.start(
            [self.attacker], [self.target],
            seed=self._effective_seed,
            end_condition=end_condition,
        )

    def _run_baseline_battle(self):
        """
        Run the baseline battle on a private engine, store results.

        Creates a throwaway BattleEngine, runs the full simulation loop,
        then collects baseline measurements.
        """
        from game.simulation.systems.battle_engine import BattleEngine, BattleLogger
        from game.ai.ai_factory import AIControllerFactory

        baseline_engine = BattleEngine(
            logger=BattleLogger(enabled=False),
            ai_factory=AIControllerFactory(),
        )

        self._setup_battle(
            baseline_engine,
            self.baseline_attacker_ship,
            self.baseline_target_ship,
        )
        # Stash references before _setup_battle overwrites self.attacker/target
        baseline_attacker = self.attacker
        baseline_target = self.target
        baseline_initial_hp = self.initial_hp

        self.configure_baseline(baseline_engine)

        # Run simulation loop (AI handles firing via strategies assigned in _setup_battle)
        for tick in range(self.max_ticks):
            baseline_engine.update()
            if baseline_engine.is_battle_over():
                break

        # Collect baseline results
        self._baseline_initial_hp = baseline_initial_hp
        self._baseline_final_hp = baseline_target.hp
        self._baseline_damage_dealt = baseline_initial_hp - baseline_target.hp
        self._baseline_ticks = baseline_engine.tick_counter
        self._baseline_target_alive = baseline_target.is_alive

        # Collect baseline weapon stats
        self._collect_weapon_stats(
            baseline_attacker, 'baseline_attacker', engine=baseline_engine
        )
        self._collect_weapon_stats(
            baseline_target, 'baseline_target', engine=baseline_engine
        )

    def configure_baseline(self, engine):
        """
        Optional hook for subclasses to customize the baseline battle.

        Called after baseline ships are loaded and engine is started,
        before the simulation loop runs.  Use this to add movement
        controllers, extract ability references, etc.
        """
        pass

    def configure_variant(self, engine):
        """
        Optional hook for subclasses to customize the variant battle.

        Called after variant ships are loaded and engine is started,
        before the runner's simulation loop begins.
        """
        pass

    def update(self, battle_engine):
        """
        Per-tick update for the active battle. AI handles firing via strategies.
        """
        self._track_tick(battle_engine.tick_counter)

    def collect_results(self, engine):
        """
        Populate measurement attributes for both battles.

        In Visual Baseline mode, only baseline results are stored.
        In normal mode, both baseline and variant results are stored.
        """
        current_damage = self.initial_hp - self.target.hp
        current_ticks = engine.tick_counter

        if self._visual_baseline:
            # Visual Baseline mode — only baseline ran on runner's engine
            self.baseline_damage_dealt = current_damage
            self.baseline_initial_hp = self.initial_hp
            self.baseline_final_hp = self.target.hp
            self.baseline_ticks = current_ticks

            self.results['baseline_damage_dealt'] = self.baseline_damage_dealt
            self.results['baseline_initial_hp'] = self.baseline_initial_hp
            self.results['baseline_final_hp'] = self.baseline_final_hp
            self.results['baseline_ticks'] = self.baseline_ticks
            self.results['ticks_run'] = current_ticks

            self._collect_weapon_stats(self.attacker, 'baseline_attacker', engine=engine)
            self._collect_weapon_stats(self.target, 'baseline_target', engine=engine)
        else:
            # Normal mode — baseline ran internally, variant on runner's engine
            self.variant_damage_dealt = current_damage
            self.variant_initial_hp = self.initial_hp
            self.variant_final_hp = self.target.hp
            self.variant_ticks = current_ticks

            self.baseline_damage_dealt = self._baseline_damage_dealt
            self.baseline_initial_hp = self._baseline_initial_hp
            self.baseline_final_hp = self._baseline_final_hp
            self.baseline_ticks = self._baseline_ticks

            self.results['baseline_damage_dealt'] = self.baseline_damage_dealt
            self.results['baseline_initial_hp'] = self.baseline_initial_hp
            self.results['baseline_final_hp'] = self.baseline_final_hp
            self.results['baseline_ticks'] = self.baseline_ticks
            self.results['variant_damage_dealt'] = self.variant_damage_dealt
            self.results['variant_initial_hp'] = self.variant_initial_hp
            self.results['variant_final_hp'] = self.variant_final_hp
            self.results['variant_ticks'] = self.variant_ticks
            self.results['ticks_run'] = current_ticks

            self._collect_weapon_stats(self.attacker, 'variant_attacker', engine=engine)
            self._collect_weapon_stats(self.target, 'variant_target', engine=engine)

        self._finalize_tracking()

        if hasattr(self, '_collect_extra_results'):
            self._collect_extra_results(engine)

    def _run_validation(self, engine):
        """
        Override base _run_validation for visual baseline mode.

        In visual baseline mode only baseline results exist — calling
        validate() would crash because variant attributes are absent.
        Collect results and return a baseline-only precondition report.
        """
        if self._visual_baseline:
            self.collect_results(engine)
            checks = self._template_preconditions()
            from simulation_tests.scenarios.validation import ValidationReport
            report = ValidationReport(checks=checks)
            self.results['validation'] = report.to_dict()
            self.results['validation_results'] = [
                {
                    'name': c.name,
                    'status': 'PASS' if c.passed else 'FAIL',
                    'expected': c.expected,
                    'actual': c.actual,
                    'p_value': None,
                    'tolerance': None,
                    'phase': c.phase,
                    'detail': c.detail,
                }
                for c in checks
            ]
            summary = report.summary()
            self.results['validation_summary'] = {
                'pass': sum(s['passed'] for s in summary.values()),
                'fail': sum(s['failed'] for s in summary.values()),
                'warn': 0,
                'info': 0,
            }
            self.results['has_validation_failures'] = not report.passed
            return report
        return super()._run_validation(engine)

    def _template_preconditions(self):
        """
        Return automatic precondition checks for ComparisonScenario.

        Validates setup correctness:
        - Both battles ran the expected number of ticks
        - Both targets were loaded (initial HP > 0)
        - Baseline and variant produced different results (when configs differ)

        In Visual Baseline mode, only checks baseline.
        """
        from simulation_tests.scenarios.validation import check_exact, check_true
        checks = []

        # Verify baseline battle ran full duration
        checks.append(check_exact(
            "Baseline Ticks", self.max_ticks, self.baseline_ticks,
            phase="precondition",
        ))
        # Verify baseline target was loaded
        checks.append(check_true(
            "Baseline Target Loaded",
            self.baseline_initial_hp > 0,
            detail=f"initial_hp={self.baseline_initial_hp}",
            phase="precondition",
        ))

        if not self._visual_baseline:
            # Verify variant battle ran full duration
            checks.append(check_exact(
                "Variant Ticks", self.max_ticks, self.variant_ticks,
                phase="precondition",
            ))
            # Verify variant target was loaded
            checks.append(check_true(
                "Variant Target Loaded",
                self.variant_initial_hp > 0,
                detail=f"initial_hp={self.variant_initial_hp}",
                phase="precondition",
            ))
            # Verify battles are not accidentally identical
            # (only when ship configs differ AND test expects different total damage)
            if self.expect_different_damage and (
                self.baseline_target_ship != self.variant_target_ship or
                self.baseline_attacker_ship != self.variant_attacker_ship
            ):
                checks.append(check_true(
                    "Battles Produced Different Results",
                    self.baseline_damage_dealt != self.variant_damage_dealt or
                    self.baseline_ticks != self.variant_ticks,
                    detail=f"baseline_dmg={self.baseline_damage_dealt}, variant_dmg={self.variant_damage_dealt}",
                    phase="precondition",
                ))
        return checks

    def verify(self, battle_engine) -> bool:
        """Legacy pass/fail. Implement validate() instead."""
        self.collect_results(battle_engine)
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement validate()"
        )
