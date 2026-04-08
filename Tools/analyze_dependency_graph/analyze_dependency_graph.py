
import ast
import os
import sys
from pathlib import Path


def _find_project_root():
    """Find project root by looking for game/ and data/ directories."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return str(current)
        current = current.parent
    raise RuntimeError("Could not find project root")


# Configuration
PROJECT_ROOT = _find_project_root()
ENTRY_POINTS = [
    os.path.join(PROJECT_ROOT, "launcher.py"),
    os.path.join(PROJECT_ROOT, "game", "app.py"),
]

# Add project root to sys.path for resolution simulation
sys.path.insert(0, PROJECT_ROOT)

def get_imports(file_path):
    """
    Parses a python file and returns a list of imported module names.
    Handles 'import x', 'import x as y', 'from x import y'.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)
    except Exception as e:
        # print(f"Error parsing {file_path}: {e}")
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                # from module import x
                # We need to handle 'from . import x' (relative imports)
                imports.append(node.module)
                # Note: We aren't capturing 'x' here, because file-level granularity is usually enough.
                # If 'from game.core import constants', we depend on game.core or game.core.constants
            else:
                # from . import x (level > 0)
                pass # Relative imports require context of the current file's package
    
    return imports

def resolve_import(import_name, current_file_path=None):
    """
    Attempts to resolve an import string to a file path.
    This is a simplified resolver and might not catch 100% of cases (namespace pkgs etc).
    """
    # 1. Try direct file match
    # import game.app -> game/app.py or game/app/__init__.py
    
    parts = import_name.split('.')
    potential_paths = [
        os.path.join(PROJECT_ROOT, *parts) + ".py",
        os.path.join(PROJECT_ROOT, *parts, "__init__.py")
    ]
    
    for p in potential_paths:
        if os.path.exists(p):
            return p
            
    # 2. Handle sub-packages (e.g. import game.core -> game/core/__init__.py)
    # Already covered by the second case above.
    
    return None

def resolve_relative_import(level, module, current_file_path):
    """
    Resolves . and .. imports
    """
    if not current_file_path:
        return None
        
    current_dir = os.path.dirname(current_file_path)
    
    # Go up 'level' times
    # level 1 = ., level 2 = ..
    target_dir = current_dir
    for _ in range(level - 1):
        target_dir = os.path.dirname(target_dir)
        
    if module:
        # from .sub import x
        parts = module.split('.')
        potential_paths = [
             os.path.join(target_dir, *parts) + ".py",
             os.path.join(target_dir, *parts, "__init__.py")
        ]
    else:
        # from . import x (implies importing from __init__.py of current pkg)
        potential_paths = [
            os.path.join(target_dir, "__init__.py")
        ]
        
    for p in potential_paths:
        if os.path.exists(p):
            return p
            
    return None

def find_reachable_files(entry_points):
    queue = list(entry_points)
    visited = set(entry_points)
    
    # BFS
    while queue:
        current_file = queue.pop(0)
        
        try:
            with open(current_file, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content, filename=current_file)
        except Exception:
            continue
            
        # Extract imports with AST
        for node in ast.walk(tree):
            resolved_path = None
            
            if isinstance(node, ast.Import):
                for alias in node.names:
                    resolved_path = resolve_import(alias.name)
                    if resolved_path and resolved_path not in visited:
                        visited.add(resolved_path)
                        queue.append(resolved_path)
                        
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:
                    # Relative import
                    resolved_path = resolve_relative_import(node.level, node.module, current_file)
                elif node.module:
                    # Absolute import
                    resolved_path = resolve_import(node.module)
                    
                    # Special case: from game.core.constants import GameState
                    # might be importing a class from a file.
                    # If resolve_import('game.core.constants') works, great.
                    # But sometimes we import 'game.core' and assume constants is in init.
                    pass
                
                if resolved_path and resolved_path not in visited:
                    visited.add(resolved_path)
                    queue.append(resolved_path)
    
    return visited

def get_all_python_files(root_dir):
    all_files = set()
    for root, dirs, files in os.walk(root_dir):
        # Skip hidden/venv/test dirs
        if "venv" in root or ".git" in root or "tests" in root or "simulation_tests" in root or "__pycache__" in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                all_files.add(os.path.join(root, file))
    return all_files

if __name__ == "__main__":
    print("Building dependency graph...")
    reachable = find_reachable_files(ENTRY_POINTS)
    print(f"Reachable files: {len(reachable)}")
    
    all_files = get_all_python_files(PROJECT_ROOT)
    print(f"Total source files (excluding tests): {len(all_files)}")
    
    dead_code = all_files - reachable
    print(f"Potentially Dead Files: {len(dead_code)}")
    
    print("\n--- Top 20 Potentially Dead Files ---")
    sorted_dead = sorted(list(dead_code))
    for f in sorted_dead[:20]:
        print(os.path.relpath(f, PROJECT_ROOT))
        
    # Save to file
    with open("dead_code_candidates.txt", "w") as f:
        for path in sorted_dead:
            f.write(path + "\n")
