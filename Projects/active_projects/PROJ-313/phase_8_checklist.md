# Phase 8: Demolition + Documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-313 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Subtractive phase. Delete the legacy slot-based system (the OR-bridge, `_handle_window_close`, the parametrised contract test) and replace with the structural-invariant test. Update docs to retire Pattern #30 and document the new `StrategyModalWindow` contract.

After this phase: `StrategyWindowManager` has only `_modals` (plus the lone `settings_window` direct slot). Router is two one-liners. `_handle_window_close` is gone. The `__init_subclass__` registry is the single source of truth for what counts as a strategy modal. Pattern #30 is marked historical.

---

## Tasks

### Task 8.1: Delete `_handle_window_close` event listener [Simple]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_event_router.py`

- [ ] Locate the `pygame_gui.UI_WINDOW_CLOSE` dispatch around line 152 of `strategy_event_router.py` and the `_handle_window_close` method around line 413-446
- [ ] Verify all branches in `_handle_window_close` reference slots that no longer exist (Phases 3-7 deleted them; if any remain, complete those phases first)
- [ ] Delete the entire `_handle_window_close` method
- [ ] Delete the `if event.type == pygame_gui.UI_WINDOW_CLOSE: self._handle_window_close(event)` dispatch in `route_event()`
- [ ] Run `pytest tests/unit/ui/screens/test_strategy_event_router.py` — pass
**Notes:** Verify the `pygame_gui.UI_WINDOW_CLOSE` dispatch isn't relied on elsewhere in the file (e.g., for non-modal windows or other purposes). If it's used for anything else, leave the event-listener dispatch but only delete `_handle_window_close`.

### Task 8.2: Collapse router scans to one-liners [Simple]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_event_router.py`

- [ ] In `has_modal_open()`: delete the OR-bridge composition (Phase 2 added it). The body becomes:
  ```python
  return any(True for _ in self.window_manager.iter_live_modals())
  ```
  (Or simpler: `return bool(list(self.window_manager.iter_live_modals()))` — implementer choice.)
- [ ] **CARE:** any non-modal slot reads remaining (e.g., `settings_window`, `menu_panel`, `build_queue_screen` — non-modal direct slots) stay if they're checked here for non-modal-related reasons. Audit each remaining clause and decide.
- [ ] In `_is_blocking_ui_element_at(self, point)`: similar collapse:
  ```python
  return any(w.rect.collidepoint(point) for w in self.window_manager.iter_live_modals())
  ```
- [ ] Verify the final method bodies match the design.md sketch
- [ ] Run targeted tests — pass
**Notes:**

### Task 8.3: Drop dead slot fields from `StrategyWindowManager.__init__` [Simple]
**File:** `game/ui/screens/strategy_window_manager.py`

- [ ] By this phase, all slot fields except `settings_window` and any genuinely non-modal slots (`menu_panel`, `build_queue_screen` per audit — verify) should already be deleted from Phases 3-7. Audit `__init__` and remove any remaining slots that referred to migrated windows.
- [ ] Confirm `_modals: list[UIWindow] = []` is initialised
- [ ] Run targeted tests — pass
**Notes:**

### Task 8.4: Replace `TestModalSlotCleanupContract` with structural-invariant test [Medium]
**File:** `tests/unit/ui/screens/test_strategy_window_manager_public_api.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_window_manager_public_api.py -v`

- [ ] Locate `class TestModalSlotCleanupContract` (the source-string-matching parametrised test class)
- [ ] DELETE it entirely (the contract it pinned no longer exists — slot fields are gone)
- [ ] Add new test class `TestStrategyModalWindowStructuralInvariant`:
  - [ ] Test `test_every_registered_subclass_appears_in_iter_live_modals_after_construction` — parametrise over `StrategyModalWindow._registered_subclasses`, instantiate each with a stub `StrategyWindowManager` (and minimal kwargs), assert membership
  - [ ] Test `test_every_registered_subclass_disappears_after_kill` — same parametrisation, instantiate then `kill()`, assert removal
  - [ ] Test `test_kill_does_not_invoke_super_directly` — assert that no subclass overrides `kill()` without calling `super().kill()`. Implement via instantiate-then-kill-and-check-state, NOT via source introspection.
- [ ] Reuse the per-subclass instantiation fixtures established for the contract test if helpful — adapt as needed.
**Notes:**

### Task 8.5: Add static guard test for direct `pygame_gui.UIWindow` subclassing [Medium]
**File:** `tests/unit/ui/screens/test_modal_subclass_guard.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/test_modal_subclass_guard.py -v`

- [ ] Create a new test that:
  - [ ] Walks all `.py` files in `game/ui/screens/` and `game/ui/screens/strategy_windows/`
  - [ ] Greps for direct subclassing of `pygame_gui.UIWindow` or `UIWindow` (when imported from pygame_gui)
  - [ ] Asserts each match is either `class StrategyModalWindow(UIWindow):` or appears in an explicit non-modal allowlist (currently just `SettingsWindow`)
  - [ ] If a new direct subclass appears, the test fails with a clear message pointing developers at `StrategyModalWindow`
- [ ] Use `ast` module for robust parsing (regex is OK for this scope but ast is more reliable)
**Notes:** This catches the "new dev forgot to subclass `StrategyModalWindow`" failure mode at CI time, providing the same protection the parametrised slot-test used to provide for forgotten slot-clauses.

### Task 8.6: Update `docs/02_PATTERNS.md` [Medium]
**File:** `docs/02_PATTERNS.md`
**Tests:** N/A (docs)

- [ ] Locate Pattern #30 "Registrar Close-Callback (BUG-121)" around line 1579
- [ ] Mark it as **historical / superseded by PROJ-313**. Keep the documentation for reference but add a `> **STATUS: Superseded.** This pattern was the per-window manual contract used for strategy modal windows. PROJ-313 (2026-04-XX) replaced it with structural enforcement via the `StrategyModalWindow` base class. New strategy-modal windows should subclass that base class instead of implementing the registrar callback pattern manually.` blockquote at the top of the section.
- [ ] Add NEW pattern entry at the end (Pattern #31) titled "Strategy Modal Window Base Class (PROJ-313)":
  - [ ] **Where:** `game/ui/screens/strategy_modal_window.py` — `StrategyModalWindow` base class.
  - [ ] **How It Works:** Subclassing `StrategyModalWindow` auto-registers the instance with `StrategyWindowManager` on construction and auto-deregisters in `kill()` (before `super().kill()`). `StrategyEventRouter.has_modal_open()` and `_is_blocking_ui_element_at()` walk a single live-list (`window_manager.iter_live_modals()`) which GC-filters dead refs via `.alive()`. The contract is structural — forgetting to register is impossible because registration happens in the base class constructor.
  - [ ] **When to Use:** Any new modal-style window that should block strategy-screen input. Subclass `StrategyModalWindow`, accept `window_manager` as a keyword-only param in `__init__`, forward it to `super().__init__(window_manager=window_manager, ...)`. No further wiring needed.
  - [ ] **Why:** Eradicates the BUG-22/BUG-69/BUG-121/foodallocation bug class structurally — clicks-through and stale-flag-leak failures are no longer possible because their causal contract steps are absent.
  - [ ] **Key Behavior:** Test contract at `tests/unit/ui/screens/test_strategy_window_manager_public_api.py::TestStrategyModalWindowStructuralInvariant` parametrises over every loaded subclass via `__init_subclass__` registry. Static guard at `tests/unit/ui/screens/test_modal_subclass_guard.py` prevents accidental direct `UIWindow` subclassing in strategy screens.
- [ ] Update the patterns count from 30 to 31 in the doc header
- [ ] Update the table of contents
- [ ] Bump `> **Last verified:** YYYY-MM-DD — PROJ-313 superseded Pattern #30 and added Pattern #31 ...`
**Notes:**

### Task 8.7: Update `docs/06_UI_STYLE_GUIDE.md` [Simple]
**File:** `docs/06_UI_STYLE_GUIDE.md`

- [ ] Add a new section: `## Window Management` (or `## Modal Windows`)
- [ ] Briefly describe `StrategyModalWindow` as the canonical way to add a strategy modal
- [ ] Cross-reference `docs/02_PATTERNS.md` Pattern #31 for full details
- [ ] Bump `> **Last verified:**`
**Notes:**

### Task 8.8: Update `docs/01_ARCHITECTURE.md` [Simple]
**File:** `docs/01_ARCHITECTURE.md`

- [ ] In the UI Layer description (top of file), add a short note: "Strategy-screen modal windows subclass `StrategyModalWindow` (`game/ui/screens/strategy_modal_window.py`) for unified lifecycle and click-blocking. See `docs/02_PATTERNS.md` Pattern #31."
- [ ] Bump `> **Last verified:**`
**Notes:**

### Task 8.9: Final verification [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite passes (record final test count — expect 15893 + ~10 new tests added across phases minus ~14 dropped from the old `TestModalSlotCleanupContract`)
- [ ] BUG-121 regression smoke: open Planet Abilities, close via `[X]`, mouse-wheel zoom on strategy map — works
- [ ] Food allocation click-through smoke (the QA-reported issue): open Food Allocation editor, click on strategy map at a different hex — selection NOT changed
- [ ] All 5 docs (`02_PATTERNS.md`, `06_UI_STYLE_GUIDE.md`, `01_ARCHITECTURE.md`) have bumped `Last verified:` timestamps
- [ ] No remaining references to `_handle_window_close`, `on_close_callback`, `_on_closed` in `game/ui/screens/strategy_*.py` (modal windows only — non-modal `settings_window` may retain its callback wiring)
- [ ] Update `Projects/projects_index.md` if needed (move PROJ-313 from active to whatever-tracker-says-completed)
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table — all phases Complete
- [ ] Update plan.md Current State to "All phases complete — ready for user smoke + sign-off"
- [ ] Run final sharded suite, record final passing count in plan.md
- [ ] Notify user that PROJ-313 is ready for verification
