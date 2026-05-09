# Phase 1: CRITICAL — B-5 modal, registry exception, test assertions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-395 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Close the 3 CRITICAL findings from the PROJ-381 OpenCode review.

---

## Tasks

### Task 1.1: B-5 dialog → `StrategyModalWindow` (Pattern #31)
**File:** `game/ui/screens/strategy_game_state_manager.py:312-317` + new file (probably `game/ui/screens/turn_failed_dialog.py`)
**Tests:** `pytest tests/integration/ui/test_strategy_turn_error_boundary.py -v`

- [ ] Create `TurnFailedDialog(StrategyModalWindow)` class with the same message + dismiss-button shape as the current `pygame_gui.windows.UIMessageWindow`
- [ ] Replace `_show_turn_failed_dialog()` to instantiate `TurnFailedDialog` via `StrategyWindowManager`. Thread the manager through from `StrategyScreen.ui` (already holds the reference).
- [ ] Verify: clicking through the dialog blocks fleet commands and turn-advance until dismissed (Pattern #31 modal tracking)
- [ ] Update the existing `test_strategy_turn_error_boundary.py` regression test to assert modal-blocking behavior (not just dialog-instantiation)
- [ ] Verify: `pytest tests/integration/ui/test_strategy_turn_error_boundary.py -v` passes

### Task 1.2: `CommandRegistry.register()` → `ValidationException`
**File:** `game/strategy/engine/commands/registry.py:191`
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry.py -v`

- [ ] Replace `raise ValueError(...)` at the duplicate-registration guard with `raise ValidationException(code=ErrorCode.DUPLICATE_COMMAND.value, context={"command_name": name, "existing_handler": ..., "duplicate_handler": ...})`
- [ ] Add `DUPLICATE_COMMAND` to `game/core/error_codes.py` if not already present
- [ ] Update or add a unit test in `tests/unit/strategy/engine/test_command_registry.py` that asserts on `code` and `context` of the raised `ValidationException`
- [ ] Verify: focused test passes

### Task 1.3: Test assertions for `code` + `context` (3 tests)
**File:** `tests/unit/strategy/test_command_handlers.py:551-620` (3 PROJ-381 tests)
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py -v`

- [ ] Identify the 3 tests in `test_command_handlers.py` that check for `ValidationException` raise but only assert `str(exc)` substring
- [ ] Use `tests/unit/strategy/engine/test_base_command_handler.py` as the canonical pattern: `assert exc.value.code == ErrorCode.MISSING_ENTITY.value` + context field assertions
- [ ] Apply the same shape to all 3 tests
- [ ] Verify: focused test passes

### Task 1.4: Final regression
**File:** —
**Tests:** `pytest tests/ -k "command_handlers or registry or strategy_turn_error" --testmon`

- [ ] Run focused regression — all of the above test paths pass
- [ ] Verify: no test was checking the old `ValueError`-style raise (would break with the new `ValidationException`)

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2

_Source review: `Reviews/results/2026-05-08_230318_code_proj-381-error-handling-cleanup-strategy-ui-assets_req-req_20260508_230317_779973/`_
