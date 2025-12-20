import math
import pygame
from components import LayerType
from logger import log_info

class AIController:
    def __init__(self, ship, grid, enemy_team_id):
        self.ship = ship
        self.grid = grid
        self.enemy_team_id = enemy_team_id
        
    def find_target(self):
        # Efficiently find nearest enemy using grid?
        # For now, simplistic: query large radius or just iterate all known if passed?
        # The prompt implies using the grid for targeting.
        # Let's query a large radius (e.g., 200000) around the ship to find candidates.
        candidates = self.grid.query_radius(self.ship.position, 200000)
        
        nearest = None
        min_dist = float('inf')
        
        for obj in candidates:
            if not obj.is_alive: continue
            if not hasattr(obj, 'team_id'): continue # Ignore non-ships
            if obj.team_id != self.enemy_team_id: continue
            
            d = self.ship.position.distance_to(obj.position)
            if d < min_dist:
                min_dist = d
                nearest = obj
                
        return nearest

    def update(self, dt):
        if not self.ship.is_alive: return

        # Target Acquisition
        target = self.ship.current_target
        if not target or not target.is_alive:
            target = self.find_target()
            self.ship.current_target = target
            
        if not target:
            # Idle / Drift
            self.ship.comp_trigger_pulled = False
            return
        
        # Dispatch Strategy
        strategy = getattr(self.ship, 'ai_strategy', 'max_range')
        
        if strategy == 'kamikaze':
            self.update_kamikaze(dt, target)
        elif strategy == 'attack_run':
            self.update_attack_run(dt, target)
        elif strategy == 'flee':
            self.update_flee(dt, target)
        else:
            self.update_max_range(dt, target)

    def update_kamikaze(self, dt, target):
        # KAMIKAZE: Ram target, no avoidance
        self.ship.comp_trigger_pulled = True
        self.navigate_to(dt, target.position, stop_dist=0, precise=False)
        
    def update_flee(self, dt, target):
        # FLEE: Run away from target
        self.ship.comp_trigger_pulled = False # Don't fire while fleeing?
        
        vec = self.ship.position - target.position
        if vec.length() == 0: vec = pygame.math.Vector2(1,0)
        
        flee_pos = self.ship.position + vec.normalize() * 1000
        self.navigate_to(dt, flee_pos, stop_dist=0, precise=False)

    def update_attack_run(self, dt, target):
        # ATTACK RUN: Approach -> Turn -> Retreat -> Turn
        # Need state. Initialize if missing.
        if not hasattr(self, 'attack_state'):
            self.attack_state = 'approach' 
            self.attack_timer = 0
            
        dist = self.ship.position.distance_to(target.position)
        
        if self.attack_state == 'approach':
            self.ship.comp_trigger_pulled = True
            # Fly to near point blank (e.g. 150)
            target_pos = target.position
            
            # Avoid direct collision if not kamikaze? 
            # Offset slightly to pass by?
            # For now, just aim at it, collision avoidance usually handles the specific hit.
            # But let's try to do a "pass"
            
            self.navigate_to(dt, target_pos, stop_dist=100, precise=False)
            
            if dist < 200:
                self.attack_state = 'retreat'
                self.attack_timer = 2.0 # Run away for 2 seconds
                
        elif self.attack_state == 'retreat':
            self.ship.comp_trigger_pulled = False
            self.attack_timer -= dt
            
            # Fly away
            vec = self.ship.position - target.position
            if vec.length() == 0: vec = pygame.math.Vector2(1,0)
            flee_pos = self.ship.position + vec.normalize() * 1000
            
            self.navigate_to(dt, flee_pos, stop_dist=0, precise=False)
            
            if self.attack_timer <= 0 and dist > self.ship.max_weapon_range * 0.8:
                self.attack_state = 'approach'

    def update_max_range(self, dt, target):
        # MAX RANGE (Kiting) - Original behavior + Coll Avoidance
        self.ship.comp_trigger_pulled = True
        
        # Collision Avoidance (Only for subtle/smart strategies)
        override_pos = self.check_avoidance()
        if override_pos:
            self.navigate_to(dt, override_pos, stop_dist=0, precise=False)
            return

        # Optimal Distance
        opt_dist = self.ship.max_weapon_range * 0.9
        if opt_dist < 200: opt_dist = 200 # Minimum spacing
        
        dist = self.ship.position.distance_to(target.position)
        
        if dist > opt_dist:
            # Close in
            self.navigate_to(dt, target.position, stop_dist=opt_dist, precise=True)
        else:
            # Too close, back off or circle?
            # Back off logic similar to flee but keeping facing?
            # Simple kiting: just stop thrusting if too close, maybe reverse?
            # If we just stop, we drift.
            # Let's try to maintain distance.
            vec = self.ship.position - target.position
            if vec.length() == 0: vec = pygame.math.Vector2(1,0)
            
            # Kite point
            kite_pos = target.position + vec.normalize() * opt_dist
            self.navigate_to(dt, kite_pos, stop_dist=0, precise=True)

    def check_avoidance(self):
        # Extracted Collision Logic
        nearby = self.grid.query_radius(self.ship.position, 1000)
        closest = None
        min_d = float('inf')
        
        for obj in nearby:
            if obj == self.ship: continue
            if not obj.is_alive: continue
            if not hasattr(obj, 'team_id'): continue
            
            # Simple physical radius check
            d = self.ship.position.distance_to(obj.position)
            thresh = self.ship.radius + getattr(obj, 'radius', 40) + 100
            
            if d < thresh:
                if d < min_d:
                    min_d = d
                    closest = obj
        
        if closest:
            # Evade
            vec = self.ship.position - closest.position
            if vec.length() == 0: vec = pygame.math.Vector2(1,0)
            return self.ship.position + vec.normalize() * 500
        return None

    def navigate_to(self, dt, target_pos, stop_dist=0, precise=False):
        # 1. Navigation
        distance = self.ship.position.distance_to(target_pos)
        
        dx = target_pos.x - self.ship.position.x
        dy = target_pos.y - self.ship.position.y
        
        target_angle = math.degrees(math.atan2(dy, dx)) % 360
        current_angle = self.ship.angle % 360
        
        angle_diff = (target_angle - current_angle + 180) % 360 - 180
        
        # Rotate
        if abs(angle_diff) > 5:
            direction = 1 if angle_diff > 0 else -1
            self.ship.rotate(dt, direction)
        
        # Thrust
        # If precise, we slow down earlier
        eff_stop_dist = stop_dist
        
        if abs(angle_diff) < 30 and distance > eff_stop_dist:
            # Throttle if facing roughly right
             self.ship.thrust_forward(dt)

    # attempt_fire removed, logic moved to Ship update via trigger

