# Phase 1: Regression Tests (TDD) [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-342 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add two failing regression tests that pin (a) the current crash surface, (b) the new constructor contract. Both must be RED on current code before any production code changes in Phase 2.

---

## Tasks

### Task 1.1: Pin the current crash surface [Simple]
**File:** `tests/unit/test_lab/test_render_progress_no_game_handle.py` (NEW)
**Tests:** `pytest tests/unit/test_lab/test_render_progress_no_game_handle.py::test_render_progress_no_game_screen_attribute -x`

This test reproduces the exact `AttributeError: 'ScreenRouter' object has no attribute 'screen'` failure mode by constructing a stub `game` that has `battle_scene` but no `screen` attribute. It must FAIL on the current `screen.py:382` code path and PASS after Phase 2.

- [x] Create test file with imports: `pygame`, `types.SimpleNamespace`, `pytest`, `Mock` from `unittest.mock`, and `from game.ui.screens.test_lab.screen import TestLabScreen`
- [x] Define test function that:
  - Bypasses `__init__` via `screen = TestLabScreen.__new__(TestLabScreen)`
  - Sets `screen.game = SimpleNamespace(battle_scene=Mock())` (note: no `.screen` attribute — this is what `ScreenRouter` looks like)
  - Sets `screen.screen_width = 3840`, `screen.screen_height = 2160`
  - Patches `pygame.display.get_surface` to return a `Mock()` that responds to `.blit`, `.fill`, `.get_width`, `.get_height`
  - Calls `screen._render_progress("title", "subtitle", "detail")`
  - Asserts no `AttributeError` is raised
- [x] Run the test against unmodified production code; **MUST FAIL** with `AttributeError: 'SimpleNamespace' object has no attribute 'screen'`
- [x] Document the expected failure mode in a comment so future readers understand it's a regression test

**Notes:** [Filled during implementation]

### Task 1.2: Pin the new constructor contract [Simple]
**File:** `tests/unit/test_lab/test_render_progress_no_game_handle.py` (same file, second test)
**Tests:** `pytest tests/unit/test_lab/test_render_progress_no_game_handle.py::test_constructor_no_game_attribute -x`

- [x] Add second test function that:
  - Constructs `TestLabScreen(3840, 2160, battle_scene=Mock(), scene_callback=Mock())` via the NEW signature
  - Asserts `not hasattr(screen, 'game')`
  - Asserts `screen.screen_width == 3840`, `screen.screen_height == 2160`
  - Asserts `screen.battle_scene is the_passed_mock`
- [x] Run against unmodified production code; **MUST FAIL** with `TypeError` (current `__init__` signature is `(game, scene_callback)`)
- [x] Use the same display-surface mocking pattern as Task 1.1 to keep `tests/unit/test_lab/conftest.py` unchanged (it does not auto-create a display per `tests/unit/ui/conftest.py:41-44` comparison)

**Notes:** [Filled during implementation]

### Task 1.3: Verify both tests fail on current code [Simple]
**Tests:** `pytest tests/unit/test_lab/test_render_progress_no_game_handle.py -x`

- [x] Run the new test file against current (pre-Phase-2) code
- [x] Confirm exactly the failure modes documented above
- [x] If a test fails for an unexpected reason, fix the test before proceeding — do not weaken assertions to make it pass

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:
- [x] Both new tests exist and are RED on unmodified production code
- [x] Test file imports are clean (no unused imports)
- [x] Test names clearly describe the regression they pin
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
