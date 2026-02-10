# Phase 4: Component Resource & Health Managers [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-88 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract resource activation methods (~80 lines) into `component_resource_manager.py` and health management methods (~60 lines) into `component_health_manager.py`. Component retains facade methods for its 161 importers.

**File:** `game/simulation/components/component.py`
**New Files:** `game/simulation/components/component_resource_manager.py`, `game/simulation/components/component_health_manager.py`
**Tests:** `pytest tests/unit/entities/ tests/unit/components/ tests/unit/combat/ -n 12`

---

## Tasks

### Task 4.1: Create ComponentResourceManager [Medium]
**File:** `game/simulation/components/component_resource_manager.py`
- [x] Create `component_resource_manager.py` in `game/simulation/components/`
- [x] Define `ComponentResourceManager` class that takes a component reference in `__init__`
- [x] Move `can_afford_activation()` logic (component.py lines 314-323): iterates ability_instances, checks trigger=='activation' and check_available
- [x] Move `try_activate()` logic (component.py lines 331-336): calls can_afford then consume
- [x] Move `consume_activation()` logic (component.py lines 325-329): iterates ResourceConsumption abilities with trigger=='activation'
- [x] Move `get_resource_cost()` logic (component.py lines 366-391): builds context, evaluates formulas, applies cost_mult
- [x] Import `safe_evaluate_math_formula` from `game.simulation.formula_system`
- [x] Add type hints and docstrings

**Notes:** Created with __slots__ for memory efficiency. Hot path methods delegated via lazy property.

---

### Task 4.2: Create ComponentHealthManager [Simple]
**File:** `game/simulation/components/component_health_manager.py`
- [x] Create `component_health_manager.py` in `game/simulation/components/`
- [x] Define `ComponentHealthManager` class that takes a component reference in `__init__`
- [x] Move `take_damage()` logic (component.py lines 341-358): reduces HP, updates status, marks hp_ratio dirty
- [x] Move `reset_hp()` logic (component.py lines 360-364): restores HP, resets status, marks hp_ratio dirty
- [x] Move `hp_ratio` property logic (component.py lines 236-249): cached HP ratio calculation
- [x] Import `ComponentStatus` from `component_constants`
- [x] Add type hints and docstrings

**Notes:** Created with __slots__ for memory efficiency. Operates directly on component HP fields.

---

### Task 4.3: Write Tests for ComponentResourceManager [Medium]
**File:** `tests/unit/components/test_component_resource_manager.py`
- [x] Create test file `tests/unit/components/test_component_resource_manager.py`
- [x] Test `can_afford_activation()` returns True when resources available
- [x] Test `can_afford_activation()` returns False when resources depleted
- [x] Test `try_activate()` returns True and consumes resources on success
- [x] Test `try_activate()` returns False and preserves resources on failure
- [x] Test `consume_activation()` only consumes activation-triggered resources
- [x] Test `get_resource_cost()` returns correct costs with multiplier
- [x] Test `get_resource_cost()` evaluates formulas correctly
- [x] Run tests: `pytest tests/unit/components/test_component_resource_manager.py -v`

**Notes:** 13 tests written covering all methods and edge cases.

---

### Task 4.4: Write Tests for ComponentHealthManager [Simple]
**File:** `tests/unit/components/test_component_health_manager.py`
- [x] Create test file `tests/unit/components/test_component_health_manager.py`
- [x] Test `take_damage()` reduces current_hp correctly
- [x] Test `take_damage()` returns True when component destroyed (hp <= 0)
- [x] Test `take_damage()` sets status to DAMAGED below threshold
- [x] Test `take_damage()` raises TypeError for non-numeric input
- [x] Test `reset_hp()` restores full HP and ACTIVE status
- [x] Test `hp_ratio` returns correct cached ratio
- [x] Test `hp_ratio` recalculates after damage (dirty flag)
- [x] Run tests: `pytest tests/unit/components/test_component_health_manager.py -v`

**Notes:** 8 tests written covering all methods and edge cases.

---

### Task 4.5: Wire Component Facade Methods [Simple]
**File:** `game/simulation/components/component.py`
- [x] Add lazy `_resource_mgr` property to Component (creates ComponentResourceManager on first access)
- [x] Add lazy `_health_mgr` property to Component (creates ComponentHealthManager on first access)
- [x] Replace `can_afford_activation()` body with `return self._resource_mgr.can_afford_activation()`
- [x] Replace `try_activate()` body with `return self._resource_mgr.try_activate()`
- [x] Replace `consume_activation()` body with `self._resource_mgr.consume_activation()`
- [x] Replace `get_resource_cost()` body with `return self._resource_mgr.get_resource_cost(context)`
- [x] Replace `take_damage()` body with `return self._health_mgr.take_damage(amount)`
- [x] Replace `reset_hp()` body with `self._health_mgr.reset_hp()`
- [x] Replace `hp_ratio` property body with `return self._health_mgr.hp_ratio`
- [x] Remove extracted method bodies (keep facade one-liners)

**Notes:** Used lazy property pattern with resource_manager/health_manager properties. Clone works correctly (new instance gets fresh lazy properties).

---

### Task 4.6: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12 --tb=short`
- [x] Run full test suite: `pytest tests/ -n 12 --tb=short`
- [x] Confirm all tests pass with zero new failures
- [x] Verify Component importers (161 files) are unaffected -- no import changes needed
- [x] Spot-check hot path: run `pytest tests/unit/combat/test_combat.py -v` to verify combat still works
- [x] Record test count: 7533 passed, 0 failed

**Notes:** Component.py reduced from 756→713 lines (-43 lines). All 161 importers unaffected.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
