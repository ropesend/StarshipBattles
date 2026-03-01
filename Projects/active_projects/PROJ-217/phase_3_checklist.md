# Phase 3: UI & Rendering

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-217 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix rendering formulas and update UI display labels.

---

## Tasks

### Task 3.1: Fix star and Dyson Sphere rendering [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py`

- [ ] Update star rendering formula (line 528):
  ```python
  screen_star_r = max(3, int(star.radius_hexes * self.hex_size * self.camera.zoom))
  ```
- [ ] Update Dyson Sphere rendering (lines 695-706):
  - Rename variable `diameter_hexes` → `radius_hexes`
  - Change default: `11.0` → `6`
  - Rename `screen_diameter` → `screen_radius`
  - Update image scaling to use `screen_radius * 2` for width/height
- [ ] Update comments on lines 689, 695, 705

**Notes:** This is THE rendering bug fix. Stars will now render at correct size.

### Task 3.2: Fix galaxy test mode [Simple]
**File:** `game/ui/screens/galaxy_test/system_mode.py`
**Tests:** `pytest tests/unit/ui/screens/test_galaxy_test_screen.py`

- [ ] Update click detection (line 339): remove `* 0.5` factor, use `radius_hexes`
- [ ] Update second rendering location (line 517): same change
- [ ] Update UI display label (line 391): `"Diameter: {star.diameter_hexes:.1f} hexes"` → `"Radius: {star.radius_hexes} hexes"`

**Notes:**

### Task 3.3: Update detail formatters [Simple]
**Files:** `game/ui/screens/strategy_detail_fmt.py`, `game/ui/screens/strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py`

- [ ] `strategy_detail_fmt.py` line 196: `"<b>Diam:</b> {star.diameter_hexes:.1f} Hex"` → `"<b>Radius:</b> {star.radius_hexes} Hex"`
- [ ] `strategy_detail_formatter.py` line 271: same change

**Notes:**

### Task 3.4: Update visual test script [Simple]
**File:** `scripts/visual_test_galaxy.py`
**Tests:** Manual verification

- [ ] Update star rendering formula (~line 222) to use `radius_hexes`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No `diameter_hexes` references remain in `game/ui/` or `scripts/`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
