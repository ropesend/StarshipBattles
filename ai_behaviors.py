
import pygame
import math

class AIBehavior:
    def __init__(self, controller):
        self.controller = controller
        
    def enter(self):
        """Called when this behavior becomes active."""
        pass
        
    def update(self, target, strategy):
        """Execute behavior logic."""
        raise NotImplementedError

class RamBehavior(AIBehavior):
    def update(self, target, strategy):
        # Ram target, no avoidance
        self.controller.navigate_to(target.position, stop_dist=0, precise=False)

class FleeBehavior(AIBehavior):
    def update(self, target, strategy):
        # Run away from target
        fire_while_retreating = strategy.get('fire_while_retreating', False)
        # Note: controller.update sets trigger to True by default, we modify it here if needed
        self.controller.ship.comp_trigger_pulled = fire_while_retreating
        
        vec = self.controller.ship.position - target.position
        if vec.length() == 0: 
            vec = pygame.math.Vector2(1, 0)
        
        flee_pos = self.controller.ship.position + vec.normalize() * 1000
        self.controller.navigate_to(flee_pos, stop_dist=0, precise=False)

class KiteBehavior(AIBehavior):
    def update(self, target, strategy):
        # Collision avoidance if enabled
        if strategy.get('avoid_collisions', True):
            override_pos = self.controller.check_avoidance()
            if override_pos:
                self.controller.navigate_to(override_pos, stop_dist=0, precise=False)
                return
        
        # Get engage distance multiplier logic
        # We need access to ENGAGE_DISTANCES from ai.py or passed in. 
        # Easier to have controller resolve it or pass it. 
        # Let's assume controller provides a helper or we access it via import (circular import risk).
        # Better: Controller logic calculates engage_mult before calling (or we duplicate logic/import).
        # Let's import the specific dict if possible or pass it.
        # Actually, let's ask the controller for the multiplier.
        
        engage_mult = self.controller.get_engage_distance_multiplier(strategy)
        
        # Calculate optimal distance
        opt_dist = self.controller.ship.max_weapon_range * engage_mult
        if opt_dist < 150:
            opt_dist = 150  # Minimum spacing
        
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
    def __init__(self, controller):
        super().__init__(controller)
        self.attack_state = 'approach'
        self.attack_timer = 0
        
    def enter(self):
        # Reset state when switching to this behavior
        self.attack_state = 'approach'
        self.attack_timer = 0

    def update(self, target, strategy):
        behavior_config = strategy.get('attack_run_behavior', {})
        approach_dist = self.controller.ship.max_weapon_range * behavior_config.get('approach_distance', 0.3)
        retreat_dist = self.controller.ship.max_weapon_range * behavior_config.get('retreat_distance', 0.8)
        retreat_duration = behavior_config.get('retreat_duration', 2.0)
        
        dist = self.controller.ship.position.distance_to(target.position)
        
        if self.attack_state == 'approach':
            self.controller.navigate_to(target.position, stop_dist=approach_dist, precise=False)
            
            if dist < approach_dist * 1.5:
                self.attack_state = 'retreat'
                self.attack_timer = retreat_duration
                
        elif self.attack_state == 'retreat':
            # Cycle-Based: 1 tick = 0.01 seconds. Decrement timer by 0.01.
            self.attack_timer -= 0.01
            
            vec = self.controller.ship.position - target.position
            if vec.length() == 0: 
                vec = pygame.math.Vector2(1, 0)
            flee_pos = self.controller.ship.position + vec.normalize() * 1000
            
            self.controller.navigate_to(flee_pos, stop_dist=0, precise=False)
            
            if self.attack_timer <= 0 and dist > retreat_dist:
                self.attack_state = 'approach'

class FormationBehavior(AIBehavior):
    def update(self, target, strategy):
        ship = self.controller.ship
        master = ship.formation_master
        
        if not master or not master.is_alive or getattr(master, 'is_derelict', False):
            ship.in_formation = False
            return

        # Calculate target position
        rotated_offset = ship.formation_offset.rotate(master.angle)
        target_pos = master.position + rotated_offset
        
        dist = ship.position.distance_to(target_pos)
        diameter = ship.radius * 2
        
        # Match Master's rotation
        angle_diff = (master.angle - ship.angle + 180) % 360 - 180
        
        # Decision: Drift or Turn
        # Use a larger threshold for drift to allow agile ships to snap into position
        # Using acceleration_rate ensures we can cover the gap in one tick if needed
        drift_threshold = max(diameter * 2, ship.acceleration_rate * 1.2)
        
        if dist <= drift_threshold:
            # Drift / Fudge Factor Zone
            
            # 1. Rotation: Feed-Forward + Correction
            # Feed-Forward: Match Master's angle exactly if we are already close
            # Correction: Close the gap
            
            turn_speed_per_tick = (ship.turn_speed * getattr(ship, 'turn_throttle', 1.0)) / 100.0
            
            # Snap to master's future angle? 
            # If master is rotating, we should be too (Feed Forward)
            # We don't have explicit 'master.is_turning' flag easily accessible, 
            # but we can infer from master.current_speed/angle change or just match angle.
            
            if abs(angle_diff) < turn_speed_per_tick * 1.5:
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
            future_target_pos = future_master_pos + ship.formation_offset.rotate(master.angle)
            
            vec_to_spot = future_target_pos - ship.position
            dist_error = vec_to_spot.length()
            
            # DEADBAND & SMOOTHING:
            # - Ignore micro-errors (< 2.0) to prevent jitter/oscillation.
            # - Smooth correction (0.2 factor) to act as a spring rather than a hard snap.
            # - Velocity Sync already handles 99% of the movement.
            
            if dist_error > 2.0:
                 # Spring force: Correct 20% of error per tick
                 # This eliminates bi-stable oscillation while ensuring convergence.
                 correction = vec_to_spot * 0.2
                 
                 # Cap correction to avoid wild jumps if something goes wrong (e.g. 500px limit)
                 if correction.length() > 500: 
                     correction.scale_to_length(500)
                 
                 ship.position += correction
                
        else:
            # Out of position > Threshold
            # Navigate to FUTURE spot (Anticipation)
            # Predict where master will be in X ticks based on current speed
            prediction_ticks = 10
            predicted_master_pos = master.position + (pygame.math.Vector2(0, -1).rotate(-master.angle) * master.current_speed * prediction_ticks * 0.01)
            # Re-calculate offset based on master's current angle (assuming constant bearing for short duration)
            target_pos = predicted_master_pos + rotated_offset
            
            self.controller.navigate_to(target_pos, stop_dist=10, precise=True)
