# Phase 3: Sample component (Flagship Sensor Array) + integration

**Status:** Not Started
**Objective:** Add a real, gameplay-meaningful component that exercises the fleet-projection path end-to-end. Validates the framework with actual data, not just synthetic tests.

---

## Tasks

### Task 3.1: Choose / introduce the new strategic ability [Medium]
**File:** Either reuse an existing ability (preferred) or add a new one (`game/simulation/components/abilities/sensor.py` or similar).

- [ ] Decide: does an appropriate ability already exist (e.g. `SensorBoost`)? If yes, reuse. If no, add one with name like `SensorRange` or `SensorBoost` and `kind=multiplier` (or `rate` if the gameplay is "sensor radius +N hexes per turn" — design call).
- [ ] If new: register in `SYSTEM_EFFECT_ABILITIES` and add display formatting in the panel renderer.
- [ ] Add tests for the ability's data shape and validation.

**Notes:**

### Task 3.2: Add Flagship Sensor Array component [Medium]
**File:** `data/components.json`

- [ ] Add a new component:
  ```json
  {
    "id": "flagship_sensor_array",
    "name": "Flagship Sensor Array",
    "type": "Sensor",
    "mass": "= ...",
    "hp": "= ...",
    "allowed_vehicle_types": ["Ship"],
    "abilities": {
      "SensorBoost": {"multiplier": 1.5, "scope": "allied_sector"}
    },
    ...
  }
  ```
- [ ] Add validation tests confirming the new component loads correctly from the registry.

**Notes:**

### Task 3.3: Add an existing test ship design that mounts the new component [Simple]
**File:** Either an existing `data/designs/qs_*.json` or a new test-ship design.

- [ ] Add the Flagship Sensor Array to (e.g.) `qs_battleship.json` so the QS battleship is a "flagship" with strategic sensor projection.
- [ ] Update tests in `tests/unit/quickstart/test_quickstart_designs.py` if the addition triggers validation.

**Notes:**

### Task 3.4: End-to-end integration test [Complex]
**File:** `tests/integration/strategy/test_fleet_sector_effects_end_to_end.py` (NEW)

- [ ] Build fixture: a galaxy with Player 1's fleet (containing a flagship with the new component) at hex H, and Player 1 also having an "observer" fleet at H.
- [ ] When the UI queries Sector Effects at H from Player 1's perspective: the SensorBoost effect appears with `source_label = "Flagship 'Indomitable' (Player 1)"`.
- [ ] Move the fleet to a different hex H' — the effect now appears at H', not H.
- [ ] Have an enemy fleet sit at H — the enemy does NOT see the SensorBoost (allied_sector scope filter).
- [ ] Combat in H — confirm `scope: fleet` aura abilities (from existing components) still flow through the FleetAuraManager combat path correctly (they were not consumed by FleetAbilitySource).

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
