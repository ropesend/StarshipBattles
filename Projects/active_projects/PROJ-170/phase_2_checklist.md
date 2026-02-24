# Phase 2: Strategy Loaders Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-170 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate all 24 ValueErrors in strategy generation loaders. No external callers — safest batch.
**Estimated Effort:** 2 hours

---

## Tasks

### Task 2.1: system_blueprints_loader.py — 15 ValueErrors [Simple]
**File:** `game/strategy/generation/loaders/system_blueprints_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k blueprint`

- [ ] Add imports: `from game.core.exceptions import ValidationException` and `from game.core.error_codes import ErrorCode`
- [ ] Line 94: `raise ValueError("No blueprints with positive weight found")` → `raise ValidationException("No blueprints with positive weight found", code=ErrorCode.VALIDATION_FAILED.value, context={"reason": "no_positive_weights"})`
- [ ] Line 118: `raise ValueError("Blueprints data must be a dict")` → `raise ValidationException("Blueprints data must be a dict", code=ErrorCode.SCHEMA_VALIDATION_ERROR.value, context={"expected_type": "dict", "actual_type": type(data).__name__})`
- [ ] Line 121: `raise ValueError("Missing 'blueprints' key")` → `raise ValidationException("Missing 'blueprints' key", code=ErrorCode.SCHEMA_VALIDATION_ERROR.value, context={"missing_key": "blueprints"})`
- [ ] Line 125: `raise ValueError("'blueprints' must be a dict")` → `raise ValidationException("'blueprints' must be a dict", code=ErrorCode.SCHEMA_VALIDATION_ERROR.value, context={"key": "blueprints", "expected_type": "dict"})`
- [ ] Line 143: `raise ValueError(f"Blueprint '{name}' missing 'star_count'")` → `raise ValidationException(f"Blueprint '{name}' missing required field", code=ErrorCode.SCHEMA_VALIDATION_ERROR.value, context={"blueprint": name, "missing_field": "star_count"})`
- [ ] Line 145: similar for 'planet_count' → same pattern
- [ ] Line 147: similar for 'weight' → same pattern
- [ ] Line 153: star_count range → `code=ErrorCode.OUT_OF_RANGE.value`
- [ ] Line 157: star_count range invalid → `code=ErrorCode.OUT_OF_RANGE.value`
- [ ] Line 159: star_count missing min → `code=ErrorCode.SCHEMA_VALIDATION_ERROR.value`
- [ ] Line 161: star_count type → `code=ErrorCode.SCHEMA_VALIDATION_ERROR.value`
- [ ] Line 166: planet_count must be dict → `code=ErrorCode.SCHEMA_VALIDATION_ERROR.value`
- [ ] Line 168: planet_count missing min/max → `code=ErrorCode.SCHEMA_VALIDATION_ERROR.value`
- [ ] Line 170: planet_count range invalid → `code=ErrorCode.OUT_OF_RANGE.value`
- [ ] Line 174: weight must be positive → `code=ErrorCode.OUT_OF_RANGE.value`
- [ ] Verify: `pytest tests/unit/strategy/generation/ -k blueprint`

**Notes:**

### Task 2.2: astrophysics_loader.py — 7 ValueErrors [Simple]
**File:** `game/strategy/generation/loaders/astrophysics_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k astrophysics`

- [ ] Add imports: `from game.core.exceptions import ValidationException` and `from game.core.error_codes import ErrorCode`
- [ ] Line 119: missing required section → `ValidationException` + `SCHEMA_VALIDATION_ERROR`
- [ ] Line 126: missing mass distribution → `ValidationException` + `SCHEMA_VALIDATION_ERROR`
- [ ] Line 133: missing orbit zone → `ValidationException` + `SCHEMA_VALIDATION_ERROR`
- [ ] Line 138: habitable_zone missing factors → `ValidationException` + `SCHEMA_VALIDATION_ERROR`
- [ ] Line 143: atmosphere_retention missing thresholds → `ValidationException` + `SCHEMA_VALIDATION_ERROR`
- [ ] Line 148: classification missing mass_thresholds → `ValidationException` + `SCHEMA_VALIDATION_ERROR`
- [ ] Line 150: classification missing temperature_thresholds → `ValidationException` + `SCHEMA_VALIDATION_ERROR`
- [ ] Verify: `pytest tests/unit/strategy/generation/ -k astrophysics`

**Notes:**

### Task 2.3: galaxy_layouts_loader.py — 2 ValueErrors [Simple]
**File:** `game/strategy/generation/loaders/galaxy_layouts_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k layout`

- [ ] Add imports: `from game.core.exceptions import ValidationException, ResourceException` and `from game.core.error_codes import ErrorCode`
- [ ] Line 53: file must contain 'layouts' key → `ResourceException("Invalid galaxy layouts file format", code=ErrorCode.INVALID_FORMAT.value, context={"file_path": str(file_path), "missing_key": "layouts"})`
- [ ] Line 75: unknown layout type → `ValidationException("Unknown layout type", code=ErrorCode.MISSING_ENTITY.value, context={"requested_type": layout_type, "available_types": available})`
- [ ] Verify: `pytest tests/unit/strategy/generation/ -k layout`

**Notes:**

### Task 2.4: Update Tests [Simple]
**Tests:** `pytest tests/unit/strategy/generation/`

- [ ] `tests/unit/strategy/generation/density/test_density_map.py:24` — `pytest.raises(ValueError)` → `pytest.raises(ValidationException)`, add import
- [ ] `tests/unit/strategy/generation/density/test_density_map.py:173` — `pytest.raises(ValueError)` → `pytest.raises(ValidationException)`
- [ ] `tests/unit/strategy/generation/density/test_density_map.py:179` — `pytest.raises(ValueError)` → `pytest.raises(ValidationException)`
- [ ] `tests/unit/strategy/generation/density/test_density_map.py:189` — `pytest.raises(ValueError)` → `pytest.raises(ValidationException)`
- [ ] `tests/unit/strategy/generation/density/test_layout_loader.py:42` — `pytest.raises(ValueError)` → `pytest.raises(ValidationException)`
- [ ] Check for any blueprint/astrophysics tests that assert ValueError and update
- [ ] Verify: `pytest tests/unit/strategy/generation/ -v`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `rg "raise ValueError" game/strategy/generation/loaders/` returns 0 matches
- [ ] `pytest tests/unit/strategy/generation/` all pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
