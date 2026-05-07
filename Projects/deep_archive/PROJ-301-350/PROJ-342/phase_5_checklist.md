# Phase 5: Update Tests [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-342 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update or delete tests broken by Phases 2-4. After this phase, `pytest tests/unit/test_lab -x` and `pytest tests/unit/combat_lab/services -x` must both pass cleanly.

---

## Tasks

### Task 5.1: Update `tests/unit/test_lab/test_visual_run.py` [Medium]
**File:** `tests/unit/test_lab/test_visual_run.py`
**Tests:** `pytest tests/unit/test_lab/test_visual_run.py -x`

- [ ] Rename `mock_game` fixture to `mock_battle_scene` and inline what was previously `mock_game.battle_scene`. Drop `mock_game.screen` setup (no longer relevant).
- [ ] In [`_create_test_lab_screen` (line 92)](../../../tests/unit/test_lab/test_visual_run.py#L92): replace `screen.game = mock_game` with `screen.battle_scene = mock_battle_scene`. The executor's `get_engine` lambda becomes `lambda: mock_battle_scene.engine`.
- [ ] In [`_create_screen_with_real_switch` (line 268)](../../../tests/unit/test_lab/test_visual_run.py#L268): same replacement.
- [ ] Update assertions: `mock_game.battle_scene.start_battle.assert_called_once()` → `mock_battle_scene.start_battle.assert_called_once()`. Same for `call_args[0][0]` etc.
- [ ] In `TestSceneTransitionCallbacks.mock_game` (lines 248-266): rename to `mock_battle_scene`, drop `game.battle_scene = ...` indirection, drop `game.screen = Mock()` setup
- [ ] Verify all tests in this file pass: `pytest tests/unit/test_lab/test_visual_run.py -v`

**Notes:** [Filled during implementation. ~30 line changes total; mechanical.]

### Task 5.2: Delete service-test files orphaned by Phase 4 [Simple]
**Files:** `tests/unit/combat_lab/services/test_test_execution_service.py` (DELETE), `test_controller_execution.py` (UPDATE), `test_controller_init_events.py` (UPDATE), `conftest.py` (UPDATE)
**Tests:** `pytest tests/unit/combat_lab/services -x`

Per Phase B Test Impact Analyst (`findings/test_impact_analyst.md`), precise dispositions:

- [ ] `git rm tests/unit/combat_lab/services/test_test_execution_service.py` — entire file (20 tests for the deleted service)
- [ ] In `tests/unit/combat_lab/services/test_controller_execution.py`:
  - Delete `TestHandleRunHeadless` class entirely (lines 14-205, 8 tests)
  - Keep `TestGetFilteredScenarios`, `TestGetShipInfo`, `TestGetComponentData` (9 tests survive)
  - Update constructor calls at lines 225, 254, 275, 293, 311, 325: `TestLabUIController(mock_game, mock_test_registry, mock_test_history)` → `TestLabUIController(mock_test_registry, mock_test_history)`
- [ ] In `tests/unit/combat_lab/services/test_controller_init_events.py`:
  - Delete `TestHandleRunVisual` class entirely (lines 134-199, 4 tests)
  - Keep init / event-handling / category-click / test-click tests (8 survive)
  - Remove the `assert controller.game is mock_game` assertion at line 18
  - Update constructor calls (8 sites) to drop `mock_game=` argument
- [ ] In `tests/unit/combat_lab/services/conftest.py`: remove the `mock_game` fixture (lines 59-66) — only used by the deleted tests
- [ ] In `tests/unit/test_lab/conftest.py`: optionally add a `mock_battle_scene` fixture if more tests need it; otherwise create it inline in `test_visual_run.py`
- [ ] Verify with `git grep -nE "handle_run_visual|handle_run_headless" tests/` — must return zero hits after these edits
- [ ] Verify with `git grep -n "mock_game" tests/unit/combat_lab/services tests/unit/test_lab` — must return zero hits

**Notes:** [Filled during implementation. Read each file before mass-deleting; surviving tests need their construction calls updated, not removed.]

### Task 5.3: Add resize-forwarding regression test [Simple]
**File:** `tests/unit/test_lab/test_handle_resize_forwards_to_viewer.py` (NEW)
**Tests:** `pytest tests/unit/test_lab/test_handle_resize_forwards_to_viewer.py -x`

Pin Phase 2 Task 2.4's `BattleStateViewer.handle_resize` forwarding so it doesn't regress.

- [ ] Construct a `TestLabScreen` via `__new__` bypass (or the new constructor with a mock display surface). Stub `battle_state_viewer` with a `Mock()`.
- [ ] Call `screen.handle_resize(1920, 1080)`
- [ ] Assert `screen.battle_state_viewer.handle_resize.assert_called_once_with(1920, 1080)`
- [ ] Assert `screen.screen_width == 1920` and `screen.screen_height == 1080`

**Notes:** [Filled during implementation]

### Task 5.4: Targeted full sweep [Simple]
**Tests:** `pytest tests/unit/test_lab tests/unit/combat_lab/services -x`

- [ ] Run both targeted directories together
- [ ] All tests must pass; if any fail, diagnose and fix the test (do NOT weaken assertions)
- [ ] If a failing test reveals a real production bug introduced in Phases 2-4, fix the production code and document in `decisions.md`

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

- [ ] `tests/unit/test_lab` is GREEN (including the new Phase 1 tests + Task 5.3 resize test)
- [ ] `tests/unit/combat_lab/services` is GREEN
- [ ] No test references `screen.game`, `controller.game`, `mock_game`, `TestExecutionService`, or `TestResultsService`
- [ ] `git grep -nE "screen\.game|controller\.game|mock_game" tests/` returns zero hits
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
