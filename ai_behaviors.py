
import pygame
import math
from typing import Any, Dict

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
    FLEE_DISTANCE: int = 1000
    
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
    MIN_SPACING: int = 150
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
    DEFAULT_APPROACH_DIST_FACTOR: float = 0.3
    DEFAULT_RETREAT_DIST_FACTOR: float = 0.8
    DEFAULT_RETREAT_DURATION: float = 2.0
    TICK_DURATION: float = 0.01
    FLEE_DISTANCE: int = 1000
    APPROACH_HYSTERESIS: float = 1.5

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
    DRIFT_THRESHOLD_FACTOR: float = 1.2
    DRIFT_THRESHOLD_DIAMETER_MULT: float = 2.0
    TURN_SPEED_FACTOR: float = 100.0
    TURN_PREDICT_FACTOR: float = 1.5
    DEADBAND_ERROR: float = 2.0
    CORRECTION_FACTOR: float = 0.2
    MAX_CORRECTION_FORCE: int = 500
    PREDICTION_TICKS: int = 10
    TICK_DURATION: float = 0.01
    NAVIGATE_STOP_DIST: int = 10

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
