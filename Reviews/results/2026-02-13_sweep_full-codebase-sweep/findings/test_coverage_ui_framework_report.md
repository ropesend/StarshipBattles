# Test Coverage Gaps Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Production Files Scanned:** 24 files (root files, services/, renderer/, interfaces/, orchestration/, assets/)
- **Test Files Cross-Referenced:** 38 files
- **Total Issues Found:** 12
- **Critical:** 0 | **Major:** 5 | **Minor:** 6 | **Info:** 1

## Scope Analysis

### Production Files Analyzed (game/ui/):
| File | Test Coverage Status |
|------|---------------------|
| `utils.py` | Well tested (test_utils.py) |
| `config.py` | **No dedicated test file** |
| `colors.py` | Tested (test_colors.py) |
| `services/validation_service.py` | Tested (test_validation_service.py) |
| `services/vehicle_class_service.py` | Tested (test_vehicle_class_service.py) |
| `services/component_service.py` | Tested (test_component_service.py) |
| `services/ship_factory.py` | Tested (test_ship_factory.py) |
| `services/screenshot_manager.py` | Tested (test_screenshot_manager.py) |
| `services/design_loader_adapter.py` | Tested (test_design_loader_adapter.py) |
| `services/input_mapper.py` | Well tested (test_input_mapper.py) |
| `services/ship_io.py` | Comprehensively tested (test_ship_io.py) |
| `services/ship_io_adapter.py` | Tested (test_ship_io_adapter.py) |
| `services/battle_ui_service.py` | Well tested (test_conversion.py, test_state_and_integration.py) |
| `renderer/game_renderer.py` | Tested (test_rendering_logic.py) |
| `renderer/camera.py` | Well tested (test_camera.py) |
| `renderer/sprites.py` | Tested (test_sprites.py) |
| `interfaces/battle_ui.py` | Tested (test_battle_ui.py) |
| `orchestration/battle_orchestrator.py` | Tested (test_battle_orchestrator.py) |
| `assets/ship_theme_manager.py` | Well tested (test_theme_discovery.py) |

## Findings

#### MAJOR: UIConfig class has no dedicated test coverage
**ID:** TCG-UI2-001
**Location:** `game/ui/config.py` (production) / `tests/unit/ui/test_config.py` (missing)
**Issue:** The UIConfig class contains 18 layout/sizing constants (PANEL_PADDING, TOAST_WIDTH, STATS_PANEL_WIDTH, etc.) but has no dedicated unit tests validating these constants exist and have reasonable values.
**Impact:** Constants could be accidentally modified without test failures; no regression protection for UI layout values.
**Recommendation:** Create `tests/unit/ui/test_config.py` with tests verifying all UIConfig constants exist, have correct types (int), and reasonable ranges. Include tests for constant relationships (e.g., TOAST_HEIGHT < CONFIRM_DIALOG_HEIGHT).
**Effort:** Simple

#### MAJOR: game_renderer draw_ship lacks edge case tests
**ID:** TCG-UI2-002
**Location:** `game/ui/renderer/game_renderer.py` (production) / `tests/unit/ui/test_rendering_logic.py` (undertested)
**Issue:** The draw_ship function handles several edge cases that lack explicit test coverage:
- Ship with radius=0 or negative radius
- Ship with position containing NaN or Infinity
- Ship with missing theme_id attribute
- Ship with very large radius causing overflow in screen coordinates
- Overlay mode with components that have broken has_ability method
**Impact:** Edge cases could cause crashes or visual glitches in battle rendering without detection.
**Recommendation:** Add parameterized tests for boundary conditions: zero/negative radius, extreme positions, missing attributes, and malformed component data.
**Effort:** Medium

#### MAJOR: draw_hud resource bar edge cases not tested
**ID:** TCG-UI2-003
**Location:** `game/ui/renderer/game_renderer.py:draw_hud` / `tests/unit/ui/test_rendering_logic.py`
**Issue:** draw_hud calls resource methods but doesn't test:
- Division by zero when max_value is 0 (currently would return 0 but not tested)
- Negative resource values
- Resources returning None instead of numeric values
- Missing layers in ship.layers dictionary
**Impact:** Ships with malformed resource data could crash the HUD rendering.
**Recommendation:** Add tests for resource edge cases: zero max values, negative values, missing resources, and empty/partial layers dict.
**Effort:** Medium

#### MAJOR: BattleUIService projectile color mapping lacks boundary tests
**ID:** TCG-UI2-004
**Location:** `game/ui/services/battle_ui_service.py` / `tests/unit/ui/services/battle_ui_service/test_conversion.py`
**Issue:** The PROJECTILE_COLORS mapping and _convert_projectile method are tested for basic cases but lack:
- Test for unknown AttackType falling back to DEFAULT_PROJECTILE_COLOR
- Test for projectile with None type attribute
- Test for projectile missing expected attributes (radius, hp, max_hp, endurance)
**Impact:** Projectiles with unexpected types or missing attributes could render with wrong colors or cause attribute errors.
**Recommendation:** Add tests verifying DEFAULT_PROJECTILE_COLOR is used for unknown types, and that defensive getattr fallbacks work correctly.
**Effort:** Simple

#### MAJOR: ShipThemeManager missing scale factor boundary tests
**ID:** TCG-UI2-005
**Location:** `game/ui/assets/ship_theme_manager.py` / `tests/unit/ui/test_theme_discovery.py`
**Issue:** get_manual_scale() returns scale values from theme.json but tests don't verify:
- Negative scale values (should be rejected or clamped)
- Scale of 0 (would cause image to disappear)
- Very large scale values (>10.0) that could cause memory issues
- Non-numeric scale values in JSON
**Impact:** Malformed theme.json files with bad scale values could cause rendering issues or crashes.
**Recommendation:** Add validation tests for scale value boundaries and tests for graceful handling of invalid JSON scale values.
**Effort:** Simple

#### MINOR: Camera fit_objects edge case with dead targets
**ID:** TCG-UI2-006
**Location:** `game/ui/renderer/camera.py` / `tests/unit/ui/test_camera.py`
**Issue:** fit_objects() is tested with live objects but not with:
- Mix of alive and dead objects
- Objects with None or missing position attribute
- Objects with position containing NaN values
**Impact:** Low - function may behave unexpectedly with edge case inputs.
**Recommendation:** Add edge case tests for fit_objects with mixed object states and invalid positions.
**Effort:** Simple

#### MINOR: InputMapper save_user_overrides file permission error handling
**ID:** TCG-UI2-007
**Location:** `game/ui/services/input_mapper.py` / `tests/unit/ui/services/test_input_mapper.py`
**Issue:** While save/load roundtrip tests exist, there's no explicit test for:
- save_user_overrides when parent directory exists but is read-only
- save_user_overrides when disk is full
- Concurrent calls to save_user_overrides
**Impact:** Low - file system edge cases could cause silent failures.
**Recommendation:** Add tests for permission errors and IO exceptions during save operations.
**Effort:** Simple

#### MINOR: ScreenshotManager capture_strategy_layer subwindow rendering order
**ID:** TCG-UI2-008
**Location:** `game/ui/services/screenshot_manager.py` / `tests/unit/ui/services/test_screenshot_manager.py`
**Issue:** capture_strategy_layer tests verify subwindows are drawn when include_subwindows=True, but don't verify:
- Rendering order (UI elements should be on top of background)
- Behavior when subwindow.draw() raises an exception
- Multiple subwindows being captured
**Impact:** Low - screenshot ordering issues would be visually obvious but not caught by tests.
**Recommendation:** Add tests verifying draw call order using mock call inspection.
**Effort:** Simple

#### MINOR: BattleOrchestrator lacks tests for AI controller failure scenarios
**ID:** TCG-UI2-009
**Location:** `game/ui/orchestration/battle_orchestrator.py` / `tests/unit/ui/test_battle_orchestrator.py`
**Issue:** Tests verify normal AI controller creation but don't test:
- What happens if AIController constructor raises an exception
- What happens if ShipControllableAdapter rejects a malformed ship
- Creating AI for a ship with enemy_team_id matching its own team_id
**Impact:** Low - AI creation failures would crash battle setup.
**Recommendation:** Add tests for error propagation from AIController and adapter construction.
**Effort:** Simple

#### MINOR: SpriteManager thread safety tests are limited
**ID:** TCG-UI2-010
**Location:** `game/ui/renderer/sprites.py` / `tests/unit/ui/test_sprites.py`
**Issue:** Thread safety tests verify concurrent instance() calls return same singleton, but don't test:
- Concurrent calls to reset() and instance()
- Concurrent get_sprite() calls during load_sprites()
**Impact:** Low - race conditions in sprite loading could cause inconsistent state.
**Recommendation:** Add stress tests for singleton reset races and concurrent access patterns.
**Effort:** Medium

#### MINOR: colors.py basic constants not tested
**ID:** TCG-UI2-011
**Location:** `game/ui/colors.py` / `tests/unit/ui/test_colors.py`
**Issue:** test_colors.py tests the COLORS dictionary but not the basic color constants (WHITE, BLACK, BLUE, RED, GREEN) or FONT_MAIN.
**Impact:** Low - basic constants are simple but could be accidentally modified.
**Recommendation:** Add tests verifying basic color constants exist and have expected RGB values, and FONT_MAIN is a valid string.
**Effort:** Simple

#### INFO: Test organization could be improved
**ID:** TCG-UI2-012
**Location:** `tests/unit/ui/` directory structure
**Issue:** Some test files are in `tests/unit/ui/` root while their corresponding production files are in subdirectories (e.g., `test_rendering_logic.py` tests `renderer/game_renderer.py`). Consider organizing tests to mirror production structure more closely.
**Impact:** None - organizational suggestion only.
**Recommendation:** Consider creating `tests/unit/ui/renderer/test_game_renderer.py` to mirror `game/ui/renderer/game_renderer.py` structure.
**Effort:** Complex (would require moving many test files)

## Top 5 Priority Issues

1. **TCG-UI2-001 (MAJOR):** UIConfig class lacks test coverage - Critical layout constants have no regression protection.

2. **TCG-UI2-002 (MAJOR):** draw_ship edge cases - Battle rendering could crash on malformed ship data without detection.

3. **TCG-UI2-003 (MAJOR):** draw_hud resource edge cases - Division by zero and missing data scenarios untested.

4. **TCG-UI2-004 (MAJOR):** Projectile color mapping boundaries - Unknown attack types and missing attributes could cause rendering issues.

5. **TCG-UI2-005 (MAJOR):** ShipThemeManager scale validation - Invalid scale values in theme.json could cause memory issues or invisible ships.

## Summary of Test Quality

The UI-Framework shard has **good overall test coverage** with most production files having corresponding test files. The test suite includes:
- Strong singleton pattern testing (SpriteManager, ShipThemeManager, ScreenshotManager)
- Good integration tests using real domain objects (BattleUIService)
- Comprehensive round-trip serialization tests (ShipIO)
- Thorough input handling tests (InputMapper)

**Areas for improvement:**
- Edge case coverage for rendering functions (draw_ship, draw_hud)
- Boundary value testing for configuration constants
- Error path testing for file operations
- Thread safety stress testing

**Coverage estimate:** ~85% of public APIs have some test coverage, but edge case coverage averages ~60%.
