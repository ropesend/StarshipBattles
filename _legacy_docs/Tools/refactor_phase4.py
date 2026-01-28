import os
import re

ROOT_DIR = r"c:\Dev\Starship Battles"
EXCLUDES = {'.git', '.vscode', '__pycache__', '.pytest_cache', 'assets'}

MAPPINGS = {
    'ai': ('game.ai.controller', None),
    'ai_behaviors': ('game.ai.behaviors', None),
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
            
            leaf_name = new_pkg.split('.')[-1]
            
            # Case 1: Pure Import "import ai"
            pattern_import = re.compile(rf'^\s*import\s+{old_mod}(\s*#.*)?$')
            if pattern_import.match(line):
                parent_pkg = new_pkg.rsplit('.', 1)[0]
                replacement = f"from {parent_pkg} import {leaf_name} as {old_mod}"
                line = re.sub(rf'import\s+{old_mod}', replacement, line)
                modified = True
                continue

            # Case 2: From Import "from ai import AIController"
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
