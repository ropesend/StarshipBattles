
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


def find_orphaned_tests(test_root, source_root):
    orphaned = []
    
    # Walk through the test directory
    for root, dirs, files in os.walk(test_root):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_path = os.path.join(root, file)
                
                # Determine relative path from test_root
                rel_path = os.path.relpath(root, test_root)
                
                # Construct expected source path
                # 1. basic mapping: test_foo.py -> foo.py
                source_file_name = file[5:] # remove test_
                
                potential_dependency_paths = []
                
                # Case 1: Direct mapping
                # tests/unit/core/test_config.py -> game/core/config.py
                p1 = os.path.join(source_root, rel_path, source_file_name)
                potential_dependency_paths.append(p1)
                
                # Case 2: Package mapping
                # tests/unit/core/test_config.py -> game/core/config/__init__.py
                # (unlikely but possible if config is a package)
                base_name = os.path.splitext(source_file_name)[0]
                p2 = os.path.join(source_root, rel_path, base_name, "__init__.py")
                potential_dependency_paths.append(p2)
                
                found = False
                for p in potential_dependency_paths:
                    if os.path.exists(p):
                        found = True
                        break
                
                if not found:
                    orphaned.append((test_path, potential_dependency_paths))

    return orphaned

if __name__ == "__main__":
    _root = _find_project_root()
    test_root = os.path.join(_root, "tests", "unit")
    source_root = os.path.join(_root, "game")

    start_dirs = [
        (test_root, source_root)
    ]

    print(f"Scanning for orphaned tests...")
    
    all_orphaned = []
    
    for t_root, s_root in start_dirs:
         if os.path.exists(t_root) and os.path.exists(s_root):
            orphans = find_orphaned_tests(t_root, s_root)
            all_orphaned.extend(orphans)
    
    print(f"Found {len(all_orphaned)} potentially orphaned tests.")
    for test, potential_sources in all_orphaned:
        print(f"Orph: {test}")
        # print(f"  Expected: {potential_sources[0]}")

