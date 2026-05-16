# Phase 2: Major — inline-and-delete + small migrations

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-392 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Inline-and-delete a set of small wrappers (one wrapper, one task), and complete two small renames (`_menu_scene` → `menu_scene`, `_get_total_crew_requirement` → public). All tasks are independent and can run in any order.

---

## Tasks

### Task 2.1: Inline strategy_renderer image-load wrappers
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/ -k strategy_renderer`

- [x] Inline `_load_star_image` / `_load_planet_v3_image` / `_load_dyson_sphere_image` (lines 217-245) at their internal call sites in `StrategyRenderer`, OR change the import aliases at lines 55-63 so callers use the canonical names directly (LEG-01-006)
- [x] Delete the 3 wrapper methods (~9 LOC)
- [x] Verify: file no longer defines these wrapper methods

### Task 2.2: Inline quickstart_builder dir wrappers
**File:** `game/strategy/quickstart_builder.py`
**Tests:** `pytest tests/ -k quickstart_builder`

- [x] Inline `Paths.get_starter_races_dir()` at line 63 (replacing call to `get_quickstart_races_dir()`) (LEG-01-007)
- [x] Inline `Paths.get_starter_designs_dir()` at line 228 (replacing call to `get_quickstart_designs_dir()`) (LEG-01-007)
- [x] Delete the 2 module-level wrapper functions at lines 39-45
- [x] Verify: file has zero references to `get_quickstart_*_dir`

### Task 2.3: Inline `find_path_deep_space`
**File:** `game/strategy/services/galaxy_pathfinding_service.py`
**Tests:** `pytest tests/ -k galaxy_pathfinding`

- [x] Replace 7 internal call sites at lines 171, 175, 181, 196, 212, 217 with `hex_linedraw(start, end)` directly (LEG-01-009)
- [x] If `pathfinding.py:44` still calls `GalaxyPathfindingService.find_path_deep_space`, update it to call `hex_linedraw` directly
- [x] Delete `find_path_deep_space` static method at lines 61-64
- [x] Verify: `grep -rn "find_path_deep_space" .` returns zero hits

### Task 2.4: Migrate `priority_sort_key` to canonical
**File:** `game/simulation/entities/stat_contributors/command.py` and `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/ -k stat_contributors`

- [x] At `ship_stats.py:505`: replace `_cmd.priority_sort_key(c)` with `lookup_crew_priority(c)` (importing from `stat_contributors/registry.py`) (LEG-01-010)
- [x] In `command.py`: delete `priority_sort_key` wrapper at lines 36-38
- [x] Update test callers in `test_command.py` accordingly
- [x] Verify: `grep -rn "priority_sort_key" game/" returns zero hits

### Task 2.5: Rename `Game._menu_scene` to `Game.menu_scene`
**File:** `game/app.py`
**Tests:** `pytest tests/ -k app`

- [x] Rename property `_menu_scene` to `menu_scene` at lines 233-234 (LEG-02-015 UNCERTAIN-included)
- [x] Update the external caller at `app.py:449` (`_handle_strategy_action("quit_to_menu")`) to use the new name
- [x] Grep `tests/` for `_menu_scene` and update any usages
- [x] Verify: `grep -rn "\._menu_scene\b" game/ tests/` returns zero hits

### Task 2.6: Find-and-replace `get_asset_manager()` → `get_default_asset_manager()`
**File:** `game/assets/asset_manager.py` and all callers
**Tests:** `pytest tests/ --testmon`

- [x] Run `grep -rn "get_asset_manager\b" game/ tests/ combat_lab/` to enumerate callers
- [x] Replace each `get_asset_manager()` call with `get_default_asset_manager()` (LEG-03-010 INFO-included)
- [x] Delete `get_asset_manager()` 1-line alias at `asset_manager.py:348`
- [x] Verify: `grep -rn "get_asset_manager\b" .` returns zero hits

### Task 2.7: Inline `_get_sector_text` instance wrapper
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/ -k empire_build_queue`

- [x] Replace the 1 internal call site of `self._get_sector_text(...)` with the direct module function `get_sector_text(...)` (LEG-03-014)
- [x] Delete the instance method `_get_sector_text` at line 589
- [x] Verify: file no longer defines `_get_sector_text`

### Task 2.8: Rename `_get_total_crew_requirement` to public, drop `get_crew_required` wrapper
**File:** `game/ui/screens/builder/stat_getters.py`
**Tests:** `pytest tests/ -k stat_getters`

- [x] Rename private helper `_get_total_crew_requirement` to public `get_total_crew_requirement` (LEG-03-016 INFO-included)
- [x] Update the dispatch registry to point at the new public name
- [x] Delete the `get_crew_required(ship)` 1-line wrapper at line 66
- [x] Update other callers of `_get_total_crew_requirement` (`crew_validator`, `life_support_validator`)
- [x] Verify: `grep -rn "_get_total_crew_requirement\|get_crew_required" .` returns zero hits

### Task 2.9: Migrate `NewGameSetupScreen` static wrapper callers to controller
**File:** `game/ui/screens/new_game_setup_screen.py` (+ 2 callers)
**Tests:** `pytest tests/ -k new_game_setup`

- [x] Identify the 2 callers of `NewGameSetupScreen.validate_save_name` / `NewGameSetupScreen.generate_default_save_name` (likely tests)
- [x] Migrate each caller to call `NewGameSetupController.validate_save_name(...)` / `NewGameSetupController.generate_default_save_name(...)` directly (LEG-04-006)
- [x] Delete the 2 static wrapper methods on `NewGameSetupScreen` at lines 701-720
- [x] Verify: `grep -rn "NewGameSetupScreen.validate_save_name\|NewGameSetupScreen.generate_default_save_name" .` returns zero hits

### Task 2.10: Final regression
**File:** —
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run full sharded suite — confirm baseline preserved
- [x] Verify: pytest passes; aggregate grep across all targeted symbols returns zero hits

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
