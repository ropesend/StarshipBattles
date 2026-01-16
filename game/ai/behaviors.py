
import pygame
from typing import Any, Dict

from game.core.config import AIConfig, PhysicsConfig

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
        self.controller.navigate_to(target.position, stop_dist=0, precise=False)

class FleeBehavior(AIBehavior):
    FLEE_DISTANCE: int = AIConfig.FLEE_DISTANCE

    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        # Run away from target
        fire_while_retreating = strategy.get('fire_while_retreating', False)
        # Note: controller.update sets trigger to True by default, we modify it here if needed
        self.controller.ship.comp_trigger_pulled = fire_while_retreating
        
        vec = self.controller.ship.position - target.position
        if vec.length() == 0: 
            vec = pygame.math.Vector2(1, 0)
        
        flee_pos = self.controller.ship.position + vec.normalize() * self.FLEE_DISTANCE
        self.controller.navigate_to(flee_pos, stop_dist=0, precise=False)

class KiteBehavior(AIBehavior):
    MIN_SPACING: int = AIConfig.MIN_SPACING
    DEFAULT_AVOIDANCE: bool = True
    
    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        # Collision avoidance if enabled
        if strategy.get('avoid_collisions', self.DEFAULT_AVOIDANCE):
            override_pos = self.controller.check_avoidance()
            if override_pos:
                self.controller.navigate_to(override_pos, stop_dist=0, precise=False)
                return
        
        # Get engage distance multiplier logic
        engage_mult = self.controller.get_engage_distance_multiplier(strategy)
        
        # Calculate optimal distance
        opt_dist = self.controller.ship.max_weapon_range * engage_mult
        if opt_dist < self.MIN_SPACING:
            opt_dist = self.MIN_SPACING  # Minimum spacing
        
        dist = self.controller.ship.position.distance_to(target.position)
        
        if dist > opt_dist:
            # Close in
            self.controller.navigate_to(target.position, stop_dist=opt_dist, precise=True)
        else:
            # Kite - maintain distance
            vec = self.controller.ship.position - target.position
            if vec.length() == 0: 
                vec = pygame.math.Vector2(1, 0)
            
            kite_pos = target.position + vec.normalize() * opt_dist
            self.controller.navigate_to(kite_pos, stop_dist=0, precise=True)

class AttackRunBehavior(AIBehavior):
    DEFAULT_APPROACH_DIST_FACTOR: float = AIConfig.ATTACK_RUN_APPROACH_DIST_FACTOR
    DEFAULT_RETREAT_DIST_FACTOR: float = AIConfig.ATTACK_RUN_RETREAT_DIST_FACTOR
    DEFAULT_RETREAT_DURATION: float = AIConfig.ATTACK_RUN_RETREAT_DURATION
    TICK_DURATION: float = PhysicsConfig.TICK_RATE
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
        approach_dist = self.controller.ship.max_weapon_range * behavior_config.get('approach_distance', self.DEFAULT_APPROACH_DIST_FACTOR)
        retreat_dist = self.controller.ship.max_weapon_range * behavior_config.get('retreat_distance', self.DEFAULT_RETREAT_DIST_FACTOR)
        retreat_duration = behavior_config.get('retreat_duration', self.DEFAULT_RETREAT_DURATION)
        
        dist = self.controller.ship.position.distance_to(target.position)
        
        if self.attack_state == 'approach':
            self.controller.navigate_to(target.position, stop_dist=approach_dist, precise=False)
            
            if dist < approach_dist * self.APPROACH_HYSTERESIS:
                self.attack_state = 'retreat'
                self.attack_timer = retreat_duration
                
        elif self.attack_state == 'retreat':
            # Cycle-Based: 1 tick = 0.01 seconds. Decrement timer by 0.01.
            self.attack_timer -= self.TICK_DURATION
            
            vec = self.controller.ship.position - target.position
            if vec.length() == 0: 
                vec = pygame.math.Vector2(1, 0)
            flee_pos = self.controller.ship.position + vec.normalize() * self.FLEE_DISTANCE
            
            self.controller.navigate_to(flee_pos, stop_dist=0, precise=False)
            
            if self.attack_timer <= 0 and dist > retreat_dist:
                self.attack_state = 'approach'

class FormationBehavior(AIBehavior):
    DRIFT_THRESHOLD_FACTOR: float = AIConfig.FORMATION_DRIFT_THRESHOLD_FACTOR
    DRIFT_THRESHOLD_DIAMETER_MULT: float = AIConfig.FORMATION_DRIFT_DIAMETER_MULT
    TURN_SPEED_FACTOR: float = AIConfig.FORMATION_TURN_SPEED_FACTOR
    TURN_PREDICT_FACTOR: float = AIConfig.FORMATION_TURN_PREDICT_FACTOR
    DEADBAND_ERROR: float = AIConfig.FORMATION_DEADBAND_ERROR
    CORRECTION_FACTOR: float = AIConfig.FORMATION_CORRECTION_FACTOR
    MAX_CORRECTION_FORCE: int = AIConfig.MAX_CORRECTION_FORCE
    PREDICTION_TICKS: int = AIConfig.FORMATION_PREDICTION_TICKS
    TICK_DURATION: float = PhysicsConfig.TICK_RATE
    NAVIGATE_STOP_DIST: int = AIConfig.FORMATION_NAVIGATE_STOP_DIST

    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        ship = self.controller.ship
        master = ship.formation_master
        
        if not master or not master.is_alive or getattr(master, 'is_derelict', False):
            ship.in_formation = False
            return

        # Calculate target position
        if getattr(ship, 'formation_rotation_mode', 'relative') == 'fixed':
             current_rel_offset = ship.formation_offset
        else:
             current_rel_offset = ship.formation_offset.rotate(master.angle)
             
        target_pos = master.position + current_rel_offset
        
        dist = ship.position.distance_to(target_pos)
        diameter = ship.radius * 2
        
        # Match Master's rotation
        angle_diff = (master.angle - ship.angle + 180) % 360 - 180
        
        # Decision: Drift or Turn
        # Use a larger threshold for drift to allow agile ships to snap into position
        # Using acceleration_rate ensures we can cover the gap in one tick if needed
        drift_threshold = max(diameter * self.DRIFT_THRESHOLD_DIAMETER_MULT, ship.acceleration_rate * self.DRIFT_THRESHOLD_FACTOR)
        
        if dist <= drift_threshold:
            # Drift / Fudge Factor Zone
            
            # 1. Rotation: Feed-Forward + Correction
            # Feed-Forward: Match Master's angle exactly if we are already close
            # Correction: Close the gap
            
            turn_speed_per_tick = (ship.turn_speed * getattr(ship, 'turn_throttle', 1.0)) / self.TURN_SPEED_FACTOR
            
            # Snap to master's future angle? 
            # If master is rotating, we should be too (Feed Forward)
            # We don't have explicit 'master.is_turning' flag easily accessible, 
            # but we can infer from master.current_speed/angle change or just match angle.
            
            if abs(angle_diff) < turn_speed_per_tick * self.TURN_PREDICT_FACTOR:
                 ship.angle = master.angle
            else:
                 direction = 1 if angle_diff > 0 else -1
                 ship.rotate(direction)
            
            # 2. Translation Logic
            # Goal: Match Velocity + Correct Position Error
            
            # A) Velocity Sync (Physics Feed-Forward)
            # Match master's target speed setting so Physics updates us by the same amount.
            master_target_speed = 0
            if getattr(master, 'is_thrusting', False):
                 # Calculate what speed the master is trying to reach
                 master_target_speed = getattr(master, 'max_speed', 0) * getattr(master, 'engine_throttle', 1.0)
            
            # Apply to self
            if ship.max_speed > 0:
                 # Calculate required throttle to match master speed
                 req_throttle = master_target_speed / ship.max_speed
                 ship.engine_throttle = min(req_throttle, 1.0)
                 
                 # Activate Engines if needed
                 if req_throttle > 0:
                     ship.thrust_forward() # Consumes fuel, sets is_thrusting=True
                     # Physics will now result in velocity ~= master.velocity
            
            # B) Positional Correction (Drift)
            # Since velocity handles the bulk movement, Drift only needs to correct the current offset error.
            # Prediction Factor = 0.0 (Target current master position)
            
            # Calculate where we SHOULD be right now
            future_master_pos = master.position # No prediction needed if velocity matched
            
            if getattr(ship, 'formation_rotation_mode', 'relative') == 'fixed':
                 future_offset = ship.formation_offset
            else:
                 future_offset = ship.formation_offset.rotate(master.angle)
                 
            future_target_pos = future_master_pos + future_offset
            
            vec_to_spot = future_target_pos - ship.position
            dist_error = vec_to_spot.length()
            
            # DEADBAND & SMOOTHING:
            # - Ignore micro-errors (< 2.0) to prevent jitter/oscillation.
            # - Smooth correction (0.2 factor) to act as a spring rather than a hard snap.
            # - Velocity Sync already handles 99% of the movement.
            
            if dist_error > self.DEADBAND_ERROR:
                 # Spring force: Correct 20% of error per tick
                 # This eliminates bi-stable oscillation while ensuring convergence.
                 correction = vec_to_spot * self.CORRECTION_FACTOR
                 
                 # Cap correction to avoid wild jumps if something goes wrong (e.g. 500px limit)
                 if correction.length() > self.MAX_CORRECTION_FORCE: 
                     correction.scale_to_length(self.MAX_CORRECTION_FORCE)
                 
                 ship.position += correction
                
        else:
            # Out of position > Threshold
            # Navigate to FUTURE spot (Anticipation)
            # Predict where master will be in X ticks based on current speed
            prediction_ticks = self.PREDICTION_TICKS
            predicted_master_pos = master.position + (pygame.math.Vector2(0, -1).rotate(-master.angle) * master.current_speed * prediction_ticks * self.TICK_DURATION)
            # Re-calculate offset based on master's current angle 
            if getattr(ship, 'formation_rotation_mode', 'relative') == 'fixed':
                 pred_offset = ship.formation_offset
            else:
                 pred_offset = ship.formation_offset.rotate(master.angle)
            
            target_pos = predicted_master_pos + pred_offset
            
            self.controller.navigate_to(target_pos, stop_dist=self.NAVIGATE_STOP_DIST, precise=True)


# =============================================================================
# TEST-SPECIFIC BEHAVIORS
# =============================================================================

class DoNothingBehavior(AIBehavior):
    """Ship sits completely still. No movement, no rotation, no firing."""
    
    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        # Explicitly disable firing
        self.controller.ship.comp_trigger_pulled = False
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
    """Random direction changes at random intervals."""
    
    def __init__(self, controller: Any) -> None:
        super().__init__(controller)
        self.direction_timer: float = 0.0
        self.current_direction: int = 1
        self.next_change_interval: float = 1.0
        
    def enter(self) -> None:
        import random
        self.direction_timer = 0.0
        self.current_direction = random.choice([-1, 1])
        self.next_change_interval = random.uniform(
            AIConfig.ERRATIC_TURN_INTERVAL_MIN,
            AIConfig.ERRATIC_TURN_INTERVAL_MAX
        )

    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        import random

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
            self.controller.ship.rotate(self.current_direction)
        
        # Always thrust forward
        self.controller.ship.thrust_forward()


class OrbitBehavior(AIBehavior):
    """Circle target at fixed distance."""

    DEFAULT_ORBIT_DISTANCE: int = AIConfig.DEFAULT_ORBIT_DISTANCE
    
    def update(self, target: Any, strategy: Dict[str, Any]) -> None:
        if not target:
            return
            
        orbit_distance = strategy.get('orbit_distance', self.DEFAULT_ORBIT_DISTANCE)
        
        ship = self.controller.ship
        vec_to_target = target.position - ship.position
        dist = vec_to_target.length()
        
        if dist == 0:
            return
        
        # Calculate tangent direction (perpendicular to radial vector)
        # Rotate 90 degrees for counter-clockwise orbit
        radial = vec_to_target.normalize()
        tangent = pygame.math.Vector2(-radial.y, radial.x)
        
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
        target_pos = ship.position + move_dir * AIConfig.ORBIT_TARGET_OFFSET
        self.controller.navigate_to(target_pos, stop_dist=0, precise=False)

