import ast
import os
import glob
import sys
import re

TARGET_DIR = r"c:\Dev\Starship Battles\tests\repro_issues"

def get_ast_nodes(source):
    tree = ast.parse(source)
    classes = {}
    
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            setup_class = None
            setup = None
            teardown_class = None
            
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    if child.name == 'setUpClass':
                        setup_class = child
                    elif child.name == 'setUp':
                        setup = child
                    elif child.name == 'tearDownClass':
                        teardown_class = child
            
            if setup_class:
                classes[node.name] = {
                    'setup_class': setup_class,
                    'setup': setup,
                    'teardown_class': teardown_class
                }
    return classes

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        source = "".join(lines)
        classes_info = get_ast_nodes(source)
        
        if not classes_info:
            return

        print(f"Migrating {filepath}...")
        
        # We process from bottom to top to keep line numbers valid?
        # Actually, string manipulation by lines is easier if we carefully track edits or just do one pass if no overlap.
        # But we might have multiple classes in one file.
        # Let's simple apply edits.
        
        # We will reconstruct the file.
        new_lines = list(lines)
        
        # Helper to comment out specific line ranges (to delete)
        # We replace with empty string or comment? Empty string is cleaner.
        
        for cls_name, nodes in classes_info.items():
            sc = nodes['setup_class']
            s = nodes['setup']
            tc = nodes['teardown_class']
            
            # 1. Handle tearDownClass (Always remove)
            if tc:
                # Remove decorators if any
                start = tc.lineno - 1 - len(tc.decorator_list)
                end = tc.end_lineno
                for i in range(start, end):
                    new_lines[i] = "" # Delete line

            # 2. Handle setUpClass
            if sc:
                sc_start = sc.lineno - 1
                sc_body_start = sc.body[0].lineno - 1
                sc_end = sc.end_lineno
                
                # Get body usage
                body_lines = lines[sc_body_start:sc_end]
                # Adjust indent processing if needed, but usually it fits.
                # Replace cls with self
                migrated_body = []
                for line in body_lines:
                    # Simple replace cls. with self. 
                    # Note: this might replace legitimate tokens, but in test context it's low risk.
                    # We only replace whole word 'cls'
                    l_new = re.sub(r'\bcls\b', 'self', line)
                    migrated_body.append(l_new)
                
                if s:
                    # Case A: Merge into existing setUp
                    # Remove original setUpClass
                    decor_start = sc_start - len(sc.decorator_list)
                    for i in range(decor_start, sc_end):
                        new_lines[i] = ""
                    
                    # Insert body into setUp
                    # Find where to insert (after def line)
                    s_def_line = s.lineno - 1
                    # Insert AFTER def line
                    # We append to that index in our list (inserting items shifts list? No, we shouldn't mod list in place while iterating indices)
                    # Actually, editing lines in place is hard if we add lines.
                    
                    # Better approach: Mark deletion regions and insertion points.
                    pass
                else:
                    # Case B: Rename
                    # Remove decorators
                    decor_start = sc_start - len(sc.decorator_list)
                    for i in range(decor_start, sc_start):
                        new_lines[i] = ""
                    
                    # Rename def
                    def_line = new_lines[sc_start]
                    new_lines[sc_start] = def_line.replace("setUpClass(cls)", "setUp(self)")
                    
                    # Body lines (cls->self)
                    for i in range(sc_body_start, sc_end):
                        new_lines[i] = re.sub(r'\bcls\b', 'self', new_lines[i])

        # If Case A involved (Insertion), we need to reconstruct.
        # Since inplace list mod is tricky, let's re-read and build output string.
        
        final_output = []
        
        # build a map of insertions: line_idx -> [lines to insert after]
        insertions = {}
        # build a set of deleted indices
        deletes = set()
        
        for cls_name, nodes in classes_info.items():
            sc = nodes['setup_class']
            s = nodes['setup']
            tc = nodes['teardown_class']
            
            if tc:
                start = tc.lineno - 1 - len(tc.decorator_list)
                end = tc.end_lineno
                for i in range(start, end):
                    deletes.add(i)
            
            if sc:
                sc_start = sc.lineno - 1
                sc_body_start = sc.body[0].lineno - 1
                sc_end = sc.end_lineno
                decor_start = sc_start - len(sc.decorator_list)
                
                body_lines = lines[sc_body_start:sc_end]
                migrated_body = [re.sub(r'\bcls\b', 'self', l) for l in body_lines]
                
                if s:
                    # Delete setUpClass
                    for i in range(decor_start, sc_end):
                        deletes.add(i)
                    
                    # Insert at setUp start
                    # s.lineno is "def setUp(self):"
                    # We want to insert AFTER this line.
                    insert_idx = s.lineno - 1
                    if insert_idx not in insertions:
                        insertions[insert_idx] = []
                    insertions[insert_idx].extend(migrated_body)
                else:
                    # Rename in place
                    # Delete decorators
                    for i in range(decor_start, sc_start):
                        deletes.add(i)
                    
                    # Rename def (handled in loop below by checking index)
                    # Body update (handled in loop below?)
                    pass

        # Construct file
        for i, line in enumerate(lines):
            # Check modification for Case B (Rename)
            found_rename = False
            for cls_name, nodes in classes_info.items():
                sc = nodes['setup_class']
                s = nodes['setup']
                if sc and not s:
                     if i == sc.lineno - 1:
                         final_output.append(line.replace("setUpClass(cls)", "setUp(self)"))
                         found_rename = True
                     elif sc.body[0].lineno - 1 <= i < sc.end_lineno:
                         final_output.append(re.sub(r'\bcls\b', 'self', line))
                         found_rename = True
            
            if found_rename:
                continue

            if i in deletes:
                continue
            
            final_output.append(line)
            
            if i in insertions:
                final_output.extend(insertions[i])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("".join(final_output))
            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    files = glob.glob(os.path.join(TARGET_DIR, "*.py"))
    # Exclude test_combat.py because we already did it manually
    files = [f for f in files if "test_combat.py" not in f]
    
    print(f"Found {len(files)} files to check in {TARGET_DIR}")
    for fp in files:
        process_file(fp)
