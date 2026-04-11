"""
AI Behaviors - Ship Movement and Combat Behaviors

This module defines the behavior classes used by AIController to control
ship movement during combat. Each behavior implements a different tactical
approach.

Behavior Classes:
    AIBehavior: Base class, defines enter() and update() interface

    Combat Behaviors:
        KiteBehavior: Maintain optimal weapon range
            - Close in if too far from target
            - Back off if too close
            - Uses collision avoidance if enabled in strategy
            - engage_distance parameter controls optimal range multiplier

        AttackRunBehavior: Hit-and-run tactics
            - Approach phase: Move toward target until approach_distance
            - Retreat phase: Flee for retreat_duration seconds
            - Cycle repeats automatically
            - Good for high-alpha, long-cooldown weapons

        RamBehavior: Direct collision course
            - Navigate straight to target position
            - No collision avoidance
            - Used by kamikaze ships

        FleeBehavior: Retreat from combat
            - Move away from target at FLEE_DISTANCE
            - fire_while_retreating controls weapon usage
            - Triggered when HP below retreat_hp_threshold

        OrbitBehavior: Circle around target
            - Maintain fixed distance while strafing
            - Good for continuous fire weapons

    Test/Debug Behaviors:
        DoNothingBehavior: No action (for isolated testing)
        StationaryFireBehavior: Fire without moving
        StraightLineBehavior: Move in straight line
        RotateOnlyBehavior: Only rotate, no thrust
        ErraticBehavior: Random movement (stress testing)

Strategy Parameters:
    Behaviors read parameters from the strategy dict passed to update():
    - avoid_collisions: bool - Enable collision avoidance (KiteBehavior)
    - engage_distance: float|'max_range'|'ram' - Range multiplier
    - fire_while_retreating: bool - Fire during flee (FleeBehavior)
    - retreat_hp_threshold: float - HP % to trigger flee
    - attack_run_behavior: dict - approach/retreat distances

Example:
    behavior = KiteBehavior(controller)
    behavior.update(target, strategy={'engage_distance': 0.8})
"""
import random
from typing import Any, Dict, Optional

from game.core.config import AIConfig, PhysicsConfig
from game.core.math import Vector2
import math


def _flee_direction(from_pos: Vector2, away_from_pos: Vector2) -> Vector2:
    """
    Calculate normalized direction vector pointing away from a position.

    Args:
        from_pos: The position to flee from (ship position)
        away_from_pos: The position to flee away from (target position)

    Returns:
        Normalized direction vector, defaults to (1, 0) if positions coincide
    """
    vec = from_pos - away_from_pos
    if vec.length() == 0:
        return Vector2(1, 0)
    return vec.normalize()


class AIBehavior:
    def __init__(self, controller: Any) -> None:
        self.controller = controller
        
    def enter(self) -> None:
        """Called when this behavior becomes active."""
        pass
        
    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        """Execute behavior logic."""
        raise NotImplementedError

class RamBehavior(AIBehavior):
    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        # Ram target, no avoidance
        self.controller.navigate_to(target.position, stop_dist=0)

class FleeBehavior(AIBehavior):
    FLEE_DISTANCE: int = AIConfig.FLEE_DISTANCE

    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        # Run away from target
        fire_while_retreating = strategy.get('fire_while_retreating', False)
        # Note: controller.update sets trigger to True by default, we modify it here if needed
        self.controller.ship.set_trigger_pulled(fire_while_retreating)

        ship_pos = self.controller.ship.get_position()
        flee_dir = _flee_direction(ship_pos, target.position)
        flee_pos = ship_pos + flee_dir * self.FLEE_DISTANCE
        self.controller.navigate_to(flee_pos, stop_dist=0)

class KiteBehavior(AIBehavior):
    """Maintain optimal weapon range from target.

    Decision Tree:
        1. Check collision avoidance (if enabled in strategy)
           - If nearby collision detected → navigate away, return
        2. Calculate optimal distance = weapon_range * engage_distance_multiplier
           - Minimum distance clamped to MIN_SPACING
        3. Compare current distance to optimal:
           - If too far → close in toward target
           - If too close → back off to maintain kite range

    Strategy Parameters:
        avoid_collisions (bool): Enable collision avoidance check (default: True)
        engage_distance (float|str): Range multiplier or 'max_range'/'ram' (default: 'max_range')
    """

    MIN_SPACING: int = AIConfig.MIN_SPACING
    DEFAULT_AVOIDANCE: bool = True

    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        # Collision avoidance if enabled
        if strategy.get('avoid_collisions', self.DEFAULT_AVOIDANCE):
            override_pos = self.controller.check_avoidance()
            if override_pos:
                self.controller.navigate_to(override_pos, stop_dist=0)
                return
        
        # Get engage distance multiplier logic
        engage_mult = self.controller.get_engage_distance_multiplier(strategy)

        # Calculate optimal distance
        opt_dist = self.controller.ship.get_weapon_range() * engage_mult
        if opt_dist < self.MIN_SPACING:
            opt_dist = self.MIN_SPACING  # Minimum spacing

        ship_pos = self.controller.ship.get_position()
        dist = ship_pos.distance_to(target.position)

        if dist > opt_dist:
            # Close in
            self.controller.navigate_to(target.position, stop_dist=opt_dist)
        else:
            # Kite - maintain distance
            kite_dir = _flee_direction(ship_pos, target.position)
            kite_pos = target.position + kite_dir * opt_dist
            self.controller.navigate_to(kite_pos, stop_dist=0)

class AttackRunBehavior(AIBehavior):
    """Hit-and-run attack pattern with approach/retreat cycles.

    State Machine:
        APPROACH → Navigate toward target until within approach_distance
                   (with hysteresis factor to prevent flickering)
                   Transition: distance < approach_distance * HYSTERESIS → RETREAT

        RETREAT  → Flee away from target for retreat_duration seconds
                   Timer decrements by TICK_DURATION each update
                   Transition: timer <= 0 AND distance > retreat_distance → APPROACH

    Strategy Parameters (via 'attack_run_behavior' dict):
        approach_distance (float): Multiplier of weapon_range to approach (default: 0.3)
        retreat_distance (float): Multiplier of weapon_range before re-approaching (default: 0.8)
        retreat_duration (float): Seconds to retreat before checking distance (default: 2.0)

    Best For:
        - High-alpha, long-cooldown weapons (missiles, torpedoes)
        - Ships that need time to cool down or reload between attacks
    """

    DEFAULT_APPROACH_DIST_FACTOR: float = AIConfig.ATTACK_RUN_APPROACH_DIST_FACTOR
    DEFAULT_RETREAT_DIST_FACTOR: float = AIConfig.ATTACK_RUN_RETREAT_DIST_FACTOR
    DEFAULT_RETREAT_DURATION: float = AIConfig.ATTACK_RUN_RETREAT_DURATION
    FLEE_DISTANCE: int = AIConfig.FLEE_DISTANCE
    APPROACH_HYSTERESIS: float = AIConfig.ATTACK_RUN_APPROACH_HYSTERESIS

    def __init__(self, controller: Any) -> None:
        super().__init__(controller)
        self.attack_state: str = 'approach'
        self.attack_timer: float = 0
        
    def enter(self) -> None:
        # Reset state when switching to this behavior
        self.attack_state = 'approach'
        self.attack_timer = 0

    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        behavior_config = strategy.get('attack_run_behavior', {})
        weapon_range = self.controller.ship.get_weapon_range()
        approach_dist = weapon_range * behavior_config.get('approach_distance', self.DEFAULT_APPROACH_DIST_FACTOR)
        retreat_dist = weapon_range * behavior_config.get('retreat_distance', self.DEFAULT_RETREAT_DIST_FACTOR)
        retreat_duration = behavior_config.get('retreat_duration', self.DEFAULT_RETREAT_DURATION)

        ship_pos = self.controller.ship.get_position()
        dist = ship_pos.distance_to(target.position)

        if self.attack_state == 'approach':
            self.controller.navigate_to(target.position, stop_dist=approach_dist)

            if dist < approach_dist * self.APPROACH_HYSTERESIS:
                self.attack_state = 'retreat'
                self.attack_timer = retreat_duration

        elif self.attack_state == 'retreat':
            # Cycle-Based: 1 tick = 0.01 seconds. Decrement timer by 0.01.
            self.attack_timer -= PhysicsConfig.TICK_RATE

            flee_dir = _flee_direction(ship_pos, target.position)
            flee_pos = ship_pos + flee_dir * self.FLEE_DISTANCE

            self.controller.navigate_to(flee_pos, stop_dist=0)

            if self.attack_timer <= 0 and dist > retreat_dist:
                self.attack_state = 'approach'


# =============================================================================
# UTILITY BEHAVIORS
# =============================================================================

class DoNothingBehavior(AIBehavior):
    """Ship sits completely still. No movement, no rotation, no firing."""

    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        # Explicitly disable firing
        self.controller.ship.set_trigger_pulled(False)
        # Do nothing else - no navigation, no rotation


class StationaryFireBehavior(AIBehavior):
    """Ship sits still but can fire weapons. Used for weapon testing."""
    
    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        # Do not disable firing (comp_trigger_pulled stays True from AIController)
        # Do nothing else - no navigation, no rotation
        pass


class StraightLineBehavior(AIBehavior):
    """Full thrust in initial facing direction. No rotation."""
    
    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        # Thrust forward without any rotation
        self.controller.ship.thrust_forward()
        # No rotation commands issued


class RotateOnlyBehavior(AIBehavior):
    """Continuous rotation at max turn rate, no translation."""
    
    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        # Get rotation direction from strategy (default: clockwise = 1)
        direction = strategy.get('rotation_direction', 1)
        self.controller.ship.rotate(direction)
        # No thrust commands issued


class ErraticBehavior(AIBehavior):
    """Random direction changes at random intervals.

    Supports optional leash constraint: if leash_radius is set in the
    movement policy, the ship steers back toward its starting position
    when it drifts beyond that radius.
    """

    def __init__(self, controller: Any) -> None:
        super().__init__(controller)
        self.direction_timer: float = 0.0
        self.current_direction: int = 1
        self.next_change_interval: float = 1.0
        self._leash_center: Optional[Any] = None

    def enter(self) -> None:
        self.direction_timer = 0.0
        self.current_direction = random.choice([-1, 1])
        self.next_change_interval = random.uniform(
            AIConfig.ERRATIC_TURN_INTERVAL_MIN,
            AIConfig.ERRATIC_TURN_INTERVAL_MAX
        )
        # Capture starting position as leash center
        pos = self.controller.ship.get_position()
        self._leash_center = (pos.x, pos.y)

    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        ship = self.controller.ship

        # Leash check: steer back if too far from start
        leash_radius = strategy.get('leash_radius', 0)
        if leash_radius > 0 and self._leash_center:
            pos = ship.get_position()
            dx = pos.x - self._leash_center[0]
            dy = pos.y - self._leash_center[1]
            dist_sq = dx * dx + dy * dy
            if dist_sq > leash_radius * leash_radius:
                # Steer back toward center
                to_cx = self._leash_center[0] - pos.x
                to_cy = self._leash_center[1] - pos.y
                target_angle = math.degrees(math.atan2(to_cy, to_cx)) % 360
                ship_angle = ship.get_rotation() % 360
                diff = (target_angle - ship_angle + 180) % 360 - 180
                if abs(diff) > 2.0:  # Dead band to prevent jitter
                    ship.rotate(1 if diff > 0 else -1)
                ship.thrust_forward()
                return

        # Update timer
        self.direction_timer += PhysicsConfig.TICK_RATE

        # Check if it's time to change direction
        min_interval = strategy.get('turn_interval_min', AIConfig.ERRATIC_TURN_INTERVAL_MIN)
        max_interval = strategy.get('turn_interval_max', AIConfig.ERRATIC_TURN_INTERVAL_MAX)

        if self.direction_timer >= self.next_change_interval:
            # Change direction randomly
            self.current_direction = random.choice([-1, 0, 1])
            self.next_change_interval = random.uniform(min_interval, max_interval)
            self.direction_timer = 0.0

        # Apply rotation if not going straight
        if self.current_direction != 0:
            ship.rotate(self.current_direction)

        # Always thrust forward
        ship.thrust_forward()


class OrbitBehavior(AIBehavior):
    """Circle target at fixed distance."""

    DEFAULT_ORBIT_DISTANCE: int = AIConfig.DEFAULT_ORBIT_DISTANCE
    
    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        if not target:
            return
            
        orbit_distance = strategy.get('orbit_distance', self.DEFAULT_ORBIT_DISTANCE)
        
        ship = self.controller.ship
        ship_pos = ship.get_position()
        vec_to_target = target.position - ship_pos
        dist = vec_to_target.length()
        
        if dist == 0:
            return
        
        # Calculate tangent direction (perpendicular to radial vector)
        # Rotate 90 degrees for counter-clockwise orbit
        radial = vec_to_target.normalize()
        tangent = Vector2(-radial.y, radial.x)
        
        # Adjust radial component to maintain orbit distance
        if dist < orbit_distance * AIConfig.ORBIT_DISTANCE_CLOSE_THRESHOLD:
            # Too close - add outward component
            move_dir = (tangent - radial * AIConfig.ORBIT_RADIAL_COMPONENT).normalize()
        elif dist > orbit_distance * AIConfig.ORBIT_DISTANCE_FAR_THRESHOLD:
            # Too far - add inward component
            move_dir = (tangent + radial * AIConfig.ORBIT_RADIAL_COMPONENT).normalize()
        else:
            # In range - pure tangent
            move_dir = tangent

        # Navigate to a point along the movement direction
        target_pos = ship_pos + move_dir * AIConfig.ORBIT_TARGET_OFFSET
        self.controller.navigate_to(target_pos, stop_dist=0)

