# Phase 1: UIWindow `bypass_init` flag (production-side)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-324 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add the `bypass_init=True` opt-in flag to UIWindow subclasses + `StrategyModalWindow`, and provide a `bypass_init(Cls)` context manager in the test factory. Production behavior MUST be unchanged when the flag is unset.

**Required reading before starting:**
- [`design.md`](design.md) — especially Implementation Pattern + Risks sections
- [`docs/known-issues.md`](docs/known-issues.md) — UIWindow blocker history
- [`tests/fixtures/ui_widget_factory.py`](tests/fixtures/ui_widget_factory.py) — existing factory (do NOT modify the factory itself in this phase, just add the context manager)

**Parallelism:** This phase is file-disjoint from PROJ-326 entirely. PROJ-325 Phases 1-2 also touch unrelated files. **Safe to run in parallel** with PROJ-326 and PROJ-325 Phases 1-2. Do NOT run in parallel with PROJ-325 Phase 3 (RaceSetupScreen) or PROJ-327 (mutable-mock rescopes touch test files we will edit in Phase 3).

---

## Tasks

### Task 1.1: Add `bypass_init` context manager + smoke tests [Simple]

**File:** [`tests/fixtures/ui_widget_factory.py`](tests/fixtures/ui_widget_factory.py) — add new function
**File:** [`tests/fixtures/test_ui_widget_factory.py`](tests/fixtures/test_ui_widget_factory.py) — add smoke tests
**Tests:** `pytest tests/fixtures/test_ui_widget_factory.py`

- [ ] Add `bypass_init(Cls)` as a `contextlib.contextmanager` to `tests/fixtures/ui_widget_factory.py`. Implementation: store original value of `getattr(Cls, 'bypass_init', None)`, set `Cls.bypass_init = True`, yield, on exit restore the original value (or `delattr` if there was none).
- [ ] Add a docstring noting: this is for UIWindow subclasses ONLY; non-UIWindow widgets should use plain `make_ui_widget(...)` without the context manager.
- [ ] Add smoke test: `bypass_init` sets and clears the flag normally.
- [ ] Add smoke test: `bypass_init` clears the flag when the body raises.
- [ ] Add smoke test: nested `bypass_init` on the same class restores the previous value (not just `False`).
- [ ] Verify: `pytest tests/fixtures/test_ui_widget_factory.py` passes.

**Notes:** [Filled during implementation]

---

### Task 1.2: Add `bypass_init` guard to `StrategyModalWindow` [Simple]

**File:** [`game/ui/screens/strategy_modal_window.py`](game/ui/screens/strategy_modal_window.py)
**Tests:** Run any existing tests that import `StrategyModalWindow` directly + smoke-test the 4 subclasses (`FleetReportWindow`, `OrdersWindow`, `TransferDialog`, `BuildQueueListWindow`) construct via `make_ui_widget` + `bypass_init`.

- [ ] Add as the FIRST executable statement of `StrategyModalWindow.__init__` (before any parameter validation, super-call, or attribute assignment):
  ```python
  if getattr(type(self), 'bypass_init', False):
      return
  ```
- [ ] Verify the guard uses `type(self)`, NOT `StrategyModalWindow` (so subclass flags are honored).
- [ ] Audit `StrategyModalWindow.__init__` for any explicit `pygame_gui.elements.UIWindow.__init__(self, ...)` ancestor calls — if any, document in Notes; the `super()` chain assumption only holds for `super().__init__()` style.
- [ ] Run a subclass smoke test:
  ```python
  with bypass_init(FleetReportWindow):
      window = make_ui_widget(FleetReportWindow, fleet=Mock(), empire=Mock(), window_manager=Mock(), on_close_callback=Mock(), split_fleet_callback=Mock())
  assert window is not None
  ```
- [ ] Verify: `pytest tests/unit/ui/ -k strategy_modal` passes; no regressions.

**Notes:** [Filled during implementation]

---

### Task 1.3: Add `bypass_init` guard to `RaceSetupScreen` [Simple]

**File:** [`game/ui/screens/race_setup/screen.py`](game/ui/screens/race_setup/screen.py)
**Tests:** `pytest tests/unit/ui/screens/race_setup/`

- [ ] Add as the FIRST executable statement of `RaceSetupScreen.__init__` (line 74+):
  ```python
  if getattr(type(self), 'bypass_init', False):
      return
  ```
- [ ] Verify guard uses `type(self)`.
- [ ] Audit for explicit ancestor calls.
- [ ] Verify: existing race_setup tests still pass: `pytest tests/unit/ui/screens/race_setup/`. Production behavior MUST be unchanged when flag unset.
- [ ] Smoke-test construction with the flag set: `with bypass_init(RaceSetupScreen): make_ui_widget(RaceSetupScreen, ...)` succeeds without a real pygame display.

**Notes:** [Filled during implementation]

---

### Task 1.4: Add `bypass_init` guard to `NewGameSetupScreen` [Simple]

**File:** [`game/ui/screens/new_game_setup_screen.py`](game/ui/screens/new_game_setup_screen.py)
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup_screen.py` (and any sibling tests)

- [ ] Add guard as FIRST executable statement of `NewGameSetupScreen.__init__` (line 87+).
- [ ] Verify guard uses `type(self)`.
- [ ] Audit for explicit ancestor calls.
- [ ] Verify existing tests pass.

**Notes:** [Filled during implementation]

---

### Task 1.5: Verify direct `StrategyModalWindow` subclasses inherit the guard correctly [Medium]

**Files (audit only, no edits expected):**
- [`game/ui/screens/fleet_report_window.py`](game/ui/screens/fleet_report_window.py)
- [`game/ui/screens/orders_window.py`](game/ui/screens/orders_window.py)
- [`game/ui/screens/transfer_dialog.py`](game/ui/screens/transfer_dialog.py)
- [`game/ui/screens/build_queue_list_window.py`](game/ui/screens/build_queue_list_window.py)

**Tests:** Smoke-test each subclass construction with `bypass_init`.

- [ ] For each of the 4 subclasses, audit `__init__`:
  - Does it call `super().__init__()`? (Required for the inherited guard to fire.)
  - Does it do any work BEFORE the `super().__init__()` call? (If yes, that work runs even with `bypass_init=True` — may need a per-class guard.)
  - Does it call `pygame_gui.elements.UIWindow.__init__(self, ...)` explicitly anywhere? (If yes, the guard does not intercept that path — needs per-class guard.)
- [ ] For each subclass that needs its own per-class guard, add it as Task 1.2 pattern.
- [ ] Smoke-test each:
  ```python
  with bypass_init(FleetReportWindow):
      w = make_ui_widget(FleetReportWindow, ...)
  with bypass_init(OrdersWindow):
      w = make_ui_widget(OrdersWindow, ...)
  with bypass_init(TransferDialog):
      w = make_ui_widget(TransferDialog, ...)
  with bypass_init(BuildQueueListWindow):
      w = make_ui_widget(BuildQueueListWindow, ...)
  ```

**Notes:** [Filled during implementation. List which subclasses needed their own guard, if any.]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py`
- [ ] No production behavior change when flag is unset (verify by running the existing UI tests that don't use `bypass_init`)
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase 2
