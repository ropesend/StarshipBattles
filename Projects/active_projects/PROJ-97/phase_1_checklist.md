# Phase 1: JSON Data & Ability Update

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-97 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create production_rates.json, update SpaceShipyardAbility, update components.json

---

## Tasks

### Task 1.1: Create `data/production_rates.json` [Simple]
**File:** `data/production_rates.json` (NEW)
**Tests:** Manual verification — load with `json.load()`

- [x] Create `data/production_rates.json` with three keys: `planetary_yard`, `space_shipyard`, `fleet_space_yard`
- [x] Each key maps to a dict of resource names → max units per turn
- [x] Planetary yard: all resources at 2000
- [x] Space shipyard and fleet space yard: all resources at 3000
- [x] Resource types: Metals, Organics, Radioactives, Vapors, Exotics

**Notes:** Created with all 5 resources per yard type.

### Task 1.2: Add `production_rates` field to SpaceShipyardAbility [Simple]
**File:** `game/simulation/components/abilities/harvester.py` (lines 95-128)
**Tests:** `pytest tests/unit/simulation/components/abilities/ -k shipyard`

- [x] Add `self.production_rates: Dict[str, float]` to `__init__`, parsed from `data.get("production_rates", {})`
- [x] Add UI row for production rates in `get_ui_rows()` if non-empty
- [x] Ensure backward compat: if `production_rates` missing from data, default to empty dict

**Notes:** Added production_rates field and UI row that shows unified rate or range.

### Task 1.3: Update `data/components.json` shipyard entries [Simple]
**File:** `data/components.json`
**Tests:** `pytest tests/ -k "component" --testmon`

- [x] Add `"production_rates": {"Metals": 3000, "Organics": 3000, "Radioactives": 3000, "Vapors": 3000, "Exotics": 3000}` to `space_shipyard`'s SpaceShipyard ability data
- [x] Same for `fleet_space_yard`'s SpaceShipyard ability data
- [x] DO NOT remove ResourceStorage yet (Phase 5)

**Notes:** Added production_rates to both space_shipyard and fleet_space_yard. ResourceStorage preserved for Phase 5.

### Task 1.4: Write unit tests for production rate loading [Simple]
**File:** `tests/unit/strategy/data/test_production_rates.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_production_rates.py`

- [x] Test loading `production_rates.json` via `load_json`
- [x] Test that all three yard types are present
- [x] Test each yard type has expected resource keys
- [x] Test default values (2000 for planetary, 3000 for shipyards)

**Notes:** 9 new tests created, all passing.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
