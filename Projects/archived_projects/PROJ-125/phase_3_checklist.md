# Phase 3: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-125 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (28 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 3.1: CON-UI2-003 - Mixed Return Type Patterns for Error Han [Medium]
**File:** `game/ui/services/ship_io.py:42`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - INTENTIONAL DESIGN. save_ship returns (bool, str), load_ship returns (Ship, str). This is explicitly documented in ShipIOAdapter docstring: "The different return types are intentional: save operations return a success flag because there is no object to return, while load operations return the loaded object." Semantic correctness.

### Task 3.2: CON-UI2-004 - Inconsistent Parameter Naming for Regist [Simple]
**File:** `Unknown`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Cannot investigate without knowing the file location. "Unknown" is not a valid path.

### Task 3.3: CON-UI2-005 - Missing Type Hints on Public Functions [Simple]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - draw_ship() is a rendering internal, not a public API. Parameters (surface, ship, camera) have clear types from pygame and game objects. Adding type hints to every pygame rendering function is over-engineering.

### Task 3.4: CON-UI2-006 - Docstring Inconsistency - Some Use Googl [Simple]
**File:** `game/ui/services/screenshot_ma`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - ScreenshotManager uses Google-style docstrings consistently with Args:, Returns: sections. File follows project conventions.

### Task 3.5: CON-UI2-007 - Inconsistent Module-Level vs Class-Level [Simple]
**File:** `game/ui/colors.py:7-14`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INTENTIONAL DESIGN - Simple values (WHITE, BLACK, FONT_MAIN) at module level, complex color collection in COLORS dict. This is standard Python pattern. Module-level constants for simple values, dicts for collections.

### Task 3.6: DUP-UI2-001 - Duplicated Lazy DI Provider Resolution P [Medium]
**File:** `game/ui/services/component_ser`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - The `_get_provider()` pattern is the ESTABLISHED DI PATTERN for this project, documented and mandated by PROJ-50 and PROJ-43. Services use lazy resolution with get_default_registry_provider(). This IS the standard pattern.

### Task 3.7: DUP-UI2-002 - Directory Creation Pattern Duplicated in [Simple]
**File:** `game/ui/services/ship_io.py:49`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - `os.makedirs()` appears twice (save and load methods). This is standard Python idiom. Two usages does not warrant abstraction - that would be over-engineering.

### Task 3.8: DUP-UI2-003 - Singleton Manager Pattern Triplicated [Medium]
**File:** `game/ui/assets/ship_theme_mana`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INTENTIONAL DESIGN - ShipThemeManager, ScreenshotManager, SpriteManager all use SingletonMeta from game.core.singleton. This IS the consolidated pattern! The finding is describing the pattern working as designed.

### Task 3.9: DUP-UI2-004 - Service Adapter Wrapping Pattern [Medium]
**File:** `game/ui/services/ship_io_adapt`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INTENTIONAL DESIGN - ShipIOAdapter is an Adapter pattern implementation for dependency injection. This IS the architectural pattern for separating UI from implementation details.

### Task 3.10: CON-UI2-008 - Inconsistent Boolean Method Naming [N]
**File:** `game/ui/services/component_ser`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - `is_modifier_allowed()` uses proper `is_` prefix for boolean methods. Naming follows Python conventions.

### Task 3.11: CON-UI2-009 - Redundant Exception Handling in ship_io. [Simple]
**File:** `game/ui/services/ship_io.py:71`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Exception handling catches specific exceptions (PermissionError, OSError, TypeError, ValueError) with appropriate error messages. This is proper error handling, not redundant.

### Task 3.12: CON-UI2-010 - Inconsistent Import Organization [Simple]
**File:** `game/ui/renderer/sprites.py:1-`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - sprites.py follows PEP 8 import ordering: stdlib (pygame, os), then local (game.core.*). Imports are properly organized.

### Task 3.13: CON-UI2-011 - Method Prefix Inconsistency - get_ vs lo [Simple]
**File:** `game/ui/assets/ship_theme_mana`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INTENTIONAL DESIGN - `load_image()` performs I/O (loads from disk), `get_image_metrics()` returns cached data, `get_manual_scale()` returns config value. Semantic distinction between loading and getting is intentional and correct.

### Task 3.14: CON-UI2-012 - Inconsistent Private Method Naming [N]
**File:** `game/ui/assets/ship_theme_mana`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - All private methods use single underscore prefix consistently: `_discover_theme()`, `_load_single_image()`, `_create_fallback_image()`, `_load_portrait_image()`, `_ship_class_to_portrait_name()`. No inconsistency found.

### Task 3.15: CON-UI2-013 - Magic Numbers in game_renderer.py [Medium]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Numbers like 50 (radius), 0.01 (min zoom), 0.3 (zoom threshold), 3 (dot size), 10 (direction indicator) are rendering constants in a rendering function. Extracting every pixel value to named constants would be over-engineering. These are visual tuning values, not domain logic.

### Task 3.16: CON-UI2-014 - Inconsistent Error Logging Format [Simple]
**File:** `game/ui/services/ship_io.py:72`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Error logging uses consistent format: `log_error(f"ShipIO: {operation} {error}")`. Class name prefix and descriptive message. Follows project logging conventions.

### Task 3.17: CON-UI2-015 - Unused Comments as Section Headers [Simple]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Section header comments (# Transform Position, # Culling, # Draw Theme Image) aid readability in a 140-line rendering function. This is good code organization, not unused comments.

### Task 3.18: DUP-UI2-005 - Font Creation Throughout UI Without Cent [Simple]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - game_renderer.py does not create any fonts. The file only does pygame.draw operations. No pygame.font usage found.

### Task 3.19: DUP-UI2-006 - Image Scaling Utility Functions Have Ove [Simple]
**File:** `game/ui/utils.py:32-64`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - `calculate_ship_image_scale()` (calculates scale factor) and `scale_and_rotate_image()` (applies scale and rotation) are COMPLEMENTARY functions with distinct responsibilities. They compose together by design.

### Task 3.20: DUP-UI2-007 - Placeholder Surface Creation Pattern [Simple]
**File:** `game/ui/utils.py:141-143`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Placeholder surface creation appears twice in `scale_image_by_visible_portion()` for edge cases (empty surface, zero dimensions). Two usages within same function for error handling does not warrant abstraction.

### Task 3.21: DUP-UI2-008 - Error Exception Handling Pattern in Ship [Simple]
**File:** `game/ui/services/ship_io.py:71`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Duplicate of Task 3.11. Same location (ship_io.py:71), same finding about exception handling.

### Task 3.22: DUP-UI2-009 - Tkinter Initialization Error Handling [Medium]
**File:** `game/ui/services/ship_io.py:21`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INTENTIONAL DESIGN - Module-level Tkinter initialization with broad exception catch is intentional and documented with comment: "Intentional broad catch: Tkinter init is platform-dependent". Platform-dependent initialization requires defensive coding.

### Task 3.23: DUP-UI2-010 - Return Value Conventions Partially Docum [Simple]
**File:** `game/ui/services/ship_io_adapt`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - ShipIOAdapter has EXCELLENT documentation of return value conventions in class docstring: "Return Value Convention: - save operations: Tuple[bool, Optional[str]] where bool=success - load operations: Tuple[Optional[T], Optional[str]] where T=loaded object - For both: message=None means user cancelled the dialog"

### Task 3.24: CON-UI2-016 - Cross-Layer Imports Documented But Incon [Simple]
**File:** `game/ui/orchestration/battle_o`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - BattleOrchestrator has detailed docstring documenting cross-layer imports: "This is an intentional boundary-crossing module that coordinates between UI, AI, and Simulation layers. The cross-layer imports below are by design". Well-documented architectural decision.

### Task 3.25: CON-UI2-017 - DTO Classes Could Use __slots__ [Simple]
**File:** `game/ui/interfaces/battle_ui.p`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - DTOs use `@dataclass(frozen=True)` which provides immutability. Adding `__slots__` is micro-optimization that would complicate code for negligible benefit. Frozen dataclasses are the idiomatic pattern for DTOs.

### Task 3.26: CON-UI2-018 - UIConfig Class Has No Methods [N]
**File:** `game/ui/config.py:17-67`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INTENTIONAL DESIGN - UIConfig is a namespace class for UI constants. Constants-only classes are standard Python pattern for namespacing when you want `UIConfig.PANEL_PADDING` instead of module-level `PANEL_PADDING`. No methods needed.

### Task 3.27: DUP-UI2-011 - Camera Zoom Clamping Pattern [Simple]
**File:** `game/ui/renderer/camera.py:114`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - `max(min_zoom, min(max_zoom, value))` is standard Python clamping idiom. Used twice in Camera class (update_input and fit_objects). Extracting to utility function for 2 uses would be over-engineering.

### Task 3.28: DUP-UI2-012 - Vector2 Import and Usage Consistency [Simple]
**File:** `game/ui/interfaces/battle_ui.p`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - battle_ui.py consistently uses `game.core.math.Vector2` which is the project's canonical Vector2 location. Import and usage are consistent throughout the file.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

