# Phase 5: Dead Code & Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-210 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove dead code, consolidate duplicates, fix minor issues
**Priority:** Low — cleanup that improves maintainability
**Findings:** DC-001 through DC-015, CQ-12, CQ-15, DC-009

---

## Tasks

### Task 5.1: Remove Dead ShipInstance Methods [Simple]
**Findings:** DC-001
**Files:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/test_ship_instance*.py -v`

- [ ] Remove get_layer_damage_summary() (returns empty dict, has TODO)
- [ ] Verify get_component_damage_summary() callers — remove if test-only
- [ ] Run tests

### Task 5.2: Consolidate Duplicate ship_has_ability [Simple]
**Findings:** DC-009
**Files:** `fleet_capability_calculator.py`, `game/strategy/services/component_inspector.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [ ] Remove FleetCapabilityCalculator.ship_has_ability() static method
- [ ] Update callers to use component_inspector.ship_has_ability() directly
- [ ] Run tests

### Task 5.3: Remove Unused Logger Import [Simple]
**Findings:** DC-006
**Files:** `game/strategy/data/planet.py`

- [ ] Remove `import logging` and `logger = logging.getLogger(__name__)` if unused
- [ ] Run tests

### Task 5.4: Add Named Constants for Magic Numbers [Simple]
**Findings:** CQ-12
**Files:** `game/strategy/data/fleet_battle_adapter.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_battle_adapter.py -v`

- [ ] Replace magic numbers 20000, 80000, 50000, 2000 with named constants
- [ ] Run tests

### Task 5.5: Final Verification [Medium]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite
- [ ] Verify Fleet.py line count (target: < 300)
- [ ] Verify Planet.py line count (target: < 300)
- [ ] Verify FleetOrderProcessor.py line count (target: < 200)
- [ ] Count remaining pass-through methods (target: 0)
- [ ] Check for any new circular imports introduced
- [ ] Commit all changes

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] ~150 lines of dead code removed
- [ ] No duplicate utility functions
- [ ] All magic numbers replaced with named constants
- [ ] All tests passing (7,353 baseline)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Mark PROJ-210 complete in plan.md
