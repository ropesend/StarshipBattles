# Phase 7: Test Quality Improvements

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-111 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Cross-cutting quality improvements to existing and new tests: improve assertion quality, reduce over-mocking, add error path and edge case coverage, test screen resize handling.
**Findings covered:** TCG-UI1-020, TCG-UI1-021, TCG-UI1-022, TCG-UI1-023, TCG-UI1-024
**Estimated tests:** ~40-60

---

## Task 7.1: Assertion Quality in Input Handler Tests [Simple]
**Finding:** TCG-UI1-020
**Source:** `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py` (372 lines, 39 tests, ~14 assertions)
**Tests:** Edit existing tests to add assertions

Current tests verify state changes but don't verify downstream effects.

- [ ] Add mock.assert_called assertions for scene method invocations when input mode changes
- [ ] Verify that mode-specific callbacks are invoked with correct parameters
- [ ] Add assertions for return values of handle_event (True when handled, False when not)
- [ ] Verify side effects: when `input_mode` changes to MOVE, verify visual feedback method is called
- [ ] Add at least 1 assertion per test that currently has 0 assertions (any tests that only check state)
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py -v`

**Notes:** Target: bring average assertions per test from 2.8 to 4+.

---

## Task 7.2: Reduce Over-Mocking in Event Tests [Medium]
**Finding:** TCG-UI1-021
**Source:** `tests/unit/ui/screens/` - multiple test files
**Tests:** Refactor selected tests to use real pygame events

- [ ] Identify 3-5 test files that mock `pygame.event.Event` construction
- [ ] Replace mock Events with real `pygame.event.Event()` objects where practical
- [ ] Verify event type attributes match real pygame event structure
- [ ] Add comments documenting which tests use real vs mock events and why
- [ ] Verify: `pytest tests/unit/ui/screens/ -v --tb=short`

**Notes:** Not all mocks should be replaced. Only replace where the mock hides real pygame behavior. Tests using `_keydown()` helper already create real events.

---

## Task 7.3: Error Path Coverage [Medium]
**Finding:** TCG-UI1-022
**Source:** Screens and panels tested in Phases 3-6
**Tests:** Add error path tests to existing test files

- [ ] Test screen initialization with invalid/missing dependencies (None width, None callback)
- [ ] Test screen operations with corrupted state (None session, empty galaxy)
- [ ] Test file I/O failures in ship loading (mock IOError, PermissionError)
- [ ] Test asset loading failures (missing images, corrupt JSON) in at least 3 screens
- [ ] Test exception handling in update() loops (verify no uncaught exceptions)
- [ ] Add try/except boundary tests for each new test file created in Phases 3-6
- [ ] Verify: No tests fail due to unhandled exceptions

---

## Task 7.4: Edge Case Coverage [Medium]
**Finding:** TCG-UI1-023
**Source:** Screens and panels tested in Phases 3-6
**Tests:** Add edge case tests to existing test files

**Empty collections:**
- [ ] Test BattleScreen with 0 ships per team
- [ ] Test StrategyScreen with 0 systems in galaxy
- [ ] Test FleetReportWindow with 0 ships in fleet
- [ ] Test BuildQueueScreen with 0 available designs
- [ ] Test PlanetListWindow with 0 planets

**Boundary values:**
- [ ] Test resource display with 0 resources
- [ ] Test HP bar with exactly 0 HP
- [ ] Test HP bar with exactly max HP
- [ ] Test ship speed at 0 and max_speed
- [ ] Test zoom at min_zoom and max_zoom boundaries

**Large collections:**
- [ ] Test planet list with 100+ planets (verify no performance issue in test)
- [ ] Test fleet with 50+ ships (verify no iteration issues)

- [ ] Verify: All edge case tests pass

---

## Task 7.5: Screen Resize Handling [Simple]
**Finding:** TCG-UI1-024
**Source:** Screens with `handle_resize()` method
**Tests:** Add resize tests to relevant test files

- [ ] Identify all screens with `handle_resize()` method
- [ ] Test BattleScreen resize updates camera dimensions
- [ ] Test StrategyScreen resize updates panel positions
- [ ] Test resize with same size (no-op should not crash)
- [ ] Test resize with minimum dimensions (e.g., 800x600)
- [ ] Test resize with maximum dimensions (e.g., 3840x2160)
- [ ] Verify: Resize tests pass for all tested screens

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All new tests passing: `pytest tests/unit/ui/ -v --tb=short`
- [ ] No regressions: `pytest tests/ -n 12`
- [ ] Total new test count documented
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "All phases complete"
