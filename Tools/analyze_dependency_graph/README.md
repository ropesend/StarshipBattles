# Analyze Dependency Graph

Finds potentially dead production code by building an import dependency graph from application entry points.

## Purpose

Identifies Python source files under `game/` that are not reachable through the import chain starting from the application's entry points (`launcher.py` and `game/app.py`). These unreachable files are candidates for removal. Useful during refactoring to find unused modules.

## Requirements

No additional dependencies beyond the base project.

## Usage

```bash
python Tools/analyze_dependency_graph/analyze_dependency_graph.py
```

No arguments. Entry points and project root are auto-detected.

## How It Works

1. **Entry points** -- Starts from `launcher.py` and `game/app.py`.
2. **BFS traversal** -- Parses each file's AST to extract `import` and `from ... import` statements, resolves them to file paths, and follows the chain.
3. **All source files** -- Collects every `.py` file under the project root (excluding `tests/`, `simulation_tests/`, `venv/`, `.git/`, `__pycache__/`).
4. **Diff** -- Files present on disk but not reached by the import graph are flagged as potentially dead.

## Output

Prints a summary to stdout and writes the full list to `dead_code_candidates.txt` in the current working directory:

```
Building dependency graph...
Reachable files: 180
Total source files (excluding tests): 195
Potentially Dead Files: 15

--- Top 20 Potentially Dead Files ---
game/core/old_utility.py
game/simulation/unused_system.py
...
```

## Limitations

- Does not resolve dynamic imports (`importlib.import_module`, `__import__`).
- Does not follow string-based module references (e.g., registry lookups by name).
- Relative imports with complex package structures may not fully resolve.
- Files only reachable through test code, scripts, or data-driven loading will appear as false positives.
