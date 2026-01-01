
import json
import os
import sys

# Add root to path
sys.path.append(os.getcwd())

from ship import Ship
from components import Component, LayerType, create_component

def load_json_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def generate_test_ships():
    # Ensure output dir exists
    output_dir = os.path.join("tests", "data", "ships")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Create Attacker
    # "Attacker": SimpleHull, test_engine_infinite, test_gun_omni, bridge, 5x armor
    attacker = Ship(name="Test Attacker", ship_class="SimpleHull", x=0, y=0, color=(255, 0, 0))
    attacker.add_component(create_component("bridge"), LayerType.CORE)
    attacker.add_component(create_component("test_engine_infinite"), LayerType.CORE)
    attacker.add_component(create_component("test_gun_omni"), LayerType.CORE)
    for _ in range(5):
        attacker.add_component(create_component("armor"), LayerType.ARMOR)
    
    attacker.recalculate_stats()
    
    # Save Attacker
    with open(os.path.join(output_dir, "Test_Attacker.json"), 'w') as f:
        json.dump(attacker.to_dict(), f, indent=4)
        print(f"Saved Test_Attacker.json to {output_dir}")

    # 2. Create Target
    # "Target": ComplexHull, bridge, 5x armor. NO ENGINE.
    target = Ship(name="Test Target", ship_class="ComplexHull", x=0, y=0, color=(0, 0, 255))
    target.add_component(create_component("bridge"), LayerType.CORE)
    # NO ENGINE
    for _ in range(5):
        target.add_component(create_component("armor"), LayerType.ARMOR)
        
    target.recalculate_stats()
    
    # Save Target
    with open(os.path.join(output_dir, "Test_Target.json"), 'w') as f:
        json.dump(target.to_dict(), f, indent=4)
        print(f"Saved Test_Target.json to {output_dir}")

if __name__ == "__main__":
    from components import COMPONENT_REGISTRY, load_components
    from ship import VEHICLE_CLASSES
    
    def load_test_data():
        COMPONENT_REGISTRY.clear()
        load_components("tests/data/test_components.json")

        class_data = load_json_data("tests/data/test_vehicleclasses.json")
        VEHICLE_CLASSES.clear()
        for k, v in class_data.items():
            VEHICLE_CLASSES[k] = v
            
    try:
        load_test_data()
        generate_test_ships()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
