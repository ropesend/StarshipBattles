# Phase 1: Critical — UI error boundary for turn processing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-381 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Close the 1 verified CRITICAL boundary failure identified by audit `2026-05-07_220225_error-audit` — `EnginePhaseError` raised from any phase currently propagates unhandled through `process_full_turn()` → `advance_turn()` → pygame event loop → `app.py`'s top-level crash handler, exiting the game. State rollback works correctly at the TurnEngine level; this phase adds the UI-level catch + modal error dialog and a regression test that exercises the failure path.

---

## Tasks

### Task 1.1: Add `except EnginePhaseError` handler in `process_full_turn()` [Medium]
**File:** `game/ui/screens/strategy_game_state_manager.py`
**Tests:** `pytest tests/integration/ui/test_strategy_turn_error_boundary.py` (new) and `pytest tests/ui/test_strategy_game_state_manager.py`

- [ ] Wrap the `self._screen._facade.process_turn(progress_callback=_on_tick)` call (lines ~122-128) in `try/except EnginePhaseError as e: ... finally: ...` instead of `try/finally`. The existing `finally` block (clearing `current_tick`/`total_ticks`) must run in both success and error paths.
- [ ] In the new `except EnginePhaseError as e:` block, surface a modal error dialog showing: failed phase name (`e.context.get("phase_name")`), tick number (`e.context.get("tick")`), original error type (`e.context.get("original_type")`), and a fixed-text "Turn has been rolled back — empire state is preserved" reassurance line (the rollback already happened in `TurnEngine.process_turn()`).
- [ ] Confirm `EnginePhaseError` is importable from `game.core.exceptions` and add the import.
- [ ] Verify the call chain is otherwise unmodified — `advance_turn()` (line ~53), `strategy_screen.advance_turn()` (~line 348), and `strategy_session_facade.process_turn()` (lines 164-182) should NOT need their own `except` blocks because the gap is closed at the UI manager.

### Task 1.2: Add regression test exercising the failure path [Medium]
**File:** `tests/integration/ui/test_strategy_turn_error_boundary.py` (new)
**Tests:** `pytest tests/integration/ui/test_strategy_turn_error_boundary.py`

- [ ] New test class `TestStrategyTurnErrorBoundary` covering: (a) baseline — turn succeeds, no dialog; (b) `EnginePhaseError` from a stub phase produces a modal dialog rather than propagating; (c) snapshot rollback context (turn_number, empire treasury) survives the failure; (d) `current_tick`/`total_ticks` are cleared in both success and error paths (the `finally` block keeps running).
- [ ] Stub a phase that raises `EnginePhaseError` deterministically (use the existing test scaffolding under `tests/integration/strategy/` if available; otherwise inject via the turn-engine config).
- [ ] Assert the modal dialog appears once and reflects the `phase_name` and `original_type` context keys from the raised `EnginePhaseError`.

### Task 1.3: Phase verification
**File:** N/A (validation only)
**Tests:** Full sharded suite

- [ ] Verify: `python Tools/test_sharded/test_sharded.py` passes; the new regression test passes; `grep -rn "except:" game/ui/screens/strategy_game_state_manager.py` returns nothing; the file does not introduce a new `except Exception:` without `# Intentional broad catch:` comment.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220225_error-audit/`. See `findings/source_audit.md` for the link._
