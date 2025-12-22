
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import pygame
# Set dummy video driver for headless
os.environ["SDL_VIDEODRIVER"] = "dummy"

from battle import BattleScene, BATTLE_LOG
from ship import Ship
from designs import create_interceptor, create_brick
from components import load_components, load_modifiers

def run_battle(seed, log_filename):
    # Setup
    pygame.init()
    pygame.display.set_mode((1,1)) # Tiny dummy screen
    
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_components(os.path.join(base_path, "data", "components.json"))
    load_modifiers(os.path.join(base_path, "data", "modifiers.json"))
    
    # Create Ships
    t1 = [create_interceptor(x=i*100, y=100) for i in range(2)]
    t2 = [create_interceptor(x=i*100, y=900) for i in range(2)]
    
    # Configure Logger
    BATTLE_LOG.filename = log_filename
    BATTLE_LOG.enabled = True
    
    # Run Battle
    scene = BattleScene(1000, 1000)
    scene.start(t1, t2, seed=seed, headless=True)
    
    # Run for fixed ticks
    for _ in range(500):
        scene.update([])
        
    BATTLE_LOG.close()
    return log_filename

def compare_files(f1, f2):
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
    
    print("  Executing Run 1...")
    run_battle(seed=42, log_filename=log1)
    
    print("  Executing Run 2...")
    run_battle(seed=42, log_filename=log2)
    
    print("\nComparing Logs...")
    if compare_files(log1, log2):
        print("SUCCESS: Logs are identical. Simulation is deterministic.")
        # Cleanup
        try:
            os.remove(log1)
            os.remove(log2)
        except:
            pass
        sys.exit(0)
    else:
        print("FAILURE: Logs differ.")
        sys.exit(1)
