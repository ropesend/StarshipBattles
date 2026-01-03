import json
import os

def refactor_components():
    filepath = "data/components.json"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, 'r') as f:
        data = json.load(f)

    count = 0
    for comp in data['components']:
        if 'allowed_layers' in comp:
            del comp['allowed_layers']
            count += 1
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
        
    print(f"Removed allowed_layers from {count} components.")

if __name__ == "__main__":
    refactor_components()
