import os
import shutil
import re

SOURCE_DIR = "unit_tests"
DEST_DIR = "tests/unit"

def reorg():
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    # Walk source
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Calculate relative path
        rel_path = os.path.relpath(root, SOURCE_DIR)
        
        # Determine target dir
        target_dir = os.path.join(DEST_DIR, rel_path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_dir, file)
            
            # Move file
            shutil.move(src_file, dst_file)
            print(f"Moved {src_file} -> {dst_file}")
            
            if file.endswith(".py"):
                update_path_resolution(dst_file)

    # Remove empty source dir
    # shutil.rmtree(SOURCE_DIR) # Safer to keep empty or manual delete
    print("Reorg complete.")

def update_path_resolution(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern: dirname(dirname(abspath(__file__))) -> root (from unit_tests, depth 1)
    # Target: dirname(dirname(dirname(abspath(__file__)))) -> root (from tests/unit, depth 2)
    
    # We look for the standard boilerplate
    pattern_2 = r"os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)"
    replacement_3 = "os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"
    
    new_content = re.sub(pattern_2, replacement_3, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated path in {filepath}")

if __name__ == "__main__":
    reorg()
