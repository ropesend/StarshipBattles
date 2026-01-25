# Phase 4: Ship Loader Re-export Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-16 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove get_or_create_validator, load_vehicle_classes, initialize_ship_data re-exports from ship.py
**Risk:** Medium (critical initialization path)
**Files Affected:** ~67

---

## Tasks

### Task 4.1: Update Critical Test Infrastructure [Medium]

**Canonical Location:** `game/simulation/entities/ship_loader.py`
**Re-export Location:** `game/simulation/entities/ship.py` (lines 21-26)
**Tests:** `pytest tests/conftest.py --collect-only`

#### Critical Files (Update First - Session Fixtures):

- [ ] `tests/conftest.py` - imports initialize_ship_data
  - **Change:** `from game.simulation.entities.ship import initialize_ship_data`
  - **To:** `from game.simulation.entities.ship_loader import initialize_ship_data`

- [ ] `tests/fixtures/common.py` - imports initialize_ship_data
  - **Change:** `from game.simulation.entities.ship import initialize_ship_data`
  - **To:** `from game.simulation.entities.ship_loader import initialize_ship_data`

- [ ] `simulation_tests/conftest.py` - imports load_vehicle_classes
  - **Change:** `from game.simulation.entities.ship import load_vehicle_classes`
  - **To:** `from game.simulation.entities.ship_loader import load_vehicle_classes`

- [ ] `tests/infrastructure/session_cache.py` - imports load_vehicle_classes
  - **Change:** `from game.simulation.entities.ship import load_vehicle_classes`
  - **To:** `from game.simulation.entities.ship_loader import load_vehicle_classes`

**Notes:**

---

### Task 4.2: Update App Initialization [Medium]

**Tests:** `python -m game` (manual launch test)

- [ ] `game/app.py` - imports from ship.py for initialization
  - **Change:** `from game.simulation.entities.ship import initialize_ship_data, load_vehicle_classes`
  - **To:** `from game.simulation.entities.ship_loader import initialize_ship_data, load_vehicle_classes`

**Notes:**

---

### Task 4.3: Update UI Layer Imports [Medium]

**Tests:** `pytest tests/unit/ui/ -v`

- [ ] `ui/builder/layer_panel.py` - imports get_or_create_validator
  - **Change:** `from game.simulation.entities.ship import get_or_create_validator`
  - **To:** `from game.simulation.entities.ship_loader import get_or_create_validator`

- [ ] `game/ui/screens/workshop_data_loader.py` - imports load_vehicle_classes, initialize_ship_data
  - **Change:** `from game.simulation.entities.ship import ...`
  - **To:** `from game.simulation.entities.ship_loader import ...`

**Notes:**

---

### Task 4.4: Update Test File Imports [Complex]

**Tests:** `pytest tests/ --testmon`

#### Builder Tests:

- [ ] `tests/unit/builder/test_ship_loading.py` - imports load_vehicle_classes

#### AI Tests:

- [ ] `tests/unit/ai/test_ai.py` - imports load_vehicle_classes

#### Systems Tests:

- [ ] `tests/unit/systems/test_allowed_layers_removal.py` - imports get_or_create_validator

#### Quickstart Tests:

- [ ] `tests/unit/quickstart/test_quickstart_designs.py` - imports load_vehicle_classes

#### Regression Tests:

- [ ] `tests/unit/regressions/test_regressions.py` - imports load_vehicle_classes

#### Repro Issue Tests:

- [ ] `tests/repro_issues/test_bug_08_fuel_validation.py` - imports load_vehicle_classes
- [ ] `tests/repro_issues/test_bug_10_repro.py` - imports load_vehicle_classes

#### Integration Tests:

- [ ] `tests/integration/test_ai_strategy.py` - imports load_vehicle_classes

#### Test Framework:

- [ ] `test_framework/runner.py` - imports load_vehicle_classes

#### Tools:

- [ ] `Tools/maintain_ship_stats.py` - imports load_vehicle_classes

**Notes:**

---

### Task 4.5: Remove Re-exports from ship.py [Simple]

**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Remove the re-export block (lines 21-26):
  ```python
  # Re-export from ship_loader for backward compatibility
  from .ship_loader import (
      get_or_create_validator,
      load_vehicle_classes,
      initialize_ship_data,
  )
  ```

**Notes:**

---

### Task 4.6: Verify No Remaining Usages [Simple]

- [ ] Run verification commands:
  ```bash
  grep -r "from game.simulation.entities.ship import get_or_create_validator" --include="*.py"
  grep -r "from game.simulation.entities.ship import load_vehicle_classes" --include="*.py"
  grep -r "from game.simulation.entities.ship import initialize_ship_data" --include="*.py"
  ```
  Expected: No results (only imports of Ship class should remain)

- [ ] Verify application launches:
  ```bash
  python -m game
  ```

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] `pytest simulation_tests/` passes
- [ ] No circular import errors: `python -c "import game"`
- [ ] Application launches: `python -m game`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
