# Phase 1: PLANET_RESOURCES Re-export Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-16 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove the PLANET_RESOURCES re-export from planet.py and update all callers to import from game.core.constants
**Risk:** Very Low
**Files Affected:** 8

---

## Tasks

### Task 1.1: Update Callers to Import from Canonical Location [Simple]

**Canonical Location:** `game/core/constants.py` (line 77)
**Re-export Location:** `game/strategy/data/planet.py` (lines 6-8)
**Tests:** `pytest tests/unit/components/test_resource_costs.py tests/unit/validation/test_component_definitions.py -v`

#### Files to Update:

- [x] `game/ui/screens/planet_list_window.py`
  - **Change:** `from game.strategy.data.planet import PLANET_RESOURCES`
  - **To:** `from game.core.constants import PLANET_RESOURCES`

- [x] `ui/builder/detail_panel.py` (conditional import)
  - **Change:** `from game.strategy.data.planet import PLANET_RESOURCES`
  - **To:** `from game.core.constants import PLANET_RESOURCES`

- [x] `ui/builder/stats_config.py` (conditional import)
  - **Change:** `from game.strategy.data.planet import PLANET_RESOURCES`
  - **To:** `from game.core.constants import PLANET_RESOURCES`

- [x] `ui/builder/structure_list_items.py` (multiple locations)
  - **Change:** `from game.strategy.data.planet import PLANET_RESOURCES`
  - **To:** `from game.core.constants import PLANET_RESOURCES`

- [x] `game/strategy/data/planet_gen.py` (combined import)
  - **Change:** `from game.strategy.data.planet import Planet, PlanetType, PLANET_RESOURCES`
  - **To:** Two imports: `from game.core.constants import PLANET_RESOURCES` and `from game.strategy.data.planet import Planet, PlanetType`

- [x] `tests/unit/components/test_resource_costs.py`
  - **Change:** `from game.strategy.data.planet import PLANET_RESOURCES`
  - **To:** `from game.core.constants import PLANET_RESOURCES`

- [x] `tests/unit/validation/test_component_definitions.py` (conditional)
  - **Change:** `from game.strategy.data.planet import PLANET_RESOURCES`
  - **To:** `from game.core.constants import PLANET_RESOURCES`

**Notes:** All 7 files updated. planet_gen.py had a combined import that wasn't detected by the initial grep (import line included other items).

---

### Task 1.2: Remove Re-export from planet.py [Simple]

**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/ --testmon`

- [x] Remove the re-export block (lines 6-8):
  ```python
  # PROJ-11: Global Resource Definition moved to game.core.constants
  # Re-exported here for backward compatibility
  from game.core.constants import PLANET_RESOURCES
  ```

**Notes:** Re-export block removed from planet.py. Also had to update planet_gen.py which was importing PLANET_RESOURCES from planet.py in a combined import statement.

---

### Task 1.3: Verify No Remaining Usages [Simple]

- [x] Run verification command:
  ```bash
  grep -r "from game.strategy.data.planet import PLANET_RESOURCES" --include="*.py"
  ```
  Expected: No results - VERIFIED

- [x] Run import verification:
  ```bash
  python -c "from game.core.constants import PLANET_RESOURCES; print('OK:', PLANET_RESOURCES)"
  ```
  Expected: `OK: ['Metals', 'Organics', 'Vapors', 'Radioactives', 'Exotics']` - VERIFIED

**Notes:** Both verification checks pass. No remaining usages of the old import.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ --testmon` passes (57 passed, 1 pre-existing error in test_ui_widgets.py)
- [x] No circular import errors: `python -c "import game"` - OK
- [ ] Application launches: `python -m game` (not tested - GUI test)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
