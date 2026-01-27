# Phase 1: Critical Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-29 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address critical severity findings that pose immediate risk
**Priority:** Immediate

---

## Tasks

### Task 1.1: SIM-01 - Bidirectional Ship coupling [Complex]
**File:** `game/simulation/components/component.py`, `game/simulation/components/abilities/resources.py`
**Tests:** `pytest tests/unit/simulation/test_component_decoupling.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
The `component.ship` back-reference was used primarily for:
1. **Formula evaluation**: Accessing `ship.max_mass_budget` in `get_resource_cost()` and `recalculate_stats()`
2. **Resource access**: Accessing `ship.resources` in ResourceConsumption ability

**Solution implemented:**
- Added optional `context` parameter to `Component.get_resource_cost()` and `Component.recalculate_stats()`
- Context supports `{'ship_class_mass': float}` for formula evaluation
- Methods fall back to `component.ship` reference if no context provided (backward compatibility)
- Added optional `resources` parameter to `ResourceConsumption.update()`, `check_and_consume()`, `check_available()`
- Methods fall back to `component.ship.resources` if no resources provided (backward compatibility)

**Impact:**
- Components can now operate without ship reference when context/resources are provided
- All 9 new decoupling tests pass
- Full test suite (819 tests) passes with no regressions


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
