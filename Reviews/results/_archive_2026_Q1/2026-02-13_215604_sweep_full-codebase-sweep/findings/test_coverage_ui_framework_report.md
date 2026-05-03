# Test Coverage Gaps Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Production Files Scanned:** 47
- **Test Files Cross-Referenced:** 32
- **Total Issues Found:** 18
- **Critical:** 2 | **Major:** 8 | **Minor:** 6 | **Info:** 2

## Findings

#### CRITICAL: SystemTreePanel Has No Unit Tests
**ID:** TCG-UI2-001
**Location:** `game/ui/panels/system_tree_panel.py` (production) / No corresponding test file exists
**Issue:** SystemTreePanel is a complex UI component with 418 lines of code handling hierarchical tree display with expand/collapse, grouping by planet/star/warp point, click handling, and dynamic layout. It has zero unit test coverage.
**Impact:** Regressions in tree rendering, selection callbacks, expand/collapse logic, or grouping could go undetected. This panel is used in the strategy screen for system object selection.
**Recommendation:** Create `tests/unit/ui/panels/test_system_tree_panel.py` with tests for:
- `SystemTreeItem` initialization, positioning, show/hide
- `SystemTreePanel.set_items()` with various content combinations
- Expand/collapse toggle behavior
- `process_event()` click handling
- Edge cases: empty list, single item, deeply nested groups
**Effort:** Complex

#### CRITICAL: BaseGallery Abstract Class Has No Tests
**ID:** TCG-UI2-002
**Location:** `game/ui/panels/base_gallery.py` (production) / No corresponding test file exists
**Issue:** BaseGallery is an abstract base class (264 lines) providing shared functionality for RacePortraitGallery and RaceFlagGallery. While it's abstract, its concrete methods `_create_content()`, `_populate_gallery()`, `on_asset_selected()`, and `handle_button_click()` have complex logic that is not tested.
**Impact:** Bugs in thumbnail layout calculation, selection highlighting, or callback invocation would affect both portrait and flag galleries. These are critical for the race creation flow.
**Recommendation:** Create `tests/unit/ui/panels/test_base_gallery.py` with a concrete test subclass that tests:
- `_populate_gallery()` column/row layout calculation
- `_sanitize_object_id()` edge cases
- `on_asset_selected()` callback invocation and highlight updates
- `set_from_config()` restoring selection
**Effort:** Medium

#### MAJOR: ShipDetailPanel Missing Comprehensive Tests
**ID:** TCG-UI2-003
**Location:** `game/ui/panels/ship_detail_panel.py` (production) / No corresponding test file exists
**Issue:** ShipDetailPanel (447 lines) handles complex ship instance display with component damage visualization, resource tracking, layer collapse/expand, and combat stats. No unit tests exist.
**Impact:** Regression in damage color calculation, resource display formatting, or layer toggle behavior could go undetected. The `get_damage_color()` helper function is particularly important for visual feedback.
**Recommendation:** Create `tests/unit/ui/panels/test_ship_detail_panel.py` testing:
- `get_damage_color()` threshold boundaries (0, 0.5, 0.75, 1.0)
- `update_ship()` with various ship states
- `_build_damage_section()` layer grouping
- `toggle_layer()` state management
- `process_event()` button handling
**Effort:** Medium

#### MAJOR: BattleUIService Conversion Logic Undertested
**ID:** TCG-UI2-004
**Location:** `game/ui/services/battle_ui_service.py` (production) / `tests/unit/ui/services/battle_ui_service/test_conversion.py` (partial coverage)
**Issue:** While test_conversion.py exists, it only tests happy path DTO conversion. Error handling, edge cases (ships with no components, empty resource lists, None targets), and boundary conditions for tick counts are not tested.
**Impact:** DTO conversion failures could cause UI crashes or display incorrect battle state during combat.
**Recommendation:** Add tests for:
- Ships with empty component lists
- Ships with None/missing target references
- Projectiles at boundary endurance (0, max)
- `get_tick_count()` after extended battles
**Effort:** Simple

#### MAJOR: InputMapper Missing Error Path Tests
**ID:** TCG-UI2-005
**Location:** `game/ui/services/input_mapper.py` (production) / `tests/unit/ui/services/test_input_mapper.py` (test exists)
**Issue:** Tests cover basic mapping functionality but not error cases: invalid keycodes, empty event lists, malformed input data, or concurrent modification during mapping.
**Impact:** Input handling failures could make the game unresponsive to certain key combinations.
**Recommendation:** Add tests for:
- Events with missing/None keycodes
- Empty event list processing
- Keyboard state changes during mapping
**Effort:** Simple

#### MAJOR: ShipIOAdapter and DesignLoaderAdapter Missing File Error Tests
**ID:** TCG-UI2-006
**Location:** `game/ui/services/ship_io_adapter.py`, `game/ui/services/design_loader_adapter.py` (production)
**Issue:** These adapters handle file I/O for ship designs. While happy path tests exist, error scenarios (missing files, malformed JSON, permission errors, disk full conditions) are not tested.
**Impact:** File I/O failures could cause data loss or crashes when loading/saving ship designs.
**Recommendation:** Add tests for:
- Loading non-existent files
- Saving to read-only locations
- Loading corrupted/malformed JSON
- Handling of partial writes
**Effort:** Medium

#### MAJOR: SpriteManager Has No Tests for File System Errors
**ID:** TCG-UI2-007
**Location:** `game/ui/renderer/sprites.py` (production) / `tests/unit/ui/test_sprites.py` (partial coverage)
**Issue:** test_sprites.py tests basic sprite retrieval, but not file system error handling during `load_sprites()` or `_load_from_directory()`. The code catches FileNotFoundError, OSError, and pygame.error but these paths are untested.
**Impact:** Missing or corrupted sprite files could cause silent failures or crashes.
**Recommendation:** Add tests mocking:
- `os.listdir()` raising PermissionError
- `pygame.image.load()` raising pygame.error
- Directory with no valid sprite files
**Effort:** Simple

#### MAJOR: draw_ship Renderer Function Has No Unit Tests
**ID:** TCG-UI2-008
**Location:** `game/ui/renderer/game_renderer.py::draw_ship()` (production)
**Issue:** The `draw_ship()` function (143 lines) handles ship rendering with culling, scaling, rotation, layer visualization, and component display. While integration tests exercise it, no unit tests verify the culling math, scale calculations, or layer color mapping.
**Impact:** Visual rendering bugs (ships rendered at wrong position/size, incorrect culling) could affect gameplay.
**Recommendation:** Create `tests/unit/ui/renderer/test_game_renderer.py` with tests for:
- Culling logic (screen bounds detection)
- Scale factor calculation with various zoom levels
- Layer color mapping with LAYER_COLORS constant
- Component visualization positioning math
**Effort:** Medium

#### MAJOR: ScreenshotManager Missing Integration Tests
**ID:** TCG-UI2-009
**Location:** `game/ui/services/screenshot_manager.py` (production) / `tests/unit/ui/services/test_screenshot_manager.py` (exists but limited)
**Issue:** ScreenshotManager handles file naming with timestamps and directory creation. Tests exist but don't verify actual file creation, directory permissions, or filename collision handling.
**Impact:** Screenshot saving failures would silently fail without user feedback.
**Recommendation:** Add integration tests that:
- Actually write test screenshots to temp directory
- Verify filename timestamp format
- Test behavior when screenshots directory doesn't exist
**Effort:** Simple

#### MAJOR: ShipThemeManager Portrait Loading Not Fully Tested
**ID:** TCG-UI2-010
**Location:** `game/ui/assets/ship_theme_manager.py` (production) / `tests/unit/ui/test_theme_discovery.py` (partial)
**Issue:** `get_portrait_image()` and `_load_portrait_image()` methods (added for PROJ-03) lack dedicated tests. The `_ship_class_to_portrait_name()` conversion logic with parentheses parsing is complex but untested.
**Impact:** Portrait images might fail to load for certain ship classes with unusual naming.
**Recommendation:** Add tests for `_ship_class_to_portrait_name()` with:
- "Fighter (Medium)" -> "MediumFighter"
- "Light Cruiser" -> "LightCruiser"
- Edge cases with multiple parentheses or special characters
**Effort:** Simple

#### MINOR: Camera.update_input() Only Tests Individual Inputs
**ID:** TCG-UI2-011
**Location:** `game/ui/renderer/camera.py` (production) / `tests/unit/ui/test_camera.py` (exists)
**Issue:** Camera tests are comprehensive but don't test combined inputs (e.g., simultaneous WASD and mouse wheel, or key held while middle-mouse dragging).
**Impact:** Interaction bugs between input methods would go undetected.
**Recommendation:** Add tests for combined input scenarios.
**Effort:** Simple

#### MINOR: ValidationService Missing Boundary Tests
**ID:** TCG-UI2-012
**Location:** `game/ui/services/validation_service.py` (production) / `tests/unit/ui/services/test_validation_service.py` (exists)
**Issue:** Validation tests exist but don't test exact boundary values (e.g., exactly at mass limit, exactly at component count limit).
**Impact:** Off-by-one errors in validation could allow invalid designs or reject valid ones.
**Recommendation:** Add boundary tests at exact limit values.
**Effort:** Simple

#### MINOR: BattleFactories Service Has No Dedicated Tests
**ID:** TCG-UI2-013
**Location:** `game/ui/services/battle_factories.py` (production)
**Issue:** While BattleFactories is used in integration tests, it has no dedicated unit tests verifying factory method behavior.
**Impact:** Factory configuration changes could break battle setup without clear test failures.
**Recommendation:** Create dedicated unit tests for factory methods.
**Effort:** Simple

#### MINOR: IBattleUI Protocol Tests Are Type-Only
**ID:** TCG-UI2-014
**Location:** `game/ui/interfaces/battle_ui.py` (production) / `tests/unit/ui/interfaces/test_battle_ui.py` (exists)
**Issue:** Tests verify protocol structure but don't test DTO frozen dataclass behavior (immutability guarantees).
**Impact:** Accidental DTO mutation could cause subtle state bugs.
**Recommendation:** Add tests verifying DTO immutability (attempts to modify should raise).
**Effort:** Simple

#### MINOR: ComponentService Missing Registry Integration Tests
**ID:** TCG-UI2-015
**Location:** `game/ui/services/component_service.py` (production) / `tests/unit/ui/services/test_component_service.py` (exists)
**Issue:** ComponentService tests mock the registry. No tests verify actual registry integration with real component data.
**Impact:** Mismatches between service and registry could cause component lookup failures.
**Recommendation:** Add integration test with real registry data.
**Effort:** Simple

#### MINOR: VehicleClassService Edge Cases
**ID:** TCG-UI2-016
**Location:** `game/ui/services/vehicle_class_service.py` (production) / `tests/unit/ui/services/test_vehicle_class_service.py` (exists)
**Issue:** Tests don't cover getting classes with very long names, special characters, or Unicode characters.
**Impact:** Display issues with unusual ship class names.
**Recommendation:** Add edge case tests for unusual class names.
**Effort:** Simple

#### INFO: test_utils.py Could Use Parameterized Tests
**ID:** TCG-UI2-017
**Location:** `tests/unit/ui/test_utils.py`
**Issue:** Many test functions test similar logic with different inputs. These could be consolidated using pytest.mark.parametrize for cleaner test organization.
**Impact:** No functional impact, but test maintenance would be easier.
**Recommendation:** Consider refactoring to use parameterized tests.
**Effort:** Simple

#### INFO: Missing conftest.py Fixtures for UI Manager
**ID:** TCG-UI2-018
**Location:** `tests/unit/ui/conftest.py` (exists but limited)
**Issue:** Many UI tests create their own pygame_gui.UIManager instances. A shared fixture could reduce setup duplication and ensure consistent configuration.
**Impact:** No functional impact, but increased test setup code duplication.
**Recommendation:** Add shared fixtures for common UI test setup (UIManager, mock surfaces, etc.).
**Effort:** Simple

## Top 5 Priority Issues

1. **TCG-UI2-001 (CRITICAL)**: SystemTreePanel (418 LOC) has no tests. This is a complex hierarchical UI component used in the strategy screen - bugs could break system object selection entirely.

2. **TCG-UI2-002 (CRITICAL)**: BaseGallery abstract class lacks tests for its concrete methods. Both portrait and flag galleries depend on this shared logic for the race creation flow.

3. **TCG-UI2-003 (MAJOR)**: ShipDetailPanel (447 LOC) has no tests. This handles ship damage visualization and combat stats display - critical for fleet management.

4. **TCG-UI2-008 (MAJOR)**: draw_ship() renderer function (143 LOC) has no unit tests. While integration tests exist, the complex rendering math (culling, scaling, layer visualization) is not directly verified.

5. **TCG-UI2-010 (MAJOR)**: ShipThemeManager portrait loading is untested. The `_ship_class_to_portrait_name()` method has complex string parsing that could fail for unusual ship class names.
