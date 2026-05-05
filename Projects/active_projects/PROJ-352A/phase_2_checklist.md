# Phase 2: T6.6 — Strategy load dialog modal tracking

**Status:** Not Started
**Objective:** Register the strategy load dialog with the modal tracker so it blocks strategy-screen input while alive — matching the behavior of every other modal in the strategy screen.

---

## Tasks

### Task 2.1: Read the modal-management plumbing [Medium]
**Files (read-only):**
- `game/ui/screens/strategy_screen_lifecycle.py:64-77` (where the dialog is created)
- `game/ui/screens/save_selection_window.py:96-100` (the dialog's class)
- `game/ui/screens/strategy_window_manager.py:122-143` (the modal slot list)
- `game/ui/screens/strategy_event_router.py:47-73` (modal detection)
- `game/ui/screens/strategy_modal_window.py` (the base class other modals use)

- [ ] For each: understand the contract. Decide between two architectural shapes:
  - **Shape A:** Migrate `SaveSelectionWindow` to subclass `StrategyModalWindow` so the existing `iter_live_modals()` flow picks it up automatically.
  - **Shape B:** Keep `SaveSelectionWindow` as raw `UIWindow`, but add a `load_dialog` slot in `StrategyWindowManager` and have `iter_live_modals()` yield it explicitly.
- [ ] Document choice + rationale in [decisions.md](decisions.md). Default lean: Shape A (uniformity), unless Shape A requires extensive other-callers refactoring.

**Notes:**

### Task 2.2: Write a failing regression test [Medium]
**File:** `tests/unit/ui/screens/test_strategy_event_router_load_dialog_modal_tracking.py` (NEW or extend an existing event-router test file)

- [ ] Test setup: instantiate strategy event router with a mocked strategy screen state. Open a load dialog (mocked or real per Pattern §33). Send a strategy-screen-relevant input event (e.g., a hex click). Assert the strategy screen does NOT see the input (the modal swallowed it).
- [ ] Run test — must FAIL pre-fix (load dialog not tracked, input passes through).

**Notes:**

### Task 2.3: Implement the chosen shape [Complex]
**File(s):** depending on Shape A vs. Shape B chosen at 2.1

- [ ] **Shape A:** Migrate `SaveSelectionWindow` to `StrategyModalWindow`. Use the two-stage construction pattern. Update tests for the dialog to use the new construction surface.
- [ ] **Shape B:** Add `load_dialog` slot to `StrategyWindowManager`. Update `show_load_game_dialog()` to register the instance. Update `iter_live_modals()` to yield it.
- [ ] Run the failing regression test from 2.2 — must now PASS.
- [ ] Run `pytest tests/unit/ui/screens/ -k "save_selection or strategy_event_router or strategy_screen_lifecycle or strategy_window_manager" -x -q`.

**Notes:**

### Task 2.4: Manual smoke [Simple]

- [ ] Launch game, navigate to strategy screen, open load dialog.
- [ ] Confirm clicking on a hex behind the dialog does NOT trigger strategy-screen action while dialog is open.
- [ ] Close dialog, re-click hex, confirm strategy input now works.

**Notes:**

### Task 2.5: Targeted slice + commit [Simple]
**Tests:** see 2.3

- [ ] All pass.
- [ ] Commit: `fix(strategy-modal): track load dialog as blocking modal (PROJ-352A T6.6)`

**Notes:**

### Task 2.6: Final verification + index update
**Tests:** `pytest tests/unit/ -q -p no:cacheprovider`

- [ ] Full unit suite green.
- [ ] `python Tools/lint_test_files.py` — 0 violations.
- [ ] Update `Projects/projects_index.md` PROJ-352A → `Awaiting Verification`. Commit: `chore(PROJ-352A): mark closeout follow-up awaiting verification`.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] T6.6 commit + chore commit landed
- [ ] plan.md phase table → `Complete`
- [ ] Surface to user
