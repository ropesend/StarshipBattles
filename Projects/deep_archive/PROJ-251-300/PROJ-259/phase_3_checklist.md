# Phase 3: Battle Engine Tick Phases

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-259 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create an `ITickPhase` protocol and `TickPhaseRegistry` in `game/simulation/systems/tick_phase.py`, implement 5 default phase classes matching the current `BattleEngine.update()` sequence, then refactor `BattleEngine.update()` to delegate to the registry.

---

## Tasks

### Task 3.1: Write Tests for ITickPhase and TickPhaseRegistry [Medium]
**File:** `tests/unit/simulation/systems/test_tick_phases.py` (NEW)
**Tests:** `pytest tests/unit/simulation/systems/test_tick_phases.py`

- [ ] Create test file `tests/unit/simulation/systems/test_tick_phases.py`
- [ ] Test: TickPhaseRegistry starts empty
- [ ] Test: `register()` adds a phase
- [ ] Test: `phases` property returns phases sorted by priority (ascending)
- [ ] Test: `execute_all()` calls `execute()` on each phase in priority order
- [ ] Test: phases with same priority maintain insertion order (stable sort)
- [ ] Test: registering multiple phases with different priorities sorts correctly
- [ ] Test: ITickPhase protocol is satisfied by classes with name, priority, execute
- [ ] Test: custom phase can be registered and executed alongside defaults
- [ ] Test: phase receives BattleEngine instance in `execute()`
- [ ] Run tests -- confirm all fail (no implementation yet)

**Notes:** Use mock phases for registry tests (Mock objects with name, priority, execute attributes). Use `@runtime_checkable` to test protocol compliance.

---

### Task 3.2: Implement ITickPhase Protocol and TickPhaseRegistry [Simple]
**File:** `game/simulation/systems/tick_phase.py` (NEW)
**Tests:** `pytest tests/unit/simulation/systems/test_tick_phases.py`

- [ ] Create `game/simulation/systems/tick_phase.py`
- [ ] Define `ITickPhase` as `@runtime_checkable Protocol` with `name: str` (property), `priority: int` (property), `execute(engine) -> None`
- [ ] Implement `TickPhaseRegistry` with `register(phase)`, `execute_all(engine)`, `phases` property
- [ ] `register()` inserts and re-sorts by priority (ascending). Use `bisect` or simple sort.
- [ ] `execute_all()` iterates `self._phases` and calls `phase.execute(engine)` for each
- [ ] Add type hints and docstrings
- [ ] Run registry/protocol tests -- confirm they pass
- [ ] Add `ITickPhase`, `TickPhaseRegistry` to `game/simulation/__init__.py` exports

**Notes:** Follow the pattern from `battle_end_conditions.py` (IEndCondition protocol + concrete classes).

---

### Task 3.3: Implement Default Phase Classes [Medium]
**File:** `game/simulation/systems/tick_phase.py` (append to same file)
**Tests:** `tests/unit/simulation/systems/test_tick_phases.py` + `tests/unit/simulation/systems/test_battle_engine_tick.py`

- [ ] Implement `RebuildGridPhase` (priority=100): calls `engine._rebuild_grid()`, stores result on engine as `engine._alive_ships_cache`
- [ ] Implement `AIAndShipUpdatePhase` (priority=200): calls `engine._update_ai_and_ships()`
- [ ] Implement `AttackProcessingPhase` (priority=300): calls `engine._collect_new_attacks(engine._alive_ships_cache)` then `engine._process_attacks(attacks)`
- [ ] Implement `RammingPhase` (priority=400): calls `engine.collision_system.process_ramming(engine.ships, engine.logger)`
- [ ] Implement `ProjectileUpdatePhase` (priority=500): calls `engine.projectile_manager.update(engine.grid)`
- [ ] Write tests for each default phase: verify it calls the expected engine methods
- [ ] Write test: `create_default_phases()` returns registry with all 5 phases in correct order
- [ ] Run tests -- confirm all pass

**Notes:** Each phase class is a thin wrapper (~5-10 lines). The real logic stays in BattleEngine's private methods. The `_alive_ships_cache` attribute on engine is set by RebuildGridPhase and consumed by AttackProcessingPhase within the same tick.

---

### Task 3.4: Refactor BattleEngine.update() to Use TickPhaseRegistry [Medium]
**File:** `game/simulation/systems/battle_engine.py` (lines 172-438)
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_tick.py` + full suite

- [ ] Add `_tick_phases: TickPhaseRegistry` attribute to `BattleEngine.__init__()` (line 172)
- [ ] Add `_create_default_phases()` method that creates a `TickPhaseRegistry` with the 5 default phases
- [ ] Call `_create_default_phases()` in `__init__()` to initialize `self._tick_phases`
- [ ] Add optional `tick_phases: Optional[TickPhaseRegistry]` parameter to `__init__()` for custom phase injection
- [ ] Refactor `update()` method (line 406-438): replace inline code with `self._tick_phases.execute_all(self)`
- [ ] Keep `_rebuild_grid()`, `_update_ai_and_ships()`, `_collect_new_attacks()`, `_process_attacks()` as private methods (phases delegate to them)
- [ ] Add `_alive_ships_cache` attribute initialized in `update()` (before execute_all) or in RebuildGridPhase
- [ ] Verify `update()` still: (a) checks `is_battle_over()`, (b) increments `tick_counter`, (c) clears `recent_beams`
- [ ] Update existing tests in `tests/unit/simulation/systems/test_battle_engine_tick.py` if mocking assumptions changed
- [ ] Run targeted tests: `pytest tests/unit/simulation/systems/`
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py`

**Notes:** The `update()` method retains the early-return check and counter increment. Only the 5-phase body is delegated. Existing private methods are unchanged -- phases just call them.

---

### Task 3.5: Write Integration Test for Custom Phase Injection [Simple]
**File:** `tests/unit/simulation/systems/test_tick_phases.py`
**Tests:** `pytest tests/unit/simulation/systems/test_tick_phases.py`

- [ ] Test: BattleEngine with custom tick_phases parameter uses those phases instead of defaults
- [ ] Test: custom phase inserted at priority 150 runs between RebuildGrid (100) and AIUpdate (200)
- [ ] Test: BattleEngine with empty TickPhaseRegistry does nothing in update() (no crash)

**Notes:** This verifies the extensibility use case -- the reason we created the abstraction.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `ITickPhase` and `TickPhaseRegistry` exist in `game/simulation/systems/tick_phase.py`
- [ ] 5 default phase classes exist: RebuildGridPhase, AIAndShipUpdatePhase, AttackProcessingPhase, RammingPhase, ProjectileUpdatePhase
- [ ] `BattleEngine.update()` delegates to `TickPhaseRegistry.execute_all()`
- [ ] `BattleEngine.__init__()` accepts optional `tick_phases` parameter
- [ ] All tests pass: `python Tools/test_sharded/test_sharded.py`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
