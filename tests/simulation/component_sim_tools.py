
import json
import os
import sys

def create_ship(filename, name, ship_class, components, ai_strategy="do_nothing", notes=""):
    """
    Helper to create a simple test ship JSON file.
    
    Args:
        filename (str): Output filename (e.g. "Test_Attacker_Proj360.json")
        name (str): Ship name
        ship_class (str): Ship class ID (e.g. "TestS_2L")
        components (list): List of component IDs to add to CORE layer
        ai_strategy (str): Default AI strategy
        notes (str): Test notes
    """
    # Base template
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, '..', 'data', 'ships')
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct layer data - simple approach: all components in CORE
    layer_comps = []
    for comp_id in components:
        layer_comps.append({
            "id": comp_id,
            "modifiers": []
        })
        
    data = {
        "name": name,
        "color": [255, 0, 0] if "Attacker" in name else [0, 0, 255],
        "team_id": 1 if "Attacker" in name else 2,
        "ship_class": ship_class,
        "theme_id": "Federation",
        "ai_strategy": ai_strategy,
        "layers": {
            "CORE": layer_comps,
            "ARMOR": []
        },
        "_test_notes": notes,
        "expected_stats": {
            # Placeholders - will be updated by update_test_ships.py
            "max_hp": 0,
            "max_fuel": 0, 
            "max_ammo": 0,
            "max_energy": 0,
            "max_speed": 0,
            "acceleration_rate": 0,
            "turn_speed": 0,
            "total_thrust": 0,
            "mass": 0,
            "armor_hp_pool": 0
        }
    }
    
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"Created {filename}")

def generate_phase_2_ships():
    # --- Attackers (Section 5.2) ---
    
    # Projectile Omni
    create_ship(
        "Test_Attacker_Proj360.json", "Test Attacker Proj360", "TestS_2L",
        ["test_weapon_proj_omni", "test_storage_ammo"], "test_do_nothing",
        "Attacker with 360 degree projectile weapon"
    )
    
    # Projectile 90 (Fixed)
    create_ship(
        "Test_Attacker_Proj90.json", "Test Attacker Proj90", "TestS_2L",
        ["test_weapon_proj_fixed", "test_storage_ammo"], "test_do_nothing",
        "Attacker with 45 degree fixed projectile weapon"
    )
    
    # Beam Variants
    create_ship(
        "Test_Attacker_Beam360_Low.json", "Test Attacker Beam360 Low", "TestS_2L",
        ["test_beam_low_acc", "test_gen_fusion", "test_storage_energy"], "test_do_nothing",
        "Attacker with Low Accuracy (0.5) Beam"
    )
    create_ship(
        "Test_Attacker_Beam360_Med.json", "Test Attacker Beam360 Med", "TestS_2L",
        ["test_beam_med_acc", "test_gen_fusion", "test_storage_energy"], "test_do_nothing",
        "Attacker with Medium Accuracy (2.0) Beam"
    )
    create_ship(
        "Test_Attacker_Beam360_High.json", "Test Attacker Beam360 High", "TestS_2L",
        ["test_beam_high_acc", "test_gen_fusion", "test_storage_energy"], "test_do_nothing",
        "Attacker with High Accuracy (5.0) Beam"
    )
    
    # Beam Fixed
    create_ship(
        "Test_Attacker_Beam90.json", "Test Attacker Beam90", "TestS_2L",
        ["test_weapon_beam_fixed", "test_gen_fusion", "test_storage_energy"], "test_do_nothing",
        "Attacker with 45 degree fixed beam weapon"
    )
    
    # Seeker Omni
    create_ship(
        "Test_Attacker_Seeker360.json", "Test Attacker Seeker360", "TestS_2L",
        ["test_weapon_missile_omni", "test_storage_ammo"], "test_do_nothing",
        "Attacker with 360 degree seeker weapon"
    )
    
    # --- Targets (Section 5.3) ---
    
    # Stationary
    create_ship(
        "Test_Target_Stationary.json", "Test Target Stationary", "TestM_2L",
        ["test_armor_std"], "test_do_nothing", # Just armor
        "Stationary target, armor only"
    )
    
    # Linear Slow (1 Engine)
    create_ship(
        "Test_Target_Linear_Slow.json", "Test Target Linear Slow", "TestM_2L",
        ["test_armor_std", "test_engine_no_fuel"], "test_straight_line",
        "Linearly moving target, slow speed"
    )
    
    # Linear Fast (3 Engines)
    create_ship(
        "Test_Target_Linear_Fast.json", "Test Target Linear Fast", "TestM_2L",
        ["test_armor_std", "test_engine_no_fuel", "test_engine_no_fuel", "test_engine_no_fuel"], "test_straight_line",
        "Linearly moving target, fast speed"
    )
    
    # Erratic Small (High Maneuverability)
    create_ship(
        "Test_Target_Erratic_Small.json", "Test Target Erratic Small", "TestS_2L",
        ["test_armor_std", "test_engine_no_fuel", "test_thruster_std"], "test_erratic_maneuver",
        "Small erratic target"
    )
    
    # Erratic Large (Low Maneuverability)
    create_ship(
        "Test_Target_Erratic_Large.json", "Test Target Erratic Large", "TestL_2L",
        ["test_armor_std", "test_engine_no_fuel", "test_thruster_std"], "test_erratic_maneuver",
        "Large erratic target"
    )
    
    # Orbiting
    create_ship(
        "Test_Target_Orbiting.json", "Test Target Orbiting", "TestM_2L",
        ["test_armor_std", "test_engine_no_fuel", "test_thruster_std"], "test_orbit_target",
        "Orbiting target"
    )

if __name__ == "__main__":
    generate_phase_2_ships()
