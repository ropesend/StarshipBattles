# Phase 4: Complex Target Planet Selection

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-79 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fleet shipyards at multi-colony hexes must prompt for which planet receives the complex. Generalize PlanetSelectionWindow from colonization-specific to reusable.

---

## Tasks

### Task 4.1: Generalize PlanetSelectionWindow [Medium]
**File:** `game/ui/screens/planet_selection_window.py`
**Tests:** `pytest tests/integration/ui/`

- [ ] Add constructor parameters with backward-compatible defaults:
  ```python
  def __init__(self, rect, manager, planets, on_selection_callback,
               window_title="Select Planet to Colonize",
               list_label="Habitable bodies:",
               show_any_button=True):
  ```
- [ ] Line 15: Replace hardcoded string with `window_title` parameter:
  ```python
  super().__init__(rect, manager, window_display_title=window_title)
  ```
- [ ] Line 29: Replace hardcoded label with `list_label` parameter:
  ```python
  self.label = UILabel(..., text=list_label, ...)
  ```
- [ ] Conditionally create `btn_any` based on `show_any_button`:
  ```python
  self.btn_any = None
  if show_any_button:
      self.btn_any = UIButton(..., "Any Planet", ...)
  ```
- [ ] Guard `btn_any.check_pressed()` (line 131):
  ```python
  if self.btn_any and self.btn_any.check_pressed():
  ```
- [ ] Verify: Existing colonization calls still work (defaults match current behavior)

**Notes:**

### Task 4.2: Verify colonization callers unchanged [Simple]
**File:** `game/ui/screens/strategy_screen.py`, `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/integration/ui/ tests/unit/strategy/`

- [ ] Verify `prompt_planet_selection()` call in strategy_ui.py uses PlanetSelectionWindow with default params
- [ ] Run colonization-related tests to ensure no breakage
- [ ] Verify: Colony ship at multi-planet hex still shows planet selection window correctly

**Notes:**

### Task 4.3: Add target_planet_id to queue items for fleet complexes [Medium]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`

- [ ] Add `on_planet_selection_needed: Optional[Callable] = None` parameter to `__init__`
- [ ] Add `hex_coord` and `galaxy` parameters to `__init__` (needed for planet lookup):
  ```python
  def __init__(self, ..., hex_coord=None, galaxy=None, empire=None,
               on_planet_selection_needed=None):
  ```
- [ ] Add helper `_needs_planet_selection(self, source, category) -> bool`:
  ```python
  def _needs_planet_selection(self, source, category):
      """Check if adding a complex to this source requires planet selection."""
      if category != "complex":
          return False
      if source.context_type != "fleet":
          return False
      if source.planet_id is not None:
          return False  # Already has a fixed planet
      if not self.hex_coord or not self.galaxy or not self.empire:
          return False
      planets = [p for p in self.galaxy.get_planets_at_global_hex(self.hex_coord)
                 if p.owner_id == self.empire.id]
      return len(planets) > 1
  ```
- [ ] In `_add_to_single_queue()`: when `_needs_planet_selection()` returns True:
  - Get planet list from galaxy
  - Call `self.on_planet_selection_needed(planets, callback)` where callback creates queue_item with `target_planet_id=planet.id`
  - Return early (don't add to queue directly — the callback does it)
- [ ] When only 1 planet at hex, auto-set `target_planet_id` without prompting
- [ ] For planet-based sources (planet_id is set), auto-set `target_planet_id=source.planet_id`
- [ ] Verify: Fleet shipyard + complex + multi-colony = callback triggered

**Notes:**

### Task 4.4: Wire planet selection prompt in BuildQueueScreen [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Manual test - fleet shipyard at multi-colony hex, add complex

- [ ] Pass `hex_coord`, `galaxy`, `empire` to `BuildQueueController.__init__()` (line 138-144)
- [ ] Add method `_prompt_target_planet(self, planets, on_selected)`:
  ```python
  def _prompt_target_planet(self, planets, on_selected):
      """Open planet selection window for complex target planet."""
      rect = pygame.Rect(200, 100, 950, 650)
      self.planet_selection_window = PlanetSelectionWindow(
          rect, self.manager, planets, on_selected,
          window_title="Select Target Planet",
          list_label="Colonies in sector:",
          show_any_button=False
      )
  ```
- [ ] Pass `on_planet_selection_needed=self._prompt_target_planet` to controller
- [ ] Add import for `PlanetSelectionWindow` at top of file
- [ ] Verify: Adding complex to fleet shipyard at multi-colony hex opens planet selection

**Notes:**

### Task 4.5: Use target_planet_id in ProductionEngine [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`

- [ ] In `_spawn_fleet_complex()` (line 460-523):
  - Read `target_planet_id` from queue item (passed as parameter or from item dict)
  - If present, find matching planet from `planets_at_hex`:
    ```python
    target_id = item.get("target_planet_id")
    if target_id is not None:
        planet = next((p for p in planets_at_hex if p.id == target_id), planets_at_hex[0])
    else:
        planet = planets_at_hex[0]  # Legacy fallback
    ```
  - Replace line 491: `planet = planets_at_hex[0]` with the above logic
- [ ] Verify: Complex spawns on correct planet when target_planet_id is set

**Notes:**

### Task 4.6: Tests [Medium]
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py tests/unit/strategy/production_engine/`

- [ ] Test PlanetSelectionWindow with `window_title="Test"` and `show_any_button=False`
- [ ] Test controller `_needs_planet_selection()` returns True for fleet+complex+multi-colony
- [ ] Test controller `_needs_planet_selection()` returns False for planet-based source
- [ ] Test controller triggers `on_planet_selection_needed` callback when needed
- [ ] Test controller auto-sets `target_planet_id` for single-colony hex
- [ ] Test `_spawn_fleet_complex()` uses `target_planet_id` when present
- [ ] Test `_spawn_fleet_complex()` falls back to first planet when absent (legacy)
- [ ] Run: `pytest tests/ --testmon`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Manual test: Fleet shipyard at multi-colony hex, add complex -> planet selection popup
- [ ] Manual test: Colonization planet selection still works correctly
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
