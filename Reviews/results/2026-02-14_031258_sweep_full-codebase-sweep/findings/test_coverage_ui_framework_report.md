# Test Coverage Gaps Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Production Files Scanned:** 22
- **Test Files Cross-Referenced:** 28
- **Total Issues Found:** 11
- **Critical:** 1 | **Major:** 5 | **Minor:** 4 | **Info:** 1

## Scope Coverage

### Production Files Analyzed
| File | Test File Exists | Coverage Assessment |
|------|-----------------|---------------------|
| `game/ui/__init__.py` | N/A (exports only) | N/A |
| `game/ui/utils.py` | Yes | Good coverage |
| `game/ui/config.py` | Yes | Good coverage |
| `game/ui/colors.py` | Yes | Good coverage |
| `game/ui/services/vehicle_class_service.py` | Yes | Good coverage |
| `game/ui/services/component_service.py` | Yes | Good coverage |
| `game/ui/services/design_loader_adapter.py` | Yes | Good coverage |
| `game/ui/services/ship_io_adapter.py` | Yes | Good coverage |
| `game/ui/services/input_mapper.py` | Yes | Excellent coverage |
| `game/ui/services/tkinter_utils.py` | Yes | Good coverage |
| `game/ui/services/battle_factories.py` | Yes | Good coverage |
| `game/ui/services/battle_ui_service.py` | Yes | Good coverage |
| `game/ui/services/ship_io.py` | Yes | Excellent coverage |
| `game/ui/services/screenshot_manager.py` | Yes | Good coverage |
| `game/ui/services/ship_factory.py` | Yes | Good coverage |
| `game/ui/services/validation_service.py` | Yes | Good coverage |
| `game/ui/renderer/camera.py` | Yes | Good coverage |
| `game/ui/renderer/sprites.py` | Yes | Good coverage |
| `game/ui/renderer/game_renderer.py` | Yes | Moderate coverage |
| `game/ui/interfaces/battle_ui.py` | Yes | Good coverage |
| `game/ui/orchestration/battle_orchestrator.py` | Yes | Good coverage |
| `game/ui/assets/ship_theme_manager.py` | Yes | Good coverage |

## Findings

#### CRITICAL: Missing Tests for Validation Service Error Aggregation
**ID:** TCG-UI2-001
**Location:** `game/ui/services/validation_service.py` / `tests/unit/ui/services/test_validation_service.py`
**Issue:** The validation service tests primarily cover individual validation functions but lack comprehensive tests for error aggregation when multiple validation failures occur simultaneously. The `validate_design()` method can return multiple errors, but tests only verify single-error scenarios. Edge cases like partial component validity, mixed error types, and error priority ordering are not tested.
**Impact:** Validation bugs could allow invalid ship designs to pass validation, or valid designs could be incorrectly rejected. Users may not see all validation errors at once.
**Recommendation:** Add tests for:
- Multiple simultaneous validation failures
- Error message ordering and priority
- Boundary cases with exactly-at-limit values
- Interaction between different validation rules
**Effort:** Medium

#### MAJOR: BattleUIService Missing Tests for Edge-Case DTO Conversions
**ID:** TCG-UI2-002
**Location:** `game/ui/services/battle_ui_service.py` / `tests/unit/ui/services/test_battle_ui_service.py`
**Issue:** While basic DTO conversion is tested, the following edge cases lack coverage:
- Ships with empty `layers` dictionary
- Ships with `None` values for optional fields (secondary_targets, current_target)
- Projectiles with unknown AttackType values
- Ships with very large HP/shield values (potential display overflow)
- Ships with negative positions (off-screen coordinates)
**Impact:** UI could crash or display incorrect data when battle contains edge-case entities.
**Recommendation:** Add parametrized tests covering null/empty/boundary values for all DTO fields.
**Effort:** Medium

#### MAJOR: GameRenderer Missing Tests for Component Overlay Rendering
**ID:** TCG-UI2-003
**Location:** `game/ui/renderer/game_renderer.py` / `tests/unit/ui/renderer/test_game_renderer.py`
**Issue:** Tests verify that overlay mode draws circles, but do not verify:
- Correct positioning of component dots relative to ship position
- Color accuracy for different LayerTypes
- Component active/inactive state visual differentiation
- Weapon arc rendering (if applicable)
- Text label rendering for components
**Impact:** Visual bugs in overlay mode could confuse players about component positions and states.
**Recommendation:** Add tests that verify specific draw call parameters (position, color, radius) match expected values based on ship/component state.
**Effort:** Medium

#### MAJOR: Camera Missing Tests for Viewport Boundary Clipping
**ID:** TCG-UI2-004
**Location:** `game/ui/renderer/camera.py` / `tests/unit/ui/test_camera.py`
**Issue:** Tests cover coordinate transformations and zoom, but missing tests for:
- `is_visible()` method (checking if world coordinate is within viewport)
- Boundary clipping when camera approaches world edge
- Behavior when viewport size exceeds world size
- Pan limits/constraints (if any)
**Impact:** Objects could be rendered when off-screen or not rendered when on-screen, causing performance issues or visual glitches.
**Recommendation:** Add tests for viewport visibility checking and boundary conditions.
**Effort:** Simple

#### MAJOR: ShipThemeManager Missing Tests for Concurrent Image Loading
**ID:** TCG-UI2-005
**Location:** `game/ui/assets/ship_theme_manager.py` / `tests/unit/ui/test_theme_discovery.py`
**Issue:** While thread-safety tests exist for singleton access, there are no tests for:
- Concurrent `load_image()` calls for the SAME theme/ship_class (potential cache race)
- Loading while `clear()` is being called
- Memory pressure behavior (many themes loaded simultaneously)
- Image loading failure mid-operation (corrupt file discovered after partial read)
**Impact:** Thread-safety issues could cause image corruption or crashes in multi-threaded game scenarios.
**Recommendation:** Add stress tests for concurrent image operations and failure scenarios.
**Effort:** Complex

#### MAJOR: BattleOrchestrator Missing Tests for Ship with No AI Strategy
**ID:** TCG-UI2-006
**Location:** `game/ui/orchestration/battle_orchestrator.py` / `tests/unit/ui/test_battle_orchestrator.py`
**Issue:** Tests verify controller creation but don't test:
- Ships with `ai_strategy = None` or empty string
- Ships with unrecognized AI strategy names
- AI controller behavior when ship is already destroyed (is_alive=False)
- Controller cleanup when ships are removed mid-battle
**Impact:** Invalid AI strategy configurations could cause crashes or undefined behavior during battles.
**Recommendation:** Add tests for edge-case AI strategy values and ship lifecycle scenarios.
**Effort:** Medium

#### MINOR: InputMapper Missing Tests for Numpad Key Handling
**ID:** TCG-UI2-007
**Location:** `game/ui/services/input_mapper.py` / `tests/unit/ui/services/test_input_mapper.py`
**Issue:** Comprehensive tests exist for letter keys, modifiers, and function keys, but no explicit tests for:
- Numpad keys (K_KP0 through K_KP9)
- Numpad Enter vs regular Enter
- NumLock state interaction with key resolution
**Impact:** Players using numpad for shortcuts may experience inconsistent behavior.
**Recommendation:** Add tests verifying numpad key recognition and numlock handling.
**Effort:** Simple

#### MINOR: ScreenshotManager Missing Tests for Very Long Filenames
**ID:** TCG-UI2-008
**Location:** `game/ui/services/screenshot_manager.py` / `tests/unit/ui/services/test_screenshot_manager.py`
**Issue:** Tests cover basic capture and clipboard operations but don't test:
- Label parameter with very long strings (>255 characters)
- Label with path separator characters (/ or \)
- Label with non-ASCII characters
- Filename collision handling (same timestamp, same label)
**Impact:** Screenshot saves could fail silently or overwrite previous screenshots.
**Recommendation:** Add edge-case tests for filename generation and sanitization.
**Effort:** Simple

#### MINOR: ShipFactory Missing Tests for Invalid Design Data
**ID:** TCG-UI2-009
**Location:** `game/ui/services/ship_factory.py` / `tests/unit/ui/services/test_ship_factory.py`
**Issue:** Tests verify happy-path creation but don't verify behavior with:
- Missing required fields in design_data
- Invalid ship_class value (not in registry)
- Invalid layer names in layers dict
- Circular formation references
**Impact:** Invalid design files could cause obscure errors instead of clear validation messages.
**Recommendation:** Add tests for malformed design data with expected error handling.
**Effort:** Simple

#### MINOR: TkinterUtils Missing Tests for Dialog Cancellation Edge Cases
**ID:** TCG-UI2-010
**Location:** `game/ui/services/tkinter_utils.py` / `tests/unit/ui/services/test_tkinter_utils.py`
**Issue:** Tests verify dialog returns None when cancelled, but don't test:
- Dialog behavior when parent window is closed
- Dialog behavior when system dialog is force-closed (Alt+F4)
- Multiple rapid dialog open/close cycles
**Impact:** Edge-case dialog interactions could leave UI in inconsistent state.
**Recommendation:** These are difficult to test without actual GUI; document as known limitations.
**Effort:** Complex (may require manual testing)

#### INFO: Test Organization Observation
**ID:** TCG-UI2-011
**Location:** `tests/unit/ui/` directory structure
**Issue:** Test files are generally well-organized with good naming conventions. The pattern of `test_<module>.py` or `services/test_<service>.py` is consistently followed. Test classes are logically grouped (e.g., `TestInputMapperLoad`, `TestInputMapperResolve`). Mock fixtures are properly scoped with `pytest.fixture`. Edge case test classes are clearly labeled (e.g., `TestInputMapperEdgeCases`).
**Impact:** N/A - positive observation
**Recommendation:** Continue following this pattern for new tests. Consider adding a conftest.py with shared UI test fixtures if not already present.
**Effort:** N/A

## Top 5 Priority Issues

1. **TCG-UI2-001 (CRITICAL):** Validation Service Error Aggregation - Invalid designs could slip through or users may not see all validation errors. This directly affects user experience and game integrity.

2. **TCG-UI2-005 (MAJOR):** ShipThemeManager Concurrent Loading - Thread-safety issues during image loading could cause hard-to-reproduce crashes in production.

3. **TCG-UI2-002 (MAJOR):** BattleUIService DTO Edge Cases - UI crashes during battle would severely impact player experience in the core game loop.

4. **TCG-UI2-003 (MAJOR):** GameRenderer Component Overlay - Incorrect visual feedback in overlay mode could mislead players about ship capabilities.

5. **TCG-UI2-006 (MAJOR):** BattleOrchestrator AI Strategy Edge Cases - Invalid AI configurations causing mid-battle crashes would frustrate players.

## Notes

Overall, the UI Framework shard has **good test coverage**. Most production files have corresponding test files with reasonable coverage of happy-path scenarios. The main gaps are in edge-case handling and concurrent operation scenarios. The test infrastructure is mature with proper use of fixtures, mocks, and parametrization.

The existing tests follow good practices:
- Clear test method naming
- Proper use of pytest fixtures
- Appropriate mocking of external dependencies (pygame, tkinter, filesystem)
- Logical test class grouping by functionality
