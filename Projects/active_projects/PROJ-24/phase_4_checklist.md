# Phase 4: Migrate core/system.py and core/behaviors.py (UI Layer)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-24 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace all direct ship attribute access in the UI-layer AI implementation

---

## Tasks

### Task 4.1: Migrate core/system.py AIController - Position/Movement [Medium]
**File:** `game/ai/core/system.py`
**Tests:** `pytest tests/ -v`

- [ ] Find all `self.ship.position` accesses and replace with `self.ship.get_position()`
- [ ] Find all `self.ship.angle` accesses and replace with `self.ship.get_rotation()`
- [ ] Find all `self.ship.velocity` accesses and replace with `self.ship.get_velocity()`
- [ ] Find all `self.ship.radius` accesses and replace with `self.ship.get_radius()`

**Notes:** Use grep to find all occurrences: `grep -n "self\.ship\." game/ai/core/system.py`

---

### Task 4.2: Migrate core/system.py AIController - Throttles [Medium]
**File:** `game/ai/core/system.py`
**Tests:** `pytest tests/ -v`

- [ ] Find all `self.ship.turn_throttle = ...` and replace with `self.ship.set_turn_throttle(...)`
- [ ] Find all `self.ship.engine_throttle = ...` and replace with `self.ship.set_throttle(...)`
- [ ] Verify `self.ship.rotate()` and `self.ship.thrust_forward()` are already interface methods

**Notes:**

---

### Task 4.3: Migrate core/system.py AIController - State/Identity [Simple]
**File:** `game/ai/core/system.py`
**Tests:** `pytest tests/ -v`

- [ ] Find all `self.ship.is_alive` and replace with `self.ship.is_alive()`
- [ ] Find all `self.ship.team_id` and replace with `self.ship.get_team_id()`

**Notes:**

---

### Task 4.4: Migrate core/system.py AIController - Formation [Medium]
**File:** `game/ai/core/system.py`
**Tests:** `pytest tests/ -v`

- [ ] Find all `self.ship.in_formation` reads and replace with `self.ship.is_in_formation()`
- [ ] Find all `self.ship.in_formation = ...` writes and replace with `self.ship.set_in_formation(...)`
- [ ] Find all `self.ship.formation_master` reads and replace with `self.ship.get_formation_master()`
- [ ] Find all `self.ship.formation_master = ...` writes and replace with `self.ship.set_formation_master(...)`
- [ ] Find all `self.ship.formation_members` reads and replace with `self.ship.get_formation_members()`
- [ ] Find all `self.ship.formation_offset` reads and replace with `self.ship.get_formation_offset()`

**Notes:** Remember `formation_master` and `formation_members` return raw Ships.

---

### Task 4.5: Migrate core/system.py AIController - Combat [Medium]
**File:** `game/ai/core/system.py`
**Tests:** `pytest tests/ -v`

- [ ] Find all `self.ship.current_target` reads and replace with `self.ship.get_current_target()`
- [ ] Find all `self.ship.current_target = ...` writes and replace with `self.ship.set_current_target(...)`
- [ ] Find all `self.ship.comp_trigger_pulled = ...` and replace with `self.ship.set_trigger_pulled(...)`
- [ ] Find all `self.ship.max_targets` and replace with `self.ship.get_max_targets()`
- [ ] Find all `self.ship.secondary_targets` reads/writes and replace with interface methods

**Notes:**

---

### Task 4.6: Migrate core/system.py AIController - Component Access [Medium]
**File:** `game/ai/core/system.py`
**Tests:** `pytest tests/ -v`

- [ ] Find all `self.ship.layers` accesses (3 occurrences) and replace with `self.ship.get_layers()`
- [ ] Find all `self.ship.get_components_by_ability(...)` - should already be interface method after Phase 1

**Notes:**

---

### Task 4.7: Migrate core/behaviors.py [Medium]
**File:** `game/ai/core/behaviors.py`
**Tests:** `pytest tests/ -v`

Apply the same migration pattern as Phase 3:

- [ ] Migrate all `ship.position` -> `ship.get_position()`
- [ ] Migrate all `ship.angle` reads -> `ship.get_rotation()`
- [ ] Migrate all `ship.angle = ...` writes -> `ship.set_rotation(...)`
- [ ] Migrate all throttle writes to setter methods
- [ ] Migrate all formation attribute access to interface methods
- [ ] Migrate FormationBehavior (if present and different from main behaviors.py)
- [ ] Migrate `ship.position += ...` -> `ship.adjust_position(...)`

**Notes:** Use grep to find all patterns: `grep -n "ship\." game/ai/core/behaviors.py`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/ai/ -v` - all AI tests pass
- [ ] Run `pytest tests/integration/ -v` - integration tests pass
- [ ] Run `pytest tests/ -v` - full test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
