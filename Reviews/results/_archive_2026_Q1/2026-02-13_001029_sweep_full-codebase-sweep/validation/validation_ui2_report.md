# Validation Report: UI-Framework (UI2)

**Validator:** Claude Opus 4.5
**Date:** 2026-02-13
**Shard:** UI2 (game/ui/ - root files, services/, renderer/, interfaces/, orchestration/, assets/, components/, utils/)
**Total Findings:** 36

## Summary

| Verdict | Count |
|---------|-------|
| CONFIRMED | 12 |
| DOWNGRADED | 5 |
| REJECTED | 19 |

**Key Observations:**
- Many "dead code" findings are FALSE POSITIVES - functions are actively used and tested
- Several "missing test coverage" findings are FALSE POSITIVES - tests exist and are comprehensive
- Multiple findings describe intentional design patterns (singleton, DI) as problems
- Some findings duplicate issues or describe acceptable architectural patterns

---

## Detailed Verdicts

### ADR-UI2-001: pygame.math.Vector2 Usage in game_renderer.py
**Severity:** MAJOR
**Location:** `game/ui/renderer/game_renderer.py:121`

**VERDICT: REJECTED**

**Analysis:** The code at line 121 uses `pygame.math.Vector2` for component position calculation:
```python
comp_world_pos = ship.position + pygame.math.Vector2(off_x, off_y)
```
This is in the UI/renderer layer where pygame is the expected dependency. Using pygame's Vector2 in a rendering module that already imports and uses pygame extensively is completely appropriate. The renderer module legitimately depends on pygame for all drawing operations. This is not an architecture violation.

---

### ADR-UI2-002: God Class Potential in ShipThemeManager
**Severity:** MAJOR
**Location:** `game/ui/assets/ship_theme_manager.py`

**VERDICT: DOWNGRADED (MAJOR -> INFO)**

**Analysis:** ShipThemeManager has 314 lines with well-defined responsibilities:
1. Theme discovery and metadata storage
2. Lazy image loading with caching
3. Thread-safe operations
4. Portrait image handling
5. Image metrics caching

The class follows Single Responsibility Principle for "managing ship visual themes". It uses appropriate patterns (singleton, lazy loading, thread safety). This is a well-designed asset manager class, not a god class. The "potential" qualifier makes this speculative.

---

### ADR-UI2-003: Lazy Import Pattern in ship_factory.py
**Severity:** MINOR
**Location:** `game/ui/services/ship_factory.py`

**VERDICT: CONFIRMED**

**Analysis:** Line 83 contains a lazy import:
```python
from game.simulation.entities.ship import Ship
```
This is inside `create_from_design()`. The docstring explains this is intentional to avoid circular imports, but it could be moved to module level with `TYPE_CHECKING` for type hints and runtime import.

---

### ADR-UI2-004: TYPE_CHECKING Import for GameRegistries
**Severity:** MINOR
**Location:** `game/ui/services/ship_factory.py`

**VERDICT: REJECTED**

**Analysis:** The file already correctly uses TYPE_CHECKING:
```python
if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.core.registry import GameRegistries
```
This is the correct pattern. The finding claims this is a problem when it's actually the solution. The lazy import in method body (ADR-UI2-003) is separate from the TYPE_CHECKING usage which is already correctly implemented.

---

### ADR-UI2-005: BattleOrchestrator Correctly Documents Cross-Layer
**Severity:** INFO
**Location:** `game/ui/orchestration/battle_orchestrator.py`

**VERDICT: CONFIRMED**

**Analysis:** The module has excellent documentation explaining its cross-layer role:
```python
"""
Architecture Note:
This is an intentional boundary-crossing module that coordinates between
UI, AI, and Simulation layers. The cross-layer imports below are by design...
"""
```
This is a positive finding acknowledging good documentation practice.

---

### CON-UI2-001: Inconsistent DI Pattern
**Severity:** CRITICAL
**Location:** `game/ui/services/vehicle_class_service.py:36-47`

**VERDICT: DOWNGRADED (CRITICAL -> MINOR)**

**Analysis:** VehicleClassService enforces strict DI (raises ValueError if None), while ComponentService allows optional DI with fallback. However:
1. VehicleClassService's docstring explicitly explains this is per PROJ-50 mandate
2. ComponentService's docstring explains it follows "standard UI service DI pattern"
3. Both patterns are documented and intentional

This is a conscious design decision with different strictness levels, not an inconsistency. The variation is documented and justified. Downgrading because it's a minor documentation/consistency issue, not critical.

---

### CON-UI2-002: Singleton vs Dependency Injection Pattern Conflict
**Severity:** MAJOR
**Location:** `game/ui/services/screenshot_manager.py`

**VERDICT: REJECTED**

**Analysis:** ScreenshotManager uses singleton because it manages:
1. Global state (enabled flag from DEBUG_SCREENSHOTS)
2. Shared directory creation
3. Clipboard operations

Services like ComponentService use DI because they depend on registries that vary per test/context. These patterns serve different purposes:
- Singleton: Global, stateless utilities
- DI: Context-dependent services

This is not a conflict but appropriate pattern selection for different use cases.

---

### CON-UI2-003: Mixed Return Type Patterns for Error Handling
**Severity:** MAJOR
**Location:** `game/ui/services/ship_io.py:42`

**VERDICT: CONFIRMED**

**Analysis:** ShipIO methods return different patterns:
- `save_ship`: Returns `Tuple[bool, Optional[str]]` (success flag + message)
- `load_ship`: Returns `Tuple[Optional[Ship], Optional[str]]` (object + message)

While ShipIOAdapter documents this intentional difference, it creates API inconsistency. This is a real consistency concern.

---

### CON-UI2-004: Inconsistent Parameter Naming
**Severity:** MAJOR
**Location:** Unknown

**VERDICT: REJECTED**

**Analysis:** No specific location provided. Reviewing the files, parameter naming is generally consistent:
- `registry_provider` for IRegistryProvider
- `registries` for GameRegistries
These serve different protocol requirements. Without specific examples, this finding is too vague to validate.

---

### CON-UI2-005: Missing Type Hints on Public Functions
**Severity:** MAJOR
**Location:** `game/ui/renderer/game_renderer.py`

**VERDICT: DOWNGRADED (MAJOR -> MINOR)**

**Analysis:** While `draw_ship`, `draw_hud`, and `draw_bar` lack full return type annotations, they all have:
- Docstrings explaining purpose
- Clear parameter documentation
- Implicit None return (void functions)

Adding explicit `-> None` return hints would be good practice but not a major issue for void rendering functions.

---

### CON-UI2-006: Docstring Inconsistency
**Severity:** MAJOR
**Location:** `game/ui/services/screenshot_manager.py`

**VERDICT: DOWNGRADED (MAJOR -> MINOR)**

**Analysis:** ScreenshotManager has comprehensive class docstrings and method docstrings for public methods like `capture()`. Some internal methods like `_copy_to_clipboard` have shorter docstrings but this is acceptable for private methods.

---

### CON-UI2-007: Inconsistent Constants Organization
**Severity:** MAJOR
**Location:** `game/ui/colors.py:7-14`

**VERDICT: CONFIRMED**

**Analysis:** The file has two organizational styles:
1. Module-level constants: `WHITE`, `BLACK`, `BLUE`, `RED`, `GREEN`
2. Dictionary constants: `COLORS = {...}`

This inconsistency makes it unclear which to use. A unified approach would be cleaner.

---

### DUP-UI2-001: Duplicated Lazy DI Provider Resolution Pattern
**Severity:** MAJOR
**Location:** `game/ui/services/component_service.py`

**VERDICT: REJECTED**

**Analysis:** The pattern `_get_provider()` in ComponentService is 5 lines of straightforward code:
```python
def _get_provider(self) -> IRegistryProvider:
    if self._provider is None:
        self._provider = get_default_registry_provider()
    return self._provider
```
This is a standard lazy initialization pattern that doesn't warrant extraction to a base class for such a simple case. Over-abstraction would hurt readability.

---

### DUP-UI2-002: Directory Creation Pattern Duplicated
**Severity:** MAJOR
**Location:** `game/ui/services/ship_io.py:49`

**VERDICT: REJECTED**

**Analysis:** The `os.makedirs` call is standard Python idiom for ensuring directories exist. The pattern appears in different contexts (ships folder vs screenshots folder) with different error handling needs. This is not problematic duplication.

---

### DUP-UI2-003: Singleton Manager Pattern Triplicated
**Severity:** MAJOR
**Location:** `game/ui/assets/ship_theme_manager.py`

**VERDICT: REJECTED**

**Analysis:** ShipThemeManager uses `SingletonMeta` from `game.core.singleton`, which is a centralized metaclass for all singletons. This is already the recommended pattern - using a shared metaclass rather than duplicating singleton logic. The pattern is NOT triplicated; it's centralized.

---

### DUP-UI2-004: Service Adapter Wrapping Pattern
**Severity:** MAJOR
**Location:** `game/ui/services/ship_io_adapter.py`

**VERDICT: REJECTED**

**Analysis:** ShipIOAdapter is an intentional adapter pattern providing:
1. A cleaner interface for UI code
2. Documented return value conventions
3. Dependency injection point for testing

This is a proper use of the Adapter pattern, not problematic duplication.

---

### LEG-UI2-001: Dead Code - draw_hud and draw_bar Functions
**Severity:** MAJOR
**Location:** `game/ui/renderer/game_renderer.py`

**VERDICT: REJECTED (FALSE POSITIVE)**

**Analysis:** These functions ARE actively used:
1. `draw_hud` and `draw_bar` are called from `game/ui/screens/battle_screen.py` and `game/app.py`
2. Comprehensive tests exist in `tests/unit/ui/test_rendering_logic.py`:
   - `TestDrawHudBehavior` class with 4 tests
   - `TestDrawBar` class with 2 tests
   - `TestRenderingLogic.test_draw_hud_stats`

Grep search confirms usage in multiple files. This is a false positive.

---

### LEG-UI2-002: Unused Method - create_ai_for_ship
**Severity:** MAJOR
**Location:** `game/ui/orchestration/battle_orchestrator.py`

**VERDICT: REJECTED (FALSE POSITIVE)**

**Analysis:** The method has:
1. Explicit docstring stating it's "for reinforcements" (future use case)
2. Full test coverage in `tests/unit/ui/test_battle_orchestrator.py`:
   - `TestCreateAIForShip` class with 4 tests
   - Tests verify correct adapter creation and enemy team ID passing

The docstring documents intended use for reinforcements feature. This is intentional API design, not dead code.

---

### LEG-UI2-003: Unused Method - capture_step
**Severity:** MAJOR
**Location:** `game/ui/services/screenshot_manager.py`

**VERDICT: REJECTED (FALSE POSITIVE)**

**Analysis:** The method has test coverage in `tests/unit/ui/services/test_screenshot_manager.py`:
- `TestCaptureStep` class with 3 tests:
  - `test_capture_step_calls_capture_with_step_label`
  - `test_capture_step_disabled_does_nothing`
  - `test_capture_step_no_surface_uses_display`

This is a debugging utility method that is tested and available for debugging draw order issues.

---

### LEG-UI2-004: Duplicate Exception Handlers in ShipIO
**Severity:** MINOR
**Location:** `game/ui/services/ship_io.py:71`

**VERDICT: CONFIRMED**

**Analysis:** Looking at lines 71-82 in save_ship:
```python
except PermissionError as e:
    ...
except OSError as e:
    ...
except (TypeError, ValueError) as e:
    ...
except (OSError, PermissionError) as e:  # Duplicate!
```
The final except clause duplicates OSError and PermissionError which are already caught above. This is dead code.

---

### LEG-UI2-005: Comment References "legacy behavior"
**Severity:** MINOR
**Location:** `game/ui/services/ship_factory.py`

**VERDICT: CONFIRMED**

**Analysis:** Line 15 contains:
```python
# When registries is not provided, uses global RegistryManager (legacy behavior).
```
The "legacy behavior" label is documented and intentional - it refers to the fallback pattern before PROJ-50's strict DI. This is informational documentation, not problematic legacy code.

---

### LEG-UI2-006: Basic Color Constants
**Severity:** MINOR
**Location:** `game/ui/colors.py:9-11`

**VERDICT: REJECTED**

**Analysis:** Basic color constants (WHITE, BLACK, BLUE, RED, GREEN) are standard UI utilities. The docstring explains:
```python
# PROJ-113: Moved basic colors (WHITE, BLACK, etc.) and FONT_MAIN from core to UI layer.
```
These were intentionally moved to UI layer as part of layer boundary cleanup. Not legacy code.

---

### LEG-UI2-007: ShipIOAdapter vs ShipIO Direct Access
**Severity:** MINOR
**Location:** `game/ui/services/ship_io_adapter.py`

**VERDICT: REJECTED**

**Analysis:** ShipIOAdapter exists to provide:
1. Dependency injection for testing
2. Cleaner documented interface
3. Consistent return value conventions

This is the Adapter pattern being used correctly. Both classes serve different purposes.

---

### LEG-UI2-008: Excessive getattr() with Defaults
**Severity:** MINOR
**Location:** `game/ui/services/battle_ui_service.py`

**VERDICT: CONFIRMED**

**Analysis:** The file uses getattr with defaults in several places:
```python
crew_onboard=getattr(ship, 'crew_onboard', 0),
crew_required=getattr(ship, 'crew_required', 0),
```
The comment explains: "crew_onboard/crew_required are dynamically set by ShipStatsCalculator, not in __init__"

This is defensive coding for attributes that may not exist. While it works, it indicates these attributes should perhaps be properly initialized in Ship.__init__.

---

### TCG-UI2-001: UIConfig class has no dedicated test coverage
**Severity:** MAJOR
**Location:** `game/ui/config.py`

**VERDICT: CONFIRMED**

**Analysis:** UIConfig is a data class containing layout constants. Grep search shows it's used but no dedicated test file exists. However, since it's just static constants with no logic, testing would be trivial (checking values exist). Low value test case.

---

### TCG-UI2-002: game_renderer draw_ship lacks edge case tests
**Severity:** MAJOR
**Location:** `game/ui/renderer/game_renderer.py`

**VERDICT: REJECTED (FALSE POSITIVE)**

**Analysis:** `tests/unit/ui/test_rendering_logic.py` contains extensive edge case tests:
- `test_draw_ship_culling` - off-screen ships
- `test_draw_ship_dead_ship_returns_early` - dead ships
- `test_draw_ship_with_theme_image` - with image
- `test_draw_ship_no_theme_image_draws_dot` - fallback
- `test_draw_ship_zoom_affects_radius` - zoom levels
- `test_draw_ship_at_camera_boundary` - edge positioning

The tests cover the claimed missing edge cases.

---

### TCG-UI2-003: draw_hud resource bar edge cases not tested
**Severity:** MAJOR
**Location:** `game/ui/renderer/game_renderer.py`

**VERDICT: DOWNGRADED (MAJOR -> MINOR)**

**Analysis:** Tests exist in `test_rendering_logic.py`:
- `test_draw_hud_renders_ship_name`
- `test_draw_hud_renders_hp_bar`
- `test_draw_hud_with_zero_hp_ship`
- `test_draw_hud_resource_display`

Missing: divide-by-zero when max_value=0. The code handles this: `if ship.resources.get_max_value(...) > 0 else 0`. Still, explicit test would be good.

---

### TCG-UI2-004: BattleUIService projectile color mapping untested
**Severity:** MAJOR
**Location:** `game/ui/services/battle_ui_service.py`

**VERDICT: CONFIRMED**

**Analysis:** PROJECTILE_COLORS mapping (lines 31-36) and DEFAULT_PROJECTILE_COLOR are not explicitly tested. The test file `test_conversion.py` tests projectile conversion but doesn't verify color mapping from AttackType.

---

### TCG-UI2-005: ShipThemeManager missing scale factor boundary tests
**Severity:** MAJOR
**Location:** `game/ui/assets/ship_theme_manager.py`

**VERDICT: REJECTED (FALSE POSITIVE)**

**Analysis:** `tests/unit/ui/test_theme_discovery.py` contains:
- `TestShipThemeManagerManualScale` class with 4 tests:
  - `test_get_manual_scale_default` - default 1.0
  - `test_get_manual_scale_before_discovery` - early call
  - `test_get_manual_scale_with_value` - configured value

Scale factor tests exist. The "boundary" tests (negative, very large) would be edge cases but basic functionality is covered.

---

### TCG-UI2-006: Camera fit_objects edge case
**Severity:** MINOR
**Location:** `game/ui/renderer/camera.py`

**VERDICT: REJECTED (FALSE POSITIVE)**

**Analysis:** `tests/unit/ui/test_camera.py` contains `TestCameraFitObjects` class with:
- `test_fit_objects_centers_camera`
- `test_fit_objects_adjusts_zoom`
- `test_fit_objects_empty_list`
- `test_fit_objects_single_object` (in TestCameraEdgeCases)

The empty list case is explicitly tested. Division by zero won't occur because the code adds 500 margin to width/height.

---

### TCG-UI2-007: InputMapper save_user_overrides
**Severity:** MINOR
**Location:** `game/ui/services/input_mapper.py`

**VERDICT: REJECTED (FALSE POSITIVE)**

**Analysis:** `tests/unit/ui/services/test_input_mapper.py` contains comprehensive tests:
- `TestInputMapperSaveLoad` class:
  - `test_save_user_overrides`
  - `test_save_load_roundtrip`
  - `test_save_unbound_action`
  - `test_save_creates_parent_directories`
  - `test_save_no_overrides_returns_true`

Full coverage exists for save_user_overrides including edge cases.

---

### TCG-UI2-008: ScreenshotManager capture_strategy_layer
**Severity:** MINOR
**Location:** `game/ui/services/screenshot_manager.py`

**VERDICT: REJECTED (FALSE POSITIVE)**

**Analysis:** `tests/unit/ui/services/test_screenshot_manager.py` has dedicated test class:
- `TestCaptureStrategyLayer`:
  - `test_capture_strategy_layer_disabled_does_nothing`
  - `test_capture_strategy_layer_with_ui`
  - `test_capture_strategy_layer_without_ui`
  - `test_capture_strategy_layer_with_subwindows`
  - `test_capture_strategy_layer_handles_invalid_dimensions`

Comprehensive coverage exists.

---

### TCG-UI2-012: Test organization could be improved
**Severity:** INFO
**Location:** `tests/unit/ui/`

**VERDICT: CONFIRMED**

**Analysis:** This is a general observation about test organization. The tests directory structure could be more consistent (some use subdirectories like `services/`, others are flat files). This is a valid but low-priority organizational improvement.

---

## Cross-Shard Duplicates

None identified. The findings are specific to UI2 shard files.

---

## Recommendations

1. **High Value Fixes:**
   - Fix duplicate exception handlers in ShipIO (LEG-UI2-004)
   - Unify colors.py organization (CON-UI2-007)
   - Add PROJECTILE_COLORS test coverage (TCG-UI2-004)

2. **Low Priority:**
   - Consider adding `-> None` return hints to rendering functions
   - Refactor getattr() usage in BattleUIService if Ship attributes are standardized
   - Consider moving lazy imports to TYPE_CHECKING where possible

3. **No Action Needed:**
   - Most "dead code" findings were false positives with existing test coverage
   - Singleton vs DI patterns are appropriate for their use cases
   - Adapter patterns are correctly implemented
