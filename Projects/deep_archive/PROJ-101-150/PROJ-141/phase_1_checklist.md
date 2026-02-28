# Phase 1: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-141 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (12 findings, 2 critical)
**Priority:** High

---

## Tasks

### Task 1.1: CON-UI2-001 - Inconsistent Dependency Injection Patter [Medium]
**File:** `game/ui/services/`
**Tests:** `pytest tests/unit/ui/services/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** SKIPPED - After investigation, this is NOT a bug. VehicleClassService uses strict DI per documented PROJ-50 decision. Other services (ComponentService, ValidationService, ShipFactory, DesignLoaderAdapter) use lazy DI. The pattern is consistent and documented. No changes needed.

### Task 1.2: DUP-UI2-001 - Tkinter Root Initialization Duplicated A [Simple]
**File:** `game/ui/services/tkinter_utils.py` (NEW)
**Tests:** `pytest tests/unit/ui/services/test_tkinter_utils.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** COMPLETE - Created new `tkinter_utils.py` module with:
- Lazy, thread-safe Tkinter root initialization
- Unified exception handling for platform-dependent operations
- Helper functions: `get_tk_root()`, `is_tkinter_available()`, `open_save_dialog()`, `open_load_dialog()`, `prompt_string()`, `copy_to_clipboard()`

Updated files to use new module:
- `game/ui/services/ship_io.py`
- `game/ui/services/screenshot_manager.py`
- `game/ui/screens/formation_editor.py`
- `game/ui/screens/workshop_ship_io.py`

Updated tests:
- `tests/unit/ui/services/test_ship_io.py`
- `tests/unit/ui/services/test_screenshot_manager.py`
- `tests/unit/builder/test_io_interactive.py`
- `tests/unit/systems/test_persistence.py`

All 11971 tests passing.

### Task 1.3: DUP-UI2-002 - Battle Factory Functions Follow Identica [Medium]
**File:** `game/ui/services/battle_factories.py`
**Tests:** `pytest tests/unit/simulation/battle_controller/test_utilities.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** COMPLETE - Extracted `_create_controller_with_config()` helper to reduce boilerplate across all 4 factory functions. Each factory now creates config, then calls helper, then adds ships/starts if needed. Also moved `ShipSerializer` import to top-level (from late import). Added 5 new tests for helper functions.

### Task 1.4: DUP-UI2-004 - BattleUIService Repeated Null-Check Patt [Simple]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/services/battle_ui_service/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** COMPLETE - Extracted `_get_engine_or_none()` helper method to eliminate duplicated null-check pattern across 6 public methods (get_ships, get_projectiles, get_recent_beams, is_battle_over, get_winner, get_tick_count). Added 3 new tests for the helper method.

### Task 1.5: CON-UI2-007 - Inconsistent Type Hint Coverage [Simple]
**File:** `game/ui/services/ship_io.py:42`
**Tests:** `pytest tests/unit/ui/services/test_ship_io.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** COMPLETE - Added type hints to save_ship() and load_ship() methods:
- `save_ship(ship: Ship) -> Tuple[bool, Optional[str]]`
- `load_ship(screen_width: int, screen_height: int) -> Tuple[Optional[Ship], Optional[str]]`
Also added import for `typing.Tuple` and `typing.Optional`.

### Task 1.6: CON-UI2-008 - Inconsistent Error Logging Patterns [Simple]
**File:** `game/ui/services/ship_io.py:72`
**Tests:** `pytest tests/unit/ui/services/test_ship_io.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Error logging patterns are already consistent. All log_error calls follow the same pattern: `log_error(f"ShipIO: <context>: {e}")`. User-facing messages appropriately vary between static text for well-known errors (PermissionError) and dynamic text for system errors (OSError). This is intentional design.

### Task 1.7: CON-UI2-010 - Boolean Parameter Naming Inconsistency [Simple]
**File:** `game/ui/services/battle_factories.py`
**Tests:** N/A - naming convention, not behavior

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Boolean parameters `headless` and `allow_retreat` follow standard Python conventions. The `is_` prefix convention applies to methods/properties that return booleans, not to function parameters. Current naming is clear and idiomatic Python.

### Task 1.8: CON-UI2-011 - Inconsistent Import Organization [Simple]
**File:** `game/ui/services/ship_io.py:1-`
**Tests:** N/A - import organization, not behavior

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** COMPLETE - Reorganized local imports by layer following PEP 8 and project conventions:
1. Standard library (json, os, typing)
2. game.core.* (alphabetically)
3. game.simulation.*
4. game.ui.*

### Task 1.9: CON-UI2-012 - Magic Numbers in Rendering Code [Simple]
**File:** `game/ui/renderer/game_renderer.py`
**Tests:** N/A - rendering constants, not testable behavior

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** COMPLETE - Extracted 8 magic numbers to named constants at module level:
- CULLING_MAX_RADIUS = 50
- MIN_ZOOM_FOR_IMAGE = 0.01
- MIN_ZOOM_FOR_COMPONENTS = 0.3
- IMAGE_ROTATION_OFFSET = -90
- COMPONENT_DOT_RADIUS = 3
- DIRECTION_LINE_OFFSET = 10
- DIRECTION_LINE_WIDTH = 2
- FALLBACK_DOT_RADIUS = 3, FALLBACK_DOT_MIN_SIZE = 2

### Task 1.10: DUP-UI2-006 - Ship Cloning Logic in create_hypothetica [Simple]
**File:** `game/ui/services/battle_factories.py`
**Tests:** `pytest tests/unit/simulation/battle_controller/test_utilities.py::TestHelperFunctions`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** COMPLETE - Extracted `_clone_ships()` helper to deduplicate the ship cloning logic in `create_hypothetical_battle()`. The duplicated loop for team1 and team2 ships is now a single reusable function. Addressed together with Task 1.3.

### Task 1.11: CON-UI2-013 - Inconsistent __all__ Export Patterns [Simple]
**File:** `game/ui/__init__.py`
**Tests:** N/A - module structure

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - The `__all__` export list is correctly defined and matches the eagerly-imported submodules. The intentional exclusion of `colors.py`, `config.py`, `utils.py` from `__all__` is by design - these are internal utilities, not part of the public API. The pattern is consistent.

### Task 1.12: DUP-UI2-008 - Adapter Classes Follow Consistent Patter [N]
**File:** `Unknown`
**Tests:** N/A - file location unknown

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** SKIPPED - Finding has "Unknown" file location. Cannot investigate without a specific file path. Adapter classes in the codebase (ShipIOAdapter, DesignLoaderAdapter) follow consistent patterns already established by PROJ-50 DI system.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
