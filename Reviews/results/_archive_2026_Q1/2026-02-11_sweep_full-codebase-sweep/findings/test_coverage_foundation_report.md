# Test Coverage Gaps Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Production Files Scanned:** 39
- **Test Files Cross-Referenced:** 58
- **Total Issues Found:** 24
- **Critical:** 3 | **Major:** 9 | **Minor:** 8 | **Info:** 4

---

## Findings

### Phase 1: Untested and Undertested Modules

#### CRITICAL: PhysicsBody.apply_force() and forward_vector() Lack Direct Unit Tests
**ID:** TCG-FND-001
**Location:** `game/engine/physics.py` (production) / `tests/unit/systems/test_physics.py` (test)
**Issue:** The `PhysicsBody.apply_force()` method and `forward_vector()` method are critical to the physics simulation. While `test_physics.py` exists and tests basic update mechanics (velocity, drag, position), it does not directly test `apply_force()` with varying mass values or `forward_vector()` at different angles. The force-to-acceleration conversion (`acceleration += force / mass`) with non-unit mass, zero mass edge case (division by zero guarded by `if self.mass > 0`), and the interaction between apply_force and the update cycle are untested. `forward_vector()` which delegates to `Vector2.rotate()` is also untested for correctness of the combined operation.
**Impact:** Bugs in force application or forward vector calculation would propagate to all ship movement, AI navigation, and formation flying. These are foundational physics operations.
**Recommendation:** Add tests for: `apply_force()` with mass=1, mass=0.5, mass=0 (no-op), multiple force accumulation; `forward_vector()` at 0, 90, 180, 270 degrees; integration test of apply_force -> update -> position change.
**Effort:** Simple

#### CRITICAL: AIController.update() Integration Path Not Fully Covered
**ID:** TCG-FND-002
**Location:** `game/ai/controller.py` (production) / `tests/unit/ai/test_ai_controller_unit.py` (test)
**Issue:** `AIController.update()` is the main AI tick function called every frame. While `test_ai_controller_unit.py` tests individual paths (formation, flee, dead ship), several critical paths through `update()` lack coverage: (1) The secondary target acquisition path (`find_secondary_targets()`) when `max_targets > 1` is only tested in `test_ai.py` at integration level, not as a unit test of the controller. (2) The behavior context merging (`behavior_context = dict(movement_policy); behavior_context.update(resolved.get('definition', {}))`) is untested -- if this merge is wrong, all behavior parameters would be incorrect. (3) The formation master targeting sync path (lines 296-299 where `master_target` is copied to the formation member) has no direct test.
**Impact:** AI behavior selection and target acquisition bugs would cause ships to select wrong targets or use wrong movement parameters during combat, which is the core gameplay loop.
**Recommendation:** Add unit tests for: behavior context merging correctness, formation target sync, secondary target acquisition in controller, and the full `update()` path for a non-formation ship with a live target and strategy-selected behavior.
**Effort:** Medium

#### CRITICAL: CollisionSystem.process_beam_attack() Hit Chance and Damage Pipeline Not Tested End-to-End
**ID:** TCG-FND-003
**Location:** `game/engine/collision.py` (production) / `tests/unit/engine/collision_edge_cases/test_beam_ramming.py` (test)
**Issue:** The existing beam tests in `test_beam_ramming.py` test edge cases (zero direction, dead target, no target) but **no test verifies the normal successful hit path end-to-end** with a real discriminant calculation. All tests mock `calculate_hit_chance` to return 1.0 or 0.0, bypassing the actual ray-sphere intersection math (quadratic formula). The `source_ship.get_total_sensor_score()` attack score path, `target.total_defense_score` defense score path, and the `beam_ab.get_damage(hit_dist)` distance-based damage path are all mocked out. Additionally, the `process_beam_attack()` method directly uses `random.random()` making it non-deterministic, but no test patches random for a controlled hit scenario with actual discriminant > 0.
**Impact:** A regression in the quadratic formula (sphere-ray intersection) or in the discriminant branching logic would go undetected. This is the core beam weapon hit detection.
**Recommendation:** Add a test that verifies the full pipeline: origin -> direction -> discriminant calculation -> valid_t range check -> hit distance -> hit chance -> damage application. Patch `random.random` for determinism. Verify that `hit_dist` passed to `get_damage()` is geometrically correct.
**Effort:** Medium

---

#### MAJOR: SpatialGrid.query_radius() Boundary and Edge Cases Undertested
**ID:** TCG-FND-004
**Location:** `game/engine/spatial.py` (production) / `tests/unit/systems/test_spatial.py`, `test_spatial_edge_cases.py` (test)
**Issue:** `SpatialGrid` is used for all proximity queries in combat (target finding, collision detection, avoidance). While basic insert/query tests exist, the following edge cases are not tested: (1) Objects exactly on cell boundaries. (2) Query with radius=0. (3) Query with very large radius that spans many cells. (4) Insert with position at (0,0) vs near cell boundary. (5) Multiple objects in the same cell. (6) The `_get_cell()` method with negative positions (floor division of negative numbers behaves differently than positive).
**Impact:** Incorrect spatial queries would cause ships to miss targets, fail to detect collisions, or return wrong candidates.
**Recommendation:** Add boundary tests for cell-edge positions, negative coordinates, zero radius query, and multi-object same-cell scenarios.
**Effort:** Simple

#### MAJOR: AIController._handle_formation_master() Turn Limiting Math Untested
**ID:** TCG-FND-005
**Location:** `game/ai/controller.py` lines 354-390 (production) / No specific test
**Issue:** The `_handle_formation_master()` method contains complex angular velocity math to limit formation master turn speed based on formation radius (`max_w_rad = max_speed / max_radius`, `max_w_deg = math.degrees(max_w_rad)`, `turn_limit = max_w_deg / base_turn`). This critical calculation prevents formation members from being flung out by excessive rotation, but it has no direct unit test. The slow-down logic (checking if members are drifting and applying `FORMATION_SLOWDOWN_THROTTLE`) also lacks tests.
**Impact:** Incorrect turn limiting would cause formations to break apart during turns, which is a visible gameplay bug.
**Recommendation:** Create a focused unit test for `_handle_formation_master()` with mock formation members at various offsets and verify throttle/turn_throttle values.
**Effort:** Medium

#### MAJOR: AIController._check_formation_integrity() Component Damage Detection Untested
**ID:** TCG-FND-006
**Location:** `game/ai/controller.py` lines 392-420 (production) / No specific test
**Issue:** `_check_formation_integrity()` checks if propulsion components are damaged and triggers formation dropout. The component damage detection logic (`getattr(comp, 'current_hp', 1) < getattr(comp, 'max_hp', 1)`) and the subsequent formation cleanup (removing from master's members list, handling `AttributeError`/`ValueError`) are untested. This method is called every tick for every ship in formation.
**Impact:** A bug in formation dropout detection would cause ships with damaged propulsion to stay in formation (causing erratic behavior) or ships with undamaged propulsion to drop out spuriously.
**Recommendation:** Add unit tests for: damaged propulsion triggers dropout, undamaged propulsion stays in formation, graceful handling of broken formation structure (missing master, already removed from list).
**Effort:** Simple

#### MAJOR: AIController.check_avoidance() Collision Detection Logic Untested
**ID:** TCG-FND-007
**Location:** `game/ai/controller.py` lines 422-452 (production) / `tests/unit/ai/test_behavior_units.py` (partial)
**Issue:** While `test_behavior_units.py` tests that KiteBehavior calls `check_avoidance()` and responds to its return value, the `check_avoidance()` method itself is not unit tested. The method contains critical logic: iterating nearby objects, skipping self (via adapter unwrapping with `getattr(self.ship, 'ship', self.ship)`), checking alive status and combatant protocol, calculating threshold distances with radii and buffer, and computing avoidance vectors. None of this internal logic is directly tested.
**Impact:** Collision avoidance bugs would cause ships to fly into each other or react to non-threatening objects.
**Recommendation:** Unit test `check_avoidance()` directly with: mock grid returning nearby objects, self-exclusion via adapter, dead object filtering, threshold calculation, and avoidance vector direction.
**Effort:** Medium

#### MAJOR: AIController.navigate_to() Core Navigation Logic Has No Tests
**ID:** TCG-FND-008
**Location:** `game/ai/controller.py` lines 454-470 (production) / No direct test
**Issue:** `navigate_to()` is the fundamental navigation method used by ALL movement behaviors. It calculates target angle via `atan2`, computes angle difference with wrapping, decides rotation direction, and triggers thrust. Despite being called by every behavior, it has no direct unit tests. All behavior tests mock `navigate_to` rather than testing it. The critical angle wrapping logic (`(target_angle - current_angle + 180) % 360 - 180`) and the 5-degree and 30-degree thresholds are untested.
**Impact:** Navigation bugs would affect all ship movement in combat. Incorrect angle wrapping would cause ships to rotate the wrong direction.
**Recommendation:** Test `navigate_to()` directly with: target at various angles relative to current heading, verify rotation direction, verify thrust activation threshold, edge cases at 0/180/360 degree boundaries.
**Effort:** Simple

#### MAJOR: ResearchService.process_turn() Leaky Bucket Algorithm Edge Cases
**ID:** TCG-FND-009
**Location:** `game/research/systems/research_service.py` (production) / `tests/unit/research/test_research_service.py` (test)
**Issue:** While `test_research_service.py` has good coverage of `process_turn()` (33+ tests), the following edge cases are missing: (1) The `tech_levels` parameter mutation path -- when a breakthrough occurs, `tech_levels[node.id] = state.current_level` is modified in-place. If the same dict is reused by the caller, this could cause subtle bugs. No test verifies this side effect. (2) Node ordering within a single turn -- if Node B depends on Node A, and both get breakthroughs in the same turn, does Node B see Node A's new level? This is tested (`test_breakthrough_updates_tech_levels_for_same_turn`) but relies on dict iteration order. (3) The fresh `random.Random()` RNG per turn call means results are non-deterministic by design, but no test verifies that different calls produce different results (testing the randomness property).
**Impact:** Subtle bugs in turn processing could cause incorrect tech tree progression or non-deterministic test failures.
**Recommendation:** Add tests for: mutation of the `tech_levels` parameter, explicit ordering verification with multi-dependency chains, and verification that the RNG is truly per-call fresh.
**Effort:** Simple

#### MAJOR: TechNode.get_effective_price() Only Partially Tested
**ID:** TCG-FND-010
**Location:** `game/research/data/tech_node.py` lines 114-145 (production) / `tests/unit/research/test_tech_node.py` (test)
**Issue:** The `get_effective_price()` method supports 6 price curve types (flat, linear, quadratic, exponential, logarithmic, sqrt) plus a default fallback for unknown types. Review of `test_tech_node.py` shows it does not exhaustively test each curve at multiple levels. The mathematical formulas (e.g., `self.price * (1.5 ** level)` for exponential) could have subtle precision or logic errors. The unknown curve type fallback path (returns `self.price`) is also untested.
**Impact:** Incorrect price curves would make research too easy or too hard for specific technologies.
**Recommendation:** Add parametrized tests for each of the 6 price curves at levels 1, 2, 5, 10 with expected values, plus the unknown curve fallback.
**Effort:** Simple

#### MAJOR: ResearchRenderer Test Coverage is Minimal
**ID:** TCG-FND-011
**Location:** `game/research/ui/research_renderer.py` (production) / `tests/unit/research/test_research_renderer.py` (test)
**Issue:** The test file only tests font cache bounding (2 tests). The actual rendering logic -- `draw()`, `_draw_dependency_lines()`, `_draw_nodes()`, `_draw_node_text()`, `_is_visible()`, and the new `_draw_dashed_line()` method -- has zero test coverage. While rendering tests are inherently harder to write, `_is_visible()` is a pure function that could easily be unit tested, and `_draw_dashed_line()` contains math that could have off-by-one errors.
**Impact:** Visual bugs in the tech tree display would go undetected. The `_is_visible()` culling function if wrong could cause nodes to disappear or render when off-screen.
**Recommendation:** Add unit tests for `_is_visible()` with various screen positions and margins. Add basic smoke tests for `_draw_dashed_line()` verifying it doesn't crash and produces expected number of line segments.
**Effort:** Simple

#### MAJOR: ResearchControlPanel.handle_event() Lacks Unit Tests
**ID:** TCG-FND-012
**Location:** `game/research/ui/research_controls.py` (production) / `tests/unit/research/research_controls/` (test)
**Issue:** While `test_event_formatting.py`, `test_node_selection.py`, and `test_reset_state.py` exist, the core `handle_event()` method (the main event dispatch) is not directly unit tested. The slider event handling for budget and allocation changes, the auto-spread toggle callback chain, and the allocation slider range update logic (`_update_allocation_slider_range()`) are untested. These are critical for user interaction.
**Impact:** UI interaction bugs would cause RP allocation to silently fail or budget changes to not propagate.
**Recommendation:** Add tests for `handle_event()` with mock pygame_gui events for each button press and slider move. Verify side effects on tracker state.
**Effort:** Medium

---

### Phase 2-3: Critical Path and Public API Coverage

#### MINOR: StrategyManager.resolve_strategy() Default Fallback Chain Untested
**ID:** TCG-FND-013
**Location:** `game/ai/strategy_manager.py` lines 116-127 (production) / `tests/unit/ai/test_strategy_system.py` (test)
**Issue:** `resolve_strategy()` chains `get_strategy()` -> `get_targeting_policy()` -> `get_movement_policy()`. Each of these falls back to defaults if the key is missing. The test file `test_strategy_system.py` tests the manager but does not test the fallback chain: what happens when a strategy references a non-existent targeting policy? Does the default get used correctly? The cross-reference integrity between strategies and their policy references is untested.
**Impact:** A strategy referencing a typo'd policy name would silently use defaults, which might go unnoticed.
**Recommendation:** Add test for resolve_strategy with: valid strategy + valid policies, valid strategy + missing policy (fallback), missing strategy (full defaults).
**Effort:** Simple

#### MINOR: HexCoord Arithmetic with Non-HexCoord Types Returns NotImplemented
**ID:** TCG-FND-014
**Location:** `game/core/hex_math.py` lines 96-103 (production) / `tests/unit/core/test_hex_math_core.py` (test)
**Issue:** `HexCoord.__add__()` and `__sub__()` return `NotImplemented` for non-HexCoord types, but no test verifies this behavior. If a caller accidentally adds a HexCoord to a tuple or int, Python would raise a `TypeError` -- this is correct behavior but should be verified by tests to document the contract.
**Impact:** Low -- Python handles this correctly, but the explicit contract should be documented in tests.
**Recommendation:** Add tests: `HexCoord(1,0) + 5` raises TypeError, `HexCoord(1,0) + (1,0)` raises TypeError.
**Effort:** Simple

#### MINOR: pixel_to_hex() Rounding Edge Cases at Cell Boundaries
**ID:** TCG-FND-015
**Location:** `game/core/hex_math.py` lines 135-163 (production) / `tests/unit/core/test_hex_math_core.py` (test)
**Issue:** The `pixel_to_hex()` function uses `_hex_round()` which makes rounding decisions based on which of q_diff, r_diff, s_diff is largest. At the exact center between three hexes, rounding behavior is deterministic but brittle. No test verifies behavior at these boundary positions. The round-trip property `pixel_to_hex(hex_to_pixel(h)) == h` should be tested for a range of hexes.
**Impact:** Clicking near hex boundaries on the galaxy map could select the wrong hex.
**Recommendation:** Add round-trip property tests for a range of hex coordinates, and boundary tests at positions equidistant from 2-3 hexes.
**Effort:** Simple

#### MINOR: RegistryManager.hydrate() Partial Resources Handling
**ID:** TCG-FND-016
**Location:** `game/core/registry.py` lines 179-216 (production) / `tests/unit/core/registry/test_registry_operations.py` (test)
**Issue:** `hydrate()` has a conditional: `if resources_data:` which means passing `None` or empty dict `{}` or `0` (falsy values) would skip resource hydration. This behavior is correct for backward compatibility but no test verifies what happens when `resources_data={}` (empty dict, falsy) vs `resources_data=None` vs `resources_data={'fuel': {...}}` (truthy). The distinction between "no resources" and "empty resources" is subtle.
**Impact:** A caller passing `resources_data={}` would not clear existing resources, which could leave stale data from a previous hydration.
**Recommendation:** Add tests for `hydrate()` with `resources_data=None`, `resources_data={}`, and `resources_data={'key': 'val'}` and verify resource state after each.
**Effort:** Simple

#### MINOR: combat_utils.is_in_pdc_arc() Missing Test for Target Behind Ship
**ID:** TCG-FND-017
**Location:** `game/ai/combat_utils.py` lines 175-228 (production) / `tests/unit/ai/test_combat_utils.py` (test)
**Issue:** The existing `is_in_pdc_arc()` tests cover: target in arc, out of range, no PDC components, and no position. Missing: target at same position as ship (zero-length vector, `length_squared() == 0` -> continue), target directly behind the ship (180 degrees from facing), target at exact arc boundary (half of firing arc). The zero-length vector path (line 216) is a specific edge case that if removed could cause a division-by-zero crash.
**Impact:** Missing edge case tests for the PDC targeting system used in anti-missile defense.
**Recommendation:** Add tests for: target at same position, target behind ship, target at exact arc boundary angle.
**Effort:** Simple

#### MINOR: TargetEvaluator._eval_speed_rule() Slowest Logic May Be Incorrect
**ID:** TCG-FND-018
**Location:** `game/ai/target_evaluator.py` lines 104-125 (production) / `tests/unit/ai/target_evaluator/test_evaluation_rules.py` (test)
**Issue:** The `_eval_speed_rule()` for 'slowest' type computes `val = -speed * (weight if weight > 0 else -factor)`. This means: if weight > 0, `val = -speed * weight` (slower = less negative = higher score, correct). But if weight <= 0, `val = -speed * -factor = speed * factor` (faster = higher score, WRONG for slowest). This appears to be a logic bug where the slowest rule with factor-based scoring would incorrectly prefer faster targets. No test catches this because all existing tests use weight > 0.
**Impact:** AI ships using the 'slowest' targeting rule with factor instead of weight would target the fastest ship instead of the slowest.
**Recommendation:** Add test for 'slowest' rule with weight=0 and factor=1, verify that a slower target scores higher than a faster one. If the test fails, it confirms a production bug.
**Effort:** Simple

#### MINOR: ResearchTracker.spread_rp_evenly() Does Not Test Pre-Computed tech_levels Path
**ID:** TCG-FND-019
**Location:** `game/research/data/research_tracker.py` lines 167-203 (production) / `tests/unit/research/test_research_tracker.py` (test)
**Issue:** `spread_rp_evenly()` accepts an optional `tech_levels` parameter for performance. All existing tests call it without this parameter, always using the default path that calls `get_all_tech_levels()`. The pre-computed path is never tested, meaning a regression where the parameter is ignored would go undetected.
**Impact:** Performance optimization code path is untested; could silently fall back to the slow path.
**Recommendation:** Add a test that provides explicit `tech_levels` and verifies the same behavior as the automatic path.
**Effort:** Simple

---

### Phase 4: Test Quality Issues

#### INFO: Collision Edge Case Tests Use Heavy Mocking That May Mask Real Integration Issues
**ID:** TCG-FND-020
**Location:** `tests/unit/engine/collision_edge_cases/` (all files)
**Issue:** All collision tests use `MagicMock` for ships, projectiles, weapons, and abilities. While this is appropriate for unit tests, the heavy mocking means these tests verify the mock interaction pattern but not the actual object contracts. For example, `mock_target_ship.combat_engine.take_damage.assert_called_with(75)` verifies the call was made but not that a real ship's combat engine correctly processes that damage through the emissive armor -> crystalline armor -> shields -> hull pipeline. There are no integration-level collision tests in the integration test directory that verify the collision system works with real Ship objects.
**Impact:** The collision system tests pass even if the mock contract diverges from the real object API.
**Recommendation:** Consider adding 1-2 integration tests using real Ship instances to verify the end-to-end collision pipeline.
**Effort:** Complex

#### INFO: ScreenshotManager Tests Are Fragile Due to Singleton Cleanup Pattern
**ID:** TCG-FND-021
**Location:** `tests/unit/core/test_screenshot_manager.py`
**Issue:** The screenshot manager tests manually manipulate `SingletonMeta._instances` for cleanup (`del SingletonMeta._instances[ScreenshotManager]`). This pattern is fragile and could leave stale singletons if a test fails before cleanup. The tests should use `ScreenshotManager.reset()` instead of direct dict manipulation. Additionally, `capture_strategy_layer()` and `capture_step()` methods have no tests at all.
**Impact:** Test isolation issues could cause flaky failures in parallel test runs.
**Recommendation:** Refactor to use `ScreenshotManager.reset()` in fixture teardown. Add basic tests for `capture_step()` and `capture_strategy_layer()`.
**Effort:** Simple

#### INFO: StrategyMetadataService Uses Legacy Singleton Pattern Instead of SingletonMeta
**ID:** TCG-FND-022
**Location:** `game/core/strategy_metadata.py` (production) / `tests/unit/core/test_strategy_metadata.py` (test)
**Issue:** `StrategyMetadataService` uses a hand-rolled singleton pattern (class-level `_instance`, `_lock`, manual `__init__` guard) instead of the project's standard `SingletonMeta` metaclass used by RegistryManager, Profiler, ScreenshotManager, etc. The test coverage for this class appears adequate, but the inconsistency means it has a different lifecycle API (direct `__init__` raises `StateException` vs `SingletonMeta` which silently returns the existing instance). This is more of a consistency/maintenance issue than a test gap.
**Impact:** Inconsistent singleton behavior across the codebase; different reset/test isolation patterns needed.
**Recommendation:** Consider migrating to `SingletonMeta` for consistency. Verify existing tests pass with the new pattern.
**Effort:** Simple

#### INFO: ErraticBehavior Uses `import random` Inside Method Body
**ID:** TCG-FND-023
**Location:** `game/ai/behaviors.py` lines 443, 452 (production)
**Issue:** `ErraticBehavior.enter()` and `update()` both use `import random` inside the method body rather than at module level. While this works, it makes the behavior harder to test deterministically because patching `random.choice` and `random.uniform` requires patching at the correct module level. The `enter()` method has no test verifying the initial direction and interval are set. No test verifies the direction change timing logic in `update()`.
**Impact:** ErraticBehavior is described as a test/debug behavior, but even so, untestable random behavior could mask issues in stress testing.
**Recommendation:** Move `import random` to module level, add basic tests for `enter()` state initialization and `update()` direction-change timing.
**Effort:** Simple

---

### Phase 5-6: Integration and Missing Category Gaps

#### MAJOR: No Integration Test for AI Controller + Real Strategy Data
**ID:** TCG-FND-024
**Location:** `tests/integration/ai_strategy/` (existing) / `game/ai/controller.py` + `game/ai/strategy_manager.py` (production)
**Issue:** The integration tests in `tests/integration/ai_strategy/` test strategy commands and evaluation, but there is no integration test that exercises the full `AIController.update()` -> `StrategyManager.resolve_strategy()` -> behavior selection -> navigation pipeline with real strategy JSON data. All controller tests use mocked strategies. This means a typo or missing field in the actual `combat_strategies.json`, `targeting_policies.json`, or `movement_policies.json` files would not be caught by any test.
**Impact:** Data-driven strategy configuration errors would only be caught during actual gameplay.
**Recommendation:** Add an integration test that loads real strategy data files and verifies that `resolve_strategy()` returns complete, valid strategy objects for each defined strategy ID.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **TCG-FND-003 (CRITICAL):** CollisionSystem beam attack pipeline lacks end-to-end test with actual ray-sphere intersection math -- the core beam weapon mechanic is tested only with mocked hit chances, not the actual geometric calculation.

2. **TCG-FND-002 (CRITICAL):** AIController.update() has multiple untested integration paths including behavior context merging, formation target sync, and secondary target acquisition -- the main AI decision loop.

3. **TCG-FND-001 (CRITICAL):** PhysicsBody.apply_force() and forward_vector() lack direct tests -- foundational physics operations used by all movement.

4. **TCG-FND-008 (MAJOR):** AIController.navigate_to() is the single most-called navigation method in all AI behaviors but has zero direct tests -- all behaviors mock it instead of testing it.

5. **TCG-FND-024 (MAJOR):** No integration test validates that real strategy JSON data files produce valid, complete strategy objects -- a data error in any of the 3 strategy config files would go undetected until gameplay.
