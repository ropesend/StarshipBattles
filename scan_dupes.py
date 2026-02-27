import os
import re

search_dir = r"c:\Dev\Starship Battles"
exclude_dirs = [".git", "__pycache__", ".agent", ".claude", "Projects", "Reviews", "docs", ".gemini", "tests", "venv", "env"]

# Patterns
font_pattern = re.compile(r'pygame\.font\.(?:SysFont|Font)')
color_pattern = re.compile(r'\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)|pygame\.Color')
vr_pattern = re.compile(r'ValidationResult\(')

results = {
    "fonts": [],
    "colors": [],
    "validation": []
}

for root, dirs, files in os.walk(search_dir):
    # Exclude directories
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            rel_path = os.path.relpath(path, search_dir)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f, 1):
                        # Fonts
                        if font_pattern.search(line):
                            results["fonts"].append(f"{rel_path}:{i} - {line.strip()}")
                        
                        # Colors: looking for variables assigned to RGB tuples, or pygame.Color
                        # Examples: WHITE = (255, 255, 255), color=(255,0,0)
                        if re.search(r'(?:color|colour|_) ?= ?\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)', line, re.IGNORECASE) or \
                           re.search(r'^[A-Z_0-9]+ ?= ?\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)', line.strip()) or \
                           'pygame.Color' in line:
                            
                            # Ignore some common non-color tuples like grid positions? (x, y, z)
                            # Actually RGB is 3-tuple.
                            results["colors"].append(f"{rel_path}:{i} - {line.strip()}")
                            
                        # ValidationResult
                        if vr_pattern.search(line):
                            results["validation"].append(f"{rel_path}:{i} - {line.strip()}")
            except Exception:
                pass

with open(r"c:\Dev\Starship Battles\scan_results.txt", "w", encoding="utf-8") as out:
    out.write("### FONT INITIALIZATIONS\n")
    for r in results["fonts"]: out.write(r + "\n")
    out.write(f"\nTotal Fonts: {len(results['fonts'])}\n\n")
    
    out.write("### COLOR DEFINITIONS\n")
    for r in results["colors"]: out.write(r + "\n")
    out.write(f"\nTotal Colors: {len(results['colors'])}\n\n")
    
    out.write("### VALIDATION RESULT BOILERPLATE\n")
    for r in results["validation"]: out.write(r + "\n")
    out.write(f"\nTotal ValidationResults: {len(results['validation'])}\n")
