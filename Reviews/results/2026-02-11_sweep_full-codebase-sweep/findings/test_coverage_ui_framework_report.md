# Test Coverage Gaps Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Production Files Scanned:** 17
- **Test Files Cross-Referenced:** 16
- **Total Issues Found:** 18
- **Critical:** 0 | **Major:** 7 | **Minor:** 8 | **Info:** 3

### Production File Inventory

| Production File | Test File(s) | Status |
|---|---|---|
| `game/ui/__init__.py` | `tests/unit/ui/test_ui_imports.py` | Covered |
| `game/ui/colors.py` | `tests/unit/ui/test_colors.py` | Covered (quality issue) |
| `game/ui/utils.py` | `tests/unit/ui/test_utils.py` | Covered |
| `game/ui/widgets.py` | `tests/unit/ui/test_ui_widgets.py` | Covered (quality issues) |
| `game/ui/services/validation_service.py` | `tests/unit/ui/services/test_validation_service.py` | Covered |
| `game/ui/services/vehicle_class_service.py` | `tests/unit/ui/services/test_vehicle_class_service.py` | Well covered |
| `game/ui/services/battle_ui_service.py` | `tests/unit/ui/services/battle_ui_service/` | Well covered |
| `game/ui/services/component_service.py` | `tests/unit/ui/services/test_component_service.py` | Well covered |
| `game/ui/services/ship_factory.py` | `tests/unit/ui/services/test_ship_factory.py` | Covered |
| `game/ui/services/ship_io_adapter.py` | `tests/unit/ui/services/test_ship_io_adapter.py` | Covered |
| `game/ui/services/design_loader_adapter.py` | `tests/unit/ui/services/test_design_loader_adapter.py` | Covered |
| `game/ui/renderer/camera.py` | `tests/unit/ui/test_camera.py`, `tests/integration/ui/test_camera_zoom.py` | Well covered |
| `game/ui/renderer/game_renderer.py` | `tests/unit/ui/test_rendering_logic.py` | Covered |
| `game/ui/renderer/sprites.py` | `tests/unit/ui/test_sprites.py`, `tests/unit/ui/test_sprite_loading.py` | Covered |
| `game/ui/interfaces/battle_ui.py` | `tests/unit/ui/interfaces/test_battle_ui.py` | Well covered |
| `game/ui/orchestration/battle_orchestrator.py` | `tests/unit/ui/test_battle_orchestrator.py` | Covered |
| `game/ui/assets/ship_theme_manager.py` | `tests/unit/ui/test_theme_discovery.py` | Covered (gap in portraits) |

## Findings

#### MAJOR: ShipThemeManager.get_portrait_image() and _ship_class_to_portrait_name() Have Zero Test Coverage
**ID:** TCG-UI2-001
**Location:** `game/ui/assets/ship_theme_manager.py` (lines 219-314) / No test file
**Issue:** Two public methods have no test coverage whatsoever:
- `get_portrait_image(theme_name, ship_class)` -- loads and caches portrait images from disk
- `_ship_class_to_portrait_name(ship_class)` -- converts ship class names to portrait filenames with non-trivial parsing logic (e.g., "Fighter (Medium)" -> "MediumFighter", "Light Cruiser" -> "LightCruiser")

The `_ship_class_to_portrait_name` method contains parsing logic with multiple branches (parenthetical extraction, space removal) that could easily have edge-case bugs. The `get_portrait_image` method has caching, file-not-found handling, and theme fallback logic that are all untested.
**Impact:** Name parsing bugs would cause portrait images to silently fail to load. Caching or file-handling bugs could cause memory leaks or repeated disk I/O.
**Recommendation:** Add unit tests for `_ship_class_to_portrait_name` covering: simple names ("Battleship"), space-separated names ("Light Cruiser"), parenthetical names ("Fighter (Medium)"), and edge cases (empty string, multiple parentheses). Add unit tests for `get_portrait_image` covering: cache hit, cache miss, missing theme, missing portrait file, before discovery.
**Effort:** Simple

#### MAJOR: Slider Widget Tests Have Weak Assertions
**ID:** TCG-UI2-002
**Location:** `tests/unit/ui/test_ui_widgets.py` (lines 89-130)
**Issue:** Multiple Slider tests have assertions that cannot meaningfully fail:
1. `test_slider_value_update` (line 108): asserts `slider.val is not None` -- this will always pass since `val` is initialized as an integer (50) and `update_val` sets it to a numeric value. The test should assert the actual value after the update.
2. `test_slider_clamps_value` (line 124-129): Only asserts the initial value is within bounds after construction -- it never calls `update_val` with an out-of-bounds mouse position, so it does not actually test clamping behavior.
**Impact:** These tests provide false confidence. Bugs in slider value computation and clamping would not be detected.
**Recommendation:** Fix `test_slider_value_update` to assert the actual computed value. Fix `test_slider_clamps_value` to call `update_val` with positions far outside the slider bounds and verify the value is clamped to min/max.
**Effort:** Simple

#### MAJOR: test_no_duplicate_color_values Is a No-Op Test
**ID:** TCG-UI2-003
**Location:** `tests/unit/ui/test_colors.py` (lines 39-49)
**Issue:** `test_no_duplicate_color_values` contains `pass` in the duplicate-detection loop and ends with `assert True`. This test can never fail regardless of whether there are duplicate color values. It claims to check for duplicates but does not actually assert anything about them.
**Impact:** If duplicate colors are introduced (potentially indicating a copy-paste error in the color palette), this test would not catch it.
**Recommendation:** Either make the test actually fail on duplicates (if duplicates are undesirable) or remove it entirely and replace with a comment explaining duplicates are acceptable. A test with `assert True` is worse than no test because it suggests coverage exists.
**Effort:** Simple

#### MAJOR: Camera.update_input() Has No Direct Unit Tests
**ID:** TCG-UI2-004
**Location:** `game/ui/renderer/camera.py` (lines 61-113) / `tests/unit/ui/test_camera.py`
**Issue:** The `update_input` method handles keyboard input (WASD/arrow keys for panning), middle-mouse drag panning, and mouse wheel zooming. None of these input paths are directly tested. The zoom limit tests in `TestCameraZoomAnimation` manually replicate the clamping logic instead of driving it through `update_input`. The keyboard panning and middle-mouse drag are entirely untested.
**Impact:** Input handling bugs (e.g., wrong key bindings, inverted drag direction, incorrect pan speed scaling with zoom) would go undetected.
**Recommendation:** Add tests that create pygame events and pass them to `update_input`, verifying: (1) arrow/WASD keys move camera position, (2) mouse wheel events set target_zoom, (3) manual movement clears camera target, (4) zoom is clamped to min/max.
**Effort:** Medium

#### MAJOR: game_renderer.py draw_ship() Overlay Mode Has Thin Coverage
**ID:** TCG-UI2-005
**Location:** `game/ui/renderer/game_renderer.py` (lines 76-136) / `tests/unit/ui/test_rendering_logic.py`
**Issue:** The `draw_ship` overlay mode (when `camera.show_overlay = True`) draws layer circles, component dots color-coded by type, and direction indicators. While `test_component_color_coding` verifies weapon and engine colors, it does not test:
1. Armor component color coding (`major_classification == 'Armor'`)
2. The direction indicator line rendering
3. Component dot positioning based on layer radius percentages
4. The zoom threshold (`camera.zoom > 0.3`) that hides component dots at low zoom
**Impact:** Visual regression bugs in the overlay rendering (e.g., wrong layer radii, broken direction indicator, incorrect component positioning) would not be caught.
**Recommendation:** Add tests for armor classification color, direction indicator rendering, zoom threshold behavior, and verify component dots are drawn at correct positions.
**Effort:** Medium

#### MAJOR: ShipFactory.setup_formation() Does Not Test Edge Cases
**ID:** TCG-UI2-006
**Location:** `game/ui/services/ship_factory.py` (lines 138-189) / `tests/unit/ui/services/test_ship_factory.py`
**Issue:** `setup_formation` is tested for the happy path (relative and fixed rotation modes) but missing edge case tests:
1. `formation_id` is `None` in formation data (should skip that entry -- line 166-167)
2. Empty `formation_data` list (should do nothing)
3. Multiple independent formations in the same data (e.g., two different `formation_id` values)
4. Invalid `ship_index` that is out of bounds (would crash with IndexError)
**Impact:** Formation setup bugs in edge cases could crash the game during battle setup.
**Recommendation:** Add tests for None formation_id entries, empty formation data, multiple formations, and boundary ship indices.
**Effort:** Simple

#### MAJOR: Widgets Button.draw() and Slider.draw() Have No Tests
**ID:** TCG-UI2-007
**Location:** `game/ui/widgets.py` (lines 27-34, 97-101) / `tests/unit/ui/test_ui_widgets.py`
**Issue:** The `draw()` methods for `Button`, `Label`, and `Slider` have no test coverage. While these are rendering methods that are harder to test meaningfully, they contain logic worth verifying:
- `Button.draw()`: Uses `is_hovered` to select between `color` and `hover_color`, renders text centered on the button rect
- `Label.draw()`: Renders text at the stored position
- `Slider.draw()`: Draws track and handle rects

These methods call `pygame.font.SysFont` and `pygame.draw.rect`, which can be mocked for verification.
**Impact:** Rendering bugs (wrong colors, wrong text position, wrong handle position) would not be caught by any test.
**Recommendation:** Add tests using mocked pygame that verify: (1) Button uses hover_color when hovered, (2) Label renders at correct position, (3) Slider handle is drawn at correct position based on value.
**Effort:** Medium

#### MINOR: Camera.update() Target Following Does Not Test Target Without is_alive Attribute
**ID:** TCG-UI2-008
**Location:** `game/ui/renderer/camera.py` (lines 57-59) / `tests/unit/ui/test_camera.py`
**Issue:** The `update` method checks `hasattr(self.target, 'is_alive')` before accessing it, but no test verifies the behavior when the target object lacks an `is_alive` attribute. The code also has incorrect indentation on line 59 (`self.position = ...` is always executed regardless of the `is_alive` check), which means the `is_alive` check is effectively a no-op -- the camera follows the target position regardless. No test catches this logical bug.
**Impact:** The `is_alive` check on the target is dead code. If the intention was to stop following dead targets, it does not work. If the intention was always to follow (including dead targets), the `if` check is misleading.
**Recommendation:** Add a test that verifies the intended behavior for dead vs alive targets. Fix the indentation if the behavior should differ for dead targets.
**Effort:** Simple

#### MINOR: ValidationService Does Not Test Thread Safety or Lazy Initialization Race
**ID:** TCG-UI2-009
**Location:** `game/ui/services/validation_service.py` (lines 42-46) / `tests/unit/ui/services/test_validation_service.py`
**Issue:** `_get_validator()` uses lazy initialization with no locking. If `validate_addition` or `validate_design` is called concurrently from multiple threads with `validator=None`, the lazy initialization could race. No test verifies concurrent access.
**Impact:** Low risk since UI services are typically single-threaded, but the pattern differs from other singletons in the codebase (ShipThemeManager, SpriteManager) that use explicit locking.
**Recommendation:** Document single-threaded assumption, or add a lock consistent with other services.
**Effort:** Simple

#### MINOR: BattleUIService conftest mock_ship Uses heading Instead of angle
**ID:** TCG-UI2-010
**Location:** `tests/unit/ui/services/battle_ui_service/conftest.py` (line 17)
**Issue:** The `mock_ship` fixture sets `ship.heading = 1.5`, but the production code in `BattleUIService._convert_ship()` (line 161) reads `ship.angle` (not `ship.heading`). Because the mock is a `Mock()` object, accessing `ship.angle` on it auto-creates a new MagicMock attribute rather than using the `heading` value. This means the heading value in the ShipDTO is a MagicMock object, not 1.5. The test `test_ship_dto_has_correct_basic_properties` does not assert on `dto.heading`, so this goes unnoticed.
**Impact:** The conftest fixture does not accurately model the real Ship interface. The heading-to-angle mapping (a key DTO conversion) is not tested through these fixtures.
**Recommendation:** Change `mock_ship.heading = 1.5` to `mock_ship.angle = 1.5` in the conftest, and add an assertion `assert dto.heading == 1.5` to `test_ship_dto_has_correct_basic_properties`.
**Effort:** Simple

#### MINOR: Slider.handle_event() MOUSEBUTTONUP Returns True Even When Not Dragging Inside
**ID:** TCG-UI2-011
**Location:** `game/ui/widgets.py` (lines 74-77) / `tests/unit/ui/test_ui_widgets.py`
**Issue:** No test verifies that `handle_event` returns `True` when a `MOUSEBUTTONUP` event ends a drag, or returns `False` when a `MOUSEBUTTONUP` event occurs without an active drag. The drag lifecycle (MOUSEDOWN -> MOUSEMOTION -> MOUSEUP) is not tested end-to-end.
**Impact:** UI event handling bugs (e.g., events not consumed properly, ghost drags) would not be caught.
**Recommendation:** Add a test that simulates the full drag lifecycle and verifies return values at each step.
**Effort:** Simple

#### MINOR: ShipIOAdapter Does Not Test save_ship Cancel Case
**ID:** TCG-UI2-012
**Location:** `game/ui/services/ship_io_adapter.py` (line 70-84) / `tests/unit/ui/services/test_ship_io_adapter.py`
**Issue:** The docstring for `save_ship` describes a cancel case returning `(False, None)`, but no test verifies this return value. The test covers success `(True, msg)` and failure `(False, msg)`, but not the cancel case `(False, None)`.
**Impact:** The cancel path for save operations is undocumented in tests. If the behavior changes, no test would catch the regression.
**Recommendation:** Add `test_save_ship_returns_false_none_on_cancel` that mocks the underlying save to return `(False, None)`.
**Effort:** Simple

#### MINOR: ComponentService.is_modifier_allowed() Does Not Test deny_abilities Restriction
**ID:** TCG-UI2-013
**Location:** `game/ui/services/component_service.py` / `tests/unit/ui/services/test_component_service.py`
**Issue:** The production code checks `allow_types`, `deny_types`, and `allow_abilities` restrictions. However, there is no `deny_abilities` restriction type tested or implemented. While the production code does not have a `deny_abilities` check, the test coverage of the restriction logic would benefit from testing what happens when an unexpected restriction key is present (e.g., `deny_abilities`, `min_mass`). Currently the code silently ignores unknown restriction keys.
**Impact:** Low -- the code handles this by ignoring unknown keys. But if a `deny_abilities` restriction is added to modifier data without implementing the check, it would be silently ignored.
**Recommendation:** Add a test that verifies unknown restriction keys are handled gracefully (currently ignored = allowed).
**Effort:** Simple

#### MINOR: DesignLoaderAdapter Does Not Test Default Position Arguments
**ID:** TCG-UI2-014
**Location:** `game/ui/services/design_loader_adapter.py` (lines 46-69) / `tests/unit/ui/services/test_design_loader_adapter.py`
**Issue:** `load_ship_from_design_data` has default parameters `center_x=0, center_y=0`, but no test calls the method without providing these arguments to verify the defaults work.
**Impact:** Low risk since the defaults are straightforward, but testing default parameter behavior is good practice.
**Recommendation:** Add a test calling `adapter.load_ship_from_design_data(design_data)` without position args and verifying the loader receives `center_x=0, center_y=0`.
**Effort:** Simple

#### MINOR: game_renderer.py draw_hud() Does Not Test Zero Mass Division Path
**ID:** TCG-UI2-015
**Location:** `game/ui/renderer/game_renderer.py` (lines 166-177) / `tests/unit/ui/test_rendering_logic.py`
**Issue:** `draw_hud` calculates `accel = ship.total_thrust / ship.mass` and `top_speed = accel / ship.drag`, guarded by `if ship.mass > 0` and `if ship.drag > 0`. No test verifies behavior when `mass == 0` (the entire physics stats section is skipped) or when `drag == 0` (would need separate handling but currently guarded). The zero-mass path is exercised by dead/derelict ships but the test for dead ships doesn't verify the physics section is omitted.
**Impact:** Division by zero would crash the HUD if mass/drag guards were removed during refactoring.
**Recommendation:** Add tests for `mass == 0` and `drag == 0` to verify no exceptions and no stats text is rendered.
**Effort:** Simple

#### INFO: test_atlas_fallback_logic Is Empty (Pass-Only Test)
**ID:** TCG-UI2-016
**Location:** `tests/unit/ui/test_sprites.py` (lines 54-58)
**Issue:** `test_atlas_fallback_logic` contains only `pass`. The docstring acknowledges this is deprecated functionality tested elsewhere, but the test still appears in test counts as a "pass" giving the impression of coverage that does not exist.
**Impact:** None functionally, but inflates test count.
**Recommendation:** Remove the empty test or mark it with `pytest.skip("Atlas fallback tested in test_sprite_loading.py")` to be explicit.
**Effort:** Simple

#### INFO: Inconsistent Import Patterns in Service Tests
**ID:** TCG-UI2-017
**Location:** Various test files under `tests/unit/ui/services/`
**Issue:** Some test files import the class under test at the module level (e.g., `test_component_service.py` line 8: `from game.ui.services.component_service import ComponentService`), while others import inside each test method (e.g., `test_ship_io_adapter.py` line 14: `from game.ui.services.ship_io_adapter import ShipIOAdapter` inside each test). The inconsistency makes the test suite harder to understand and maintain.
**Impact:** No functional impact. Organizational concern.
**Recommendation:** Standardize on module-level imports unless there is a specific reason for lazy imports (e.g., preventing import side effects).
**Effort:** Simple

#### INFO: BattleUIService Integration Tests Are Comprehensive But Rely on Real Registries
**ID:** TCG-UI2-018
**Location:** `tests/unit/ui/services/battle_ui_service/test_state_and_integration.py`
**Issue:** The integration tests for `BattleUIServiceRealShipIntegration` and `BattleUIServiceRealProjectileIntegration` create real Ship objects with real components, which is excellent for integration coverage. However, they depend on `fresh_registries` fixture and specific component IDs (`bridge`, `crew_quarters`, `life_support`, `standard_engine`, `railgun`). If any of these component IDs are renamed or removed, these tests will fail with obscure errors rather than clear messages.
**Impact:** Maintenance burden when component data changes. Not a coverage gap per se, but a fragility concern.
**Recommendation:** Consider adding a comment documenting the required components, or use constants from a central test data file.
**Effort:** Simple

## Top 5 Priority Issues

1. **TCG-UI2-001 (MAJOR):** `ShipThemeManager.get_portrait_image()` and `_ship_class_to_portrait_name()` have zero test coverage. The name parsing method has multiple code paths with no tests at all. This is the largest untested surface area in the shard.

2. **TCG-UI2-002 (MAJOR):** Slider widget tests have weak assertions that cannot meaningfully fail. `test_slider_value_update` asserts `is not None` (always true), and `test_slider_clamps_value` never exercises the clamping code path.

3. **TCG-UI2-004 (MAJOR):** `Camera.update_input()` handles keyboard, mouse drag, and mouse wheel input with no direct unit tests. This is a critical interaction point between user input and camera state.

4. **TCG-UI2-010 (MINOR):** BattleUIService conftest `mock_ship` fixture sets `heading` instead of `angle`, causing the heading DTO field to be untested. This is a subtle bug in the test infrastructure that masks a real behavior.

5. **TCG-UI2-003 (MAJOR):** `test_no_duplicate_color_values` in test_colors.py always passes (`assert True`), providing false coverage. Tests that can never fail are worse than no tests.
