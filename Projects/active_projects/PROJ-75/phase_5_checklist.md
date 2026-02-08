# Phase 5: Maintenance System

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-75 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Deduct 5% of build cost per turn, scuttle on failure

---

## Tasks

### Task 5.1: Write TDD tests for MaintenanceEngine [Medium]
**File:** `tests/unit/strategy/engine/test_maintenance_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py -v`

- [ ] Create test file with TestMaintenanceEngine class
- [ ] Test: maintenance cost = 5% of total build cost
- [ ] Test: successful payment deducts from empire pool
- [ ] Test: facility scuttled when payment fails
- [ ] Test: ship scuttled when payment fails
- [ ] Test: multiple facilities - all checked in one pass
- [ ] Test: scuttle cascade prevented (one-pass processing)
- [ ] Test: non-operational facilities have no maintenance
- [ ] Test: scuttle events returned for notification

**Notes:**

---

### Task 5.2: Create MaintenanceEngine class [Medium]
**File:** `game/strategy/engine/maintenance_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py -v`

- [ ] Create `MaintenanceEngine` class:
  ```python
  @dataclass
  class ScuttleEvent:
      empire_id: int
      entity_type: str  # "facility" or "ship"
      entity_name: str
      location: str

  class MaintenanceEngine:
      MAINTENANCE_RATE = 0.05  # 5% per turn

      def __init__(self, *, registries: GameRegistries = None):
          self._registries = registries

      def process_maintenance(self, empires) -> List[ScuttleEvent]:
          """Process maintenance for all empires. Returns scuttle events."""
          events = []
          for empire in empires:
              events.extend(self._process_empire(empire))
          return events
  ```
- [ ] Implement `_process_empire(empire) -> List[ScuttleEvent]`
- [ ] Implement `_calculate_maintenance_cost(design_data) -> Dict[str, float]`
- [ ] Implement facility and ship maintenance checking
- [ ] Implement scuttling logic (remove from lists)

**Notes:**

---

### Task 5.3: Implement scuttling logic [Medium]
**File:** `game/strategy/engine/maintenance_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py -v`

- [ ] Implement `_scuttle_facility(planet, facility) -> ScuttleEvent`:
  ```python
  def _scuttle_facility(self, planet, facility) -> ScuttleEvent:
      planet.facilities.remove(facility)
      return ScuttleEvent(
          empire_id=planet.owner_id,
          entity_type="facility",
          entity_name=facility.name,
          location=f"Planet {planet.id}"
      )
  ```
- [ ] Implement `_scuttle_ship(fleet, ship) -> ScuttleEvent`
- [ ] Implement `_cleanup_empty_fleets(empire)` to remove fleets with no ships

**Notes:**

---

### Task 5.4: Integrate MaintenanceEngine into TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_maintenance.py -v`

- [ ] Write integration test in `tests/integration/strategy/turn_engine/test_maintenance.py` (NEW)
- [ ] Add `_maintenance_engine` property with lazy initialization
- [ ] Call after harvesting, before per-turn consumption
- [ ] Store/log scuttle events for UI notification

**Notes:**

---

### Task 5.5: Add ship maintenance [Medium]
**File:** `game/strategy/engine/maintenance_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py -v`

- [ ] Iterate empire.fleets -> ships
- [ ] Calculate ship maintenance from design_data
- [ ] Deduct from empire pool or scuttle ship
- [ ] Handle fleet becoming empty after scuttles

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
