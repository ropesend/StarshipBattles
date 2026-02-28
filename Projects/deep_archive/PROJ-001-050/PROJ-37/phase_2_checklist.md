# Phase 2: Manifest Extension

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-37 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add star color mappings to asset_manifest.json and create lookup method in AssetManager

---

## Tasks

### Task 2.1: Add star_colors section to manifest [Simple]
**File:** `assets/asset_manifest.json`
**Tests:** Verify JSON is valid with `python -c "import json; json.load(open('assets/asset_manifest.json'))"`

Add the star color threshold configuration to the manifest file.

- [x] Open `assets/asset_manifest.json`
- [x] Add `"star_colors"` section after `"warp_points"` section (before closing brace)
- [x] Add color rules with RGB thresholds
- [x] Verify JSON is valid (no trailing commas, proper structure)
- [x] Run JSON validation: `python -c "import json; json.load(open('assets/asset_manifest.json'))"`

**Notes:**
- Yellow is default (empty rule matches everything else)
- Simplified rules to match original logic (r_min=200 for red, g_max=100 for red, etc.)

---

### Task 2.2: Add get_star_color_key method to AssetManager [Medium]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/unit/core/test_asset_manager.py -v`

Add a method to look up star color from RGB values using manifest configuration.

- [x] Open `game/assets/asset_manager.py`
- [x] Add `get_star_color_key(self, rgb: tuple) -> str` method after `get_random_from_group` (~line 140)
- [x] Method uses thresholds from manifest's 'star_colors' section
- [x] Returns 'yellow' as default if no rules match
- [x] Run existing tests to verify no regressions: `pytest tests/unit/core/test_asset_manager.py -v`

**Notes:** The threshold logic uses `<=` and `>=` to match the original code's `>` and `<` behavior

---

### Task 2.3: Add unit tests for get_star_color_key [Simple]
**File:** `tests/unit/core/test_asset_manager.py`
**Tests:** `pytest tests/unit/core/test_asset_manager.py::TestGetStarColorKey -v`

Add tests for the new method.

- [x] Open `tests/unit/core/test_asset_manager.py`
- [x] Add `TestGetStarColorKey` class with 8 tests covering:
  - Red, blue, white, orange star detection
  - Yellow default behavior
  - Empty manifest graceful fallback
  - Missing star_colors section handling
  - Threshold boundary tests
- [x] Run new tests: `pytest tests/unit/core/test_asset_manager.py -v` (24 tests passing)

**Notes:** Tests written FIRST following Strict TDD - all passed after implementation

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `assets/asset_manifest.json` has valid `star_colors` section
- [x] `game/assets/asset_manager.py` has `get_star_color_key()` method
- [x] Run `pytest tests/unit/core/test_asset_manager.py -v` - all 24 pass
- [x] Run `pytest tests/ --testmon` - 31 affected tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
