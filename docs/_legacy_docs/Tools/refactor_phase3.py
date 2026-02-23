import os
import re

ROOT_DIR = r"c:\Dev\Starship Battles"
EXCLUDES = {'.git', '.vscode', '__pycache__', '.pytest_cache', 'assets'}

# Mapping of old module names to new import paths
MAPPINGS = {
    'components': ('game.simulation.components.component', None),
    'abilities': ('game.simulation.components.abilities', None),
    'component_modifiers': ('game.simulation.components.modifiers', None),
    'resources': ('game.simulation.systems.resource_manager', None),
    'ship': ('game.simulation.entities.ship', None),
    'projectiles': ('game.simulation.entities.projectile', None),
    'battle_engine': ('game.simulation.systems.battle_engine', None),
    'ship_io': ('game.simulation.systems.persistence', None),
}

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print(f"Skipping binary file: {filepath}")
        return

    new_lines = []
    modified = False
    
    for line in lines:
        for old_mod, (new_pkg, alias_suggestion) in MAPPINGS.items():
            
            # Logic:
            # 1. "import ship_io" -> "from game.simulation.systems import persistence as ship_io"
            # 2. "from ship_io import ShipIO" -> "from game.simulation.systems.persistence import ShipIO"
            
            leaf_name = new_pkg.split('.')[-1]
            
            # Case 1: Pure Import "import X"
            pattern_import = re.compile(rf'^\s*import\s+{old_mod}(\s*#.*)?$')
            if pattern_import.match(line):
                # If name changed, use Alias; otherwise use simple import (if simpler) 
                # OR always use from ... import ... as ... to be safe and consistent.
                
                # Ex: import ship_io -> from game...systems import persistence as ship_io
                parent_pkg = new_pkg.rsplit('.', 1)[0]
                replacement = f"from {parent_pkg} import {leaf_name} as {old_mod}"
                
                line = re.sub(rf'import\s+{old_mod}', replacement, line)
                modified = True
                continue

            # Case 2: From Import "from X import Y"
            pattern_from = re.compile(rf'^\s*from\s+{old_mod}\s+import')
            if pattern_from.match(line):
                line = re.sub(rf'from\s+{old_mod}\s+import', f"from {new_pkg} import", line)
                modified = True
                continue
                
        new_lines.append(line)

    if modified:
        print(f"Refactoring imports in {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDES]
        
        for file in files:
             if file.endswith('.py'):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
