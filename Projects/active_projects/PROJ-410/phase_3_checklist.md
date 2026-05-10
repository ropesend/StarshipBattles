# Phase 3: Screen Lifecycle Resets + Selector Fix

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-410 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Wire B-hook (renderer) and C-hook (screen) so yard switch and close+reopen invalidate correctly. Fix the `BuildQueueSelector` container-visibility bug. After this phase, Phase 1 scenarios (a), (b), (d), (e), and yard-selector should pass.

**Hard constraints:**
- All command dispatch via `self.facade.handle_command()`. No direct session bypass.
- Manager-reuse semantics preserved (`open_for_yard()` still callable on a reused screen).
- Validation cache on `BuildQueueController._validation_cache` MUST survive yard switches (PROJ-373 phase 1 perf win).

---

## Tasks

### Task 3.1: B-hook in `BuildQueueRenderer.refresh_queue_display()` [Simple]
**File:** `game/ui/screens/build_queue_renderer.py:140–164`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_renderer.py` (extend or create)

- [ ] Inside `refresh_queue_display()`, after `data_source.set_queue(queue, build_rate)` and before `virtual_table.update_visible_rows()`, call `virtual_table.invalidate_widget_caches()`.
- [ ] Add a `# PROJ-410:` comment with one-line rationale ("flush per-row caches whenever a new queue is pushed; pool widgets are reused across yards/players").
- [ ] Add a unit test asserting `invalidate_widget_caches` is called exactly once per `refresh_queue_display()` call (use a Mock on `virtual_table`).

**Notes:**

---

### Task 3.2: C-hook in `BuildQueueScreen.open_for_yard()` [Medium]
**File:** `game/ui/screens/build_queue_screen.py:264–344`
**Tests:** Phase 1 tests 1.2, 1.3, 1.5 should now pass.

- [ ] Read the current resets at lines 317–337:
  - `self.controller.build_context = yard`
  - `self.controller.set_active_queue(self.active_queue_source)`
  - `self.controller.reset_filters()`
  - `self.drag_handler.reset_state()`
  - `self.drag_handler.design_library = design_library`
  - `self._queue_selector.refresh()`
- [ ] Verify whether `controller.set_active_queue(...)` clears `selected_queue_sources`. If not, add an explicit `self.controller.selected_queue_sources = []` reset (or whatever the cleanest API is on the controller — read source first).
- [ ] The renderer's B-hook (Task 3.1) fires via `_refresh_queue_display()` at line 342 — no extra `invalidate_widget_caches()` call from the screen needed.
- [ ] Add a `# PROJ-410:` comment grouping the lifecycle resets with one-line rationale.

**Notes:**

---

### Task 3.3: Fix `BuildQueueDragHandler.reset_state()` if Phase 1 confirmed gap [Simple — conditional]
**File:** `game/ui/panels/build_queue_drag_handler.py:88–101`
**Tests:** Phase 1 Task 1.1 test passes after this change.

- [ ] **Conditional**: only if Phase 1 Task 1.1 verified `selected_design` is NOT cleared by `reset_state()`.
- [ ] Add `self.selected_design = None` to the body of `reset_state()`.
- [ ] If Task 1.1 found it's already cleared (transitively via another mechanism), skip this task and the regression test from 1.1 locks in the existing behavior.

**Notes:**

---

### Task 3.4: Fix `BuildQueueSelector` container visibility [Medium]
**File:** `game/ui/screens/build_queue_selector.py:50–134` and possibly `build_queue_screen.py:369–373`
**Tests:** Phase 1 Task 1.7 test passes.

- [ ] Read `BuildQueueSelector.refresh()` (lines 89–134) and `BuildQueueScreen.show()` (lines 369–373) carefully to confirm the swarm's diagnosis: when the screen was previously hidden, the selector's `UIScrollingContainer` is not re-shown when `refresh()` adds new buttons, so buttons are added to a hidden container.
- [ ] Pick the smallest fix that addresses the root cause:
  - **Option 1 (preferred):** in `BuildQueueScreen.show()`, propagate `show()` to known child containers including the selector's container.
  - **Option 2:** in `BuildQueueSelector.refresh()`, ensure the selector's container is shown before populating buttons.
- [ ] Verify Phase 1 Task 1.7 test passes.
- [ ] Add a `# PROJ-410:` comment near the fix site.

**Notes:**

---

### Task 3.5: Run scenarios (a), (b), (d), (e), and yard-selector and verify pass [Simple]
**File:** (verification only)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py tests/integration/ui/build_queue_screen/test_queue_selector.py tests/unit/ui/components/table/test_virtual_table.py -v`

- [ ] Phase 1 Task 1.2 test passes (yard switch identical geometry).
- [ ] Phase 1 Task 1.3 test passes (close + reopen).
- [ ] Phase 1 Task 1.5 test passes (ship-yard ↔ planetary-yard).
- [ ] Phase 1 Task 1.6 test passes (button-press after switch — already passing from Phase 2 Task 2.4 if test lives in test_virtual_table.py).
- [ ] Phase 1 Task 1.7 test passes (yard-selector visible on second player).
- [ ] Phase 1 Task 1.4 (turn-boundary) and 1.8 (save/load) intentionally still fail — they land in Phase 4.
- [ ] `TestRowPoolReuseGuard` and `TestSecondClickReuse` still green.

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All Phase 3 task checkboxes are checked.
- [ ] Phase 1 scenarios (a), (b), (d), (e), and yard-selector pass; (c) and save/load still expected to fail.
- [ ] `pytest tests/ --testmon` shows no new failures elsewhere.
- [ ] `TestRowPoolReuseGuard` green.
- [ ] `tests/static_guards/test_facade_bypass_guard.py` green.
- [ ] No new direct-session bypass introduced (manual visual review of changed files).
- [ ] Update status at top of this file to `Complete`.
- [ ] Update `plan.md` phase table row to `Complete`.
- [ ] Update `plan.md` Current State to point to Phase 4.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-410 3` — output PASSED.
