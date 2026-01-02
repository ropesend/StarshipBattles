
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
    output_dir = os.path.join("unit_tests", "data", "ships")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Create Attacker
    # "Attacker": TestShip_S_2L, test_engine_infinite, test_weapon_proj_omni, test_bridge_basic, 5x test_armor_std
    attacker = Ship(name="Test Attacker", ship_class="TestShip_S_2L", x=0, y=0, color=(255, 0, 0))
    attacker.add_component(create_component("test_bridge_basic"), LayerType.CORE)
    attacker.add_component(create_component("test_engine_infinite"), LayerType.CORE)
    attacker.add_component(create_component("test_weapon_proj_omni"), LayerType.CORE)
    for _ in range(5):
        attacker.add_component(create_component("test_armor_std"), LayerType.ARMOR)
    
    attacker.recalculate_stats()
    
    # Save Attacker
    with open(os.path.join(output_dir, "Test_Attacker.json"), 'w') as f:
        json.dump(attacker.to_dict(), f, indent=4)
        print(f"Saved Test_Attacker.json to {output_dir}")

    # 2. Create Target
    # "Target": TestShip_L_4L, test_bridge_basic, 5x test_armor_std, NO ENGINE
    target = Ship(name="Test Target", ship_class="TestShip_L_4L", x=0, y=0, color=(0, 0, 255))
    target.add_component(create_component("test_bridge_basic"), LayerType.CORE)
    # NO ENGINE
    for _ in range(5):
        target.add_component(create_component("test_armor_std"), LayerType.ARMOR)
        
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
        load_components("unit_tests/data/test_components.json")

        class_data = load_json_data("unit_tests/data/test_vehicleclasses.json")
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
