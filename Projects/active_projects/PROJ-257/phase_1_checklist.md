# Phase 1: DamageContext Move + PhysicsBody Boundary

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-257 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the Engine->Simulation layer violation by moving DamageContext to core. Clarify the PhysicsBody boundary by removing dead code and documenting the arcade physics model.

---

## Tasks

### Task 1.1: Create `game/core/combat_types.py` with DamageContext [Simple]
**File:** `game/core/combat_types.py` (new)
**Tests:** `tests/unit/core/test_combat_types.py` (new)

**TDD Steps:**
- [ ] Create test file `tests/unit/core/test_combat_types.py` with tests for DamageContext:
  - Test creation with all fields (attacker, source_weapon, damage_type)
  - Test creation with defaults (all None/unknown)
  - Test frozen immutability (assignment raises FrozenInstanceError)
  - Test import path: `from game.core.combat_types import DamageContext`
- [ ] Run tests, confirm they fail: `pytest tests/unit/core/test_combat_types.py -x`
- [ ] Create `game/core/combat_types.py` containing the `DamageContext` frozen dataclass (copy from `game/simulation/combat/combat_events.py:60-70`)
- [ ] Run tests, confirm they pass: `pytest tests/unit/core/test_combat_types.py -x`
- [ ] Verify: DamageContext is identical to the original (frozen=True, slots=True, same 3 fields, same defaults)

**Notes:**

---

### Task 1.2: Update `combat_events.py` to re-export DamageContext from core [Simple]
**File:** `game/simulation/combat/combat_events.py`
**Tests:** `pytest tests/unit/simulation/combat/test_combat_events.py -x`

- [ ] In `game/simulation/combat/combat_events.py`, remove the `DamageContext` class definition (lines 60-70)
- [ ] Add import at top: `from game.core.combat_types import DamageContext`
- [ ] Verify `DamageContext` is still accessible via `from game.simulation.combat.combat_events import DamageContext` (existing test imports)
- [ ] Run existing tests: `pytest tests/unit/simulation/combat/test_combat_events.py -x`
- [ ] Verify: all `TestDamageContext` tests pass without modification

**Notes:**

---

### Task 1.3: Update `collision.py` to import DamageContext from core [Simple]
**File:** `game/engine/collision.py:53`
**Tests:** `pytest tests/unit/systems/test_collision.py -x` (or equivalent collision tests)

- [ ] In `game/engine/collision.py`, change line 53 from:
  `from game.simulation.combat.combat_events import DamageContext`
  to:
  `from game.core.combat_types import DamageContext`
- [ ] Run collision tests to verify behavior unchanged
- [ ] Verify: `game/engine/collision.py` has NO imports from `game.simulation` (grep the file)

**Notes:**

---

### Task 1.4: Update `projectile_manager.py` to import DamageContext from core [Simple]
**File:** `game/simulation/projectile_manager.py:146`
**Tests:** `pytest tests/ -k projectile_manager --testmon`

- [ ] In `game/simulation/projectile_manager.py`, change line 146 from:
  `from game.simulation.combat.combat_events import DamageContext`
  to:
  `from game.core.combat_types import DamageContext`
- [ ] Run relevant tests to verify behavior unchanged
- [ ] Verify: import works and projectile damage context creation is unchanged

**Notes:**

---

### Task 1.5: Update `damage_calculator.py` TYPE_CHECKING import [Simple]
**File:** `game/simulation/combat/damage_calculator.py:25-28`
**Tests:** `pytest tests/unit/simulation/combat/ --testmon`

- [ ] In `game/simulation/combat/damage_calculator.py`, change the TYPE_CHECKING block (lines 25-28) from:
  ```python
  from game.simulation.combat.combat_events import (
      CombatEventBus,
      DamageContext,
  )
  ```
  to:
  ```python
  from game.simulation.combat.combat_events import CombatEventBus
  from game.core.combat_types import DamageContext
  ```
- [ ] Run combat tests: `pytest tests/unit/simulation/combat/ --testmon`
- [ ] Verify: type hints still resolve correctly

**Notes:**

---

### Task 1.6: Grep verification - no Engine->Simulation imports remain [Simple]
**Tests:** Manual grep verification

- [ ] Run: `grep -rn "from game\.simulation" game/engine/` -- must return zero results
- [ ] Run: `grep -rn "import game\.simulation" game/engine/` -- must return zero results
- [ ] Run: `grep -rn "DamageContext" game/` and verify all production imports use `game.core.combat_types` (except the re-export in `combat_events.py`)
- [ ] Run incremental tests: `pytest tests/ --testmon`

**Notes:**

---

### Task 1.7: PhysicsBody - Write tests for boundary clarification [Medium]
**File:** `tests/unit/systems/test_physics.py` (modify existing) or `tests/unit/engine/test_physics_body.py` (new)
**Tests:** `pytest tests/unit/systems/test_physics.py -x`

**TDD Steps:**
- [ ] Write test asserting PhysicsBody provides position, velocity, angle, mass, forward_vector() (property container role)
- [ ] Write test asserting PhysicsBody.update() is a no-op (or raises NotImplementedError) -- documents that subclasses must override
- [ ] Write test asserting PhysicsBody does NOT have apply_force() method (or it raises NotImplementedError)
- [ ] Run tests, confirm they fail against current code: `pytest tests/unit/systems/test_physics.py -x`

**Notes:** Existing tests in `test_physics.py` and `test_physics_edge_cases.py` test the current apply_force/update behavior. These tests will need updating after the changes.

---

### Task 1.8: PhysicsBody - Remove dead code, update docstrings [Medium]
**File:** `game/engine/physics.py`
**Tests:** `pytest tests/unit/systems/test_physics.py tests/unit/systems/test_physics_edge_cases.py tests/unit/simulation/entities/test_ship_physics.py --testmon`

- [ ] Remove or gut `apply_force()` method in `PhysicsBody` (line 103-106): either remove entirely or replace with `raise NotImplementedError("Subclasses use their own physics model")`
- [ ] Replace `update()` method body (lines 82-101) with `pass` or `raise NotImplementedError("Subclasses must implement their own update")`
- [ ] Update the module-level docstring (lines 1-50) to document:
  - PhysicsBody is a property container for physical entities
  - Ship uses ShipPhysicsMixin for arcade physics (velocity = heading * speed)
  - Projectile uses direct velocity integration (position += velocity)
  - Neither Ship nor Projectile uses the force-accumulation model
- [ ] Update the class docstring to describe the property container role
- [ ] Update existing tests in `test_physics.py` and `test_physics_edge_cases.py` that test apply_force/update to match new behavior
- [ ] Run all physics-related tests: `pytest tests/unit/systems/test_physics.py tests/unit/systems/test_physics_edge_cases.py tests/unit/simulation/entities/test_ship_physics.py -x`
- [ ] Run broader regression: `pytest tests/ --testmon`

**Notes:** Check `test_physics.py` and `test_physics_edge_cases.py` for tests that exercise apply_force() or update() -- these will need updating.

---

### Task 1.9: Phase 1 regression test [Simple]
**Tests:** `pytest tests/ --testmon`

- [ ] Run incremental test suite: `pytest tests/ --testmon`
- [ ] Fix any regressions
- [ ] Verify test count is >= 14783

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `grep -rn "from game\.simulation" game/engine/` returns zero results
- [ ] DamageContext importable from both `game.core.combat_types` and `game.simulation.combat.combat_events`
- [ ] PhysicsBody docstring documents arcade physics model
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
