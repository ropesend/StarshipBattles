# Phase 4: Unify Action Execution Engines

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-238 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Merge PlanetActionEngine logic into ActionExecutionEngine. Handle fleet speed-based intervals vs planet every-tick. Delete PlanetActionEngine. Update TurnEngine to use single engine.

---

## Tasks

### Task 4.1: Extend ActionExecutionEngine for Planet Orders [Complex]
**File:** `game/strategy/engine/action_execution_engine.py`
- [ ] Add planet order processing method (iterate empire.colonies, not just empire.fleets)
- [ ] Handle "every tick" execution for planets (no speed concept — interval = 1)
- [ ] Integrate planet-specific order execution (ACTIVATE_SHIELD, DEACTIVATE_SHIELD) — move logic from PlanetActionEngine._execute_order()
- [ ] Use unified ActionTimeResolver (from Phase 3)
- [ ] Return unified result type for both fleet and planet actions

### Task 4.2: Update TurnEngine [Medium]
**File:** `game/strategy/engine/turn_engine.py`
- [ ] Remove `planet_action_engine` lazy property
- [ ] Remove `_planet_action_engine` storage
- [ ] Remove `planet_action_engine` constructor parameter
- [ ] Remove Phase 1.6 (planet_actions) — merged into Phase 1.5 (actions)
- [ ] Update Phase 1.5 call to process both fleets and planets
- [ ] Remove `'planet_actions'` from `_reset_phase_times()`
- [ ] Update perf logging

### Task 4.3: Update Interfaces [Simple]
**File:** `game/strategy/interfaces/engines.py`
- [ ] Remove `IPlanetActionEngine` (merged into `IActionExecutionEngine`)
- [ ] Update `IActionExecutionEngine` to indicate it handles both entity types
- [ ] Update `__all__`

### Task 4.4: Delete PlanetActionEngine [Simple]
- [ ] Delete `game/strategy/engine/planet_action_engine.py`
- [ ] Move/merge tests from `test_planet_action_engine.py` into `test_action_execution_engine.py`

### Task 4.5: Verify [Simple]
- [ ] `python -m pytest tests/ -n 12 -q` — same count as baseline

---

## Phase Completion Checklist
- [ ] Single ActionExecutionEngine handles both fleet and planet orders
- [ ] PlanetActionEngine deleted
- [ ] TurnEngine has one action phase (not two)
- [ ] All tests pass
