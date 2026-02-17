# Phase 3: Delete Old Directory Trees

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-155 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove 4 old test directories confirmed as strict subsets of newer simulation/ tests.
**Priority:** High

---

## CRITICAL: Approach

**DO NOT wholesale-delete directories.** Delete file-by-file after verifying each pair.

For each file:
1. Identify the corresponding new file in `tests/unit/simulation/`
2. Verify test count: new file should have >= old file's test count
3. Delete the old file
4. Run tests to confirm no regressions

Validation review 4 warned that old files sometimes use real objects (integration-style) while new files use MagicMock (unit-style). If an old file has no clear new counterpart, KEEP it and note in decisions.md.

---

## Tasks

### Task 3.1: Delete tests/unit/services/ [Medium]
**Directory:** `tests/unit/services/` (7 files, ~1,307 lines)
**New location:** `tests/unit/simulation/services/`
**Tests:** `pytest tests/unit/simulation/services/ -q`

**Verified pairs (from validation review 4):**
- [ ] `test_battle_service.py` → `simulation/services/test_battle_service.py` (15→77 tests, confirmed subset)
- [ ] `test_vehicle_design_service.py` → verify new counterpart exists
- [ ] `test_vehicle_design_service_di.py` → verify new counterpart exists
- [ ] `test_modifier_service.py` → verify new counterpart exists
- [ ] `test_modifier_service_di.py` → verify new counterpart exists
- [ ] `test_ship_stats_calculator_di.py` → verify new counterpart exists
- [ ] `__init__.py` → delete
- [ ] After all files deleted, remove `tests/unit/services/` directory
- [ ] Run `pytest tests/ -n 12 -q` to verify no regressions

**Notes:** All 6 pairs confirmed as subsets by validation review 4 spot-check.

### Task 3.2: Delete tests/unit/components/ [Simple]
**Prerequisite:** Phase 2 Task 2.14 must be complete (merge unique health manager tests)
**Directory:** `tests/unit/components/` (4 files, ~583 lines)
**New location:** `tests/unit/simulation/components/`
**Tests:** `pytest tests/unit/simulation/components/ -q`

- [ ] Verify Task 2.14 is complete (unique health manager tests migrated)
- [ ] `test_component_health_manager.py` → should already be deleted in Task 2.14
- [ ] `test_component_health_edge_cases.py` → `simulation/components/test_component_health_edge_cases.py` (verified subset)
- [ ] `test_resource_costs.py` → verify new counterpart exists
- [ ] `test_component_resource_manager.py` → verify new counterpart exists
- [ ] After all files deleted, remove `tests/unit/components/` directory
- [ ] Run `pytest tests/ -n 12 -q` to verify no regressions

**Notes:**

### Task 3.3: Delete subset files from tests/unit/combat/ [Complex]
**Directory:** `tests/unit/combat/` (20 files, ~3,136 lines)
**New locations:** Various under `tests/unit/simulation/`
**Tests:** `pytest tests/unit/simulation/ -n 12 -q`

**Already deleted in Phase 1:**
- test_combat_endurance_edge_cases.py (Task 1.6)
- test_targeting_edge_cases.py (Task 1.6)
- test_lead.py (Task 1.6)
- test_ccd.py (Task 1.6)

**Remaining files — verify each pair before deletion:**
- [ ] List all remaining .py files in `tests/unit/combat/`
- [ ] For each file, search for corresponding file in `tests/unit/simulation/`
- [ ] Compare test method counts (new must be >= old)
- [ ] Delete files confirmed as subsets one-by-one
- [ ] For files with NO clear new counterpart, keep and document in decisions.md
- [ ] Check if `tests/unit/combat/` directory is empty; if so, remove
- [ ] Run `pytest tests/ -n 12 -q` to verify no regressions

**Notes:** Validation review 4 confirmed: projectile_manager (2/3 tests mapped, verify test_projectile_movement), combat_endurance (5→45 tests), targeting_system (covered by simulation/combat/). The remaining ~15 files need individual verification.

### Task 3.4: Delete subset files from tests/unit/entities/ [Complex]
**Directory:** `tests/unit/entities/` (~45 files, ~7,740 lines)
**New location:** `tests/unit/simulation/entities/`
**Tests:** `pytest tests/unit/simulation/entities/ -q`

**Already deleted in Phase 1:**
- test_ship_formation_edge_cases.py (Task 1.2)
- test_projectile_edge_cases.py (Task 1.2)
- test_ability_aggregator_scope.py (Task 1.2)

**Verified pairs (from validation review 4):**
- [ ] `test_layer_data.py` → `simulation/entities/test_layer_data.py` (24→64 tests, confirmed subset)
- [ ] `test_ship_formation.py` → `simulation/entities/test_ship_formation.py` (14→76 tests, confirmed subset)
- [ ] `test_combat_endurance.py` → `simulation/entities/` tests (5→45 tests, confirmed subset)

**Remaining files — verify each pair:**
- [ ] List all remaining .py files in `tests/unit/entities/` (including subdirectories)
- [ ] For each file, search for corresponding file in `tests/unit/simulation/entities/`
- [ ] Compare test method counts
- [ ] Delete files confirmed as subsets one-by-one
- [ ] For files with NO clear new counterpart, keep and document
- [ ] After all confirmed subsets deleted, assess if directory can be removed
- [ ] Run `pytest tests/ -n 12 -q` to verify no regressions

**Notes:** This is the largest directory (~45 files). Some entity test files may NOT have simulation/ counterparts (e.g., ship_helpers/). Be conservative — only delete confirmed subsets.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12 -q` — verify no new failures vs baseline
- [ ] Record total lines removed in this phase in decisions.md
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
