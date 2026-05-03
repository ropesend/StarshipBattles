# Test Coverage Gaps Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Production Files Scanned:** 20
- **Test Files Cross-Referenced:** 16
- **Total Issues Found:** 15
- **Critical:** 1 | **Major:** 6 | **Minor:** 5 | **Info:** 3

## Scope Coverage

### Production Files Analyzed
| File | Has Test File | Coverage Level |
|------|--------------|----------------|
| `game/ui/__init__.py` | No | Module init only |
| `game/ui/utils.py` | Yes | Good |
| `game/ui/config.py` | No | Constants only |
| `game/ui/colors.py` | Yes | Good |
| `game/ui/services/__init__.py` | No | Module init only |
| `game/ui/services/validation_service.py` | Yes | Good |
| `game/ui/services/vehicle_class_service.py` | Yes | Good |
| `game/ui/services/component_service.py` | Yes | Good |
| `game/ui/services/ship_factory.py` | Yes | Good |
| `game/ui/services/design_loader_adapter.py` | Yes | Good |
| `game/ui/services/ship_io_adapter.py` | No | **MAJOR GAP** |
| `game/ui/services/ship_io.py` | Yes | Comprehensive |
| `game/ui/services/battle_ui_service.py` | Yes | Comprehensive |
| `game/ui/services/screenshot_manager.py` | Yes | Good |
| `game/ui/services/input_mapper.py` | Yes | Comprehensive |
| `game/ui/renderer/__init__.py` | No | Module init only |
| `game/ui/renderer/camera.py` | Yes | Good |
| `game/ui/renderer/sprites.py` | Yes | Good |
| `game/ui/renderer/game_renderer.py` | No | **CRITICAL GAP** |
| `game/ui/interfaces/__init__.py` | No | Module init only |
| `game/ui/interfaces/battle_ui.py` | Yes (via service tests) | Good |
| `game/ui/orchestration/battle_orchestrator.py` | Yes | Good |
| `game/ui/assets/ship_theme_manager.py` | Yes | Comprehensive |

## Findings

#### CRITICAL: game_renderer.py Has No Test Coverage
**ID:** TCG-UI2-001
**Location:** `game/ui/renderer/game_renderer.py` (production) / No test file exists
**Issue:** The `draw_ship()` function in game_renderer.py has no unit tests. This is a critical rendering function that:
- Handles ship visibility culling
- Scales ship images based on zoom
- Draws theme images with rotation
- Renders collision overlays and layer boundaries
- Draws component positions for each layer
- Falls back to simple dots when no image available
**Impact:** Rendering bugs could go undetected, causing visual glitches or crashes. Layer boundary calculations, culling logic, and image scaling are untested.
**Recommendation:** Create `tests/unit/ui/renderer/test_game_renderer.py` with tests for:
- `draw_ship()` with various zoom levels (0.01, 0.3, 1.0, 2.0)
- Culling logic (ship outside viewport should not draw)
- Overlay mode rendering
- Image fallback when theme image is None
- Component visualization at different zoom thresholds
**Effort:** Medium

#### MAJOR: ShipIOAdapter Has No Dedicated Tests
**ID:** TCG-UI2-002
**Location:** `game/ui/services/ship_io_adapter.py` (production) / No test file exists
**Issue:** ShipIOAdapter is an adapter that wraps ShipIO but has no dedicated unit tests. While ShipIO itself is well-tested, the adapter layer is untested.
**Impact:** Changes to the adapter could break UI code that depends on it without test failures.
**Recommendation:** Create `tests/unit/ui/services/test_ship_io_adapter.py` testing:
- Constructor with default ShipIO injection
- Constructor with custom ShipIO class injection (DI)
- `set_ships_folder()` and `get_ships_folder()` methods
- `save_ship()` delegation
- `load_ship()` delegation
**Effort:** Simple

#### MAJOR: UIConfig Has No Tests
**ID:** TCG-UI2-003
**Location:** `game/ui/config.py` (production) / No test file exists
**Issue:** UIConfig contains layout constants that are used throughout the UI. While these are constants, there are no validation tests.
**Impact:** Invalid constant values (e.g., negative dimensions) could cause runtime errors. No regression protection if constants change.
**Recommendation:** Create `tests/unit/ui/test_config.py` with tests validating:
- All dimension constants are positive integers
- All alpha values are in range [0, 255]
- Related constants have sensible relationships (e.g., HEADER_HEIGHT < SIDEBAR_WIDTH)
**Effort:** Simple

#### MAJOR: Camera Tests Missing Edge Cases for offset_x/offset_y Construction
**ID:** TCG-UI2-004
**Location:** `game/ui/renderer/camera.py` (production) / `tests/unit/ui/test_camera.py`
**Issue:** Camera tests cover basic operations but lack tests for:
- Negative offset values
- Very large offset values
- Offset values larger than viewport dimensions
**Impact:** Edge cases could cause coordinate transformation bugs.
**Recommendation:** Add tests for:
- `Camera(800, 600, offset_x=-100, offset_y=-50)` construction
- Offset values exceeding screen dimensions
- Zero-dimension handling (`Camera(0, 0)` should not crash or divide by zero)
**Effort:** Simple

#### MAJOR: DesignLoaderAdapter Missing Error Path Tests
**ID:** TCG-UI2-005
**Location:** `game/ui/services/design_loader_adapter.py` (production) / `tests/unit/ui/services/test_design_loader_adapter.py`
**Issue:** Tests exist but miss error handling scenarios:
- Invalid design data (missing required fields)
- File not found errors
- Malformed JSON in design file
- Registry lookup failures
**Impact:** Error handling paths are untested.
**Recommendation:** Add tests for:
- `load_ship_from_design_data()` with empty dict
- `load_ship_from_design_data()` with missing "ship_class" field
- `load_ship_from_file()` with non-existent path
- `load_ship_from_file()` with invalid JSON file
**Effort:** Simple

#### MAJOR: BattleUIService Missing Tests for Edge Cases
**ID:** TCG-UI2-006
**Location:** `game/ui/services/battle_ui_service.py` (production) / `tests/unit/ui/services/battle_ui_service/`
**Issue:** While BattleUIService has comprehensive tests, some edge cases are missing:
- Ship with no layers (empty `ship.layers`)
- Ship with empty resource list
- Projectile with `type=None` (uses DEFAULT_PROJECTILE_COLOR)
- Multiple ships with same ID (duplicate ID handling)
**Impact:** Edge cases in production could cause unexpected behavior.
**Recommendation:** Add tests for:
- `_convert_ship()` with ship that has `layers = {}`
- `_convert_projectile()` with `proj.type = None`
- Ship with resources.get_all_resources() returning empty list
**Effort:** Simple

#### MAJOR: ValidationService Missing Boundary Value Tests
**ID:** TCG-UI2-007
**Location:** `game/ui/services/validation_service.py` (production) / `tests/unit/ui/services/test_validation_service.py`
**Issue:** ValidationService tests exist but lack boundary value testing:
- Validation at exact capacity limits
- Validation with zero-capacity hull
- Validation with negative component counts
**Impact:** Boundary conditions at slot/capacity limits may not be properly validated.
**Recommendation:** Add tests for exact boundary values (e.g., component count == max slots).
**Effort:** Simple

#### MINOR: SpriteManager Test Skips Production Directory Test
**ID:** TCG-UI2-008
**Location:** `game/ui/renderer/sprites.py` (production) / `tests/unit/ui/test_sprites.py`
**Issue:** Test `test_load_sprites` skips if Components directory doesn't exist. This means CI could pass without testing actual sprite loading.
**Impact:** Integration with real assets not tested in some environments.
**Recommendation:** Consider adding a small test asset directory in tests/fixtures for sprite loading tests.
**Effort:** Medium

#### MINOR: InputMapper Missing Tests for Modifier Combinations
**ID:** TCG-UI2-009
**Location:** `game/ui/services/input_mapper.py` (production) / `tests/unit/ui/services/test_input_mapper.py`
**Issue:** While InputMapper tests are comprehensive, some modifier combinations are not tested:
- Ctrl+Alt+key combinations
- Ctrl+Shift+Alt (triple modifier)
- Numpad keys vs main keyboard keys
**Impact:** Complex keybindings may not work correctly.
**Recommendation:** Add tests for triple-modifier combinations if supported.
**Effort:** Simple

#### MINOR: ShipThemeManager Tests Skip When Federation Theme Missing
**ID:** TCG-UI2-010
**Location:** `game/ui/assets/ship_theme_manager.py` (production) / `tests/unit/ui/test_theme_discovery.py`
**Issue:** Multiple tests skip when Federation theme is not found. This reduces test coverage in CI environments without full assets.
**Impact:** Theme loading behavior not fully tested in all environments.
**Recommendation:** Create minimal mock theme fixtures for CI testing.
**Effort:** Medium

#### MINOR: ScreenshotManager capture() Region Clipping Tests Incomplete
**ID:** TCG-UI2-011
**Location:** `game/ui/services/screenshot_manager.py` (production) / `tests/unit/ui/services/test_screenshot_manager.py`
**Issue:** Tests for region capture exist but don't verify the actual clipped image content.
**Impact:** Region clipping may produce incorrect results.
**Recommendation:** Add tests that verify clipped surface dimensions match expected values.
**Effort:** Simple

#### MINOR: colors.py WHITE and BLACK Constants Not Tested
**ID:** TCG-UI2-012
**Location:** `game/ui/colors.py` (production) / `tests/unit/ui/test_colors.py`
**Issue:** Tests validate the COLORS dict but not the standalone WHITE, BLACK constants and FONT_MAIN.
**Impact:** Basic constants could be modified without test failure.
**Recommendation:** Add tests verifying WHITE == (255, 255, 255), BLACK == (0, 0, 0), FONT_MAIN is non-empty string.
**Effort:** Simple

#### INFO: BattleOrchestrator Tests Use Heavy Mocking
**ID:** TCG-UI2-013
**Location:** `game/ui/orchestration/battle_orchestrator.py` (production) / `tests/unit/ui/test_battle_orchestrator.py`
**Issue:** Several tests mock AIController and ShipControllableAdapter, which tests the orchestrator's wiring but not the actual integration.
**Impact:** Integration issues between orchestrator and actual AI classes won't be caught.
**Recommendation:** Consider adding integration tests that use real AI classes (if practical).
**Effort:** Medium

#### INFO: test_atlas_fallback_logic Is Empty
**ID:** TCG-UI2-014
**Location:** `tests/unit/ui/test_sprites.py` line 54-58
**Issue:** Test method `test_atlas_fallback_logic` has an empty body with just `pass`.
**Impact:** No actual test verification - test always passes.
**Recommendation:** Either implement a meaningful test or remove the empty test method.
**Effort:** Simple

#### INFO: utils.py Tests Could Use Parameterization
**ID:** TCG-UI2-015
**Location:** `tests/unit/ui/test_utils.py`
**Issue:** Many test methods test similar logic with different values. Could benefit from pytest parameterization for cleaner code and more value coverage.
**Impact:** None - test quality is good, this is a style suggestion.
**Recommendation:** Consider using `@pytest.mark.parametrize` for scale factor tests.
**Effort:** Simple (optional)

## Top 5 Priority Issues

1. **TCG-UI2-001 (CRITICAL)**: `game_renderer.py` has no test coverage. This is a critical rendering function that handles ship visualization, culling, and overlay rendering.

2. **TCG-UI2-002 (MAJOR)**: `ShipIOAdapter` has no dedicated tests. While it's a thin adapter, any bugs in the adapter layer would be undetected.

3. **TCG-UI2-003 (MAJOR)**: `UIConfig` constants have no validation tests. Invalid values could cause runtime errors throughout the UI.

4. **TCG-UI2-005 (MAJOR)**: `DesignLoaderAdapter` error handling paths are untested. Error scenarios like missing files or invalid data are not covered.

5. **TCG-UI2-006 (MAJOR)**: `BattleUIService` edge cases (empty layers, missing resources) are not tested.

## Test Quality Observations

### Strengths
- **ShipIO tests are comprehensive**: 100+ lines covering save/load, round-trip, error handling, and edge cases
- **InputMapper tests are thorough**: Coverage of contexts, conflicts, modifiers, and save/load roundtrip
- **ShipThemeManager tests include thread safety**: Concurrent access tests verify singleton behavior
- **Camera tests cover coordinate transforms**: World-to-screen and screen-to-world roundtrip verification
- **BattleUIService integration tests**: Real Ship objects tested alongside mocks

### Weaknesses
- **No tests for game_renderer.py**: Critical rendering code is untested
- **Some tests skip in CI**: Asset-dependent tests may skip when full assets unavailable
- **One empty test method**: `test_atlas_fallback_logic` does nothing
- **No boundary value tests for validators**: Exact capacity limits not tested
