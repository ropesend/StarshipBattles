# Phase 1: Critical Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-239 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix the two critical-severity findings that pose immediate risk
**Priority:** Immediate

---

## Tasks

### Task 1.1: ERR-001 — Add error handling to turn engine tick loop [Medium]
**File:** `game/strategy/engine/turn_engine.py:369-370`
**Tests:** `pytest tests/unit/strategy/engine/test_turn_engine.py`

The `process_turn` method runs 100 ticks across 12+ sub-engine phases with zero exception handling. Any sub-engine failure crashes the turn mid-processing, leaving galaxy/empire state partially modified.

- [ ] Write test: inject a mock sub-engine that raises, verify turn engine catches it gracefully
- [ ] Add try/except around `_process_tick` calls with logging and state recovery strategy
- [ ] Design decision: fail-fast (abort turn, rollback) vs skip-and-continue (log error, continue remaining ticks) — document choice in decisions.md
- [ ] Verify: existing turn engine tests still pass, new error case is covered

**Notes:** Consider whether each sub-engine phase should be individually wrapped, or the entire tick. Individual wrapping gives better diagnostics but more complexity.

### Task 1.2: AR-001 — Remove AI layer import from strategy adapter [Medium]
**File:** `game/strategy/adapters/simulation_adapter.py:127`
**Tests:** `pytest tests/unit/strategy/adapters/`

`SimulationBattleResolver` has a late import of `game.ai.ai_factory.AIControllerFactory` in its default code path. Strategy is only allowed to depend on Core and Simulation — importing from AI is an architecture violation.

- [ ] Write test: verify `SimulationBattleResolver` works without AI import when factory is injected
- [ ] Refactor: make `ai_factory` a required constructor parameter (no default that imports AI)
- [ ] Update all call sites to inject the AI factory from the UI layer (where AI imports are allowed)
- [ ] Verify: no remaining `game.ai` imports anywhere in `game/strategy/`

**Notes:** The fix is to push the AI factory creation up to the UI/app layer and inject it down. The adapter should never need to know about AI directly.


---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
