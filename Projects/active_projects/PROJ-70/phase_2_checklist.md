# Phase 2: Enhance format_fleet_info()

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-70 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Rewrite `format_fleet_info()` with 4 new sections and 3 helper functions. All Phase 1 tests should pass after this.

---

## Tasks

### Task 2.1: Add `_format_ship_groups()` Helper [Medium]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_detail_fmt.py -k ship`

- [x] Add `_format_ship_groups(fleet) -> str` function after `format_fleet_info()`
- [x] If no ships: return `"<b>Ships: None</b><br>"`
- [x] Use `collections.Counter` to group ships by `design_id`
- [x] For each unique design, get mass via `ship.get_calculated_stats().get('mass', 0)` (only first ship per design)
- [x] Get display name via `ship.design_data.get('name', design_id)`
- [x] Sort groups by mass descending
- [x] Format: `"<b>Ships (N):</b><br>"` header + `" Devastator x 3<br>"` per group (or `" Scout<br>"` if count=1)

**Notes:**

### Task 2.2: Add `_format_cargo_summary()` Helper [Simple]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_detail_fmt.py -k cargo`

- [x] Add `_format_cargo_summary(fleet) -> str` function
- [x] Iterate all ships' `cargo_contents` dicts, aggregate by cargo type
- [x] If no cargo found (all amounts <=0): return `""`
- [x] Format: `"<b>Cargo:</b><br>"` header + `" Passengers: 80<br>"` per type
- [x] Capitalize cargo type names: `cargo_type.replace('_', ' ').title()`

**Notes:**

### Task 2.3: Add `_format_orders()` Helper [Medium]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_detail_fmt.py -k order`

- [x] Add `_format_orders(fleet) -> str` function
- [x] Handle all order types:
  - `MOVE`: `" {i+1}. MOVE {order.target}<br>"`
  - `COLONIZE`: `" {i+1}. COLONIZE {planet_name}<br>"` (use `getattr(order.target, 'name', 'Unknown')`)
  - `BUILD`: `" {i+1}. BUILDING ({queue_size} items)<br>"` (use `getattr(fleet, 'construction_queue', [])`)
  - `TRANSFER`: existing logic from current `format_fleet_info()` (direction, cargo_type, amount)
  - Default: `" {i+1}. {order.type.name}<br>"`
- [x] No orders: `" (No Orders)<br>"`

**Notes:** This merges BUILD handling from `strategy_ui.py` inline code with TRANSFER handling from existing `format_fleet_info()`

### Task 2.4: Rewrite `format_fleet_info()` [Medium]
**File:** `game/ui/screens/strategy_detail_fmt.py` (replace lines 203-240)
**Tests:** `pytest tests/unit/ui/screens/test_fleet_detail_fmt.py`

- [x] Replace body of `format_fleet_info(fleet)` with:
  1. Header: Fleet ID, Owner, Location
  2. Range: `fleet.speed` as int hex/turn + `fleet.fuel_endurance()` display (unlimited if -1)
  3. Ship list: call `_format_ship_groups(fleet)`
  4. Cargo: call `_format_cargo_summary(fleet)`
  5. Orders: call `_format_orders(fleet)`
- [x] Verify ALL tests pass: `pytest tests/unit/ui/screens/test_fleet_detail_fmt.py`
- [x] Verify existing 2 TRANSFER tests still pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All Phase 1 tests pass (14/14)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
