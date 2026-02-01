# Phase 4: Clean Up Serialization & Format Support

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-42 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove dead format support code, standardize serialization
**Complexity:** Medium

---

## Pre-Phase Checklist
- [x] Phase 3 complete
- [x] Read [design.md](design.md) - review "Serialization Legacy Formats" section
- [x] Verify: `pytest tests/` passes

---

## Task 4.1: Remove Ship String Format Parser [Simple]
**Issue:** BCD-010 (partial)
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/entities/test_ship_serialization.py`

### Subtasks
- [x] Locate the string format handling code (lines 168-172)
- [x] Replace with explicit dict requirement - raises ValueError for non-dict
- [x] Verify no saves use string format (all tests pass with dict-only)
- [x] Run tests: `pytest tests/unit/entities/test_ship_serialization.py`

**Notes:** Implemented strict dict requirement. Non-dict types now raise ValueError.

---

## Task 4.2: Standardize Component Serialization to Dict-Only [Simple]
**Issue:** BCD-010
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/entities/test_ship_serialization.py`

### Subtasks
- [x] Review `to_dict()` method - verify it outputs dict format
- [x] Review `from_dict()` method - verify it only accepts dict format (after Task 4.1)
- [x] Add format version field to serialization output: `"_format_version": "2.0"`
- [x] Add version comment in `from_dict()` - graceful migration (dict check is enforcement)
- [x] Run tests: `pytest tests/unit/entities/test_ship_serialization.py`

**Notes:** Added `_format_version: "2.0"` to output. Version check is informational; dict type check is actual enforcement.

---

## Task 4.3: Clean Up Formation Editor Dual Format Support [Medium]
**Issue:** LPH-007
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/ui/` (or manual test formation editor)

### Subtasks
- [x] Locate dual format handling (lines 204-209)
- [x] Replace with dict-only loading - raises ValueError for non-dict
- [x] Save format already uses dict format in `save_to_file()`
- [x] Tests pass (no formation editor specific tests, but no regressions)

**Notes:** Legacy list format support removed. Arrows must be dict: `{"pos": [x, y], "rotation_mode": "..."}`

---

## Task 4.4: Remove Stats Mismatch Warning Fallback [Simple]
**Issue:** BCD-006
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/entities/test_ship_serialization.py`

### Subtasks
- [x] Locate stats mismatch handling (lines 208-246)
- [x] Decision: Option B - Keep warning with documentation
- [x] Added comment explaining this is data integrity verification, not compat fallback
- [x] Run tests: `pytest tests/unit/entities/test_ship_serialization.py`

**Notes:** Stats mismatch verification is intentional - detects component/formula changes. Not a backward compat issue.

---

## Task 4.5: Clean Up getattr Defaults for Ship Attributes [Simple]
**Issue:** BCD-009
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/entities/test_ship_serialization.py`

### Subtasks
- [x] Locate getattr with defaults (lines 41-66)
- [x] Verified: `vehicle_type` is set in `Ship.__init__` - removed getattr
- [x] Verified: strategic stats (`total_strategic_movement`, `warp_max_tonnage`, etc.) are set during `recalculate_stats()` - kept getattr with documentation
- [x] Added comment explaining why some getattr remain (defensive for uncalculated ships)
- [x] Run tests: `pytest tests/unit/entities/test_ship_serialization.py`

**Notes:** `vehicle_type` always exists (set in `__init__`). Strategic stats set during recalculate, so getattr is protective.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/` - all tests pass (5360 passed, 3 skipped)
- [x] Verify no isinstance checks for legacy formats remain in serialization
- [x] Verify format version field added to serialization (`_format_version: "2.0"`)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
- [x] Commit: "PROJ-42 Phase 4: Standardize serialization formats"
