"""
Scenario Templates for Combat Lab Test Framework

These base templates eliminate ~2000 lines of duplicated code across 35+ test scenarios
by providing common setup/update/verify patterns for different test types.

Template Hierarchy:
- TestScenario (base class in base.py)
  - StaticTargetScenario: Attacker vs stationary target
  - DuelScenario: Two ships engaging each other
  - PropulsionScenario: Single ship movement/physics tests

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

    def setup(self, battle_engine):
        """
        Standard setup for static target scenarios.
        Subclasses can override for custom setup, or use configuration attributes.
        """
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

        # Start battle with time-based end condition
        battle_engine.start([self.attacker], [self.target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        self.attacker.current_target = self.target

        # Call custom setup hook if defined
        if hasattr(self, 'custom_setup'):
            self.custom_setup(battle_engine)

    def update(self, battle_engine):
        """
        Standard update for static target scenarios.
        Forces attacker to fire each tick (if force_fire=True).
        Subclasses can override for custom behavior.
        """
        if self.force_fire:
            if self.attacker and self.attacker.is_alive:
                self.attacker.comp_trigger_pulled = True

        # Call custom update hook if defined
        if hasattr(self, 'custom_update'):
            self.custom_update(battle_engine)

    def verify(self, battle_engine) -> bool:
        """
        Standard verification for static target scenarios.
        Stores standard results and optionally verifies damage dealt.
        Subclasses should override for custom verification logic.
        """
        # Calculate damage dealt
        self.damage_dealt = self.initial_hp - self.target.hp

        # Store standard results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Calculate hit rate if applicable (1 damage per hit)
        if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        # Auto-verify if configured
        if self.verify_damage_dealt:
            return self.damage_dealt > 0

        # Subclasses must implement verification
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement verify() or set verify_damage_dealt=True"
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

        # Set mutual targeting
        if self.auto_target:
            self.ship1.current_target = self.ship2
            self.ship2.current_target = self.ship1

        # Call custom setup hook if defined
        if hasattr(self, 'custom_setup'):
            self.custom_setup(battle_engine)

    def update(self, battle_engine):
        """
        Standard update for duel scenarios.
        Forces both ships to fire each tick (if force_fire=True).
        Subclasses can override for custom behavior.
        """
        if self.force_fire:
            if self.ship1 and self.ship1.is_alive:
                self.ship1.comp_trigger_pulled = True
            if self.ship2 and self.ship2.is_alive:
                self.ship2.comp_trigger_pulled = True

        # Call custom update hook if defined
        if hasattr(self, 'custom_update'):
            self.custom_update(battle_engine)

    def verify(self, battle_engine) -> bool:
        """
        Standard verification for duel scenarios.
        Stores comprehensive results about both ships.
        Subclasses should override for custom verification logic.
        """
        # Calculate damage dealt and taken
        self.ship1_damage_taken = self.ship1_initial_hp - self.ship1.hp
        self.ship2_damage_taken = self.ship2_initial_hp - self.ship2.hp
        self.ship1_damage_dealt = self.ship2_damage_taken
        self.ship2_damage_dealt = self.ship1_damage_taken

        # Store comprehensive results
        self.results['ship1_initial_hp'] = self.ship1_initial_hp
        self.results['ship2_initial_hp'] = self.ship2_initial_hp
        self.results['ship1_final_hp'] = self.ship1.hp
        self.results['ship2_final_hp'] = self.ship2.hp
        self.results['ship1_damage_dealt'] = self.ship1_damage_dealt
        self.results['ship2_damage_dealt'] = self.ship2_damage_dealt
        self.results['ship1_damage_taken'] = self.ship1_damage_taken
        self.results['ship2_damage_taken'] = self.ship2_damage_taken
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['ship1_alive'] = self.ship1.is_alive
        self.results['ship2_alive'] = self.ship2.is_alive

        # Determine winner
        if self.ship1.is_alive and not self.ship2.is_alive:
            self.winner = 'ship1'
        elif self.ship2.is_alive and not self.ship1.is_alive:
            self.winner = 'ship2'
        elif not self.ship1.is_alive and not self.ship2.is_alive:
            self.winner = 'draw'
        else:
            self.winner = None  # Both alive or draw
        self.results['winner'] = self.winner

        # Subclasses must implement verification
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement verify() method"
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

        # Call custom setup hook if defined
        if hasattr(self, 'custom_setup'):
            self.custom_setup(battle_engine)

    def update(self, battle_engine):
        """
        Standard update for propulsion scenarios.
        Applies configured thrust/turn commands each tick.
        Subclasses can override for custom behavior.
        """
        if self.ship and self.ship.is_alive:
            if self.thrust_forward:
                self.ship.thrust_forward()
            if self.thrust_backward:
                self.ship.thrust_backward()
            if self.turn_left:
                self.ship.turn_left()
            if self.turn_right:
                self.ship.turn_right()

        # Call custom update hook if defined
        if hasattr(self, 'custom_update'):
            self.custom_update(battle_engine)

    def verify(self, battle_engine) -> bool:
        """
        Standard verification for propulsion scenarios.
        Stores comprehensive movement/physics results.
        Subclasses should override for custom verification logic.
        """
        # Calculate final state
        self.final_position = self.ship.position.copy()
        self.final_velocity = self.ship.velocity.copy()
        self.final_angle = self.ship.angle

        # Calculate deltas
        self.distance_traveled = (self.final_position - self.start_position).length()
        self.velocity_change = (self.final_velocity - self.start_velocity).length()
        self.angle_change = abs(self.final_angle - self.start_angle)

        # Store comprehensive results
        self.results['initial_position'] = (self.start_position.x, self.start_position.y)
        self.results['final_position'] = (self.final_position.x, self.final_position.y)
        self.results['initial_velocity'] = (self.start_velocity.x, self.start_velocity.y)
        self.results['final_velocity'] = (self.final_velocity.x, self.final_velocity.y)
        self.results['initial_velocity_magnitude'] = self.start_velocity.length()
        self.results['final_velocity_magnitude'] = self.final_velocity.length()
        self.results['initial_angle'] = self.start_angle
        self.results['final_angle'] = self.final_angle
        self.results['distance_traveled'] = self.distance_traveled
        self.results['velocity_change'] = self.velocity_change
        self.results['angle_change'] = self.angle_change
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['expected_max_speed'] = self.expected_max_speed
        self.results['expected_acceleration_rate'] = self.expected_acceleration_rate

        # Subclasses must implement verification
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement verify() method"
        )
