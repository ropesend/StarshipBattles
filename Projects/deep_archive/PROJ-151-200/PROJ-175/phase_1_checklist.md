# Phase 1: JSON Quick Wins

**Goal:** Complete JSON standardization — eliminate all direct `json.load()`/`json.dump()` file I/O calls outside `json_utils.py`, tighten `json_utils` error handling, and clean up exception-only imports.

**Estimated effort:** 1-2 hours
**Risk:** VERY LOW — only 5 files, mechanical replacement, all in UI/strategy layer

## Pre-Phase
- [x] Run full test suite, record baseline: `pytest tests/ -n 12` → 12023 passed, 1 skipped
- [x] Record baseline: `grep -rn "json\.load\b\|json\.dump\b" game/ --include="*.py" | grep -v json_utils` → 3 results

## Task 1: Migrate formation_editor.py (2 operations)
- [x] Read `game/ui/screens/formation_editor.py` — find `json.dump()` and `json.load()` calls
- [x] Replace `json.dump(data, f, indent=4)` with `save_json(file_path, data)` (add `from game.core.json_utils import save_json`)
- [x] Replace `json.load(f)` with `load_json(file_path)` or `load_json_required(file_path)` as appropriate
- [x] Remove `with open(...)` wrapper (json_utils handles file open internally)
- [x] Remove `import json` if no longer needed
- [x] Run related tests: `pytest tests/ -k formation -n 4`

## Task 2: Migrate stats_config.py (1 operation)
- [x] Read `game/ui/screens/builder/stats_config.py` — find `json.load()` call
- [x] Replace `json.load(f)` with `load_json(file_path, default={})` (add `from game.core.json_utils import load_json`)
- [x] Remove `with open(...)` wrapper
- [x] Remove `import json` if no longer needed
- [x] Run related tests: `pytest tests/ -k "stats_config or builder" -n 4`

## Task 3: Clean up exception-only imports (2 files)
- [x] Read `game/strategy/systems/save_game_service.py` — find `import json`
- [x] Change `import json` to `from json import JSONDecodeError`
- [x] Update exception handler: `except json.JSONDecodeError` → `except JSONDecodeError`
- [x] Read `game/strategy/systems/design_library.py` — same pattern
- [x] Change `import json` to `from json import JSONDecodeError`
- [x] Update exception handler: `except json.JSONDecodeError` → `except JSONDecodeError`
- [x] Run: `pytest tests/ -k "save_game or design_library" -n 4`

## Task 4: Audit WorkshopDataLoader (1 file)
- [x] Read `game/ui/screens/workshop_data_loader.py` — find all JSON file I/O
- [x] Identify which `json.load()` calls should use `load_json()` or `load_json_required()` — NONE (already uses loader functions)
- [x] Migrate file I/O calls to json_utils (keep orchestration logic intact) — N/A
- [x] Remove direct `import json` if no longer needed → Changed to `from json import JSONDecodeError`
- [x] Run: `pytest tests/ -k workshop -n 4`

## Task 5: Tighten json_utils Error Handling (MOD-CORE-015)
- [x] Read `game/core/json_utils.py`
- [x] In `load_json()`: Add `PermissionError` catch between `FileNotFoundError` and `IOError`
- [x] In `load_json()`: Rename `IOError` to `OSError` for clarity
- [x] In `save_json()`: Add `PermissionError` catch, rename `IOError` to `OSError`
- [x] Run json_utils tests: `pytest tests/ -k json_utils -n 4`

## Verification
- [x] Verify zero direct file I/O: `grep -rn "json\.load\b\|json\.dump\b" game/ --include="*.py" | grep -v json_utils` returns nothing
- [x] Verify no full `import json` (except json_utils itself and string-ops files): check results manually
- [x] Run full test suite: `pytest tests/ -n 12` → 12023 passed, 1 skipped
- [x] Confirm zero regressions vs. baseline ✓

## Completion Checklist
- [x] formation_editor.py migrated to json_utils
- [x] stats_config.py migrated to json_utils
- [x] save_game_service.py exception import cleaned up
- [x] design_library.py exception import cleaned up
- [x] workshop_data_loader.py exception import cleaned up (no file I/O needed - already uses loaders)
- [x] json_utils error handling tightened (PermissionError, OSError)
- [x] All tests pass
- [x] Update plan.md Phase 1 status to "Complete"

## Notes
- Updated 2 unit tests that mocked json.dump/load directly to mock json_utils functions instead
- workshop_data_loader.py already uses loader functions from other modules, only needed exception import cleanup
