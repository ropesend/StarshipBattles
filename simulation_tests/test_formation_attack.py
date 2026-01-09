
import pygame
import os
import math
import sys
import json

# Setup paths (assuming running from root)
sys.path.append(os.getcwd())

from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.entities.ship import Ship, initialize_ship_data
from game.simulation.components.component import load_components, load_modifiers
from game.ai.controller import AIController
from game.ai.behaviors import AttackRunBehavior

def setup_simulation():
    # Initialize Data
    pygame.init()
    base_path = os.getcwd()
    initialize_ship_data(base_path)
    load_components(os.path.join(base_path, "data", "components.json"))
    load_modifiers(os.path.join(base_path, "data", "modifiers.json"))
    
    # Load Designs
    with open("ships/Fighting Falcon.json", "r") as f:
        design_data = json.load(f)
        
    # X Formation
    with open("X Formation.json", "r") as f:
        form_data = json.load(f)
        
    ships = []
    arrows = form_data['arrows']
    
    # Scale
    temp_ship = Ship.from_dict(design_data)
    temp_ship.recalculate_stats()
    diameter = temp_ship.radius * 2
    GRID_UNIT = 50.0
    
    # Start far enough away to trigger approach
    start_pos = pygame.math.Vector2(0, 10000) 
    master = None
    
    # Center Logic
    min_x = min(p[0] for p in arrows)
    max_x = max(p[0] for p in arrows)
    min_y = min(p[1] for p in arrows)
    max_y = max(p[1] for p in arrows)
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    
    for i, (ax, ay) in enumerate(arrows):
        dx = ax - center_x
        dy = ay - center_y
        world_x = (dx / GRID_UNIT) * diameter
        world_y = (dy / GRID_UNIT) * diameter
        
        s = Ship.from_dict(design_data)
        s.position = pygame.math.Vector2(start_pos.x + world_x, start_pos.y + world_y)
        s.team_id = 0
        s.recalculate_stats()
        
        if i == 0:
            master = s
            s.name = "Master"
            s.formation_members = []
            s.ai_strategy = 'attack_run' # Force strategy
        else:
            s.name = f"Wing-{i}"
            s.formation_master = master
            master.formation_members.append(s)
            diff = s.position - master.position
            s.formation_offset = diff
            
        ships.append(s)
        
    return ships, master

def run_test():
    ships, master = setup_simulation()
    
    # Create Dummy Target: Well Armored (High HP), Stationary, Unarmed (No Weapons)
    # Just reuse design but buff HP and set team 1
    target = Ship.from_dict(ships[0].to_dict()) # Clone
    target.name = "Target Dummy"
    target.team_id = 1
    # Trick: Modify components or bypass property if possible, or just set current hp high and let it be capped?
    # Actually Ship.max_hp is a property derived from components.
    # To make a dummy target tough, let's give it a cheat modifier or just ignore it.
    # Simpler: Just override the property via private attribute if Python allows, or add a cheat component.
    # For now, let's just let it regenerate or have massive armor.
    # Better yet, let's just leave it default but set team ID. 
    # If it dies, the test ends? No, loop runs for 10000 ticks.
    # The error is because I tried to set a property.
    # Let's just create a dummy "Station" class or similar? 
    # Or just don't set max_hp manually.
    # Let's set it to derelict=False explicitly and ensure it has components.
    pass
    target.position = pygame.math.Vector2(0, -10000) # 20k distance
    target.max_speed = 0 # Stationary
    ships.append(target)
    
    engine = BattleEngine()
    engine.ships = ships
    
    # Setup AI
    engine.ai_controllers = []
    
    # Master AI
    master_ai = AIController(master, engine.grid, 1)
    engine.ai_controllers.append(master_ai)
    
    # Follower AI
    for s in ships:
        if s != master and s != target:
            ctrl = AIController(s, engine.grid, 1)
            engine.ai_controllers.append(ctrl)
            
    # Target AI (Passive)
    target_ai = AIController(target, engine.grid, 0)
    engine.ai_controllers.append(target_ai)
    
    print(f"Starting Attack Run Test with {len(ships)} ships.")
    
    max_dev_global = 0
    phase = "unknown"
    
    for tick in range(10000): # Long enough for run
        # Cheat: Keep target alive manually
        for val in target.layers.values():
            for comp in val['components']:
                if hasattr(comp, 'current_hp'):
                    comp.current_hp = comp.max_hp
        
        engine.update()
        
        # Check Master Phase
        if master_ai.current_behavior and isinstance(master_ai.current_behavior, AttackRunBehavior):
            new_phase = master_ai.current_behavior.attack_state
            if new_phase != phase:
                phase = new_phase
                print(f"Tick {tick}: Master entered phase '{phase}'")
        
        # Measure Deviation
        devs = []
        for s in master.formation_members:
            if not s.in_formation: 
                 # print(f"Ship {s.name} dropped formation!")
                 continue
            rotated_offset = s.formation_offset.rotate(master.angle)
            ideal_pos = master.position + rotated_offset
            dist = s.position.distance_to(ideal_pos)
            devs.append(dist)
            
        current_max_dev = max(devs) if devs else 0
        max_dev_global = max(max_dev_global, current_max_dev)
        
        if tick % 500 == 0:
             print(f"Tick {tick}: Phase {phase}, Dev {current_max_dev:.1f}, Master Pos {master.position.y:.0f}")
             
        if phase == 'retreat' and tick % 10 == 0:
             print(f"RETREAT TICK {tick}: Dev {current_max_dev:.1f} MasterAng {master.angle:.1f}")

    print(f"Test Complete. Max Deviation: {max_dev_global:.1f}")

if __name__ == "__main__":
    run_test()
