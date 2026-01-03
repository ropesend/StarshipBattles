
import json
import os
import sys

# Add current directory to path so we can import modules
sys.path.append(os.getcwd())

from game.simulation.components.component import COMPONENT_REGISTRY, Component
from game.simulation.entities.ship import Ship, LayerType
from ship_stats import ShipStatsCalculator
from game.simulation.systems.resource_manager import ResourceRegistry

def check_legacy_fields(data, filename):
    print(f"Checking {filename} for legacy fields...")
    legacy_keys = [
        'fuel_cost', 'energy_cost', 'ammo_cost', 
        'capacity', 'resource_type', 'energy_generation'
    ]
    
    issues = []
    
    for comp in data.get('components', []):
        cid = comp.get('id', 'unknown')
        for key in legacy_keys:
            if key in comp:
                issues.append(f"Component '{cid}' has legacy field '{key}'")
                
    if issues:
        print(f"Found {len(issues)} legacy field issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("No legacy fields found.")
        return True

def verify_stat_calculation():
    print("\nVerifying ShipStatsCalculator with new resource system...")
    
    # Create a dummy ship
    ship = Ship("TestShip", 0, 0, (255, 255, 255))
    
    # 1. Test Fuel Storage via Ability
    # Create a fresh component with FuelStorage ability (no legacy fields)
    fuel_tank_data = {
        "id": "test_fuel_tank",
        "name": "Test Tank",
        "type": "Tank",
        "mass": 10,
        "hp": 10,
        "abilities": {
            "FuelStorage": 1000
        }
    }
    
    # Register purely for this test
    # We can just instantiate component directly
    comp = Component(fuel_tank_data)
    ship.add_component(comp, LayerType.CORE)
    
    # Recalculate
    ship.recalculate_stats()
    
    # Check max fuel
    expected_fuel = 1000
    if ship.max_fuel == expected_fuel:
        print(f"SUCCESS: Fuel Storage verified. Expected {expected_fuel}, got {ship.max_fuel}")
    else:
        print(f"FAILURE: Fuel Storage mismatch. Expected {expected_fuel}, got {ship.max_fuel}")
        return False

    # 2. Test Energy Generation via Ability
    gen_data = {
        "id": "test_generator",
        "name": "Test Gen",
        "type": "Generator",
        "mass": 10,
        "hp": 10,
        "abilities": {
            "EnergyGeneration": 50
        }
    }
    comp_gen = Component(gen_data)
    ship.add_component(comp_gen, LayerType.CORE)
    
    ship.recalculate_stats()
    
    # Energy regen is usually calculated per tick in logic, but ShipStats might aggregate it?
    # Let's check ShipStatsCalculator.calculate output or ship.resources
    # ship_stats.py calculates 'energy_generation', 'fuel_consumption', etc.
    
    # Check ship.resources['energy'].regen
    # The stats calculator typically sets this on the resource
    
    # Actually, ShipStatsCalculator updates ship.stats dictionary.
    # It ALSO updates ship.resources values.
    
    energy_res = ship.resources.get_resource('energy')
    if energy_res and energy_res.regen_rate == 50:
         print(f"SUCCESS: Energy Generation verified. Expected 50, got {energy_res.regen_rate}")
    else:
         print(f"FAILURE: Energy Generation mismatch. Expected 50, got {energy_res.regen_rate if energy_res else 'None'}")
         return False
         
    return True

def main():
    # 1. Verify JSON Files
    files_to_check = [
        "data/components.json",
        "tests/data/test_components.json"
    ]
    
    all_clean = True
    for fpath in files_to_check:
        if os.path.exists(fpath):
            with open(fpath, 'r') as f:
                data = json.load(f)
            if not check_legacy_fields(data, fpath):
                all_clean = False
        else:
            print(f"Warning: File {fpath} not found.")
            
    if not all_clean:
        print("\nDATA VERIFICATION FAILED: Legacy fields detected.")
        sys.exit(1)
        
    # 2. Verify Logic
    if not verify_stat_calculation():
        print("\nLOGIC VERIFICATION FAILED: Stat calculation mismatch.")
        sys.exit(1)
        
    print("\nALL SYSTEMS VERIFIED. Resource Refactor is consistent.")

if __name__ == "__main__":
    main()
