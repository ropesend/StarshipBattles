# Phase 1: Quick Wins - DRY & Magic Numbers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract duplicate code and centralize constants. Low risk, high impact.

---

## Tasks

### Task 1.1: Extract Duplicate Quickstart Methods [Simple]
**File:** `game/app.py`
**Issue:** CQ-007 - `start_quickstart_1p()` and `start_quickstart_2p()` nearly identical
**Tests:** `pytest tests/unit/app/`

- [ ] Create `_start_quickstart(player_count: int)` helper method
- [ ] Refactor `start_quickstart_1p()` to call helper with `player_count=1`
- [ ] Refactor `start_quickstart_2p()` to call helper with `player_count=2`
- [ ] Verify: Both quickstart modes still work

**Notes:**

---

### Task 1.2: Extract Window Rect Creation Helper [Simple]
**File:** `game/app.py`, create `game/ui/utils.py`
**Issue:** CQ-008 - Window creation pattern duplicated 3+ locations
**Tests:** `pytest tests/unit/ui/`

- [ ] Create `game/ui/utils.py` if not exists
- [ ] Add `create_centered_rect(width, height, screen_width, screen_height) -> pygame.Rect`
- [ ] Replace duplicates at lines 224-229, 344-349, 438-443 in `app.py`
- [ ] Replace duplicates in `game/ui/screens/workshop_screen.py` lines 776-780, 900-904
- [ ] Verify: All windows still center correctly

**Notes:**

---

### Task 1.3: Extract Image Scaling Utility [Medium]
**Files:** 10+ files with duplicate pattern
**Issue:** CQ-04 - Same image scaling pattern in 10+ files
**Tests:** `pytest tests/unit/ui/`

- [ ] Add to `game/ui/utils.py`:
  ```python
  def scale_image_to_fit(image, target_size, theme_manager=None, theme_id=None, ship_class=None, rotation=0.0) -> pygame.Surface
  ```
- [ ] Replace pattern in `game/ui/renderer/renderer.py` lines 50-83
- [ ] Replace pattern in `game/ui/renderer/game_renderer.py` lines 50-84
- [ ] Replace pattern in `game/ui/screens/builder/schematic_view.py`
- [ ] Replace pattern in `game/ui/screens/strategy_renderer.py` lines 479-523
- [ ] Verify: All ship images still render correctly

**Notes:**

---

### Task 1.4: Create UIConstants Class [Medium]
**File:** Create `game/ui/ui_constants.py`
**Issue:** CQ-016, CQ-07, SIM-010 - Magic numbers scattered
**Tests:** `pytest tests/unit/ui/`

- [ ] Create `game/ui/ui_constants.py` with UIConstants class
- [ ] Replace magic numbers in `game/ui/screens/builder/weapons_panel.py` lines 10-75
- [ ] Replace magic numbers in `game/ui/screens/race_setup_screen.py` line 59 (THEME_SHIP_SIZE)
- [ ] Verify: UI still renders correctly

**Notes:**

---

### Task 1.5: Create SimulationConstants Class [Simple]
**File:** `game/core/constants.py`
**Issue:** SIM-010 - Simulation constants scattered
**Tests:** `pytest tests/unit/simulation/`

- [ ] Add SimulationConstants class to `game/core/constants.py`
- [ ] Replace in `game/simulation/managers/retreat_manager.py` lines 33, 49
- [ ] Replace in `game/simulation/battle_controller.py` lines 51, 71
- [ ] Verify: Battle simulation works unchanged

**Notes:**

---

### Task 1.6: Unify Damage Threshold to 50% [Simple]
**Files:** `game/strategy/services/ship_stats_service.py`, `game/core/constants.py`
**Issue:** CQ-018 - Conflicting damage thresholds (50% vs 30%)
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`

- [ ] Change `ship_stats_service.py` line 32: `DEFAULT_DAMAGE_THRESHOLD = 0.5`
- [ ] Update degradation formula if using gradual model
- [ ] Add comment explaining alignment with `CombatConstants.DEFAULT_DAMAGE_THRESHOLD`
- [ ] Update any tests expecting 30% threshold
- [ ] Verify: Strategy layer shows consistent damage behavior with simulation

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
