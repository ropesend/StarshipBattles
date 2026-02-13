import os
import ast
import re

DEAD_CODE_FILE = r"c:\Dev\Starship Battles\dead_code_candidates.txt"
TEST_DIR = r"c:\Dev\Starship Battles\tests\unit\ui"
ROOT_DIR = r"c:\Dev\Starship Battles"

def load_dead_code_list():
    with open(DEAD_CODE_FILE, 'r') as f:
        # Normalize paths to lowercase and standard separators
        return {os.path.normpath(line.strip()).lower() for line in f if line.strip()}

def resolve_import_to_path(module_name):
    # module_name: game.ui.orchestration.battle_orchestrator
    # path: c:\Dev\Starship Battles\game\ui\orchestration\battle_orchestrator.py
    rel_path = module_name.replace('.', os.sep) + ".py"
    abs_path = os.path.join(ROOT_DIR, rel_path)
    return os.path.normpath(abs_path)

def check_legacy_markers(name, content=None):
    markers = ["Legacy", "Old", "Deprecated", "V1", "Tmp"]
    for m in markers:
        if m.lower() in name.lower():
            return m
        if content and m.lower() in content.lower() and f"class {m}" in content: # heuristic for class names
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
        # Fallback to regex if AST fails (e.g. syntax error in test file?)
        pass
    return imports, content

def audit_file(file_path, dead_code_set):
    rel_path = os.path.relpath(file_path, ROOT_DIR).replace("\\", "/")
    
    # Check filename for legacy
    filename = os.path.basename(file_path)
    legacy_marker = check_legacy_markers(filename)
    if legacy_marker:
        return f"{rel_path},REVIEW,Filename contains '{legacy_marker}',"

    # function to normalize path for comparison
    def norm(p): return os.path.normpath(p).lower()

    imports, content = get_imports(file_path)
    
    suts = []
    
    for imp in imports:
        # We are looking for imports starting with 'game.' usually
        if imp.startswith('game.'):
            path = resolve_import_to_path(imp)
            suts.append(path)
            if norm(path) in dead_code_set:
                rel_sut = os.path.relpath(path, ROOT_DIR).replace("\\", "/")
                return f"{rel_path},DELETE,Tests dead code: {rel_sut},{rel_sut}"
    
    # Check for legacy content
    # legacy_in_content = check_legacy_markers("", content)
    # if legacy_in_content:
    #     return f"{rel_path},REVIEW,Content contains '{legacy_in_content}',"

    # If no issues found
    sut_str = ";".join([os.path.relpath(s, ROOT_DIR).replace("\\", "/") for s in suts[:1]]) # Just take first one for CSV simplicity
    return f"{rel_path},KEEP,Active test,{sut_str}"

def main():
    dead_code = load_dead_code_list()
    results = []
    
    for root, dirs, files in os.walk(TEST_DIR):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                full_path = os.path.join(root, file)
                result = audit_file(full_path, dead_code)
                results.append(result)
                print(result)

if __name__ == "__main__":
    main()
