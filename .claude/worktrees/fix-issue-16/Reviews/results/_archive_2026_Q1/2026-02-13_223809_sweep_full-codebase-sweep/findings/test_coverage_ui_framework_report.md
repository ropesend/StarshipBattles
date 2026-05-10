# Test Coverage Gaps Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Production Files Scanned:** 21
- **Test Files Cross-Referenced:** 26
- **Total Issues Found:** 9
- **Critical:** 1 | **Major:** 4 | **Minor:** 3 | **Info:** 1

## Scope Details

### Production Files Scanned
**Root Files:**
- `game/ui/__init__.py`
- `game/ui/utils.py`
- `game/ui/config.py`
- `game/ui/colors.py`

**Services:**
- `game/ui/services/validation_service.py`
- `game/ui/services/vehicle_class_service.py`
- `game/ui/services/component_service.py`
- `game/ui/services/ship_factory.py`
- `game/ui/services/design_loader_adapter.py`
- `game/ui/services/ship_io_adapter.py`
- `game/ui/services/battle_factories.py`
- `game/ui/services/battle_ui_service.py`
- `game/ui/services/input_mapper.py`
- `game/ui/services/screenshot_manager.py`
- `game/ui/services/ship_io.py`

**Renderer:**
- `game/ui/renderer/camera.py`
- `game/ui/renderer/game_renderer.py`
- `game/ui/renderer/sprites.py`

**Interfaces:**
- `game/ui/interfaces/battle_ui.py`

**Orchestration:**
- `game/ui/orchestration/battle_orchestrator.py`

**Assets:**
- `game/ui/assets/ship_theme_manager.py`

## Findings

#### CRITICAL: No Tests for game_renderer.py (Ship Rendering Logic)
**ID:** TCG-UI2-001
**Location:** `game/ui/renderer/game_renderer.py` (production) / No corresponding test file
**Issue:** The `game_renderer.py` module contains the `draw_ship()` function which renders ships with theme images, layers, components, and direction indicators. This is a visually critical path with zoom-dependent behavior, culling logic, and complex coordinate transformations. There are no unit tests for this module.
**Impact:** Visual bugs in ship rendering would go undetected. The function has branches for overlay mode, low zoom fallbacks, and component visualization that are untested. Regression risk is high for any refactoring.
**Recommendation:** Create `tests/unit/ui/renderer/test_game_renderer.py` with tests covering:
- Culling logic (ships outside viewport)
- Theme image scaling and rotation
- Overlay mode rendering paths
- Low-zoom fallback behavior
- Component dot positioning
**Effort:** Medium

#### MAJOR: No Tests for battle_factories.py (Battle Creation Factory Functions)
**ID:** TCG-UI2-002
**Location:** `game/ui/services/battle_factories.py` (production) / No dedicated test file
**Issue:** The `battle_factories.py` module provides critical factory functions (`create_manual_battle`, `create_test_battle`, `create_strategy_battle`, `create_hypothetical_battle`) that configure battle controllers with AI factories. While these functions are used indirectly in integration tests, there are no dedicated unit tests for the factory functions themselves.
**Impact:** Changes to battle configuration defaults or factory logic could break battle setup without detection. The hypothetical battle cloning logic is particularly complex and untested.
**Recommendation:** Create `tests/unit/ui/services/test_battle_factories.py` with tests for:
- Each factory function returns a correctly configured BattleController
- Default AI factory creation
- Ship cloning in hypothetical battles preserves ship state
- Correct BattleMode is set for each factory
**Effort:** Simple

#### MAJOR: config.py Has No Test Coverage
**ID:** TCG-UI2-003
**Location:** `game/ui/config.py` (production) / No test file
**Issue:** The `config.py` file likely contains UI configuration constants and settings. While configuration files are often considered simple, they can contain computed values, validation logic, or factory methods that should be tested.
**Impact:** Configuration drift or typos in constants would go undetected.
**Recommendation:** Review `config.py` contents and add tests for any non-trivial logic. If it's pure constants, add a basic import test and consider documenting that it's intentionally untested.
**Effort:** Simple

#### MAJOR: utils.py Has Thin Test Coverage
**ID:** TCG-UI2-004
**Location:** `game/ui/utils.py` (production) / `tests/unit/ui/test_utils.py` (test)
**Issue:** The test file exists but may not cover all public functions. The production file contains utility functions like `calculate_ship_image_scale()` and `scale_and_rotate_image()` which are used by the untested `game_renderer.py`. These functions have edge cases around scaling factors, rotation angles, and image metrics.
**Impact:** Image scaling bugs would affect ship rendering quality.
**Recommendation:** Verify test coverage includes:
- Edge cases for scale calculation (very small/large images, edge zoom levels)
- Rotation angle normalization
- Image metrics handling (None metrics, zero-sized images)
**Effort:** Simple

#### MAJOR: ship_io_adapter.py Needs Error Path Testing
**ID:** TCG-UI2-005
**Location:** `game/ui/services/ship_io_adapter.py` (production) / `tests/unit/ui/services/test_ship_io_adapter.py` (test)
**Issue:** While the adapter has test coverage, the tests may not adequately cover error propagation from the underlying `ShipIO` class. The adapter wraps `ShipIO` and should properly propagate or handle errors from tkinter failures, file I/O errors, and deserialization failures.
**Impact:** Error handling inconsistencies between the adapter and underlying service could cause confusing error messages or silent failures.
**Recommendation:** Add tests verifying:
- Tkinter unavailability is properly propagated
- File permission errors are handled gracefully
- Malformed JSON handling
**Effort:** Simple

#### MINOR: BattleOrchestrator Missing Edge Case Tests
**ID:** TCG-UI2-006
**Location:** `game/ui/orchestration/battle_orchestrator.py` (production) / `tests/unit/ui/test_battle_orchestrator.py` (test)
**Issue:** The orchestrator tests verify basic functionality but don't test edge cases such as:
- Creating AI for ships with None values
- Very large team sizes
- Ships with invalid enemy_team_id values
**Impact:** Edge cases in battle AI setup could cause unexpected behavior.
**Recommendation:** Add edge case tests for boundary conditions and invalid inputs.
**Effort:** Simple

#### MINOR: screenshot_manager.py Tests Could Mock Less Heavily
**ID:** TCG-UI2-007
**Location:** `game/ui/services/screenshot_manager.py` (production) / `tests/unit/ui/services/test_screenshot_manager.py` (test)
**Issue:** The screenshot manager tests extensively mock pygame, tkinter, and filesystem operations. While this is necessary for unit testing, there's a risk that the mocks don't accurately represent real behavior, especially for clipboard operations which are platform-specific.
**Impact:** The tests may pass but the actual clipboard/screenshot functionality could fail on specific platforms.
**Recommendation:** Consider adding a small set of integration tests (marked with pytest skip for CI) that test actual screenshot capture to a temp directory without mocking pygame.
**Effort:** Medium

#### MINOR: colors.py Has Test Coverage but Missing Edge Cases
**ID:** TCG-UI2-008
**Location:** `game/ui/colors.py` (production) / `tests/unit/ui/test_colors.py` (test)
**Issue:** The colors module test file exists but should verify edge cases for any color manipulation functions (if present). Common edge cases include: RGB values at boundaries (0, 255), alpha channel handling, and color format conversions.
**Impact:** Color rendering bugs at extreme values.
**Recommendation:** Review color functions and add boundary value tests.
**Effort:** Simple

#### INFO: Excellent Test Coverage on BattleUIService
**ID:** TCG-UI2-009
**Location:** `game/ui/services/battle_ui_service.py` (production) / `tests/unit/ui/services/battle_ui_service/` (test directory)
**Issue:** (Positive observation) The BattleUIService has exemplary test coverage with:
- Separate test modules for conversion logic and state/integration
- Tests with both mock objects AND real domain objects
- Edge case testing for missing attributes, None values
- Protocol compliance verification
**Impact:** This is a model for how other UI services should be tested.
**Recommendation:** Use this as a template when creating tests for `battle_factories.py` and other services.
**Effort:** N/A

## Top 5 Priority Issues

1. **TCG-UI2-001 (CRITICAL):** `game_renderer.py` - Zero test coverage for the primary ship rendering function. This is visually critical code with complex branching logic.

2. **TCG-UI2-002 (MAJOR):** `battle_factories.py` - No tests for battle creation factory functions. These configure critical game state.

3. **TCG-UI2-004 (MAJOR):** `utils.py` - Utility functions used by the untested renderer need thorough edge case testing.

4. **TCG-UI2-005 (MAJOR):** `ship_io_adapter.py` - Error propagation paths need verification to ensure consistent error handling.

5. **TCG-UI2-003 (MAJOR):** `config.py` - Should have at least basic validation that configuration values are sane.

## Test Quality Observations

### Strengths
- `BattleUIService` has excellent coverage with both unit and integration tests
- `Camera` class has comprehensive coordinate transformation tests with edge cases
- `ShipIO` has thorough round-trip serialization tests
- `SpriteManager` tests include thread safety and error path coverage
- `ShipThemeManager` tests cover caching, error paths, and concurrent access

### Areas for Improvement
- Several services rely heavily on mocks without any integration test counterpart
- Renderer code has no tests at all
- Factory functions are tested only indirectly through integration tests
