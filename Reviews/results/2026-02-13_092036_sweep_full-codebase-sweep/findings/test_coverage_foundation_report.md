# Test Coverage Gaps Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Production Files Scanned:** 33
- **Test Files Cross-Referenced:** 92
- **Total Issues Found:** 14
- **Critical:** 2 | **Major:** 5 | **Minor:** 5 | **Info:** 2

## Findings

#### CRITICAL: PhysicsBody Has Minimal Direct Unit Tests
**ID:** TCG-FND-001
**Location:** `game/engine/physics.py` (production) / `tests/unit/systems/test_physics_edge_cases.py` (partial tests)
**Issue:** PhysicsBody is the foundational class for all physical entities, yet direct unit tests only cover edge cases (velocity, mass, drag). Missing tests for:
- `update()` method integration (acceleration application, drag factor clamping, position/angle updates)
- `apply_force()` method with various force magnitudes and mass values
- `forward_vector()` method with various angles
- Property setters (x, y) and their interaction with Vector2 position
- Interaction between linear and angular drag in the same update cycle
**Impact:** PhysicsBody behavior changes could silently break ship movement, projectile physics, and combat mechanics without detection.
**Recommendation:** Create `tests/unit/engine/test_physics_body.py` with comprehensive tests for all public methods and properties.
**Effort:** Medium

#### CRITICAL: Research UI Components Have No Pygame-Independent Unit Tests
**ID:** TCG-FND-002
**Location:** `game/research/ui/research_controls.py`, `game/research/ui/research_renderer.py` (production) / `tests/unit/research/` (tests exist but mock pygame)
**Issue:** The research UI components (ResearchControlPanel, ResearchRenderer) have limited testable behavior extraction. Current tests exist but focus on event formatting and state management. Missing tests for:
- `ResearchRenderer._draw_dashed_line()` math calculations (dashed line rendering for negated requirements)
- `ResearchRenderer._get_font()` cache quantization logic
- `ResearchControlPanel._update_allocation_slider_range()` boundary calculations
- `ResearchControlPanel.update_turn_log()` HTML truncation logic (keeping last 5 turns)
**Impact:** UI rendering bugs could go undetected; font cache could grow unboundedly; log truncation could fail.
**Recommendation:** Extract pure-logic methods from UI classes into testable utility functions, or add targeted mocked tests for the calculation logic.
**Effort:** Complex

#### MAJOR: CollisionSystem Missing Integration Tests with Real Ship Components
**ID:** TCG-FND-003
**Location:** `game/engine/collision.py` (production) / `tests/unit/engine/collision_edge_cases/` (exists)
**Issue:** While `test_beam_ramming.py` has extensive tests, they use heavy mocking. Missing integration tests for:
- `process_beam_attack()` with real BeamWeaponAbility instances and ship components
- Sensor score and defense score calculation flow through the hit chance formula
- Damage pipeline from beam hit through `combat_engine.take_damage()`
**Impact:** Integration bugs between collision detection and ship component systems could go undetected.
**Recommendation:** Add integration tests in `tests/integration/combat/` that exercise the full damage pipeline with minimal mocking.
**Effort:** Medium

#### MAJOR: TechTree.detect_cycles() Has Limited Cycle Detection Test Coverage
**ID:** TCG-FND-004
**Location:** `game/research/data/tech_tree.py` (production) / `tests/unit/research/tech_tree/test_loading.py` (partial)
**Issue:** The cycle detection algorithm is complex (DFS with recursion stack), but tests only verify basic cycle detection. Missing tests for:
- Multi-node cycles (A -> B -> C -> A)
- Self-referential cycles (A -> A)
- Cycles involving negated requirements (should they be ignored?)
- Very deep dependency chains without cycles (performance edge case)
**Impact:** Malformed tech tree JSON could cause infinite loops or incorrect validation.
**Recommendation:** Add dedicated `test_cycle_detection.py` with parameterized cycle scenarios.
**Effort:** Simple

#### MAJOR: AI FleeHehavior Has No Direct Tests
**ID:** TCG-FND-005
**Location:** `game/ai/behaviors.py` (production) / `tests/unit/ai/test_ai_behaviors.py` (partial)
**Issue:** `test_ai_behaviors.py` tests KiteBehavior, FormationBehavior, and RamBehavior, but FleeHehavior has no tests. Missing tests for:
- Flee direction calculation (away from threat)
- Speed multiplier application
- Interaction with collision avoidance during flee
**Impact:** Flee behavior regressions would go undetected; ships might flee toward enemies instead of away.
**Recommendation:** Add `TestFleeBehavior` class to `test_ai_behaviors.py`.
**Effort:** Simple

#### MAJOR: TargetEvaluator Rule Processing Missing Boundary Tests
**ID:** TCG-FND-006
**Location:** `game/ai/target_evaluator.py` (production) / `tests/unit/ai/target_evaluator/test_evaluation_rules.py` (exists)
**Issue:** Target evaluator has tests for individual rules, but missing tests for:
- Rule processing order (first match vs. cumulative scoring)
- Empty rules list behavior
- Rules with zero weight/score
- Very large rule lists (performance)
- Rules referencing nonexistent component abilities
**Impact:** Targeting could behave unexpectedly with edge-case strategy configurations.
**Recommendation:** Add boundary and edge-case tests to `test_evaluation_rules.py`.
**Effort:** Simple

#### MAJOR: AIControllerFactory Missing Error Path Tests
**ID:** TCG-FND-007
**Location:** `game/ai/ai_factory.py` (production) / `tests/unit/simulation/factories/test_ai_factory.py` (exists)
**Issue:** Factory tests verify happy path, but missing:
- What happens when ship has no valid strategy ID?
- What happens when grid is set to None after being set?
- Memory/resource cleanup when controllers are discarded
**Impact:** Production edge cases could cause crashes or resource leaks.
**Recommendation:** Add error path tests to `test_ai_factory.py`.
**Effort:** Simple

#### MINOR: game/core/protocols.py ICamera Interface Missing Validation Tests
**ID:** TCG-FND-008
**Location:** `game/core/protocols.py` (production) / `tests/unit/core/test_protocols.py` (exists but limited)
**Issue:** ICamera protocol defines methods like `world_to_screen()`, `screen_to_world()` but tests only verify protocol existence, not that implementations conform correctly. Missing:
- Tests that verify Camera class actually implements ICamera correctly
- Tests for edge cases (negative coordinates, extreme zoom values)
**Impact:** Camera implementations could drift from protocol expectations without test failures.
**Recommendation:** Add protocol conformance tests for actual implementations.
**Effort:** Simple

#### MINOR: hex_math.py Missing Tests for Large Coordinate Values
**ID:** TCG-FND-009
**Location:** `game/core/hex_math.py` (production) / `tests/unit/core/test_hex_math_core.py` (61 tests)
**Issue:** Tests cover typical coordinate ranges but missing:
- Very large hex coordinates (overflow potential)
- Negative hex coordinates
- Hex distance calculations at map boundaries
**Impact:** Galaxy map with large coordinate ranges could have calculation errors.
**Recommendation:** Add parameterized tests with extreme coordinate values.
**Effort:** Simple

#### MINOR: ResearchService.estimate_turns_to_breakthrough() Estimation Accuracy Not Validated
**ID:** TCG-FND-010
**Location:** `game/research/systems/research_service.py` (production) / `tests/unit/research/test_research_service.py` (exists)
**Issue:** Tests verify the estimate is finite and ordering is correct, but not that the estimate is reasonably accurate. Missing:
- Statistical validation that the estimate is within acceptable bounds of actual breakthrough times
- Edge cases where estimate diverges significantly from reality
**Impact:** Players could receive misleading research time estimates.
**Recommendation:** Add Monte Carlo-style tests that run many turns and validate estimate accuracy.
**Effort:** Medium

#### MINOR: SpatialGrid._get_cell() Not Tested with Negative Coordinates
**ID:** TCG-FND-011
**Location:** `game/engine/spatial.py` (production) / `tests/unit/systems/test_spatial.py` (one negative test)
**Issue:** Only one test (`test_query_with_negative_coordinates`) exercises negative coordinates. Missing tests for:
- Objects spanning cell boundaries in negative quadrants
- Query radius overlapping positive and negative cells
- Very large negative coordinates (integer overflow potential with `int()` floor division)
**Impact:** Battle space extending into negative coordinates could have spatial partitioning bugs.
**Recommendation:** Add comprehensive negative coordinate tests to `test_spatial_edge_cases.py`.
**Effort:** Simple

#### MINOR: ResearchTracker.spread_rp_evenly() Distribution Accuracy
**ID:** TCG-FND-012
**Location:** `game/research/data/research_tracker.py` (production) / `tests/unit/research/test_research_tracker.py` (exists)
**Issue:** Tests verify count of nodes receiving allocation, but not:
- Actual even distribution verification (each node gets base_rp or base_rp+1)
- Total allocated equals budget after spread
- Spread with single available node
**Impact:** RP could be distributed unevenly or lost during spread operation.
**Recommendation:** Add distribution accuracy assertions to existing spread tests.
**Effort:** Simple

#### INFO: Test Organization - AI Tests Scattered Across Multiple Directories
**ID:** TCG-FND-013
**Location:** `tests/unit/ai/`, `tests/unit/simulation/factories/` (test locations)
**Issue:** AI-related tests are split between `tests/unit/ai/` and `tests/unit/simulation/factories/test_ai_factory.py`. This makes it harder to find all AI-related tests.
**Impact:** Maintenance overhead; developers might miss relevant tests when modifying AI code.
**Recommendation:** Consider moving `test_ai_factory.py` to `tests/unit/ai/` since the factory is now in `game/ai/`.
**Effort:** Simple

#### INFO: Research UI Tests Could Benefit from Visual Regression Testing
**ID:** TCG-FND-014
**Location:** `tests/unit/research/test_research_renderer.py` (exists)
**Issue:** Current tests mock pygame and verify method calls, but cannot detect visual regressions (e.g., node positions, colors, text truncation). Visual regression testing frameworks exist for pygame.
**Impact:** Visual bugs in research tree could go undetected.
**Recommendation:** Consider adding visual regression tests using screenshot comparison or pygame-testing utilities.
**Effort:** Complex

## Top 5 Priority Issues

1. **TCG-FND-001 (CRITICAL):** PhysicsBody minimal direct tests - Core physics foundation needs comprehensive unit tests for `update()`, `apply_force()`, and `forward_vector()` to prevent silent regressions in ship movement.

2. **TCG-FND-002 (CRITICAL):** Research UI lacks pygame-independent unit tests - Extract testable calculation logic (font cache quantization, dashed line math, log truncation) into pure functions.

3. **TCG-FND-005 (MAJOR):** FleeHehavior has no tests - This AI behavior is used in combat when ships retreat; untested flee logic could cause ships to flee toward enemies.

4. **TCG-FND-003 (MAJOR):** CollisionSystem integration tests - While unit tests exist, integration tests with real ship components would catch issues in the full damage pipeline.

5. **TCG-FND-004 (MAJOR):** TechTree cycle detection edge cases - Complex DFS algorithm needs more comprehensive cycle scenario tests to ensure tech tree validation is reliable.
