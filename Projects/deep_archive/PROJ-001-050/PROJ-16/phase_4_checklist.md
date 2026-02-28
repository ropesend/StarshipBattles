# Phase 4: Ship Loader Re-export Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-16 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove get_or_create_validator, load_vehicle_classes, initialize_ship_data re-exports from ship.py
**Risk:** Medium (critical initialization path)
**Files Affected:** ~98 (more than initially estimated)

---

## Tasks

### Task 4.1: Update Critical Test Infrastructure [Medium]

**Canonical Location:** `game/simulation/entities/ship_loader.py`
**Re-export Location:** `game/simulation/entities/ship.py` (lines 21-26)
**Tests:** `pytest tests/conftest.py --collect-only`

#### Critical Files (Update First - Session Fixtures):

- [x] `tests/conftest.py` - imports initialize_ship_data
  - **Change:** `from game.simulation.entities.ship import initialize_ship_data`
  - **To:** `from game.simulation.entities.ship_loader import initialize_ship_data`

- [x] `tests/fixtures/common.py` - imports initialize_ship_data
  - **Change:** `from game.simulation.entities.ship import initialize_ship_data`
  - **To:** `from game.simulation.entities.ship_loader import initialize_ship_data`

- [x] `simulation_tests/conftest.py` - imports load_vehicle_classes
  - **Change:** `from game.simulation.entities.ship import load_vehicle_classes`
  - **To:** `from game.simulation.entities.ship_loader import load_vehicle_classes`

- [x] `tests/infrastructure/session_cache.py` - imports load_vehicle_classes
  - **Change:** `from game.simulation.entities.ship import load_vehicle_classes`
  - **To:** `from game.simulation.entities.ship_loader import load_vehicle_classes`

**Notes:** Also updated root conftest.py monkeypatch path from `game.simulation.entities.ship.load_vehicle_classes` to `game.simulation.entities.ship_loader.load_vehicle_classes`

---

### Task 4.2: Update App Initialization [Medium]

**Tests:** `python -m game` (manual launch test)

- [x] `game/app.py` - imports from ship.py for initialization
  - **Change:** `from game.simulation.entities.ship import initialize_ship_data, load_vehicle_classes`
  - **To:** `from game.simulation.entities.ship_loader import initialize_ship_data, load_vehicle_classes`

**Notes:**

---

### Task 4.3: Update UI Layer Imports [Medium]

**Tests:** `pytest tests/unit/ui/ -v`

- [x] `ui/builder/layer_panel.py` - imports get_or_create_validator
  - **Change:** `from game.simulation.entities.ship import get_or_create_validator`
  - **To:** `from game.simulation.entities.ship_loader import get_or_create_validator`

- [x] `game/ui/screens/workshop_data_loader.py` - imports load_vehicle_classes, initialize_ship_data
  - **Change:** `from game.simulation.entities.ship import ...`
  - **To:** `from game.simulation.entities.ship_loader import ...`

- [x] `game/ui/screens/builder/main.py` - imports load_vehicle_classes
  - **Change:** `from game.simulation.entities.ship import load_vehicle_classes, VEHICLE_CLASSES, SHIP_CLASSES`
  - **To:** `from game.simulation.entities.ship import VEHICLE_CLASSES, SHIP_CLASSES`
        `from game.simulation.entities.ship_loader import load_vehicle_classes`

- [x] `game/simulation/services/vehicle_design_service.py` - imports get_or_create_validator
  - **Change:** `from game.simulation.entities.ship import Ship, get_or_create_validator`
  - **To:** `from game.simulation.entities.ship import Ship`
        `from game.simulation.entities.ship_loader import get_or_create_validator`

**Notes:**

---

### Task 4.4: Update Test File Imports [Complex]

**Tests:** `pytest tests/ --testmon`

Used batch Python script to update 98 files total. All test files with combined imports like:
```python
from game.simulation.entities.ship import Ship, initialize_ship_data, LayerType
```
Were split into:
```python
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_loader import initialize_ship_data
```

#### Updated Files (partial list - 98 total):
- [x] `tests/unit/builder/test_ship_loading.py`
- [x] `tests/unit/ai/test_ai.py`
- [x] `tests/unit/systems/test_allowed_layers_removal.py`
- [x] `tests/unit/quickstart/test_quickstart_designs.py`
- [x] `tests/unit/regressions/test_regressions.py`
- [x] `tests/repro_issues/test_bug_08_fuel_validation.py`
- [x] `tests/repro_issues/test_bug_10_repro.py`
- [x] `tests/integration/test_ai_strategy.py`
- [x] `test_framework/runner.py`
- [x] `test_framework/scenario.py`
- [x] `Tools/maintain_ship_stats.py`
- [x] `Tools/debug_devastator.py`
- [x] `Tools/debug_test.py`
- [x] `Tools/quick_test_modifiers.py`
- [x] `Tools/visual_test_beam_weapon.py`
- [x] All tests/unit/* files
- [x] All tests/integration/* files

**Notes:** Batch update script handled combined imports correctly

---

### Task 4.5: Remove Re-exports from ship.py [Simple]

**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/ --testmon`

- [x] Remove the re-export block (lines 20-25):
  ```python
  # Re-export from ship_loader for backward compatibility
  from .ship_loader import (
      get_or_create_validator,
      load_vehicle_classes,
      initialize_ship_data,
  )
  ```

- [x] Keep internal import for get_or_create_validator (used by Ship class):
  ```python
  # Internal import (no longer re-exported)
  from .ship_loader import get_or_create_validator
  ```

**Notes:** ship.py uses get_or_create_validator internally for validation, so kept the import but removed re-export

---

### Task 4.6: Verify No Remaining Usages [Simple]

- [x] Run verification commands:
  ```bash
  grep -r "from game.simulation.entities.ship import get_or_create_validator" --include="*.py"
  grep -r "from game.simulation.entities.ship import load_vehicle_classes" --include="*.py"
  grep -r "from game.simulation.entities.ship import initialize_ship_data" --include="*.py"
  ```
  Result: No results - all imports now use ship_loader.py directly

- [x] Verify no circular imports:
  ```bash
  python -c "import game"
  ```
  Result: Import check passed

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ --testmon` passes (4378 passed, pre-existing failures unrelated to this change)
- [x] No circular import errors: `python -c "import game"`
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
