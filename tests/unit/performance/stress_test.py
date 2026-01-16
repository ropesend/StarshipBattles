"""
Stress Test Performance Script for Starship Battles.
Measures update and collision detection performance with many entities.
"""
import pygame
import cProfile
import pstats
import random
import os

# Headless environment
os.environ["SDL_VIDEODRIVER"] = "dummy"

from game.simulation.designs import create_brick, create_interceptor
from game.simulation.components.component import load_components, load_modifiers
from game.simulation.entities.ship import initialize_ship_data
from game.core.registry import RegistryManager
from game.core.constants import AttackType, ROOT_DIR, COMPONENTS_FILE, MODIFIERS_FILE

def run_stress_test():
    try:
        pygame.init()
        # Fallback display initialization for headless
        pygame.display.set_mode((100, 100))

        load_components(COMPONENTS_FILE)
        load_modifiers(MODIFIERS_FILE)
        initialize_ship_data(ROOT_DIR)
        
        all_ships = []
        print("Spawning 100 ships...")
        for i in range(50):
            s = create_brick(random.randint(0, 20000), random.randint(0, 20000))
            s.team_id = 0
            all_ships.append(s)
        
        for i in range(50):
            s = create_interceptor(random.randint(80000, 100000), random.randint(0, 20000))
            s.team_id = 1
            all_ships.append(s)
            
        projectiles = []
        
        # Profiling Loop
        print("Running 500 frames...")
        
        for frame in range(500):
            dt = 0.016 # Fixed dt
            
            alive_ships = [s for s in all_ships if s.is_alive]
            if not alive_ships:
                print("All ships destroyed early.")
                break
                
            # Update Ships
            for s in alive_ships:
                s.update(dt)
                # Simulated AI firing - simplified for stress test
                if random.random() < 0.05: # Occasional fire
                    s.comp_trigger_pulled = True
                    # Resulting attacks are collected below
                else:
                    s.comp_trigger_pulled = False
                
                # Collect and process projectiles
                if hasattr(s, 'just_fired_projectiles') and s.just_fired_projectiles:
                    for attack in list(s.just_fired_projectiles):
                        is_dict = isinstance(attack, dict)
                        a_type = attack.get('type') if is_dict else getattr(attack, 'type', None)
                        
                        if a_type in [AttackType.PROJECTILE, 'projectile', AttackType.MISSILE, 'missile']:
                            p_pos = attack.get('position') if is_dict else getattr(attack, 'position')
                            p_vel = attack.get('velocity') if is_dict else getattr(attack, 'velocity')
                            p_dmg = attack.get('damage') if is_dict else getattr(attack, 'damage')
                            p_source = attack.get('source') if is_dict else getattr(attack, 'owner')
                            
                            projectiles.append({
                                'pos': p_pos.copy(),
                                'vel': p_vel.copy(),
                                'damage': p_dmg,
                                'owner': p_source
                            })
                            s.just_fired_projectiles.remove(attack)
                        elif a_type in [AttackType.BEAM, 'beam']:
                            # Simplified beam for stress test: direct damage to random target
                            target = s.current_target
                            if not target or not target.is_alive:
                                enemies = [e for e in alive_ships if e.team_id != s.team_id]
                                if enemies: target = random.choice(enemies)
                            
                            if target:
                                target.take_damage(attack['damage'] if is_dict else getattr(attack, 'damage'))
                                
                            s.just_fired_projectiles.remove(attack)
                        else:
                            # Other types (launch etc)
                            s.just_fired_projectiles.remove(attack)
                        
            # Update Projectiles & Collision (The Expensive Part)
            new_projectiles = []
            for p in projectiles:
                p['pos'] += p['vel'] * dt
                
                hit = False
                # Collision Check O(N*M) - This is what we are stress testing
                for target in alive_ships:
                    if target == p['owner'] or target.team_id == p['owner'].team_id: continue
                    
                    if p['pos'].distance_to(target.position) < target.radius + 5:
                        target.take_damage(p['damage'])
                        hit = True
                        break
                
                if not hit:
                    # In a real engine we'd check max range too, but keep it simple
                    if p['pos'].length() < 200000: # Simple boundary
                        new_projectiles.append(p)
            
            projectiles = new_projectiles

        print("Done.")
    finally:
        RegistryManager.instance().clear()
        pygame.quit()

if __name__ == "__main__":
    # Run and print stats
    pr = cProfile.Profile()
    pr.enable()
    run_stress_test()
    pr.disable()
    
    ps = pstats.Stats(pr).sort_stats('cumtime')
    ps.print_stats(20)
