
import os
import sys
import json
import pygame

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from game.simulation.entities.ship import Ship, load_vehicle_classes
from game.simulation.components.component import load_components

def update_ships():
    print("Initializing...")
    pygame.init()
    
    # Load TEST data
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    load_vehicle_classes(os.path.join(data_dir, "test_vehicleclasses.json"))
    load_components(os.path.join(data_dir, "test_components.json"))
    
    ships_dir = os.path.join(data_dir, "ships")
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
            
            # Update original data with NEW fields (preserving unknown fields like _test_notes)
            # We want new_data to win for colliding fields
            original_data.update(new_data)
            
            # Save back
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(original_data, f, indent=4)
                
            print(f"  -> Updated expected_stats: MaxSpeed={ship.max_speed:.2f}, Accel={ship.acceleration_rate:.3f}")
            
        except Exception as e:
            print(f"  [ERROR] Failed to process {filename}: {e}")

if __name__ == "__main__":
    update_ships()
