# Phase 3: Parameter Naming Standardization (NCA-002)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-46 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Standardize `filepath` → `file_path` across 14 files, 127 occurrences

---

## Sub-phase 3A: Core Utilities

### Task 3A.1: Update json_utils.py [Medium]
**File:** `game/core/json_utils.py`
**Tests:** `pytest tests/unit/core/`

- [x] Rename parameter `filepath` → `file_path` in `load_json()` (line 27)
- [x] Update all internal references to `filepath` in `load_json()`
- [x] Rename parameter `filepath` → `file_path` in `load_json_required()` (line 64)
- [x] Update all internal references in `load_json_required()`
- [x] Rename parameter `filepath` → `file_path` in `save_json()` (line 93)
- [x] Update all internal references in `save_json()`
- [x] Update docstrings to reflect new parameter name
- [x] Search for all call sites using keyword arg `filepath=` and update
- [x] Run tests

**Notes:** No call sites using `filepath=` keyword arg - all use positional args.

---

### Task 3A.2: Update resources.py [Medium]
**File:** `game/core/resources.py`
**Tests:** `pytest tests/unit/core/`

- [x] Rename parameter `filepath` → `file_path` in `_resolve_resource_path()` (line 22)
- [x] Update all internal references
- [x] Rename parameter `filepath` → `file_path` in `load_resources_data()` (line 46)
- [x] Update all internal references
- [x] Rename parameter `filepath` → `file_path` in `load_resources()` (line 82)
- [x] Update all internal references
- [x] Update docstrings
- [x] Run tests

**Notes:** Complete.

---

## Sub-phase 3B: Simulation Layer

### Task 3B.1: Update component.py [Medium]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/simulation/`

- [x] Rename `filepath` → `file_path` in `load_components_data()` (line ~692)
- [x] Update all internal references
- [x] Rename `filepath` → `file_path` in `load_components()` (line ~735)
- [x] Update all internal references
- [x] Rename `filepath` → `file_path` in `load_modifiers_data()` (line ~769)
- [x] Update all internal references
- [x] Rename `filepath` → `file_path` in `load_modifiers()` (line ~815)
- [x] Update all internal references
- [x] Update docstrings
- [x] Run tests

**Notes:** Complete.

---

### Task 3B.2: Update ship_loader.py [Simple]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/entities/`

- [x] Rename `filepath` → `file_path` in `load_vehicle_classes()` (line ~87)
- [x] Also rename `layers_filepath` → `layers_file_path` if present
- [x] Update all internal references
- [x] Update docstrings
- [x] Update call sites: workshop_data_loader.py, registry.py
- [x] Run tests

**Notes:** Also updated `load_vehicle_classes_data()` and 2 call sites using `layers_filepath=` keyword arg.

---

### Task 3B.3: Update design_loader.py [Simple]
**File:** `game/simulation/services/design_loader.py`
**Tests:** `pytest tests/unit/services/`

- [x] Rename `filepath` → `file_path` in `load_ship_from_file()` (line ~61)
- [x] Update all internal references
- [x] Update docstrings
- [x] Run tests

**Notes:** Complete.

---

## Sub-phase 3C: Strategy/UI Layer

### Task 3C.1: Update tech_tree.py [Simple]
**File:** `game/research/data/tech_tree.py`
**Tests:** `pytest tests/unit/research/`

- [x] Rename `filepath` → `file_path` in `TechTree.load_from_json()` (line ~29)
- [x] Update all internal references
- [x] Update docstrings
- [x] Run tests

**Notes:** Complete.

---

### Task 3C.2: Update design_metadata.py [Simple]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Rename `filepath` → `file_path` in `DesignMetadata.from_design_file()` (line ~75)
- [x] Update all internal references
- [x] Update docstrings
- [x] Run tests

**Notes:** Complete.

---

### Task 3C.3: Update race_config.py [Simple]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Rename `filepath` → `file_path` in `RaceConfig.save()` (line ~117)
- [x] Rename `filepath` → `file_path` in `RaceConfig.load()` (line ~137)
- [x] Update all internal references
- [x] Update docstrings
- [x] Run tests

**Notes:** Complete.

---

### Task 3C.4: Update setup_data_io.py [Simple]
**File:** `game/ui/screens/setup_data_io.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Rename `filepath` → `file_path` in `save_battle_setup()` (line ~140)
- [x] Rename `filepath` → `file_path` in `load_battle_setup()` (line ~183)
- [x] Update all internal references
- [x] Update docstrings
- [x] Run tests

**Notes:** Complete.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Grep for "filepath" shows no remaining occurrences (except comments/strings)
- [x] Run `pytest tests/ --testmon` - all affected tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4

## Implementation Notes
- 2026-01-30: Renamed all `filepath` parameters to `file_path` across 10 files
- Updated 2 call sites using `layers_filepath=` keyword arg in workshop_data_loader.py and registry.py
- Tests: 2781 passed, 1 skipped
