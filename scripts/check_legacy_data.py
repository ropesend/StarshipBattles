
import json
import sys

def check_legacy_fields():
    try:
        with open('data/components.json', 'r') as f:
            data = json.load(f)
            
        legacy_fields = ['range', 'damage', 'firing_arc', 'energy_cost', 'ammo_cost', 'projectile_speed']
        legacy_count = 0
        
        print(f"Scanning {len(data['components'])} components for legacy fields: {legacy_fields}")
        
        for comp in data['components']:
            found = []
            for field in legacy_fields:
                if field in comp:
                    found.append(field)
            
            if found:
                print(f"FAIL: Component '{comp['id']}' has legacy fields: {found}")
                legacy_count += 1
                
        if legacy_count == 0:
            print("SUCCESS: No legacy fields found. components.json is clean!")
            return 0
        else:
            print(f"Found {legacy_count} components with legacy fields.")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(check_legacy_fields())
