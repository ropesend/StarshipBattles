import math
import pygame
from components import LayerType

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
            
        # Collision Avoidance / Ramming Logic
        closest_threat = None
        current_min_dist = float('inf') # Track actual closest for decision
        
        # Dynamic check
        nearby = self.grid.query_radius(self.ship.position, 2000) # Query broad, filter narrow
        
        for obj in nearby:
            if obj == self.ship: continue
            if not obj.is_alive: continue
            if not hasattr(obj, 'team_id'): continue
            
            d = self.ship.position.distance_to(obj.position)
            
            # Calculate dynamic threshold
            # 1. Physical collision safety margin
            obj_radius = getattr(obj, 'radius', 40)
            physical_safe = self.ship.radius + obj_radius + 50
            
            # 2. Tactical range (stay further back)
            tactical_safe = self.ship.max_weapon_range * 0.9
            
            avoid_threshold = max(physical_safe, tactical_safe)
            
            if d < avoid_threshold:
                 # Check if this is the closest/most urgent threat relative to its own threshold?
                 # Or just closest absolute?
                 # Let's track the one that violates its threshold the most or is just closest absolute distance.
                 if d < current_min_dist:
                     closest_threat = obj
                     current_min_dist = d
                     # We break if we only care about ONE, but we should probably scan all to find the worst.
                     # But for simplicity, closest absolute that is within threshold is fine.
        
        override_target_pos = None
        
        if closest_threat:
            # Decision Time
            is_enemy = (closest_threat.team_id != self.ship.team_id)
            
            should_ram = False
            if is_enemy:
                # Check Overwhelming Favor (e.g. 2x HP)
                # Ensure we have HP data
                my_hp = self.ship.hp
                their_hp = closest_threat.hp
                if my_hp > their_hp * 2.0:
                    should_ram = True
            
            if should_ram:
                # Steer TOWARDS threat (RAM)
                override_target_pos = closest_threat.position
            else:
                # Steer AWAY from threat
                # Vector from threat to me
                flee_vec = self.ship.position - closest_threat.position
                if flee_vec.length() == 0: flee_vec = pygame.math.Vector2(1,0)
                # Target a point away
                override_target_pos = self.ship.position + flee_vec.normalize() * 1000

        # Determine navigation target
        nav_target_pos = override_target_pos if override_target_pos else target.position

        distance = self.ship.position.distance_to(nav_target_pos)
        
        # 1. Navigation
        # Calculate angle to target
        dx = nav_target_pos.x - self.ship.position.x
        dy = nav_target_pos.y - self.ship.position.y
        
        target_angle = math.degrees(math.atan2(dy, dx)) % 360
        current_angle = self.ship.angle % 360
        
        # Calculate difference (-180 to 180)
        angle_diff = (target_angle - current_angle + 180) % 360 - 180
        
        # Rotate
        if abs(angle_diff) > 5:
            direction = 1 if angle_diff > 0 else -1
            self.ship.rotate(dt, direction)
        
        # Thrust
        # Calculate dynamic stopping distance to prevent overshooting into collision
        # Stop thrusting if within 80% of weapon range (if we have weapons)
        # Otherwise default to 300
        stop_dist = max(300, self.ship.max_weapon_range * 0.8)
        
        if abs(angle_diff) < 20 and distance > stop_dist: 
            if abs(angle_diff) < 5:
                self.ship.thrust_forward(dt)

        # 2. Combat
        in_sights = abs(angle_diff) < 10
        
        if in_sights:
            self.ship.comp_trigger_pulled = True
        else:
            self.ship.comp_trigger_pulled = False

    # attempt_fire removed, logic moved to Ship update via trigger

