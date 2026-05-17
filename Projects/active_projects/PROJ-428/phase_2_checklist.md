# Phase 2: Move planet-modifier engine resolution onto `TurnEngine`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-428 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/turn_engine.py`
- `game/strategy/engine/turn_phase_registry.py`
- `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
- `tests/unit/strategy/engine/test_no_lazy_fallback_init.py`

**Objective:** Move `_resolve_planet_modifier_effects` out of the registry by
adding a `TurnEngine.planet_modifier_effect_engine` lazy property and
repointing the descriptor resolver. **Do not** add a new `TurnEngineConfig`
field.

---

## Tasks

### Task 2.1: Red test — registry no longer imports `PlanetModifierEffectEngine` [Simple]
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`

- [ ] Add a failing test that imports `game.strategy.engine.turn_phase_registry`,
      walks the module AST, and asserts no top-level import resolves to
      `PlanetModifierEffectEngine`.
- [ ] Confirm the test fails against current code for the intended reason.

**Notes:**

### Task 2.2: Add `TurnEngine.planet_modifier_effect_engine` lazy property [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py tests/unit/strategy/engine/test_no_lazy_fallback_init.py`

- [ ] Add a lazy property on `TurnEngine` that constructs and caches a
      `PlanetModifierEffectEngine`.
- [ ] Add unit coverage that the property returns the same instance on
      repeated access (cache works).
- [ ] Confirm no new `TurnEngineConfig` field was added (run
      `test_turn_engine_config.py`).
- [ ] Confirm `test_no_lazy_fallback_init.py` is still green.

**Notes:**

### Task 2.3: Repoint descriptor resolver [Simple]
**File:** `game/strategy/engine/turn_phase_registry.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_default_tick_phase_list.py tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py`

- [ ] Change the descriptor for the planet-modifier phase to
      `lambda e: e.planet_modifier_effect_engine.process_modifier_effects_tick`.
- [ ] Confirm `DEFAULT_TICK_PHASE_LIST` and
      `DEFAULT_END_OF_TURN_PHASE_LIST` golden tests stay green.

**Notes:**

### Task 2.4: Delete `_resolve_planet_modifier_effects` [Simple]
**File:** `game/strategy/engine/turn_phase_registry.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -x`

- [ ] Remove `_resolve_planet_modifier_effects` from
      `turn_phase_registry.py`.
- [ ] Remove the `PlanetModifierEffectEngine` import from
      `turn_phase_registry.py`.
- [ ] Confirm the Task 2.1 AST test now passes.
- [ ] Verify: focused turn-engine suite is green.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/turn_engine/ -x` is green
- [ ] `pytest tests/unit/strategy/engine/test_turn_engine_config.py tests/unit/strategy/engine/test_no_lazy_fallback_init.py -x` is green
- [ ] Update status at top of this file to `Complete (Committed)`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
