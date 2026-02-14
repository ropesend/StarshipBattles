# Test Coverage Gaps Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Production Files Scanned:** 42
- **Test Files Cross-Referenced:** 88
- **Total Issues Found:** 18
- **Critical:** 3 | **Major:** 7 | **Minor:** 5 | **Info:** 3

## Findings

#### CRITICAL: PhysicsBody Class Has No Direct Unit Tests
**ID:** TCG-FND-001
**Location:** `game/engine/physics.py` (production) / No corresponding test file
**Issue:** The `PhysicsBody` class (base physics entity with position, velocity, acceleration, drag model) has no dedicated unit tests. While Ship extends this class and may exercise some functionality, the base class's core methods (`update()`, `apply_force()`, `forward_vector()`) are not directly tested in isolation. This is critical because PhysicsBody defines the fundamental physics behavior for all entities.
**Impact:** Bugs in base physics calculations (drag application, force integration, coordinate system handling) could propagate undetected through all physics-enabled entities.
**Recommendation:** Create `tests/unit/engine/test_physics_body.py` with tests for:
- `update()` method: acceleration integration, drag application, position/angle updates
- `apply_force()`: force-to-acceleration conversion with mass
- `forward_vector()`: angle-to-direction vector conversion
- Edge cases: zero mass, extreme drag values, boundary angle wrapping
**Effort:** Medium

#### CRITICAL: SpatialGrid Missing Comprehensive Unit Tests
**ID:** TCG-FND-002
**Location:** `game/engine/spatial.py` (production) / No corresponding test file
**Issue:** The `SpatialGrid` class is critical infrastructure for all proximity queries (collision detection, target acquisition). There are no dedicated unit tests for this class. Tests exist only in `tests/unit/engine/collision_edge_cases/` which focus on collision scenarios rather than the SpatialGrid API directly.
**Impact:** Bugs in spatial partitioning (incorrect cell calculations, missing candidates in query_radius) could cause collision detection failures or AI targeting issues.
**Recommendation:** Create `tests/unit/engine/test_spatial_grid.py` with tests for:
- `insert()`: correct bucket assignment, negative coordinates, large coordinate values
- `query_radius()`: returns correct candidates, boundary cases, overlapping cells
- `clear()`: properly resets all buckets
- Edge cases: very small/large cell sizes, objects at cell boundaries
**Effort:** Simple

#### CRITICAL: AIControllerFactory Missing Test Coverage
**ID:** TCG-FND-003
**Location:** `game/ai/ai_factory.py` (production) / No corresponding test file
**Issue:** The `AIControllerFactory` class has no dedicated unit tests. This factory is responsible for creating AI controllers for all ships in combat. The two-phase initialization pattern (create factory, then set_grid) and the RuntimeError on premature usage are untested.
**Impact:** Factory failures could break combat AI initialization entirely. The grid-not-set RuntimeError path is never verified.
**Recommendation:** Create `tests/unit/ai/test_ai_factory.py` with tests for:
- `set_grid()`: properly stores grid reference
- `create_for_ship()`: returns valid IAIController, uses ShipControllableAdapter
- `create_for_ship()` without grid: raises RuntimeError
- `create_for_ships()`: creates multiple controllers correctly
**Effort:** Simple

#### MAJOR: game/core/paths.py Missing Test Coverage
**ID:** TCG-FND-004
**Location:** `game/core/paths.py` (production) / `tests/unit/core/test_paths_config.py` exists but may be incomplete
**Issue:** The `Paths` class is used throughout the codebase for file locations. While `test_paths_config.py` exists, it needs verification that `_find_project_root()` error handling and all Path accessor methods are tested, especially the `ResourceException` raised when project root cannot be found.
**Impact:** Path resolution failures could cause cryptic errors across the entire application.
**Recommendation:** Verify test coverage includes:
- `_find_project_root()` failure scenario (ResourceException)
- All `get_*` class methods return correct Path objects
- String path attributes are valid
**Effort:** Simple

#### MAJOR: game/core/hex_math.py Edge Cases Undertested
**ID:** TCG-FND-005
**Location:** `game/core/hex_math.py` (production) / `tests/unit/core/test_hex_math_core.py` exists
**Issue:** While hex_math has a test file, the module needs verification that coordinate conversion edge cases are tested: negative coordinates, large coordinate values, boundary conditions at hex edges, and pathfinding edge cases.
**Impact:** Hex coordinate calculation bugs could cause incorrect positioning on the strategy map.
**Recommendation:** Verify or add tests for:
- Negative hex coordinates
- Very large coordinate values
- Coordinates at exact hex boundaries
- Hex ring generation edge cases
**Effort:** Simple

#### MAJOR: OrbitBehavior Missing Edge Case Tests
**ID:** TCG-FND-006
**Location:** `game/ai/behaviors.py` (OrbitBehavior class) / Tests in `tests/unit/ai/test_ai_behaviors.py`
**Issue:** The `OrbitBehavior` class has tests for basic functionality but lacks edge case coverage for:
- Target at same position as ship (dist == 0, returns early)
- No target provided (None target handling)
- Orbit distance thresholds (ORBIT_DISTANCE_CLOSE_THRESHOLD, ORBIT_DISTANCE_FAR_THRESHOLD)
**Impact:** Edge cases in orbit behavior could cause AI ships to behave erratically.
**Recommendation:** Add tests to `tests/unit/ai/test_ai_behaviors.py` for OrbitBehavior edge cases.
**Effort:** Simple

#### MAJOR: ErraticBehavior Uses random Without Seeding Control
**ID:** TCG-FND-007
**Location:** `game/ai/behaviors.py` (ErraticBehavior class)
**Issue:** `ErraticBehavior` uses `random.choice()` and `random.uniform()` directly without seeding control. Tests for this behavior may be non-deterministic/flaky. The behavior is marked as test/debug but is still production code.
**Impact:** Tests involving ErraticBehavior may intermittently fail. Reproducibility of AI behavior during debugging is compromised.
**Recommendation:** Either:
1. Add a seed parameter to ErraticBehavior for test determinism
2. Ensure tests mock random functions
3. Document that this behavior is intentionally non-deterministic
**Effort:** Simple

#### MAJOR: Research UI Components Have Thin Coverage
**ID:** TCG-FND-008
**Location:** `game/research/ui/research_renderer.py`, `game/research/ui/research_controls.py`, `game/research/ui/research_scene.py`
**Issue:** Research UI components have test files but coverage appears focused on happy paths. Missing tests for:
- Empty tech tree rendering
- Very long tech names/descriptions
- Extreme zoom levels
- Error states (missing data, corrupted state)
**Impact:** UI edge cases could cause visual glitches or crashes in the research screen.
**Recommendation:** Add edge case tests to research UI test files:
- Empty/null data handling
- Boundary value testing for zoom/scroll
- Invalid state handling
**Effort:** Medium

#### MAJOR: game/core/strategy_metadata.py Serialization Not Tested
**ID:** TCG-FND-009
**Location:** `game/core/strategy_metadata.py` / `tests/unit/core/test_strategy_metadata.py` exists
**Issue:** The `load_data()` method which loads strategy JSON files needs verification that JSON parsing errors, missing files, and malformed data are handled gracefully.
**Impact:** Corrupted or missing strategy JSON could crash the game during startup.
**Recommendation:** Add tests for:
- Missing strategy file handling
- Malformed JSON handling
- Empty strategies dict
- strategies key missing from JSON
**Effort:** Simple

#### MAJOR: collision.py Missing Direct Tests
**ID:** TCG-FND-010
**Location:** `game/engine/collision.py` (production) / Tests only in `tests/unit/engine/collision_edge_cases/`
**Issue:** While collision edge case tests exist, there's no direct test file for collision.py. The existing tests use fixtures and test collision scenarios through higher-level APIs. Direct unit tests for collision functions would improve coverage.
**Impact:** Collision detection bugs could cause missed hits or false positives.
**Recommendation:** Review collision.py public API and add direct unit tests if needed.
**Effort:** Medium

#### MINOR: game/core/__init__.py - No Tests Needed
**ID:** TCG-FND-011
**Location:** `game/core/__init__.py`
**Issue:** Package init file typically only contains exports - no tests needed unless it has complex logic.
**Impact:** N/A
**Recommendation:** Verify init file is export-only.
**Effort:** None

#### MINOR: game/ai/interfaces/__init__.py - No Tests Needed
**ID:** TCG-FND-012
**Location:** `game/ai/interfaces/__init__.py`
**Issue:** Package init file for exports only.
**Impact:** N/A
**Recommendation:** Verify init file is export-only.
**Effort:** None

#### MINOR: Test Behaviors (DoNothing, StationaryFire, etc.) Not Tested
**ID:** TCG-FND-013
**Location:** `game/ai/behaviors.py` (test behavior classes)
**Issue:** Test/debug behaviors (DoNothingBehavior, StationaryFireBehavior, StraightLineBehavior, RotateOnlyBehavior) have minimal or no tests. While these are test utilities, they should still have basic verification.
**Impact:** Test utilities could have bugs that confuse test results.
**Recommendation:** Add basic smoke tests for test behaviors to verify they don't crash.
**Effort:** Simple

#### MINOR: FormationBehavior Complex Logic Needs More Coverage
**ID:** TCG-FND-014
**Location:** `game/ai/behaviors.py` (FormationBehavior class) / `tests/unit/ai/formation_prediction/`
**Issue:** FormationBehavior has complex state machine logic (drift vs navigation, velocity sync, position correction). Tests exist but should verify:
- Deadband error handling (< 2.0 units)
- MAX_CORRECTION_FORCE capping
- Master death/derelict handling
- Rotation mode switching
**Impact:** Formation flying edge cases could cause ships to drift or oscillate.
**Recommendation:** Add targeted tests for FormationBehavior edge conditions.
**Effort:** Medium

#### MINOR: IControllable Interface Tests Could Be More Exhaustive
**ID:** TCG-FND-015
**Location:** `game/ai/interfaces/controllable.py` / `tests/unit/ai/controllable_interface/`
**Issue:** The IControllable interface has 30+ abstract methods. Tests exist for the adapter but should verify all interface methods are implemented correctly by ShipControllableAdapter.
**Impact:** Missing adapter method could cause AttributeError during combat.
**Recommendation:** Add exhaustive adapter method verification test.
**Effort:** Simple

#### INFO: Test File Organization Follows Good Patterns
**ID:** TCG-FND-016
**Location:** All test directories
**Issue:** Test file organization mirrors production structure well. Good use of conftest.py for shared fixtures. Test naming is consistent.
**Impact:** Positive - easy to locate tests for specific modules.
**Recommendation:** Continue following established patterns.
**Effort:** None

#### INFO: Research Module Has Strong Test Coverage
**ID:** TCG-FND-017
**Location:** `game/research/` / `tests/unit/research/`
**Issue:** The research module has comprehensive test coverage including edge cases for research service, tech tree, and tracker. The TCG-FND-009 tests added for process_turn demonstrate thorough testing.
**Impact:** Positive - research system is well-tested.
**Recommendation:** Maintain current test quality standard.
**Effort:** None

#### INFO: AI Module Has Good Coverage But Could Use More Integration
**ID:** TCG-FND-018
**Location:** `game/ai/` / `tests/unit/ai/`, `tests/integration/ai_strategy/`
**Issue:** AI module has extensive unit tests. Integration tests exist but could be expanded to test full combat AI scenarios with multiple ships, formation combat, and strategy transitions.
**Impact:** Unit tests pass but integration scenarios may have hidden bugs.
**Recommendation:** Consider adding more AI integration tests in simulation_tests/.
**Effort:** Medium

## Top 5 Priority Issues

1. **TCG-FND-001 (CRITICAL): PhysicsBody Class Has No Direct Unit Tests** - Fundamental physics calculations are untested. High risk of undetected bugs affecting all physics entities.

2. **TCG-FND-002 (CRITICAL): SpatialGrid Missing Comprehensive Unit Tests** - Critical infrastructure for collision detection and target acquisition has no dedicated tests.

3. **TCG-FND-003 (CRITICAL): AIControllerFactory Missing Test Coverage** - Factory pattern's error handling paths are completely untested.

4. **TCG-FND-010 (MAJOR): collision.py Missing Direct Tests** - Core collision detection module needs more direct unit test coverage.

5. **TCG-FND-008 (MAJOR): Research UI Components Have Thin Coverage** - UI edge cases for research screen could cause user-facing issues.
