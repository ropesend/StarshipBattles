import os
import glob
from pathlib import Path

def analyze_codebase(root_path):
    stats = []
    
    # Walk through all python files
    for path in Path(root_path).rglob('*.py'):
        if 'venv' in str(path) or '.git' in str(path) or 'Reviews' in str(path):
            continue
            
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                line_count = len(lines)
                byte_size = path.stat().st_size
                stats.append({
                    'path': str(path),
                    'lines': line_count,
                    'bytes': byte_size
                })
        except Exception as e:
            print(f"Error reading {path}: {e}")

    # Sort by lines
    stats.sort(key=lambda x: x['lines'], reverse=True)
    
    return stats[:30]

if __name__ == "__main__":
    root = "c:/Developer/StarshipBattles"
    print(f"Analyzing {root}...")
    top_files = analyze_codebase(root)
    
    print("\nTop 30 Largest Python Files:")
    print("-" * 80)
    print(f"{'Lines':<10} | {'Path'}")
    print("-" * 80)
    for file in top_files:
        print(f"{file['lines']:<10} | {file['path']}")
