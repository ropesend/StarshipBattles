# Phase 1 Checklist: Declare Fleet Bonus Attributes on Ship
**Status:** Not Started

## Task 1.1: Write failing tests for attribute existence [Simple]
**File:** `tests/unit/simulation/entities/test_ship_fleet_attrs.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/test_ship_fleet_attrs.py -v`
- [ ] Create test file `tests/unit/simulation/entities/test_ship_fleet_attrs.py`
- [ ] Write test: freshly constructed Ship has `fleet_attack_bonus == 0.0` (use minimal Ship constructor with mock registries)
- [ ] Write test: freshly constructed Ship has `fleet_defense_bonus == 0.0`
- [ ] Write test: `fleet_attack_bonus` can be set to a float and read back
- [ ] Write test: `fleet_defense_bonus` can be set to a float and read back
- [ ] Run tests -- confirm they fail with `AttributeError` (attributes not declared yet)
**Notes:**

## Task 1.2: Declare attributes in Ship.__init__ [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_fleet_attrs.py -v`
- [ ] Add the following two lines after line 165 (`self.baseline_to_hit_offense: float = 0.0`):
  ```python
  self.fleet_attack_bonus: float = 0.0   # Set by FleetAuraManager._recalculate()
  self.fleet_defense_bonus: float = 0.0  # Set by FleetAuraManager._recalculate()
  ```
- [ ] Run new tests -- confirm they pass
- [ ] Run existing ship tests: `pytest tests/unit/simulation/entities/ -v`
**Notes:**

## Task 1.3: Verify no regressions [Simple]
**Tests:** `pytest tests/unit/simulation/ -v`
- [ ] Run: `pytest tests/unit/simulation/ -v` -- all pass
- [ ] Confirm `FleetAuraManager._recalculate()` still sets the attributes correctly (no behavior change -- it overwrites declared defaults)
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
