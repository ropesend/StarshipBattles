# Phase 8: Long Method Refactoring

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Break down remaining long methods.

---

## Tasks

### Task 8.1: Split ShipStatsCalculator.calculate() [Medium]
**File:** `game/simulation/systems/stats.py`
**Issue:** CQ-011 - 200+ line method with 6 phases
**Tests:** `pytest tests/unit/simulation/`

- [ ] Extract `_check_damage_and_gather_resources(ship)` - Phase 1
- [ ] Extract `_allocate_crew_and_life_support(ship)` - Phase 2
- [ ] Extract `_aggregate_component_stats(ship)` - Phase 3
- [ ] Extract `_apply_physics_limits(ship)` - Phase 4
- [ ] Extract `_calculate_combat_stats(ship)` - Phase 5
- [ ] Main `calculate()` orchestrates phases
- [ ] Verify: Ship stats calculation unchanged

**Notes:**

---

### Task 8.2: Refactor LayerRestrictionDefinitionRule.validate() [Simple]
**File:** `game/simulation/systems/validator.py`
**Issue:** CQ-03 - High cyclomatic complexity
**Tests:** `pytest tests/unit/simulation/`

- [ ] Extract `_check_block_rules(component, restrictions) -> bool`
- [ ] Extract `_check_allow_rules(component, restrictions) -> bool`
- [ ] Simplify main `validate()` to orchestrate
- [ ] Verify: Validation still works

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
