import os
import sys
import re
from pathlib import Path
from collections import defaultdict


def _find_project_root():
    """Find project root by looking for game/ and data/ directories."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


_PROJECT_ROOT = _find_project_root()
sys.path.insert(0, str(_PROJECT_ROOT))

from game.core.paths import Paths

game_dir = Path(Paths.GAME_DIR)

# Collect all module files (relative to game/)
all_modules = {}
for py_file in sorted(game_dir.rglob("*.py")):
    rel = py_file.relative_to(game_dir)
    # Convert to module name
    module_name = str(rel).replace("\\", "/").replace(".py", "")
    if module_name.endswith("/__init__"):
        module_name = module_name[:-9]  # Remove /__init__
    all_modules[module_name] = py_file

# Track which modules import which
imported_by = defaultdict(list)

# Parse imports
for module_name, py_file in all_modules.items():
    try:
        content = py_file.read_text(encoding='utf-8')
        
        # Find imports: "from X import" or "import X"
        # Handle both "from game.X" and relative "from X"
        imports = set()
        
        # Pattern 1: from game.X import Y
        for m in re.finditer(r'from\s+game\.(\w+[\w./]*?)\s+import', content):
            imports.add(m.group(1).replace("/", ".").split(".")[0])
        
        # Pattern 2: from .X import or from ..X import (relative)
        # Pattern 3: import game.X
        for m in re.finditer(r'import\s+game\.(\w+[\w./]*?)(?:\s|$)', content):
            imports.add(m.group(1).replace("/", ".").split(".")[0])
        
        # Track imports
        for imp in imports:
            # Normalize
            imp_norm = imp.replace("/", ".").replace("\\", ".")
            if imp_norm in all_modules or any(m.startswith(imp_norm + ".") for m in all_modules):
                if imp_norm in all_modules:
                    imported_by[imp_norm].append(module_name)
    except:
        pass

# Find orphaned modules (not imported, excluding special cases)
orphaned = []
for module_name in sorted(all_modules.keys()):
    # Skip app.py, __init__ files, and things already imported
    if module_name == "app":
        continue
    if module_name in imported_by:
        continue
    if module_name.endswith("__init__"):
        continue
    
    orphaned.append(module_name)

print(f"Orphaned modules: {len(orphaned)}")
for mod in orphaned[:50]:
    print(f"  {mod}")
    
if len(orphaned) > 50:
    print(f"  ... and {len(orphaned) - 50} more")

