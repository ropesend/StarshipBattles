# Phase 7: Audit Fixes (Cycle 1) [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Actually delete the 5 shim files that were incorrectly marked as deleted

---

## Background

Audit Cycle 1 found that Phases 3 and 6 marked "delete shim file" tasks as complete, but the files were actually converted to backward-compatibility wrapper/alias modules instead of being deleted.

**Files that should NOT exist:**
1. `game/simulation/services/ship_builder_service.py` (11-line alias module)
2. `game/ui/screens/builder_screen.py` (169-line wrapper class)
3. `game/ui/screens/builder_viewmodel.py` (alias module)
4. `game/ui/screens/builder_data_loader.py` (alias module)
5. `game/ui/screens/builder_event_router.py` (alias module)
6. `tests/unit/services/test_ship_builder_service.py` (redundant test file)

---

## Tasks

### Task 7.1: Verify No External Imports of Shim Files [Medium]
**Tests:** `python -c "import game"` should work after deletions

Before deleting, verify that no code imports from these files:

- [x] `grep -r "from game.simulation.services.ship_builder_service" game/ tests/ --include="*.py"` - Found only in test_ship_builder_service.py (will be deleted)
- [x] `grep -r "from game.ui.screens.builder_screen import" game/ tests/ --include="*.py"` - NOTHING
- [x] `grep -r "from game.ui.screens.builder_viewmodel import" game/ tests/ --include="*.py"` - NOTHING
- [x] `grep -r "from game.ui.screens.builder_data_loader import" game/ tests/ --include="*.py"` - NOTHING
- [x] `grep -r "from game.ui.screens.builder_event_router import" game/ tests/ --include="*.py"` - NOTHING

**Notes:** Only test_ship_builder_service.py imports from the shim. services/__init__.py already uses vehicle_design_service directly.

---

### Task 7.2: Delete ShipBuilderService Shim [Simple]
**File:** `game/simulation/services/ship_builder_service.py`
**Tests:** `pytest tests/unit/services/test_vehicle_design_service.py -v`

- [x] Delete file: `game/simulation/services/ship_builder_service.py`
- [x] Delete file: `tests/unit/services/test_ship_builder_service.py` (if it imports from shim)
- [x] Update `game/simulation/services/__init__.py` if it imports from ship_builder_service - NOT NEEDED (already uses vehicle_design_service)
- [x] Verify: `python -c "from game.simulation.services import VehicleDesignService"` works

**Notes:** Both files deleted. __init__.py already imported from vehicle_design_service.

---

### Task 7.3: Delete Builder Screen Shim [Medium]
**File:** `game/ui/screens/builder_screen.py`
**Tests:** `pytest tests/unit/builder/ -v`

- [x] Delete file: `game/ui/screens/builder_screen.py`
- [x] Verify: `python -c "from game.ui.screens.workshop_screen import DesignWorkshopGUI"` works

**Notes:** File deleted. 169-line wrapper class removed.

---

### Task 7.4: Delete Builder ViewModel Shim [Simple]
**File:** `game/ui/screens/builder_viewmodel.py`
**Tests:** `pytest tests/unit/builder/test_builder_viewmodel.py -v`

- [x] Delete file: `game/ui/screens/builder_viewmodel.py`
- [x] Verify: `python -c "from game.ui.screens.workshop_viewmodel import WorkshopViewModel"` works

**Notes:** File deleted.

---

### Task 7.5: Delete Builder DataLoader Shim [Simple]
**File:** `game/ui/screens/builder_data_loader.py`
**Tests:** `pytest tests/unit/builder/test_builder_data_loader.py -v`

- [x] Delete file: `game/ui/screens/builder_data_loader.py`
- [x] Verify: `python -c "from game.ui.screens.workshop_data_loader import WorkshopDataLoader"` works

**Notes:** File deleted.

---

### Task 7.6: Delete Builder EventRouter Shim [Simple]
**File:** `game/ui/screens/builder_event_router.py`
**Tests:** `pytest tests/unit/builder/ -v`

- [x] Delete file: `game/ui/screens/builder_event_router.py`
- [x] Verify: `python -c "from game.ui.screens.workshop_event_router import WorkshopEventRouter"` works

**Notes:** File deleted.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All 5 production shim files are ACTUALLY deleted (not just marked deleted)
- [x] Test file deleted (if applicable)
- [x] `ls game/ui/screens/builder*.py` returns only `builder_selection.py` and `builder_utils.py`
- [x] `ls game/simulation/services/ship_builder*.py` returns nothing
- [x] Run: `pytest tests/unit/builder/ tests/unit/services/ -v` - 187 passed
- [x] Run: `python -c "import game"` - no import errors
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate ready for re-audit
