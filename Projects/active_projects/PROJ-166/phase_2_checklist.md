# Phase 2: Refactor RaceThemeGallery to Extend BaseGallery

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-166 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Rewrite RaceThemeGallery to inherit from BaseGallery, implementing the 9 abstract methods and overriding `_create_content` and `_populate_gallery` for its unique vertical-list layout.

---

## Tasks

### Task 2.1: Change class declaration and imports [Simple]
**File:** `game/ui/panels/race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py -v` (will fail until Task 2.3 — that's expected)

- [x] Add import (after existing imports, ~line 16):
  ```python
  from game.ui.panels.base_gallery import BaseGallery
  from game.ui.screens.race_asset_loader import RaceAssetLoader
  ```
- [x] Change class declaration (line 22) from:
  ```python
  class RaceThemeGallery:
  ```
  To:
  ```python
  class RaceThemeGallery(BaseGallery):
  ```
- [x] Update module docstring to note PROJ-166 refactoring

**Notes:** Complete. Also removed log_debug import (now inherited from BaseGallery).

### Task 2.2: Rewrite __init__ to call super().__init__() [Medium]
**File:** `game/ui/panels/race_theme_gallery.py`

- [x] Rewrite `__init__` (lines 32-68). New version:
  ```python
  def __init__(
      self,
      panel: pygame_gui.elements.UIPanel,
      manager: pygame_gui.UIManager,
      race_config: 'RaceConfig',
      x: int,
      y: int,
      width: int,
      height: int,
      on_select_callback: Optional[Callable[[str], None]] = None,
      asset_loader: Optional[RaceAssetLoader] = None,
  ):
      # Theme-specific cache (dict of surfaces, not single surface)
      self._theme_cache: Optional[List[Tuple[str, Dict[str, pygame.Surface]]]] = None

      super().__init__(
          panel, manager, race_config, x, y, width, height,
          on_select_callback, asset_loader
      )
  ```
- [x] Remove old instance variable initialization that BaseGallery now handles:
  - `self.panel`, `self.ui_manager`, `self.race_config`, `self.on_select_callback` — handled by super
  - `self.theme_buttons` → replaced by `self.asset_buttons` from BaseGallery
  - `self.theme_scroll` → replaced by `self.scroll_container` from BaseGallery
  - `self.height` — no longer stored separately (was only used in __init__)

**Notes:** Complete. Also removed SHIP_SIZE constant (unused).

### Task 2.3: Implement abstract methods [Medium]
**File:** `game/ui/panels/race_theme_gallery.py`

- [x] Add all 9 abstract method implementations:
  ```python
  # --- BaseGallery abstract method implementations ---

  def _get_label_text(self) -> str:
      return "Select Ship Theme:"

  def _get_thumb_size(self) -> int:
      return 50  # Button height for list layout

  def _get_preview_size(self) -> int:
      return 0  # No preview panel

  def _get_object_id_prefix(self) -> str:
      return "theme"

  def _get_preview_panel_object_id(self) -> str:
      return "#theme_preview"

  def _get_current_selection(self) -> Optional[str]:
      return self.race_config.theme_id

  def _set_selection(self, asset_id: str) -> None:
      self.race_config.theme_id = asset_id

  def _update_preview(self, asset_id: str) -> None:
      pass  # No preview panel — ship preview handled by RaceSetupScreen callback
  ```

**Notes:** Complete.

### Task 2.4: Override _create_content for list layout [Medium]
**File:** `game/ui/panels/race_theme_gallery.py`

- [x] Override `_create_content` (replacing old lines 70-125). The theme gallery uses a **full-height scroll container** with no label or preview panel:
  ```python
  def _create_content(self, x: int, y: int, width: int, height: int):
      """Create theme gallery with vertical list layout (no label or preview)."""
      self.scroll_container = pygame_gui.elements.UIScrollingContainer(
          relative_rect=pygame.Rect(x, y, width, height),
          manager=self.ui_manager,
          container=self.panel,
          allow_scroll_x=False,
          allow_scroll_y=True,
      )

      self._populate_gallery(width)

      # Pre-select from config or default to first
      current = self._get_current_selection()
      if current:
          self.on_asset_selected(current)
      elif self.asset_buttons:
          self.on_asset_selected(self.asset_buttons[0][1])
  ```
- [x] Note: This skips the label and preview panel that BaseGallery's default `_create_content` creates — that's the whole point of the override

**Notes:** Complete.

### Task 2.5: Override _populate_gallery for vertical list [Medium]
**File:** `game/ui/panels/race_theme_gallery.py`

- [x] Override `_populate_gallery` (replacing old inline button creation). Uses vertical list buttons with ship preview thumbnails instead of image-grid:
  ```python
  def _populate_gallery(self, width: int):
      """Populate gallery with vertical list of theme buttons."""
      themes = self._discover_assets()
      btn_height = 50
      local_y = 0

      for theme_id, ship_surfs in themes:
          btn = pygame_gui.elements.UIButton(
              relative_rect=pygame.Rect(0, local_y, width - 20, btn_height),
              text=theme_id,
              manager=self.ui_manager,
              container=self.scroll_container,
              object_id=f"#theme_{self._sanitize_object_id(theme_id)}",
          )
          btn.asset_id = theme_id

          # Add small ship preview images on the right
          if "Escort" in ship_surfs:
              pygame_gui.elements.UIImage(
                  relative_rect=pygame.Rect(width - 90, local_y + 5, 30, 40),
                  image_surface=ship_surfs["Escort"],
                  manager=self.ui_manager,
                  container=self.scroll_container,
              )
          if "Battleship" in ship_surfs:
              pygame_gui.elements.UIImage(
                  relative_rect=pygame.Rect(width - 55, local_y + 5, 30, 40),
                  image_surface=ship_surfs["Battleship"],
                  manager=self.ui_manager,
                  container=self.scroll_container,
              )

          self.asset_buttons.append((btn, theme_id))
          local_y += btn_height + 5

      # Set scrollable area dimensions
      total_height = local_y if local_y > 0 else 1
      self.scroll_container.set_scrollable_area_dimensions(
          (width - 20, total_height)
      )
  ```

**Notes:** Complete.

### Task 2.6: Refactor _discover_themes → _discover_assets [Simple]
**File:** `game/ui/panels/race_theme_gallery.py`

- [x] Rename `_discover_themes` (line 127) to `_discover_assets`
- [x] Change cache reference from `self._theme_cache` to `self._theme_cache` (keep the cache name since it stores theme-specific Dict data, not a simple surface)
- [x] Existing logic stays the same — ShipThemeManager discovery is correct
- [x] Return type stays `List[Tuple[str, Dict[str, pygame.Surface]]]` — `_populate_gallery` is overridden so it handles this format directly
- [x] Note: BaseGallery's `_discover_assets` declares return `List[Tuple[str, pygame.Surface]]` — our override returns a slightly different type, but since `_populate_gallery` is also overridden, the type difference never causes issues. Add a type: ignore comment if needed.

**Notes:** Complete. Added `# type: ignore[override]` comment.

### Task 2.7: Delete duplicated methods [Simple]
**File:** `game/ui/panels/race_theme_gallery.py`

- [x] Delete `_sanitize_object_id` method (lines 157-159) — inherited from BaseGallery
- [x] Delete `on_theme_selected` method (lines 161-180) — replaced by `on_asset_selected` from BaseGallery
- [x] Delete `set_from_config` method (lines 182-185) — inherited from BaseGallery
- [x] Delete `handle_button_click` method (lines 187-201) — inherited from BaseGallery
- [x] Remove unused imports: `from game.core.logger import log_debug` (if no longer used directly — BaseGallery handles the logging in on_asset_selected)
- [x] Verify: No references remain to `theme_buttons`, `theme_scroll`, `on_theme_selected`

**Notes:** Complete. All duplicate methods removed.

### Task 2.8: Verify no caller changes needed [Simple]
**File:** `game/ui/screens/race_setup_screen.py`

- [x] Verify line 354-363: Constructor call still works — `on_select_callback` is positional, `asset_loader` not passed (optional)
- [x] Verify line 822-824: `set_from_config()` — method exists in BaseGallery ✓
- [x] Verify line 901-903: `handle_button_click()` — method exists in BaseGallery ✓
- [x] Grep for `on_theme_selected` in race_setup_screen.py — should NOT be called directly (only via callback)
- [x] Grep for `theme_buttons` in race_setup_screen.py — should NOT be accessed directly
- [x] Grep for `theme_scroll` in race_setup_screen.py — should NOT be accessed directly
- [x] **No changes to race_setup_screen.py** — confirm this

**Notes:** Complete. race_setup_screen.py unchanged — uses callback pattern, not direct method calls.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] RaceThemeGallery extends BaseGallery
- [x] No duplicate methods remain (_sanitize_object_id, handle_button_click, set_from_config)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
