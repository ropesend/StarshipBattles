# Phase 5: TurnEngine Per-Tick Processing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-08 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add per-tick resource consumption for `per_turn` trigger

---

## Tasks

### Task 5.1: Add Per-Turn Resource Processing Method [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Add `_process_per_turn_resources()` method

**Notes:** Lines 404-433 implement the method

### Task 5.2: Add Auto-Disable Helper [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Add `_auto_disable_components_for_resource()` helper

**Notes:** Lines 435-471 implement the helper

### Task 5.3: Integrate Per-Turn Processing into Tick Loop [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] In `_process_tick()`, add call at start of tick as Phase 0

**Notes:** Lines 243-244 call `_process_per_turn_resources()` as Phase 0

### Task 5.4: Update Movement Processing to Use Generic Methods [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Update fuel check to use `has_resources_for_movement()`
- [x] Update fuel consumption to use `consume_movement_resources(1)`

**Notes:** Line 287 uses `has_resources_for_movement()`, line 305 uses `consume_movement_resources(1)`

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
