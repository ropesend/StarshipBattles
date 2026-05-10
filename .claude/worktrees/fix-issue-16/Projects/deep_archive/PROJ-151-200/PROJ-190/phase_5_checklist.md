# Phase 5: Update Test Mocks

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-190 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix tests broken by stricter typing. ~50-80 test failures expected, mostly from mock objects that don't include all protocol-required attributes.

---

## Tasks

### Task 5.1: Update targeting system test mocks [Medium]
**File:** `tests/unit/simulation/combat/test_targeting_system.py`
**Tests:** `pytest tests/unit/simulation/combat/test_targeting_system.py`

- [x] Find all `MagicMock(spec=[...])` that create enemies/targets with partial attributes
- [x] Delete obsolete tests that verified duck-typed fallback behavior:
  - `test_select_target_handles_missing_is_alive_attribute`
  - `test_select_target_handles_missing_team_id`
  - `test_calculate_firing_solution_target_no_velocity_attribute`
- [x] Verify: all targeting tests pass

**Notes:** Deleted 3 tests. Objects must now have required attributes (no fallback).

---

### Task 5.2: Update weapon firing system test mocks [Simple]
**File:** `tests/unit/simulation/combat/test_weapon_firing_system.py`
**Tests:** `pytest tests/unit/simulation/combat/test_weapon_firing_system.py`

- [x] Update mock weapons: `weapon_ab.facing_angle = 0` (moved from component to ability)
- [x] Fixed 3 seeker weapon tests that needed `facing_angle` on `weapon_ab`
- [x] Verify: all weapon firing tests pass (28 tests)

**Notes:** Phase 4 changed `facing_angle` from component to weapon ability attribute.

---

### Task 5.3: Update projectile test mocks [Simple]
**File:** `tests/unit/simulation/entities/test_projectile.py`
**Tests:** `pytest tests/unit/simulation/entities/test_projectile.py`

- [x] Deleted `test_projectile_handles_owner_without_team` (obsolete duck-typed test)
- [x] Verify: all projectile tests pass

**Notes:** Owner must now have team_id attribute.

---

### Task 5.4: Update formation test mocks [Simple]
**File:** `tests/unit/simulation/entities/test_ship_formation.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_formation.py`

- [x] No changes needed - formation tests already pass
- [x] Verify: all formation tests pass

**Notes:** Formation TypeGuards work correctly with existing mocks.

---

### Task 5.5: Update remaining test files [Medium]
**Files:** Multiple test files
**Tests:** `pytest tests/unit/simulation/ -n 12`

- [x] `tests/unit/simulation/entities/test_ship_physics.py` — deleted 2 obsolete tests:
  - `test_rotate_without_turn_throttle_attribute`
  - `test_missing_engine_throttle_defaults_to_one`
- [x] `tests/unit/simulation/test_projectile_manager.py` — deleted:
  - `test_weapon_ability_without_get_damage_method`
- [x] `tests/unit/simulation/managers/test_battle_state_manager.py` — deleted:
  - `test_validate_state_missing_mode`
- [x] `tests/unit/simulation/ship_combat_engine/test_cooldowns.py` — deleted 2 obsolete tests:
  - `test_shield_regen_works_without_resources_attribute`
  - `test_missing_repair_rate_attribute`
- [x] `tests/unit/simulation/projectile_guidance/conftest.py` — added `combat_engine` to mock_owner
- [x] `tests/unit/simulation/projectile_guidance/test_guidance_behavior.py` — deleted:
  - `test_lead_calculation_without_solve_lead`
- [x] Run full simulation test suite: `pytest tests/unit/simulation/ -n 12` — 2583 passed

**Notes:** Deleted 11 obsolete tests that verified duck-typed fallback behavior. Updated conftest to provide required attributes.

---

### Task 5.6: Update simulation test scenarios [Simple]
**Files:** `simulation_tests/scenarios/base.py` and others
**Tests:** `pytest simulation_tests/ -n 4`

- [x] Reviewed simulation_tests - 12 failures are PRE-EXISTING test data issues (resource tests)
- [x] Not related to Phase 5 changes - same failures before and after changes
- [x] 55 tests pass, 4 skipped - all Phase 5 relevant tests pass

**Notes:** simulation_tests/tests/test_resource_consumption.py failures are due to test data mismatches (max_hp, fuel_capacity), not duck typing changes. These are documented as pre-existing issues.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/simulation/ -n 12` — 2583 passed (zero failures)
- [x] `pytest simulation_tests/ -n 4` — 55 passed, 12 failed (pre-existing test data issues)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
