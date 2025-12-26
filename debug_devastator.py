
import json
import os
import sys

sys.path.append(os.getcwd())

from ship import Ship, load_vehicle_classes
from components import load_components, load_modifiers

def debug_devastator():
    print("Loading data...")
    load_components("data/components.json")
    load_modifiers("data/modifiers.json")
    load_vehicle_classes("data/vehicleclasses.json")
    
    ship_path = "ships/Devastator (MN).json"
    if not os.path.exists(ship_path):
        print(f"File not found: {ship_path}")
        return

    with open(ship_path, 'r') as f:
        data = json.load(f)
        
    print(f"Creating ship from {ship_path}...")
    
    # Manually mimic from_dict but with debug prints
    name = data.get("name", "Unnamed")
    s = Ship(name, 0, 0, (255,255,255), ship_class=data.get("ship_class", "Escort"))
    # Ensure initialized correct max mass from loaded classes
    from ship import VEHICLE_CLASSES
    if s.ship_class in VEHICLE_CLASSES: # Need global access?
         pass
         
    print(f"Ship Class: {s.ship_class}")
    print(f"Max Mass Budget: {s.max_mass_budget}")
    
    # Check layers
    for ltype, ldata in s.layers.items():
        print(f"Layer {ltype.name}: Max Mass {s.max_mass_budget * ldata['max_mass_pct']}")

    from components import COMPONENT_REGISTRY, LayerType, MODIFIER_REGISTRY
    
    for l_name, comps_list in data.get("layers", {}).items():
        try:
            layer_type = LayerType[l_name]
        except KeyError:
            continue
            
        print(f"\nProcessing Layer {l_name}")
        for c_entry in comps_list:
            comp_id = ""
            modifiers_data = []
            if isinstance(c_entry, dict):
                comp_id = c_entry.get("id")
                modifiers_data = c_entry.get("modifiers", [])
            else:
                continue # simple string
                
            if comp_id in COMPONENT_REGISTRY:
                new_comp = COMPONENT_REGISTRY[comp_id].clone()
                for m_dat in modifiers_data:
                    mid = m_dat['id']
                    mval = m_dat['value']
                    if mid in MODIFIER_REGISTRY:
                        new_comp.add_modifier(mid, mval)
                
                print(f"  Adding {comp_id} Mass: {new_comp.mass:.1f}")
                
                # Check budget manually
                layer_data = s.layers[layer_type]
                current_layer_mass = sum(c.mass for c in layer_data['components'])
                max_layer_mass = s.max_mass_budget * layer_data.get('max_mass_pct', 1.0)
                
                if current_layer_mass + new_comp.mass > max_layer_mass:
                     print(f"    FAIL: Budget Exceeded! Current: {current_layer_mass:.1f} + {new_comp.mass:.1f} > {max_layer_mass:.1f}")
                
                success = s.add_component(new_comp, layer_type)
                if not success:
                    print("    Add failed.")
                else:
                    print("    Add success.")

if __name__ == "__main__":
    debug_devastator()
