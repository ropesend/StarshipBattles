# Phase 3: Redesign Ship Preview Grid

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-96 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rewrite `_refresh_ship_preview` for 3-column layout, 9 ships, smart top-down scaling, centered labels, tighter spacing.

---

## Tasks

### Task 3.1: Expand to 9 ship classes and 3 columns [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/ --testmon` + visual test

- [ ] Replace `ship_classes` list (lines 399-406) with:
  ```python
  ship_classes = [
      "Fighter (Medium)", "Satellite (Medium)", "Escort",
      "Frigate", "Cruiser", "Heavy Cruiser",
      "Battleship", "Dreadnought", "Superdreadnought",
  ]
  ```
- [ ] Define column count and sizes:
  ```python
  num_cols = 3
  portrait_size = 160  # or use self.SHIP_PREVIEW_SIZE
  image_gap = 5
  col_width = container_width // num_cols
  row_height = portrait_size + 35  # label(25) + gap(5) + image + bottom_pad(5)
  row_spacing = 10
  ```
- [ ] Update scroll height calculation:
  ```python
  total_rows = (len(ship_classes) + num_cols - 1) // num_cols
  scroll_height = 10 + total_rows * (row_height + row_spacing) + 20
  ```
- [ ] Update column/row iteration:
  ```python
  col = i % num_cols
  if col == 0 and i > 0:
      y += row_height + row_spacing
  x = 10 + col * col_width
  ```
- [ ] Verify: 3 columns visible, 9 ships total

**Notes:**

### Task 3.2: Center labels above image pairs [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** Visual test

- [ ] Update label creation (lines 433-438):
  ```python
  label = pygame_gui.elements.UILabel(
      relative_rect=pygame.Rect(x, y, col_width - 10, 25),
      text=ship_class,
      manager=self.ui_manager,
      container=container
  )
  ```
- [ ] Verify: Labels centered above both images in each cell

**Notes:** UILabel centers text by default

### Task 3.3: Smart top-down image scaling using visible bounding rect [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** Visual test

- [ ] Replace naive scaling (lines 446-449) with metrics-based scaling:
  ```python
  skin_surf = theme_manager.load_image(theme_id, ship_class)
  if skin_surf:
      img_width, img_height = skin_surf.get_size()
      metrics = theme_manager.get_image_metrics(theme_id, ship_class)

      if metrics and metrics.width > 0 and metrics.height > 0:
          # Scale so visible portion fits portrait_size
          scale_factor = portrait_size / max(metrics.width, metrics.height)
          scale_factor = min(scale_factor, 3.0)  # Cap to prevent blowup
      else:
          scale_factor = portrait_size / max(img_width, img_height)

      new_w = max(1, int(img_width * scale_factor))
      new_h = max(1, int(img_height * scale_factor))
      scaled_skin = pygame.transform.smoothscale(skin_surf, (new_w, new_h))

      # Crop to visible area
      if metrics:
          crop_x = max(0, int(metrics.x * scale_factor))
          crop_y = max(0, int(metrics.y * scale_factor))
          crop_w = min(int(metrics.width * scale_factor), new_w - crop_x)
          crop_h = min(int(metrics.height * scale_factor), new_h - crop_y)
          if crop_w > 0 and crop_h > 0:
              cropped = scaled_skin.subsurface(pygame.Rect(crop_x, crop_y, crop_w, crop_h))
              scaled_skin = cropped
  ```
- [ ] Verify: Top-down images appear at similar height to portraits

**Notes:** `get_image_metrics()` returns a `pygame.Rect` with (x, y, width, height) of visible pixels. Located at `ship_theme_manager.py:207`.

### Task 3.4: Tighter image layout within each cell [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** Visual test

- [ ] Calculate centered positions for the image pair:
  ```python
  # Total width of image pair
  topdown_w = scaled_skin.get_width() if skin_surf else 0
  pair_width = topdown_w + image_gap + portrait_size
  pair_x = x + (col_width - pair_width) // 2
  ```
- [ ] Position top-down image at `(pair_x, y + 30, topdown_w, scaled_skin.get_height())`
- [ ] Position portrait image at `(pair_x + topdown_w + image_gap, y + 30, portrait_size, portrait_size)`
- [ ] Verify: Images are close together and centered under the label

**Notes:**

### Task 3.5: Use `ShipThemeManager.get_portrait_image()` and delete `_load_ship_portrait` [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Replace `self._load_ship_portrait(theme_id, ship_class)` (line 461) with:
  ```python
  portrait_surf = theme_manager.get_portrait_image(theme_id, ship_class)
  ```
- [ ] Scale the returned surface to `portrait_size`:
  ```python
  if portrait_surf:
      p_w, p_h = portrait_surf.get_size()
      p_scale = min(portrait_size / p_w, portrait_size / p_h)
      scaled_portrait = pygame.transform.smoothscale(
          portrait_surf, (int(p_w * p_scale), int(p_h * p_scale))
      )
  ```
- [ ] Delete entire `_load_ship_portrait` method (lines 472-508)
- [ ] Verify: Portraits still load and display correctly

**Notes:** `ShipThemeManager.get_portrait_image()` is at `ship_theme_manager.py:259`. It has proper caching and thread safety.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Visual test: 3x3 grid, labels centered, top-down images appropriately sized
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
