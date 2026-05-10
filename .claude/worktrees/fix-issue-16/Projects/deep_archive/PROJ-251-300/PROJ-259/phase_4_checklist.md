# Phase 4: Documentation + Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-259 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all affected documentation to reflect the three new abstractions. Run final verification to confirm zero regressions and all project goals are met.

---

## Tasks

### Task 4.1: Update Architecture Documentation [Simple]
**File:** `docs/01_ARCHITECTURE.md`
**Tests:** N/A (documentation only)

- [ ] Add `state_machine.py` to `game/core/` package table with description: "ScreenStateMachine -- generic state machine with transition table, guards, state stack"
- [ ] Add `turn_engine_config.py` to `game/strategy/engine/` subpackage description
- [ ] Add `tick_phase.py` to `game/simulation/systems/` subpackage description
- [ ] Update Entry Point section (line 406): mention that `Game` uses `ScreenStateMachine` for scene transitions
- [ ] Update `game.simulation` exports if `ITickPhase` and `TickPhaseRegistry` were added
- [ ] Verify the Strategy Turn Flow diagram still accurately describes TurnEngine behavior (no phase order changes)
- [ ] Verify the Battle Flow diagram still accurately describes BattleEngine behavior

**Notes:** The architecture doc must stay accurate. Three new files, no behavioral changes.

---

### Task 4.2: Update Patterns Documentation [Simple]
**File:** `docs/02_PATTERNS.md`
**Tests:** N/A (documentation only)

- [ ] Add new pattern section: "State Machine (ScreenStateMachine)" with Where, How It Works, When to Use
  - Where: `game/core/state_machine.py`
  - How: transition table, guards, state stack, on_enter/on_exit hooks
  - When: managing finite state transitions with explicit allowed transitions
- [ ] Add new pattern section: "Configuration Bundling (TurnEngineConfig)" under existing "Configuration Classes" pattern (pattern #12)
  - Where: `game/strategy/engine/turn_engine_config.py`
  - How: frozen dataclass bundling optional engine parameters
  - When: constructor has many optional parameters of the same kind
- [ ] Add new pattern section: "Tick Phase Registry" with Where, How It Works, When to Use
  - Where: `game/simulation/systems/tick_phase.py`
  - How: ITickPhase protocol, priority ordering, TickPhaseRegistry
  - When: ordered processing pipeline that needs to be extensible
- [ ] Update Table of Contents at top of file
- [ ] Update pattern count in file header (currently says "20 patterns")

**Notes:** Follow the existing pattern section format exactly.

---

### Task 4.3: Update Strategy Layer Documentation [Simple]
**File:** `docs/systems/strategy_layer.md`
**Tests:** N/A (documentation only)

- [ ] Update TurnEngine section to document the new constructor signature (4 params instead of 20)
- [ ] Document `TurnEngineConfig` dataclass: fields, frozen semantics, None-means-default convention
- [ ] Update `create_default_turn_engine()` documentation to show optional config parameter
- [ ] Update any example code that shows TurnEngine constructor calls

**Notes:** The strategy_layer.md documents the TurnEngine API. Constructor change must be reflected.

---

### Task 4.4: Update Combat Simulation Documentation [Simple]
**File:** `docs/systems/combat_simulation.md`
**Tests:** N/A (documentation only)

- [ ] Document the `ITickPhase` protocol and `TickPhaseRegistry`
- [ ] Document the 5 default phases with their priorities and what they do
- [ ] Document how to add a custom tick phase (register with appropriate priority)
- [ ] Document the `tick_phases` parameter on `BattleEngine.__init__()`
- [ ] Verify the tick sequence description matches the 5-phase implementation

**Notes:** The combat_simulation.md documents BattleEngine. Tick phase system must be described.

---

### Task 4.5: Final Verification [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py`
- [ ] Verify test count is >= 14783 (baseline from CLAUDE.md)
- [ ] Verify 0 failures, 0 errors
- [ ] Verify `_switch_scene()` method does not exist in `game/app.py`
- [ ] Verify `TurnEngine.__init__()` has exactly 5 parameters (battle_resolver, registries, config, ai_factory, event_bus)
- [ ] Verify `BattleEngine.update()` delegates to `TickPhaseRegistry.execute_all()`
- [ ] Verify all new files exist:
  - `game/core/state_machine.py`
  - `game/strategy/engine/turn_engine_config.py`
  - `game/simulation/systems/tick_phase.py`
  - `tests/unit/core/test_state_machine.py`
  - `tests/unit/strategy/engine/test_turn_engine_config.py`
  - `tests/unit/simulation/systems/test_tick_phases.py`

**Notes:** This is the final verification before marking the project complete.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 4 documentation files updated
- [ ] Full test suite passes with 0 failures
- [ ] All project goals from plan.md verified
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
- [ ] Update plan.md Verification section -- check all boxes
