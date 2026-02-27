# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-203 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing test coverage before any code changes to ensure safe refactoring.

**Test File:** `tests/unit/ui/screens/test_strategy_renderer.py`

---

## Tasks

### Task 1.1: Colony Marker Tests [Medium]
**File:** `tests/unit/ui/screens/test_strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py -v -k "colony_marker"`

Add a new `TestDrawSystemsColonyMarker` class with these tests:

- [ ] `test_colony_marker_appears_at_low_zoom`
  - Setup: `camera.zoom = 0.4`, system with owned planet
  - Assert: `pygame.draw.circle` called with owner empire color

- [ ] `test_no_colony_marker_at_high_zoom`
  - Setup: `camera.zoom = 0.6`, system with owned planet
  - Assert: Colony marker draw NOT called (only star rendering)

- [ ] `test_colony_marker_uses_first_owner_color`
  - Setup: System with 2 planets owned by different empires
  - Assert: Marker uses `planets[0].owner_id`'s empire color

- [ ] `test_colony_marker_handles_orphaned_owner`
  - Setup: Planet with `owner_id` that doesn't exist in empires list
  - Assert: No exception, no marker drawn

**Notes:**

---

### Task 1.2: Star Rendering Tests [Medium]
**File:** `tests/unit/ui/screens/test_strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py -v -k "star"`

Add a new `TestDrawSystemsStar` class with these tests:

- [ ] `test_star_fallback_circle_when_no_image`
  - Setup: `asset_manager.load_image` returns `None`
  - Assert: `pygame.draw.circle` called with star.color

- [ ] `test_star_minimum_radius_is_3`
  - Setup: Star with very small `diameter_hexes` (e.g., 0.001)
  - Assert: Radius passed to draw is at least 3

- [ ] `test_star_selection_highlight_on_primary`
  - Setup: `scene.selected_object = sys`, star is primary
  - Assert: White circle drawn with radius `screen_star_r + 4`

**Notes:**

---

### Task 1.3: Viewport Culling Tests [Simple]
**File:** `tests/unit/ui/screens/test_strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py -v -k "margin or culling"`

Add to existing `TestDrawSystems` class:

- [ ] `test_system_beyond_margin_not_rendered`
  - Setup: System at hex (10000, 10000), camera centered at (0, 0)
  - Assert: No draw calls for that system

- [ ] `test_system_within_margin_rendered`
  - Setup: System just inside 600-unit margin
  - Assert: Star draw calls made

**Notes:**

---

### Task 1.4: Verification [Simple]
**Tests:** Full suite

- [ ] Run all new tests pass: `pytest tests/unit/ui/screens/test_strategy_renderer.py -v`
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All tests pass (no failures, no errors)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 9 new tests written and passing
- [ ] No changes to production code
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
