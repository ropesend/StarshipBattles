"""
Script to generate test ship design JSON files.
Used by unit tests to ensure consistent test data.
"""
import json
import os
import sys

from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component, LayerType, create_component
from game.core.registry import RegistryManager
from game.simulation.components.component import load_components
from game.core.constants import ROOT_DIR

def load_json_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def generate_test_ships():
    # Ensure output dir exists
    output_dir = os.path.join(ROOT_DIR, "tests", "unit", "data", "ships")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Create Attacker
    attacker = Ship(name="Test Attacker", ship_class="TestShip_S_2L", x=0, y=0, color=(255, 0, 0))
    attacker.add_component(create_component("test_bridge_basic"), LayerType.CORE)
    attacker.add_component(create_component("test_engine_infinite"), LayerType.CORE)
    attacker.add_component(create_component("test_weapon_proj_omni"), LayerType.CORE)
    for _ in range(5):
        attacker.add_component(create_component("test_armor_std"), LayerType.ARMOR)
    
    attacker.recalculate_stats()
    
    # Save Attacker
    attacker_path = os.path.join(output_dir, "Test_Attacker.json")
    with open(attacker_path, 'w') as f:
        json.dump(attacker.to_dict(), f, indent=4)
        print(f"Saved Test_Attacker.json to {output_dir}")

    # 2. Create Target
    target = Ship(name="Test Target", ship_class="TestShip_L_4L", x=0, y=0, color=(0, 0, 255))
    target.add_component(create_component("test_bridge_basic"), LayerType.CORE)
    for _ in range(5):
        target.add_component(create_component("test_armor_std"), LayerType.ARMOR)
        
    target.recalculate_stats()
    
    # Save Target
    target_path = os.path.join(output_dir, "Test_Target.json")
    with open(target_path, 'w') as f:
        json.dump(target.to_dict(), f, indent=4)
        print(f"Saved Test_Target.json to {output_dir}")

def run_generation():
    try:
        # Load test registry data
        RegistryManager.instance().clear()

        test_data_dir = os.path.join(ROOT_DIR, "tests", "unit", "data")

        # Load components - assumes test_components.json or similar exists?
        # The original script just called load_components() which defaults to data/components.json
        # But then it might not find the 'test_' components.
        # Let's check for test_components.json
        test_comp_path = os.path.join(test_data_dir, "test_components.json")
        if os.path.exists(test_comp_path):
            load_components(test_comp_path)
        else:
            load_components()

        # Load vehicle classes
        test_vclass_path = os.path.join(test_data_dir, "test_vehicleclasses.json")
        if os.path.exists(test_vclass_path):
            vehicle_classes_data = load_json_data(test_vclass_path)
            # Support both format with "classes" key or direct dict
            if "classes" in vehicle_classes_data:
                classes = vehicle_classes_data["classes"]
            else:
                classes = vehicle_classes_data

            RegistryManager.instance().vehicle_classes.update(classes)

        generate_test_ships()
    finally:
        RegistryManager.instance().clear()

if __name__ == "__main__":
    run_generation()
