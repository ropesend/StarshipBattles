
import os
import re

# We simply want to add one more os.path.dirname wrap to the existing sys.path hack
# Pattern: sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Target: sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return

    # Naive string replace might safeguard against regex complexity
    # But usually whitespace matters.
    # Regex for flexible whitespace:
    # sys\.path\.append\(\s*os\.path\.dirname\(\s*os\.path\.dirname\(\s*os\.path\.abspath\(__file__\)\)\)\)
    
    pattern = r'sys\.path\.append\(\s*os\.path\.dirname\(\s*os\.path\.dirname\(\s*os\.path\.abspath\(__file__\)\s*\)\s*\)\s*\)'
    replacement = 'sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        print(f"Updating path depth in {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

def main():
    # Only target unit_tests folder (which we will move to tests/unit)
    target_dir = r"c:\Dev\Starship Battles\unit_tests"
    
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.py'):
                process_file(os.path.join(root, file))

    # Also simulation_tests ? 
    # Check simulation_tests depth.
    # simulation_tests/data_driven/test_... usually 2 levels deep relative to root?
    # root/simulation_tests/data_driven/test.py -> dirname(dirname(dirname(file)))? 
    # If moved to tests/integration/data_driven/test.py -> One more level.
    
    target_dir_sim = r"c:\Dev\Starship Battles\simulation_tests"
    for root, dirs, files in os.walk(target_dir_sim):
        for file in files:
            if file.endswith('.py'):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
