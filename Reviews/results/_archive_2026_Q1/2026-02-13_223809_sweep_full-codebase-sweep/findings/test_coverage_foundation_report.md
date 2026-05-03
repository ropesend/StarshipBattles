# Test Coverage Gaps Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Production Files Scanned:** 35
- **Test Files Cross-Referenced:** 62
- **Total Issues Found:** 12
- **Critical:** 1 | **Major:** 5 | **Minor:** 4 | **Info:** 2

## Findings

#### CRITICAL: AIController Integration with StrategyManager Missing Edge Case Tests
**ID:** TCG-FND-001
**Location:** `game/ai/controller.py` (production) / `tests/unit/ai/test_ai.py` (test gap)
**Issue:** AIController.update() has complex behavior involving target selection, strategy resolution, and behavior dispatch. While basic scenarios are tested, critical edge cases are missing:
- No tests for what happens when StrategyManager returns a strategy with missing policy references
- No tests for behavior fallback when an unknown strategy type is used
- No tests for race conditions in multi-threaded scenarios (even though StrategyManager has locks)
- No tests for AIController when ship has no weapons but strategy expects fire_weapons behavior
**Impact:** Strategy configuration errors could cause silent failures or incorrect AI behavior in combat, potentially affecting game balance and player experience
**Recommendation:** Add tests for:
1. Strategy with invalid targeting_policy reference
2. Strategy with invalid movement_policy reference
3. AIController behavior when ship lacks expected capabilities
4. StrategyManager thread-safety under concurrent access
**Effort:** Medium

#### MAJOR: TargetEvaluator Rule Types Missing Comprehensive Tests
**ID:** TCG-FND-002
**Location:** `game/ai/target_evaluator.py` (production) / `tests/unit/ai/test_target_evaluator_edge_cases.py` (partial coverage)
**Issue:** TargetEvaluator supports 14 rule types (nearest, farthest, distance, mass, largest, smallest, strongest, weakest, fastest, slowest, most_damaged, least_damaged, has_weapons, least_armor, pdc_arc, missiles_in_pdc_arc), but edge case tests only cover a subset:
- `_eval_speed_rule()`: No test for "slowest" rule type with weight vs factor logic
- `_eval_mass_rule()`: "strongest" and "weakest" rule types not directly tested
- No tests for negative factor values in rules
- No tests for rule type with both weight=0 and factor=0
**Impact:** Untested rule combinations could produce unexpected scores, affecting target prioritization in combat
**Recommendation:** Add parametrized tests for all 14 rule types with various weight/factor combinations including edge values (0, negative, very large)
**Effort:** Medium

#### MAJOR: PhysicsBody Missing Dedicated Unit Tests
**ID:** TCG-FND-003
**Location:** `game/engine/physics.py` (production) / no direct test file
**Issue:** PhysicsBody class has no dedicated unit tests. It is only tested indirectly through Ship physics tests. Missing direct tests for:
- `update()` method with various drag values
- `apply_force()` with zero mass (division by zero protection)
- `apply_force()` with negative mass
- `forward_vector()` at boundary angles (0, 90, 180, 270, 360, -90)
- Property setters (x, y) behavior
- Angular velocity and angular_drag interaction
- Drag value clamping (if drag > 1)
**Impact:** Physics edge cases could cause subtle bugs in movement and force application
**Recommendation:** Create `tests/unit/engine/test_physics_body.py` with focused unit tests for PhysicsBody class
**Effort:** Simple

#### MAJOR: TechTree.validate_requirements() Return Value Not Tested
**ID:** TCG-FND-004
**Location:** `game/research/data/tech_tree.py` (production) / `tests/unit/research/tech_tree/` (partial coverage)
**Issue:** TechTree has validation methods (validate_requirements, detect_cycles, validate) but tests focus on structure, not error message content:
- No tests verify the exact format of error messages returned
- No tests for validate() combining both validation types
- No tests for detect_cycles() with complex multi-path cycles
- No tests for requirements pointing to self (which is valid use case per test_tech_node.py)
**Impact:** Error messages could become inconsistent or unhelpful without regression tests
**Recommendation:** Add tests that assert on specific error message formats, and test validate() method directly
**Effort:** Simple

#### MAJOR: SpatialGrid Remove/Update Operations Not Implemented
**ID:** TCG-FND-005
**Location:** `game/engine/spatial.py` (production) / `tests/unit/systems/test_spatial.py` (test gap)
**Issue:** SpatialGrid only supports insert() and clear(). There's no remove() or update() method. Tests exist for insert/query/clear, but:
- No architectural test documenting the intentional omission of remove/update
- No performance test for large-scale grid operations
- No test for what happens with duplicate inserts of the same object
- No test for query_radius with radius=0
**Impact:** If remove/update are needed in future, lack of tests could lead to integration issues
**Recommendation:** Add documentation test explaining the design decision (clear+rebuild per tick), and test edge cases like duplicate inserts and zero radius
**Effort:** Simple

#### MAJOR: AIFactory Missing Tests
**ID:** TCG-FND-006
**Location:** `game/ai/ai_factory.py` (production) / tests indirectly through simulation tests
**Issue:** ai_factory.py is used to create AI controllers but has no dedicated unit tests. The factory pattern is tested only through integration in battle engine tests.
- No tests for factory registration/lookup
- No tests for default AI type fallback
- No tests for invalid AI type handling
**Impact:** Factory changes could break AI creation without direct detection
**Recommendation:** Create `tests/unit/ai/test_ai_factory.py` with unit tests for factory pattern
**Effort:** Simple

#### MINOR: Resources Module (game/core/resources.py) Missing Test Coverage
**ID:** TCG-FND-007
**Location:** `game/core/resources.py` (production) / no test file found
**Issue:** game/core/resources.py exists but no corresponding test file was found in tests/unit/core/. The file may contain utility functions for resource management that should have tests.
**Impact:** Resource handling edge cases might not be caught
**Recommendation:** Review resources.py content and add tests if it contains testable logic
**Effort:** Simple

#### MINOR: ResearchService.estimate_turns_to_breakthrough Edge Cases
**ID:** TCG-FND-008
**Location:** `game/research/systems/research_service.py` (production) / `tests/unit/research/test_research_service.py` (partial)
**Issue:** estimate_turns_to_breakthrough() tests cover zero RP and decay > gain, but:
- No test for exact boundary where gain equals decay
- No test for very large RP values (potential overflow)
- No test for volatility = 0 (would make added_chance always 0)
**Impact:** Edge cases in turn estimation could confuse players with incorrect feedback
**Recommendation:** Add boundary tests and extreme value tests
**Effort:** Simple

#### MINOR: Profiler Test Coverage Could Be Enhanced
**ID:** TCG-FND-009
**Location:** `game/core/profiling.py` (production) / `tests/unit/core/test_profiling_edge_cases.py` (exists)
**Issue:** Profiler tests exist but could be enhanced:
- profile_action decorator not tested when profiler is inactive
- save_history with custom filename not tested
- No test for profile_block context manager exception handling (what happens if code inside raises)
**Impact:** Profiling edge cases might behave unexpectedly
**Recommendation:** Add decorator and context manager edge case tests
**Effort:** Simple

#### MINOR: Controllable Interface Adapter Test Enhancement
**ID:** TCG-FND-010
**Location:** `game/ai/interfaces/controllable.py` (production) / `tests/unit/ai/test_controllable_adapter.py` (exists)
**Issue:** ShipControllableAdapter tests exist but could benefit from:
- Testing adaptation of ships with missing optional attributes
- Testing interface method calls when underlying ship methods fail
- Verifying all interface methods are covered
**Impact:** Adapter failures could cause AI crashes during combat
**Recommendation:** Review adapter for complete interface coverage tests
**Effort:** Simple

#### INFO: Test Organization Observation
**ID:** TCG-FND-011
**Location:** tests/unit/engine/ vs tests/unit/systems/
**Issue:** Engine tests are split between `tests/unit/engine/collision_edge_cases/` and `tests/unit/systems/test_collision_system.py`. This split organization could cause confusion about where to add new tests.
**Impact:** Minor - organizational clarity
**Recommendation:** Consider consolidating engine tests or adding a README explaining the organization
**Effort:** Simple

#### INFO: TechRequirement Negation Logic Test Enhancement Opportunity
**ID:** TCG-FND-012
**Location:** `game/research/data/tech_node.py` (production) / `tests/unit/research/test_tech_node.py` (test file)
**Issue:** TechRequirement has a `negate` field for "must be BELOW this level" requirements, but:
- Negation is tested in tech_node tests, but no integration test shows negated requirements in a full TechTree context
- No test for combining negated and non-negated requirements in the same AND group
**Impact:** Complex requirement scenarios might not work as expected
**Recommendation:** Add integration test with negated requirements in full TechTree
**Effort:** Simple

## Top 5 Priority Issues

1. **TCG-FND-001 (CRITICAL)** - AIController integration edge cases with StrategyManager could cause silent failures in combat AI behavior. This affects core gameplay.

2. **TCG-FND-002 (MAJOR)** - TargetEvaluator missing comprehensive tests for all 14 rule types. Incorrect target prioritization directly impacts combat balance.

3. **TCG-FND-003 (MAJOR)** - PhysicsBody lacks dedicated unit tests. Physics bugs can cascade through the entire simulation.

4. **TCG-FND-006 (MAJOR)** - AIFactory missing unit tests. Factory pattern changes could silently break AI creation.

5. **TCG-FND-005 (MAJOR)** - SpatialGrid design decisions (no remove/update) need documentation tests to prevent future misunderstandings.

---

## Coverage Summary by Module

### game/core/ (18 files)
- **Well Tested:** math.py, hex_math.py, json_utils.py, validation.py, exceptions.py, error_codes.py, singleton.py, config.py, constants.py, input_actions.py, logger.py, paths.py
- **Partial Coverage:** profiling.py (edge cases missing), protocols.py (boundary tests)
- **Needs Review:** resources.py (no direct tests found), strategy_metadata.py (tested through integration)

### game/ai/ (9 files)
- **Well Tested:** combat_utils.py, behaviors.py, controller.py (basic scenarios)
- **Partial Coverage:** target_evaluator.py (not all rule types tested), strategy_manager.py (thread safety)
- **Missing Unit Tests:** ai_factory.py

### game/research/ (11 files)
- **Well Tested:** tech_node.py, research_tracker.py, research_service.py, tech_tree.py
- **Partial Coverage:** research_scene.py, research_controls.py, research_renderer.py (UI tests exist but limited)

### game/engine/ (4 files)
- **Well Tested:** collision.py, spatial.py
- **Missing Direct Tests:** physics.py (PhysicsBody - tested only through Ship)
