"""
Strategy Tournament Simulation for Starship Battles.
Runs all combat strategies vs all combat strategies with 5v5 escort ships.
Logs results to CSV for analysis.
"""
import sys
import os
import json
import csv
import time
import random
from datetime import datetime
from itertools import product

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Minimal pygame init (headless)
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((800, 600))

from game.simulation.entities.ship import Ship, LayerType
from game.ai.controller import AIController, COMBAT_STRATEGIES
from game.engine.spatial import SpatialGrid
from game.simulation.components.component import load_components, load_modifiers

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
                ai.update(dt)
        
        # Update ships
        for s in ships:
            s.update(dt)
        
        # Collect and process projectiles
        for s in alive_ships:
            if hasattr(s, 'just_fired_projectiles') and s.just_fired_projectiles:
                for attack in s.just_fired_projectiles:
                    if attack['type'] == 'projectile':
                        projectiles.append({
                            'pos': attack['position'].copy(),
                            'vel': attack['velocity'].copy(),
                            'damage': attack['damage'],
                            'range': attack['range'],
                            'distance_traveled': 0,
                            'owner': attack['source'],
                            'radius': 3
                        })
                s.just_fired_projectiles = []
        
        # Update projectiles with CCD
        projectiles_to_remove = set()
        
        for idx, p in enumerate(projectiles):
            if idx in projectiles_to_remove:
                continue
            
            p_pos_t0 = p['pos']
            p_vel = p['vel']
            p_vel_length = p_vel.length()
            p_pos_t1 = p_pos_t0 + p_vel * dt
            
            hit_occurred = False
            
            # Broad-phase
            query_pos = (p_pos_t0 + p_pos_t1) * 0.5
            query_radius = p_vel_length * dt + 100
            nearby_ships = grid.query_radius(query_pos, query_radius)
            
            for s in nearby_ships:
                if not s.is_alive:
                    continue
                if s.team_id == p['owner'].team_id:
                    continue
                
                # CCD check
                s_vel = s.velocity
                s_pos_t1 = s.position
                s_pos_t0 = s_pos_t1 - s_vel * dt
                
                D0 = p_pos_t0 - s_pos_t0
                DV = p_vel - s_vel
                
                dv_sq = DV.dot(DV)
                collision_radius = s.radius + 5
                
                hit = False
                if dv_sq == 0:
                    if D0.length() < collision_radius:
                        hit = True
                else:
                    t = -D0.dot(DV) / dv_sq
                    t_clamped = max(0, min(t, dt))
                    p_at_t = p_pos_t0 + p_vel * t_clamped
                    s_at_t = s_pos_t0 + s_vel * t_clamped
                    if p_at_t.distance_to(s_at_t) < collision_radius:
                        hit = True
                
                if hit:
                    s.take_damage(p['damage'])
                    hit_occurred = True
                    break
            
            if hit_occurred:
                projectiles_to_remove.add(idx)
            else:
                p['pos'] = p_pos_t1
                p['distance_traveled'] += p_vel_length * dt
                if p['distance_traveled'] > p['range']:
                    projectiles_to_remove.add(idx)
        
        if projectiles_to_remove:
            projectiles = [p for i, p in enumerate(projectiles) if i not in projectiles_to_remove]
        
        # Process beam weapons
        import math
        for s in alive_ships:
            if hasattr(s, 'just_fired_projectiles') and s.just_fired_projectiles:
                for attack in list(s.just_fired_projectiles):
                    if attack['type'] == 'beam':
                        start_pos = attack['origin']
                        direction = attack['direction']
                        max_range = attack['range']
                        target = attack.get('target')
                        
                        if target and target.is_alive:
                            # Raycast against target
                            f = start_pos - target.position
                            a = direction.dot(direction)
                            b = 2 * f.dot(direction)
                            c = f.dot(f) - target.radius**2
                            
                            discriminant = b*b - 4*a*c
                            hit = False
                            hit_dist = 0
                            
                            if discriminant >= 0:
                                t1 = (-b - math.sqrt(discriminant)) / (2*a)
                                t2 = (-b + math.sqrt(discriminant)) / (2*a)
                                
                                valid_t = []
                                if 0 <= t1 <= max_range: valid_t.append(t1)
                                if 0 <= t2 <= max_range: valid_t.append(t2)
                                
                                if valid_t:
                                    hit_dist = min(valid_t)
                                    hit = True
                            
                            if hit:
                                beam_comp = attack['component']
                                chance = beam_comp.calculate_hit_chance(hit_dist)
                                if random.random() < chance:
                                    target.take_damage(attack['damage'])
                        
                        # Remove beam from list (already processed)
                        s.just_fired_projectiles.remove(attack)
        
        # Ship-to-ship collisions (Ramming) - only for kamikaze strategy
        for s in ships:
            if not s.is_alive: 
                continue
            if getattr(s, 'ai_strategy', '') != 'kamikaze': 
                continue
            
            target = s.current_target
            if not target or not target.is_alive: 
                continue
            
            collision_radius = s.radius + target.radius
            
            if s.position.distance_to(target.position) < collision_radius:
                # Ramming collision!
                hp_rammer = s.hp
                hp_target = target.hp
                
                if hp_rammer < hp_target:
                    s.take_damage(hp_rammer + 9999)
                    target.take_damage(hp_rammer * 0.5)
                elif hp_target < hp_rammer:
                    target.take_damage(hp_target + 9999)
                    s.take_damage(hp_target * 0.5)
                else:
                    s.take_damage(hp_rammer + 9999)
                    target.take_damage(hp_target + 9999)
    
    # Time limit reached - determine winner by survivors
    team_a_alive = sum(1 for s in ships if s.is_alive and s.team_id == 0)
    team_b_alive = sum(1 for s in ships if s.is_alive and s.team_id == 1)
    
    if team_a_alive > team_b_alive:
        winner = 'A'
    elif team_b_alive > team_a_alive:
        winner = 'B'
    else:
        winner = 'DRAW'
    
    return (winner, team_a_alive, team_b_alive, MAX_TICKS, True)

def run_tournament():
    """Run full tournament of all strategies vs all strategies."""
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Load game data
    load_components(os.path.join(base_path, "data/components.json"))
    load_modifiers(os.path.join(base_path, "data/modifiers.json"))
    
    # Ship file path
    ship_json_path = os.path.join(base_path, "escort1.json")
    
    if not os.path.exists(ship_json_path):
        print(f"ERROR: Ship file not found: {ship_json_path}")
        return
    
    # Get all strategy IDs
    strategies = list(COMBAT_STRATEGIES.keys())
    print(f"Found {len(strategies)} strategies: {strategies}")
    
    # Create results log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(base_path, f"tournament_results_{timestamp}.csv")
    
    results = []
    total_matches = len(strategies) ** 2
    match_num = 0
    
    print(f"\n{'='*60}")
    print(f"STRATEGY TOURNAMENT")
    print(f"Ships: {SHIPS_PER_TEAM}v{SHIPS_PER_TEAM} | Time Limit: {TIME_LIMIT_MINUTES} min")
    print(f"Total Matches: {total_matches}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    # Run all matchups
    for strategy_a in strategies:
        for strategy_b in strategies:
            match_num += 1
            name_a = COMBAT_STRATEGIES[strategy_a].get('name', strategy_a)
            name_b = COMBAT_STRATEGIES[strategy_b].get('name', strategy_b)
            
            print(f"[{match_num}/{total_matches}] {name_a} vs {name_b}...", end=" ", flush=True)
            
            match_start = time.time()
            winner, surv_a, surv_b, ticks, timeout = run_battle(
                strategy_a, strategy_b, ship_json_path, seed=match_num
            )
            match_time = time.time() - match_start
            
            result = {
                'match': match_num,
                'strategy_a': strategy_a,
                'strategy_a_name': name_a,
                'strategy_b': strategy_b,
                'strategy_b_name': name_b,
                'winner': winner,
                'survivors_a': surv_a,
                'survivors_b': surv_b,
                'ticks': ticks,
                'seconds': ticks / TICK_RATE,
                'timeout': timeout,
                'sim_time': round(match_time, 2)
            }
            results.append(result)
            
            outcome = f"{'TIMEOUT - ' if timeout else ''}{winner} wins ({surv_a}-{surv_b})"
            print(f"{outcome} [{match_time:.1f}s]")
    
    total_time = time.time() - start_time
    
    # Write results to CSV
    with open(log_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n{'='*60}")
    print(f"TOURNAMENT COMPLETE")
    print(f"Total Time: {total_time/60:.1f} minutes")
    print(f"Results saved to: {log_path}")
    print(f"{'='*60}")
    
    # Summary statistics
    print("\n--- STRATEGY PERFORMANCE SUMMARY ---\n")
    
    wins = {s: 0 for s in strategies}
    losses = {s: 0 for s in strategies}
    draws = {s: 0 for s in strategies}
    
    for r in results:
        if r['winner'] == 'A':
            wins[r['strategy_a']] += 1
            losses[r['strategy_b']] += 1
        elif r['winner'] == 'B':
            wins[r['strategy_b']] += 1
            losses[r['strategy_a']] += 1
        else:
            draws[r['strategy_a']] += 1
            draws[r['strategy_b']] += 1
    
    # Sort by wins
    sorted_strategies = sorted(strategies, key=lambda s: wins[s], reverse=True)
    
    print(f"{'Strategy':<25} {'Wins':>6} {'Losses':>8} {'Draws':>7} {'Win %':>7}")
    print("-" * 55)
    for s in sorted_strategies:
        name = COMBAT_STRATEGIES[s].get('name', s)
        total = wins[s] + losses[s] + draws[s]
        win_pct = (wins[s] / total * 100) if total > 0 else 0
        print(f"{name:<25} {wins[s]:>6} {losses[s]:>8} {draws[s]:>7} {win_pct:>6.1f}%")

if __name__ == "__main__":
    run_tournament()
