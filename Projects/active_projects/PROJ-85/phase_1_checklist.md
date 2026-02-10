# Phase 1: Remove Module-Level Globals

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-85 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete the three dead module-level globals and clean up orphaned imports

---

## Tasks

### Task 1.1: Remove COMPONENT_REGISTRY and MODIFIER_REGISTRY [Simple]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/ -n 12`

- [x] Delete lines 77-82 (comment block + both global assignments):
  ```python
  # Convenience aliases for registry data (read-only references)
  # PROJ-42 Note: These module-level references are intentionally kept for UI hot-reload
  # functionality (see builder/main.py _reload_data). They provide mutable dict refs
  # that can be cleared.
  COMPONENT_REGISTRY = get_default_registry_provider().get_components()
  MODIFIER_REGISTRY = get_default_registry_provider().get_modifiers()
  ```
- [x] Verify: `get_default_registry_provider` import on line 65 is KEPT (still used by `load_components_data` line 544, `load_components` line 600, `load_modifiers` line 693)

**Notes:** Deleted 6 lines. Import kept as expected.

---

### Task 1.2: Remove VEHICLE_CLASSES and clean imports [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/ -n 12`

- [x] Delete lines 24-27 (comment block + global assignment):
  ```python
  # PROJ-42: Module-level VEHICLE_CLASSES kept for UI hot-reload compatibility.
  # This is the actual registry dict reference - UI uses it for in-place reload.
  # Internal Ship methods use self._registries.vehicle_classes instead.
  VEHICLE_CLASSES = get_default_registry_provider().get_vehicle_classes()
  ```
- [x] Modify line 11 — remove `get_default_registry_provider` from import:
  ```python
  # BEFORE:
  from game.core.registry import get_default_registry_provider, GameRegistries
  # AFTER:
  from game.core.registry import GameRegistries
  ```
- [x] Delete lines 14-15 (dead TYPE_CHECKING block):
  ```python
  if TYPE_CHECKING:
      pass  # GameRegistries imported above
  ```
- [x] Modify line 4 — remove `TYPE_CHECKING` from typing import:
  ```python
  # BEFORE:
  from typing import Callable, List, Dict, Tuple, Optional, Any, Union, Set, Iterator, TYPE_CHECKING
  # AFTER:
  from typing import Callable, List, Dict, Tuple, Optional, Any, Union, Set, Iterator
  ```

**Notes:** All 4 edits applied successfully.

---

### Task 1.3: Full Test Suite Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify: All 7353 tests pass (or current baseline)
- [x] Grep confirmation: `COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, `VEHICLE_CLASSES` have no runtime references in `game/` (only comments remain)

**Notes:** 7351 passed. Grep shows only documentation comments and file path constants.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to completion
