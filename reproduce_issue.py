
import json
import traceback
import sys
import os

# Add current directory to path so we can import modules
sys.path.append(os.getcwd())

from ship import Ship
from components import load_components, load_modifiers

def reproduce():
    try:
        print("Loading components...")
        load_components("data/components.json")
        print("Loading modifiers...")
        load_modifiers("data/modifiers.json")
        
        ship_path = "ships/Devastator (MN).json"
        print(f"Loading {ship_path}...")
        
        with open(ship_path, 'r') as f:
            data = json.load(f)
            
        ship = Ship.from_dict(data)
        print("Ship loaded successfully")
        ship.recalculate_stats()
        print("Stats recalculated successfully")
        
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    reproduce()
