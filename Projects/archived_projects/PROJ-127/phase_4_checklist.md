# Phase 4: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-127 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (4 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 4.1: DUP-UI2-004 - Image Transform Operations Scattered Wit [Simple]
**File:** `game/ui/utils.py:66-94`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - The utils.py already provides centralized helpers (`scale_and_rotate_image`, `scale_image_to_fit`, etc.). Direct `pygame.transform.scale/rotate` calls elsewhere are simple one-line operations (single rotation, scaling to exact size) where helpers would add unnecessary indirection. No duplicate combined transform logic found.

### Task 4.2: DUP-UI2-005 - Validation Service Pattern Has Single-Pu [N]
**File:** `game/ui/services/validation_se`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - This is an intentional facade pattern (documented as PROJ-43). The service provides layer separation (UI → Simulation), dependency injection support, and lazy initialization. Single-purpose facades are a valid architectural pattern, not duplication.

### Task 4.3: DUP-UI2-006 - Camera Coordinate Transform Duplication [Medium]
**File:** `game/ui/renderer/camera.py:116`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - The `world_to_screen()` and `screen_to_world()` methods ARE the centralized transforms in Camera class. All 14 files using these methods are CALLING the camera methods (e.g., `camera.world_to_screen(pos)`), not duplicating the logic. This is correct usage of centralized methods.

### Task 4.4: DUP-UI2-007 - Color Constants Could Be Centralized Fur [N]
**File:** `game/ui/colors.py:7-45`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INFO - The colors.py already provides centralized `COLORS` dict and `WHITE`/`BLACK` constants. Some files use inline `(255, 255, 255)` literals in context-specific rendering - this is cosmetic and optional to change. 12 files already import from colors.py.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
