# Phase 2: Migrate AIController (Simulation Layer)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-24 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace all direct ship attribute access in controller.py with interface methods

---

## Tasks

### Task 2.1: Migrate position/movement reads [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [ ] Line 105: `self.ship.position` -> `self.ship.get_position()` in `_find_enemies_in_radius`
- [ ] Line 112: `self.ship.position` -> `self.ship.get_position()` in missile query
- [ ] Line 115: `self.ship.team_id` -> `self.ship.get_team_id()` (verify or update)
- [ ] Line 335: `self.ship.position` -> `self.ship.get_position()` in `check_avoidance`
- [ ] Line 350-351: `self.ship.position` -> `self.ship.get_position()` (2 occurrences)
- [ ] Line 359, 362: `self.ship.position` -> `self.ship.get_position()` (2 occurrences)
- [ ] Line 366-368: `self.ship.position` -> `self.ship.get_position()` in `navigate_to` (3 occurrences)

**Notes:**

---

### Task 2.2: Migrate angle/rotation access [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [ ] Line 370: `self.ship.angle` -> `self.ship.get_rotation()` in `navigate_to`
- [ ] Verify Line 375: `self.ship.rotate(direction)` - already interface method, keep as-is
- [ ] Verify Line 379: `self.ship.thrust_forward()` - already interface method, keep as-is

**Notes:**

---

### Task 2.3: Migrate throttle writes [Medium]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [ ] Line 201: `self.ship.turn_throttle = 1.0` -> `self.ship.set_turn_throttle(1.0)`
- [ ] Line 202: `self.ship.engine_throttle = ...` -> `self.ship.set_throttle(...)`
- [ ] Line 291: `self.ship.turn_throttle = min(...)` -> `self.ship.set_turn_throttle(min(...))`
- [ ] Line 305: `self.ship.engine_throttle = ...` -> `self.ship.set_throttle(...)`
- [ ] Line 306: `self.ship.turn_throttle = min(...)` -> `self.ship.set_turn_throttle(min(...))`
- [ ] Line 330: `self.ship.turn_throttle = 1.0` -> `self.ship.set_turn_throttle(1.0)`
- [ ] Line 331: `self.ship.engine_throttle = 1.0` -> `self.ship.set_throttle(1.0)`

**Notes:**

---

### Task 2.4: Migrate formation attribute access [Medium]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [ ] Line 202: `self.ship.formation_members` -> `self.ship.get_formation_members()`
- [ ] Line 205: `self.ship.formation_members` -> `self.ship.get_formation_members()`
- [ ] Line 209: `self.ship.in_formation` -> `self.ship.is_in_formation()`
- [ ] Line 209: `self.ship.formation_master` -> `self.ship.get_formation_master()`
- [ ] Line 216: `self.ship.in_formation` -> `self.ship.is_in_formation()`
- [ ] Line 216: `self.ship.formation_master` -> `self.ship.get_formation_master()`
- [ ] Line 217: `self.ship.formation_master.current_target` - keep as chain (master is raw Ship)
- [ ] Line 227: `self.ship.in_formation` -> `self.ship.is_in_formation()`
- [ ] Line 237: `self.ship.in_formation` -> `self.ship.is_in_formation()`
- [ ] Line 248: `self.ship.in_formation` -> `self.ship.is_in_formation()`
- [ ] Line 248: `self.ship.formation_master` -> `self.ship.get_formation_master()`
- [ ] Line 276: `self.ship.radius` -> `self.ship.get_radius()`
- [ ] Line 278: `self.ship.formation_members` -> `self.ship.get_formation_members()`
- [ ] Line 288: `self.ship.turn_speed` -> `self.ship.get_turn_speed()`
- [ ] Line 294-299: Formation member access - members are raw Ships, keep as-is for member.* access

**Notes:** `formation_master` and `formation_members` return raw Ships, not adapters. Access to their properties remains direct.

---

### Task 2.5: Migrate target and combat attributes [Medium]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [ ] Line 158: `self.ship.max_targets` -> `self.ship.get_max_targets()` (via getattr)
- [ ] Line 163: `self.ship.current_target` -> `self.ship.get_current_target()`
- [ ] Line 219: `self.ship.current_target = master_target` -> `self.ship.set_current_target(master_target)`
- [ ] Line 222: `self.ship.current_target` -> `self.ship.get_current_target()`
- [ ] Line 225: `self.ship.current_target = None` -> `self.ship.set_current_target(None)`
- [ ] Line 229: `self.ship.current_target = target` -> `self.ship.set_current_target(target)`
- [ ] Line 232: `self.ship.max_targets` -> `self.ship.get_max_targets()` (via getattr)
- [ ] Line 233: `self.ship.secondary_targets = ...` -> `self.ship.set_secondary_targets(...)`
- [ ] Line 235: `self.ship.secondary_targets = []` -> `self.ship.set_secondary_targets([])`
- [ ] Line 238: `self.ship.comp_trigger_pulled = False` -> `self.ship.set_trigger_pulled(False)`
- [ ] Line 241: `self.ship.comp_trigger_pulled = True` -> `self.ship.set_trigger_pulled(True)`

**Notes:**

---

### Task 2.6: Migrate remaining attributes [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [ ] Line 197: `self.ship.is_alive` -> `self.ship.is_alive()`
- [ ] Line 285: `self.ship.max_speed` -> `self.ship.get_max_speed()` (via getattr)
- [ ] Line 311-313: `self.ship.get_components_by_ability(...)` -> keep as-is (now interface method)
- [ ] Line 321: `self.ship.in_formation = False` -> `self.ship.set_in_formation(False)`
- [ ] Line 325-326: Unwrap adapter pattern - review but keep (accessing raw ship for removal from list)
- [ ] Line 329: `self.ship.formation_master = None` -> `self.ship.set_formation_master(None)`

**Notes:** Line 325-326 uses `getattr(self.ship, 'ship', self.ship)` to unwrap adapter for list removal - this is intentional.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/ai/ -v` - all AI tests pass
- [ ] Run `pytest tests/integration/test_ai_strategy.py -v` - integration tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
