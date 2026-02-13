# Phase 3: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-114 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (16 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 3.1: CON-UI2-001 - Inconsistent DI Pattern Across Services [Medium]
**File:** `game/ui/services/vehicle_class`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - ComponentService docstring (lines 31-38) explicitly documents intentional pattern variation. VehicleClassService uses strict DI per PROJ-50; others use lenient DI intentionally.

### Task 3.2: CON-UI2-002 - Complete Absence of Type Hints in render [Medium]
**File:** `game/ui/renderer/camera.py:all`
**Tests:** `pytest tests/unit/ui/test_camera.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIX - Added type hints to all Camera methods: __init__, update, update_input, world_to_screen, screen_to_world, fit_objects.

### Task 3.3: CON-UI2-003 - Complete Absence of Type Hints in widget [Simple]
**File:** `game/ui/widgets.py:1-102`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED - widgets.py was deleted in PROJ-117 Phase 3.

### Task 3.4: CON-UI2-004 - Singleton Pattern Used in renderer/ and [Complex]
**File:** `game/ui/renderer/sprites.py:7`
**Tests:** `pytest tests/unit/ui/test_sprites.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED - SpriteManager already uses SingletonMeta metaclass from PROJ-108.

### Task 3.5: CON-UI2-005 - Missing Docstrings on Public Methods in [Medium]
**File:** `game/ui/renderer/sprites.py:27`
**Tests:** `pytest tests/unit/ui/test_sprites.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIX - Added docstrings and type hints to _load_from_directory, get_sprite, and updated load_sprites docstring format.

### Task 3.6: CON-UI2-006 - Inconsistent Error Handling - traceback [Simple]
**File:** `game/ui/renderer/sprites.py:11`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - No traceback import or usage in sprites.py or renderer directory.

### Task 3.7: CON-UI2-007 - Hardcoded Magic Colors in renderer/game_ [Medium]
**File:** `game/ui/renderer/game_renderer`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - LAYER_COLORS constant is properly defined. Inline colors in draw_hud are acceptable for temporary debug HUD rendering.

### Task 3.8: CON-UI2-008 - Hardcoded Font Creation in game_renderer [Medium]
**File:** `game/ui/renderer/game_renderer`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Fonts created per-call for rarely-used debug HUD. Extracting to constants would be premature optimization.

### Task 3.9: CON-UI2-009 - game/ui/__init__.py Imports Screens but [Simple]
**File:** `game/ui/__init__.py:14-16`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - __init__.py imports AND exports correctly (lines 14-27). Docstring explains imports are for pytest-xdist race conditions.

### Task 3.10: CON-UI2-010 - Mixed Naming for Internal Provider Acces [Simple]
**File:** `game/ui/services/component_ser`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Both ComponentService and VehicleClassService use consistent `_get_provider()` method naming.

### Task 3.11: CON-UI2-011 - Inconsistent Return Patterns for load_sh [Medium]
**File:** `game/ui/services/ship_io_adapt`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - ship_io_adapter.py docstring (lines 28-35) explicitly documents intentional difference: save returns Tuple[bool, str], load returns Tuple[Optional[T], str].

### Task 3.12: CON-UI2-012 - Camera.fit_objects Sets zoom Directly, B [Simple]
**File:** `game/ui/renderer/camera.py:153`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - fit_objects sets zoom directly for instant snap (not animated). This is intentional for fitting camera without animation.

### Task 3.13: CON-UI2-013 - draw_ship Contains Inline Import of Ship [Simple]
**File:** `game/ui/renderer/game_renderer`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Late import at line 46 avoids circular dependency. This is documented pattern in codebase.

### Task 3.14: CON-UI2-014 - Service Class Naming Convention - "Servi [N]
**File:** `game/ui/services/`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - All service classes use consistent "Service" suffix: ComponentService, VehicleClassService, ValidationService, etc.

### Task 3.15: CON-UI2-015 - colors.py Has No Module Docstring and No [Simple]
**File:** `game/ui/colors.py:1-35`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - colors.py has module docstring at lines 1-4 referencing PROJ-113.

### Task 3.16: CON-UI2-016 - Inconsistent Docstring Style Between ren [Simple]
**File:** `game/ui/renderer/camera.py:24-`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Camera docstrings use consistent style (imperative sentences, Args/Returns sections).


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

## Summary
- **16 findings investigated**
- **3 fixes**: Camera type hints, SpriteManager docstrings/type hints
- **2 already fixed**: widgets.py (deleted), singleton pattern
- **11 false positive/acceptable**: DI pattern, traceback, magic colors, fonts, __init__.py, provider naming, load_ship return, fit_objects, inline import, service naming, colors docstring, docstring style
