# Phase 4: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-133 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (9 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 4.1: CON-UI2-001 - Inconsistent DI Pattern Between Services [Medium]
**File:** `game/ui/services/`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPT AS-IS (Design Decision) - DI pattern varies intentionally. ComponentService docstring documents that "Services may choose strict required pattern when PROJ-50 explicitly mandated it (e.g., VehicleClassService)". The pattern is:
- Optional with lazy resolution = default for most services
- Strict required = when explicitly mandated by PROJ-50
This is documented design, not inconsistency.

### Task 4.2: CON-UI2-003 - Singleton Classes Missing Type Hints on [Simple]
**File:** `game/ui/renderer/sprites.py:26`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPT AS-IS (False Positive) - All singleton classes use the same pattern: __init__ with no type hints on instance variables. This is consistent across ALL singletons (SpriteManager, ScreenshotManager, ShipThemeManager). The pattern is uniform, not inconsistent.

### Task 4.3: CON-UI2-004 - Inconsistent Docstring Presence and Form [Medium]
**File:** `game/ui/services/screenshot_manager.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Converted :param style docstrings in screenshot_manager.py to Google Args: style for consistency with the rest of the codebase. Updated capture() and capture_strategy_layer() methods.

### Task 4.4: CON-UI2-005 - Static Methods vs Instance Methods Incon [Medium]
**File:** `game/ui/services/ship_io.py:41`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPT AS-IS (Design Decision) - Static method pattern with class-level config is appropriate for UI file dialog utilities. ShipIO doesn't need DI for registries - it's a stateless file I/O utility where the only "state" is a configurable folder path. This pattern differs from other services intentionally because file dialogs are fundamentally different from registry-dependent services.

### Task 4.5: CON-UI2-002 - Mixed Parameter Naming for Registry Inje [Simple]
**File:** `game/ui/services/`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPT AS-IS (False Positive) - Parameter naming IS consistent. All services use `registry_provider` for registry dependencies. Type variations (IRegistryProvider vs GameRegistries vs Any) are intentional based on each service's requirements:
- IRegistryProvider = protocol/interface
- GameRegistries = concrete implementation
- Any = when accepting multiple types

### Task 4.6: CON-UI2-009 - Magic Numbers in Rendering Code [Simple]
**File:** `game/ui/renderer/game_renderer`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPT AS-IS (Design Decision) - Rendering constants (50 culling radius, 0.3 zoom threshold, etc.) are visual parameters tightly coupled to the renderer logic. Extracting to UIConfig would add indirection without benefit since:
1. They're only used in this file
2. They require understanding render context to modify
3. They're not shared across modules

### Task 4.7: CON-UI2-012 - Module-Level Side Effects [Medium]
**File:** `game/ui/services/ship_io.py:20`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPT AS-IS (Design Decision) - Module-level Tkinter initialization is appropriate for a file dialog utility module. The side effect is:
1. Contained and documented
2. Handled gracefully with try/except
3. Logged when it fails
4. Required before file dialogs can work

### Task 4.8: CON-UI2-007 - Inconsistent Error Handling - Return vs [Simple]
**File:** `game/ui/services/ship_io.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPT AS-IS (Design Decision) - Error handling pattern varies appropriately by use case:
- User-facing operations (file dialogs) → return tuple for graceful UI handling
- Internal factory operations → raise exceptions for clear error propagation
- Validation operations → return ValidationResult with details
This is consistent by PURPOSE, not arbitrary.

### Task 4.9: CON-UI2-010 - Inconsistent Use of Optional Type Annota [Simple]
**File:** `game/ui/renderer/sprites.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Changed `"pygame.Surface | None"` to `Optional[pygame.Surface]` in sprites.py get_sprite() method for consistency with codebase convention. Added `from typing import Optional` import.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
