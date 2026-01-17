import json
import os

COMPONENTS_FILE = "data/components.json"

# Cost data from implementation_plan.md
COSTS = {
    "bridge": {"Metals": 80, "Organics": 20, "Vapors": 10, "Radioactives": 5, "Exotics": 10},
    "central_complex_command": {"Metals": 100, "Organics": 25, "Vapors": 15, "Radioactives": 10, "Exotics": 15},
    "railgun": {"Metals": 150, "Radioactives": 30},
    "standard_engine": {"Metals": 120, "Radioactives": 40},
    "thruster": {"Metals": 40, "Radioactives": 10},
    "armor_plate": {"Metals": 100},
    "emissive_armor": {"Metals": 80, "Exotics": 30},
    "crystalline_armor": {"Metals": 60, "Exotics": 50},
    "scattering_armor": {"Metals": 70, "Vapors": 20, "Exotics": 20},
    "fuel_tank": {"Metals": 60},
    "ordnance_tank": {"Metals": 50, "Radioactives": 10},
    "battery": {"Metals": 40, "Vapors": 10, "Radioactives": 5, "Exotics": 10},
    "generator": {"Metals": 70, "Radioactives": 50, "Exotics": 10},
    "laser_cannon": {"Metals": 40, "Radioactives": 10, "Exotics": 30},
    "crew_quarters": {"Metals": 40, "Organics": 50, "Vapors": 10},
    "life_support": {"Metals": 30, "Organics": 40, "Vapors": 20},
    "combat_sensor": {"Metals": 50, "Vapors": 30, "Exotics": 20},
    "ecm_suite": {"Metals": 60, "Vapors": 40, "Exotics": 30},
    "multiplex_tracking": {"Metals": 60, "Vapors": 30, "Exotics": 25},
    "shield_generator": {"Metals": 80, "Radioactives": 20, "Exotics": 60},
    "shield_regen": {"Metals": 60, "Radioactives": 20, "Exotics": 40},
    "capital_missile": {"Metals": 100, "Radioactives": 40, "Exotics": 20},
    "point_defence_cannon": {"Metals": 20, "Radioactives": 5, "Exotics": 15},
    "fighter_launch_bay": {"Metals": 400, "Organics": 50, "Radioactives": 20, "Exotics": 30},
    "master_computer": {"Metals": 80, "Vapors": 40, "Exotics": 60},
    "robotic_drone_crew": {"Metals": 50, "Vapors": 10, "Radioactives": 10, "Exotics": 30},
    "emergency_repair_bay": {"Metals": 100, "Organics": 20, "Radioactives": 10, "Exotics": 20},
    "ordnance_vat": {"Metals": 120, "Vapors": 30, "Radioactives": 50, "Exotics": 20},
    "satellite_core": {"Metals": 30, "Vapors": 5, "Exotics": 10},
    "fighter_cockpit": {"Metals": 10, "Organics": 5, "Vapors": 2, "Exotics": 2},
    "mini_engine": {"Metals": 15, "Radioactives": 5},
    "mini_thruster": {"Metals": 5, "Radioactives": 2},
    "mini_battery": {"Metals": 5, "Vapors": 2, "Radioactives": 1, "Exotics": 2},
    "mini_generator": {"Metals": 10, "Radioactives": 8, "Exotics": 2},
    "mini_ordnance": {"Metals": 5, "Radioactives": 2},
    "mini_fuel_tank": {"Metals": 8},
    "mini_railgun": {"Metals": 15, "Radioactives": 3},
    "mini_laser_cannon": {"Metals": 5, "Radioactives": 2, "Exotics": 5},
    "mini_capital_missile": {"Metals": 15, "Radioactives": 6, "Exotics": 3},
    "mini_armor": {"Metals": 10},
    "mini_sensor": {"Metals": 8, "Vapors": 5, "Exotics": 3},
    "mini_ecm": {"Metals": 10, "Vapors": 6, "Exotics": 5},
    "mini_shield_generator": {"Metals": 12, "Radioactives": 3, "Exotics": 10},
    "mini_emissive_armor": {"Metals": 8, "Exotics": 5},
    "mini_scattering_armor": {"Metals": 8, "Vapors": 3, "Exotics": 3},
    "heavy_railgun": {"Metals": 300, "Radioactives": 60},
    "heavy_laser_cannon": {"Metals": 80, "Radioactives": 20, "Exotics": 60}
}

# Mass parsing helper
def get_mass_for_hulls(comp):
    mass_val = comp.get("mass", 0)
    if isinstance(mass_val, str) and mass_val.startswith("="):
        # We can't easily evaluate formulas here, but we can look for hardcoded mass in hull IDs
        pass
    return mass_val

# Hull costs logic
def get_hull_cost(comp_id, mass):
    if "hull_escort" in comp_id: return {"Metals": 80}
    if "hull_frigate" in comp_id: return {"Metals": 150}
    if "hull_destroyer" in comp_id: return {"Metals": 300}
    if "hull_light_cruiser" in comp_id: return {"Metals": 450}
    if "hull_cruiser" in comp_id: return {"Metals": 600}
    if "hull_heavy_cruiser" in comp_id: return {"Metals": 900}
    if "hull_battle_cruiser" in comp_id: return {"Metals": 1200}
    if "hull_battleship" in comp_id: return {"Metals": 2400}
    if "hull_dreadnought" in comp_id: return {"Metals": 4800}
    if "hull_superdreadnaugh" in comp_id: return {"Metals": 9600}
    if "hull_monitor" in comp_id: return {"Metals": 19200}
    
    if "hull_fighter" in comp_id:
        if "heavy" in comp_id: return {"Metals": 30}
        if "medium" in comp_id: return {"Metals": 22}
        if "test" in comp_id: return {"Metals": 15}
        return {"Metals": 8}
        
    if "satellite" in comp_id:
        if "xl" in comp_id: return {"Metals": 600}
        if "large" in comp_id: return {"Metals": 300}
        if "medium" in comp_id: return {"Metals": 150}
        return {"Metals": 75}
        
    if "complex_tier" in comp_id:
        try:
            tier = int(comp_id.split("tier")[-1])
            metals = 1500 * (2 ** (tier - 1))
            return {"Metals": metals}
        except: pass
        
    return {"Metals": 100} # Default for unknown hulls

def main():
    with open(COMPONENTS_FILE, "r") as f:
        data = json.load(f)
        
    for comp in data["components"]:
        comp_id = comp["id"]
        
        # 1. Check direct table
        if comp_id in COSTS:
            comp["resource_cost"] = COSTS[comp_id]
        # 2. Check hull logic
        elif "hull" in comp_id or "satellite" in comp_id or "complex" in comp_id:
            comp["resource_cost"] = get_hull_cost(comp_id, 0)
        # 3. Default
        else:
            comp["resource_cost"] = {"Metals": 50}
            
    with open(COMPONENTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    main()
