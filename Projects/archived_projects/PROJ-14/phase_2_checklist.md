# Phase 2: Remove Commented/Dead Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-14 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Clean up commented debug code from production files

---

## Tasks

### Task 2.1: Clean ui/test_lab_scene.py [Simple]
**File:** `ui/test_lab_scene.py`
**Tests:** `pytest tests/unit/ui/test_test_lab_scene.py -v`

**IMPORTANT:** Work from bottom to top to preserve line numbers!

- [x] Delete deprecated method `_draw_seed_controls_OLD()` (lines 3657-3741, 85 lines)
  - This entire method is marked `"""DEPRECATED - Seed controls moved to header. This is kept for reference."""`
- [x] Remove debug import at lines 2718-2719:
  ```python
  import traceback
  traceback.print_exc()
  ```
- [x] Remove debug import at lines 2585-2586:
  ```python
  import traceback
  traceback.print_exc()
  ```
- [x] Remove debug import at lines 2167-2168:
  ```python
  import traceback
  traceback.print_exc()
  ```
- [x] Remove debug import at lines 1941-1942:
  ```python
  import traceback
  traceback.print_exc()
  ```
- [x] Verify: `pytest tests/unit/ui/test_test_lab_scene.py -v` - passes

**Notes:** Removed deprecated _draw_seed_controls_OLD method (85 lines) and all 4 debug traceback imports. 79 tests pass.

---

### Task 2.2: Clean game/core/profiling.py [Simple]
**File:** `game/core/profiling.py`
**Tests:** `pytest tests/ --testmon`

- [x] Remove commented debug log at line 108:
  ```python
  # logger.debug(f"Profiled {name}: {duration*1000:.2f}ms")
  ```
- [x] Verify: File still works

**Notes:** Removed commented debug log. Import works correctly.

---

### Task 2.3: Clean simulation_tests/tests/test_example_scenarios.py [Simple]
**File:** `simulation_tests/tests/test_example_scenarios.py`
**Tests:** `pytest simulation_tests/tests/test_example_scenarios.py -v`

- [x] Remove commented test methods at lines 92-99:
  ```python
  # def test_beam_mid_range(self):
  #     scenario = self.runner.run_scenario(BeamMidRangeTest, headless=True)
  #     assert scenario.passed
  #
  # def test_beam_max_range(self):
  #     scenario = self.runner.run_scenario(BeamMaxRangeTest, headless=True)
  #     assert scenario.passed
  ```
- [x] Verify: File still parses correctly

**Notes:** Removed commented test placeholder methods. File parses correctly.

---

### Task 2.4: Clean tests/unit/combat/test_pdc.py [Simple]
**File:** `tests/unit/combat/test_pdc.py`
**Tests:** `pytest tests/unit/combat/test_pdc.py -v`

- [x] Remove commented debug prints at lines 130-131:
  ```python
  # print(f"DEBUG: Alive={self.ship.is_alive}, Derelict={self.ship.is_derelict}...")
  # print(f"DEBUG: PDC Active={self.pdc.is_active}, CD={self.pdc.cooldown_timer}...")
  ```
- [x] Verify: Test still passes

**Notes:** Removed commented diagnostic prints. 2 tests pass.

---

### Task 2.5: Clean Tools/process_planet_images.py [Simple]
**File:** `Tools/process_planet_images.py`
**Tests:** N/A (utility script)

- [x] Remove commented nested loops at lines 28-32:
  ```python
  # for x in range(width):
  #     for y in range(height):
  #         c = image.get_at((x, y))
  #         if c[0] < threshold and c[1] < threshold and c[2] < threshold:
  #             image.set_at((x, y), (0, 0, 0, 0))
  ```
- [x] Verify: File still parses correctly

**Notes:** Removed commented code block and associated explanation comments. File parses correctly.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ --testmon` - passes
- [x] No functionality changes (this phase only removes dead code)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
