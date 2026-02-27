import os
import re

target_dir = r"c:\Dev\Starship Battles"
output_file = r"C:\Dev\Starship Battles\found_exceptions_all.txt"

pattern = re.compile(r"raise\s+(ValueError|RuntimeError)\b")
exclude_dirs = {"Reviews", "Projects", "tests", "simulation_tests", ".git", ".pytest_cache", ".agent", ".vscode", "__pycache__"}

results = []

for root, dirs, files in os.walk(target_dir):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    for i, line in enumerate(file):
                        if pattern.search(line):
                            rel_path = os.path.relpath(path, target_dir)
                            results.append(f"{rel_path}:{i+1} : {line.strip()}")
            except Exception as e:
                pass

with open(output_file, "w", encoding="utf-8") as out:
    out.write("\n".join(results))
print(f"Found {len(results)} instances.")
print(f"Found {len(results)} instances.")
