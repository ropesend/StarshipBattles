"""
Script to update ship expected_stats based on current simulation logic.
Parses all ship JSONs, recalculates stats, and updates the files.
"""
import os
import sys
import json
import pygame

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from game.simulation.entities.ship import Ship, load_vehicle_classes
from game.simulation.components.component import load_components
from game.core.registry import RegistryManager

def update_ships():
    print("Initializing...")
    original_path = sys.path.copy()
    try:
        pygame.init()
        # Headless display for any coordinate math or surface transforms
        pygame.display.set_mode((1, 1))
        
        # Load TEST data
        data_dir = os.path.join(ROOT_DIR, 'tests', 'unit', 'data')
        load_vehicle_classes(os.path.join(data_dir, "test_vehicleclasses.json"))
        load_components(os.path.join(data_dir, "test_components.json"))
        
        ships_dir = os.path.join(data_dir, "ships")
        if not os.path.exists(ships_dir):
            print(f"Error: Ships directory not found at {ships_dir}")
            return
            
        files = [f for f in os.listdir(ships_dir) if f.endswith('.json')]
        print(f"Found {len(files)} ship files in {ships_dir}")
        
        for filename in files:
            filepath = os.path.join(ships_dir, filename)
            print(f"Processing {filename}...")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    original_data = json.load(f)
                
                # Create ship and recalc
                ship = Ship.from_dict(original_data)
                ship.recalculate_stats()
                
                # Get new data
                new_data = ship.to_dict()
                
                # Update original data (preserving extra fields)
                original_data.update(new_data)
                
                # Save back
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(original_data, f, indent=4)
                    
                print(f"  -> Updated: Speed={ship.max_speed:.2f}, Accel={ship.acceleration_rate:.3f}")
                
            except Exception as e:
                print(f"  [ERROR] Failed to process {filename}: {e}")
                
    finally:
        RegistryManager.instance().clear()
        pygame.quit()
        sys.path = original_path

if __name__ == "__main__":
    update_ships()
