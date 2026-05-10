# Phase 3: Reuse VirtualTable row pool across opens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-373 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (Phase 2 deferred — guard ships independently and pays off when Phase 2 lands later)
**Objective:** Verify that Phase 2's screen-reuse keeps the `VirtualTable.row_pool` alive across opens. Add an explicit guard so `_rebuild_row_pool` is only called when panel dimensions change, not on every yard switch. After Phase 2, this is largely a verification phase; the explicit guard catches any future regression.

---

## Pre-flight

- [ ] Phase 2 complete; `BuildQueueScreen` survives across opens.
- [ ] Re-read [findings/01_lifecycle_research.md](findings/01_lifecycle_research.md) §4 (`VirtualTable._rebuild_row_pool`).
- [ ] Re-read [virtual_table.py:143](../../../game/ui/components/table/virtual_table.py#L143) (`_rebuild_row_pool`) and [line 161](../../../game/ui/components/table/virtual_table.py#L161) (`visible_rows = max(1, (panel_height // row_height) + 2)`).
- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline.

---

## Tasks

### Task 3.1: Add row-pool reuse tests (TDD-first) [Simple]
**File:** `tests/unit/ui/components/table/test_virtual_table.py`
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py -v -k row_pool`

- [ ] Add tests:
  - `test_set_queue_does_not_rebuild_pool_when_dimensions_unchanged` — construct `VirtualTable`, capture `len(self._row_pool)`, call `set_queue(new_queue)`, assert pool list identity (`is`) unchanged AND `_rebuild_row_pool` was not invoked. (Use a counter or spy on the method.)
  - `test_panel_height_change_rebuilds_pool` — construct, change `panel_height`, call the rebuild trigger (whatever surface is exposed), assert pool was rebuilt.
  - `test_row_height_change_rebuilds_pool` — same with `row_height`.
- [ ] Run tests; **confirm they fail** on current code where `set_queue` may always trigger a pool rebuild.
- [ ] **Verify:** failures match expected reasons.

**Notes:**

### Task 3.2: Cache last-rebuild dimensions on `VirtualTable` [Simple]
**File:** `game/ui/components/table/virtual_table.py`

- [ ] In `__init__`, after the initial `_rebuild_row_pool`, cache `self._last_pool_dims = (self.panel_rect.height, self.row_height)`.
- [ ] Add private helper `_pool_dims_changed(self) -> bool` that compares the current `(panel_rect.height, row_height)` against `self._last_pool_dims` and returns `True` if either changed.
- [ ] In `_rebuild_row_pool` (or whatever the rebuild trigger is): early-return if `not self._pool_dims_changed()`. After a successful rebuild, update `self._last_pool_dims`.
- [ ] **Verify:** Task 3.1 tests pass.

**Notes:** Inspect existing `_rebuild_row_pool` callers (`grep -n '_rebuild_row_pool' game/ui/components/table/virtual_table.py`) — there may be paths that genuinely need to rebuild (e.g., manager teardown). Don't break those.

### Task 3.3: Verify `update_visible_rows` re-binds content correctly [Simple]
**File:** `game/ui/components/table/virtual_table.py`

- [ ] Read [virtual_table.py:261](../../../game/ui/components/table/virtual_table.py#L261) (`update_visible_rows`) end-to-end. Confirm the path that re-binds row content (labels, images, action buttons) on every dirty refresh — independent of pool rebuild.
- [ ] Add a unit test: pool is unchanged across two `set_queue + update_visible_rows` calls with different queue data; the resulting label texts on the visible rows reflect the second queue's data, not the first.
- [ ] **Verify:** test passes — content is re-bound; pool is reused.

**Notes:** This is a verification task; if the test fails, that's a real bug — file under findings/ and decide whether to fix here or defer.

### Task 3.4: Re-profile and confirm gain [Simple]
**Tests:** `python Tools/profile_game/profile_game.py`

- [ ] Open build queue at yard A, close, open at yard B (same context type), close.
- [ ] In the resulting HTML, confirm `_rebuild_row_pool` is invoked **once** (during the first open) and not on the yard-switch.
- [ ] Capture before/after.

**Notes:**

### Task 3.5: Full sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Pass count ≥ baseline + new Phase 3 tests.

**Notes:**

### Task 3.6: Commit Phase 3 [Simple]

- [ ] `git status --short`.
- [ ] Commit message: `feat(PROJ-373): Phase 3 — guard VirtualTable row-pool rebuild on dimension change only`
- [ ] Co-author trailer.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `_rebuild_row_pool` does not fire on yard-switch with same panel dimensions
- [ ] `_rebuild_row_pool` still fires on dimension change
- [ ] `update_visible_rows` correctly re-binds content across queue swaps
- [ ] Re-profile confirms ~1.5s/click saved on yard switches (in the cases that previously rebuilt the pool)
- [ ] Sharded suite green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
