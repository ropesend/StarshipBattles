# Phase 1: GameSession Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-211 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Establish registries on GameSession and wire to TurnEngine + Facade
**Priority:** Immediate - Foundation for all subsequent phases
**Risk:** Low

---

## Tasks

### Task 1.1: Add `registries` property to GameSession [DI-S-003, AR-004]
**Files:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/engine/`

- [ ] Read `game_session.py` to understand current constructor and `from_dict()`
- [ ] Add `_registries` field, resolve once at init time from `get_default_registry_provider()`
- [ ] Expose via `registries` property
- [ ] Pass `registries=self._registries` to `TurnEngine()` in both `__init__()` and `from_dict()`
- [ ] Write test verifying GameSession.registries is populated
- [ ] Verify: `pytest tests/ -n 12` passes

### Task 1.2: Make TurnEngine `registries` required [DI-S-003, DI-S-007]
**Files:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/`

- [ ] Change `registries: Optional[GameRegistries] = None` to `registries: GameRegistries`
- [ ] Remove the fallback block (lines 164-170)
- [ ] Update docstring (DI-S-007) to remove "Falls back to..." language
- [ ] Update `create_default_turn_engine()` factory if it exists
- [ ] Verify: all tests pass

### Task 1.3: Fix StrategySessionFacade.get_fleet_remaining_pods() [DI-S-004, AR-005]
**Files:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/`

- [ ] Replace inline `get_default_registry_provider()` call with `self._session.registries.components`
- [ ] Remove the broad try/except error swallowing (lines 501-506)
- [ ] Remove unused `get_default_registry_provider` import if no other usages
- [ ] Verify: all tests pass

### Task 1.4: Make ShipInstance.to_ship() registries required [DI-S-005]
**Files:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/`

- [ ] Change `registries: Optional[GameRegistries] = None` to `registries: GameRegistries` on `to_ship()`
- [ ] Remove "Phase 6" docstring comment about transitional state
- [ ] Verify existing callers (FleetBattleAdapter, SimulationAdapter) already pass registries
- [ ] Verify: all tests pass

### Task 1.5: Make EmpireEconomyCalculator registries required [DI-S-008]
**Files:** `game/strategy/engine/empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/`

- [ ] Change `registries: Optional[GameRegistries] = None` to `registries: GameRegistries`
- [ ] Update docstring (DI-S-006) to show proper DI example instead of global resolution
- [ ] Verify caller (`empire_panel_window.py`) already passes registries
- [ ] Verify: all tests pass

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` - full suite passes
- [ ] No new `get_default_registry_provider()` calls introduced
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
