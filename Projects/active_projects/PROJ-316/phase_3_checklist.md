# Phase 3: Replace Phase 7 click-blocking regression test

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-316 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** the regression test must fail if any of the migration
steps are undone — subclass changed, spawn-site omits
`window_manager`, or base class skips registration. Closes audit
finding P1.3 (Phase 7 test does not exercise real editors).

---

## Tasks

### Task 3.1: Add structural-subclass test [Simple]
**File:** `tests/integration/ui/test_editor_click_blocking.py`
**Tests:** `pytest tests/integration/ui/test_editor_click_blocking.py`

- [ ] At the top of the file, import the 5 editor classes:
      ```python
      from game.ui.screens.food_allocation_editor import FoodAllocationEditor
      from game.ui.screens.atmosphere_target_editor import AtmosphereTargetEditor
      from game.ui.screens.gravity_target_editor import GravityTargetEditor
      from game.ui.screens.water_target_editor import WaterTargetEditor
      from game.ui.screens.radiation_shield_editor import RadiationShieldEditor
      from game.ui.screens.strategy_modal_window import StrategyModalWindow
      ```
- [ ] Add a parametrised test over the imported class objects (not strings) that asserts `issubclass(cls, StrategyModalWindow)`. Failure mode: a future commit removing the subclass relationship causes a hard test failure — not a soft assertion-message failure.

      ```python
      @pytest.mark.parametrize("cls", [
          FoodAllocationEditor, AtmosphereTargetEditor,
          GravityTargetEditor, WaterTargetEditor, RadiationShieldEditor,
      ])
      def test_editor_subclasses_strategy_modal_window(cls):
          assert issubclass(cls, StrategyModalWindow)
      ```

**Notes:**

---

### Task 3.2: Add registration-on-construct test [Medium]
**File:** `tests/integration/ui/test_editor_click_blocking.py`
**Tests:** `pytest tests/integration/ui/test_editor_click_blocking.py`

- [ ] Add a helper that constructs each editor with a stub `StrategyWindowManager` using the `__new__` + patched-`pygame_gui.elements.UIWindow.__init__` pattern (mirror `tests/unit/ui/screens/test_strategy_modal_window.py::_make_modal_window`). Each editor's domain-specific `__init__` will be patched out, and only `StrategyModalWindow.__init__` invoked manually so registration runs.
- [ ] For each of the 5 editors, assert the constructed instance appears in the manager's modal list immediately after `StrategyModalWindow.__init__` runs.
- [ ] For each, call `kill()` and assert it deregisters from the modal list.

**Notes:** `FoodAllocationEditor` and `AtmosphereTargetEditor` have non-trivial `__init__` bodies (resource catalog lookup, gas registry, etc.). The patched-init technique avoids those.

---

### Task 3.3: Add spawn-site assertion test [Medium]
**File:** `tests/integration/ui/test_editor_click_blocking.py` (or a new file `test_editor_spawn_sites.py` if cleaner — implementer's choice).
**Tests:** `pytest tests/integration/ui/test_editor_click_blocking.py`

- [ ] For each of the 5 `StrategyEventRouter._open_*_editor()` methods (`_open_food_allocation_editor`, `_open_atmosphere_editor`, `_open_gravity_editor`, `_open_water_editor`, `_open_radiation_shield_editor`):
      patch the editor class via `unittest.mock.patch`, call the spawn method on a stub router, assert `mock_editor.call_args.kwargs["window_manager"]` is `ui.window_manager` and is not `None`.
- [ ] Assert `window_manager` is passed as a keyword argument (not in `*args`).
- [ ] Failure mode: if a future commit removes `window_manager=ui.window_manager` from the spawn site, this test fails.

**Notes:** Each spawn method is its own test for clarity.

---

### Task 3.4: Rename or remove the existing click-blocking integration test [Simple]
**File:** `tests/integration/ui/test_editor_click_blocking.py`
**Tests:** N/A.

- [ ] The current `test_editor_blocks_click_inside_rect` exercises the router OR-bridge with a mocked editor in `iter_live_modals`. Decide:
      a) **Keep** under a clearer name like `test_router_blocks_clicks_inside_any_modal_in_iter_live_modals` — useful as router-level coverage independent of the editor classes.
      b) **Delete** entirely, now that the structural tests above provide stronger coverage.
- [ ] Recommend (a) — keep it but rename. The router-level test catches a different class of regression (router wiring).

**Notes:**

---

### Task 3.5: Manual mutation test (verification) [Simple]
**Tests:** Manual.

- [ ] Temporarily un-subclass `FoodAllocationEditor` from `StrategyModalWindow` (change to `pygame_gui.elements.UIWindow`). Run the new tests. Confirm Task 3.1's test fails. Revert.
- [ ] Temporarily comment out `window_manager=ui.window_manager` in `_open_food_allocation_editor`. Run tests. Confirm Task 3.3's test fails. Revert.
- [ ] Temporarily comment out `window_manager.register_modal(self)` in `StrategyModalWindow.__init__`. Run tests. Confirm Task 3.2's test fails. Revert.
- [ ] All three mutation tests confirm the new tests have teeth. Document in `decisions.md`.

**Notes:** This step is the proof that the new tests cover what the old test claimed to cover.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] 3 mutation tests confirm the test suite catches subclass / spawn-site / registration regressions
- [ ] `pytest tests/integration/ui/test_editor_click_blocking.py` clean with new tests
- [ ] `pytest tests/unit/ui/ tests/integration/ui/` no regression
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
