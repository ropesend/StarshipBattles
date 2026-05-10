# Phase 1: GameSession Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-211 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Establish registries on GameSession and wire to TurnEngine + Facade
**Priority:** Immediate - Foundation for all subsequent phases
**Risk:** Low

---

## Tasks

### Task 1.1: Add `registries` property to GameSession [DI-S-003, AR-004]
**Files:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/engine/`

- [x] Read `game_session.py` to understand current constructor and `from_dict()`
- [x] Add `_registries` field, resolve once at init time from `get_default_registry_provider()`
- [x] Expose via `registries` property
- [x] Pass `registries=self._registries` to `TurnEngine()` in both `__init__()` and `from_dict()`
- [x] Write test verifying GameSession.registries is populated
- [x] Verify: `pytest tests/ -n 12` passes

### Task 1.2: Make TurnEngine `registries` required [DI-S-003, DI-S-007]
**Files:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/`

- [x] Change `registries: Optional[GameRegistries] = None` to `registries: GameRegistries`
- [x] Remove the fallback block (lines 164-170)
- [x] Update docstring (DI-S-007) to remove "Falls back to..." language
- [x] Update `create_default_turn_engine()` factory to require registries param
- [x] Update all test files with TurnEngine() to pass registries
- [x] Verify: all tests pass

### Task 1.3: Fix StrategySessionFacade.get_fleet_remaining_pods() [DI-S-004, AR-005]
**Files:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/`

- [x] Replace inline `get_default_registry_provider()` call with `self._session.registries.components`
- [x] Remove the broad try/except error swallowing (lines 501-506)
- [x] Remove unused `StateException` import (no other usages)
- [x] Verify: all tests pass

### Task 1.4: Make ShipInstance.to_ship() registries required [DI-S-005]
**Files:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Change `registries: Optional[GameRegistries] = None` to `registries: GameRegistries` on `to_ship()`
- [x] Remove "Phase 6" docstring comment about transitional state
- [x] Verify existing callers (FleetBattleAdapter, SimulationAdapter) already pass registries
- [x] Verify: all tests pass

### Task 1.5: Make EmpireEconomyCalculator registries required [DI-S-008]
**Files:** `game/strategy/engine/empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/`

- [x] Change `registries: Optional[GameRegistries] = None` to `registries: GameRegistries`
- [x] Update docstring (DI-S-006) to show proper DI example instead of global resolution
- [x] Verify caller (`empire_panel_window.py`) already passes registries
- [x] Update all test files to pass registries
- [x] Verify: all tests pass

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` - full suite passes (12866 passed, 4 pre-existing bug_13 failures)
- [x] No new `get_default_registry_provider()` calls introduced
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
