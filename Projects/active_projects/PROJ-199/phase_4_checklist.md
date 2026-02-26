# Phase 4: ShipStatsCalculator Dual-Format Helpers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-199 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `get_component_type()` and `get_component_threshold()` helpers to `component_inspector.py` for the remaining 2 dual-format patterns.

---

## Tasks

### Task 4.1: Add helpers to component_inspector.py [Simple]
**File:** `game/strategy/services/component_inspector.py`
**Tests:** `pytest tests/unit/strategy/services/ --testmon`

- [ ] Add `get_component_type(comp_def: Any) -> str` function after `get_component_abilities()`
- [ ] Add `get_component_threshold(comp_def: Any, default: float) -> float` function after `get_component_type()`
- [ ] Add both names to `__all__` list

**Notes:**

### Task 4.2: Update ShipStatsCalculator [Simple]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/services/ --testmon`

- [ ] Update import to include `get_component_type, get_component_threshold`
- [ ] L327-331: Replace 4-line isinstance/getattr block with `comp_type = get_component_type(comp_def)`
- [ ] L354-358: Replace 4-line isinstance/getattr block with `threshold = get_component_threshold(comp_def, DEFAULT_DAMAGE_THRESHOLD)`

**Notes:** Line numbers may shift after Phase 3 changes — verify before editing

### Task 4.3: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All 12724 tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
