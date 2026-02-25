# Phase 5: Update Test Mocks

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-190 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix tests broken by stricter typing. ~50-80 test failures expected, mostly from mock objects that don't include all protocol-required attributes.

---

## Tasks

### Task 5.1: Update targeting system test mocks [Medium]
**File:** `tests/unit/simulation/combat/test_targeting_system.py`
**Tests:** `pytest tests/unit/simulation/combat/test_targeting_system.py`

- [ ] Find all `MagicMock(spec=[...])` that create enemies/targets with partial attributes
- [ ] Add missing protocol attributes: `is_alive`, `team_id`, `position`, `velocity`, `type`
- [ ] Ensure all mock targets satisfy `ICombatShip` or `IProjectile` protocol requirements
- [ ] Verify: all targeting tests pass

**Notes:**

---

### Task 5.2: Update weapon firing system test mocks [Simple]
**File:** `tests/unit/simulation/combat/test_weapon_firing_system.py`
**Tests:** `pytest tests/unit/simulation/combat/test_weapon_firing_system.py`

- [ ] Update mock ships to include all `ICombatShip` required attributes
- [ ] Update mock components to include all `IComponent` required attributes
- [ ] Verify: all weapon firing tests pass

**Notes:**

---

### Task 5.3: Update projectile test mocks [Simple]
**File:** `tests/unit/simulation/entities/test_projectile.py`
**Tests:** `pytest tests/unit/simulation/entities/test_projectile.py`

- [ ] Line ~65: `MagicMock(spec=[])` owner → add `team_id` attribute
- [ ] Verify: all projectile tests pass

**Notes:**

---

### Task 5.4: Update formation test mocks [Simple]
**File:** `tests/unit/simulation/entities/test_ship_formation.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_formation.py`

- [ ] Update mocks that intentionally lack `formation` attribute
- [ ] Since code now uses `isinstance(ship, IFormationHost)` instead of `hasattr`, mock objects that don't implement the protocol will naturally fail the check — verify this is the desired behavior
- [ ] Verify: all formation tests pass

**Notes:**

---

### Task 5.5: Update remaining test files [Medium]
**Files:** Multiple test files
**Tests:** `pytest tests/unit/simulation/ -n 12`

- [ ] `tests/unit/simulation/entities/test_combat_endurance.py` — update mocks with partial component specs
- [ ] `tests/unit/simulation/components/test_modifier_introspection.py` — update mock abilities with minimal specs
- [ ] `tests/unit/simulation/test_projectile_manager.py` — update `MagicMock(spec=[])` for weapon abilities
- [ ] `tests/unit/simulation/managers/test_battle_state_manager.py` — update state mocks
- [ ] Any other test files that fail — investigate and fix mock specs
- [ ] Run full simulation test suite: `pytest tests/unit/simulation/ -n 12` — ALL PASS

**Notes:**

---

### Task 5.6: Update simulation test scenarios [Simple]
**Files:** `simulation_tests/scenarios/base.py` and others
**Tests:** `pytest simulation_tests/ -n 4`

- [ ] Review `simulation_tests/scenarios/base.py` for `hasattr`/`getattr` patterns on simulation objects
- [ ] Update any defensive access that now has typed alternatives
- [ ] Run: `pytest simulation_tests/ -n 4` — all pass

**Notes:** Simulation test scenarios may legitimately use defensive access for optional stats — evaluate case-by-case.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/simulation/ -n 12` — ALL PASS (zero failures)
- [ ] `pytest simulation_tests/ -n 4` — ALL PASS
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
