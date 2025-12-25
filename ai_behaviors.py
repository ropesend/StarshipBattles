
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
        if dist <= diameter:
            # Drift / Fudge Factor Zone
            
            # 1. Rotation: Try to match master's heading
            if abs(angle_diff) > 0.5:
                direction = 1 if angle_diff > 0 else -1
                ship.rotate(direction)
            
            # 2. Translation: Drift
            drift_amount = ship.acceleration_rate
            vec_to_spot = target_pos - ship.position
            
            if vec_to_spot.length() > 0:
                if vec_to_spot.length() > drift_amount:
                    vec_to_spot.scale_to_length(drift_amount)
                
                # Apply position change (Drift)
                ship.position += vec_to_spot
                
                # Maintain Master's speed
                ship.target_speed = master.current_speed
                
        else:
            # Out of position > 1 Diameter
            # Navigate to spot (Turn and Burn)
            self.controller.navigate_to(target_pos, stop_dist=10, precise=True)
