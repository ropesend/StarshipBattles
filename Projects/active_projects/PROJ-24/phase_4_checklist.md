# Phase 4: Migrate core/system.py and core/behaviors.py (UI Layer)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-24 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace all direct ship attribute access in the UI-layer AI implementation

---

## Tasks

### Task 4.1: Migrate core/system.py AIController - Position/Movement [Medium]
**File:** `game/ai/core/system.py`
**Tests:** `pytest tests/ -v`

- [x] Find all `self.ship.position` accesses and replace with `self.ship.get_position()`
- [x] Find all `self.ship.angle` accesses and replace with `self.ship.get_rotation()`
- [x] Find all `self.ship.velocity` accesses and replace with `self.ship.get_velocity()`
- [x] Find all `self.ship.radius` accesses and replace with `self.ship.get_radius()`

**Notes:** Migrated all position/movement accesses in find_target, find_secondary_targets, check_avoidance, navigate_to, _handle_formation_master.

---

### Task 4.2: Migrate core/system.py AIController - Throttles [Medium]
**File:** `game/ai/core/system.py`
**Tests:** `pytest tests/ -v`

- [x] Find all `self.ship.turn_throttle = ...` and replace with `self.ship.set_turn_throttle(...)`
- [x] Find all `self.ship.engine_throttle = ...` and replace with `self.ship.set_throttle(...)`
- [x] Verify `self.ship.rotate()` and `self.ship.thrust_forward()` are already interface methods

**Notes:** Migrated all throttle writes in update(), _handle_formation_master(), _check_formation_integrity().

---

### Task 4.3: Migrate core/system.py AIController - State/Identity [Simple]
**File:** `game/ai/core/system.py`
**Tests:** `pytest tests/ -v`

- [x] Find all `self.ship.is_alive` and replace with `self.ship.is_alive()`
- [x] Find all `self.ship.team_id` and replace with `self.ship.get_team_id()`

**Notes:** Migrated is_alive check in update() and team_id comparisons in find_target/find_secondary_targets.

---

### Task 4.4: Migrate core/system.py AIController - Formation [Medium]
**File:** `game/ai/core/system.py`
**Tests:** `pytest tests/ -v`

- [x] Find all `self.ship.in_formation` reads and replace with `self.ship.is_in_formation()`
- [x] Find all `self.ship.in_formation = ...` writes and replace with `self.ship.set_in_formation(...)`
- [x] Find all `self.ship.formation_master` reads and replace with `self.ship.get_formation_master()`
- [x] Find all `self.ship.formation_master = ...` writes and replace with `self.ship.set_formation_master(...)`
- [x] Find all `self.ship.formation_members` reads and replace with `self.ship.get_formation_members()`
- [x] Find all `self.ship.formation_offset` reads and replace with `self.ship.get_formation_offset()`

**Notes:** Migrated all formation accesses. Remember: formation_master and formation_members return raw Ships, so their properties are accessed directly.

---

### Task 4.5: Migrate core/system.py AIController - Combat [Medium]
**File:** `game/ai/core/system.py`
**Tests:** `pytest tests/ -v`

- [x] Find all `self.ship.current_target` reads and replace with `self.ship.get_current_target()`
- [x] Find all `self.ship.current_target = ...` writes and replace with `self.ship.set_current_target(...)`
- [x] Find all `self.ship.comp_trigger_pulled = ...` and replace with `self.ship.set_trigger_pulled(...)`
- [x] Find all `self.ship.max_targets` and replace with `self.ship.get_max_targets()`
- [x] Find all `self.ship.secondary_targets` reads/writes and replace with interface methods

**Notes:** Migrated all combat accesses in update() and find_secondary_targets().

---

### Task 4.6: Migrate core/system.py AIController - Component Access [Medium]
**File:** `game/ai/core/system.py`
**Tests:** `pytest tests/ -v`

- [x] Find all `self.ship.layers` accesses (3 occurrences) and replace with `self.ship.get_layers()`
- [x] Find all `self.ship.get_components_by_ability(...)` - should already be interface method after Phase 1

**Notes:** Migrated layers access in _check_formation_integrity(). get_components_by_ability already uses interface.

---

### Task 4.7: Migrate core/behaviors.py [Medium]
**File:** `game/ai/core/behaviors.py`
**Tests:** `pytest tests/ -v`

Apply the same migration pattern as Phase 3:

- [x] Migrate all `ship.position` -> `ship.get_position()`
- [x] Migrate all `ship.angle` reads -> `ship.get_rotation()`
- [x] Migrate all `ship.angle = ...` writes -> `ship.set_rotation(...)`
- [x] Migrate all throttle writes to setter methods
- [x] Migrate all formation attribute access to interface methods
- [x] Migrate FormationBehavior (if present and different from main behaviors.py)
- [x] Migrate `ship.position += ...` -> `ship.adjust_position(...)`

**Notes:** Migrated FleeBehavior, KiteBehavior, AttackRunBehavior, FormationBehavior, DoNothingBehavior, OrbitBehavior. Note: FormationBehavior's `master` is a raw Ship (from get_formation_master()), so its properties are accessed directly.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/ai/ -v` - all AI tests pass (214 passed)
- [x] Run `pytest tests/integration/ -v` - integration tests pass
- [x] Run `pytest tests/ -v` - full test suite passes (4593 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
