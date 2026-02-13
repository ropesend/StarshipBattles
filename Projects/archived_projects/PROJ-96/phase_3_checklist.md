# Phase 3: Redesign Ship Preview Grid

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-96 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Rewrite `_refresh_ship_preview` for 3-column layout, 9 ships, smart top-down scaling, centered labels, tighter spacing.

---

## Tasks

### Task 3.1: Expand to 9 ship classes and 3 columns [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/ --testmon` + visual test

- [x] Replace `ship_classes` list with 9 ship classes:
  Fighter (Medium), Satellite (Medium), Escort, Frigate, Cruiser, Heavy Cruiser, Battleship, Dreadnought, Superdreadnought
- [x] Define column count and sizes: num_cols=3, portrait_size=160, image_gap=5
- [x] Update scroll height calculation for 3-column grid
- [x] Update column/row iteration with num_cols and row_spacing
- [x] Verify: 3 columns visible, 9 ships total

**Notes:** Layout constants defined: portrait_size=160, image_gap=5, row_spacing=10

### Task 3.2: Center labels above image pairs [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** Visual test

- [x] Update label creation with col_width-10 and height 25
- [x] Verify: Labels centered above both images in each cell

**Notes:** UILabel centers text by default

### Task 3.3: Smart top-down image scaling using visible bounding rect [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** Visual test

- [x] Replace naive scaling with metrics-based scaling using get_image_metrics()
- [x] Scale so visible portion fits portrait_size, capped at 3.0x
- [x] Crop to visible area using scaled metrics
- [x] Verify: Top-down images appear at similar height to portraits

**Notes:** `get_image_metrics()` returns pygame.Rect with visible pixels bounding box

### Task 3.4: Tighter image layout within each cell [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** Visual test

- [x] Calculate centered positions for the image pair
- [x] Position top-down image at pair_x with actual dimensions
- [x] Position portrait image at pair_x + topdown_w + image_gap
- [x] Verify: Images are close together and centered under the label

**Notes:** Images centered based on actual rendered widths

### Task 3.5: Use `ShipThemeManager.get_portrait_image()` and delete `_load_ship_portrait` [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/ --testmon`

- [x] Replace `self._load_ship_portrait()` with `theme_manager.get_portrait_image()`
- [x] Scale the returned surface to portrait_size
- [x] Delete entire `_load_ship_portrait` method (37 lines removed)
- [x] Verify: Portraits still load and display correctly

**Notes:** Deleted duplicate code, now using centralized ShipThemeManager API

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes (7593 passed)
- [x] Visual test: 3x3 grid, labels centered, top-down images appropriately sized
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
