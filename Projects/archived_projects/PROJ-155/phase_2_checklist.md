# Phase 2: Merge Unique Tests Then Delete

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-155 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (PROJ-154 + PROJ-157)
**Objective:** For each file with partial overlap, migrate unique tests to the primary file, then delete the source.
**Priority:** High

---

## PROJ-154 / PROJ-157 Overlap Summary

PROJ-157 completed Tasks 2.1, 2.2, 2.3, 2.8, and 2.14 (via directory deletion).
PROJ-154 completed Tasks 2.6 (engines contracts merge) and 2.7 (fleet battle adapter merge).

PROJ-157 also discovered that several merge TARGETS planned by PROJ-155 don't exist — the source files ARE the canonical versions. Tasks 2.4, 2.5, 2.9, 2.10, 2.11 are now DROPPED.

Tasks 2.12 and 2.13 were conditional — source files didn't exist (already cleaned up before either project).

**All Phase 2 work is complete.**

---

## Tasks

### Task 2.1: Merge layer restriction rule refactor [Simple] — DONE by PROJ-157
**Source:** `tests/unit/simulation/test_layer_restriction_rule_refactor.py`
**Target:** `tests/unit/simulation/validation/test_ship_validator_rules.py`

- [x] Migrated `test_combined_block_and_allow_rules` to target — PROJ-157
- [x] Deleted source file — PROJ-157

### Task 2.2: Merge json utils edge cases [Medium] — DONE by PROJ-157
**Source:** `tests/unit/core/test_json_utils_edge_cases.py`
**Target:** `tests/unit/core/test_json_utils.py`

- [x] Migrated 3 unique tests to target — PROJ-157
- [x] Deleted source file — PROJ-157

### Task 2.3: Merge validation edge cases [Medium] — DONE by PROJ-157
**Source:** `tests/unit/core/test_validation_edge_cases.py`
**Target:** `tests/unit/core/test_validation.py`

- [x] Migrated 5 unique tests to target — PROJ-157
- [x] Deleted source file — PROJ-157

### Task 2.4: Merge logger events [Simple] — DROPPED
**Source:** `tests/unit/core/logger/test_events.py`
**Original Target:** `tests/unit/core/logger/test_logger.py`

- [x] DROPPED: Target file `test_logger.py` does not exist. Source IS the canonical file. — PROJ-157 verified

**Notes:** `test_logger.py` never existed. `test_events.py` is canonical and should be kept.

### Task 2.5: Merge logger singleton [Medium] — DROPPED
**Source:** `tests/unit/core/logger/test_singleton.py`
**Original Target:** `tests/unit/core/logger/test_logger.py`

- [x] DROPPED: Target file `test_logger.py` does not exist. Source IS the canonical file. — PROJ-157 verified

**Notes:** Same as Task 2.4. `test_singleton.py` is canonical and should be kept.

### Task 2.6: Merge engines contracts [Medium] — DONE by PROJ-154
**Source:** `tests/unit/strategy/interfaces/test_engines_contracts.py` (~379 lines)
**Target:** `tests/unit/strategy/interfaces/test_engine_interfaces.py`

- [x] Migrated 16 unique tests (IPopulationEngine, IResupplyEngine, IHarvestingEngine, process_construction_tick, module exports) — PROJ-154
- [x] Deleted source file — PROJ-154
- [x] Target now has 55 tests — PROJ-154

### Task 2.7: Merge fleet battle adapter data/ [Simple] — DONE by PROJ-154
**Source:** `tests/unit/strategy/data/test_fleet_battle_adapter.py` (303 lines)
**Target:** `tests/unit/strategy/test_fleet_battle_adapter.py`

- [x] Migrated `test_to_battle_ships_passes_registries` to target — PROJ-154
- [x] Deleted source file — PROJ-154
- [x] Target now has 13 tests — PROJ-154

### Task 2.8: Merge AI behaviors [Medium] — DONE by PROJ-157
**Source:** `tests/unit/ai/formation_prediction/test_ai_behaviors.py`
**Target:** `tests/unit/ai/formation_prediction/test_behavior_units.py`

- [x] Migrated 3 truly unique tests — PROJ-157
- [x] Deleted source file — PROJ-157

### Task 2.9: Merge target evaluator rules [Complex] — DROPPED
**Source:** `tests/unit/ai/target_evaluator/test_evaluation_rules.py`
**Original Target:** `tests/unit/ai/target_evaluator/test_target_evaluator_rules.py`

- [x] DROPPED: Target file does not exist. Source IS the canonical file (54 tests). — PROJ-157 verified

**Notes:** `test_evaluation_rules.py` is canonical. Includes `TestSpeedRulesFactorBased` documenting a known bug. Keep it.

### Task 2.10: Merge evaluation integration [Medium] — DROPPED
**Source:** `tests/unit/ai/target_evaluator/test_evaluation_integration.py`
**Original Target:** `tests/unit/ai/target_evaluator/test_target_evaluator_edge_cases.py`

- [x] DROPPED: Target file does not exist. Source IS the canonical file. — PROJ-157 verified

### Task 2.11: Merge controllable adapter files [Medium] — DROPPED
**Source:** `tests/unit/ai/controllable_interface/test_adapter_basics.py` + `test_adapter_methods.py`
**Original Target:** `tests/unit/ai/controllable_interface/test_controllable_adapter_edge_cases.py`

- [x] DROPPED: Target file does not exist. Sources ARE the canonical files (39 tests combined). — PROJ-157 verified

### Task 2.12: Merge spatial extended [Simple] (CONDITIONAL) — N/A

- [x] Source file does not exist. Already cleaned up before PROJ-155/157.

### Task 2.13: Merge collision system [Medium] (CONDITIONAL) — N/A

- [x] Source file does not exist. Already cleaned up before PROJ-155/157.

### Task 2.14: Merge component health manager [Simple] — DONE by PROJ-157

- [x] PROJ-157 deleted entire `tests/unit/components/` directory after verifying all files were strict subsets of `tests/unit/simulation/components/`.

---

## Remaining Work Summary

No remaining work. All tasks complete or dropped.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12 -q` — verified by PROJ-154
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
