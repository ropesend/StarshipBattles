# Check Orphans

Finds Python modules under `game/` that are not imported by any other module in the codebase.

## Purpose

Identifies production modules that may be unused by scanning all import statements across the `game/` package. Unlike `analyze_dependency_graph` which traces from entry points, this tool checks whether each module is imported by at least one other module -- a simpler heuristic that catches modules disconnected from the internal import graph.

## Requirements

No additional dependencies beyond the base project.

## Usage

```bash
python Tools/check_orphans/check_orphans.py
```

No arguments. Scans the `game/` directory automatically.

## How It Works

1. **Collects** all `.py` files under `game/` and converts them to module names.
2. **Parses** import statements (`from game.X import ...` and `import game.X`) in every module using regex.
3. **Tracks** which modules are imported by at least one other module.
4. **Reports** modules that are never imported (excluding `app.py` and `__init__.py` files).

## Output

```
Orphaned modules: 5
  core/deprecated_helper
  simulation/old_calculator
  strategy/unused_service
  ui/legacy_renderer
  ui/debug_overlay
```

Shows the first 50 orphaned modules. If more exist, prints a count of the remainder.

## Limitations

- Uses regex-based import detection, not full AST parsing -- may miss complex import patterns.
- Only checks top-level package references (e.g., `from game.core import X` registers `core` as imported, not `core/specific_module`).
- Modules loaded dynamically, via registry lookups, or only referenced from tests/scripts will appear as false positives.
- Does not check `__init__.py` files or `app.py` (these are excluded by design).
