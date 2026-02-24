# Phase 2: Strategy Loaders Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-170 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate all 24 ValueErrors in strategy generation loaders. No external callers — safest batch.
**Estimated Effort:** 2 hours

---

## Tasks

### Task 2.1: system_blueprints_loader.py — 15 ValueErrors [Simple]
**File:** `game/strategy/generation/loaders/system_blueprints_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k blueprint`

- [x] Add imports: `from game.core.exceptions import ValidationException` and `from game.core.error_codes import ErrorCode`
- [x] Line 94: `raise ValueError("No blueprints with positive weight found")` → `raise ValidationException("No blueprints with positive weight found", code=ErrorCode.VALIDATION_FAILED.value, context={"reason": "no_positive_weights"})`
- [x] Line 118: `raise ValueError("Blueprints data must be a dict")` → `raise ValidationException("Blueprints data must be a dict", code=ErrorCode.SCHEMA_VALIDATION_ERROR.value, context={"expected_type": "dict", "actual_type": type(data).__name__})`
- [x] Line 121: `raise ValueError("Missing 'blueprints' key")` → `raise ValidationException("Missing 'blueprints' key", code=ErrorCode.SCHEMA_VALIDATION_ERROR.value, context={"missing_key": "blueprints"})`
- [x] Line 125: `raise ValueError("'blueprints' must be a dict")` → `raise ValidationException("'blueprints' must be a dict", code=ErrorCode.SCHEMA_VALIDATION_ERROR.value, context={"key": "blueprints", "expected_type": "dict"})`
- [x] Line 143: `raise ValueError(f"Blueprint '{name}' missing 'star_count'")` → `raise ValidationException(f"Blueprint '{name}' missing required field", code=ErrorCode.SCHEMA_VALIDATION_ERROR.value, context={"blueprint": name, "missing_field": "star_count"})`
- [x] Line 145: similar for 'planet_count' → same pattern
- [x] Line 147: similar for 'weight' → same pattern
- [x] Line 153: star_count range → `code=ErrorCode.OUT_OF_RANGE.value`
- [x] Line 157: star_count range invalid → `code=ErrorCode.OUT_OF_RANGE.value`
- [x] Line 159: star_count missing min → `code=ErrorCode.SCHEMA_VALIDATION_ERROR.value`
- [x] Line 161: star_count type → `code=ErrorCode.SCHEMA_VALIDATION_ERROR.value`
- [x] Line 166: planet_count must be dict → `code=ErrorCode.SCHEMA_VALIDATION_ERROR.value`
- [x] Line 168: planet_count missing min/max → `code=ErrorCode.SCHEMA_VALIDATION_ERROR.value`
- [x] Line 170: planet_count range invalid → `code=ErrorCode.OUT_OF_RANGE.value`
- [x] Line 174: weight must be positive → `code=ErrorCode.OUT_OF_RANGE.value`
- [x] Verify: `pytest tests/unit/strategy/generation/ -k blueprint`

**Notes:** All 15 ValueError converted to ValidationException with appropriate error codes.

### Task 2.2: astrophysics_loader.py — 7 ValueErrors [Simple]
**File:** `game/strategy/generation/loaders/astrophysics_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k astrophysics`

- [x] Add imports: `from game.core.exceptions import ValidationException` and `from game.core.error_codes import ErrorCode`
- [x] Line 119: missing required section → `ValidationException` + `SCHEMA_VALIDATION_ERROR`
- [x] Line 126: missing mass distribution → `ValidationException` + `SCHEMA_VALIDATION_ERROR`
- [x] Line 133: missing orbit zone → `ValidationException` + `SCHEMA_VALIDATION_ERROR`
- [x] Line 138: habitable_zone missing factors → `ValidationException` + `SCHEMA_VALIDATION_ERROR`
- [x] Line 143: atmosphere_retention missing thresholds → `ValidationException` + `SCHEMA_VALIDATION_ERROR`
- [x] Line 148: classification missing mass_thresholds → `ValidationException` + `SCHEMA_VALIDATION_ERROR`
- [x] Line 150: classification missing temperature_thresholds → `ValidationException` + `SCHEMA_VALIDATION_ERROR`
- [x] Verify: `pytest tests/unit/strategy/generation/ -k astrophysics`

**Notes:** All 7 ValueError converted to ValidationException with SCHEMA_VALIDATION_ERROR code.

### Task 2.3: galaxy_layouts_loader.py — 2 ValueErrors [Simple]
**File:** `game/strategy/generation/loaders/galaxy_layouts_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k layout`

- [x] Add imports: `from game.core.exceptions import ValidationException, ResourceException` and `from game.core.error_codes import ErrorCode`
- [x] Line 53: file must contain 'layouts' key → `ResourceException("Invalid galaxy layouts file format", code=ErrorCode.INVALID_FORMAT.value, context={"file_path": str(file_path), "missing_key": "layouts"})`
- [x] Line 75: unknown layout type → `ValidationException("Unknown layout type", code=ErrorCode.MISSING_ENTITY.value, context={"requested_type": layout_type, "available_types": available})`
- [x] Verify: `pytest tests/unit/strategy/generation/ -k layout`

**Notes:** Converted 2 ValueError — one to ResourceException (file format), one to ValidationException (missing entity).

### Task 2.4: Update Tests [Simple]
**Tests:** `pytest tests/unit/strategy/generation/`

- [x] `tests/unit/strategy/generation/density/test_layout_loader.py:42` — `pytest.raises(ValueError)` → `pytest.raises(ValidationException)`, add import
- [x] Check for any blueprint/astrophysics tests that assert ValueError and update — None found (tests use KeyError for invalid blueprint, not ValueError)
- [x] Verify: `pytest tests/unit/strategy/generation/ -v`

**Notes:**
- test_density_map.py tests are for density_map.py (Phase 3, Task 3.16), not the loaders
- Only test_layout_loader.py:42 needed updating for Phase 2

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `rg "raise ValueError" game/strategy/generation/loaders/` returns 0 matches
- [x] `pytest tests/unit/strategy/generation/` all pass (223 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
