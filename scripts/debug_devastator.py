
import sys
import os
import json
import traceback

sys.path.append(os.getcwd())

from ship import Ship, load_vehicle_classes
from components import load_components, load_modifiers

def debug():
    try:
        load_components("data/components.json")
        load_modifiers("data/modifiers.json")
        load_vehicle_classes("data/vehicleclasses.json")
        
        ship_path = os.path.join(os.getcwd(), "ships", "Devastator (MN).json")
        print(f"Loading {ship_path}")
        with open(ship_path, 'r') as f:
            data = json.load(f)
            
        ship = Ship.from_dict(data)
        print("Ship created. Recalculating...")
        ship.recalculate_stats()
        print("Success!")
        
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    debug()
