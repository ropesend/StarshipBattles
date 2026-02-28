# Phase 4: Zone-Aware Selection & Interaction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-139 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update UI selection and colonization to work with multi-hex zones.

---

## Tasks

### Task 4.1: Update `_handle_picking()` for zone selection [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py`

- [x] In `_handle_picking()` (line 719): after star collection (line 756), add zone object lookup
- [x] Use galaxy's `get_zones_at_global_hex(hex_clicked)` to find zone objects
- [x] Add zone objects to sector_contents (avoid duplicates with existing stars/planets)
- [x] Determine how scene exposes galaxy reference (check `self.scene.galaxy` or `self.scene.session.galaxy`)
- [x] Write tests:
  - `test_picking_finds_star_via_zone_hex`
  - `test_picking_finds_dyson_sphere_via_zone_hex`
  - `test_picking_priority_fleet_over_zone`
- [x] Verify: `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py` passes

**Notes:** Added zone lookup after star collection. Tests in TestZoneSelection class. 3 new tests.

### Task 4.2: Update `ColonizeValidator.validate()` for zone colonization [Medium]
**File:** `game/strategy/validation/colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py`

- [x] In `validate()` (line 81): after `get_planets_at_global_hex`, also check zone registry
- [x] Fleet in a Dyson Sphere's zone should find the Dyson Sphere as a colonization candidate
- [x] Write tests:
  - `test_validate_colonize_dyson_sphere_from_zone_hex`
  - `test_validate_colonize_dyson_sphere_from_center`
  - `test_validate_colonize_normal_planet_unchanged`
- [x] Verify: `pytest tests/unit/strategy/validation/test_colonize_validator.py` passes

**Notes:** Added zone lookup to all_planets_at_hex. Tests in TestColonizeValidatorZoneColonization class. 4 new tests.

### Task 4.3: Update `strategy_colonization.py` for zone targeting [Medium]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** `pytest tests/unit/ui/`

- [x] In `on_colonize_click()` (~line 73-82): include zone planets in candidate list
- [x] After checking `p.location == loc_local`, also check zone membership via galaxy registry
- [x] Write test: `test_colonize_click_finds_dyson_sphere_via_zone`
- [x] Also updated `handle_colonize_designation()` for zone targeting
- [x] Verify: `pytest tests/unit/ui/` passes

**Notes:** Added zone lookup with safe checks (callable and isinstance). Created test_strategy_colonization.py with 2 tests.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/` passes (11937 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
