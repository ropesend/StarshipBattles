# Phase 9: Constant Consolidation (AR-013, AR-05)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 9`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Single canonical location for LayerType and shared constants

---

## Prerequisites
- [x] Core phases (1-5) complete

## Background

**Problem (AR-013, AR-05):**
- LayerType defined in `game/simulation/components/component_constants.py`
- Also imported from `game/core/constants.py` in some UI files
- AI layer imports from simulation to use LayerType
- Confusing and error-prone

**Target:** Move LayerType to `game/core/constants.py` if not already, update all imports.

---

## Tasks

### Task 9.1: Audit LayerType Locations [Simple] - COMPLETE
**Files:** Multiple
**Tests:** N/A (analysis)

- [x] Check if LayerType exists in `game/core/constants.py`
- [x] Check if LayerType exists in `game/simulation/components/component_constants.py`
- [x] Run grep to find all LayerType imports:
  ```bash
  grep -rn "LayerType" game/
  ```
- [x] Document all import locations in findings/phase_9_audit.md
- [x] Identify canonical location

**Notes:** LayerType is canonically defined in game/core/constants.py (lines 82-93).
component_constants.py has a re-export. Found 16 files using canonical location (UI),
12 simulation files using deprecated path, 1 AI file (AR-013), and 3 UI files with
incorrect local imports from ship.py.

---

### Task 9.2: Establish Canonical Location [Simple] - COMPLETE
**File:** `game/core/constants.py`
**Tests:** `pytest tests/unit/core/`

If LayerType is not in core:
- [x] Move LayerType enum to `game/core/constants.py` (already there from PROJ-17)
- [x] Add to `__all__` exports (added comprehensive __all__ list)
- [x] Verify definition is complete

If already in core:
- [x] Verify it's in `__all__` (added)
- [x] Document as canonical location

**Notes:** LayerType was already in game/core/constants.py (lines 82-93).
Added __all__ export list for proper API definition. Verified import works correctly.

---

### Task 9.3: Update Simulation Imports [Medium] - COMPLETE
**Files:** All simulation files importing LayerType
**Tests:** `pytest tests/unit/simulation/`

- [x] Find all simulation files importing LayerType:
  ```bash
  grep -rn "from.*component_constants.*LayerType" game/simulation/
  ```
- [x] Update to import from `game.core.constants`
- [x] Remove re-exports from component_constants.py (keeping for backward compat - see Task 9.7)
- [x] Run simulation tests

**Notes:** Updated 12 simulation files:
- designs.py, validation/base.py, entities/ship_stats.py
- entities/ship_serialization.py, entities/ship_combat_engine.py
- entities/ship.py, entities/ship_component_manager.py
- battle_state.py, ship_validator.py, systems/stats.py
- services/vehicle_design_service.py, systems/validator.py
All 138 simulation tests pass.

---

### Task 9.4: Update AI Imports (AR-013) [Simple] - COMPLETE
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/`

**Current issue:** AI imports LayerType from simulation

- [x] Update import to use `game.core.constants`
- [x] Verify no other AI files import from simulation for constants
- [x] Run AI tests

**Notes:** Updated target_evaluator.py to import LayerType from game.core.constants
alongside AttackType (single import line). Verified no other AI files import
from simulation. All 215 AI tests pass. AR-013 cross-layer violation resolved.

---

### Task 9.5: Update UI Imports [Simple] - COMPLETE
**Files:** All UI files importing LayerType
**Tests:** `pytest tests/unit/ui/`

- [x] Find all UI files importing LayerType
- [x] Update to import from `game.core.constants`
- [x] Run UI tests

**Notes:** Fixed 3 UI files with incorrect imports from ship.py:
- left_panel.py:259 - deferred import updated
- stats_config.py:126 - deferred import updated
- workshop_viewmodel.py:22 - TYPE_CHECKING import updated
16 other UI files already use canonical location. All 564 UI tests pass.

---

### Task 9.6: Update Strategy Imports [Simple] - N/A
**Files:** All strategy files importing LayerType
**Tests:** `pytest tests/unit/strategy/`

- [x] Find all strategy files importing LayerType
- [x] Update to import from `game.core.constants` (N/A - none found)
- [x] Run strategy tests (N/A)

**Notes:** No strategy files import LayerType. Grep confirmed no matches.

---

### Task 9.7: Remove Duplicate Definitions [Simple] - COMPLETE
**File:** `game/simulation/components/component_constants.py`
**Tests:** `pytest tests/unit/simulation/`

- [x] Remove LayerType definition if moved to core (already done in PROJ-17)
- [x] Or add deprecation re-export (already present):
  ```python
  # Re-export LayerType from core for backward compatibility
  # PROJ-17: LayerType moved to game/core/constants.py for proper layer architecture
  from game.core.constants import LayerType
  ```
- [x] Run tests to verify no breakage

**Notes:** The re-export was already in place from PROJ-17. Added __all__ export
list to make API explicit. All 346 simulation tests pass.

---

### Task 9.8: Verify No Duplicate Imports [Simple] - COMPLETE
**Tests:** `python -c "from game.core.constants import LayerType; from game.simulation.components.component_constants import LayerType"`

- [x] Verify both imports resolve to same enum
- [x] Verify no import errors
- [x] Run full test suite

**Notes:** Verified CoreLayerType is SimLayerType (same id, same values).
Incremental test suite: 738 passed, 1 skipped.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] LayerType has single canonical location in game.core.constants
- [x] All imports updated to use canonical location
- [x] No duplicate definitions (only re-exports with deprecation warning if needed)
- [x] All tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 10
