import os
import ast
import csv

DEAD_FILES_PATH = r"c:\Dev\Starship Battles\dead_code_candidates.txt"
ORPHANED_TESTS_PATH = r"c:\Dev\Starship Battles\orphaned_tests.txt"
OUTPUT_CSV = r"c:\Dev\Starship Battles\audit_results_D.csv"
REPO_ROOT = r"c:\Dev\Starship Battles"

def get_dead_files():
    if not os.path.exists(DEAD_FILES_PATH):
        return set()
    with open(DEAD_FILES_PATH, 'r', encoding='utf-8') as f:
        return set(line.strip().lower() for line in f if line.strip())

def get_orphaned_tests():
    tests = []
    if not os.path.exists(ORPHANED_TESTS_PATH):
        return []
    
    try:
        with open(ORPHANED_TESTS_PATH, 'r', encoding='utf-16') as f:
            content = f.read()
    except UnicodeError:
        try:
            with open(ORPHANED_TESTS_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeError:
             with open(ORPHANED_TESTS_PATH, 'r', encoding='latin-1') as f:
                content = f.read()

    for line in content.splitlines():
        line = line.strip()
        if line.startswith("Orph: "):
            path = line[6:].strip()
            tests.append(path)
    return tests

def find_sut(test_path):
    """
    Naive SUT finder. Looks for imports from game.*
    Returns a list of potential SUT paths.
    """
    suts = []
    try:
        with open(test_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=test_path)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith('game'):
                    # Convert module path to file path
                    # game.core.config -> game/core/config.py
                    module_parts = node.module.split('.')
                    rel_path = os.path.join(*module_parts) + ".py"
                    abs_path = os.path.join(REPO_ROOT, rel_path)
                    suts.append(abs_path)
                    
                    # Also check for package imports: game/core/config/__init__.py
                    abs_path_init = os.path.join(REPO_ROOT, os.path.join(*module_parts), "__init__.py")
                    suts.append(abs_path_init)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith('game'):
                         module_parts = alias.name.split('.')
                         rel_path = os.path.join(*module_parts) + ".py"
                         abs_path = os.path.join(REPO_ROOT, rel_path)
                         suts.append(abs_path)
                         
                         abs_path_init = os.path.join(REPO_ROOT, os.path.join(*module_parts), "__init__.py")
                         suts.append(abs_path_init)

    except Exception as e:
        # print(f"Error parsing {test_path}: {e}")
        pass
    return list(set(suts))

def main():
    dead_files = get_dead_files()
    orphans = get_orphaned_tests()
    
    results = []
    
    print(f"Auditing {len(orphans)} orphaned tests...")
    
    for test_path in orphans:
        verdict = "REVIEW"
        reason = "Manual review required"
        sut_path = "Unknown"
        
        if not os.path.exists(test_path):
             verdict = "DELETE"
             reason = "Test file not found"
             results.append([test_path, verdict, reason, sut_path])
             continue

        # Check for Legacy markers in filename
        filename = os.path.basename(test_path).lower()
        if "legacy" in filename or "old" in filename or "deprecated" in filename or "tmp" in filename:
            verdict = "DELETE" # Strong candidate for deletion if already orphaned
            reason = "Legacy naming convention"
        
        # Check imports (SUT)
        suts = find_sut(test_path)
        
        real_sut_found = False
        dead_sut_found = False
        
        found_suts = []

        if suts:
            for s in suts:
                if os.path.exists(s):
                    real_sut_found = True
                    found_suts.append(os.path.relpath(s, REPO_ROOT))
                    if s.lower() in dead_files:
                        dead_sut_found = True
                        sut_path = os.path.relpath(s, REPO_ROOT)
                        break # Stop if we found a dead SUT
            
            if found_suts:
                 sut_path = ";".join(found_suts)

        if dead_sut_found:
            verdict = "DELETE"
            reason = f"Tests dead code: {sut_path}"
        elif not real_sut_found and suts:
            # Imports exist but files don't.
            verdict = "DELETE"
            reason = "Imports missing files (Ghost test)"
        elif not suts:
            # No game imports found.
            # Might be testing utilities or self-contained.
            if verdict != "DELETE":
                verdict = "REVIEW"
                reason = "No SUT identified"
        
        # Write Result
        results.append([os.path.relpath(test_path, REPO_ROOT), verdict, reason, sut_path])

    # Write CSV
    file_exists = os.path.exists(OUTPUT_CSV)
    mode = 'a' if file_exists else 'w'
    
    with open(OUTPUT_CSV, mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["TestFilePath", "Verdict", "Reason", "SUT_Path"])
        writer.writerows(results)

    print(f"Audit complete. Processed {len(results)} tests. Results appended to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
