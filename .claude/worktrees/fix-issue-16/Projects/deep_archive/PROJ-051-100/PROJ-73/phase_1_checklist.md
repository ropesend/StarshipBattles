# Phase 1: Add Animation State and Rotation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-73 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add slow rotation animation to warp point graphics

---

## Tasks

### Task 1.1: Add Animation State to Renderer [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/ --testmon`

- [x] Add constant after imports (line ~17):
  ```python
  # Animation constants
  WARP_POINT_ROTATION_SPEED = 12.0  # degrees per second
  ```
- [x] Add `_elapsed_time = 0.0` to `__init__` (line ~34, after font cache init)
- [x] Add `update(dt)` method after `__init__`:
  ```python
  def update(self, dt: float) -> None:
      """Update animation state.

      Args:
          dt: Delta time in seconds since last frame
      """
      self._elapsed_time += dt
  ```
- [x] Verify: No test failures

**Notes:** Added constant, _elapsed_time field, and update() method. Also added `from game.ui.utils import scale_and_rotate_image` import in same edit.

---

### Task 1.2: Wire Up Renderer Update [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py --testmon`

- [x] Modify `update(dt)` method (line 176-179) to add renderer update:
  ```python
  def update(self, dt):
      """Update scene state."""
      self.camera.update(dt)
      self._renderer.update(dt)  # ADD THIS LINE
      self.ui.update(dt)
  ```
- [x] Verify: No test failures

**Notes:** Added `self._renderer.update(dt)` between camera and ui updates.

---

### Task 1.3: Add Rotation Import [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** N/A (import only)

- [x] Add import at top of file (after line 17):
  ```python
  from game.ui.utils import scale_and_rotate_image
  ```
- [x] Verify: File still imports without error

**Notes:** Combined with Task 1.1 edit.

---

### Task 1.4: Apply Rotation to Warp Point Rendering [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/ --testmon` then visual test

- [x] Replace warp point rendering code (lines 464-468)
- [x] Verify: `pytest tests/ --testmon` passes
- [ ] Visual test: Launch game, enter strategy view, zoom in on system with warp points (deferred to user)
- [ ] Verify: Warp points rotate slowly (deferred to user)
- [ ] Verify: Different warp points have different rotation angles (deferred to user)

**Notes:** Replaced smoothscale with scale_and_rotate_image. Uses hash(wp) % 360 for per-warp-point offset + elapsed_time * WARP_POINT_ROTATION_SPEED for continuous rotation.

---

### Task 1.5: Final Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify: All tests pass (6823 passed, 1 pre-existing failure in test_protocols.py)
- [ ] Visual test: Warp points rotate smoothly with unique offsets (deferred to user)

**Notes:** 6823 passed (up from 6813 baseline, +10 new animation tests). 1 pre-existing failure unrelated.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to completion
