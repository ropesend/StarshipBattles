# Test Coverage Gaps Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Production Files Scanned:** 37
- **Test Files Cross-Referenced:** 84
- **Total Issues Found:** 18
- **Critical:** 2 | **Major:** 7 | **Minor:** 7 | **Info:** 2

---

## Findings

### Critical Issues

#### CRITICAL: CollisionSystem raycasting edge cases untested
**ID:** TCG-FND-001
**Location:** `game/engine/collision.py` (production) / `tests/unit/systems/test_collision_system.py` (partial coverage)
**Issue:** While `test_collision_system.py` exists and tests basic beam hit/miss scenarios, the following critical edge cases are not tested:
- Division by zero when direction vector has length 0 (`a == 0` guard at line 87-88)
- Tangent hits where discriminant equals exactly 0 (edge of sphere)
- Multiple valid intersection points (entry and exit) - test only checks first hit
- Beam attack with `source` ship missing `get_total_sensor_score` attribute
- Hit chance calculation edge cases (attack_score=0, defense_score=very high)
**Impact:** Raycasting bugs could cause beams to miss when they should hit or vice versa - core combat mechanics
**Recommendation:** Add tests for zero-length direction, tangent hits, sensor score edge cases, and verify both t1/t2 intersection handling
**Effort:** Medium

#### CRITICAL: ResearchService leaky bucket algorithm edge cases untested
**ID:** TCG-FND-002
**Location:** `game/research/systems/research_service.py` (production) / `tests/unit/research/test_research_service.py` (partial)
**Issue:** The stochastic research system has critical edge cases that are not explicitly tested:
- Roll exactly at the breakthrough threshold (roll == current_chance)
- MAX_CHANCE cap behavior when chance accumulates past 95%
- Decay applied to locked nodes with accumulated chance (lines 77-91)
- Price curve calculations with level=0 input
- `tech_levels` mutation during turn processing (line 156)
- Negative RP allocation protection in `calculate_added_chance`
**Impact:** Research breakthrough probabilities could be incorrectly calculated, affecting game balance
**Recommendation:** Add parametrized tests for boundary roll values, max chance capping, and level 0 edge cases
**Effort:** Medium

---

### Major Issues

#### MAJOR: AIController navigation and avoidance algorithms lack comprehensive testing
**ID:** TCG-FND-003
**Location:** `game/ai/controller.py` (production) / `tests/unit/ai/test_ai_controller_unit.py` (partial)
**Issue:** Key AIController methods lack thorough unit tests:
- `check_avoidance()` - collision avoidance logic
- `navigate_to()` - navigation algorithm with stop_dist and precise parameters
- `get_engage_distance_multiplier()` - strategy parameter parsing
- `angle_to_target()` - angle calculation edge cases (same position, very large values)
**Impact:** AI ships may behave unpredictably during combat, causing frustrating player experience
**Recommendation:** Add unit tests for navigation with zero stop_dist, precise=True/False variations, avoidance with no nearby ships
**Effort:** Medium

#### MAJOR: TargetEvaluator rule evaluation missing edge case coverage
**ID:** TCG-FND-004
**Location:** `game/ai/target_evaluator.py` (production) / `tests/unit/ai/target_evaluator/` (partial)
**Issue:** Specific evaluation rules lack edge case testing:
- `_eval_distance_rule` with distance_cache=None and inf distance
- `_eval_mass_rule` with mass=0 or negative mass
- `_eval_speed_rule` with zero velocity vector
- `_eval_damage_rule` with hp_percent=0.0 and hp_percent=1.0
- `_eval_pdc_arc_rule` with non-missile entity type
- Weight=0 and factor=0 combinations across all rule types
**Impact:** Target selection bugs could cause AI to prioritize wrong targets
**Recommendation:** Add parametrized tests for boundary values in each evaluation rule
**Effort:** Simple

#### MAJOR: Behavior classes missing state transition and timer edge case tests
**ID:** TCG-FND-005
**Location:** `game/ai/behaviors.py` (production) / `tests/unit/ai/test_ai_behaviors.py` (partial)
**Issue:** Several behaviors have untested state transitions:
- `AttackRunBehavior`: State flip at exactly APPROACH_HYSTERESIS boundary, timer rollover with negative values
- `FormationBehavior`: Master death during drift phase, rotation mode switching mid-flight
- `OrbitBehavior`: dist=0 (same position as target) early return
- `FleeBehavior`: flee direction calculation when ship and target at same position
- `ErraticBehavior`: Random behavior reproducibility not tested with seeded RNG
**Impact:** AI behaviors could get stuck in incorrect states or crash at edge cases
**Recommendation:** Add state machine transition tests with boundary inputs
**Effort:** Medium

#### MAJOR: TechTree validation methods lack test coverage for cycle detection
**ID:** TCG-FND-006
**Location:** `game/research/data/tech_tree.py` (production) / `tests/unit/research/tech_tree/` (partial)
**Issue:** The `detect_cycles()` method (lines 208-252) lacks comprehensive testing:
- No test for complex multi-node cycles (A->B->C->A)
- No test for self-referencing nodes
- Negated requirement cycle handling not tested
- Large tree performance characteristics not verified
**Impact:** Circular dependencies in tech tree could cause infinite loops or crashes
**Recommendation:** Add tests for various cycle configurations and performance with large trees
**Effort:** Simple

#### MAJOR: TechRequirement fuzzy resolution edge cases untested
**ID:** TCG-FND-007
**Location:** `game/research/data/tech_node.py` (production) / `tests/unit/research/test_tech_node.py` (partial)
**Issue:** `TechRequirement.resolve()` method lacks tests for:
- level_range with min > max (invalid input)
- level_range with min == max (deterministic resolution)
- `is_met()` with resolved_level=None (pre-resolution state)
- Negate=True requirement satisfaction logic edge cases
**Impact:** Fuzzy requirement resolution could produce unexpected unlock conditions
**Recommendation:** Add validation tests for level_range and pre-resolution state handling
**Effort:** Simple

#### MAJOR: ResearchTracker serialization roundtrip not fully tested
**ID:** TCG-FND-008
**Location:** `game/research/data/research_tracker.py` (production) / `tests/unit/research/test_research_tracker.py` (partial)
**Issue:** `to_dict()` and `from_dict()` serialization lacks complete roundtrip testing:
- NodeState with current_chance at MAX boundary (0.95)
- Missing fields in deserialized data (defaults)
- Auto_spread_enabled flag persistence
- Turn log not serialized (transient data) - behavior not documented in tests
**Impact:** Research progress could be lost or corrupted during save/load
**Recommendation:** Add roundtrip tests with edge case values and verify transient data handling
**Effort:** Simple

#### MAJOR: SpatialGrid query_radius does not filter by actual distance
**ID:** TCG-FND-009
**Location:** `game/engine/spatial.py` (production) / `tests/unit/systems/test_spatial.py` (partial)
**Issue:** The test `test_query_returns_candidates_not_exact_distance` documents that `query_radius` returns ALL objects in overlapping cells, not just those within exact radius. However:
- No test verifies this is the intended behavior
- No test for extremely large radius (performance/memory)
- No test for very small cell_size relative to query radius
- Callers must filter results themselves - no integration test verifies this pattern
**Impact:** Callers could assume radius filtering is exact and get incorrect results
**Recommendation:** Add documentation test and verify integration patterns filter correctly
**Effort:** Simple

---

### Minor Issues

#### MINOR: PhysicsBody x/y property setters not tested
**ID:** TCG-FND-010
**Location:** `game/engine/physics.py` (production) / `tests/unit/systems/test_physics.py` (partial)
**Issue:** While `test_physics.py` tests initialization and movement, the x/y property setters (lines 67-80) are never directly tested:
- `body.x = value` setter
- `body.y = value` setter
**Impact:** Low - properties are simple delegations, but untested code paths
**Recommendation:** Add simple property setter tests for completeness
**Effort:** Simple

#### MINOR: ShipControllableAdapter formation methods return raw Ship objects
**ID:** TCG-FND-011
**Location:** `game/ai/interfaces/controllable.py` (production) / `tests/unit/ai/controllable_interface/` (partial)
**Issue:** The adapter's `get_formation_master()` and `get_formation_members()` return raw Ship objects rather than adapters (documented in code comments at line 296-298). However:
- No test explicitly verifies this is intentional
- No test for mixed adapter/Ship access patterns
**Impact:** Low - documented behavior, but could confuse future maintainers
**Recommendation:** Add documentation test asserting return types are raw Ships
**Effort:** Simple

#### MINOR: Logger module singleton behavior not fully tested
**ID:** TCG-FND-012
**Location:** `game/core/logger.py` (production) / `tests/unit/core/logger/` (partial)
**Issue:** Logger tests exist but missing:
- Thread safety of singleton under concurrent access
- Log level filtering behavior
- Max message queue size handling (if any)
**Impact:** Low - logger is infrastructure, unlikely to affect gameplay
**Recommendation:** Add thread safety test for concurrent logging
**Effort:** Simple

#### MINOR: Config module edge cases for clamp values not tested
**ID:** TCG-FND-013
**Location:** `game/core/config.py` (production) / `tests/unit/core/test_config.py` (partial)
**Issue:** Configuration classes contain many magic numbers and bounds. Not all bounds are explicitly tested:
- ResearchTracker.MIN_RP_BUDGET and MAX_RP_BUDGET clamping
- PhysicsConfig drag > 1 behavior
- AIConfig boundary values
**Impact:** Low - config values rarely change
**Recommendation:** Add bounds verification tests for critical config values
**Effort:** Simple

#### MINOR: Error code enum completeness not verified
**ID:** TCG-FND-014
**Location:** `game/core/error_codes.py` (production) / `tests/unit/core/test_error_codes.py` (partial)
**Issue:** While error codes are tested for uniqueness, there's no verification that:
- All error codes are actually used somewhere
- Error code ranges don't overlap between categories
- Error messages exist for all codes
**Impact:** Low - dead code detection for error codes
**Recommendation:** Add test that searches codebase for error code usage
**Effort:** Simple

#### MINOR: Profiling decorator edge cases not tested
**ID:** TCG-FND-015
**Location:** `game/core/profiling.py` (production) / `tests/unit/core/profiling/` (partial)
**Issue:** Profiling decorator tests exist but missing:
- Exception handling when profiled function raises
- Nested decorator behavior
- Profiling disabled state behavior
**Impact:** Low - profiling is debug infrastructure
**Recommendation:** Add exception propagation test for profiled functions
**Effort:** Simple

#### MINOR: hex_ring negative radius input not tested
**ID:** TCG-FND-016
**Location:** `game/core/hex_math.py` (production) / `tests/unit/core/test_hex_math_core.py` (good coverage)
**Issue:** Test `test_ring_radius_0` verifies `hex_ring(0)` returns `[HexCoord(0,0)]`. However:
- No test for negative radius input
- No test for very large radius (performance)
**Impact:** Low - negative radius is likely programmer error
**Recommendation:** Add assertion that negative radius raises ValueError or returns empty list
**Effort:** Simple

---

### Informational

#### INFO: Research system UI rendering tests use mocking extensively
**ID:** TCG-FND-017
**Location:** `game/research/ui/research_renderer.py` / `tests/unit/research/test_research_renderer.py`
**Issue:** Research renderer tests mock pygame extensively, which is appropriate but:
- Tests verify method calls rather than rendered output
- No visual regression testing infrastructure exists
- UI tests are integration-style but in unit test folder
**Impact:** None - appropriate test design for UI layer
**Recommendation:** Consider separating UI integration tests into dedicated folder
**Effort:** N/A

#### INFO: Test file organization follows production structure well
**ID:** TCG-FND-018
**Location:** Tests structure mirrors `game/` structure
**Issue:** Test coverage organization is well-structured. Most production modules have corresponding test files. This sweep found coverage gaps primarily in edge cases rather than missing test files entirely.
**Impact:** Positive - good test architecture
**Recommendation:** Continue maintaining parallel structure as codebase grows
**Effort:** N/A

---

## Top 5 Priority Issues

1. **TCG-FND-001 (CRITICAL):** CollisionSystem raycasting edge cases - core combat mechanic with division by zero guard untested
2. **TCG-FND-002 (CRITICAL):** ResearchService leaky bucket boundary conditions - affects game balance for research progression
3. **TCG-FND-003 (MAJOR):** AIController navigation/avoidance - AI behavior predictability during combat
4. **TCG-FND-005 (MAJOR):** Behavior state transitions - AI could get stuck in incorrect states
5. **TCG-FND-006 (MAJOR):** TechTree cycle detection - could cause infinite loops with invalid tech tree data
