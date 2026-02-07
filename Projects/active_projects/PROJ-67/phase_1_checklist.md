# PROJ-67 Phase 1: Fleet Space Yard Component & Data Model

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-67 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the fleet space yard component, add construction_queue to Fleet, add has_space_shipyard property.

---

## Tasks

### Task 1.1: Add `fleet_space_yard` Component to components.json [Simple]
**File:** `data/components.json`
**Tests:** `pytest tests/unit/simulation/components/ -k space`

- [x] Add new component entry `fleet_space_yard` near existing `space_shipyard` (~line 1893)
- [x] Set `allowed_vehicle_types: ["Ship"]` (different from complex's `["Planetary Complex"]`)
- [x] Set `type: "SpaceShipyard"` (same type string)
- [x] Use `SpaceShipyard` ability with `construction_speed_bonus: 1.0, max_ship_mass: 100000`
- [x] Add appropriate mass, hp, crew, resource cost values
- [x] Add `major_classification: "Production"`
- [x] Verify component loads correctly: run `pytest tests/unit/simulation/components/`

**Notes:**

---

### Task 1.2: Add `construction_queue` to Fleet [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k fleet`

- [x] Add `self.construction_queue: list = []` in `Fleet.__init__()` (after line 62)
- [x] Add `construction_queue` to `Fleet.to_dict()` serialization (line ~571)
- [x] Add `construction_queue` restoration in `Fleet.from_dict()` (line ~597)
- [x] Write test: fleet initializes with empty construction_queue
- [x] Write test: fleet serialization round-trips construction_queue

**Notes:**

---

### Task 1.3: Add `has_space_shipyard` Property to Fleet [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k "fleet and shipyard"`

- [x] Add `has_space_shipyard` property to Fleet class
- [x] Implementation: check if any ship in fleet has a component with `SpaceShipyard` ability
- [x] Use `ShipInstance.get_calculated_stats()` or inspect `design_data` layers (follow Planet.has_space_shipyard pattern)
- [x] Write test: fleet without yard ship returns False
- [x] Write test: fleet with yard ship returns True
- [x] Write test: fleet with destroyed yard ship returns False (if ship not combat_capable)

**Notes:**

---

### Task 1.4: Add `can_build_type()` Method to Fleet [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k "fleet and build_type"`

- [x] Add `can_build_type(self, vehicle_type: str, galaxy=None) -> bool` method
- [x] Ships/fighters/satellites: always True if has_space_shipyard
- [x] Complexes: True only if has_space_shipyard AND at same hex as a planet (requires galaxy param)
- [x] Write test: fleet with yard can build ships
- [x] Write test: fleet without yard cannot build ships
- [x] Write test: fleet with yard at planet hex can build complexes
- [x] Write test: fleet with yard NOT at planet hex cannot build complexes

**Notes:** The galaxy parameter is needed for planet-proximity checks. For tests, mock a galaxy with `get_planets_at_global_hex()`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/simulation/components/` passes
- [x] `pytest tests/unit/strategy/ -k fleet` passes
- [x] `pytest tests/ --testmon` passes (no regressions)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
