# Phase 7: Combat Layer Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-189 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Apply storm shield interference during tactical combat in storm hexes.

---

## Tasks

### Task 7.1: Pass storm effects to battle resolver [Medium]
**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/conflict_resolution/test_storm_integration.py`

- [x] Read current `ConflictResolutionEngine` to understand how battles are triggered and resolved
- [x] Read `resolve_all_conflicts()` method to understand the combat location resolution flow
- [x] Accept optional `area_effect_manager: AreaEffectManager = None` in constructor
- [x] Before calling battle resolver for a conflict at a hex:
  - Query `area_effect_manager.get_effects_at_global_hex(galaxy, conflict_hex)` to get environmental effects
  - Pass `environmental_effects` to the battle resolver call
- [x] Write test: conflict resolution passes environmental effects to battle resolver when in storm hex
- [x] Write test: conflict resolution passes neutral effects when not in storm hex
- [x] Run existing conflict resolution tests

**Implementation Notes:**
- Added `area_effect_manager` and `_galaxy` attributes to ConflictResolutionEngine
- Modified `resolve_all_conflicts()` to accept optional `galaxy` parameter
- Modified `_resolve_combat_simulated()` to query environmental effects and pass to resolver
- Updated IConflictEngine interface to include galaxy parameter
- Updated TurnEngine to pass galaxy to resolve_all_conflicts and inject AreaEffectManager

### Task 7.2: Apply shield_capacity_mult in combat simulation [Medium]
**File:** `game/strategy/adapters/simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/adapters/test_simulation_adapter_storms.py`

- [x] Read current `SimulationBattleResolver` to understand how battles are set up
- [x] Accept optional `environmental_effects: EnvironmentalEffects = None` parameter in the resolve method
- [x] Before combat simulation starts, if `environmental_effects` has `shield_capacity_mult != 1.0`:
  - Apply shield multiplier directly to ship.max_shields
  - Cap ship.current_shields to new max
- [x] Write test: ships fighting in storm hex with shield_capacity_mult=0.5 have halved shield capacity during combat
- [x] Write test: ships fighting outside storm have normal shields
- [x] Write test: shield stats are properly restored after combat (N/A - ships are converted fresh each battle)
- [x] Run existing battle resolution tests

**Implementation Notes:**
- Added `environmental_effects` parameter to IBattleResolver.resolve_battle()
- Added `_apply_shield_interference()` helper method to SimulationBattleResolver
- Shield reduction applied after ship conversion, before battle starts
- Updated existing mock resolvers in tests to accept new parameter

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: 12,705 passed, 1 skipped
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 8
