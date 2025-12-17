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
        # Let's query a large radius (e.g., 50000) around the ship to find candidates.
        candidates = self.grid.query_radius(self.ship.position, 50000)
        
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

        distance = self.ship.position.distance_to(target.position)
        
        # 1. Navigation
        # Calculate angle to enemy
        dx = target.position.x - self.ship.position.x
        dy = target.position.y - self.ship.position.y
        
        target_angle = math.degrees(math.atan2(dy, dx)) % 360
        current_angle = self.ship.angle % 360
        
        # Calculate difference (-180 to 180)
        angle_diff = (target_angle - current_angle + 180) % 360 - 180
        
        # Rotate
        if abs(angle_diff) > 5:
            direction = 1 if angle_diff > 0 else -1
            self.ship.rotate(dt, direction)
        
        # Thrust
        if abs(angle_diff) < 20 and distance > 300: 
            if abs(angle_diff) < 5:
                self.ship.thrust_forward(dt)

        # 2. Combat
        in_sights = abs(angle_diff) < 10
        
        if in_sights:
            self.ship.comp_trigger_pulled = True
        else:
            self.ship.comp_trigger_pulled = False

    # attempt_fire removed, logic moved to Ship update via trigger

