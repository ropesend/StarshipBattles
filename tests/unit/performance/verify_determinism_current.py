import os
import sys
import time
import pygame

# Set dummy video driver for headless
os.environ["SDL_VIDEODRIVER"] = "dummy"

from game.ui.screens.battle_scene import BattleScene
from game.simulation.entities.ship import Ship, initialize_ship_data
from game.simulation.designs import create_interceptor, create_brick
from game.simulation.components.component import load_components, load_modifiers
from game.core.registry import RegistryManager
from game.core.constants import ROOT_DIR, COMPONENTS_FILE, MODIFIERS_FILE

def run_battle(seed, log_filename):
    # Setup
    pygame.init()
    # Dummy display for UI components that might check it
    pygame.display.set_mode((1,1))

    try:
        RegistryManager.instance().clear()

        initialize_ship_data(ROOT_DIR)
        load_components(COMPONENTS_FILE)
        load_modifiers(MODIFIERS_FILE)
        
        # Create Ships
        t1 = [create_interceptor(x=float(i*100), y=100.0) for i in range(2)]
        t2 = [create_interceptor(x=float(i*100), y=900.0) for i in range(2)]
        
        # Run Battle
        scene = BattleScene(1000, 1000)
        
        # Configure Logger
        scene.engine.logger.filename = log_filename
        scene.engine.logger.enabled = True
        scene.start(t1, t2, seed=seed, headless=True)
        
        # Run for fixed ticks
        for _ in range(500):
            scene.update([])
            
        scene.engine.logger.close()
    finally:
        pygame.quit()
        RegistryManager.instance().clear()
        
    return log_filename

def compare_files(f1, f2):
    if not os.path.exists(f1) or not os.path.exists(f2):
        print(f"FAIL: Log files missing ({f1}, {f2})")
        return False
        
    with open(f1, 'r') as file1:
        c1 = file1.readlines()
    with open(f2, 'r') as file2:
        c2 = file2.readlines()
        
    if len(c1) != len(c2):
        print(f"FAIL: Line count mismatch ({len(c1)} vs {len(c2)})")
        return False
        
    for i, (l1, l2) in enumerate(zip(c1, c2)):
        if l1 != l2:
            print(f"FAIL: Mismatch at line {i+1}")
            print(f"  Run 1: {l1.strip()}")
            print(f"  Run 2: {l2.strip()}")
            return False
            
    return True

if __name__ == "__main__":
    print("Running Determinism Verification...")
    
    log1 = "test_run_1.log"
    log2 = "test_run_2.log"
    
    try:
        print("  Executing Run 1...")
        run_battle(seed=42, log_filename=log1)

        print("  Executing Run 2...")
        run_battle(seed=42, log_filename=log2)

        print("\nComparing Logs...")
        if compare_files(log1, log2):
            print("SUCCESS: Logs are identical. Simulation is deterministic.")
            # Cleanup
            try:
                if os.path.exists(log1): os.remove(log1)
                if os.path.exists(log2): os.remove(log2)
            except:
                pass
            sys.exit(0)
        else:
            print("FAILURE: Logs differ.")
            sys.exit(1)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
