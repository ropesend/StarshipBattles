<<<<<<< HEAD
# Phase 2: Template Refactor & Projectile Migration
=======
# Phase 2: Enhance PlanetReportPanel API
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-54 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
<<<<<<< HEAD
**Objective:** Refactor `StaticTargetScenario.verify()` to support result collection hooks, then migrate projectile scenarios from raw `TestScenario` to `StaticTargetScenario`.

**Prerequisite:** Phase 1 complete
=======
**Objective:** Add backward-compatible parameters to PlanetReportPanel to make it flexible for different contexts (Strategy UI, Planet List, Colonize window).

**Why This Phase:** These API enhancements enable panel reuse in Strategy UI (no complexes list) and cleaner initialization patterns. All changes are backward-compatible.
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

---

## Tasks

<<<<<<< HEAD
### Task 2.1: Refactor `StaticTargetScenario.verify()` [Medium]
**File:** `simulation_tests/scenarios/templates.py`
**Tests:** `pytest simulation_tests/ -v`

The current `verify()` at lines 168-222 combines result collection with pass/fail logic. Subclasses that override `verify()` lose all standard result collection. Split into two parts.

- [x] Create `_collect_results(self, battle_engine)` method that extracts the result-storage portion of `verify()`:
  ```python
  def _collect_results(self, battle_engine):
      """Collect standard results. Always called, even if verify() is overridden."""
      self.damage_dealt = self.initial_hp - self.target.hp
      self.results['initial_hp'] = self.initial_hp
      self.results['final_hp'] = self.target.hp
      self.results['damage_dealt'] = self.damage_dealt
      self.results['ticks_run'] = battle_engine.tick_counter
      self.results['target_alive'] = self.target.is_alive
      if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
          self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter
      for key in self.custom_result_keys:
          if hasattr(self, key):
              self.results[key] = getattr(self, key)
      # Hook for subclasses to add extra results
      if hasattr(self, '_collect_extra_results'):
          self._collect_extra_results(battle_engine)
      # Run validation rules
      if hasattr(self.metadata, 'validation_rules') and self.metadata.validation_rules:
          self.run_validation(battle_engine)
  ```
- [x] Update `verify()` to call `_collect_results()` first, then apply pass criteria:
  ```python
  def verify(self, battle_engine) -> bool:
      if self.skip_test:
          self.results['skipped'] = True
          self.results['skip_reason'] = self.skip_reason
          return False
      self._collect_results(battle_engine)
      # Pass criteria precedence (highest to lowest):
      # 1. measurement_mode - always passes if simulation completed
      # 2. expect_no_damage - passes if zero damage
      # 3. min_damage_threshold - passes if damage >= threshold
      # 4. verify_damage_dealt - passes if any damage dealt
      # 5. NotImplementedError - subclass must override
      if self.measurement_mode:
          return battle_engine.tick_counter > 0
      elif self.expect_no_damage:
          return self.damage_dealt == 0
      elif self.min_damage_threshold > 0:
          return self.damage_dealt >= self.min_damage_threshold
      elif self.verify_damage_dealt:
          return self.damage_dealt > 0
      else:
          raise NotImplementedError(...)
  ```
- [x] Document pass criteria precedence in a docstring/comment on `verify()` (Issue 5)
- [x] Verify: Run `pytest simulation_tests/ -v` - all existing tests pass unchanged

**Notes:** Subclasses that currently override `verify()` will still work - they just won't benefit from `_collect_results()` yet. Phases 3 will update them.

---

### Task 2.2: Migrate Projectile Scenarios to `StaticTargetScenario` [Complex]
**File:** `simulation_tests/scenarios/projectile_scenarios.py`
**Tests:** `pytest simulation_tests/ -v`

All 9 projectile scenarios extend raw `TestScenario`. They need to extend `StaticTargetScenario` and use its setup/update/verify machinery.

**Strategy:** Migrate one scenario at a time. After each, run tests to verify identical behavior.

- [x] Study first projectile scenario (`ProjectileStationaryTargetScenario`) - note its setup, update, verify logic
- [x] Compare with `StaticTargetScenario` template - identify what's identical vs. unique
- [x] Migrate `ProjectileStationaryTargetScenario`:
  - Change base class to `StaticTargetScenario`
  - Set class attributes: `attacker_ship`, `target_ship`, `distance`
  - Remove manual `setup()` - rely on template (or use `custom_setup` for unique parts)
  - Remove manual `update()` - rely on template `force_fire=True`
  - Simplify `verify()` - use template flags or call `_collect_results()`
  - Ensure test ID and pass/fail behavior unchanged
- [x] Verify: `pytest simulation_tests/ -v` - ProjectileStationaryTargetScenario passes
- [x] Migrate remaining 8 projectile scenarios one at a time:
  - [x] `ProjectileLinearSlowTargetScenario` (was listed as ProjectileLongRangeScenario)
  - [x] `ProjectileLinearFastTargetScenario` (was listed as ProjectileOutOfRangeScenario)
  - [x] `ProjectileErraticSmallTargetScenario` (was listed as ProjectileHighDamageScenario)
  - [x] `ProjectileErraticLargeTargetScenario` (was listed as ProjectileMultiShotScenario)
  - [x] `ProjectileOutOfRangeScenario` (was listed as ProjectileSpeedVariationScenario)
  - [x] `ProjectileDamageCloseRangeScenario` (was listed as ProjectileDamageAccumulationScenario)
  - [x] `ProjectileDamageMidRangeScenario` (was listed as ProjectileDestructionScenario)
  - [x] `ProjectileDamageLongRangeScenario` (was listed as ProjectileMaxRangeScenario)
- [x] Verify after each migration: `pytest simulation_tests/ -v`
- [x] Remove helper functions in projectile_scenarios.py that are no longer needed (`calculate_ticks_needed` removed; `calculate_projectile_travel_time` still used by 4 scenarios)
- [x] Update `simulation_tests/scenarios/__init__.py` exports if class names changed (they didn't)

**Notes:** The key constraint is that test IDs and pass/fail must be identical. This is a refactor.
=======
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
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

---

## Phase Completion Checklist
When all tasks above are done:
<<<<<<< HEAD
- [x] All task checkboxes above are checked
- [x] `pytest simulation_tests/ -v` passes
- [x] `pytest tests/ -n 4` passes (full suite)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
=======
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

>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08
