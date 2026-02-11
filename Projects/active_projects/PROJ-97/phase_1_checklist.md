# Phase 1: JSON Data & Ability Update

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-97 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create production_rates.json, update SpaceShipyardAbility, update components.json

---

## Tasks

### Task 1.1: Create `data/production_rates.json` [Simple]
**File:** `data/production_rates.json` (NEW)
**Tests:** Manual verification — load with `json.load()`

- [ ] Create `data/production_rates.json` with three keys: `planetary_yard`, `space_shipyard`, `fleet_space_yard`
- [ ] Each key maps to a dict of resource names → max units per turn
- [ ] Planetary yard: all resources at 2000
- [ ] Space shipyard and fleet space yard: all resources at 3000
- [ ] Resource types: Metals, Organics, Radioactives, Vapors, Exotics

**Notes:**

### Task 1.2: Add `production_rates` field to SpaceShipyardAbility [Simple]
**File:** `game/simulation/components/abilities/harvester.py` (lines 95-128)
**Tests:** `pytest tests/unit/simulation/components/abilities/ -k shipyard`

- [ ] Add `self.production_rates: Dict[str, float]` to `__init__`, parsed from `data.get("production_rates", {})`
- [ ] Add UI row for production rates in `get_ui_rows()` if non-empty
- [ ] Ensure backward compat: if `production_rates` missing from data, default to empty dict

**Notes:**

### Task 1.3: Update `data/components.json` shipyard entries [Simple]
**File:** `data/components.json`
**Tests:** `pytest tests/ -k "component" --testmon`

- [ ] Add `"production_rates": {"Metals": 3000, "Organics": 3000, "Radioactives": 3000, "Vapors": 3000, "Exotics": 3000}` to `space_shipyard`'s SpaceShipyard ability data
- [ ] Same for `fleet_space_yard`'s SpaceShipyard ability data
- [ ] DO NOT remove ResourceStorage yet (Phase 5)

**Notes:**

### Task 1.4: Write unit tests for production rate loading [Simple]
**File:** `tests/unit/strategy/data/test_production_rates.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_production_rates.py`

- [ ] Test loading `production_rates.json` via `load_json`
- [ ] Test that all three yard types are present
- [ ] Test each yard type has expected resource keys
- [ ] Test default values (2000 for planetary, 3000 for shipyards)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
