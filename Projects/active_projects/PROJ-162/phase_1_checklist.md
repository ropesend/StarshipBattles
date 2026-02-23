# Phase 1: Create CargoTransferService

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-162 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract shared business logic into a new service class with full test coverage.

---

## Tasks

### Task 1.1: Create CargoTransferService [Medium]
**File:** `game/strategy/services/cargo_transfer_service.py`
**Tests:** `pytest tests/unit/strategy/services/test_cargo_transfer_service.py -v`

- [ ] Create `game/strategy/services/cargo_transfer_service.py` with class `CargoTransferService`
- [ ] Implement `resolve_colonies(facade, hex_coord, fleet)` — static method:
  - Call `facade.get_planets_at_hex(hex_coord)`
  - If empty and fleet has `location`, fallback to `facade.get_planets_at_hex(fleet.location)`
  - Filter to colonies where `owner_id is not None`
  - Return list of PlanetInfo
  - Reference: `cargo_quick_dialog.py` lines 119-129 and 147-154
- [ ] Implement `get_unload_items(facade, fleet_id, colonies)` — static method:
  - Call `facade.get_fleet(fleet_id)` to get FleetInfo
  - Extract passengers from `fleet_info.passengers_current`
  - Return list of dicts: `{label, cargo_type, species_id, max_amount}`
  - Reference: `cargo_quick_dialog.py` lines 113-140
- [ ] Implement `get_load_items(facade, colonies)` — static method:
  - For each colony, call `facade.get_planet(colony.planet_id)`
  - Extract population items from `planet_info.population_details` (race_id, count, happiness)
  - Fallback to `planet_info.total_population` if no population_details
  - Return list of dicts: `{label, cargo_type, species_id, max_amount, planet_id}`
  - Reference: `cargo_quick_dialog.py` lines 164-194, `transfer_dialog.py` lines 240-275
- [ ] Implement `get_inventory_items(obj_info)` — static method:
  - Duck-type check: `passengers_current` → fleet, `population_details` → colony, `total_population` → planet fallback
  - Return list of dicts: `{label, cargo_type, species_id, max_amount}`
  - Reference: `transfer_dialog.py` lines 240-275 (`_get_inventory_items`)
- [ ] Implement `build_transfer_command(fleet_id, planet_id, cargo_type, direction, amount, max_amount, species_id)` — static method:
  - If `amount >= max_amount`, set amount to 0 (engine convention for "all")
  - Return `IssueTransferCommand` instance
  - Reference: `cargo_quick_dialog.py` lines 331-342

**Notes:**

---

### Task 1.2: Add service to exports [Simple]
**File:** `game/strategy/services/__init__.py`
**Tests:** N/A (import verification in Task 1.3)

- [ ] Read current `__init__.py` contents
- [ ] Add import for `CargoTransferService`

**Notes:**

---

### Task 1.3: Create service unit tests [Medium]
**File:** `tests/unit/strategy/services/test_cargo_transfer_service.py`
**Tests:** `pytest tests/unit/strategy/services/test_cargo_transfer_service.py -v`

- [ ] Create directory `tests/unit/strategy/services/` if it doesn't exist
- [ ] Create `tests/unit/strategy/services/__init__.py`
- [ ] Create `tests/unit/strategy/services/test_cargo_transfer_service.py` with:
- [ ] `test_resolve_colonies_at_primary_hex` — facade returns colonies at primary hex
- [ ] `test_resolve_colonies_fallback_to_fleet_location` — primary hex empty, falls back to fleet.location
- [ ] `test_resolve_colonies_filters_uncolonized` — only returns planets with owner_id not None
- [ ] `test_get_unload_items_with_passengers` — fleet has passengers, returns item
- [ ] `test_get_unload_items_zero_passengers` — returns empty list
- [ ] `test_get_load_items_with_population_details` — colony has species, returns per-species items
- [ ] `test_get_load_items_total_population_fallback` — no population_details, uses total_population
- [ ] `test_get_load_items_no_colony_returns_empty` — empty colonies list
- [ ] `test_get_inventory_items_fleet` — duck-types as fleet (passengers_current)
- [ ] `test_get_inventory_items_colony` — duck-types as colony (population_details)
- [ ] `test_build_transfer_command_normal_amount` — amount < max passes through
- [ ] `test_build_transfer_command_max_becomes_zero` — amount >= max → 0
- [ ] Verify all tests pass: `pytest tests/unit/strategy/services/ -v`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/services/ -v` — all new tests pass
- [ ] `pytest tests/ --testmon` — no regressions
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
