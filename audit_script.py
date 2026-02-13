import os
import ast
import re

DEAD_CODE_FILE = r"c:\Dev\Starship Battles\dead_code_candidates.txt"
TEST_DIR = r"c:\Dev\Starship Battles\tests\unit\ui"
ROOT_DIR = r"c:\Dev\Starship Battles"
OUTPUT_FILE = r"c:\Dev\Starship Battles\audit_results_B.csv"

def load_dead_code_list():
    with open(DEAD_CODE_FILE, 'r') as f:
        return {os.path.normpath(line.strip()).lower() for line in f if line.strip()}

def resolve_import_to_path(module_name):
    rel_path = module_name.replace('.', os.sep)
    abs_path_py = os.path.join(ROOT_DIR, rel_path + ".py")
    abs_path_init = os.path.join(ROOT_DIR, rel_path, "__init__.py")
    
    if os.path.exists(abs_path_py):
        return os.path.normpath(abs_path_py)
    if os.path.exists(abs_path_init):
        return os.path.normpath(abs_path_init)
    return os.path.normpath(abs_path_py) # Default to .py if neither found, though checking existence is better

def check_legacy_markers(name, content=None):
    markers = ["Legacy", "Old", "Deprecated", "V1", "Tmp"]
    for m in markers:
        if m.lower() in name.lower():
            return m
        if content and m.lower() in content.lower() and f"class {m}" in content:
             return m
    return None

def get_imports(file_path):
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except Exception as e:
        content = ""
    return imports, content

def audit_file(file_path, dead_code_set):
    rel_path = os.path.relpath(file_path, ROOT_DIR).replace("\\", "/")
    
    filename = os.path.basename(file_path)
    legacy_marker = check_legacy_markers(filename)
    if legacy_marker:
        return f"{rel_path},REVIEW,Filename contains '{legacy_marker}',"

    def norm(p): return os.path.normpath(p).lower()

    imports, content = get_imports(file_path)
    
    suts = []
    verdict = "KEEP"
    reason = "Active test"

    # Prioritize finding dead code
    for imp in imports:
        if imp.startswith('game.'):
            path = resolve_import_to_path(imp)
            suts.append(path)
            if norm(path) in dead_code_set:
                verdict = "DELETE"
                rel_sut = os.path.relpath(path, ROOT_DIR).replace("\\", "/")
                reason = f"Tests dead code: {rel_sut}"
                return f"{rel_path},{verdict},{reason},{rel_sut}"
    
    sut_str = ";".join([os.path.relpath(s, ROOT_DIR).replace("\\", "/") for s in suts[:1]])
    return f"{rel_path},{verdict},{reason},{sut_str}"

def main():
    dead_code = load_dead_code_list()
    
    # Overwrite the file to start fresh
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("TestFilePath,Verdict,Reason,SUT_Path\n")

    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        for root, dirs, files in os.walk(TEST_DIR):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    full_path = os.path.join(root, file)
                    result = audit_file(full_path, dead_code)
                    if result:
                        f.write(result + "\n")
                        print(result)

if __name__ == "__main__":
    main()
