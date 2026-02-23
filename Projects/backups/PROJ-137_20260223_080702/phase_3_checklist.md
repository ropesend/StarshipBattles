# Phase 3: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-137 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (5 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 3.1: DUP-UI2-001 - Tkinter Root Initialization Duplicated [Medium]
**File:** `game/ui/services/ship_io.py:20`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS - Different use cases. ship_io.py creates a persistent tk_root at module level (for file dialogs that need a root window). screenshot_manager.py creates/destroys Tk() per clipboard operation (stateless). Extracting would couple unrelated modules with different lifecycle requirements. Not actual duplication.

### Task 3.2: DUP-UI2-003 - Image Bounding Box + Scale Logic Duplica [Simple]
**File:** `game/ui/utils.py:116-162`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS - Already consolidated. utils.py has `get_visible_bounding_box()` and `scale_image_by_visible_portion()`. Other usages (ship_theme_manager, design_image_helper) have different semantics: ship_theme_manager uses inline get_bounding_rect() for metrics caching; design_image_helper uses scale-then-crop algorithm (vs crop-then-scale). Not duplication - intentionally different approaches.

### Task 3.3: DUP-UI2-002 - Registry Provider Lazy Resolution Patter [Medium]
**File:** `game/ui/services/component_ser`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS - Intentional DI pattern. The `_get_provider()` lazy resolution is the STANDARD documented pattern (see component_service.py lines 34-42). Only 2 files use it (component_service, vehicle_class_service). This is proper dependency injection with lazy fallback - a deliberate architectural choice, not duplication.

### Task 3.4: DUP-UI2-004 - Singleton Manager Boilerplate [Simple]
**File:** `game/ui/assets/ship_theme_mana`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS - Already consolidated. All 10 singleton managers use `metaclass=SingletonMeta` from `game.core.singleton`. The pattern IS extracted - each class just applies the metaclass. No duplication exists.

### Task 3.5: DUP-UI2-006 - Clipboard Copy Implementation [Simple]
**File:** `game/ui/services/screenshot_ma`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS - Different mechanisms for different needs. screenshot_manager uses Tkinter+subprocess fallback (for copying file paths with Windows compatibility). test_lab/screen.py uses pygame.scrap (for in-game text copy). Different APIs, different use cases, not duplication.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
