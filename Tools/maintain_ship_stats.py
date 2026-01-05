
import sys
import os
import json
import glob

sys.path.append(os.getcwd())

from game.simulation.entities.ship import Ship, load_vehicle_classes
from game.simulation.components.component import load_components, load_modifiers
from game.core.registry import RegistryManager

def update_stats():
    print("Loading data...")
    load_components("data/components.json")
    load_modifiers("data/modifiers.json")
    load_vehicle_classes("data/vehicleclasses.json")
    
    ships_dir = os.path.join(os.getcwd(), "ships")
    ship_files = glob.glob(os.path.join(ships_dir, "*.json"))
    
    print(f"Found {len(ship_files)} ship files.")
    
    for ship_path in ship_files:
        try:
            print(f"Processing {os.path.basename(ship_path)}...")
            with open(ship_path, 'r') as f:
                data = json.load(f)
            
            # Create ship and recalc
            ship = Ship.from_dict(data)
            ship.recalculate_stats()
            
            # Update expected_stats
            if 'expected_stats' not in data:
                data['expected_stats'] = {}
            
            # Update keys that exist or are standard
            keys_to_update = ['max_hp', 'max_fuel', 'max_ammo', 'max_energy', 'total_thrust', 'mass', 'max_speed', 'turn_speed']
            
            for key in keys_to_update:
                if hasattr(ship, key):
                    val = getattr(ship, key)
                    # For floats, maybe round? JSON uses simple values.
                    # Checks usually use delta=1.
                    if isinstance(val, float):
                        val = round(val, 2)
                    data['expected_stats'][key] = val
            
            # Write back
            with open(ship_path, 'w') as f:
                json.dump(data, f, indent=4)
                
            print(f"  Updated stats for {ship.name}")
            
        except Exception as e:
            print(f"  Error processing {ship_path}: {e}")

if __name__ == "__main__":
    update_stats()
