# Test Coverage Gaps Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Production Files Scanned:** 42
- **Test Files Cross-Referenced:** 86
- **Total Issues Found:** 18
- **Critical:** 2 | **Major:** 8 | **Minor:** 6 | **Info:** 2

## Findings

### Core Layer (game/core/)

#### CRITICAL: `game/core/profiling.py` - Missing Unit Tests for Core Profiling Functions
**ID:** TCG-FND-001
**Location:** `game/core/profiling.py` (production) / `tests/unit/core/profiling/` (test gap)
**Issue:** The profiling module has tests for recording/persistence/decorators, but the core timing functions (`start_timer`, `stop_timer`, `profile_context`) lack direct unit tests. These are used throughout the codebase for performance monitoring. No tests verify timer accuracy, nested timer behavior, or what happens when stop_timer is called without start_timer.
**Impact:** Profiling bugs could go undetected, masking performance regressions. Incorrect timing data could lead to false optimization decisions.
**Recommendation:** Add tests for `start_timer`/`stop_timer` pairs, nested profiling contexts, error handling for mismatched calls, and timer accuracy bounds.
**Effort:** Medium

#### MAJOR: `game/core/protocols.py` - Incomplete Protocol Conformance Tests
**ID:** TCG-FND-002
**Location:** `game/core/protocols.py` (production) / `tests/unit/core/test_protocols.py` (partial coverage)
**Issue:** The protocols module defines type protocols (`IRegistry`, etc.) for structural typing, but test coverage only verifies that protocols are importable and basic method signatures. No tests verify that actual implementations across the codebase properly conform to these protocols.
**Impact:** Interface contracts could drift from implementations without detection, causing runtime errors in production.
**Recommendation:** Add conformance tests that verify real classes implement protocol methods correctly (using `isinstance` checks with runtime_checkable protocols).
**Effort:** Medium

#### MAJOR: `game/core/resources.py` - Edge Cases Not Tested
**ID:** TCG-FND-003
**Location:** `game/core/resources.py` (production) / `tests/unit/core/test_resource_loading.py` (partial coverage)
**Issue:** The `load_resources_data` function has extensive error handling (FileNotFoundError, JSONDecodeError, PermissionError, TypeError), but tests only cover the happy path and basic file-not-found fallback. No tests verify behavior when JSON is malformed, when permissions are denied, or when the data structure is malformed (e.g., `resources` is not a list).
**Impact:** Edge case bugs in resource loading could cause silent fallback to defaults when actual configuration errors exist, hiding problems.
**Recommendation:** Add tests for each exception branch: malformed JSON, permission errors, malformed data structure (TypeError/AttributeError paths).
**Effort:** Simple

#### MAJOR: `game/core/registry.py` - TestRegistryProvider Edge Cases Not Covered
**ID:** TCG-FND-004
**Location:** `game/core/registry.py` (production) / `tests/unit/core/` (test gap)
**Issue:** `TestRegistryProvider` class is used extensively in tests but has no dedicated tests for its own behavior. No tests verify that it correctly isolates data between instances, that modifying one provider's data doesn't affect another, or that `get_vehicle_classes()` works correctly.
**Impact:** Test isolation assumptions could be incorrect, causing cross-test contamination bugs that are hard to diagnose.
**Recommendation:** Add unit tests for `TestRegistryProvider` verifying complete isolation between instances and correct behavior of all three getter methods.
**Effort:** Simple

#### MINOR: `game/core/input_actions.py` - Missing Tests for New Input Actions
**ID:** TCG-FND-005
**Location:** `game/core/input_actions.py` (production) / `tests/unit/core/test_input_actions.py` (partial coverage)
**Issue:** Tests exist for `InputActions` class but rely on checking specific action names exist. If new actions are added without updating tests, no test failure alerts developers. No test verifies that action names are unique or that all actions have valid key bindings.
**Impact:** New input actions could be added with duplicate names or invalid bindings without test detection.
**Recommendation:** Add test that verifies action name uniqueness and that all actions have required fields (key binding, category, etc.).
**Effort:** Simple

#### MINOR: `game/core/paths.py` - No Direct Unit Tests
**ID:** TCG-FND-006
**Location:** `game/core/paths.py` (production) / `tests/unit/core/test_paths_config.py` (partial coverage)
**Issue:** The `Paths` class provides essential path constants (`ROOT_DIR`, `DATA_DIR`, `ASSETS_DIR`). Existing tests verify config paths but don't verify that `Paths.ROOT_DIR` correctly resolves to the actual project root, or that all path attributes exist and are valid directories.
**Impact:** Path misconfiguration could cause file loading failures that are only discovered at runtime.
**Recommendation:** Add tests that verify `Paths.ROOT_DIR` exists, that all defined paths are valid directories (or at least resolvable), and that relative path construction works correctly.
**Effort:** Simple

### AI Layer (game/ai/)

#### MAJOR: `game/ai/behaviors.py` - Orbit and Erratic Behaviors Undertested
**ID:** TCG-FND-007
**Location:** `game/ai/behaviors.py` (production) / `tests/unit/ai/test_ai_behaviors.py` (partial coverage)
**Issue:** `OrbitBehavior` and `ErraticBehavior` have no dedicated test cases. Tests exist for KiteBehavior, AttackRunBehavior, FormationBehavior, but orbital mechanics and random behavior patterns are not verified. `OrbitBehavior.update()` has complex radial/tangent vector math that is untested.
**Impact:** Orbit behavior bugs could cause ships to spiral in/out incorrectly. Erratic behavior timing issues could cause predictable patterns.
**Recommendation:** Add tests for OrbitBehavior: target at orbit distance, too close, too far, no target. Add tests for ErraticBehavior: direction changes occur, timer resets correctly.
**Effort:** Medium

#### MAJOR: `game/ai/controller.py` - `navigate_to` Edge Cases Untested
**ID:** TCG-FND-008
**Location:** `game/ai/controller.py` (production) / `tests/unit/ai/test_ai.py` (partial coverage)
**Issue:** The `navigate_to()` method is tested indirectly through behavior tests, but edge cases are not covered: what happens when target position equals current position? What if stop_dist is negative? What if ship has no turn speed? The rotation deadband logic is also untested.
**Impact:** Navigation bugs at edge cases could cause ships to spin infinitely or fail to stop at destinations.
**Recommendation:** Add direct unit tests for `navigate_to()` with: target at current position, very small distances, zero turn speed, negative stop_dist, targets exactly at stop_dist threshold.
**Effort:** Medium

#### MAJOR: `game/ai/ai_factory.py` - No Unit Tests
**ID:** TCG-FND-009
**Location:** `game/ai/ai_factory.py` (production) / No test file exists
**Issue:** `AIControllerFactory` has no dedicated unit tests. The factory is tested indirectly through integration tests, but no unit tests verify: `set_grid()` must be called before `create_for_ship()`, `create_for_ships()` handles empty list, error raised when grid not set.
**Impact:** Factory initialization bugs could cause cryptic runtime errors in battle setup.
**Recommendation:** Add unit tests for: factory creation, set_grid required before create, create_for_ships with empty list, create_for_ship returns IAIController.
**Effort:** Simple

#### MINOR: `game/ai/target_evaluator.py` - Speed Rule Edge Cases
**ID:** TCG-FND-010
**Location:** `game/ai/target_evaluator.py` (production) / `tests/unit/ai/target_evaluator/` (partial coverage)
**Issue:** `_eval_speed_rule()` extracts velocity via `getattr(candidate, 'velocity', Vector2(0, 0)).length()`. No tests verify behavior when velocity attribute is missing, when velocity is (0,0), or when velocity is very large.
**Impact:** Targeting could fail silently or produce incorrect scores for stationary targets.
**Recommendation:** Add tests for: missing velocity attribute fallback, zero velocity case, very large velocity values.
**Effort:** Simple

### Research Layer (game/research/)

#### MAJOR: `game/research/data/tech_tree.py` - `validate()` Method Untested
**ID:** TCG-FND-011
**Location:** `game/research/data/tech_tree.py` (production) / `tests/unit/research/tech_tree/` (partial coverage)
**Issue:** The `validate()` method combines `validate_requirements()` and `detect_cycles()`, but no test verifies the combined output. `validate_requirements()` has tests for missing refs, `detect_cycles()` has tests for cycles, but no test verifies that `validate()` returns all errors from both functions correctly aggregated.
**Impact:** Validation could incorrectly report errors from only one check, missing the other.
**Recommendation:** Add test that creates a tree with both missing refs AND a cycle, verify `validate()` returns errors for both issues.
**Effort:** Simple

#### MINOR: `game/research/systems/research_service.py` - No Boundary Tests for MAX_CHANCE
**ID:** TCG-FND-012
**Location:** `game/research/systems/research_service.py` (production) / `tests/unit/research/test_research_service.py` (partial coverage)
**Issue:** Tests verify that chance is capped at MAX_CHANCE (0.95), but no tests verify behavior at exactly MAX_CHANCE, or what happens when multiple nodes all hit MAX_CHANCE in the same turn.
**Impact:** Edge case bugs in chance capping could cause unexpected probability behavior.
**Recommendation:** Add tests for: exact MAX_CHANCE boundary, multiple nodes at MAX_CHANCE, verify roll comparison at boundary.
**Effort:** Simple

#### MINOR: `game/research/ui/research_controls.py` - No Unit Tests for Input Handling
**ID:** TCG-FND-013
**Location:** `game/research/ui/research_controls.py` (production) / `tests/unit/research/research_controls/` (partial coverage)
**Issue:** Research controls have tests for event formatting and node selection, but keyboard/mouse input handling is not tested. No tests for: scroll wheel behavior, click events, keyboard shortcuts.
**Impact:** Input handling bugs could cause unresponsive research UI.
**Recommendation:** Add tests for input event handling: mouse clicks on nodes, scroll wheel zoom, keyboard shortcuts if any.
**Effort:** Medium

### Engine Layer (game/engine/)

#### CRITICAL: `game/engine/collision.py` - Division by Zero Not Tested
**ID:** TCG-FND-014
**Location:** `game/engine/collision.py` (production) / `tests/unit/engine/collision_edge_cases/` (partial coverage)
**Issue:** The beam attack raycasting code has a guard for `a == 0` (zero-length direction vector), but this guard path is not directly tested with assertions on the result values. Tests only verify "should not crash" but don't verify correct behavior (what values should t1/t2 be?). The code sets `t1 = t2 = 0` which means hit would be at origin, which may not be intended behavior.
**Impact:** Zero-length direction beams could produce incorrect hit calculations, potentially hitting unintended targets.
**Recommendation:** Add explicit test that verifies zero-direction beam behavior: either no hit should be registered, or hit should be at origin with clear documentation of intended behavior.
**Effort:** Simple

#### MAJOR: `game/engine/spatial.py` - Large Radius Query Performance Not Tested
**ID:** TCG-FND-015
**Location:** `game/engine/spatial.py` (production) / `tests/unit/systems/test_spatial.py` (partial coverage)
**Issue:** `query_radius()` calculates cell steps as `int(math.ceil(radius / self.cell_size))`. No tests verify behavior with very large radii (e.g., 1000000) that would query millions of cells, or with very small radii that might round to 0 steps.
**Impact:** Performance issues with large radii could cause frame drops during combat. Zero-step queries could miss nearby objects.
**Recommendation:** Add tests for: very large radius (verify doesn't freeze/memory error), very small radius (verify objects in same cell still found), radius exactly equal to cell_size.
**Effort:** Simple

#### MINOR: `game/engine/physics.py` - Drag Clamping Edge Case
**ID:** TCG-FND-016
**Location:** `game/engine/physics.py` (production) / `tests/unit/systems/test_physics.py` (partial coverage)
**Issue:** The update method has `if drag_factor > 1: drag_factor = 1` but no test verifies this clamping works correctly, or what happens with negative drag values. Setting drag > 1 would cause velocity to flip direction without the clamp.
**Impact:** Drag misconfiguration could cause physics anomalies.
**Recommendation:** Add tests for: drag > 1 is clamped, drag = 1 results in zero velocity, drag = 0 preserves velocity, negative drag behavior.
**Effort:** Simple

### Integration Test Gaps

#### INFO: No End-to-End AI Strategy Resolution Tests
**ID:** TCG-FND-017
**Location:** `game/ai/strategy_manager.py` + `game/ai/controller.py` (cross-system)
**Issue:** `StrategyManager.resolve_strategy()` combines strategy definition, targeting policy, and movement policy into a single resolved object. No integration test verifies the full resolution chain from strategy ID to behavior execution with real policy files.
**Impact:** Strategy resolution bugs could cause incorrect AI behavior that only manifests in actual gameplay.
**Recommendation:** Add integration test that loads real strategy files, resolves a strategy, and verifies the AIController executes correct behavior based on resolved policy.
**Effort:** Medium

#### INFO: Research UI Integration with Service Layer Undertested
**ID:** TCG-FND-018
**Location:** `game/research/ui/research_scene.py` + `game/research/systems/research_service.py` (cross-system)
**Issue:** Research UI tests mock the research service. No integration test verifies that the actual ResearchService processes turns correctly when triggered by UI events.
**Impact:** UI-to-service integration bugs could cause research progress not to apply correctly.
**Recommendation:** Add integration test that creates ResearchScene with real TechTree and ResearchTracker, processes turns via UI interaction, verifies service state changes.
**Effort:** Medium

## Top 5 Priority Issues

1. **TCG-FND-001 (CRITICAL)** - Core profiling functions lack unit tests. These are used throughout the codebase for performance monitoring.

2. **TCG-FND-014 (CRITICAL)** - Collision system division-by-zero guard has unclear intended behavior and is not properly tested.

3. **TCG-FND-007 (MAJOR)** - OrbitBehavior's complex orbital mechanics math is completely untested, risking AI navigation bugs.

4. **TCG-FND-008 (MAJOR)** - AIController.navigate_to() edge cases (same position, zero turn speed) are untested.

5. **TCG-FND-009 (MAJOR)** - AIControllerFactory has no unit tests despite being the factory for all AI controllers in battle.
