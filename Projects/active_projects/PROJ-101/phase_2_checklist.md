# Phase 2: New Columns

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-101 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add 7 new data columns (Speed, Tonnage, Warp, Spaceyard, Transport, Resources, Cargo) — all hidden by default, togglable from sidebar.

---

## Tasks

### Task 2.1: Add Per-Ship Spaceyard Check [Simple]
**File:** `game/strategy/data/fleet_capability_calculator.py`
**Tests:** `pytest tests/unit/strategy/ -k capability`

- [ ] Add static method `ship_has_spaceyard(ship: ShipInstance) -> bool`:
  - Check `ship.design_data['layers']` for components with SpaceShipyard ability
  - Pattern: iterate layer values → component dicts → check abilities dict for 'SpaceShipyard'
  - Reference: existing `has_space_shipyard` property logic (same file)
- [ ] Refactor existing `has_space_shipyard` property to call `FleetCapabilityCalculator.ship_has_spaceyard(ship)` for each combat-capable ship
- [ ] Write unit test for `ship_has_spaceyard()` with ship that has/doesn't have spaceyard

**Notes:**

### Task 2.2: Add Column Definitions [Simple]
**File:** `game/ui/screens/column_manager.py`
**Tests:** `pytest tests/unit/ui/ -k column_manager`

- [ ] Add 7 new columns to `DEFAULT_FLEET_COLUMNS` (after line 23, all with `visible: False`):
  ```python
  {'id': 'speed', 'width': 70, 'title': 'Spd', 'visible': False},
  {'id': 'tonnage', 'width': 80, 'title': 'Tons', 'visible': False},
  {'id': 'warp', 'width': 55, 'title': 'Warp', 'visible': False},
  {'id': 'spaceyard', 'width': 60, 'title': 'Yard', 'visible': False},
  {'id': 'transport', 'width': 65, 'title': 'Pax', 'visible': False},
  {'id': 'resources', 'width': 130, 'title': 'Resources', 'visible': False},
  {'id': 'cargo', 'width': 65, 'title': 'Cargo', 'visible': False},
  ```
- [ ] Write test: new columns exist in defaults
- [ ] Write test: new columns are all hidden by default

**Notes:**

### Task 2.3: Add Column Value Extraction [Medium]
**File:** `game/ui/screens/column_manager.py`
**Tests:** `pytest tests/unit/ui/ -k column_manager`

- [ ] Add import: `from game.core.constants import ResourceType` (top of file)
- [ ] Add `elif` branches in `get_column_value()` for each new column:
  - `speed`: Late import `FleetSpeedCalculator`, call `calculate_ship_speed(ship)`, return `str(speed)`
  - `tonnage`: `ship.get_calculated_stats().get('mass', 0)`, return `f"{mass:,.0f}"`
  - `warp`: Late import `ShipStatsCalculator`, call `has_warp_capability(ship)`, return `"Yes"/"No"`
  - `spaceyard`: Late import `FleetCapabilityCalculator`, call `ship_has_spaceyard(ship)`, return `"Yes"/"No"`
  - `transport`: `ship.get_calculated_stats().get('cargo_storage', {}).get('passengers', 0) > 0`, return `"Yes"/"No"`
  - `resources`: Build compact string like `"E:80 F:90 A:100"` using `ship.get_resource_percentage(ResourceType.ENERGY)` etc. Only include resources with non-zero capacity.
  - `cargo`: `sum(ship.cargo_contents.values()) if ship.cargo_contents else 0`, return `str(total)` or `"--"`
- [ ] Write unit tests for each column value extraction (mock ship objects)

**Notes:** Use late imports inside get_column_value() to avoid import cycles. The codebase uses this pattern extensively (see fleet.py:132, ship_instance.py:232).

### Task 2.4: Add Sort Key Handlers [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/strategy/ -k fleet_report_filters`

- [ ] Add `elif` branches in `sort_ships()` → `get_sort_key()` for:
  - `speed`: Late import FleetSpeedCalculator → `calculate_ship_speed(ship)`
  - `tonnage`: `ship.get_calculated_stats().get('mass', 0)`
  - `warp`: `1 if ShipStatsCalculator.has_warp_capability(ship) else 0`
  - `spaceyard`: `1 if FleetCapabilityCalculator.ship_has_spaceyard(ship) else 0`
  - `transport`: `1 if ship.get_calculated_stats().get('cargo_storage', {}).get('passengers', 0) > 0 else 0`
  - `cargo`: `sum(ship.cargo_contents.values()) if ship.cargo_contents else 0`
  - `resources`: `0` (no meaningful sort for combined column)
- [ ] Write unit tests for sorting by new columns

**Notes:**

### Task 2.5: Run Tests [Simple]
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
