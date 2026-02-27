# Phase 1: Delete Deprecated API

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-181 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove `get_default_registries()`, `set_default_registries()`, and `_default_registries` from registry.py and all exports. Update composition roots.

---

## Tasks

### Task 1.1: Remove deprecated functions from registry.py [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/ -x` (expect failures until callers updated in Phase 2)

- [x] Delete `_default_registries: Optional[GameRegistries] = None` (line 81)
- [x] Delete `set_default_registries()` function (lines 84-104)
- [x] Delete `get_default_registries()` function (lines 107-134)
- [x] Remove `'get_default_registries'` from `__all__` (line 38)
- [x] Remove `'set_default_registries'` from `__all__` (line 39)

**Notes:** Complete - all deprecated code removed from registry.py

### Task 1.2: Remove deprecated exports from core __init__.py [Simple]
**File:** `game/core/__init__.py`
**Tests:** `pytest tests/unit/core/ -x`

- [x] Remove `get_default_registries,` from import block (line 74)
- [x] Remove `set_default_registries,` from import block (line 75)
- [x] Remove `'get_default_registries', 'set_default_registries',` from `__all__` (line 134)

**Notes:** Complete - exports removed

### Task 1.3: Update root conftest.py composition root [Medium]
**File:** `conftest.py`
**Tests:** `pytest tests/unit/core/test_registry_provider.py -x`

- [x] Remove `set_default_registries` from import on line 8
- [x] Remove the `set_default_registries()` call block (lines 57-67: comments + with block)
- [x] Remove `import warnings` at top if no longer used elsewhere in file
- [x] Verify: `reset_game_state` fixture still hydrates RegistryManager and `DefaultRegistryProvider` reads from it

**Notes:** Complete - conftest.py now only hydrates RegistryManager, DefaultRegistryProvider reads from it

### Task 1.4: Update game/app.py composition root [Simple]
**File:** `game/app.py`
**Tests:** Manual - app startup (not testable in automated suite)

- [x] Remove `set_default_registries` from import statement
- [x] Remove the `set_default_registries()` call block (lines 130-133)
- [x] Remove `import warnings` if no longer used elsewhere in file
- [x] Keep `self.registries = GameRegistries(...)` (line 124-129) - still used directly by app

**Notes:** Complete - app.py composition root updated

### Task 1.5: Update simulation_tests/conftest.py [Simple]
**File:** `simulation_tests/conftest.py`
**Tests:** `pytest simulation_tests/ --co` (collection only, callers fixed in Phase 2)

- [x] Remove `set_default_registries` import (if present)
- [x] Remove `get_default_registries` import (if present)
- [x] Remove the comment + `registries = GameRegistries(...)` block (lines 101-107)
- [x] Remove the `set_default_registries(registries)` call (line 108)

**Notes:** Complete - simulation_tests/conftest.py updated

### Task 1.6: Fix stale TYPE_CHECKING import [Simple]
**File:** `game/simulation/services/design_loader.py`
**Tests:** `pytest tests/unit/simulation/services/test_simulation_design_loader.py -x`

- [x] Change line 28 from `from game.core.registries import GameRegistries` to `from game.core.registry import GameRegistries`

**Notes:** Complete - typo fixed

---

## Additional Test File Updates (discovered during execution)

Phase 1 also required updating test files that imported the deprecated functions:

- [x] `tests/unit/core/registry/conftest.py` - Removed `_default_registries` save/restore
- [x] `tests/unit/core/registry/test_registry_features.py` - Deleted `TestDefaultRegistries` class
- [x] `tests/unit/core/test_protocols_boundary.py` - Use `get_default_registry_provider()`
- [x] `tests/unit/entities/test_ship_di.py` - Removed cleanup fixture
- [x] `tests/unit/entities/test_component_di.py` - Removed cleanup fixture
- [x] `tests/unit/builder/test_fleet_composition.py` - Removed setup fixture
- [x] `tests/unit/ui/services/test_design_loader_adapter.py` - Removed deprecated call
- [x] `tests/unit/builder/test_workshop_context_di.py` - Use `get_default_registry_provider()`
- [x] `tests/regression/test_deprecated_code_removed.py` - Updated to verify functions are removed

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12` to verify no regressions from API deletion
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2

**Test Results:** 12373 passed, 1 skipped (down from 12375 - deleted 2 deprecated tests)
