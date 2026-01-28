
import os
import re

MAPPINGS = [
    ("rendering", "game.ui.renderer.renderer"),
    ("builder_gui", "game.ui.screens.builder.main"),
    ("builder_components", "game.ui.screens.builder.legacy_components"), # renaming to legacy_components to avoid conflict? Or just components.
    ("formation_editor", "game.ui.screens.formation_editor"),
    ("ship_theme", "game.ui.renderer.ship_theme"),
    ("ui.colors", "game.ui.colors"),
    ("ui.components", "game.ui.widgets"), # renaming generics to widgets?
]
# Wait, builder_components.py is likely legacy specific builder parts.
# ui.components.py is generic widgets.

# Root directory
ROOT_DIR = r"c:\Dev\Starship Battles"

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return

    original_content = content
    
    for old, new in MAPPINGS:
        # 1. from old import
        pattern_from = r'from\s+' + re.escape(old) + r'\b'
        replacement_from = f'from {new}'
        content = re.sub(pattern_from, replacement_from, content)
        
        # 2. import old
        pattern_import = r'^import\s+' + re.escape(old) + r'\b'
        replacement_import = f'import {new} as {old}'
        content = re.sub(pattern_import, replacement_import, content, flags=re.MULTILINE)

        # 3. import old as X
        pattern_import_as = r'^import\s+' + re.escape(old) + r'\s+as\s+(\w+)'
        replacement_import_as = f'import {new} as \\1'
        content = re.sub(pattern_import_as, replacement_import_as, content, flags=re.MULTILINE)

    if content != original_content:
        print(f"Updating {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    skip_dirs = {'.git', '.vscode', '__pycache__', 'refactor_docs', '.pytest_cache'}
    
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith('.py'):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
