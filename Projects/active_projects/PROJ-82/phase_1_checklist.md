# Phase 1: Remove Resources from Text & Add Resource Grid

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-82 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove resource information from the scrollable text area and create a dedicated resource grid panel at the bottom of the PlanetReportPanel with resource icons, quantity, quality, and production rows.

---

## Tasks

### Task 1.1: Remove resource section from format_planet_info [Simple]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_enhanced_planet_report.py`

- [ ] Remove the resource block (lines 147-159) from `format_planet_info()`:
  ```python
  # REMOVE THIS ENTIRE BLOCK:
  if hasattr(planet, 'resources') and planet.resources:
      text += "<br><b>Resources:</b><br>"
      for r_name, r_data in planet.resources.items():
          qty = r_data['quantity']
          if qty >= 1000000:
              q_str = f"{qty/1000000:.1f}M"
          elif qty >= 1000:
              q_str = f"{qty/1000:.0f}k"
          else:
              q_str = str(qty)
          qual = r_data['quality']
          text += f" {r_name}: {q_str} (Q:{qual:.0f})<br>"
  ```
- [ ] Verify function still returns valid HTML for all other sections (planet stats, colony status, facilities)
- [ ] Run tests to confirm no crashes

**Notes:**

---

### Task 1.2: Add resource icon loading to PlanetReportPanel [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_enhanced_planet_report.py`

- [ ] Add imports at top of file:
  ```python
  from game.ui.panels.build_queue_portraits import RESOURCE_PORTRAIT_FILES, RESOURCE_FALLBACK_COLORS
  from game.core.constants import PLANET_RESOURCES
  import os
  ```
- [ ] Add `_load_resource_icons(self, icon_size=24)` method:
  - Iterate `PLANET_RESOURCES` list using `RESOURCE_PORTRAIT_FILES` for filenames
  - Load each icon via `pygame.image.load(path)` + `pygame.transform.smoothscale(img, (icon_size, icon_size))`
  - Base path: `os.path.join("assets", "Images", "Resource Portraits")`
  - On failure: create fallback colored square using `RESOURCE_FALLBACK_COLORS`
  - Store in `self._resource_icons: Dict[str, pygame.Surface]`
- [ ] Call `_load_resource_icons()` in `__init__` before building grid

**Notes:**

---

### Task 1.3: Add resource grid panel to PlanetReportPanel [Medium]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_enhanced_planet_report.py`

- [ ] Define constant `RESOURCE_PANEL_HEIGHT = 100` at module level
- [ ] Add `production_rates: Optional[Dict[str, float]] = None` parameter to `__init__` signature
- [ ] Store `self.production_rates = production_rates or {}`
- [ ] Reduce `text_h` calculation: change `rect.height - 20` to `rect.height - 20 - RESOURCE_PANEL_HEIGHT` (line ~71)
- [ ] Reduce atmosphere graph height: change `graph_h = rect.height - 180` to `rect.height - 180 - RESOURCE_PANEL_HEIGHT` (line ~105)
- [ ] If `show_complexes=True`, also reduce complexes container height by `RESOURCE_PANEL_HEIGHT` (line ~83)
- [ ] Create resource grid UIPanel at bottom:
  ```python
  resource_y = rect.height - RESOURCE_PANEL_HEIGHT - 10
  self.resource_panel = UIPanel(
      relative_rect=pygame.Rect(10, resource_y, rect.width - 20, RESOURCE_PANEL_HEIGHT),
      manager=manager,
      container=self.panel
  )
  ```
- [ ] Add `_build_resource_grid(self)` method that populates the grid:
  - Calculate column width: `col_w = (grid_width - 60) // 5` (60px for row labels)
  - Row label column (x=5): Add UILabels "Qty", "Qual", "Prod" at y offsets 30, 50, 70
  - For each resource in `PLANET_RESOURCES` (index i):
    - Column x = `60 + i * col_w`
    - Add UIImage with resource icon at (x, 2, 24, 24) — icon header
    - Add UILabel with quantity at (x, 30, col_w, 18)
    - Add UILabel with quality at (x, 50, col_w, 18)
    - Add UILabel with production at (x, 70, col_w, 18)
  - Format values using compact format (same as removed code: >=1M → "1.2M", >=1k → "250k")
  - Production: `self.production_rates.get(resource_name, 0.0)` — show 0 if missing or non-colony
- [ ] Track all grid UI elements in `self._resource_grid_items: List` for cleanup
- [ ] Add `_update_resource_grid(self)` method to refresh values when planet changes:
  - Kill existing grid items
  - Rebuild grid with new planet data
- [ ] Add `production_rates` parameter to `update_planet()` method signature
- [ ] Store new `self.production_rates` in `update_planet()`, then call `_update_resource_grid()`
- [ ] Call `_build_resource_grid()` in `__init__` after other components
- [ ] Update `kill()` method to also kill `self.resource_panel`
- [ ] Update `get_height_required()` to return `350 + RESOURCE_PANEL_HEIGHT` (was 350)

**Notes:**

---

### Task 1.4: Update strategy_ui.py to pass production_rates [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/integration/ui/ -k strategy`

- [ ] Add helper method `_compute_planet_production(self, planet) -> Dict[str, float]`:
  ```python
  def _compute_planet_production(self, planet):
      """Compute per-resource production rates for a colony planet."""
      if planet.owner_id is None:
          return {}
      rates = {}
      for facility in getattr(planet, 'facilities', []):
          if not getattr(facility, 'is_operational', True):
              continue
          design_data = getattr(facility, 'design_data', {})
          for layer_data in design_data.get('layers', {}).values():
              if not isinstance(layer_data, list):
                  continue
              for comp in layer_data:
                  harvester = None
                  if isinstance(comp, dict):
                      harvester = comp.get('abilities', {}).get('ResourceHarvester')
                  if harvester and isinstance(harvester, dict):
                      res_type = harvester.get('resource_type', '')
                      base_rate = harvester.get('base_harvest_rate', 0.0)
                      if res_type and base_rate > 0:
                          quality = planet.resources.get(res_type, {}).get('quality', 0.0)
                          rates[res_type] = rates.get(res_type, 0.0) + base_rate * quality
      return rates
  ```
- [ ] Pass `production_rates=self._compute_planet_production(obj)` when creating PlanetReportPanel (~line 646)
- [ ] Pass `production_rates=self._compute_planet_production(planet)` in any `update_planet()` calls

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/integration/ui/test_build_queue_enhanced_planet_report.py` — all pass
- [ ] Run `pytest tests/ --testmon` — no regressions
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
