# Phase 3: Migrate Behaviors (Simulation Layer)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-24 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace all direct ship attribute access in behaviors.py with interface methods

---

## Tasks

### Task 3.1: Migrate FleeBehavior [Simple]
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/test_ai_behaviors.py -v`

- [ ] Line 93: `self.controller.ship.comp_trigger_pulled = fire_while_retreating` -> `self.controller.ship.set_trigger_pulled(fire_while_retreating)`
- [ ] Line 95: `self.controller.ship.position` -> `self.controller.ship.get_position()`
- [ ] Line 99: `self.controller.ship.position` -> `self.controller.ship.get_position()`

**Notes:**

---

### Task 3.2: Migrate KiteBehavior [Simple]
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/test_ai_behaviors.py -v`

- [ ] Line 118: `self.controller.ship.max_weapon_range` -> `self.controller.ship.get_weapon_range()`
- [ ] Line 122: `self.controller.ship.position` -> `self.controller.ship.get_position()`
- [ ] Line 129: `self.controller.ship.position` -> `self.controller.ship.get_position()`

**Notes:**

---

### Task 3.3: Migrate AttackRunBehavior [Simple]
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/test_ai_behaviors.py -v`

- [ ] Line 156: `self.controller.ship.max_weapon_range` -> `self.controller.ship.get_weapon_range()`
- [ ] Line 157: `self.controller.ship.max_weapon_range` -> `self.controller.ship.get_weapon_range()`
- [ ] Line 160: `self.controller.ship.position` -> `self.controller.ship.get_position()`
- [ ] Line 173: `self.controller.ship.position` -> `self.controller.ship.get_position()`

**Notes:**

---

### Task 3.4: Migrate FormationBehavior [Complex - HIGHEST RISK]
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/test_formation_prediction.py -v`

**IMPORTANT:** `master` is a raw Ship (not adapter). Access to `master.*` properties stays direct.

- [ ] Line 196-197: Keep `ship = self.controller.ship` as local reference for readability
- [ ] Line 199: `master.is_alive` - keep as-is (master is raw Ship)
- [ ] Line 200: `ship.in_formation = False` -> `ship.set_in_formation(False)`
- [ ] Line 204: `ship.formation_rotation_mode` - check if needed via interface or keep via getattr
- [ ] Line 205: `ship.formation_offset` -> `ship.get_formation_offset()`
- [ ] Line 207: `ship.formation_offset` -> `ship.get_formation_offset()`
- [ ] Line 209: `master.position` - keep as-is (raw Ship)
- [ ] Line 211: `ship.position` -> `ship.get_position()`
- [ ] Line 212: `ship.radius` -> `ship.get_radius()`
- [ ] Line 215: `master.angle` - keep as-is; `ship.angle` -> `ship.get_rotation()`
- [ ] Line 220: `ship.acceleration_rate` -> `ship.get_acceleration_rate()`
- [ ] Line 229: `ship.turn_speed` -> `ship.get_turn_speed()`
- [ ] Line 229: `ship.turn_throttle` - need getter? Or use getattr pattern
- [ ] Line 237: `ship.angle = master.angle` -> `ship.set_rotation(master.angle)`
- [ ] Line 240: `ship.rotate(direction)` - already interface method
- [ ] Line 248: `master.is_thrusting` - keep as-is (raw Ship)
- [ ] Line 250: `master.max_speed`, `master.engine_throttle` - keep as-is (raw Ship)
- [ ] Line 253: `ship.max_speed` -> `ship.get_max_speed()`
- [ ] Line 256: `ship.engine_throttle = ...` -> `ship.set_throttle(...)`
- [ ] Line 260: `ship.thrust_forward()` - already interface method
- [ ] Line 268: `master.position` - keep as-is (raw Ship)
- [ ] Line 270-273: `ship.formation_offset` -> `ship.get_formation_offset()`
- [ ] Line 277: `ship.position` -> `ship.get_position()`
- [ ] Line 294: `ship.position += correction` -> `ship.adjust_position(correction)`
- [ ] Line 301: `master.position`, `master.current_speed`, `master.angle` - keep as-is (raw Ship)
- [ ] Line 303-306: `ship.formation_offset` -> `ship.get_formation_offset()`

**Notes:** This is the highest-risk task. Test thoroughly with formation scenarios after completion.

---

### Task 3.5: Migrate test/debug behaviors [Simple]
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [ ] Line 322: DoNothingBehavior `self.controller.ship.comp_trigger_pulled = False` -> `self.controller.ship.set_trigger_pulled(False)`
- [ ] Line 340: StraightLineBehavior `thrust_forward()` - verify already interface method
- [ ] Line 350: RotateOnlyBehavior `rotate()` - verify already interface method
- [ ] Line 390: ErraticBehavior `rotate()` - verify already interface method
- [ ] Line 393: ErraticBehavior `thrust_forward()` - verify already interface method
- [ ] Line 407-408: OrbitBehavior `ship = self.controller.ship` - keep local reference
- [ ] Line 408: `target.position` - target is raw entity, keep as-is
- [ ] Line 409: `ship.position` -> `ship.get_position()`
- [ ] Line 431: `ship.position` -> `ship.get_position()`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/ai/ -v` - all AI tests pass
- [ ] Run `pytest tests/unit/ai/test_formation_prediction.py -v` - formation tests pass
- [ ] Run `pytest tests/integration/test_ai_strategy.py -v` - integration tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
