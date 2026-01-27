# Phase 3: Design Metadata & Tech Tree

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-20 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove dual-format handling for design layer format and tech tree requirements.

**Risk:** Low - straightforward pattern simplification

---

## Tasks

### Task 3.1: Standardize design_metadata.py layer format [Simple]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py -v` (if exists)

**Current State:**
- Lines 163-171 in `_calculate_combat_power()`: Dual format handling
- Lines 210-216 in `_calculate_resource_cost()`: Same pattern

**Before:**
```python
if isinstance(layer_data, list):
    components = layer_data
elif isinstance(layer_data, dict):
    components = layer_data.get("components", [])
```

**After:**
```python
components = layer_data  # Always list format
```

- [x] Lines 163-171: Remove isinstance checks, assume direct list format
- [x] Lines 210-216: Same change
- [x] Remove any other dual format handling in this file
- [x] Verify: `grep -n "\.get.*components" game/strategy/data/design_metadata.py` returns nothing (for JSON dict methods)

**Notes:** The `.get('components', [])` pattern remains in `_from_ship` methods which access Ship.layers (runtime objects) - this is correct as Ship instances use `{'components': [...]}` internal structure.

---

### Task 3.2: Standardize planet.py has_space_shipyard [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/strategy/test_production.py -v`

**Current State (Lines 110-130):**
```python
if isinstance(layer_data, list):
    for comp in layer_data: ...
elif isinstance(layer_data, dict):
    for comp in layer_data.get("components", []): ...
```

- [x] Simplify to assume direct list format
- [x] Remove isinstance checks for layer data
- [x] Verify: Shipyard detection still works correctly

**Notes:** Updated test fixtures in test_planetary_facilities.py, test_production.py, and test_complex_workflow.py to use new format.

---

### Task 3.3: Standardize ship_stats_service.py layer iteration [Simple]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py -v`

**Current State (Lines 347-354):**
```python
if isinstance(layer_components, list):
    components = layer_components
elif isinstance(layer_components, dict):
    components = layer_components.get('components', [])
```

- [x] Simplify to assume direct list format
- [x] Remove dual format handling
- [x] Verify: Stats calculation still works

**Notes:** All 65 tests pass.

---

### Task 3.4: Verify design data files use correct format [Simple]
**Files:** `data/designs/*.json` (if any)
**Tests:** Manual verification

- [x] Check if any design JSON files exist with `{"components": [...]}` wrapper format
- [x] If so, convert them to direct list format `[...]`
- [x] If no JSON files exist in data/designs/, skip this task
- [x] Verify: All design files use direct list format

**Notes:** No `data/designs/` folder exists. Design files in `saves/` and `tests/fixtures/` already use direct list format.

---

### Task 3.5: Standardize tech tree requirement format [Simple]
**File:** `game/research/data/tech_tree.py`
**Tests:** `pytest tests/unit/research/ -v` (if exists)

**Current State (Lines 64-70):**
```python
if "level_range" in req:
    level_range = tuple(req["level_range"])
elif "level" in req:
    level_range = (req["level"], req["level"])
else:
    level_range = (1, 1)
```

- [x] Check techtree.json to verify all requirements use `level_range` format
- [x] If any use legacy `level` format, update the JSON file first
- [x] Remove `elif "level" in req` branch, keep only `level_range` handling
- [x] Keep the `else` default for safety
- [x] Verify: `grep -n "'level':" game/research/` shows no single-level format

**Notes:** Updated test_tech_tree.py test_load_node_with_requirements_single_level to use new format.

---

### Task 3.6: Update techtree.json if needed [Simple]
**File:** `data/research/techtree.json` (if exists)
**Tests:** Manual verification + application launch

- [x] Check for any `"level": N` entries (legacy format)
- [x] Convert to `"level_range": [N, N]` format
- [x] Verify: Tech tree loads correctly

**Notes:** 17 entries with `"level": 1` converted to `"level_range": [1, 1]`. All research tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/ tests/unit/research/ -v` passes (relevant tests)
- [x] `grep -rn "\.get.*components" game/strategy/data/design_metadata.py` returns nothing (for JSON data methods)
- [x] No dual format checks remain in layer iteration code
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
