# Phase 2: Restructure Ships Panel to Side-by-Side Layout

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-96 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Change `_create_ships_panel_content` from stacked layout (theme gallery on top, previews below) to side-by-side (theme list on left, preview grid on right).

---

## Tasks

### Task 2.1: Rewrite `_create_ships_panel_content` layout [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/ --testmon` + visual test

- [x] Keep title creation at top (lines 339-345), unchanged
- [x] Define layout constants after title:
  ```python
  THEME_LIST_WIDTH = 200
  CONTENT_GAP = 10
  content_y = y  # after title
  content_height = panel_height - content_y - 10
  ```
- [x] Update `RaceThemeGallery` creation (lines 349-357) to pass new position and `height`:
  ```python
  self._theme_gallery = RaceThemeGallery(
      panel=panel,
      manager=self.ui_manager,
      race_config=self.race_config,
      x=10,
      y=content_y,
      width=THEME_LIST_WIDTH,
      height=content_height,
      on_select_callback=self._on_theme_selected
  )
  ```
- [x] Remove old `theme_gallery_height = 200` estimation (line 361)
- [x] Remove old `y += theme_gallery_height + 10` (line 362)
- [x] Create ship preview scroll container to the right:
  ```python
  preview_x = 10 + THEME_LIST_WIDTH + CONTENT_GAP
  preview_width = panel_width - THEME_LIST_WIDTH - CONTENT_GAP
  self.ship_preview_scroll = pygame_gui.elements.UIScrollingContainer(
      relative_rect=pygame.Rect(preview_x, content_y, preview_width, content_height),
      manager=self.ui_manager,
      container=panel,
      allow_scroll_x=False,
      allow_scroll_y=True
  )
  ```
- [x] Remove `self.ship_preview_container = self.ship_preview_scroll` alias (line 375) - unused

**Notes:** Removed alias and old variables. Layout now side-by-side with theme list on left (200px) and preview area on right.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ --testmon` passes
- [x] Visual test: theme list appears on left, ship previews on right (user verification)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
