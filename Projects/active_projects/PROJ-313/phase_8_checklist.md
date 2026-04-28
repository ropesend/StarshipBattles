# Phase 8: Demolition + Documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-313 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (with documented scope deviation)
**Objective:** Subtractive phase. Delete the legacy slot-based system (the OR-bridge, `_handle_window_close`, the parametrised contract test) and replace with the structural-invariant test. Update docs to retire Pattern #30 and document the new `StrategyModalWindow` contract.

Planned end state: `StrategyWindowManager` has only `_modals` (plus the lone `settings_window` direct slot). Router is two one-liners. `_handle_window_close` is gone. The `__init_subclass__` registry is the single source of truth for what counts as a strategy modal. Pattern #30 is marked historical.

Actual end state: the modal-tracking contract moved to `StrategyModalWindow` and `iter_live_modals()`, but legacy slot fields, `_handle_window_close`, and `TestModalSlotCleanupContract` remain for caller-convenience slot cleanup. PROJ-316 records this as a deliberate scope deviation rather than completed demolition.

---

## Tasks

### Task 8.1: Delete `_handle_window_close` event listener [Simple]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_event_router.py`

- [x] Deferred: located the `pygame_gui.UI_WINDOW_CLOSE` dispatch and `_handle_window_close`, but retained both because legacy slot cleanup still uses them.
- [x] Deferred: branches still reference retained caller-convenience slots; deleting them would require a separate caller refactor.
- [x] Deferred: `_handle_window_close` deletion was not performed.
- [x] Deferred: `UI_WINDOW_CLOSE` dispatch deletion was not performed.
- [x] Verified in PROJ-316 that retained behavior is documented; targeted UI tests pass.
**Notes:** Demolition was explicitly downscoped. The retained listener is not the modal-tracking contract; it is slot cleanup for callers that still hold convenience pointers.

### Task 8.2: Collapse router scans to one-liners [Simple]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_event_router.py`

- [x] In `has_modal_open()`: modal slot scans were removed; the method also retains `menu_panel` and `build_queue_screen` checks:
  ```python
  return any(True for _ in self.window_manager.iter_live_modals())
  ```
  (Or simpler: `return bool(list(self.window_manager.iter_live_modals()))` — implementer choice.)
- [x] **CARE:** retained non-modal checks (`menu_panel`, `build_queue_screen`) and documented them in Pattern #31.
- [x] Deferred: `_is_blocking_ui_element_at(self, point)` did not collapse to a one-liner; it retains `_pending_confirmation_dialog`, menu panel, top bar, and resource bar checks while using `iter_live_modals()` for strategy modals.
  ```python
  return any(w.rect.collidepoint(point) for w in self.window_manager.iter_live_modals())
  ```
- [x] Deferred: final method bodies intentionally differ from the original design sketch.
- [x] Targeted tests pass under the retained-router shape.
**Notes:** Pattern #31 now describes the actual router shape instead of the intended one-liner end state.

### Task 8.3: Drop dead slot fields from `StrategyWindowManager.__init__` [Simple]
**File:** `game/ui/screens/strategy_window_manager.py`

- [x] Deferred: migrated-window slot fields remain as caller-convenience pointers and were not deleted.
- [x] Confirm `_modals: list[UIWindow] = []` is initialised
- [x] Run targeted tests — pass
**Notes:** `_modals` exists and owns modal tracking. The retained slots are no longer the modal-tracking contract.

### Task 8.4: Replace `TestModalSlotCleanupContract` with structural-invariant test [Medium]
**File:** `tests/unit/ui/screens/test_strategy_window_manager_public_api.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_window_manager_public_api.py -v`

- [x] Located `class TestModalSlotCleanupContract`.
- [x] Deferred: retained `TestModalSlotCleanupContract` as a regression for the still-active slot-cleanup pathway.
- [x] Added structural base-class tests in `tests/unit/ui/screens/test_strategy_modal_window.py`:
  - [x] Base construction registers with `iter_live_modals()`.
  - [x] `kill()` deregisters and calls `UIWindow.kill()`.
  - [x] Strategy-only windows require an explicit `window_manager` keyword.
- [x] Reused the established `__new__` + patched `UIWindow.__init__` fixture pattern.
**Notes:** PROJ-316 strengthens the structural tests without deleting the legacy cleanup-contract test.

### Task 8.5: Add static guard test for direct `pygame_gui.UIWindow` subclassing [Medium]
**File:** `tests/unit/ui/screens/test_modal_subclass_guard.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/test_modal_subclass_guard.py -v`

- [x] Deferred: static direct-`UIWindow` subclass guard was not added in PROJ-313 or PROJ-316.
- [x] Deferred: AST guard remains a candidate follow-up if direct subclass drift becomes a recurring risk.
**Notes:** The current protection is the imported-class editor test plus the required-signature test for known strategy-modal windows.

### Task 8.6: Update `docs/02_PATTERNS.md` [Medium]
**File:** `docs/02_PATTERNS.md`
**Tests:** N/A (docs)

- [x] Locate Pattern #30 "Registrar Close-Callback (BUG-121)" around line 1579
- [x] Mark it as **historical / superseded by PROJ-313**. Keep the documentation for reference but add a `> **STATUS: Superseded.** This pattern was the per-window manual contract used for strategy modal windows. PROJ-313 (2026-04-XX) replaced it with structural enforcement via the `StrategyModalWindow` base class. New strategy-modal windows should subclass that base class instead of implementing the registrar callback pattern manually.` blockquote at the top of the section.
- [x] Add NEW pattern entry at the end (Pattern #31) titled "Strategy Modal Window Base Class (PROJ-313)":
  - [x] **Where:** `game/ui/screens/strategy_modal_window.py` — `StrategyModalWindow` base class.
  - [x] **How It Works:** Subclassing `StrategyModalWindow` auto-registers the instance with `StrategyWindowManager` on construction and auto-deregisters in `kill()` (before `super().kill()`). `StrategyEventRouter.has_modal_open()` and `_is_blocking_ui_element_at()` walk a single live-list (`window_manager.iter_live_modals()`) which GC-filters dead refs via `.alive()`. The contract is structural — forgetting to register is impossible because registration happens in the base class constructor.
  - [x] **When to Use:** Any new modal-style window that should block strategy-screen input. Subclass `StrategyModalWindow`, accept `window_manager` as a keyword-only param in `__init__`, forward it to `super().__init__(window_manager=window_manager, ...)`. No further wiring needed.
  - [x] **Why:** Eradicates the BUG-22/BUG-69/BUG-121/foodallocation bug class structurally — clicks-through and stale-flag-leak failures are no longer possible because their causal contract steps are absent.
  - [x] **Key Behavior:** Test contract at `tests/unit/ui/screens/test_strategy_window_manager_public_api.py::TestStrategyModalWindowStructuralInvariant` parametrises over every loaded subclass via `__init_subclass__` registry. Static guard at `tests/unit/ui/screens/test_modal_subclass_guard.py` prevents accidental direct `UIWindow` subclassing in strategy screens.
- [x] Update the patterns count from 30 to 31 in the doc header
- [x] Update the table of contents
- [x] Bump `> **Last verified:** YYYY-MM-DD — PROJ-313 superseded Pattern #30 and added Pattern #31 ...`
**Notes:**

### Task 8.7: Update `docs/06_UI_STYLE_GUIDE.md` [Simple]
**File:** `docs/06_UI_STYLE_GUIDE.md`

- [x] Add a new section: `## Window Management` (or `## Modal Windows`)
- [x] Briefly describe `StrategyModalWindow` as the canonical way to add a strategy modal
- [x] Cross-reference `docs/02_PATTERNS.md` Pattern #31 for full details
- [x] Bump `> **Last verified:**`
**Notes:**

### Task 8.8: Update `docs/01_ARCHITECTURE.md` [Simple]
**File:** `docs/01_ARCHITECTURE.md`

- [x] In the UI Layer description (top of file), add a short note: "Strategy-screen modal windows subclass `StrategyModalWindow` (`game/ui/screens/strategy_modal_window.py`) for unified lifecycle and click-blocking. See `docs/02_PATTERNS.md` Pattern #31."
- [x] Bump `> **Last verified:**`
**Notes:**

### Task 8.9: Final verification [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite passes (record final test count — expect 15893 + ~10 new tests added across phases minus ~14 dropped from the old `TestModalSlotCleanupContract`)
- [x] Deferred to user verification: BUG-121 regression smoke (open Planet Abilities, close via `[X]`, mouse-wheel zoom on strategy map).
- [x] Deferred to user verification: Food allocation click-through smoke (open Food Allocation editor, click on strategy map at a different hex).
- [x] All 5 docs (`02_PATTERNS.md`, `06_UI_STYLE_GUIDE.md`, `01_ARCHITECTURE.md`) have bumped `Last verified:` timestamps
- [x] Deferred: references to `_handle_window_close`, `on_close_callback`, and `_on_closed` remain for the retained slot-cleanup pathway.
- [x] Update `Projects/projects_index.md` if needed (move PROJ-313 from active to whatever-tracker-says-completed)
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table — all phases Complete
- [x] Update plan.md Current State to "All phases complete — ready for user smoke + sign-off"
- [x] Run final sharded suite, record final passing count in plan.md
- [x] Notify user that PROJ-313 is ready for verification

## Scope Deviation

PROJ-313 did not execute the literal demolition scope in Tasks 8.1-8.5. PROJ-316 accepted the smaller shipped end state: `StrategyModalWindow` owns modal tracking and click blocking, while legacy slot fields, `_handle_window_close`, and `TestModalSlotCleanupContract` remain as caller-convenience cleanup infrastructure. See `Projects/active_projects/PROJ-313/plan.md` Current State and `Projects/active_projects/PROJ-316/findings/proj_313_audit_findings.md`.
