"""
Strategy Tournament Simulation for Starship Battles.
Runs all combat strategies vs all combat strategies with 5v5 escort ships.
Logs results to CSV for analysis.
"""
import os
import json
import csv
import time
import random
import math
from datetime import datetime
from itertools import product

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Minimal pygame init (headless)
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((800, 600))

from game.simulation.entities.ship import Ship, LayerType
from game.ai.controller import AIController, StrategyManager
from game.engine.spatial import SpatialGrid
from game.simulation.components.component import load_components, load_modifiers
from game.core.registry import RegistryManager
from game.core.constants import AttackType

# Configuration
SHIPS_PER_TEAM = 5
TIME_LIMIT_MINUTES = 5
TIME_LIMIT_SECONDS = TIME_LIMIT_MINUTES * 60
TICK_RATE = 60  # FPS
MAX_TICKS = TIME_LIMIT_SECONDS * TICK_RATE

def load_ship_from_json(filepath, x, y, team_id, strategy):
    """Load a ship from JSON and configure it for battle."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    ship = Ship.from_dict(data)
    ship.position = pygame.math.Vector2(x, y)
    ship.team_id = team_id
    ship.ai_strategy = strategy
    ship.recalculate_stats()
    return ship

def run_battle(strategy_a, strategy_b, ship_json_path, seed=None):
    """
    Run a single battle between two strategies.
    Returns: (winner, team_a_survivors, team_b_survivors, ticks_elapsed, timeout)
    """
    if seed is not None:
        random.seed(seed)
    
    ships = []
    ai_controllers = []
    grid = SpatialGrid(cell_size=2000)
    
    # Team A (left side)
    for i in range(SHIPS_PER_TEAM):
        s = load_ship_from_json(
            ship_json_path,
            500 + random.randint(-200, 200),
            i * 400 + 200 + random.randint(-50, 50),
            team_id=0,
            strategy=strategy_a
        )
        s.angle = 0  # Face right
        ships.append(s)
        ai_controllers.append(AIController(s, grid, enemy_team_id=1))
    
    # Team B (right side)
    for i in range(SHIPS_PER_TEAM):
        s = load_ship_from_json(
            ship_json_path,
            2500 + random.randint(-200, 200),
            i * 400 + 200 + random.randint(-50, 50),
            team_id=1,
            strategy=strategy_b
        )
        s.angle = 180  # Face left
        ships.append(s)
        ai_controllers.append(AIController(s, grid, enemy_team_id=0))
    
    projectiles = []
    dt = 1.0  # Tick-based physics (time-independent)
    
    for tick in range(MAX_TICKS):
        # Update spatial grid
        grid.clear()
        alive_ships = [s for s in ships if s.is_alive]
        for s in alive_ships:
            grid.insert(s)
        
        # Count survivors
        team_a_alive = sum(1 for s in ships if s.is_alive and s.team_id == 0)
        team_b_alive = sum(1 for s in ships if s.is_alive and s.team_id == 1)
        
        # Check for victory
        if team_a_alive == 0:
            return ('B', 0, team_b_alive, tick, False)
        if team_b_alive == 0:
            return ('A', team_a_alive, 0, tick, False)
        
        # Update AI
        for ai in ai_controllers:
            if ai.ship.is_alive:
                ai.update()
        
        # Update ships
        for s in ships:
            s.update(dt)
        
        # Collect and process projectiles
        for s in alive_ships:
            if hasattr(s, 'just_fired_projectiles') and s.just_fired_projectiles:
                for attack in list(s.just_fired_projectiles):
                    # Handle both dict and object (Projectile)
                    is_dict = isinstance(attack, dict)
                    a_type = attack.get('type') if is_dict else getattr(attack, 'type', None)
                    
                    if a_type in [AttackType.PROJECTILE, 'projectile', AttackType.MISSILE, 'missile']:
                        # Convert to local simplified projectile dict for this script's processing
                        p_pos = attack.get('position') if is_dict else getattr(attack, 'position')
                        p_vel = attack.get('velocity') if is_dict else getattr(attack, 'velocity')
                        p_dmg = attack.get('damage') if is_dict else getattr(attack, 'damage')
                        p_rng = attack.get('range') if is_dict else getattr(attack, 'max_range', 1000)
                        p_source = attack.get('source') if is_dict else getattr(attack, 'owner')
                        
                        projectiles.append({
                            'pos': p_pos.copy(),
                            'vel': p_vel.copy(),
                            'damage': p_dmg,
                            'range': p_rng,
                            'distance_traveled': 0,
                            'owner': p_source,
                            'radius': 3
                        })
                        s.just_fired_projectiles.remove(attack)
                    
                    elif a_type in [AttackType.BEAM, 'beam']:
                        # Handle Beam in dict format
                        start_pos = attack['origin']
                        direction = attack['direction']
                        max_range = attack['range']
                        target = attack.get('target')
                        
                        if target and target.is_alive:
                            # Raycast
                            f = start_pos - target.position
                            a = direction.dot(direction)
                            b = 2 * f.dot(direction)
                            c = f.dot(f) - target.radius**2
                            
                            discriminant = b*b - 4*a*c
                            if discriminant >= 0:
                                t1 = (-b - math.sqrt(discriminant)) / (2*a)
                                t2 = (-b + math.sqrt(discriminant)) / (2*a)
                                valid_t = [t for t in [t1, t2] if 0 <= t <= max_range]
                                if valid_t:
                                    # Hit chance based on component
                                    hit_dist = min(valid_t)
                                    beam_comp = attack['component']
                                    chance = beam_comp.calculate_hit_chance(hit_dist)
                                    if random.random() < chance:
                                        target.take_damage(attack['damage'])
                        
                        s.just_fired_projectiles.remove(attack)
        
        # ... Rest of processing (collisions, etc.)
        # Update projectiles with CCD
        projectiles_to_remove = set()
        for idx, p in enumerate(projectiles):
            p_pos_t0 = p['pos']
            p_pos_t1 = p_pos_t0 + p['vel'] * dt
            
            # Simple broad-phase/CCD check
            query_pos = (p_pos_t0 + p_pos_t1) * 0.5
            query_radius = p['vel'].length() * dt + 100
            nearby_ships = grid.query_radius(query_pos, query_radius)
            
            hit_occurred = False
            for target_ship in nearby_ships:
                if not target_ship.is_alive or target_ship.team_id == p['owner'].team_id: continue
                
                # Simplified point-segment distance for CCD
                D = p['vel'] * dt
                if D.length_squared() == 0:
                    dist = p_pos_t0.distance_to(target_ship.position)
                else:
                    t = max(0, min(1, (target_ship.position - p_pos_t0).dot(D) / D.length_squared()))
                    closest = p_pos_t0 + D * t
                    dist = closest.distance_to(target_ship.position)
                
                if dist < target_ship.radius + 5:
                    target_ship.take_damage(p['damage'])
                    hit_occurred = True
                    break
            
            if hit_occurred:
                projectiles_to_remove.add(idx)
            else:
                p['pos'] = p_pos_t1
                p['distance_traveled'] += p['vel'].length() * dt
                if p['distance_traveled'] > p['range']:
                    projectiles_to_remove.add(idx)
        
        if projectiles_to_remove:
            projectiles = [p for i, p in enumerate(projectiles) if i not in projectiles_to_remove]
    
    # End of battle
    team_a_alive = sum(1 for s in ships if s.is_alive and s.team_id == 0)
    team_b_alive = sum(1 for s in ships if s.is_alive and s.team_id == 1)
    
    if team_a_alive > team_b_alive: winner = 'A'
    elif team_b_alive > team_a_alive: winner = 'B'
    else: winner = 'DRAW'
    
    return (winner, team_a_alive, team_b_alive, MAX_TICKS, True)

def run_tournament():
    """Run full tournament of all strategies vs all strategies."""
    try:
        base_path = ROOT_DIR
        load_components(os.path.join(base_path, "data/components.json"))
        load_modifiers(os.path.join(base_path, "data/modifiers.json"))

        ship_json_path = os.path.join(base_path, "ships/RailGun Frigate (FR).json")
        if not os.path.exists(ship_json_path):
             ships_dir = os.path.join(base_path, "ships")
             if os.path.exists(ships_dir):
                 for f in os.listdir(ships_dir):
                     if f.endswith(".json"):
                         ship_json_path = os.path.join(ships_dir, f)
                         break

        if not os.path.exists(ship_json_path):
            print("ERROR: No ship file found")
            return

        strategies = list(StrategyManager.instance().strategies.keys())
        if not strategies:
            print("ERROR: No strategies found")
            return

        print(f"Tournament: {len(strategies)} strategies. Ship: {os.path.basename(ship_json_path)}")

        for strategy_a in strategies:
            for strategy_b in strategies:
                winner, surv_a, surv_b, ticks, timeout = run_battle(strategy_a, strategy_b, ship_json_path, seed=42)
                print(f"{strategy_a} vs {strategy_b}: {winner} wins ({surv_a}-{surv_b})")

                if os.environ.get("VERIFY_RUN") == "1": return
    finally:
        RegistryManager.instance().clear()
        pygame.quit()

if __name__ == "__main__":
    run_tournament()
