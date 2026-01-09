"""
Performance profiling for Starship Battles simulation.
Runs a headless battle simulation and outputs profiling data.
"""
import sys
import os
import cProfile
import pstats
import random
import io

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Minimal pygame init
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((800, 600))

from game.simulation.entities.ship import Ship, LayerType
from game.ai.controller import AIController
from game.engine.spatial import SpatialGrid
from game.simulation.designs import create_brick, create_interceptor
from game.simulation.components.component import load_components, load_modifiers

def run_battle_simulation(num_ships_per_team=10, num_ticks=300):
    """Run a headless battle simulation for profiling."""
    
    # Load components
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    load_components(os.path.join(base_path, "data/components.json"))
    load_modifiers(os.path.join(base_path, "data/modifiers.json"))
    
    # Create ships
    ships = []
    ai_controllers = []
    grid = SpatialGrid(cell_size=2000)
    
    # Team 1 - Bricks (left line)
    for i in range(num_ships_per_team):
        s = create_brick(
            1000 + random.randint(-500, 500), 
            i * 300 + random.randint(-100, 100)
        )
        s.team_id = 0
        ships.append(s)
        ai_controllers.append(AIController(s, grid, 1))
    
    # Team 2 - Interceptors (right line, within weapon range ~2400)
    for i in range(num_ships_per_team):
        s = create_interceptor(
            3000 + random.randint(-500, 500), 
            i * 300 + random.randint(-100, 100)
        )
        s.team_id = 1
        s.angle = 180
        ships.append(s)
        ai_controllers.append(AIController(s, grid, 0))
    
    projectiles = []
    beams = []
    dt = 1.0 / 60.0  # Fixed timestep
    
    print(f"Starting simulation: {num_ships_per_team}v{num_ships_per_team} for {num_ticks} ticks...")
    
    for tick in range(num_ticks):
        # Update spatial grid
        grid.clear()
        alive_ships = [s for s in ships if s.is_alive]
        for s in alive_ships:
            grid.insert(s)
        
        # Update AI
        for ai in ai_controllers:
            ai.update(dt)
        
        # Update ships
        for s in ships:
            s.update(dt)
        
        # Collect attacks
        for s in alive_ships:
            if hasattr(s, 'just_fired_projectiles') and s.just_fired_projectiles:
                for attack in s.just_fired_projectiles:
                    if attack['type'] == 'projectile':
                        projectiles.append({
                            'pos': attack['position'],
                            'vel': attack['velocity'],
                            'damage': attack['damage'],
                            'range': attack['range'],
                            'distance_traveled': 0,
                            'owner': attack['source'],
                            'radius': 3
                        })
                s.just_fired_projectiles = []
        
        # Update projectiles with CCD collision
        projectiles_to_remove = set()
        
        for idx, p in enumerate(projectiles):
            if idx in projectiles_to_remove:
                continue
            
            p_pos_t0 = p['pos']
            p_vel = p['vel']
            p_vel_length = p_vel.length()
            p_pos_t1 = p_pos_t0 + p_vel * dt
            
            hit_occurred = False
            
            # Broad-phase: use spatial grid
            query_pos = (p_pos_t0 + p_pos_t1) * 0.5
            query_radius = p_vel_length * dt + 100
            nearby_ships = grid.query_radius(query_pos, query_radius)
            
            for s in nearby_ships:
                if not s.is_alive: continue
                if s.team_id == p['owner'].team_id: continue
                
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
        
        # Progress update every 100 ticks
        if tick % 100 == 0:
            alive_t1 = sum(1 for s in ships if s.is_alive and s.team_id == 0)
            alive_t2 = sum(1 for s in ships if s.is_alive and s.team_id == 1)
            print(f"  Tick {tick}: Team1={alive_t1}, Team2={alive_t2}, Projectiles={len(projectiles)}")
    
    # Final stats
    alive_t1 = sum(1 for s in ships if s.is_alive and s.team_id == 0)
    alive_t2 = sum(1 for s in ships if s.is_alive and s.team_id == 1)
    print(f"Final: Team1={alive_t1} alive, Team2={alive_t2} alive")

def main():
    # Profile with cProfile
    print("=" * 60)
    print("STARSHIP BATTLES PROFILER")
    print("=" * 60)
    
    # Set seed for reproducibility
    random.seed(42)
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    run_battle_simulation(num_ships_per_team=25, num_ticks=500)
    
    profiler.disable()
    
    # Output stats
    print("\n" + "=" * 60)
    print("TOP 30 FUNCTIONS BY CUMULATIVE TIME")
    print("=" * 60)
    
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    stats.print_stats(30)
    
    print("\n" + "=" * 60)
    print("TOP 20 FUNCTIONS BY TOTAL TIME (self)")
    print("=" * 60)
    stats.sort_stats('tottime')
    stats.print_stats(20)

if __name__ == "__main__":
    main()
