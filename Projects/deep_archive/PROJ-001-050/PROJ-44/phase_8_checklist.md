# Phase 8: Long Method Refactoring

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Break down remaining long methods.

---

## Tasks

### Task 8.1: Split ShipStatsCalculator.calculate() [Medium]
**File:** `game/simulation/systems/stats.py`
**Issue:** CQ-011 - 200+ line method with 6 phases
**Tests:** `pytest tests/unit/simulation/`

- [x] Extract `_check_damage_and_gather_resources(ship)` - Phase 1
- [x] Extract `_allocate_crew_and_life_support(ship)` - Phase 2
- [x] Extract `_aggregate_component_stats(ship)` - Phase 3
- [x] Extract `_apply_physics_limits(ship)` - Phase 4
- [x] Extract `_calculate_combat_stats(ship)` - Phase 5
- [x] Main `calculate()` orchestrates phases
- [x] Verify: Ship stats calculation unchanged

**Notes:**
- Refactored calculate() from ~320 lines to ~25 line orchestrator
- Added _reset_base_stats() helper for initialization
- Added _finalize_resources() helper for endurance calculation
- All 15 new tests pass + 6 existing ship stats tests pass

---

### Task 8.2: Refactor LayerRestrictionDefinitionRule.validate() [Simple]
**File:** `game/simulation/ship_validator.py` (note: not systems/validator.py)
**Issue:** CQ-03 - High cyclomatic complexity
**Tests:** `pytest tests/unit/simulation/`

- [x] Extract `_check_block_rules(component, restrictions) -> bool`
- [x] Extract `_check_allow_rules(component, restrictions) -> bool`
- [x] Simplify main `validate()` to orchestrate
- [x] Verify: Validation still works

**Notes:**
- File was at game/simulation/ship_validator.py (corrected from checklist)
- Extracted two helper methods for block and allow rule processing
- Main _do_validate() now orchestrates the two phases
- All 14 new tests pass

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ --testmon` - all tests pass (5687 passed, 3 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
