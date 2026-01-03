
import json
import os

def remove_radius_pct():
    filepath = "data/vehicleclasses.json"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        classes = data.get('classes', {})
        count = 0
        
        for class_name, cls_data in classes.items():
            layers = cls_data.get('layers', [])
            for layer in layers:
                if 'radius_pct' in layer:
                    del layer['radius_pct']
                    count += 1
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f"Successfully removed 'radius_pct' from {count} layer definitions.")
        
    except Exception as e:
        print(f"Error updating JSON: {e}")

if __name__ == "__main__":
    remove_radius_pct()
