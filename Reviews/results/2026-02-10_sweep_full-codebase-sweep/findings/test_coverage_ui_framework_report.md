# Test Coverage Gaps Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework (game/ui/ root + services/ + renderer/ + interfaces/ + orchestration/ + assets/)
- **Production Files Scanned:** 23 Python files
- **Test Files Cross-Referenced:** 13 test modules found
- **Total Issues Found:** 12
- **Critical:** 3 | **Major:** 5 | **Minor:** 4 | **Info:** 0

## Findings

#### CRITICAL: No Test Coverage for game_renderer.py Critical Rendering Functions
**ID:** TCG-UI2-001
**Location:** `c:\Dev\Starship Battles\game\ui\renderer\game_renderer.py`
**Issue:** The file contains two critical rendering functions (`draw_ship()` and `draw_hud()`) that have partial test coverage. `draw_ship()` is ~135 lines with complex logic for culling, theme loading, layer visualization, and component rendering. `draw_hud()` is ~70 lines handling ship stats display. While one test file (`test_rendering_logic.py`) attempts to test these functions, it uses heavy mocking that bypasses actual pygame rendering code paths. No integration tests verify the actual visual output or coordinate transformations during rendering.
**Impact:** Critical rendering pipeline is undertested. Edge cases like: invalid ship states, missing theme images, extreme zoom levels, viewport offset calculations, and resource display edge cases are not verified.
**Recommendation:** Add integration tests that:
1. Create real Ship objects with actual components
2. Render to actual pygame surfaces (not mocks)
3. Verify color-coded component rendering based on ability types
4. Test HUD stat calculations with edge cases (zero mass, missing resources, broken stats)
5. Test theme image loading fallback (missing images, corrupted files)
6. Test viewport culling with various camera positions and zoom levels
**Effort:** Complex

#### CRITICAL: SpriteManager Singleton Lacks Comprehensive Test Coverage
**ID:** TCG-UI2-002
**Location:** `c:\Dev\Starship Battles\game\ui\renderer\sprites.py`
**Issue:** SpriteManager is a thread-safe singleton (lines 6-164) with critical functionality:
- `load_sprites()` with fallback logic (directory → atlas file)
- `_load_from_directory()` parsing multiple naming conventions (Comp_*, 2048Portrait_Comp_*)
- Thread synchronization with locks
- Error handling for missing/corrupted image files

Current tests (`test_sprites.py`) only test happy path with real asset files. Missing coverage:
- Thread safety under concurrent access
- All error paths (missing directories, corrupted files, invalid filenames)
- Edge cases (empty sprite list, invalid indices, malformed image files)
- Fallback behavior when directory doesn't exist but atlas does
- Reset/singleton enforcement
**Impact:** Critical asset loading system could fail silently or crash with invalid input. Thread safety guarantees are unverified.
**Recommendation:** Add tests for:
1. Concurrent access from multiple threads (verify lock behavior)
2. Missing directory fallback to atlas file
3. Corrupted/invalid image files with graceful error handling
4. Naming convention parsing edge cases (malformed filenames, wrong prefixes)
5. Singleton enforcement (reset/instance creation)
6. Sparse sprite lists (missing indices)
7. Out-of-bounds sprite access
**Effort:** Complex

#### CRITICAL: ShipThemeManager Lazy Loading Has Untested Edge Cases
**ID:** TCG-UI2-003
**Location:** `c:\Dev\Starship Battles\game\ui\assets\ship_theme_manager.py`
**Issue:** ShipThemeManager (150+ lines) implements lazy-loading theme discovery with complex state management:
- Thread-safe initialization with double-checked locking
- Lazy image loading with caching
- Metrics caching for visible portion calculations
- Portrait image caching
- Discovery vs. load state separation

Current tests (`test_theme_discovery.py`) verify basic theme discovery but miss critical edge cases:
- Behavior when theme.json is missing or malformed
- Behavior when image files referenced in theme.json don't exist
- Cache invalidation and re-discovery
- Thread safety under concurrent image loading
- Fallback behavior (missing themes, missing classes)
- Metrics calculation accuracy
- Clear() vs reset() lifecycle
**Impact:** Theme system could fail with confusing errors or inconsistent state. Cache invalidation issues could lead to stale theme data.
**Recommendation:** Add comprehensive tests for:
1. Malformed or missing theme.json files
2. Concurrent theme loading from multiple threads
3. Cache behavior (hit/miss rates, invalidation)
4. Fallback when requested theme/class doesn't exist
5. Metrics caching accuracy
6. Portrait loading and caching
7. Clear() and reset() behavior and state cleanup
8. Edge cases: empty theme directories, invalid JSON, circular references
**Effort:** Complex

#### MAJOR: Camera.py Lacks Edge Case and Integration Testing
**ID:** TCG-UI2-004
**Location:** `c:\Dev\Starship Battles\game\ui\renderer\camera.py`
**Issue:** Camera class (155 lines) implements critical viewport management with:
- Smooth zoom interpolation with anchor point tracking
- Target following with dead target handling
- Viewport offset support
- Input handling for keyboard/mouse
- Coordinate transformation (world ↔ screen)
- Object fitting

Existing tests (`test_camera.py`) cover basic transformations but lack:
- Zoom anchor stability during animation (pixel-perfect verification)
- Dead target following behavior
- Offset application in transformations
- Input accumulation (multiple events)
- Zoom limits enforcement during animation
- Edge cases: negative zoom, extreme coordinates, null targets
- Integration with actual game objects (Ships with physics)
**Impact:** Camera could behave unexpectedly in edge cases (viewport jitter during zoom, incorrect dead reckoning for moving targets, coordinate misalignment with offsets).
**Recommendation:** Add tests for:
1. Zoom anchor stability (verify screen point doesn't move during animation)
2. Dead target following (dead ships render at corpse location)
3. Offset propagation in all transformations
4. Multiple sequential zoom operations
5. Manual pan breaking target focus
6. Edge cases: zero zoom, infinite coordinates, null objects
7. Integration tests with moving Ship objects
**Effort:** Medium

#### MAJOR: BattleUIService DTO Conversion Missing Error Path Tests
**ID:** TCG-UI2-005
**Location:** `c:\Dev\Starship Battles\game\ui\services\battle_ui_service.py`
**Issue:** BattleUIService (100+ lines) converts simulation objects to immutable DTOs. Current test coverage (`test_conversion.py`, `test_state_and_integration.py`) tests happy paths but lacks:
- Null/None battle engine handling (verified in is_battle_over but not in get_ships/get_projectiles)
- Invalid target references (stale target pointers)
- Missing components or corrupt layer data
- Resource dictionary edge cases (missing resource types, zero values)
- Extreme stat values (negative HP, unbounded speeds)
- Winner determination with edge cases (no team representatives alive, invalid team_id)
- Thread safety of get_recent_beams (is it cleared atomically?)
- Conversion of derelict ships (status generation logic)
**Impact:** UI could crash or display corrupted data when simulation objects are in edge cases. DTOs could expose inconsistent state.
**Recommendation:** Add tests for:
1. All None/null paths in conversions
2. Invalid target references
3. Missing component types
4. Resource edge cases (missing, zero, NaN values)
5. Stat extremes (negative HP, zero mass, unbounded thrust)
6. Derelict ship status conversion
7. Winner determination logic with edge team compositions
8. Recent beams list atomic access and clearing
**Effort:** Medium

#### MAJOR: game/ui/utils.py Image Scaling Functions Need Edge Case Testing
**ID:** TCG-UI2-006
**Location:** `c:\Dev\Starship Battles\game\ui\utils.py`
**Issue:** File contains 6 public image scaling/manipulation functions (lines 32-220):
- `calculate_ship_image_scale()` - scale factor calculation
- `scale_and_rotate_image()` - scaling + rotation
- `get_visible_bounding_box()` - transparent pixel detection
- `scale_image_by_visible_portion()` - smart scaling
- `scale_image_to_fit()` - fit-to-bounds scaling

Tests (`test_utils.py`) cover basic cases but lack:
- Rotation edge cases (90°, 180°, 270°, non-integer angles)
- Alpha threshold boundary conditions (0, 10, 255 pixels)
- Extreme scale factors (0.001x, 100x)
- Fully transparent surfaces
- Surfaces with alpha=0 but opaque pixels
- Very small images (1x1, 2x2)
- Scale factor precision (floats vs. integers)
- Rotation + scale combination verification
- Background color handling in scale_image_to_fit
**Impact:** Ship rendering could have visual artifacts, incorrect sizing, or fail with extreme scales. Transparent detection could incorrectly identify non-transparent areas.
**Recommendation:** Add tests for:
1. All rotation angles (0, 45, 90, 180, 270, 359)
2. Alpha threshold extremes and boundary cases
3. Very small image handling (1x1, 2x2)
4. Fully transparent surfaces
5. Scale factor edge cases (0.001x, 100x, negative)
6. Combined rotation + scale operations
7. Background color verification in fit function
8. Placeholder generation with various dimensions
**Effort:** Medium

#### MAJOR: Vehicle/Component Service Tests Missing Modifier Restrictions Deep Paths
**ID:** TCG-UI2-007
**Location:** `c:\Dev\Starship Battles\game\ui\services\component_service.py` and `vehicle_class_service.py`
**Issue:** ComponentService.is_modifier_allowed() (lines 76-100+) implements restriction checking with multiple branches (allow_types, forbid_types, require_abilities, forbid_abilities). Current tests only verify:
- No restrictions (always allowed)
- Basic single restriction type

Missing:
- Multiple restriction types simultaneously
- Ability restriction checking (require_abilities, forbid_abilities)
- Component with no abilities
- Component with multiple abilities
- Negative/inverse restrictions (forbid_types, forbid_abilities)
- Restriction conflicts (can't simultaneously require X and forbid X)

VehicleClassService has minimal test coverage for get_classes_for_type() edge cases:
- Empty vehicle class registry
- Classes without type field (defaults to 'Ship')
- Filtering accuracy
- Sorting behavior
**Impact:** Modifier restrictions could be incorrectly applied, allowing invalid modifications or blocking valid ones.
**Recommendation:** Add tests for:
1. All restriction type combinations
2. Ability-based restrictions (require/forbid)
3. Multi-ability components with complex restrictions
4. Restriction conflict detection
5. VehicleClassService with empty registry
6. Type filtering accuracy
7. Max mass extraction
8. Edge cases (None values, missing fields)
**Effort:** Medium

#### MINOR: game/ui/colors.py Has No Dedicated Test Module
**ID:** TCG-UI2-008
**Location:** `c:\Dev\Starship Battles\game\ui\colors.py`
**Issue:** Pure color constant definitions (lines 4-35) with 16 color tuples. No dedicated test file. Color values are used throughout rendering but never validated for:
- RGB value ranges (should be 0-255)
- Tuple format consistency
- Color name uniqueness
- Visual contrast ratios for accessibility
- Hex vs. RGB consistency (if dual-defined anywhere)
**Impact:** Low (hardcoded constants), but incorrect colors could affect game aesthetics.
**Recommendation:** Add minimal test to verify:
1. All color tuples have 3 components (R, G, B)
2. All components are in range [0, 255]
3. No duplicate color definitions
4. Color names are descriptive and unique
**Effort:** Simple

#### MINOR: widgets.py Legacy Code Lacks Button/Label/Slider Integration Tests
**ID:** TCG-UI2-009
**Location:** `c:\Dev\Starship Battles\game\ui\widgets.py`
**Issue:** Legacy widget classes (Button, Label, Slider - lines 5-102) have basic unit tests but lack:
- Draw method verification (pixels rendered correctly)
- State transitions (hover → click, drag states)
- Callback execution timing
- Multiple simultaneous buttons
- Slider value clamping edge cases
- Font rendering failures
- Very large/small dimensions
- Integration with actual pygame event systems
**Impact:** Low (legacy code, likely superseded), but button interaction bugs could affect menus.
**Recommendation:** Add tests for:
1. Draw output verification (not just call counts)
2. State machine transitions
3. Edge case dimensions (0 width, 10000px, negative)
4. Slider value precision
5. Multiple button interactions
**Effort:** Simple

#### MINOR: ShipIOAdapter and ValidationService Missing Error Case Testing
**ID:** TCG-UI2-010
**Location:** `c:\Dev\Starship Battles\game\ui\services\ship_io_adapter.py` and `validation_service.py`
**Issue:** Both adapter services are thin wrappers tested at the happy path but lacking:
- File I/O error scenarios (permission denied, disk full, path too long)
- Validator returning None or invalid results
- Edge cases in folder path handling
- Unicode filename handling
- Concurrent access to file operations
**Impact:** Low (errors propagate from underlying systems), but error messages could be unhelpful.
**Recommendation:** Add tests for error paths (at mock level) and verify error propagation.
**Effort:** Simple

#### MINOR: Orchestration/Interfaces Missing Cross-Layer Integration Tests
**ID:** TCG-UI2-011
**Location:** `c:\Dev\Starship Battles\game\ui\orchestration/` and `game/ui/interfaces/`
**Issue:** BattleOrchestrator and IBattleUI protocol have unit tests but no integration tests verifying:
- AIController creation with real Ship objects
- Protocol implementation completeness
- DTO immutability enforcement across layers
- Type checking with real protocol instances
**Impact:** Low (protocol contracts verified at unit level), but integration could fail silently.
**Recommendation:** Add integration tests creating real objects and verifying protocol satisfaction.
**Effort:** Simple

#### INFO: __init__.py Files Have Module-Level Import Ordering But No Tests
**ID:** TCG-UI2-012
**Location:** `c:\Dev\Starship Battles\game\ui/__init__.py`
**Issue:** Root __init__.py (lines 1-27) has intentional import ordering to prevent pytest-xdist race conditions and excludes workshop_screen due to Tkinter side effects. No tests verify:
- All expected modules are importable
- Import order is maintained
- Circular dependency prevention
- Side effect avoidance (workshop_screen not imported)
**Impact:** Very low (import-time issues caught quickly during test runs), but regression possible.
**Recommendation:** Add basic import test to verify module initialization.
**Effort:** Simple

## Top 5 Priority Issues

1. **TCG-UI2-001: game_renderer.py Critical Rendering Functions** 
   - Impact: Rendering pipeline almost untested, heavy reliance on mocks hiding real issues
   - Complexity: High but necessary for correctness
   - Effort: Complex
   - Blocks: All UI visual correctness

2. **TCG-UI2-002: SpriteManager Singleton Threading & Fallback Logic**
   - Impact: Asset loading could fail silently, thread safety unverified
   - Complexity: High (threading, file I/O, fallback paths)
   - Effort: Complex
   - Blocks: Asset pipeline reliability

3. **TCG-UI2-003: ShipThemeManager Lazy Loading Edge Cases**
   - Impact: Theme system could have stale cache, missing fallback behavior
   - Complexity: High (caching, lazy loading, file I/O)
   - Effort: Complex
   - Blocks: Theme system reliability

4. **TCG-UI2-004: Camera.py Zoom Anchor & Offset Handling**
   - Impact: Viewport could jitter, dead targets render incorrectly, offset breaks
   - Complexity: Medium (math-heavy but isolated)
   - Effort: Medium
   - Blocks: Battle UI camera fluidity

5. **TCG-UI2-005: BattleUIService DTO Error Paths**
   - Impact: UI could crash with corrupted battle state
   - Complexity: Medium (many paths but straightforward)
   - Effort: Medium
   - Blocks: Battle UI stability
