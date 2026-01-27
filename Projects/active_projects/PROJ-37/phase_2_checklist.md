# Phase 2: Manifest Extension

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-37 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add star color mappings to asset_manifest.json and create lookup method in AssetManager

---

## Tasks

### Task 2.1: Add star_colors section to manifest [Simple]
**File:** `assets/asset_manifest.json`
**Tests:** Verify JSON is valid with `python -c "import json; json.load(open('assets/asset_manifest.json'))"`

Add the star color threshold configuration to the manifest file.

- [ ] Open `assets/asset_manifest.json`
- [ ] Add `"star_colors"` section after `"warp_points"` section (before closing brace)
- [ ] Add color rules with RGB thresholds:
  ```json
  "star_colors": {
    "red": {"r_min": 200, "g_max": 100, "b_max": 150},
    "blue": {"r_max": 100, "g_max": 100, "b_min": 200},
    "white": {"r_min": 200, "g_min": 200, "b_min": 200},
    "orange": {"r_min": 200, "g_min": 150, "b_max": 150},
    "neutron": {"r_min": 150, "g_min": 150, "b_min": 200},
    "yellow": {}
  }
  ```
- [ ] Verify JSON is valid (no trailing commas, proper structure)
- [ ] Run JSON validation: `python -c "import json; json.load(open('assets/asset_manifest.json'))"`

**Notes:**
- Yellow is default (empty rule matches everything else)
- Order matters: more specific rules should be checked first in code
- `neutron` is new - covers bluish-white stars

---

### Task 2.2: Add get_star_color_key method to AssetManager [Medium]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/unit/core/test_asset_manager.py -v`

Add a method to look up star color from RGB values using manifest configuration.

- [ ] Open `game/assets/asset_manager.py`
- [ ] Add method after `get_random_from_group` (~line 130):
  ```python
  def get_star_color_key(self, rgb: tuple) -> str:
      """
      Determine the star asset key based on RGB color values.

      Uses thresholds defined in manifest's 'star_colors' section.
      Returns 'yellow' as default if no rules match.

      Args:
          rgb: Tuple of (r, g, b) color values (0-255)

      Returns:
          Star asset key string (e.g., 'red', 'blue', 'yellow')
      """
      star_colors = self.manifest.get('star_colors', {})
      r, g, b = rgb[0], rgb[1], rgb[2]

      for color_name, thresholds in star_colors.items():
          if not thresholds:  # Empty dict = default (yellow)
              continue

          matches = True
          if 'r_min' in thresholds and r <= thresholds['r_min']:
              matches = False
          if 'r_max' in thresholds and r >= thresholds['r_max']:
              matches = False
          if 'g_min' in thresholds and g <= thresholds['g_min']:
              matches = False
          if 'g_max' in thresholds and g >= thresholds['g_max']:
              matches = False
          if 'b_min' in thresholds and b <= thresholds['b_min']:
              matches = False
          if 'b_max' in thresholds and b >= thresholds['b_max']:
              matches = False

          if matches:
              return color_name

      return 'yellow'  # default
  ```
- [ ] Add type hint import if needed: `from typing import Tuple` (check if already imported)
- [ ] Run existing tests to verify no regressions: `pytest tests/unit/core/test_asset_manager.py -v`

**Notes:** The threshold logic uses `<=` and `>=` to match the original code's `>` and `<` behavior

---

### Task 2.3: Add unit tests for get_star_color_key [Simple]
**File:** `tests/unit/core/test_asset_manager.py`
**Tests:** `pytest tests/unit/core/test_asset_manager.py::TestAssetManager::test_get_star_color_key -v`

Add tests for the new method.

- [ ] Open `tests/unit/core/test_asset_manager.py`
- [ ] Add test method to `TestAssetManager` class:
  ```python
  def test_get_star_color_key_red(self):
      """Test red star detection."""
      am = get_asset_manager()
      am.manifest = {'star_colors': {'red': {'r_min': 200, 'g_max': 100}, 'yellow': {}}}
      assert am.get_star_color_key((220, 50, 50)) == 'red'

  def test_get_star_color_key_default_yellow(self):
      """Test yellow as default."""
      am = get_asset_manager()
      am.manifest = {'star_colors': {'red': {'r_min': 200, 'g_max': 100}, 'yellow': {}}}
      assert am.get_star_color_key((150, 150, 50)) == 'yellow'

  def test_get_star_color_key_no_manifest(self):
      """Test graceful fallback with empty manifest."""
      am = get_asset_manager()
      am.manifest = {}
      assert am.get_star_color_key((220, 50, 50)) == 'yellow'
  ```
- [ ] Run new tests: `pytest tests/unit/core/test_asset_manager.py -v`

**Notes:** Reset AssetManager between tests if needed

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `assets/asset_manifest.json` has valid `star_colors` section
- [ ] `game/assets/asset_manager.py` has `get_star_color_key()` method
- [ ] Run `pytest tests/unit/core/test_asset_manager.py -v` - all pass
- [ ] Run `pytest tests/` - full suite still passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
