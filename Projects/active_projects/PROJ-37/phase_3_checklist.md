# Phase 3: Extend RaceAssetLoader

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-37 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add empire-specific asset loading methods to RaceAssetLoader

---

## Tasks

### Task 3.1: Add load_empire_race_assets method [Medium]
**File:** `game/ui/screens/race_asset_loader.py`
**Tests:** `pytest tests/unit/ui/test_race_asset_loader.py -v`

Add method to load race flags (rectangle, shield) for empire display.

- [ ] Open `game/ui/screens/race_asset_loader.py`
- [ ] Add import at top if needed: `from typing import Dict, Optional`
- [ ] Add new method after existing methods:
  ```python
  def load_empire_race_assets(self, flag_id: str) -> Dict[str, pygame.Surface]:
      """
      Load race flag assets for empire display in strategy view.

      Args:
          flag_id: The race flag identifier (e.g., 'flag_2fl0bh')

      Returns:
          Dict with keys 'colony' (rectangle flag) and 'fleet_flag' (shield flag).
          Returns placeholders for missing shapes.
      """
      result = {}

      if not flag_id:
          return result

      # Load full flags using existing method
      shapes = self.load_flag_full(flag_id)

      # shapes[0] = rectangle, shapes[1] = shield, shapes[2] = triangle
      if len(shapes) >= 1 and shapes[0]:
          result['colony'] = shapes[0]
      if len(shapes) >= 2 and shapes[1]:
          result['fleet_flag'] = shapes[1]

      return result
  ```
- [ ] Verify method works: Add a quick test or verify via manual testing
- [ ] Run existing tests to check for regressions: `pytest tests/unit/ui/test_race_asset_loader.py -v`

**Notes:** Reuses existing `load_flag_full()` which already has resolution hierarchy logic

---

### Task 3.2: Add load_empire_theme_assets method [Medium]
**File:** `game/ui/screens/race_asset_loader.py`
**Tests:** `pytest tests/unit/ui/test_race_asset_loader.py -v`

Add method to load theme assets (colony flag, fleet icon) for empire display.

- [ ] Add import at top: `from game.assets.asset_manager import get_asset_manager`
- [ ] Add new method:
  ```python
  def load_empire_theme_assets(self, theme_id: str, asset_base: str) -> Dict[str, pygame.Surface]:
      """
      Load theme-based assets for empire display in strategy view.

      Args:
          theme_id: The empire theme identifier (e.g., 'Federation', 'Atlantians')
          asset_base: Base path for ship themes (from GameConfig.asset_base_path)

      Returns:
          Dict with keys 'colony' (Colony_Flag.jpg) and 'fleet' (Battlecruiser.png).
          Returns empty dict if theme directory doesn't exist.
      """
      import os
      result = {}

      if not theme_id or not asset_base:
          return result

      theme_path = os.path.join(asset_base, theme_id)
      if not os.path.exists(theme_path):
          log_warning(f"Theme directory not found: {theme_path}")
          return result

      am = get_asset_manager()

      # Load colony flag
      colony_path = os.path.join(theme_path, "Flags", "Colony_Flag.jpg")
      if os.path.exists(colony_path):
          result['colony'] = am.load_external_image(colony_path)

      # Load fleet icon (Battlecruiser skin)
      fleet_path = os.path.join(theme_path, "Skins", "Battlecruiser.png")
      if os.path.exists(fleet_path):
          result['fleet'] = am.load_external_image(fleet_path)

      return result
  ```
- [ ] Add `log_warning` import if needed: `from game.core.logger import log_warning`
- [ ] Run existing tests: `pytest tests/unit/ui/test_race_asset_loader.py -v`

**Notes:** Uses AssetManager.load_external_image for caching benefits

---

### Task 3.3: Add load_all_empire_assets method [Simple]
**File:** `game/ui/screens/race_asset_loader.py`
**Tests:** `pytest tests/unit/ui/test_race_asset_loader.py -v`

Add combined method that loads all empire assets with proper precedence.

- [ ] Add new method:
  ```python
  def load_all_empire_assets(self, empire, asset_base: str) -> Dict[str, pygame.Surface]:
      """
      Load all visual assets for an empire (flags and fleet icon).

      Race assets take precedence over theme assets for 'colony' key.

      Args:
          empire: Empire object with flag_id and empire_theme_id attributes
          asset_base: Base path for ship themes

      Returns:
          Dict with keys 'colony', 'fleet', and optionally 'fleet_flag'.
      """
      result = {}

      # Load theme assets first (lower priority)
      if hasattr(empire, 'empire_theme_id') and empire.empire_theme_id:
          theme_assets = self.load_empire_theme_assets(empire.empire_theme_id, asset_base)
          result.update(theme_assets)

      # Load race assets second (higher priority - overwrites theme 'colony')
      if hasattr(empire, 'flag_id') and empire.flag_id:
          race_assets = self.load_empire_race_assets(empire.flag_id)
          result.update(race_assets)

      return result
  ```
- [ ] Run all tests: `pytest tests/unit/ui/test_race_asset_loader.py -v`

**Notes:** Order matters - race assets loaded second to overwrite theme's 'colony' key

---

### Task 3.4: Add unit tests for new methods [Medium]
**File:** `tests/unit/ui/test_race_asset_loader.py`
**Tests:** `pytest tests/unit/ui/test_race_asset_loader.py -v`

Add tests for the new empire asset loading methods.

- [ ] Open `tests/unit/ui/test_race_asset_loader.py`
- [ ] Add new test class `TestEmpireAssetLoading`:
  ```python
  class TestEmpireAssetLoading:
      """Tests for empire asset loading methods."""

      def test_load_empire_race_assets_returns_dict(self):
          """Test that method returns a dict."""
          loader = RaceAssetLoader()
          result = loader.load_empire_race_assets("nonexistent_flag")
          assert isinstance(result, dict)

      def test_load_empire_race_assets_empty_flag_id(self):
          """Test empty flag_id returns empty dict."""
          loader = RaceAssetLoader()
          result = loader.load_empire_race_assets("")
          assert result == {}

      def test_load_empire_theme_assets_returns_dict(self):
          """Test that method returns a dict."""
          loader = RaceAssetLoader()
          result = loader.load_empire_theme_assets("Federation", "/nonexistent/path")
          assert isinstance(result, dict)

      def test_load_all_empire_assets_race_precedence(self):
          """Test that race assets override theme assets for 'colony'."""
          # This test requires mocking - implement based on existing patterns
          pass
  ```
- [ ] Run new tests: `pytest tests/unit/ui/test_race_asset_loader.py -v`

**Notes:** Some tests may need filesystem mocking - follow existing test patterns

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `game/ui/screens/race_asset_loader.py` has 3 new methods:
  - `load_empire_race_assets()`
  - `load_empire_theme_assets()`
  - `load_all_empire_assets()`
- [ ] Run `pytest tests/unit/ui/test_race_asset_loader.py -v` - all pass
- [ ] Run `pytest tests/` - full suite still passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
