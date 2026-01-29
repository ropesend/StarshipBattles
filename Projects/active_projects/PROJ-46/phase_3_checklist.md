# Phase 3: Parameter Naming Standardization (NCA-002)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-46 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Standardize `filepath` → `file_path` across 14 files, 127 occurrences

---

## Sub-phase 3A: Core Utilities

### Task 3A.1: Update json_utils.py [Medium]
**File:** `game/core/json_utils.py`
**Tests:** `pytest tests/unit/core/`

- [ ] Rename parameter `filepath` → `file_path` in `load_json()` (line 27)
- [ ] Update all internal references to `filepath` in `load_json()`
- [ ] Rename parameter `filepath` → `file_path` in `load_json_required()` (line 64)
- [ ] Update all internal references in `load_json_required()`
- [ ] Rename parameter `filepath` → `file_path` in `save_json()` (line 93)
- [ ] Update all internal references in `save_json()`
- [ ] Update docstrings to reflect new parameter name
- [ ] Search for all call sites using keyword arg `filepath=` and update
- [ ] Run tests

**Notes:**

---

### Task 3A.2: Update resources.py [Medium]
**File:** `game/core/resources.py`
**Tests:** `pytest tests/unit/core/`

- [ ] Rename parameter `filepath` → `file_path` in `_resolve_resource_path()` (line 22)
- [ ] Update all internal references
- [ ] Rename parameter `filepath` → `file_path` in `load_resources_data()` (line 46)
- [ ] Update all internal references
- [ ] Rename parameter `filepath` → `file_path` in `load_resources()` (line 82)
- [ ] Update all internal references
- [ ] Update docstrings
- [ ] Run tests

**Notes:**

---

## Sub-phase 3B: Simulation Layer

### Task 3B.1: Update component.py [Medium]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/simulation/`

- [ ] Rename `filepath` → `file_path` in `load_components_data()` (line ~692)
- [ ] Update all internal references
- [ ] Rename `filepath` → `file_path` in `load_components()` (line ~735)
- [ ] Update all internal references
- [ ] Rename `filepath` → `file_path` in `load_modifiers_data()` (line ~769)
- [ ] Update all internal references
- [ ] Rename `filepath` → `file_path` in `load_modifiers()` (line ~815)
- [ ] Update all internal references
- [ ] Update docstrings
- [ ] Run tests

**Notes:**

---

### Task 3B.2: Update ship_loader.py [Simple]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/entities/`

- [ ] Rename `filepath` → `file_path` in `load_vehicle_classes()` (line ~87)
- [ ] Also rename `layers_filepath` → `layers_file_path` if present
- [ ] Update all internal references
- [ ] Update docstrings
- [ ] Run tests

**Notes:**

---

### Task 3B.3: Update design_loader.py [Simple]
**File:** `game/simulation/services/design_loader.py`
**Tests:** `pytest tests/unit/services/`

- [ ] Rename `filepath` → `file_path` in `load_ship_from_file()` (line ~61)
- [ ] Update all internal references
- [ ] Update docstrings
- [ ] Run tests

**Notes:**

---

## Sub-phase 3C: Strategy/UI Layer

### Task 3C.1: Update tech_tree.py [Simple]
**File:** `game/research/data/tech_tree.py`
**Tests:** `pytest tests/unit/research/`

- [ ] Rename `filepath` → `file_path` in `TechTree.load_from_json()` (line ~29)
- [ ] Update all internal references
- [ ] Update docstrings
- [ ] Run tests

**Notes:**

---

### Task 3C.2: Update design_metadata.py [Simple]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/`

- [ ] Rename `filepath` → `file_path` in `DesignMetadata.from_design_file()` (line ~75)
- [ ] Update all internal references
- [ ] Update docstrings
- [ ] Run tests

**Notes:**

---

### Task 3C.3: Update race_config.py [Simple]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/`

- [ ] Rename `filepath` → `file_path` in `RaceConfig.save()` (line ~117)
- [ ] Rename `filepath` → `file_path` in `RaceConfig.load()` (line ~137)
- [ ] Update all internal references
- [ ] Update docstrings
- [ ] Run tests

**Notes:**

---

### Task 3C.4: Update setup_data_io.py [Simple]
**File:** `game/ui/screens/setup_data_io.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Rename `filepath` → `file_path` in `save_battle_setup()` (line ~140)
- [ ] Rename `filepath` → `file_path` in `load_battle_setup()` (line ~183)
- [ ] Update all internal references
- [ ] Update docstrings
- [ ] Run tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Grep for "filepath" shows no remaining occurrences (except comments/strings)
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
