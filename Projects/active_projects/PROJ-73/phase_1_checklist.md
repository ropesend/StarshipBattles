# Phase 1: Add Animation State and Rotation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-73 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add slow rotation animation to warp point graphics

---

## Tasks

### Task 1.1: Add Animation State to Renderer [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/ --testmon`

- [ ] Add constant after imports (line ~17):
  ```python
  # Animation constants
  WARP_POINT_ROTATION_SPEED = 12.0  # degrees per second
  ```
- [ ] Add `_elapsed_time = 0.0` to `__init__` (line ~34, after font cache init)
- [ ] Add `update(dt)` method after `__init__`:
  ```python
  def update(self, dt: float) -> None:
      """Update animation state.

      Args:
          dt: Delta time in seconds since last frame
      """
      self._elapsed_time += dt
  ```
- [ ] Verify: No test failures

**Notes:** [Filled during implementation]

---

### Task 1.2: Wire Up Renderer Update [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py --testmon`

- [ ] Modify `update(dt)` method (line 176-179) to add renderer update:
  ```python
  def update(self, dt):
      """Update scene state."""
      self.camera.update(dt)
      self._renderer.update(dt)  # ADD THIS LINE
      self.ui.update(dt)
  ```
- [ ] Verify: No test failures

**Notes:** [Filled during implementation]

---

### Task 1.3: Add Rotation Import [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** N/A (import only)

- [ ] Add import at top of file (after line 17):
  ```python
  from game.ui.utils import scale_and_rotate_image
  ```
- [ ] Verify: File still imports without error

**Notes:** [Filled during implementation]

---

### Task 1.4: Apply Rotation to Warp Point Rendering [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/ --testmon` then visual test

- [ ] Replace warp point rendering code (lines 464-468):

  **Before:**
  ```python
  if img:
      size = int(12 * self.camera.zoom)
      scaled = pygame.transform.smoothscale(img, (size, size))
      dest = scaled.get_rect(center=(int(w_screen.x), int(w_screen.y)))
      screen.blit(scaled, dest, special_flags=pygame.BLEND_ADD)
  ```

  **After:**
  ```python
  if img:
      size = int(12 * self.camera.zoom)

      # Calculate rotation: unique offset per warp point + continuous rotation
      rotation_offset = hash(wp) % 360
      rotation_angle = rotation_offset + (self._elapsed_time * WARP_POINT_ROTATION_SPEED)

      # Scale factor for rotation utility
      orig_size = max(img.get_width(), img.get_height())
      scale_factor = size / orig_size if orig_size > 0 else 1.0

      # Apply scale and rotation
      rotated = scale_and_rotate_image(img, scale_factor, rotation_angle)
      dest = rotated.get_rect(center=(int(w_screen.x), int(w_screen.y)))
      screen.blit(rotated, dest, special_flags=pygame.BLEND_ADD)
  ```
- [ ] Verify: `pytest tests/ --testmon` passes
- [ ] Visual test: Launch game, enter strategy view, zoom in on system with warp points
- [ ] Verify: Warp points rotate slowly
- [ ] Verify: Different warp points have different rotation angles

**Notes:** [Filled during implementation]

---

### Task 1.5: Final Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: All tests pass (baseline: 6630 passed, 1 pre-existing failure)
- [ ] Visual test: Warp points rotate smoothly with unique offsets

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to completion
