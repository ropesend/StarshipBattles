# Phase 1 Checklist: Declare Fleet Bonus Attributes on Ship
**Status:** Complete

## Task 1.1: Write failing tests for attribute existence [Simple]
**File:** `tests/unit/simulation/entities/test_ship_fleet_attrs.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/test_ship_fleet_attrs.py -v`
- [x] Create test file `tests/unit/simulation/entities/test_ship_fleet_attrs.py`
- [x] Write test: freshly constructed Ship has `fleet_attack_bonus == 0.0` (use minimal Ship constructor with mock registries)
- [x] Write test: freshly constructed Ship has `fleet_defense_bonus == 0.0`
- [x] Write test: `fleet_attack_bonus` can be set to a float and read back
- [x] Write test: `fleet_defense_bonus` can be set to a float and read back
- [x] Run tests -- confirm they fail with `AttributeError` (attributes not declared yet)
**Notes:** Tests confirmed to fail with AttributeError before implementation. 2 of 4 failed (set-and-read pass because Python allows arbitrary attribute assignment).

## Task 1.2: Declare attributes in Ship.__init__ [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_fleet_attrs.py -v`
- [x] Add the following two lines after line 165 (`self.baseline_to_hit_offense: float = 0.0`):
  ```python
  self.fleet_attack_bonus: float = 0.0   # Set by FleetAuraManager._recalculate()
  self.fleet_defense_bonus: float = 0.0  # Set by FleetAuraManager._recalculate()
  ```
- [x] Run new tests -- confirm they pass
- [x] Run existing ship tests: `pytest tests/unit/simulation/entities/ -v`
**Notes:** All 458 entity tests pass. All 4 new tests pass.

## Task 1.3: Verify no regressions [Simple]
**Tests:** `pytest tests/unit/simulation/ -v`
- [x] Run: `pytest tests/unit/simulation/ -v` -- all pass
- [x] Confirm `FleetAuraManager._recalculate()` still sets the attributes correctly (no behavior change -- it overwrites declared defaults)
**Notes:** 2775 tests pass (2771 existing + 4 new). FleetAuraManager._recalculate() sets ship.fleet_attack_bonus and ship.fleet_defense_bonus directly -- declaring them in __init__ just provides a safe default before the aura manager runs.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
