# Phase 1: Delete Deprecated API

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-181 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove `get_default_registries()`, `set_default_registries()`, and `_default_registries` from registry.py and all exports. Update composition roots.

---

## Tasks

### Task 1.1: Remove deprecated functions from registry.py [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/ -x` (expect failures until callers updated in Phase 2)

- [ ] Delete `_default_registries: Optional[GameRegistries] = None` (line 81)
- [ ] Delete `set_default_registries()` function (lines 84-104)
- [ ] Delete `get_default_registries()` function (lines 107-134)
- [ ] Remove `'get_default_registries'` from `__all__` (line 38)
- [ ] Remove `'set_default_registries'` from `__all__` (line 39)

**Notes:**

### Task 1.2: Remove deprecated exports from core __init__.py [Simple]
**File:** `game/core/__init__.py`
**Tests:** `pytest tests/unit/core/ -x`

- [ ] Remove `get_default_registries,` from import block (line 74)
- [ ] Remove `set_default_registries,` from import block (line 75)
- [ ] Remove `'get_default_registries', 'set_default_registries',` from `__all__` (line 134)

**Notes:**

### Task 1.3: Update root conftest.py composition root [Medium]
**File:** `conftest.py`
**Tests:** `pytest tests/unit/core/test_registry_provider.py -x`

- [ ] Remove `set_default_registries` from import on line 8
- [ ] Remove the `set_default_registries()` call block (lines 57-67: comments + with block)
- [ ] Remove `import warnings` at top if no longer used elsewhere in file
- [ ] Verify: `reset_game_state` fixture still hydrates RegistryManager and `DefaultRegistryProvider` reads from it

**Notes:** The `DefaultRegistryProvider` wraps `RegistryManager`, so any code using `get_default_registry_provider()` already sees hydrated data without needing the deprecated setter.

### Task 1.4: Update game/app.py composition root [Simple]
**File:** `game/app.py`
**Tests:** Manual - app startup (not testable in automated suite)

- [ ] Remove `set_default_registries` from import statement
- [ ] Remove the `set_default_registries()` call block (lines 130-133)
- [ ] Remove `import warnings` if no longer used elsewhere in file
- [ ] Keep `self.registries = GameRegistries(...)` (line 124-129) - still used directly by app

**Notes:** `self.registries` is still created and passed to screens. The deprecated setter was only populating `_default_registries` which nothing will need after this project.

### Task 1.5: Update simulation_tests/conftest.py [Simple]
**File:** `simulation_tests/conftest.py`
**Tests:** `pytest simulation_tests/ --co` (collection only, callers fixed in Phase 2)

- [ ] Remove `set_default_registries` import (if present)
- [ ] Remove `get_default_registries` import (if present)
- [ ] Remove the comment + `registries = GameRegistries(...)` block (lines 101-107)
- [ ] Remove the `set_default_registries(registries)` call (line 108)

**Notes:** simulation_tests callers of `get_default_registries()` will be migrated in Phase 2 Task 2.1.

### Task 1.6: Fix stale TYPE_CHECKING import [Simple]
**File:** `game/simulation/services/design_loader.py`
**Tests:** `pytest tests/unit/simulation/services/test_simulation_design_loader.py -x`

- [ ] Change line 28 from `from game.core.registries import GameRegistries` to `from game.core.registry import GameRegistries`

**Notes:** The module `game.core.registries` does not exist. This was always a typo hidden behind TYPE_CHECKING guard.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` to verify no regressions from API deletion
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
