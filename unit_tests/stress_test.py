import sys
import os
import pygame
import cProfile
import pstats
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from game_engine import GameEngine # Wait, main.py has Game class, but is it reusable?
# main.py has Game class which runs the loop. We want a headless or automated version.
# Let's import Game from main
from main import Game, create_brick, create_interceptor

def run_stress_test():
    # Initialize Game (Headless-ish, we still need pygame initialized)
    pygame.init()
    # Set a dummy display mode to avoid window popping up if possible, or just minimize
    # os.environ["SDL_VIDEODRIVER"] = "dummy" 
    # Use real display to measure render cost too
    screen = pygame.display.set_mode((1200, 900))
    
    game = Game()
    game.running = True
    game.state = 2 # BATTLE
    
    # Spawn 100 ships
    ships = []
    print("Spawning 100 ships...")
    for i in range(50):
        # Team 1
        s1 = create_brick(random.randint(0, 10000), random.randint(0, 50000))
        game.ship1 = s1 # This logic overrides specific slots...
        # The game engine in main.py is hardcoded for 2 ships (ship1, ship2).
        # We need to hack it or update it to support a list of ships for this test to work well.
        # But wait, the user wants "100s of ships".
        # The current Game class only supports 2 ships: self.ship1, self.ship2.
        # This confirms a MAJOR architectural bottleneck right away!
        pass

    # For now, let's just make the 2 ships fight very fast to measure update cost,
    # OR better, let's fast-forward the battle loop in main.py to handle a list of ships if we want to test 100.
    # But we can't easily change the engine just for the test without changing the engine.
    
    # Plan B: Create a synthetic list of ships and update them manually in the test loop
    # duplicating the logic we WANT to test (collision/update).
    
    from ship import Ship
    from ai import AIController
    
    all_ships = []
    for i in range(50):
        s = create_brick(random.randint(0, 20000), random.randint(0, 20000))
        all_ships.append(s)
    
    for i in range(50):
        s = create_interceptor(random.randint(80000, 100000), random.randint(0, 20000))
        all_ships.append(s)
        
    projectiles = []
    
    # Profiling Loop
    print("Running 500 frames...")
    clock = pygame.time.Clock()
    
    for frame in range(500):
        dt = 0.016 # Fixed dt
        
        # Update Ships
        for s in all_ships:
            s.update(dt)
            # Simulated AI firing
            if random.random() < 0.05: # Occasional fire
                attacks = s.fire_weapons()
                if attacks:
                    projectiles.extend(attacks)
                    
        # Update Projectiles & Collision (The Expensive Part)
        for p in projectiles[:]:
            if p['type'] == 'projectile':
                p['pos'] += p['vel'] * dt
                p['distance_traveled'] += p['vel'].length() * dt
            
                # Collision Check O(N*M)
                for target in all_ships:
                    if target == p['owner']: continue
                    if not target.is_alive: continue
                    if p['pos'].distance_to(target.position) < 40:
                        target.take_damage(p['damage'])
                        # Remove p
                        if p in projectiles: projectiles.remove(p)
                        break

    print("Done.")

if __name__ == "__main__":
    import cProfile
    # Run and print stats
    pr = cProfile.Profile()
    pr.enable()
    run_stress_test()
    pr.disable()
    
    ps = pstats.Stats(pr).sort_stats('cumtime')
    ps.print_stats(20)
