# Phase 1: Test Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-37 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add unit tests for existing behavior BEFORE any changes (safety net for refactoring)

---

## Tasks

### Task 1.1: Add star color mapping tests [Medium]
**File:** `tests/unit/ui/test_star_color_mapping.py` (NEW)
**Tests:** `pytest tests/unit/ui/test_star_color_mapping.py -v`

Create tests that verify the CURRENT behavior of star color mapping in `strategy_scene.py` lines 497-508.

- [x] Create new test file `tests/unit/ui/test_star_color_mapping.py`
- [x] Add `TestStarColorMapping` class with setup to mock AssetManager
- [x] `test_red_star_maps_correctly`: RGB (220, 50, 50) → returns 'red' asset
- [x] `test_blue_star_maps_correctly`: RGB (50, 50, 220) → returns 'blue' asset
- [x] `test_white_star_maps_correctly`: RGB (220, 220, 220) → returns 'white' asset
- [x] `test_orange_star_maps_correctly`: RGB (220, 160, 50) → returns 'orange' asset
- [x] `test_yellow_default_for_unknown`: RGB (150, 150, 50) → returns 'yellow' (default)
- [x] `test_threshold_boundary_red`: RGB (200, 100, 100) → test edge case at threshold
- [x] `test_threshold_boundary_blue`: RGB (100, 100, 200) → test edge case at threshold
- [x] Verify all tests pass: `pytest tests/unit/ui/test_star_color_mapping.py -v`

**Reference Code (current logic to test):**
```python
# strategy_scene.py lines 497-508
if is_star(obj):
    color = obj.color
    asset_key = 'yellow'  # default
    if color[0] > 200 and color[1] < 100:
        asset_key = 'red'
    elif color[2] > 200 and color[0] < 100:
        asset_key = 'blue'
    elif color[0] > 200 and color[1] > 200 and color[2] > 200:
        asset_key = 'white'
    elif color[0] > 200 and color[1] > 150:
        asset_key = 'orange'
    return am.get_image('stars', asset_key)
```

**Notes:** These tests validate the CURRENT behavior. They will need updating in Phase 5 after manifest migration.

---

### Task 1.2: Add empire asset loading tests [Medium]
**File:** `tests/unit/ui/test_empire_asset_loading.py` (NEW)
**Tests:** `pytest tests/unit/ui/test_empire_asset_loading.py -v`

Create tests that verify empire asset loading behavior in `strategy_scene.py` `_load_assets()`.

- [x] Create new test file `tests/unit/ui/test_empire_asset_loading.py`
- [x] Add `TestEmpireAssetLoading` class
- [x] Add fixtures for mock Empire objects with flag_id and empire_theme_id
- [x] `test_load_race_flag_rectangle`: When flag_id exists → 'colony' key has Surface
- [x] `test_load_race_flag_shield`: When flag_id exists → 'fleet_flag' key has Surface
- [x] `test_load_fleet_icon_from_theme`: When empire_theme_id exists → 'fleet' key has Surface
- [x] `test_race_flag_precedence_over_theme`: Both exist → 'colony' uses race flag (not theme)
- [x] `test_fallback_to_theme_when_race_missing`: No race flag → 'colony' uses theme flag
- [x] `test_missing_assets_return_placeholder`: Nothing exists → returns placeholder surfaces
- [x] Verify all tests pass: `pytest tests/unit/ui/test_empire_asset_loading.py -v`

**Notes:** Use mocking for filesystem operations (patch `os.path.exists`, `pygame.image.load`)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/ui/test_star_color_mapping.py tests/unit/ui/test_empire_asset_loading.py -v` - all pass (25 tests)
- [x] Run `pytest tests/` - full suite still passes (4973 passed, no regressions)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
