import json
import os

FILE_PATH = r"c:\Dev\Starship Battles\data\vehicleclasses.json"

def update_layers():
    with open(FILE_PATH, 'r') as f:
        data = json.load(f)

    # Access the 'classes' key
    classes_dict = data.get('classes', {})
    
    for class_id, class_data in classes_dict.items():
        if 'layers' not in class_data:
            continue

        layers = class_data['layers']
        num_layers = len(layers)
        
        # Determine mass limits based on rules
        limits = {}
        if num_layers == 2:
            limits = {'CORE': 1.0, 'ARMOR': 0.3}
        elif num_layers == 3:
            limits = {'CORE': 0.5, 'OUTER': 0.7, 'ARMOR': 0.3}
        elif num_layers == 4:
            limits = {'CORE': 0.3, 'INNER': 0.5, 'OUTER': 0.5, 'ARMOR': 0.3}
        else:
            print(f"Warning: {class_id} has {num_layers} layers, using default 1.0 for all.")
            limits = {l['type']: 1.0 for l in layers}

        # Apply limits
        for layer in layers:
            l_type = layer['type']
            if l_type in limits:
                layer['max_mass_pct'] = limits[l_type]
            else:
                 # Fallback for unexpected layer types (like maybe ENGINE layer if it existed separately?)
                 # But looking at rules, standard types are covered.
                 # If a ship has weird layers, default to something safe or 1.0
                 layer['max_mass_pct'] = 1.0

    with open(FILE_PATH, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Updated {FILE_PATH} with mass limits.")

if __name__ == "__main__":
    update_layers()
