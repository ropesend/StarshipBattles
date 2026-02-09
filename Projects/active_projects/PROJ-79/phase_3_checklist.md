# Phase 3: Queue Item Display + Column Headers + Resource Icons

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-79 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Show per-turn resource cost in queue items, add column headers with resource portrait icons, restructure queue item layout for column alignment.

---

## Tasks

### Task 3.1: Load resource portrait icons [Simple]
**File:** `game/ui/screens/build_queue_screen.py` (or new helper in `game/ui/panels/build_queue_portraits.py`)
**Tests:** Manual test - verify icons load

- [ ] Add resource icon loading method (can go in BuildQueueScreen or BuildQueuePortraitLoader):
  ```python
  def _load_resource_icons(self, icon_size: int = 20) -> Dict[str, pygame.Surface]:
      """Load resource portrait icons scaled to icon_size."""
      icons = {}
      resource_files = {
          "Metals": "resource_metals_portrait.png",
          "Organics": "resource_organics_portrait.png",
          "Vapors": "resource_vapors_portrait.png",
          "Radioactives": "resource_radioactives_portrait.png",
          "Exotics": "resource_exotics_portrait.png",
      }
      base_path = os.path.join("assets", "Images", "Resource Portraits")
      for resource, filename in resource_files.items():
          path = os.path.join(base_path, filename)
          try:
              img = pygame.image.load(path)
              icons[resource] = pygame.transform.smoothscale(img, (icon_size, icon_size))
          except (FileNotFoundError, pygame.error):
              # Create fallback colored square
              surf = pygame.Surface((icon_size, icon_size))
              surf.fill((128, 128, 128))
              icons[resource] = surf
      return icons
  ```
- [ ] Call `_load_resource_icons()` in `__init__` and store as `self.resource_icons`
- [ ] Verify: Icons load without error, fallback works if file missing

**Notes:**

### Task 3.2: Add column headers to build queue panel [Medium]
**File:** `game/ui/screens/build_queue_screen.py`, `_create_build_queue_panel()` (line 419)
**Tests:** Manual test - verify headers appear

- [ ] After the `"<b>Build Queue</b>"` header text box (line 443-448), add a header row:
  ```python
  # Column header row
  header_y = 45
  header_height = 25
  col_x = 10  # Start position

  # Item name column (wide)
  ui.UILabel(rect=Rect(col_x, header_y, 150, header_height), text="Item", ...)
  col_x += 155

  # Turns column
  ui.UILabel(rect=Rect(col_x, header_y, 40, header_height), text="Turns", ...)
  col_x += 45

  # Resource icon columns (one per resource)
  for resource in PLANET_RESOURCES:
      icon = self.resource_icons.get(resource)
      if icon:
          ui.UIImage(rect=Rect(col_x, header_y, 20, 20), image_surface=icon, ...)
      col_x += 30
  ```
- [ ] Shift `queue_scrollable` Y start from 45 to ~75 to accommodate header row
- [ ] Store column X positions for use in queue item layout: `self.queue_column_positions`
- [ ] Verify: Headers show Item, Turns, then 5 resource icons in a row

**Notes:**

### Task 3.3: Show per-turn resource cost per queue item [Medium]
**File:** `game/ui/screens/build_queue_screen.py`, `_refresh_queue_display()` (line 687)
**Tests:** Manual test - verify costs display under correct columns

- [ ] For each queue item with cost tracking, compute per-turn cost:
  ```python
  per_turn_cost = {}
  if total_cost and turns > 0:
      for res in PLANET_RESOURCES:
          amount = total_cost.get(res, 0)
          if amount > 0:
              per_turn_cost[res] = amount / turns  # or cost_per_tick[res] * 100
  ```
- [ ] Restructure queue item panel layout to align with column headers:
  - Portrait icon (left, 50x50)
  - Design name label aligned with "Item" column
  - Turns remaining label aligned with "Turns" column
  - Individual resource per-turn cost labels aligned under their respective resource icon columns
- [ ] Replace the current compact `"Cost: consumed/total"` format with columnar per-turn values
- [ ] Adjust `panel_height` to accommodate the layout (may need 80-90px per item)
- [ ] Verify: Per-turn costs appear under correct resource icon columns

**Notes:**

### Task 3.4: Tests [Simple]
**Tests:** `pytest tests/integration/ui/`

- [ ] Verify resource icons load without crashing (mock pygame if needed)
- [ ] Verify queue items with cost tracking show per-turn costs
- [ ] Verify column header layout doesn't overlap with queue content
- [ ] Run: `pytest tests/ --testmon`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Manual test: Build queue panel shows resource icon column headers
- [ ] Manual test: Queue items show per-turn cost aligned under icons
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
