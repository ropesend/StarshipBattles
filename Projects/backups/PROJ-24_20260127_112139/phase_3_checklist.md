# Phase 3: Migrate Behaviors (Simulation Layer)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-24 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace all direct ship attribute access in behaviors.py with interface methods

---

## Tasks

### Task 3.1: Migrate FleeBehavior [Simple] - COMPLETE
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/test_ai_behaviors.py -v`

- [x] Line 93: `self.controller.ship.comp_trigger_pulled = fire_while_retreating` -> `self.controller.ship.set_trigger_pulled(fire_while_retreating)`
- [x] Line 95: `self.controller.ship.position` -> `self.controller.ship.get_position()`
- [x] Line 99: `self.controller.ship.position` -> `self.controller.ship.get_position()`

---

### Task 3.2: Migrate KiteBehavior [Simple] - COMPLETE
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/test_ai_behaviors.py -v`

- [x] Line 118: `self.controller.ship.max_weapon_range` -> `self.controller.ship.get_weapon_range()`
- [x] Line 122: `self.controller.ship.position` -> `self.controller.ship.get_position()`
- [x] Line 129: `self.controller.ship.position` -> `self.controller.ship.get_position()`

---

### Task 3.3: Migrate AttackRunBehavior [Simple] - COMPLETE
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/test_ai_behaviors.py -v`

- [x] Line 156-157: `self.controller.ship.max_weapon_range` -> `self.controller.ship.get_weapon_range()`
- [x] Line 160, 173: `self.controller.ship.position` -> `self.controller.ship.get_position()`

---

### Task 3.4: Migrate FormationBehavior [Complex] - COMPLETE
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/test_formation_prediction.py -v`

All migrations complete. Key points:
- `master` remains raw Ship (intentional - formation_master returns raw Ship)
- All ship.* accesses now use interface methods
- Test fixtures updated with interface method mocks and side_effects

---

### Task 3.5: Migrate test/debug behaviors [Simple] - COMPLETE
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [x] DoNothingBehavior: `set_trigger_pulled(False)`
- [x] StraightLineBehavior: `thrust_forward()` (already interface)
- [x] RotateOnlyBehavior: `rotate()` (already interface)
- [x] ErraticBehavior: `rotate()` and `thrust_forward()` (already interface)
- [x] OrbitBehavior: `ship.get_position()`

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/ai/ -v` - 214 AI tests pass
- [x] Run `pytest tests/unit/ai/test_formation_prediction.py -v` - 30 formation tests pass
- [x] Run `pytest tests/integration/test_ai_strategy.py -v` - integration tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State
