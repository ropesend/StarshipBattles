# Phase 3: New Filters

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-101 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add "Has Spaceyard / No Spaceyard" and "Has Cargo / No Cargo" filter pairs.

---

## Tasks

### Task 3.1: Add Filter State to ViewModel [Simple]
**File:** `game/ui/screens/fleet_report_view_model.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_list_view_model`

- [ ] Add filter state attributes in `__init__` (after line 41):
  ```python
  self.filter_show_has_spaceyard = True
  self.filter_show_no_spaceyard = True
  self.filter_show_has_cargo = True
  self.filter_show_no_cargo = True
  ```
- [ ] Add toggle handlers in `toggle_filter()` (after line 89):
  ```python
  elif filter_id == 'has_spaceyard':
      self.filter_show_has_spaceyard = not self.filter_show_has_spaceyard
      result = self.filter_show_has_spaceyard
  elif filter_id == 'no_spaceyard':
      self.filter_show_no_spaceyard = not self.filter_show_no_spaceyard
      result = self.filter_show_no_spaceyard
  elif filter_id == 'has_cargo':
      self.filter_show_has_cargo = not self.filter_show_has_cargo
      result = self.filter_show_has_cargo
  elif filter_id == 'no_cargo':
      self.filter_show_no_cargo = not self.filter_show_no_cargo
      result = self.filter_show_no_cargo
  ```
- [ ] Add entries to `get_filter_state()` (after line 127):
  ```python
  'show_has_spaceyard': self.filter_show_has_spaceyard,
  'show_no_spaceyard': self.filter_show_no_spaceyard,
  'show_has_cargo': self.filter_show_has_cargo,
  'show_no_cargo': self.filter_show_no_cargo,
  ```
- [ ] Add labels in `get_filter_label()`:
  ```python
  'has_spaceyard': 'Has Yard',
  'no_spaceyard': 'No Yard',
  'has_cargo': 'Has Cargo',
  'no_cargo': 'No Cargo',
  ```
- [ ] Write unit tests for new filter toggle states

**Notes:**

### Task 3.2: Add Filter Logic [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/strategy/ -k fleet_report_filters`

- [ ] Add spaceyard filter in `filter_ships()` (after warp filter block, ~line 130):
  ```python
  # Spaceyard capability filter
  show_has_yard = filter_state.get('show_has_spaceyard', True)
  show_no_yard = filter_state.get('show_no_spaceyard', True)
  if not show_has_yard or not show_no_yard:
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
      if has_yard and not show_has_yard:
          continue
      if not has_yard and not show_no_yard:
          continue
  ```
- [ ] Add cargo filter (after spaceyard filter):
  ```python
  # Cargo filter (includes population)
  show_has_cargo = filter_state.get('show_has_cargo', True)
  show_no_cargo = filter_state.get('show_no_cargo', True)
  if not show_has_cargo or not show_no_cargo:
      has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
      if has_cargo and not show_has_cargo:
          continue
      if not has_cargo and not show_no_cargo:
          continue
  ```
- [ ] Write unit tests for filter_ships with spaceyard and cargo filters

**Notes:**

### Task 3.3: Add Filter UI Buttons [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** Manual test — visual verification

- [ ] After WARP CAPABILITY section (~line 296), add SPACEYARD filter section:
  ```python
  # Spaceyard filter section
  UILabel(relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 25),
          text="SPACEYARD", manager=self.ui_manager, container=self.sidebar_panel)
  y += 28

  spaceyard_configs = [
      ('has_spaceyard', 'Has Yard'),
      ('no_spaceyard', 'No Yard'),
  ]
  # ... same button creation pattern as warp filters
  ```
- [ ] Add CARGO filter section:
  ```python
  # Cargo filter section
  UILabel(relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 25),
          text="CARGO", manager=self.ui_manager, container=self.sidebar_panel)
  y += 28

  cargo_configs = [
      ('has_cargo', 'Has Cargo'),
      ('no_cargo', 'No Cargo'),
  ]
  ```
- [ ] Verify: sidebar doesn't overflow vertically at 1600px height

**Notes:**

### Task 3.4: Run Tests [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite
- [ ] All tests pass (baseline + new tests)
- [ ] No regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
