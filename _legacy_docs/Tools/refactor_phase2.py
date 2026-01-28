import os
import re

ROOT_DIR = r"c:\Dev\Starship Battles"
EXCLUDES = {'.git', '.vscode', '__pycache__', '.pytest_cache', 'assets'}

# Mapping of old module names to new import paths
# Key: Old module name
# Value: (New full dotted path, New module alias if any)
MAPPINGS = {
    'game_constants': ('game.core.constants', None),
    'logger': ('game.core.logger', None),
    'profiling': ('game.core.profiling', None),
    'physics': ('game.engine.physics', None),
    'spatial': ('game.engine.spatial', None),
    'collision_system': ('game.engine.collision', None),
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
        original_line = line
        
        # 1. Handle "import X" -> "from game.core import X as X" (or similar)
        # We need to be careful. "import game_constants" -> "from game.core import constants as game_constants"
        # because the code uses "game_constants.SCREEN_WIDTH". 
        # So alias is CRITICAL to avoid mass refactoring of usage sites.
        
        # Regex for "import module" or "import module as alias"
        # We only really care about the modules in our mapping.
        
        for old_mod, (new_pkg, alias_suggestion) in MAPPINGS.items():
            # Pattern 1: exact "import X"
            # We want to replace it with "from package.sub import module as X"
            # This preserves "X.attr" usage.
            # Example: "import game_constants" -> "from game.core import constants as game_constants"
            
            # Extract the leaf module name from new_pkg (e.g. 'constants' from 'game.core.constants')
            leaf_name = new_pkg.split('.')[-1]
            if leaf_name == old_mod:
                 # If name didn't change (e.g. pure move), "from game.core import logger" is fine IF usage was "logger.x"
                 replacement = f"from {new_pkg.rsplit('.', 1)[0]} import {leaf_name}"
            else:
                 # Name changed (e.g. game_constants -> constants).
                 # Must alias back to old name to preserve "game_constants.X" usage
                 replacement = f"from {new_pkg.rsplit('.', 1)[0]} import {leaf_name} as {old_mod}"
            
            # Regex: ^\s*import game_constants(\s*#.*)?$
            pattern_import_pure = re.compile(rf'^\s*import\s+{old_mod}(\s*#.*)?$')
            if pattern_import_pure.match(line):
                line = re.sub(rf'import\s+{old_mod}', replacement, line)
                modified = True
                continue

            # Pattern 2: "from X import Y"
            # "from game_constants import SCREEN_WIDTH" -> "from game.core.constants import SCREEN_WIDTH"
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
