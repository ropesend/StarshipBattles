# Phase 2: VirtualTable Invalidation Surface

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-410 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add the targeted invalidation surface inside `VirtualTable` itself. Pure component-layer changes — no facade or screen code touched. After this phase, scenario (e) from Phase 1 passes; scenarios (a)/(b)/(d) pass once the screen-side hook lands in Phase 3.

**Hard constraints:**
- MUST NOT call `.kill()` on any widget — `TestRowPoolReuseGuard` lock-in.
- MUST NOT modify `_pool_dims_changed()` or the pool-rebuild geometry check.
- The dirty flag MUST be ephemeral (cleared after one `update_visible_rows()` re-render).

---

## Tasks

### Task 2.1: Add `_data_identity_dirty` private flag [Simple]
**File:** `game/ui/components/table/virtual_table.py`
**Tests:** Unit test asserts default value.

- [ ] In `__init__` (near the existing `_last_pool_dims` declaration at ~line 103), add `self._data_identity_dirty: bool = True`.
- [ ] Add unit test in `tests/unit/ui/components/table/test_virtual_table.py` verifying `vt._data_identity_dirty is True` immediately after construction.

**Notes:**

---

### Task 2.2: Add `invalidate_widget_caches()` public method [Medium]
**File:** `game/ui/components/table/virtual_table.py`
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py -k invalidate_widget_caches`

- [ ] Add `def invalidate_widget_caches(self) -> None:` near other public lifecycle methods.
- [ ] Implementation: iterate `self._row_pool`. For each row: `row["_last_color"] = None`. For each `widget` in `row["widgets"]`: if widget type is `"label"`, set `widget["_last_text"] = None`; otherwise (image), set `widget["_last_img"] = None`. Set `self._data_identity_dirty = True`. Do NOT call `.kill()`. Idempotent.
- [ ] Add unit tests:
  - [ ] After call, every pool widget's `_last_text` / `_last_img` is None and every row's `_last_color` is None.
  - [ ] After call, `_data_identity_dirty` is True.
  - [ ] No widget `.kill()` calls (use a `Mock` spy on `widget["el"].kill` or assert kill counts).
  - [ ] Idempotent: calling twice yields same observable state.

**Notes:**

---

### Task 2.3: Gate `update_visible_rows()` early-return on the dirty flag [Medium]
**File:** `game/ui/components/table/virtual_table.py:309–323`
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py -k update_visible_rows_data_identity`

- [ ] Modify the early-return guard at lines 318–323 to also require `not self._data_identity_dirty`:
  ```python
  if (current_pct == self._last_scroll_pct and
      current_count == self._last_row_count and
      not self._data_identity_dirty):
      return
  ```
- [ ] After the per-row update loop completes (around line 423, after the `else` branch that handles rows beyond `current_count`), set `self._data_identity_dirty = False`. This is the **ephemeral** semantics — the flag clears on first re-render.
- [ ] Add unit test: invalidate + identical scroll/count → re-render fires (per-row updates observable). Second call without invalidate → re-render skipped (flag was cleared by prior pass).

**Notes:**

---

### Task 2.4: Re-bind action button row indices on dirty refresh [Complex]
**File:** `game/ui/components/table/virtual_table.py` — inside `update_visible_rows()` per-row mapping (~lines 332–423) and `check_action_button_press()` (lines 503–531)
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py -k button_press` (Phase 1 Task 1.6 test) now passes.

- [ ] Read the action-button construction site in `_rebuild_row_pool()` (~lines 244–265) carefully to determine HOW row index is captured by handlers — closure over `row_index` at construction, or read from `row.get("row_index")` at click time?
- [ ] If handlers capture via closure: refactor so handlers read `row.get("row_index")` at click time (lookup, not closure). Pool rows become truly index-agnostic.
- [ ] In `update_visible_rows()`, when dirty re-render runs, ensure each pool row's `row_index` is updated to the new data row before any click can fire.
- [ ] Add unit test (or extend Phase 1 Task 1.6 test): invalidate + new data; click `+` button on visible row 0; verify handler observes the new data's row 0 design id, not the old.
- [ ] Confirm Phase 1 Task 1.6 test passes.

**Notes:**

---

### Task 2.5: Verify perf-lock tests stay green [Simple]
**File:** (no edit) — verification only
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py::TestRowPoolReuseGuard -v`

- [ ] All 4–5 `TestRowPoolReuseGuard` tests pass unchanged.
- [ ] `test_force_update_does_not_force_pool_rebuild` still passes — `invalidate_widget_caches()` does not affect `_last_pool_dims`.
- [ ] No new widget `.kill()` calls anywhere in the changed code.

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All Phase 2 task checkboxes are checked.
- [ ] All new + existing VirtualTable unit tests are green.
- [ ] `TestRowPoolReuseGuard` is green (perf lock-in preserved).
- [ ] `pytest tests/ --testmon` shows no new failures.
- [ ] `tests/static_guards/test_facade_bypass_guard.py` green.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update `plan.md` phase table row to `Complete`.
- [ ] Update `plan.md` Current State to point to Phase 3.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-410 2` — output PASSED.
