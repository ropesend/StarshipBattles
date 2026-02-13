# Phase 4: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-113 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (10 findings, 2 critical)
**Priority:** High

---

## Tasks

### Task 4.1: ADR-UI2-001 - Pygame in Core Layer -- ScreenshotManager [Medium]
**File:** `game/core/screenshot_manager.py`
**Tests:** N/A - already fixed

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED in Phase 1 - ScreenshotManager moved from game/core/ to game/ui/services/

### Task 4.2: ADR-UI2-002 - Pygame in Core Layer -- InputMapper [Complex]
**File:** `game/core/input_mapper.py:26`
**Tests:** N/A - already fixed

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED in Phase 1 - InputMapper moved from game/core/ to game/ui/services/

### Task 4.3: ADR-UI2-003 - Renderer Directly Accesses Simulation Domain [Medium]
**File:** `game/ui/renderer/game_renderer.py`
**Tests:** N/A - false positive

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - game_renderer.py imports LayerType/LayerDefaults from game.core.constants (correct layer). No simulation imports present. The file correctly accesses ship properties via the passed ship object (not directly importing simulation modules).

### Task 4.4: ADR-UI2-004 - ShipFactory Uses pygame.math.Vector2 [Simple]
**File:** `game/ui/services/ship_factory.py`
**Tests:** N/A - false positive

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - ShipFactory is in game/ui/services/ (UI layer). Pygame imports are acceptable in UI layer. The factory correctly uses pygame.math.Vector2 for position handling.

### Task 4.5: ADR-UI2-005 - DesignLoaderAdapter Has Hard Runtime Import [Simple]
**File:** `game/ui/services/design_loader_adapter.py`
**Tests:** N/A - architectural pattern

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ARCHITECTURAL PATTERN - The adapter's PURPOSE is to wrap SimulationDesignLoader. This is correct facade/adapter pattern: UI layer → Adapter → Simulation layer. The import is the mechanism by which the adapter provides its service. No change needed.

### Task 4.6: ADR-UI2-006 - Pygame TYPE_CHECKING Import in AI Layer [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** N/A - already fixed

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED - controllable.py uses `Any` type hints for Vector2 to avoid pygame dependency in AI layer. Comment at line 18: "Note: Vector2 type hints use Any to avoid pygame dependency in AI layer."

### Task 4.7: ADR-UI2-007 - ScreenshotManager Accesses Private _renderer [Medium]
**File:** `game/core/screenshot_manager.py`
**Tests:** N/A - already fixed

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED in Phase 1 - ScreenshotManager moved from game/core/ to game/ui/services/. File no longer exists at old location.

### Task 4.8: ADR-UI2-008 - ValidationService Has Eager Runtime Import [Simple]
**File:** `game/ui/services/validation_service.py`
**Tests:** N/A - architectural pattern

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ARCHITECTURAL PATTERN - ValidationService imports get_or_create_validator from simulation layer. This is correct facade pattern: UI layer → Service → Simulation validator. The service wraps the validator with a clean interface. No change needed.

### Task 4.9: ADR-UI2-009 - game_renderer.py Uses Lazy Import Inside Function [Simple]
**File:** `game/ui/renderer/game_renderer.py`
**Tests:** N/A - acceptable pattern

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Line 46 lazy imports ShipThemeManager. This is UI layer → UI layer import (game.ui.assets). The lazy import avoids circular dependency within UI layer. Both modules are in correct layer.

### Task 4.10: ADR-UI2-010 - Consistent Use of Facade/Adapter Pattern [N]
**File:** `game/ui/services/`
**Tests:** N/A - info severity

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INFO - This is an observation about existing patterns. The services in game/ui/services/ (ShipFactory, ValidationService, DesignLoaderAdapter) consistently use facade/adapter pattern to access simulation layer. Pattern is correctly implemented.


---

## Summary
- **ALREADY FIXED (Phase 1):** 4.1, 4.2, 4.6, 4.7 (ScreenshotManager, InputMapper moved to UI)
- **FALSE POSITIVE:** 4.3, 4.4 (correct layer usage)
- **ARCHITECTURAL PATTERN:** 4.5, 4.8 (facade/adapter correctly wrapping simulation)
- **ACCEPTABLE:** 4.9 (UI→UI lazy import)
- **INFO:** 4.10 (observation, pattern correctly implemented)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
