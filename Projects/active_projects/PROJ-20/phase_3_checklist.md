# Phase 3: Design Metadata & Tech Tree

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-20 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Lines 163-171: Remove isinstance checks, assume direct list format
- [ ] Lines 210-216: Same change
- [ ] Remove any other dual format handling in this file
- [ ] Verify: `grep -n "\.get.*components" game/strategy/data/design_metadata.py` returns nothing

**Notes:**

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

- [ ] Simplify to assume direct list format
- [ ] Remove isinstance checks for layer data
- [ ] Verify: Shipyard detection still works correctly

**Notes:**

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

- [ ] Simplify to assume direct list format
- [ ] Remove dual format handling
- [ ] Verify: Stats calculation still works

**Notes:**

---

### Task 3.4: Verify design data files use correct format [Simple]
**Files:** `data/designs/*.json` (if any)
**Tests:** Manual verification

- [ ] Check if any design JSON files exist with `{"components": [...]}` wrapper format
- [ ] If so, convert them to direct list format `[...]`
- [ ] If no JSON files exist in data/designs/, skip this task
- [ ] Verify: All design files use direct list format

**Notes:**

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

- [ ] Check techtree.json to verify all requirements use `level_range` format
- [ ] If any use legacy `level` format, update the JSON file first
- [ ] Remove `elif "level" in req` branch, keep only `level_range` handling
- [ ] Keep the `else` default for safety
- [ ] Verify: `grep -n "'level':" game/research/` shows no single-level format

**Notes:**

---

### Task 3.6: Update techtree.json if needed [Simple]
**File:** `data/research/techtree.json` (if exists)
**Tests:** Manual verification + application launch

- [ ] Check for any `"level": N` entries (legacy format)
- [ ] Convert to `"level_range": [N, N]` format
- [ ] Verify: Tech tree loads correctly

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/ tests/unit/research/ -v` passes (relevant tests)
- [ ] `grep -rn "\.get.*components" game/strategy/data/design_metadata.py` returns nothing
- [ ] No dual format checks remain in layer iteration code
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
