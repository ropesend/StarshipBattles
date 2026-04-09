# Phase 3: Classification + Resource Config Additions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-236 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add chthonian stripping thresholds to ClassificationConfig, move _RAMP_C to ResourceGenerationConfig

---

## Tasks

### Task 3.1: Add chthonian stripping to ClassificationConfig [Simple]
**File:** `game/strategy/data/classification_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_classification_config.py tests/unit/strategy/data/test_planet_gen.py::TestPlanetTypeDetermination -v`

- [x] Add `DEFAULT_CHTHONIAN` dict to ClassificationConfig:
  ```python
  DEFAULT_CHTHONIAN = {
      "certain_temp": 600,       # planet_gen.py:466 — temp above which stripping is certain
      "strip_start_temp": 300,   # planet_gen.py:468 — temp above which stripping begins
      "max_probability": 0.30,   # planet_gen.py:470 — maximum stripping probability
      "strip_divisor": 4000,     # planet_gen.py:470 — divisor for probability formula
  }
  ```
- [x] Update `_load_from_json()`: add `chthonian = classification.get("chthonian_stripping", {})` and load 4 values
- [x] Update `_use_defaults()`: add 4 assignments from `DEFAULT_CHTHONIAN`
- [x] Add `"chthonian_stripping"` subsection to `data/astrophysics.json` inside `"classification"`:
  ```json
  "chthonian_stripping": {
      "certain_temp": 600,
      "strip_start_temp": 300,
      "max_probability": 0.30,
      "strip_divisor": 4000
  }
  ```
- [x] Add tests for new config values in `test_classification_config.py`
- [x] Wire `planet_gen.py:_determine_type` (lines 466-470):
  - `temp > 600` → `temp > cfg.chthonian_certain_temp` (line 466)
  - `temp > 300` → `temp > cfg.chthonian_strip_start_temp` (line 468)
  - `min(0.30, ...)` → `min(cfg.chthonian_max_probability, ...)` (line 470)
  - `/ 4000` → `/ cfg.chthonian_strip_divisor` (line 470)
- [x] Run classification tests — all 14 parametrized cases pass
**Notes:** The `cfg` variable already exists in `_determine_type` from ClassificationConfig loading at line 459.

---

### Task 3.2: Move _RAMP_C to ResourceGenerationConfig [Simple]
**File:** `game/strategy/data/resource_generation_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_resource_generation_config.py tests/unit/strategy/data/test_planet_gen.py::TestResourceGeneration -v`

- [x] Add `"ramp_c": 24.8` to `DEFAULT_QUANTITY` dict (after `"minimum_floor"`)
- [x] Update `_load_from_json()`: add `self.ramp_c = qty.get("ramp_c", self.DEFAULT_QUANTITY["ramp_c"])`
- [x] Update `_use_defaults()`: add `self.ramp_c = self.DEFAULT_QUANTITY["ramp_c"]`
- [x] Add `"ramp_c": 24.8` to `data/astrophysics.json` under `"resource_generation"."quantity"`
- [x] Add test in `test_resource_generation_config.py`: `assert cfg.ramp_c == 24.8`
- [x] Wire `planet_gen.py:_generate_resources` (line 558):
  - Remove `_RAMP_C = 24.8` local variable
  - Replace `_RAMP_C` usage with `cfg.ramp_c` (lines 558-559, 564)
- [x] Run resource generation tests — all pass
**Notes:** `cfg` already exists from `get_resource_generation_config()` call at line 548.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/data/test_classification_config.py tests/unit/strategy/data/test_resource_generation_config.py tests/unit/strategy/data/test_planet_gen.py tests/unit/strategy/data/test_planet_classification_logic.py -v` — all pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
