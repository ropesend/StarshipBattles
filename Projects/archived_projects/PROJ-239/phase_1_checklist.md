# Phase 1: Critical Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-239 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the two critical-severity findings that pose immediate risk
**Priority:** Immediate

---

## Tasks

### Task 1.1: ERR-001 — Add error handling to turn engine tick loop [Medium]
**File:** `game/strategy/engine/turn_engine.py:369-370`
**Tests:** `pytest tests/unit/strategy/engine/test_turn_engine.py`

The `process_turn` method runs 100 ticks across 12+ sub-engine phases with zero exception handling. Any sub-engine failure crashes the turn mid-processing, leaving galaxy/empire state partially modified.

- [x] Write test: inject a mock sub-engine that raises, verify turn engine catches it gracefully
- [x] Add try/except around `_process_tick` calls with logging and state recovery strategy
- [x] Design decision: fail-fast (abort turn, rollback) vs skip-and-continue (log error, continue remaining ticks) — document choice in decisions.md
- [x] Verify: existing turn engine tests still pass, new error case is covered

**Notes:** Used log-and-continue approach via `_time_phase()` — the single chokepoint for all sub-engine calls. Error handling wraps each phase call individually so a harvesting failure doesn't block movement, etc. 6 new tests in `test_turn_error_handling.py`. Also added `None` guard for `env_events` extend (line 484) since environmental phase could return `None` on error. All 32 turn engine tests pass.

### Task 1.2: AR-001 — Remove AI layer import from strategy adapter [Medium]
**File:** `game/strategy/adapters/simulation_adapter.py:127`
**Tests:** `pytest tests/unit/strategy/adapters/`

`SimulationBattleResolver` has a late import of `game.ai.ai_factory.AIControllerFactory` in its default code path. Strategy is only allowed to depend on Core and Simulation — importing from AI is an architecture violation.

- [x] Write test: AST-based test verifying no `game.ai` imports in `game/strategy/`
- [x] Refactor: make `ai_factory` a required param on `SimulationBattleResolver`
- [x] Update all call sites: `app.py` creates `AIControllerFactory()` and injects through `GameSession` → `TurnEngine` → `SimulationBattleResolver`
- [x] Verify: no remaining `game.ai` imports anywhere in `game/strategy/`

**Notes:** Made `SimulationBattleResolver(ai_factory=...)` required. `ConflictResolutionEngine(battle_resolver=...)` also now required. `TurnEngine` lazily creates the resolver when `conflict_engine` is first accessed, using `_NullBattleResolver` as safe fallback when no factory is provided (tests that don't trigger combat). AI factory flows from `app.py` (UI layer) → `GameSession` → `TurnEngine`. `SaveGameService.load_game` also accepts `ai_factory` param. Updated ~25 test files to pass mock battle resolvers/factories.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
