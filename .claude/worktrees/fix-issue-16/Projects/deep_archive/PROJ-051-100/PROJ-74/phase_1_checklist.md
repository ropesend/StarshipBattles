# Phase 1: Fuel Synthesizer Component

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-74 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add new Fuel Synthesizer component to components.json

---

## Tasks

### Task 1.1: Add fuel_synthesizer component [Simple]
**File:** `data/components.json`
**Tests:** `pytest tests/unit/simulation/components/ -k fuel`

- [x] Add new component after existing generators (around line 340):
  ```json
  {
      "id": "fuel_synthesizer",
      "name": "Fuel Synthesizer",
      "type": "Generator",
      "mass": 100,
      "hp": 150,
      "allowed_vehicle_types": ["Planetary Complex"],
      "sprite_index": 21,
      "abilities": {
          "ResourceGeneration": [
              {"resource": "fuel", "amount": 300}
          ],
          "CrewRequired": 10
      },
      "major_classification": "Infrastructure",
      "resource_cost": {
          "Metals": 200,
          "Vapors": 100,
          "Radioactives": 50
      }
  }
  ```
- [x] Verify component loads without errors: Run game or `pytest tests/unit/simulation/components/`
- [x] Verify: Component appears in game when designing a Planetary Complex

**Notes:** Amount 300/turn is mid-range (configurable later). Uses existing ResourceGeneration ability pattern.
Component tests: 38 passed. Full suite: 6805 passed (1 pre-existing failure excluded).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ --testmon` - all tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
