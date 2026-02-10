# Phase 4: Component Resource & Health Managers [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-88 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract resource activation methods (~80 lines) into `component_resource_manager.py` and health management methods (~60 lines) into `component_health_manager.py`. Component retains facade methods for its 161 importers.

**File:** `game/simulation/components/component.py`
**New Files:** `game/simulation/components/component_resource_manager.py`, `game/simulation/components/component_health_manager.py`
**Tests:** `pytest tests/unit/entities/ tests/unit/components/ tests/unit/combat/ -n 12`

---

## Tasks

### Task 4.1: Create ComponentResourceManager [Medium]
**File:** `game/simulation/components/component_resource_manager.py`
- [ ] Create `component_resource_manager.py` in `game/simulation/components/`
- [ ] Define `ComponentResourceManager` class that takes a component reference in `__init__`
- [ ] Move `can_afford_activation()` logic (component.py lines 314-323): iterates ability_instances, checks trigger=='activation' and check_available
- [ ] Move `try_activate()` logic (component.py lines 331-336): calls can_afford then consume
- [ ] Move `consume_activation()` logic (component.py lines 325-329): iterates ResourceConsumption abilities with trigger=='activation'
- [ ] Move `get_resource_cost()` logic (component.py lines 366-391): builds context, evaluates formulas, applies cost_mult
- [ ] Import `safe_evaluate_math_formula` from `game.simulation.formula_system`
- [ ] Add type hints and docstrings

**Notes:** `can_afford_activation` and `try_activate` are hot path methods called during weapon firing every tick. The facade delegation in Component must be a single direct method call -- no dynamic dispatch or property lookup overhead.

---

### Task 4.2: Create ComponentHealthManager [Simple]
**File:** `game/simulation/components/component_health_manager.py`
- [ ] Create `component_health_manager.py` in `game/simulation/components/`
- [ ] Define `ComponentHealthManager` class that takes a component reference in `__init__`
- [ ] Move `take_damage()` logic (component.py lines 341-358): reduces HP, updates status, marks hp_ratio dirty
- [ ] Move `reset_hp()` logic (component.py lines 360-364): restores HP, resets status, marks hp_ratio dirty
- [ ] Move `hp_ratio` property logic (component.py lines 236-249): cached HP ratio calculation
- [ ] Import `ComponentStatus` from `component_constants`
- [ ] Add type hints and docstrings

**Notes:** The health manager needs access to `component.current_hp`, `component.max_hp`, `component.is_active`, `component.status`, `component.damage_threshold`, `component._hp_ratio_dirty`, and `component._cached_hp_ratio`. These are accessed via the component reference.

---

### Task 4.3: Write Tests for ComponentResourceManager [Medium]
**File:** `tests/unit/components/test_component_resource_manager.py`
- [ ] Create test file `tests/unit/components/test_component_resource_manager.py`
- [ ] Test `can_afford_activation()` returns True when resources available
- [ ] Test `can_afford_activation()` returns False when resources depleted
- [ ] Test `try_activate()` returns True and consumes resources on success
- [ ] Test `try_activate()` returns False and preserves resources on failure
- [ ] Test `consume_activation()` only consumes activation-triggered resources
- [ ] Test `get_resource_cost()` returns correct costs with multiplier
- [ ] Test `get_resource_cost()` evaluates formulas correctly
- [ ] Run tests: `pytest tests/unit/components/test_component_resource_manager.py -v`

**Notes:**

---

### Task 4.4: Write Tests for ComponentHealthManager [Simple]
**File:** `tests/unit/components/test_component_health_manager.py`
- [ ] Create test file `tests/unit/components/test_component_health_manager.py`
- [ ] Test `take_damage()` reduces current_hp correctly
- [ ] Test `take_damage()` returns True when component destroyed (hp <= 0)
- [ ] Test `take_damage()` sets status to DAMAGED below threshold
- [ ] Test `take_damage()` raises TypeError for non-numeric input
- [ ] Test `reset_hp()` restores full HP and ACTIVE status
- [ ] Test `hp_ratio` returns correct cached ratio
- [ ] Test `hp_ratio` recalculates after damage (dirty flag)
- [ ] Run tests: `pytest tests/unit/components/test_component_health_manager.py -v`

**Notes:**

---

### Task 4.5: Wire Component Facade Methods [Simple]
**File:** `game/simulation/components/component.py`
- [ ] Add lazy `_resource_mgr` property to Component (creates ComponentResourceManager on first access)
- [ ] Add lazy `_health_mgr` property to Component (creates ComponentHealthManager on first access)
- [ ] Replace `can_afford_activation()` body with `return self._resource_mgr.can_afford_activation()`
- [ ] Replace `try_activate()` body with `return self._resource_mgr.try_activate()`
- [ ] Replace `consume_activation()` body with `self._resource_mgr.consume_activation()`
- [ ] Replace `get_resource_cost()` body with `return self._resource_mgr.get_resource_cost(context)`
- [ ] Replace `take_damage()` body with `return self._health_mgr.take_damage(amount)`
- [ ] Replace `reset_hp()` body with `self._health_mgr.reset_hp()`
- [ ] Replace `hp_ratio` property body with `return self._health_mgr.hp_ratio`
- [ ] Remove extracted method bodies (keep facade one-liners)

**Notes:** Verify that the lazy property initialization does not break Component's `clone()` method. The clone creates a new Component from `self.data` which will get its own fresh lazy properties.

---

### Task 4.6: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12 --tb=short`
- [ ] Run full test suite: `pytest tests/ -n 12 --tb=short`
- [ ] Confirm all tests pass with zero new failures
- [ ] Verify Component importers (161 files) are unaffected -- no import changes needed
- [ ] Spot-check hot path: run `pytest tests/unit/combat/test_combat.py -v` to verify combat still works
- [ ] Record test count: _____ passed, _____ failed

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
