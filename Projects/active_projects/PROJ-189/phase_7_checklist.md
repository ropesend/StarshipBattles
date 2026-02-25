# Phase 7: Combat Layer Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-189 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Apply storm shield interference during tactical combat in storm hexes.

---

## Tasks

### Task 7.1: Pass storm effects to battle resolver [Medium]
**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_conflict_resolution_engine.py`

- [ ] Read current `ConflictResolutionEngine` to understand how battles are triggered and resolved
- [ ] Read `resolve_all_conflicts()` method to understand the combat location resolution flow
- [ ] Accept optional `area_effect_manager: AreaEffectManager = None` in constructor
- [ ] Before calling battle resolver for a conflict at a hex:
  - Query `area_effect_manager.get_effects_at_global_hex(galaxy, conflict_hex)` to get environmental effects
  - Pass `environmental_effects` to the battle resolver call
- [ ] Write test: conflict resolution passes environmental effects to battle resolver when in storm hex
- [ ] Write test: conflict resolution passes neutral effects when not in storm hex
- [ ] Run existing conflict resolution tests

**Notes:** This phase requires understanding the full combat resolution pipeline. Read `conflict_resolution_engine.py` and `simulation_adapter.py` carefully.

### Task 7.2: Apply shield_capacity_mult in combat simulation [Medium]
**File:** `game/strategy/adapters/simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/adapters/ tests/integration/`

- [ ] Read current `SimulationBattleResolver` to understand how battles are set up
- [ ] Accept optional `environmental_effects: EnvironmentalEffects = None` parameter in the resolve method
- [ ] Before combat simulation starts, if `environmental_effects` has `shield_capacity_mult != 1.0`:
  - For each participating ship:
    - Access shield components and apply `shield_capacity_mult` to their stats
    - Use the stat modification pipeline: `component.stats['shield_capacity_mult'] = effects.shield_capacity_mult`
    - Call `component.recalculate()` to update derived values
  - This ensures shields are reduced during the entire battle
- [ ] After combat completes, restore original shield_capacity_mult to 1.0 (so saved stats aren't permanently modified)
- [ ] Write test: ships fighting in storm hex with shield_capacity_mult=0.5 have halved shield capacity during combat
- [ ] Write test: ships fighting outside storm have normal shields
- [ ] Write test: shield stats are properly restored after combat
- [ ] Run existing battle resolution tests

**Notes:** The exact mechanism for applying shield_capacity_mult depends on how the simulation adapter sets up ship instances for combat. Need to understand the component stats pipeline. Phase 3 adds the stat key; this phase uses it.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 8
