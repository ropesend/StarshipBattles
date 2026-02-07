# PROJ-67 Phase 1: Fleet Space Yard Component & Data Model

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-67 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the fleet space yard component, add construction_queue to Fleet, add has_space_shipyard property.

---

## Tasks

### Task 1.1: Add `fleet_space_yard` Component to components.json [Simple]
**File:** `data/components.json`
**Tests:** `pytest tests/unit/simulation/components/ -k space`

- [ ] Add new component entry `fleet_space_yard` near existing `space_shipyard` (~line 1893)
- [ ] Set `allowed_vehicle_types: ["Ship"]` (different from complex's `["Planetary Complex"]`)
- [ ] Set `type: "SpaceShipyard"` (same type string)
- [ ] Use `SpaceShipyard` ability with `construction_speed_bonus: 1.0, max_ship_mass: 100000`
- [ ] Add appropriate mass, hp, crew, resource cost values
- [ ] Add `major_classification: "Production"`
- [ ] Verify component loads correctly: run `pytest tests/unit/simulation/components/`

**Notes:**

---

### Task 1.2: Add `construction_queue` to Fleet [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k fleet`

- [ ] Add `self.construction_queue: list = []` in `Fleet.__init__()` (after line 62)
- [ ] Add `construction_queue` to `Fleet.to_dict()` serialization (line ~571)
- [ ] Add `construction_queue` restoration in `Fleet.from_dict()` (line ~597)
- [ ] Write test: fleet initializes with empty construction_queue
- [ ] Write test: fleet serialization round-trips construction_queue

**Notes:**

---

### Task 1.3: Add `has_space_shipyard` Property to Fleet [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k "fleet and shipyard"`

- [ ] Add `has_space_shipyard` property to Fleet class
- [ ] Implementation: check if any ship in fleet has a component with `SpaceShipyard` ability
- [ ] Use `ShipInstance.get_calculated_stats()` or inspect `design_data` layers (follow Planet.has_space_shipyard pattern)
- [ ] Write test: fleet without yard ship returns False
- [ ] Write test: fleet with yard ship returns True
- [ ] Write test: fleet with destroyed yard ship returns False (if ship not combat_capable)

**Notes:**

---

### Task 1.4: Add `can_build_type()` Method to Fleet [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k "fleet and build_type"`

- [ ] Add `can_build_type(self, vehicle_type: str, galaxy=None) -> bool` method
- [ ] Ships/fighters/satellites: always True if has_space_shipyard
- [ ] Complexes: True only if has_space_shipyard AND at same hex as a planet (requires galaxy param)
- [ ] Write test: fleet with yard can build ships
- [ ] Write test: fleet without yard cannot build ships
- [ ] Write test: fleet with yard at planet hex can build complexes
- [ ] Write test: fleet with yard NOT at planet hex cannot build complexes

**Notes:** The galaxy parameter is needed for planet-proximity checks. For tests, mock a galaxy with `get_planets_at_global_hex()`.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/simulation/components/` passes
- [ ] `pytest tests/unit/strategy/ -k fleet` passes
- [ ] `pytest tests/ --testmon` passes (no regressions)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
