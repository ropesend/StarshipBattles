# Phase 2: Rename is_destroyed to is_alive

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-95 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace `is_destroyed` with `is_alive` across strategy layer. Invert all boolean logic. Update serialization.

---

## Tasks

### Task 2.1: Update ShipInstance field and methods [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ --testmon`

9 changes with logic inversion:

- [ ] Line 60: Change `is_destroyed: bool = False` to `is_alive: bool = True`
- [ ] Line 189: Change `instance.is_destroyed = not ship.is_alive` to `instance.is_alive = ship.is_alive`
- [ ] Line 203: Change `return not self.is_destroyed and not self.is_derelict` to `return self.is_alive and not self.is_derelict`
- [ ] Line 544: Change `self.is_destroyed = False` to `self.is_alive = True`
- [ ] Line 546: Change `self.is_destroyed = True` to `self.is_alive = False`
- [ ] Line 616: Change `'is_destroyed': self.is_destroyed` to `'is_alive': self.is_alive`
- [ ] Line 642: Change `is_destroyed=data.get('is_destroyed', False)` to `is_alive=data.get('is_alive', True)`
- [ ] Line 674: Change `is_destroyed=self.is_destroyed` to `is_alive=self.is_alive`
- [ ] Line 683: Change `"DESTROYED" if self.is_destroyed` to `"DESTROYED" if not self.is_alive`
- [ ] Run: `pytest tests/unit/strategy/ship_instance/ --testmon`

**Notes:** Line numbers may shift if PROJ-94 Phase 1 already modified this file (bridge helper extraction). Verify actual line numbers before editing.

---

### Task 2.2: Update ShipDisplayFormatter [Simple]
**File:** `game/strategy/data/ship_display_formatter.py`
**Tests:** `pytest tests/unit/strategy/test_ship_display_formatter.py --testmon`

- [ ] Line 50: Change `if self._ship.is_destroyed:` to `if not self._ship.is_alive:`
- [ ] Run: `pytest tests/unit/strategy/test_ship_display_formatter.py --testmon`

**Notes:**

---

### Task 2.3: Update fleet_report_filters.py [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_report_filters.py --testmon`

- [ ] Line 138: Change `if ship.is_destroyed:` to `if not ship.is_alive:`
- [ ] Line 193: Change `if ship.is_destroyed:` to `if not ship.is_alive:`
- [ ] Run: `pytest tests/unit/strategy/test_fleet_report_filters.py --testmon`

**Notes:**

---

### Task 2.4: Update column_manager.py [Simple]
**File:** `game/ui/screens/column_manager.py`
**Tests:** `pytest tests/unit/ui/test_column_manager.py --testmon`

- [ ] Line 148: Change `if ship.is_destroyed:` to `if not ship.is_alive:`
- [ ] Run: `pytest tests/unit/ui/test_column_manager.py --testmon`

**Notes:**

---

### Task 2.5: Update test files [Medium]
**Tests:** `pytest tests/ -n 12`

10 test files, 32 occurrences -- all need logic inversion:

- [ ] `tests/unit/strategy/test_fleet_report_filters.py` (9 occurrences) -- change all `is_destroyed` to `is_alive` with inverted values
- [ ] `tests/unit/strategy/fleet/test_warp_resources.py` (5 occurrences) -- change all with inverted values
- [ ] `tests/unit/ui/test_column_manager.py` (4 occurrences) -- change all with inverted values
- [ ] `tests/integration/gameplay_loop/test_fleet_operations.py` (3 occurrences) -- change all with inverted values
- [ ] `tests/unit/ui/test_fleet_list_view_model.py` (3 occurrences) -- change all with inverted values
- [ ] `tests/unit/strategy/test_ship_display_formatter.py` (2 occurrences) -- change all with inverted values
- [ ] `tests/unit/strategy/test_ship_detail_panel.py` (2 occurrences) -- change all with inverted values
- [ ] `tests/integration/strategy/turn_engine/conftest.py` (2 occurrences) -- change all with inverted values
- [ ] `tests/integration/strategy/turn_engine/test_resources.py` (1 occurrence) -- change with inverted value
- [ ] `tests/integration/resource_system/test_resource_pipeline.py` (1 occurrence) -- change with inverted value
- [ ] Run: `pytest tests/ -n 12`

**Notes:** Key inversion patterns:
- `is_destroyed = True` becomes `is_alive = False`
- `is_destroyed = False` becomes `is_alive = True`
- `assert ship.is_destroyed` becomes `assert not ship.is_alive`
- `assert not ship.is_destroyed` becomes `assert ship.is_alive`
- `not is_destroyed and not is_derelict` becomes `is_alive and not is_derelict`

---

### Task 2.6: Verification [Simple]
- [ ] Grep: No `is_destroyed` in `game/` -- expect 0 matches
- [ ] Grep: No `is_destroyed` in `tests/` -- expect 0 matches
- [ ] Full test suite: `pytest tests/ -n 12` -- all pass
- [ ] Record test count

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
