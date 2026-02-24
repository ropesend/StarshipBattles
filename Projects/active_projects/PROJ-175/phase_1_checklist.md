# Phase 1: JSON Quick Wins

**Goal:** Complete JSON standardization — eliminate all direct `json.load()`/`json.dump()` file I/O calls outside `json_utils.py`, tighten `json_utils` error handling, and clean up exception-only imports.

**Estimated effort:** 1-2 hours
**Risk:** VERY LOW — only 5 files, mechanical replacement, all in UI/strategy layer

## Pre-Phase
- [ ] Run full test suite, record baseline: `pytest tests/ -n 12`
- [ ] Record baseline: `grep -rn "json\.load\b\|json\.dump\b" game/ --include="*.py" | grep -v json_utils` (expect ~3 results)

## Task 1: Migrate formation_editor.py (2 operations)
- [ ] Read `game/ui/screens/formation_editor.py` — find `json.dump()` and `json.load()` calls
- [ ] Replace `json.dump(data, f, indent=4)` with `save_json(file_path, data)` (add `from game.core.json_utils import save_json`)
- [ ] Replace `json.load(f)` with `load_json(file_path)` or `load_json_required(file_path)` as appropriate
- [ ] Remove `with open(...)` wrapper (json_utils handles file open internally)
- [ ] Remove `import json` if no longer needed
- [ ] Run related tests: `pytest tests/ -k formation -n 4`

## Task 2: Migrate stats_config.py (1 operation)
- [ ] Read `game/ui/screens/builder/stats_config.py` — find `json.load()` call
- [ ] Replace `json.load(f)` with `load_json(file_path, default={})` (add `from game.core.json_utils import load_json`)
- [ ] Remove `with open(...)` wrapper
- [ ] Remove `import json` if no longer needed
- [ ] Run related tests: `pytest tests/ -k "stats_config or builder" -n 4`

## Task 3: Clean up exception-only imports (2 files)
- [ ] Read `game/strategy/systems/save_game_service.py` — find `import json`
- [ ] Change `import json` to `from json import JSONDecodeError`
- [ ] Update exception handler: `except json.JSONDecodeError` → `except JSONDecodeError`
- [ ] Read `game/strategy/systems/design_library.py` — same pattern
- [ ] Change `import json` to `from json import JSONDecodeError`
- [ ] Update exception handler: `except json.JSONDecodeError` → `except JSONDecodeError`
- [ ] Run: `pytest tests/ -k "save_game or design_library" -n 4`

## Task 4: Audit WorkshopDataLoader (1 file)
- [ ] Read `game/ui/screens/workshop_data_loader.py` — find all JSON file I/O
- [ ] Identify which `json.load()` calls should use `load_json()` or `load_json_required()`
- [ ] Migrate file I/O calls to json_utils (keep orchestration logic intact)
- [ ] Remove direct `import json` if no longer needed
- [ ] Run: `pytest tests/ -k workshop -n 4`

## Task 5: Tighten json_utils Error Handling (MOD-CORE-015)
- [ ] Read `game/core/json_utils.py`
- [ ] In `load_json()`: Add `PermissionError` catch between `FileNotFoundError` and `IOError`:
  ```python
  except PermissionError as e:
      log_error(f"Permission denied reading {file_path}: {e}")
      return default
  ```
- [ ] In `load_json()`: Rename `IOError` to `OSError` for clarity (they're the same, but `OSError` is canonical)
- [ ] In `save_json()`: Add `PermissionError` catch, rename `IOError` to `OSError`
- [ ] Run json_utils tests: `pytest tests/ -k json_utils -n 4`

## Verification
- [ ] Verify zero direct file I/O: `grep -rn "json\.load\b\|json\.dump\b" game/ --include="*.py" | grep -v json_utils` returns nothing
- [ ] Verify no full `import json` (except json_utils itself and string-ops files): check results manually
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Confirm zero regressions vs. baseline

## Completion Checklist
- [ ] formation_editor.py migrated to json_utils
- [ ] stats_config.py migrated to json_utils
- [ ] save_game_service.py exception import cleaned up
- [ ] design_library.py exception import cleaned up
- [ ] workshop_data_loader.py migrated to json_utils
- [ ] json_utils error handling tightened (PermissionError, OSError)
- [ ] All tests pass
- [ ] Update plan.md Phase 1 status to "Complete"
