
import pygame
import os
import math
import sys

# Setup paths (assuming running from root)
sys.path.append(os.getcwd())

from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.entities.ship import Ship, initialize_ship_data
from game.simulation.components.component import load_components, load_modifiers
from game.ai.controller import AIController
import json

def setup_simulation():
    # Initialize Data
    pygame.init() # Needed for vectors
    base_path = os.getcwd()
    initialize_ship_data(base_path)
    load_components(os.path.join(base_path, "data", "components.json"))
    load_modifiers(os.path.join(base_path, "data", "modifiers.json"))
    
    # Load Designs
    with open("ships/Fighting Falcon.json", "r") as f:
        design_data = json.load(f)
        
    with open("X Formation.json", "r") as f:
        form_data = json.load(f)
        
    # Create Ships
    ships = []
    arrows = form_data['arrows']
    
    # Center of formation logic
    min_x = min(p[0] for p in arrows)
    max_x = max(p[0] for p in arrows)
    min_y = min(p[1] for p in arrows)
    max_y = max(p[1] for p in arrows)
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    
    # Scale
    temp_ship = Ship.from_dict(design_data)
    temp_ship.recalculate_stats()
    diameter = temp_ship.radius * 2
    GRID_UNIT = 50.0
    
    start_pos = pygame.math.Vector2(0, 0)
    master = None
    
    for i, (ax, ay) in enumerate(arrows):
        dx = ax - center_x
        dy = ay - center_y
        world_x = (dx / GRID_UNIT) * diameter
        world_y = (dy / GRID_UNIT) * diameter
        
        s = Ship.from_dict(design_data)
        s.position = pygame.math.Vector2(start_pos.x + world_x, start_pos.y + world_y)
        s.team_id = 0
        s.recalculate_stats()
        
        # Link Formation
        if i == 0:
            master = s
            s.name = f"Master"
            s.formation_members = []
        else:
            s.name = f"Wing-{i}"
            s.formation_master = master
            master.formation_members.append(s)
            
            # Global - Master
            diff = s.position - master.position
            # Rotate into Master's frame (Master is angle 0 initially)
            s.formation_offset = diff # Already aligned since master angle is 0
            
        ships.append(s)
        
    # Add Dummy Enemy to prevent battle end
    dummy = Ship.from_dict(design_data)
    dummy.position = pygame.math.Vector2(200000, 200000)
    dummy.team_id = 1
    ships.append(dummy)
        
    return ships, master

class CheckpointBehavior:
    def __init__(self, ship, checkpoints):
        self.ship = ship
        self.checkpoints = checkpoints
        self.current_idx = 0
        
    def update(self):
        if self.current_idx >= len(self.checkpoints):
            self.ship.target_speed = 0
            return
            
        target = self.checkpoints[self.current_idx]
        dist = self.ship.position.distance_to(target)
        
        if dist < 500:
            self.current_idx += 1
            print(f"Reached checkpoint {self.current_idx}")
            return
            
        # Navigation
        dx = target.x - self.ship.position.x
        dy = target.y - self.ship.position.y
        target_angle = math.degrees(math.atan2(dy, dx)) % 360
        current = self.ship.angle % 360
        diff = (target_angle - current + 180) % 360 - 180
        
        # Simple Rotate
        turn_acc = (self.ship.turn_speed * getattr(self.ship, 'turn_throttle', 1.0)) / 100.0
        if abs(diff) > turn_acc:
             direction = 1 if diff > 0 else -1
             self.ship.angle += direction * turn_acc
        else:
             self.ship.angle = target_angle
             
        # Simple Thrust
        self.ship.thrust_forward()

def run_test():
    ships, master = setup_simulation()
    
    engine = BattleEngine()
    engine.ships = ships
    
    # Custom AI for Followers AND Master (for formation logic)
    engine.ai_controllers = []
    
    # Master AI (for formation throttle logic)
    master_ai = AIController(master, engine.grid, 1)
    engine.ai_controllers.append(master_ai)
    
    for s in ships:
        if s != master:
            ctrl = AIController(s, engine.grid, 1)
            engine.ai_controllers.append(ctrl)
            
    checkpoints = [
        pygame.math.Vector2(0, 10000),      # Straight
        pygame.math.Vector2(10000, 10000),  # Hard Right
        pygame.math.Vector2(10000, 0),      # Hard Right
        pygame.math.Vector2(0, 0)           # Home
    ]
    
    behavior = CheckpointBehavior(master, checkpoints)
    
    print(f"Starting Simulation with {len(ships)} ships.")
    print(f"Master Max Speed: {master.max_speed}")
    print(f"Master Turn Speed Raw: {master.turn_speed}")
    print(f"Master Fuel: {master.current_fuel}/{master.max_fuel}")

    max_dev_global = 0
    
    for tick in range(3000):
        # Update Master AI manually for steering
        behavior.update()
        
        # Update Engine (Physics + AI for followers + Master formation logic)
        engine.update()
        
        # Measure Deviation
        devs = []
        for s in master.formation_members:
            if not s.in_formation: 
                devs.append(9999) # Dropped out
                continue
                
            rotated_offset = s.formation_offset.rotate(master.angle)
            ideal_pos = master.position + rotated_offset
            dist = s.position.distance_to(ideal_pos)
            devs.append(dist)
            
        current_max_dev = max(devs) if devs else 0
        max_dev_global = max(max_dev_global, current_max_dev)
        
        if tick % 100 == 0:
            print(f"Tick {tick}: Master Pos {master.position}, Spd {master.current_speed:.1f}, Max Dev: {current_max_dev:.1f}")

    print(f"Test Complete. All-Time Max Deviation: {max_dev_global:.1f}")

if __name__ == "__main__":
    run_test()
