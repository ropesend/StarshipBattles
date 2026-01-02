
import json
import os

def migrate_component(comp):
    changed = False
    
    # Ensure abilities dict exists
    if 'abilities' not in comp:
        comp['abilities'] = {}
        changed = True
    
    abilities = comp['abilities']

    # 1. Fuel Cost -> ResourceConsumption (Constant -> trigger: constant)
    # NOTE: Shim used 'constant'. We will stick to that to preserve behavior.
    if 'fuel_cost' in comp:
        val = comp.pop('fuel_cost')
        if val > 0:
            if 'ResourceConsumption' not in abilities:
                abilities['ResourceConsumption'] = []
            
            # Check if exists (unlikely if we are migrating legacy field)
            exists = any(x.get('resource') == 'fuel' for x in abilities['ResourceConsumption'])
            # Also check if it was defined as a dict (unlikely for new list format)
            
            if not exists:
                abilities['ResourceConsumption'].append({
                    "resource": "fuel",
                    "amount": val,
                    "trigger": "constant"
                })
                print(f"  - Migrated fuel_cost {val} to ResourceConsumption")
        changed = True

    # 2. Energy Cost -> ResourceConsumption (Activation)
    if 'energy_cost' in comp:
        val = comp.pop('energy_cost')
        if val > 0:
            if 'ResourceConsumption' not in abilities:
                abilities['ResourceConsumption'] = []
            
            exists = any(x.get('resource') == 'energy' and x.get('trigger') == 'activation' for x in abilities['ResourceConsumption'])
            
            if not exists:
                abilities['ResourceConsumption'].append({
                    "resource": "energy",
                    "amount": val,
                    "trigger": "activation"
                })
                print(f"  - Migrated energy_cost {val} to ResourceConsumption")
        changed = True

    # 3. Ammo Cost -> ResourceConsumption (Activation)
    if 'ammo_cost' in comp:
        val = comp.pop('ammo_cost')
        if val > 0:
            if 'ResourceConsumption' not in abilities:
                abilities['ResourceConsumption'] = []
            
            exists = any(x.get('resource') == 'ammo' and x.get('trigger') == 'activation' for x in abilities['ResourceConsumption'])
            
            if not exists:
                abilities['ResourceConsumption'].append({
                    "resource": "ammo",
                    "amount": val,
                    "trigger": "activation"
                })
                print(f"  - Migrated ammo_cost {val} to ResourceConsumption")
        changed = True

    # 4. Energy Generation -> EnergyGeneration (Shortcut) OR ResourceGeneration
    if 'energy_generation' in comp:
        val = comp.pop('energy_generation')
        if val > 0:
            # Check if we should use shortcut "EnergyGeneration": val
            # or generic "ResourceGeneration": [{"resource": "energy", "amount": val}]
            # The shim uses generic ResourceGeneration list.
            # But components.json already uses "EnergyGeneration": 25 shortcut in some places.
            # Let's map to the SHORTCUT "EnergyGeneration" if possible because it's cleaner,
            # BUT the shim mapped to generic. Let's use generic to be robust or specific if defined.
            
            # Looking at components.py:
            # if name == 'EnergyGeneration': self.ability_instances.append(ResourceGeneration('energy', data))
            
            current_eg = abilities.get('EnergyGeneration')
            if current_eg is None:
                abilities['EnergyGeneration'] = val
                print(f"  - Migrated energy_generation {val} to EnergyGeneration")
            else:
                # If it already exists, maybe we are just updating? Or duplicates?
                # Assuming legacy field overlaps with new ability field -> legacy should likely be removed or merged.
                # If they match, just remove legacy.
                if current_eg == val:
                    pass
                else:
                    # Conflict?
                    pass
        changed = True

    # 5. Capacity + Resource Type -> ResourceStorage (Generic)
    if 'capacity' in comp:
        val = comp.pop('capacity')
        rtype = comp.pop('resource_type', 'fuel') # Default to fuel if capacity but no type?
        
        if val > 0:
            # Map to specific shortcuts if available
            key_map = {
                'fuel': 'FuelStorage',
                'energy': 'EnergyStorage',
                'ammo': 'AmmoStorage'
            }
            
            target_key = key_map.get(rtype)
            
            if target_key:
                # Use shortcut
                if target_key not in abilities:
                    abilities[target_key] = val
                    print(f"  - Migrated capacity {val} ({rtype}) to {target_key}")
            else:
                # Use Generic
                if 'ResourceStorage' not in abilities:
                    abilities['ResourceStorage'] = []
                
                abilities['ResourceStorage'].append({
                    "resource": rtype,
                    "amount": val
                })
                print(f"  - Migrated capacity {val} ({rtype}) to ResourceStorage")
        else:
             # Remove resource_type if it was there but capacity 0
             pass
        changed = True
    elif 'resource_type' in comp:
        # Just lonely resource_type?
        comp.pop('resource_type')
        changed = True

    return changed

def migrate_file(filepath):
    print(f"Migrating {filepath}...")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to load {filepath}: {e}")
        return

    comps = data.get('components', [])
    total_migrated = 0
    
    for comp in comps:
        print(f"Checking {comp.get('id', 'unknown')}...")
        if migrate_component(comp):
            total_migrated += 1
            
    if total_migrated > 0:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Success! Migrated {total_migrated} components.")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    migrate_file("data/components.json")
    migrate_file("unit_tests/data/test_components.json")
