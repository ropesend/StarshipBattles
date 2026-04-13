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

        def validate(self, outcome, telemetry=None):
            checks = self._template_preconditions()
            checks.append(check_true(
                "Damage dealt", self.damage_dealt > 100,
                detail=f"damage={self.damage_dealt}", phase="outcome",
            ))
            return checks
"""

import pygame
from typing import Optional
from combat_lab.scenarios.base import TestScenario


# ---------------------------------------------------------------------------
# PROJ-269 Task 6.7a: helpers for run_battle-path `wire_ships` lookups.
# ---------------------------------------------------------------------------


def _pre_start_hp(initial_state, role, *, fallback):
    """Read a role's pre-engine-start HP from the snapshot dict.

    Falls back to the provided value when no snapshot is available
    (e.g., legacy `setup()` path still uses ships live-read).
    """
    if initial_state is None:
        return fallback
    entry = initial_state.get(role)
    if entry is None:
        return fallback
    return entry.get("hp", fallback)


def _pre_start_resource(initial_state, role, resource_name, *, fallback):
    """Read a role's pre-engine-start resource value from the snapshot."""
    if initial_state is None:
        return fallback
    entry = initial_state.get(role)
    if entry is None:
        return fallback
    return entry.get("resources", {}).get(resource_name, fallback)


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

            def validate(self, outcome, telemetry=None):
                checks = self._template_preconditions()
                checks.append(check_true(
                    "Damage dealt", self.damage_dealt > 0,
                    detail=f"damage={self.damage_dealt}", phase="outcome",
                ))
                return checks
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

    def wire_ships(self, ships_by_role, *, engine=None, initial_state=None):
        """Wire materialized Ships onto the scenario (PROJ-269 Task 6.7a).

        Used by `combat_lab/runner.py::_run_scenario_via_battle_runner` —
        replaces the side-effect wiring previously done inside `setup()`.
        Mirrors `setup()`'s tail: cache attacker/target refs, store
        `initial_hp`, and apply movement policies.
        """
        _ = engine
        self.attacker = ships_by_role["attacker"]
        self.target = ships_by_role["target"]
        # Prefer pre-start snapshot so `initial_hp` matches the
        # materialized ship's HP before `engine.start()` touched it.
        self.initial_hp = _pre_start_hp(
            initial_state, "target", fallback=self.target.hp
        )
        if self.force_fire:
            self.attacker.movement_policy = "test_stationary"
        else:
            self.attacker.movement_policy = "test_do_nothing"
        self.target.movement_policy = "test_do_nothing"

    def update(self, battle_engine):
        """Per-tick update. AI handles firing and movement via strategies."""
        if self.skip_test:
            return
        self._track_tick(battle_engine.tick_counter)

    def collect_results(self, outcome, telemetry=None):
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
        self.results['ticks_run'] = outcome.duration_ticks
        self.results['target_alive'] = self.target.is_alive

        if outcome.duration_ticks > 0 and self.damage_dealt > 0:
            self.results['hit_rate'] = self.damage_dealt / outcome.duration_ticks

        # Collect per-weapon firing statistics (pass engine for in-flight counting)
        if hasattr(self, 'attacker') and self.attacker:
            self._collect_weapon_stats(self.attacker, 'attacker', telemetry=telemetry)
        if hasattr(self, 'target') and self.target:
            self._collect_weapon_stats(self.target, 'target', telemetry=telemetry)

        self._finalize_tracking()

        for key in self.custom_result_keys:
            if hasattr(self, key):
                self.results[key] = getattr(self, key)

        # Scenario-specific extra-results hook
        self._collect_extra_results(outcome, telemetry)

    def _template_preconditions(self):
        """
        Return automatic precondition checks based on template config.

        StaticTargetScenario checks:
        - Simulation ran (ticks > 0)
        - Weapon fired if force_fire was set
        """
        from combat_lab.scenarios.validation import check_true
        checks = []
        ticks = self.results.get('ticks_run', 0)
        checks.append(check_true(
            "Simulation Ran",
            ticks > 0,
            actual=ticks,
        ))
        return checks

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

            def validate(self, outcome, telemetry=None):
                checks = self._template_preconditions()
                checks.append(check_true(
                    "Ship1 wins", self.winner == 'ship1',
                    detail=f"winner={self.winner}", phase="outcome",
                ))
                return checks
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

    def wire_ships(self, ships_by_role, *, engine=None, initial_state=None):
        """Wire materialized Ships onto the scenario (PROJ-269 Task 6.7a)."""
        _ = engine
        self.ship1 = ships_by_role["ship1"]
        self.ship2 = ships_by_role["ship2"]
        self.ship1_initial_hp = _pre_start_hp(
            initial_state, "ship1", fallback=self.ship1.hp
        )
        self.ship2_initial_hp = _pre_start_hp(
            initial_state, "ship2", fallback=self.ship2.hp
        )
        if self.force_fire:
            self.ship1.movement_policy = "test_stationary"
            self.ship2.movement_policy = "test_stationary"
        else:
            self.ship1.movement_policy = "test_do_nothing"
            self.ship2.movement_policy = "test_do_nothing"

    def update(self, battle_engine):
        """
        Per-tick update. AI handles firing via strategies.
        Only custom hooks and tracking remain.
        """

        self._track_tick(battle_engine.tick_counter)

    def collect_results(self, outcome, telemetry=None):
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
        self.results['ticks_run'] = outcome.duration_ticks
        self.results['ship1_alive'] = self.ship1.is_alive
        self.results['ship2_alive'] = self.ship2.is_alive

        # Collect per-weapon firing statistics
        self._collect_weapon_stats(self.ship1, 'ship1', telemetry=telemetry)
        self._collect_weapon_stats(self.ship2, 'ship2', telemetry=telemetry)

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
        from combat_lab.scenarios.validation import check_true
        checks = []
        ticks = self.results.get('ticks_run', 0)
        checks.append(check_true("Simulation Ran", ticks > 0, actual=ticks))
        return checks

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

            def validate(self, outcome, telemetry=None):
                checks = self._template_preconditions()
                checks.append(check_true(
                    "Accelerated",
                    self.final_velocity.length() > self.initial_velocity.length(),
                    phase="outcome",
                ))
                return checks
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

    def wire_ships(self, ships_by_role, *, engine=None, initial_state=None):
        """Wire materialized Ship onto the scenario (PROJ-269 Task 6.7a).

        Mirrors the tail of `setup()`: cache start pose, compute physics
        expectations, apply movement policy based on thrust/turn flags.
        """
        _ = engine, initial_state
        self.ship = ships_by_role["ship"]
        self.start_position = self.ship.position.copy()
        self.start_velocity = self.ship.velocity.copy()
        self.start_angle = self.ship.angle

        from combat_lab.scenarios.propulsion_scenarios import K_SPEED, K_THRUST
        self.expected_max_speed = (self.ship.total_thrust * K_SPEED) / self.ship.mass
        self.expected_acceleration_rate = (
            (self.ship.total_thrust * K_THRUST) / (self.ship.mass ** 2)
        )

        if self.thrust_forward and not self.turn_left and not self.turn_right:
            self.ship.movement_policy = "test_straight_line"
        elif self.turn_right:
            self.ship.movement_policy = "test_rotate_right"
        elif self.turn_left:
            self.ship.movement_policy = "test_rotate_left"
        else:
            self.ship.movement_policy = "test_do_nothing"

    def update(self, battle_engine):
        """
        Per-tick update. AI handles thrust/rotation via strategies.
        Only custom hooks and tracking remain.
        """

        self._track_tick(battle_engine.tick_counter)

    def collect_results(self, outcome, telemetry=None):
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
        self.results['ticks_run'] = outcome.duration_ticks
        self.results['expected_max_speed'] = self.expected_max_speed
        self.results['expected_acceleration_rate'] = self.expected_acceleration_rate

        # For turn tests: calculate expected angle change from turn_speed
        # turn_speed is in degrees per 100 ticks
        if hasattr(self, 'ship') and self.ship.turn_speed > 0:
            ticks_run = outcome.duration_ticks
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
        from combat_lab.scenarios.validation import check_true
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
        from combat_lab.scenarios.validation import check_exact
        return [
            check_exact("Ship Mass", expected_mass, self.ship.mass),
            check_exact("Engine Thrust", expected_thrust, self.ship.total_thrust),
        ]

    def _propulsion_outcome_checks(self, expected_max_speed, expected_final_speed, expected_distance=None):
        """Common outcome checks for propulsion scenarios."""
        from combat_lab.scenarios.validation import check_approx
        checks = [
            check_approx("Max Speed", expected_max_speed, self.ship.max_speed),
            check_approx("Final Speed", expected_final_speed, self.final_velocity.length()),
        ]
        if expected_distance is not None:
            checks.append(check_approx("Distance", expected_distance, self.distance_traveled, tolerance=0.02))
        return checks

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

            def validate(self, outcome, telemetry=None) -> list:
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

    def wire_ships(self, ships_by_role, *, engine=None, initial_state=None):
        """Wire materialized Ships onto the scenario (PROJ-269 Task 6.7a)."""
        _ = engine
        self.ship = ships_by_role["ship"]
        # Always prefer the pre-engine-start snapshot for initial_value —
        # `engine.start()` runs an initial component-update cycle that
        # drains always-on resources (fuel/energy) by ~1 tick's worth.
        self.initial_value = _pre_start_resource(
            initial_state, "ship", self.resource_type,
            fallback=self.ship.resources.get_value(self.resource_type),
        )
        self.start_position = pygame.math.Vector2(self.ship.position)

        self.target = ships_by_role.get("target")
        if self.target is not None:
            self.initial_hp = _pre_start_hp(
                initial_state, "target", fallback=self.target.hp
            )

        if self.thrust_forward and self.force_fire:
            self.ship.movement_policy = "test_straight_line"
        elif self.thrust_forward:
            self.ship.movement_policy = "test_straight_line"
        elif self.force_fire:
            self.ship.movement_policy = "test_stationary"
        else:
            self.ship.movement_policy = "test_do_nothing"

        if self.target is not None:
            self.target.movement_policy = "test_do_nothing"

    def update(self, battle_engine):
        """
        Per-tick update. AI handles thrust/firing via strategies.
        Only custom hooks and tracking remain.
        """

        self._track_tick(battle_engine.tick_counter)

    def collect_results(self, outcome, telemetry=None):
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

        self.results['ticks_run'] = outcome.duration_ticks
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
        self._collect_weapon_stats(self.ship, 'ship', telemetry=telemetry)
        if self.target is not None:
            self._collect_weapon_stats(self.target, 'target', telemetry=telemetry)

        self._finalize_tracking()

        # Scenario-specific extra-results hook
        self._collect_extra_results(outcome, telemetry)

    def _template_preconditions(self):
        """
        Return automatic precondition checks for ResourceScenario.

        Checks:
        - Simulation ran (ticks > 0)
        """
        from combat_lab.scenarios.validation import check_true
        checks = []
        ticks = self.results.get('ticks_run', 0)
        checks.append(check_true(
            "Simulation Ran",
            ticks > 0,
            actual=ticks,
        ))
        return checks

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

            def validate(self, outcome, telemetry=None) -> list:
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


    def _run_baseline_battle(self):
        """Run the private baseline battle via `run_battle(spec)`.

        PROJ-269 Task 6.8: replaces the legacy throwaway-`BattleEngine(...)`
        path. Compiles a dedicated baseline `BattleSpec` with
        `baseline_*_ship` files, runs it through the unified entry, then
        captures the same metrics onto `self._baseline_*` attributes the
        legacy code exposed.
        """
        from game.ai.ai_factory import AIControllerFactory
        from game.simulation.battle_runner import run_battle

        baseline_spec = self._build_baseline_battle_spec()

        # Role-keyed ship registry populated by ship_builder.
        baseline_ships: dict = {}

        def ship_builder(ship_spec):
            ship = self._load_ship(ship_spec.design_id)
            if ship_spec.instance_id.endswith(":baseline_attacker"):
                baseline_ships["attacker"] = ship
            elif ship_spec.instance_id.endswith(":baseline_target"):
                baseline_ships["target"] = ship
            return ship

        # PROJ-270 Phase 2.5: capture in-flight projectile counts via
        # per_tick callback — replaces the engine_ref closure trick.
        baseline_in_flight: dict = {}

        def pre_tick_loop(engine):
            """Wire the baseline ships and invoke the configure_baseline hook."""
            attacker = baseline_ships["attacker"]
            target = baseline_ships["target"]
            # Temporarily bind the baseline ships onto `self.attacker` /
            # `self.target` so `configure_baseline` (which subclasses
            # implement using `self.target.movement_policy = ...` etc.)
            # references the right ships. The outer wire_ships will rebind
            # these to variant ships after _run_baseline_battle returns.
            self.attacker = attacker
            self.target = target
            self.initial_hp = target.hp
            if self.force_fire:
                attacker.movement_policy = "test_stationary"
            else:
                attacker.movement_policy = "test_do_nothing"
            target.movement_policy = "test_do_nothing"
            self.configure_baseline(engine)

        def per_tick(engine):
            # Capture in-flight projectiles per role; only final tick kept.
            for role_key, ship_ref in baseline_ships.items():
                baseline_in_flight[role_key] = sum(
                    1 for p in engine.projectiles
                    if p.is_alive and p.owner is ship_ref
                )

        baseline_outcome = run_battle(
            baseline_spec,
            ai_factory=AIControllerFactory(),
            ship_builder=ship_builder,
            pre_tick_loop_callback=pre_tick_loop,
            per_tick_callback=per_tick,
        )

        baseline_attacker = baseline_ships["attacker"]
        baseline_target = baseline_ships["target"]

        # Stash references + collect metrics (same shape as the legacy path).
        self._baseline_attacker = baseline_attacker
        self._baseline_target = baseline_target
        self._baseline_initial_hp = self.initial_hp
        self._baseline_final_hp = baseline_target.hp
        self._baseline_damage_dealt = self.initial_hp - baseline_target.hp
        self._baseline_ticks = baseline_outcome.duration_ticks
        self._baseline_target_alive = baseline_target.is_alive

        # Collect baseline weapon stats. Build a mini CombatLabTelemetry so
        # in-flight counts flow through `_collect_weapon_stats`.
        from combat_lab.telemetry import CombatLabTelemetry
        baseline_telemetry = CombatLabTelemetry(in_flight_by_role={
            "baseline_attacker": baseline_in_flight.get("attacker", 0),
            "baseline_target": baseline_in_flight.get("target", 0),
        })
        self._collect_weapon_stats(
            baseline_attacker, "baseline_attacker", telemetry=baseline_telemetry
        )
        self._collect_weapon_stats(
            baseline_target, "baseline_target", telemetry=baseline_telemetry
        )

    def _build_baseline_battle_spec(self):
        """Build the BattleSpec for the private baseline battle.

        Structurally identical to `_compile_comparison` in the compiler,
        but uses `baseline_*_ship` files regardless of `_visual_baseline`.
        """
        from game.core.math import Vector2
        from game.simulation.battle_spec import ( BattleSpec, CombatPolicies, EntryVector,
            ShipSpec, SquadronSpec, TaskForceSpec, TeamSpec,
        )
        from game.simulation.combat.boundary import UnboundedRegion
        from game.simulation.combat.formation import FormationShape, FormationSpec
        from game.simulation.combat.modifier_stack import ModifierStack
        from game.simulation.combat.telemetry import TelemetryLevel

        attacker = ShipSpec(
            instance_id=f"{self.metadata.test_id}:baseline_attacker",
            design_id=self.baseline_attacker_ship,
            theme_id="Federation",
            name=f"{self.metadata.test_id}-baseline_attacker",
            position=Vector2(0.0, 0.0),
            angle=float(self.attacker_angle),
            velocity=Vector2(0.0, 0.0),
            components=(),
        )
        target = ShipSpec(
            instance_id=f"{self.metadata.test_id}:baseline_target",
            design_id=self.baseline_target_ship,
            theme_id="Federation",
            name=f"{self.metadata.test_id}-baseline_target",
            position=Vector2(float(self.distance), 0.0),
            angle=float(self.target_angle),
            velocity=Vector2(0.0, 0.0),
            components=(),
        )
        single_custom = FormationSpec(
            shape=FormationShape.CUSTOM,
            spacing=100.0,
            custom_positions=(Vector2(0.0, 0.0),),
        )

        def _team(team_id, name, ship, origin, facing):
            return TeamSpec(
                team_id=team_id, name=name,
                entry_vector=EntryVector(origin=origin, facing=facing),
                fleet_hierarchy=(
                    TaskForceSpec(
                        task_force_id=f"tf-{name.lower()}",
                        formation=single_custom,
                        policies=CombatPolicies(),
                        squadrons=(
                            SquadronSpec(
                                squadron_id=f"sq-{name.lower()}",
                                policies=CombatPolicies(),
                                ships=(ship,),
                            ),
                        ),
                    ),
                ),
            )

        return BattleSpec(
            seed=self._effective_seed,
            telemetry_level=TelemetryLevel.DETAILED,
            boundary=UnboundedRegion(),
            end_condition=self._create_end_condition(),
            absolute_max_ticks=max(self.metadata.max_ticks * 10, 1000),
            teams=(
                _team(0, "Attacker", attacker, Vector2(0.0, 0.0), 0.0),
                _team(
                    1, "Target", target,
                    Vector2(float(self.distance), 0.0), 180.0,
                ),
            ),
            modifier_stack=ModifierStack.empty(),
            post_battle_hook=None,
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

    def before_run_battle(self, spec) -> None:
        """Run the private baseline battle before the main run_battle.

        Baseline must run BEFORE variant ships are materialized, to
        match the legacy `setup()`'s ship-creation ordering — ship IDs
        are generated during `_load_ship`, and changing the order of
        generation perturbs deterministic same-seed outcomes for
        same-group-MAX comparison scenarios.
        """
        if self._visual_baseline:
            return
        self._effective_seed = spec.seed
        self._run_baseline_battle()

    def wire_ships(self, ships_by_role, *, engine=None, initial_state=None):
        """Wire materialized Ships onto the scenario (PROJ-269 Task 6.7a).

        Assumes `before_run_battle` has already run the private baseline
        battle in normal mode — this method handles variant wiring only
        (or baseline wiring in visual-baseline mode).
        """
        if self._visual_baseline:
            role_attacker, role_target = "baseline_attacker", "baseline_target"
        else:
            role_attacker, role_target = "variant_attacker", "variant_target"

        attacker = ships_by_role[role_attacker]
        target = ships_by_role[role_target]

        self.attacker = attacker
        self.target = target
        self.initial_hp = _pre_start_hp(
            initial_state, role_target, fallback=self.target.hp
        )

        if self.force_fire:
            self.attacker.movement_policy = "test_stationary"
        else:
            self.attacker.movement_policy = "test_do_nothing"
        self.target.movement_policy = "test_do_nothing"

        # Invoke the configure hook for whichever battle runs on the
        # runner's engine. `configure_baseline` for the private baseline
        # engine is already called inside `_run_baseline_battle`.
        if engine is not None:
            if self._visual_baseline:
                self.configure_baseline(engine)
            else:
                self.configure_variant(engine)

    def update(self, battle_engine):
        """
        Per-tick update for the active battle. AI handles firing via strategies.
        """
        self._track_tick(battle_engine.tick_counter)

    def collect_results(self, outcome, telemetry=None):
        """
        Populate measurement attributes for both battles.

        In Visual Baseline mode, only baseline results are stored.
        In normal mode, both baseline and variant results are stored.
        """
        current_damage = self.initial_hp - self.target.hp
        current_ticks = outcome.duration_ticks

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

            self._collect_weapon_stats(self.attacker, 'baseline_attacker', telemetry=telemetry)
            self._collect_weapon_stats(self.target, 'baseline_target', telemetry=telemetry)
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

            self._collect_weapon_stats(self.attacker, 'variant_attacker', telemetry=telemetry)
            self._collect_weapon_stats(self.target, 'variant_target', telemetry=telemetry)

        self._finalize_tracking()

        self._collect_extra_results(outcome, telemetry)

    def _run_validation(self, outcome, telemetry=None):
        """
        Override base _run_validation for visual baseline mode.

        In visual baseline mode only baseline results exist — calling
        validate() would crash because variant attributes are absent.
        Collect results and return a baseline-only precondition report.
        """
        if self._visual_baseline:
            self.collect_results(outcome, telemetry)
            checks = self._template_preconditions()
            from combat_lab.scenarios.validation import ValidationReport
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
        return super()._run_validation(outcome, telemetry)

    def _template_preconditions(self):
        """
        Return automatic precondition checks for ComparisonScenario.

        Validates setup correctness:
        - Both battles ran the expected number of ticks
        - Both targets were loaded (initial HP > 0)
        - Baseline and variant produced different results (when configs differ)

        In Visual Baseline mode, only checks baseline.
        """
        from combat_lab.scenarios.validation import check_exact, check_true
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

