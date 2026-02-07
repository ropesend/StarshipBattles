# Phase 2: Enhance PlanetReportPanel API

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-54 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add backward-compatible parameters to PlanetReportPanel to make it flexible for different contexts (Strategy UI, Planet List, Colonize window).

**Why This Phase:** These API enhancements enable panel reuse in Strategy UI (no complexes list) and cleaner initialization patterns. All changes are backward-compatible.

---

## Tasks

### Task 2.1: Add portrait_surface parameter to __init__ [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_enhanced_planet_report.py`

- [ ] Read current `__init__` method (line 27)
- [ ] Update signature to add `portrait_surface=None`:
  ```python
  def __init__(self, manager, rect, planet, container=None, portrait_surface=None):
  ```
- [ ] Store parameter for potential later use: `self._init_portrait_surface = portrait_surface`
- [ ] At end of `__init__` (after line 102), call portrait update:
  ```python
  # Apply initial portrait if provided
  if portrait_surface is not None:
      self._update_portrait(portrait_surface)
  ```
- [ ] Update docstring (lines 16-25) to document new parameter:
  ```python
  """
  Args:
      ...existing args...
      portrait_surface (pygame.Surface, optional): Pre-loaded portrait image.
          If provided, will be used instead of generating placeholder.
  ```
- [ ] Test backward compatibility: Verify existing BuildQueueScreen code still works without passing portrait_surface

**Notes:**
_[Implementation discoveries, any issues found]_

---

### Task 2.2: Add show_complexes parameter [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/integration/ui/test_planet_complexes_list.py`

- [ ] Update `__init__` signature (line 27) to add `show_complexes=True`:
  ```python
  def __init__(self, manager, rect, planet, container=None, portrait_surface=None, show_complexes=True):
  ```
- [ ] Locate complexes list creation code (lines 71-95)
- [ ] Wrap in conditional:
  ```python
  if show_complexes:
      # Create complexes list header (line 71)
      complexes_label = UILabel(...)

      # Create scrolling container (lines 74-80)
      self.complexes_container = UIScrollingContainer(...)

      # Initialize items list
      self.complex_items = []
  else:
      # No complexes list - set to None
      self.complexes_container = None
      self.complex_items = []
  ```
- [ ] Adjust info text width calculation (around line 67):
  ```python
  # Calculate text box width based on whether complexes are shown
  if show_complexes:
      text_width = rect.width - 380  # Leave room for complexes list (200px + margins)
  else:
      text_width = rect.width - 170  # Only leave room for portrait and graph
  ```
- [ ] Update `_update_complexes_list()` method (line 199) to check if enabled:
  ```python
  def _update_complexes_list(self):
      """Update the list of built complexes."""
      if not self.complexes_container:
          return  # Complexes list disabled, nothing to update

      # ... existing code
  ```
- [ ] Update docstring to document new parameter
- [ ] Test with `show_complexes=False`: Panel should adapt layout, no complexes list visible

**Notes:**
_[Layout observations, width calculations]_

---

### Task 2.3: Update BuildQueueScreen to use new __init__ parameters [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Manual test - open build queue, verify panel displays

- [ ] Locate PlanetReportPanel creation (lines 102-121)
- [ ] Update to use new `portrait_surface` parameter at init time:
  ```python
  # Current approach (two-step):
  self.planet_report = PlanetReportPanel(...)
  if self.portrait_surface:
      self.planet_report.update_planet(self.planet, self.portrait_surface)

  # New approach (single step):
  self.planet_report = PlanetReportPanel(
      manager=self.manager,
      rect=pygame.Rect(10, 10, 580, 350),
      planet=self.planet,
      container=self.background,
      portrait_surface=self.portrait_surface  # Pass at init
  )
  ```
- [ ] Remove redundant `update_planet()` call if no longer needed
- [ ] Test: Open build queue, verify planet panel displays correctly

**Notes:**
_[Cleaner initialization observed]_

---

### Task 2.4: Add tests for new parameters [Medium]
**File:** `tests/integration/ui/test_build_queue_enhanced_planet_report.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_enhanced_planet_report.py -v`

- [ ] Add test for `portrait_surface` parameter in __init__:
  ```python
  def test_portrait_surface_at_init(session_with_planet, manager):
      """Test passing portrait_surface at initialization."""
      planet = session_with_planet.galaxy.planets[0]

      # Create a test portrait surface
      portrait = pygame.Surface((150, 150))
      portrait.fill((100, 100, 200))

      panel = PlanetReportPanel(
          manager=manager,
          rect=pygame.Rect(0, 0, 580, 350),
          planet=planet,
          portrait_surface=portrait
      )

      # Verify portrait was applied
      assert panel.portrait_image is not None
      # Verify no crash, panel created successfully
      assert panel.planet == planet
  ```
- [ ] Add test for `show_complexes=False`:
  ```python
  def test_show_complexes_false(session_with_planet, manager):
      """Test panel with complexes list hidden."""
      planet = session_with_planet.galaxy.planets[0]

      panel = PlanetReportPanel(
          manager=manager,
          rect=pygame.Rect(0, 0, 580, 350),
          planet=planet,
          show_complexes=False
      )

      # Verify complexes container is None
      assert panel.complexes_container is None
      assert panel.complex_items == []

      # Verify panel still functions (info text wider)
      assert panel.detail_text is not None
  ```
- [ ] Run all existing tests, verify backward compatibility (no failures)
- [ ] Document test results

**Notes:**
_[Test results, any failures to fix]_

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `portrait_surface` parameter works at __init__
- [ ] `show_complexes=False` hides complexes list, adapts layout
- [ ] BuildQueueScreen uses cleaner initialization
- [ ] All tests pass (no new failures)
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row 2 to `Complete`
- [ ] Update `plan.md` Current State to:
  ```
  **Last Updated:** [DATE]
  **Active Phase:** Phase 3 - Replace Strategy UI
  **Last Action:** Completed Phase 2 - PlanetReportPanel API enhanced with backward-compatible parameters
  **Next Action:** Begin Phase 3 - Replace Strategy UI inline implementation with PlanetReportPanel
  ```

