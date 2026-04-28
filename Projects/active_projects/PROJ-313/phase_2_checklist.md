# Phase 2: Router OR-bridge

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-313 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Modify `StrategyEventRouter.has_modal_open()` and `_is_blocking_ui_element_at()` to OR the new `iter_live_modals()` walk with the existing slot scans. The modal list is still empty (no windows migrated yet), so this is a no-op behaviourally — but it prepares the router for incremental migration in Phases 3-7.

---

## Tasks

### Task 2.1: OR-bridge `has_modal_open()` [Simple]
**File:** `game/ui/screens/strategy_event_router.py` (lines 47-95)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_event_router.py tests/unit/ui/screens/test_strategy_window_manager_public_api.py`

- [x] Locate `has_modal_open()` (around line 47)
- [x] At the END of the existing chain (after the last `is not None` check), add a final clause:
  ```python
  if any(True for _ in self.window_manager.iter_live_modals()):
      return True
  return False
  ```
  Or refactor the existing return-True-on-first-hit pattern to: `if any(...): return True` for the new modal list, retaining all existing slot checks above it.
- [x] Verify no behavioural change — run targeted test before/after Task 2.1, assert same result.
**Notes:** The OR-bridge is a logical OR — slot checks AND the modal list both contribute. As windows migrate (Phases 3-7), each window-specific commit deletes its slot check from this method, leaving only the `iter_live_modals()` walk by Phase 8.

### Task 2.2: OR-bridge `_is_blocking_ui_element_at()` [Simple]
**File:** `game/ui/screens/strategy_event_router.py` (lines 499-517 per audit; verify exact range)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_event_router.py`

- [x] Locate `_is_blocking_ui_element_at(self, point)` (around line 499)
- [x] At the END of the existing chain, add the modal-list walk:
  ```python
  for w in self.window_manager.iter_live_modals():
      if w.rect.collidepoint(point):
          return True
  ```
  Or use `any(w.rect.collidepoint(point) for w in self.window_manager.iter_live_modals())` if the existing chain returns True early; otherwise append to the existing pattern matching the existing return convention.
- [x] Verify no behavioural change.
**Notes:**

### Task 2.3: Add invariant tests for OR-bridge correctness [Medium]
**File:** `tests/unit/ui/screens/test_strategy_event_router.py` (extend existing or add new test class)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_event_router.py -v -k or_bridge`

- [x] Test `test_has_modal_open_returns_true_when_only_modal_list_populated` — populate `_modals` directly with a stub window (no slot fields used), assert `has_modal_open() == True`
- [x] Test `test_has_modal_open_returns_true_when_only_slot_populated` — populate one slot field directly, assert `has_modal_open() == True`
- [x] Test `test_has_modal_open_returns_false_when_both_empty` — assert `has_modal_open() == False` when no slots and no modals
- [x] Mirror the same three tests for `_is_blocking_ui_element_at(point)` with appropriate rect setup
**Notes:** These tests pin the OR-bridge invariant during Phases 3-7 migration. They become irrelevant after Phase 8 (when slots are gone) — Phase 8 deletes them.

### Task 2.4: Verify baseline preserved [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run full sharded suite — assert 15893 + N tests passing (N = baseline + Phase 1 new + Phase 2 new)
- [x] No existing test breaks
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3 (Migrate event-listener-only windows)
