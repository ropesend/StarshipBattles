# Phase 2: design_role migration to RoleRegistry

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-278 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace the legacy `DesignRoleRegistry` class with a layered `RoleRegistry` instance loaded via a new `game/strategy/data/design_role_registry.py` module. Port `data/design_roles.json` to the new format. Migrate all production call sites and the existing test file. Delete `DesignRoleRegistry` and its singleton accessor.

**User decisions (locked) for Phase 2:**
1. Port `data/design_roles.json` to new shape (don't extend loader)
2. Delete `DesignRoleRegistry` and migrate all call sites (no compat shim)
3. Add `load_from_file_optional` to `RoleRegistry` for the user-overlay path

---

## Prerequisites

- Phase 1 complete (`Role`, `RoleRegistry`, `RoleRegistryReadOnlyError` shipped in `game/core/roles.py`)
- 3 production call sites identified (audit confirmed: 4 total grep hits, but `design_role.py` itself was the registry definition — leaving 3 actual consumers):
  - [game/ui/screens/design_selector_window.py](../../../game/ui/screens/design_selector_window.py) (lines 288-289, 324-326)
  - [game/ui/screens/builder/right_panel.py](../../../game/ui/screens/builder/right_panel.py) (lines 397-399)
  - [game/ui/screens/workshop_event_router.py](../../../game/ui/screens/workshop_event_router.py) (lines 509-512)
- 1 test file to migrate: [tests/unit/strategy/data/test_design_role_registry.py](../../../tests/unit/strategy/data/test_design_role_registry.py) (225 lines)
- Methods used by callers: `get_roles_for_vehicle_type(vehicle_type)`, `get_role_name(role_id)`, `get_role_id_by_name(display_name)`

---

## Tasks

### Task 2.1: Add `load_from_file_optional` to RoleRegistry [Simple]
**File:** `game/core/roles.py`, `tests/unit/core/test_role_registry.py`
**Tests:** `pytest tests/unit/core/test_role_registry.py`

- [x] Write test: `load_from_file_optional(missing_path, source_tag)` returns silently (no roles loaded)
- [x] Write test: `load_from_file_optional(valid_path, source_tag)` loads roles same as `load_from_file`
- [x] Write test: `load_from_file_optional(malformed_path, source_tag)` STILL raises `json.JSONDecodeError` (only existence is tolerated)
- [x] Run tests — confirm they fail (red phase verified)
- [x] Implement `load_from_file_optional(path, source_tag)`
- [x] Re-run tests — confirm pass

**Notes:** Added a 4th test (`load_from_file_optional` does NOT fire invalidation — same as `load_from_file`, since both are initialization not mutation). All 4 pass.

### Task 2.2: Add `get_roles_for_vehicle_type` query method to RoleRegistry [Simple]
**File:** `game/core/roles.py`, `tests/unit/core/test_role_registry.py`
**Tests:** `pytest tests/unit/core/test_role_registry.py`

- [x] Write test: roles with empty `vehicle_type_filter` match ANY vehicle type
- [x] Write test: roles with non-empty `vehicle_type_filter` match only vehicle types in the filter
- [x] Write test: result is sorted by `display_name` (matches legacy ordering)
- [x] Write test: returns empty list when no roles match
- [x] Implement `get_roles_for_vehicle_type(vehicle_type: str) -> List[Role]`
- [x] Run tests — confirm pass

**Notes:** Added a 5th test (mix of filtered + unfiltered roles in same registry). All 5 pass. Total RoleRegistry test count after Tasks 2.1+2.2: 29.

### Task 2.3: Port `data/design_roles.json` to new shape [Medium]
**File:** `data/design_roles.json`
**Tests:** None directly (validated by Task 2.5 integration test)

- [x] Read existing file — note all 27 role definitions (initial estimate of "11" was wrong)
- [x] Convert to new shape `{"roles": [{...}, ...]}`
- [x] Field renames: `name` → `display_name`, `allowed_vehicle_types` → `vehicle_type_filter`
- [x] Verify JSON parses (sanity check via `json.load`)
- [x] Verify all 27 roles preserved (no data loss; unique IDs confirmed)

**Notes:** Actual role count was 27 (not 28 as the conventions doc claimed). Doc updated in Task 2.11.

### Task 2.4: Create `design_role_registry.py` module + module-level accessor [Medium]
**File:** `game/strategy/data/design_role_registry.py` (NEW), `tests/unit/strategy/data/test_design_role_registry_loader.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_design_role_registry_loader.py`

- [x] Write tests for `get_default_*`, `set_default_*`, `reset_default_*` accessor pattern (with autouse fixture for clean state)
- [x] Implement module per pattern of other context-managed services
- [x] Add `Paths.USER_DESIGN_ROLES_FILE` constant (= `output/design_roles_overlay.json`)
- [x] Add `Paths.MODS_DIR` constant (= `mods/` at project root)
- [x] Layered loader: base (required) → mods/* (optional dir) → user overlay (optional file)
- [x] Run tests — confirm pass (12/12)

**Notes:** User overlay path lives under `output/` (not `user_data/`) to match the project's existing convention for runtime/user data. Mods dir is `mods/` at project root.

### Task 2.5: Add integration test — production data file loads cleanly [Simple]
**File:** `tests/unit/strategy/data/test_design_role_registry_loader.py`
**Tests:** `pytest tests/unit/strategy/data/test_design_role_registry_loader.py`

- [x] Write tests for production data file loads cleanly (registry has roles, expected role IDs present, all roles have non-empty display_name + description, general_purpose accepts all vehicle types, get_roles_for_vehicle_type works)
- [x] Add layered-loading tests (user overlay overrides base via monkeypatch; missing user overlay silently ignored)
- [x] Run tests — confirm pass

**Notes:** Combined with Task 2.4. Includes 6 production-data smoke tests + 2 layered-loading tests. Total loader test count: 12.

### Task 2.6: Migrate `design_selector_window.py` call sites [Simple]
**File:** `game/ui/screens/design_selector_window.py`
**Tests:** Run `pytest tests/unit/ui/` after each file changed

- [x] Replace import: `from game.strategy.data.design_role import get_default_design_role_registry` → `from game.strategy.data.design_role_registry import get_default_design_role_registry`
- [x] Replace `registry.get_role_id_by_name(role_option)` with `next((r.id for r in registry.all() if r.display_name == role_option), None)`
- [x] Replace `registry.get_all_role_ids()` + `registry.get_role_name(role_id)` with `sorted(registry.all(), key=lambda r: r.display_name)` + `role.display_name`
- [x] Run targeted tests

**Notes:** Two migration sites in this file: `_refresh_designs` (filter dropdown selection→id lookup) and `_get_role_filter_options` (build display-name list). The first uses the inline `next(...)` reverse-lookup pattern; the second sorts roles by display_name for stable UI ordering.

### Task 2.7: Migrate `right_panel.py` call sites [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/ui/builder/`

- [x] Replace import to new module path
- [x] Update `roles[0]["name"]` → `roles[0].display_name`
- [x] Update `registry.get_role_name(curr_role_id)` → `registry.get(curr_role_id).display_name` with KeyError fallback to id
- [x] Run targeted tests

**Notes:** Added KeyError fallback because the new `RoleRegistry.get()` raises (dict-like) where the legacy `get_role_name` returned the id silently. Behaviorally equivalent.

### Task 2.8: Migrate `workshop_event_router.py` call sites [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Replace import to new module path
- [x] Replace `registry.get_role_id_by_name(selected_name)` with `next((r.id for r in registry.all() if r.display_name == selected_name), None)`
- [x] Run targeted tests

**Notes:** Single migration site (`_handle_role_dropdown`). The `if role_id:` guard already filters None returns, so the new pattern slots in cleanly.

### Task 2.9: Migrate `test_design_role_registry.py` to test the new loader [Medium]
**File:** `tests/unit/strategy/data/test_design_role_registry.py`
**Tests:** `pytest tests/unit/strategy/data/test_design_role_registry.py`

- [x] Update all imports to use new module path
- [x] Replace `DesignRoleRegistry()` instantiation pattern with `get_default_design_role_registry()`
- [x] Add `_reset_registry` autouse fixture for clean module state
- [x] Update `registry.get_all_role_ids()` → `[r.id for r in registry.all()]`
- [x] Update `registry.get_role_name(id)` → `registry.get(id).display_name`
- [x] Update `registry.get_role_id_by_name(name)` callers — use the inline next-comprehension pattern
- [x] Update `registry.get_roles_for_vehicle_type(vt)` consumers — return type changed from `List[Dict]` to `List[Role]`
- [x] Update unknown-role tests — new API raises `KeyError` (not silent return of id)
- [x] Keep `TestShipDesignRoleSerialization` class unchanged (Ship serialization is independent of registry)
- [x] Run tests — confirm pass (16/16)

**Notes:** `get_role_id_by_name` was NOT re-added to RoleRegistry — every caller migrated to the inline `next(...)` pattern. Cleaner than maintaining a one-line wrapper method.

### Task 2.10: Delete `DesignRoleRegistry` class + singleton from `design_role.py` [Simple]
**File:** `game/strategy/data/design_role.py`
**Tests:** `pytest tests/unit/strategy/data/`

- [x] Delete `class DesignRoleRegistry` (was lines 160-238)
- [x] Delete `_default_registry` module-level variable
- [x] Delete `get_default_design_role_registry()` function
- [x] Verify `DesignRole` enum + `classify_design_role()` + `classify_from_design_data()` + the `_*_ABILITIES` constants remain untouched
- [x] Update module docstring to point readers at the new module
- [x] Remove unused imports (`Optional`, `List`, `load_json`, `Paths`)
- [x] Grep `DesignRoleRegistry` repo-wide → only docstring breadcrumbs + test class name remain
- [x] Run regression: `pytest tests/unit/core/ tests/unit/strategy/data/test_design_role_registry.py tests/unit/strategy/data/test_design_role_registry_loader.py tests/unit/ui/` (4277 passed)

**Notes:** The 78 failures observed in `tests/unit/strategy/data/test_galaxy_cleanup.py` during a wider sweep are pre-existing (`AttributeError: 'Galaxy' object has no attribute '_spatial'`) and unrelated to PROJ-278.

### Task 2.11: Update documentation [Simple]
**File:** `docs/01_ARCHITECTURE.md`, `docs/systems/strategy_layer.md`, `docs/03_CONVENTIONS.md`
**Tests:** N/A

- [x] `docs/01_ARCHITECTURE.md` — package directory map for `game/strategy/data/` updated to mention `design_role_registry.py` (PROJ-278) with layered loading details; `design_role.py` row no longer claims to define `DesignRoleRegistry`
- [x] `docs/systems/strategy_layer.md` § "Design Roles" — full rewrite covering new file split (schema in `game/core/roles.py`, accessor in `game/strategy/data/design_role_registry.py`, classifier still in `design_role.py`); new field names (`display_name` / `vehicle_type_filter`); layered loading; runtime add semantics; new RoleRegistry API; reverse-lookup pattern
- [x] `docs/03_CONVENTIONS.md` — `data/design_roles.json` row updated with corrected role count (27, not 28) and reference to new loader module
- [x] Phase 2 design rationale captured in this checklist + decisions.md

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/core/` passes (Phase 1 tests still green)
- [x] `pytest tests/unit/strategy/data/test_design_role_registry.py tests/unit/strategy/data/test_design_role_registry_loader.py` passes (16 + 12 = 28 tests)
- [x] Targeted UI tests pass for the 3 migrated screens (covered by `tests/unit/ui/`)
- [x] Targeted regression sweep: `pytest tests/unit/core/ tests/unit/strategy/data/ tests/unit/ui/` returns 4277 passed (78 failures in `test_galaxy_cleanup.py` are pre-existing, unrelated)
- [x] Grep `DesignRoleRegistry` returns only docstring breadcrumbs + the now-generic test class name
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3 (Combat Lab scenario_role migration)
