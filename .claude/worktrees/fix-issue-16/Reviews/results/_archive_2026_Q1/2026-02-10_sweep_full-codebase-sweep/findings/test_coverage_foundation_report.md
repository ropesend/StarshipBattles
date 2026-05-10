# Test Coverage Gaps Sweep: Foundation

## Summary
- **Shard:** Foundation (`game/core/`, `game/ai/`, `game/research/`, `game/engine/`)
- **Production Files Scanned:** 43 files
- **Test Files Cross-Referenced:** 622 total test files
- **Total Issues Found:** 21
- **Critical:** 3 | **Major:** 8 | **Minor:** 10

## Findings

### CRITICAL Issues

#### CRITICAL: Hex Math Module - No Unit Test Coverage
**ID:** TCG-FND-001
**Location:** `game/core/hex_math.py` (250 lines)
**Issue:** Core hex grid mathematics module with 8 public functions (`hex_distance`, `hex_ring`, `hex_lerp`, `hex_linedraw`, `pixel_to_hex`, `hex_to_pixel`, `hex_to_dict`, `hex_from_dict`) has zero unit test coverage. Hex coordinates are fundamental to galaxy generation, fleet positioning, and pathfinding. Only integration tests exist (`test_hex_math_strategy.py`), which don't test edge cases.
**Impact:** CRITICAL - Hex math is critical path for galaxy simulation. Missing edge case tests: negative coordinates, boundary conditions, coordinate wrapping, serialization round-trip failures.
**Recommendation:** Create dedicated unit test file `tests/unit/core/test_hex_math.py` covering:
  - HexCoord creation, equality, hashing, arithmetic (add/sub)
  - hex_distance with edge cases (negative, same coord, large distances)
  - hex_ring with radius 0, negative radius
  - hex_lerp with t=0, t=1, t=0.5 (rounding correctness)
  - hex_linedraw with same start/end
  - pixel_to_hex rounding behavior with fractional pixels
  - Serialization round-trip (hex_to_dict -> hex_from_dict)
**Effort:** Medium

#### CRITICAL: AI Behaviors Module - No Unit Tests
**ID:** TCG-FND-002
**Location:** `game/ai/behaviors.py` (700+ lines)
**Issue:** Core behavior system (11 behavior classes: KiteBehavior, RamBehavior, FleeBehavior, AttackRunBehavior, FormationBehavior, etc.) lacks dedicated unit tests. Tests exist in integration (`test_formation_behavior.py`) and scattered in `test_advanced_behaviors.py`, `test_ai_behaviors.py`, but no comprehensive unit tests for behavior lifecycle, state transitions, and edge cases.
**Impact:** CRITICAL - Behaviors drive all combat AI decision-making. Undertested paths: behavior initialization failures, state transitions with dead targets, edge cases in targeting logic, formation dropout recovery, attack state machine transitions.
**Recommendation:** Create `tests/unit/ai/test_behaviors.py` with unit tests for each behavior class covering:
  - Behavior initialization and update cycle
  - State transitions (approach → attack → retreat)
  - Target death/removal handling
  - Formation constraints with invalid masters
  - Range calculations with zero/infinity edge cases
**Effort:** Complex (11 behavior classes to test)

#### CRITICAL: Registry Loading - No Error Path Tests
**ID:** TCG-FND-003
**Location:** `game/core/resources.py` (143 lines)
**Issue:** Resource registry loading functions (`load_resources`, `load_resources_data`) handle multiple error cases (FileNotFoundError, json.JSONDecodeError, PermissionError, TypeError) but error paths are not unit tested. Only success path is tested in `test_registry_fixtures.py`.
**Impact:** CRITICAL - Registry loading is initialization critical path. Untested: malformed JSON fallback, missing file handling, permission errors, corrupted data structure recovery. Silent failures could leave registries in inconsistent state.
**Recommendation:** Create comprehensive error path tests covering all 5 exception handlers with mocked file I/O failures.
**Effort:** Medium

### MAJOR Issues

#### MAJOR: Core Input Mapper - Incomplete Test Coverage
**ID:** TCG-FND-004
**Location:** `game/core/input_mapper.py` (300+ lines)
**Issue:** InputMapper has tests (`test_input_mapper.py`) but missing critical coverage: conflict detection, context overlap rules, modifier handling edge cases. Tests focus on basic resolution, not the conflict checking system or modifier key combinations.
**Impact:** MAJOR - Input system is UI critical path. Untested: keybinding conflict detection, context overlap rules (fleet/strategy/detail_panel), multiple modifier key combinations (Ctrl+Shift+Alt), edge cases in lookup table building.
**Recommendation:** Add tests for:
  - Conflict detection with overlapping contexts
  - All modifier combinations (CTRL, SHIFT, ALT)
  - _rebuild_lookup() correctness with complex bindings
  - Context overlap resolution (7 overlapping contexts defined)
**Effort:** Medium

#### MAJOR: Paths Module - No Unit Tests
**ID:** TCG-FND-005
**Location:** `game/core/paths.py` (134 lines)
**Issue:** Path resolution module with critical initialization function `_find_project_root()` has no unit tests. Only indirect testing through resource loading tests.
**Impact:** MAJOR - Path resolution is initialization critical path. Untested: project root discovery algorithm (searches up 10 parents), fallback to defaults, edge cases with symlinks or non-standard directory structures.
**Recommendation:** Create `tests/unit/core/test_paths.py` with:
  - Project root discovery with various starting positions
  - Error handling when root not found
  - All path constants are valid (DATA_DIR, ASSET_DIR, etc.)
  - Accessors (get_data_dir(), get_assets_dir(), etc.)
**Effort:** Medium

#### MAJOR: Screenshot Manager - No Unit Tests
**ID:** TCG-FND-006
**Location:** `game/core/screenshot_manager.py` (219 lines)
**Issue:** Singleton screenshot manager with clipboard integration, file I/O, and threading has zero unit tests. Functionality: capture to file, region clipping, clipboard copy (Tkinter + Windows fallback).
**Impact:** MAJOR - Thread-safe singleton pattern with fallback clipboard system. Untested: singleton instance creation/reset, region clipping bounds checking, clipboard failures (both Tkinter and Windows clip), file I/O errors, disabled screenshot state.
**Recommendation:** Create `tests/unit/core/test_screenshot_manager.py` with:
  - Singleton pattern enforcement (reset, multiple instance calls)
  - File save with various surfaces and regions
  - Region bounds validation (clipping outside surface)
  - Clipboard fallback mechanisms (mock Tkinter failure → clip fallback)
  - IO error handling
**Effort:** Medium

#### MAJOR: AI Controller - Incomplete Coverage
**ID:** TCG-FND-007
**Location:** `game/ai/controller.py` (500+ lines)
**Issue:** AIController is tested in integration but unit tests don't cover all public methods. Missing: behavior selection logic, strategy resolution, engage distance calculations, targeting with special cases (satellites, dead targets).
**Impact:** MAJOR - Controller is combat decision-making hub. Untested paths: behavior selection with retreat threshold, strategy resolution failures, formation dropout recovery, engage distance multiplier with invalid policies.
**Recommendation:** Expand unit test coverage for:
  - `get_resolved_strategy()` with missing strategies
  - `get_engage_distance_multiplier()` with edge cases
  - Behavior selection (alive check, formation, retreat logic)
  - Formation constraints with invalid/dead masters
**Effort:** Medium

#### MAJOR: Strategy Manager - Singleton State Not Fully Tested
**ID:** TCG-FND-008
**Location:** `game/ai/strategy_manager.py` (200+ lines)
**Issue:** StrategyManager is a singleton that resolves combat strategies from IDs. Has basic tests (`test_strategy_manager_singleton.py`) but missing: invalid strategy ID handling, fallback behavior, concurrent access, strategy validation.
**Impact:** MAJOR - Strategy resolution is critical path for AI decision-making. Untested: missing strategy IDs, None returns, concurrent resolution attempts, invalid strategy data structures.
**Recommendation:** Add error path tests:
  - resolve_strategy() with invalid/missing IDs
  - Thread safety with concurrent access
  - Strategy validation (required fields present)
  - Fallback to default strategy
**Effort:** Medium

#### MAJOR: Target Evaluator - Rule Evaluation Edge Cases
**ID:** TCG-FND-009
**Location:** `game/ai/target_evaluator.py` (500+ lines)
**Issue:** TargetEvaluator has comprehensive rule tests but missing edge cases: division by zero (range penalties), position access failures with different entity types, distance_cache behavior, stat helper customization limits.
**Impact:** MAJOR - Target evaluation is combat decision-making core. Untested: safe distance calculation with invalid positions, distance_cache concurrent access, stat helper failures, required flag with zero-weight rules.
**Recommendation:** Add edge case tests:
  - Distance calculation with None/invalid positions
  - distance_cache thread safety
  - Custom stat helper edge cases (returning NaN, infinity)
  - Required flag behavior with weight=0
**Effort:** Medium

#### MAJOR: Research Service - Turn Processing Edge Cases
**ID:** TCG-FND-010
**Location:** `game/research/systems/research_service.py` (180+ lines)
**Issue:** ResearchService.process_turn() has basic tests but missing: locked node handling, breakthrough probability capping at 95%, volatility calculations with edge values, tech level tracking consistency.
**Impact:** MAJOR - Research progression is core gameplay loop. Untested: locked node decay, breakthrough chance rollover, volatility=0 handling, invalid node references in tech_levels dict, turn order inconsistencies.
**Recommendation:** Add comprehensive turn processing tests:
  - Locked node handling (decay without progress)
  - Breakthrough probability capping at MAX_CHANCE (0.95)
  - Volatility edge cases (0, very high values)
  - Tech level consistency across turns
  - Event logging accuracy
**Effort:** Medium

### MINOR Issues

#### MINOR: Core Math Module - Vector2 Methods Not Fully Tested
**ID:** TCG-FND-011
**Location:** `game/core/math.py` (230+ lines)
**Issue:** Vector2 class has good coverage of basic operations but missing: `__getitem__` bounds error, `__len__`, `normalize()` on zero vector, `distance_squared_to()`, `rotate()` with various angles, `angle_to()` with specific geometries.
**Impact:** MINOR - Math utilities are widely used but basic functionality is reliable. Missing: negative angle rotation, angle_to() with negative deltas, as_int_tuple() rounding behavior.
**Recommendation:** Add edge case tests for:
  - `__getitem__` with index >= 2 (should raise IndexError)
  - `__len__` returns 2
  - `normalize()` on zero vector (should return zero vector)
  - `rotate()` with negative angles, 360+ degrees
  - `angle_to()` in all quadrants
  - `as_int_tuple()` rounding behavior (0.5, -0.5)
**Effort:** Simple

#### MINOR: Logger Module - No Unit Tests
**ID:** TCG-FND-012
**Location:** `game/core/logger.py` (200+ lines)
**Issue:** Logger singleton has no unit tests, only indirect usage in other tests. Covers log_info, log_warning, log_error, log_debug functions.
**Impact:** MINOR - Logger is utility, not game logic. But: no singleton safety tests, no format validation, no thread safety verification for logging.
**Recommendation:** Create `tests/unit/core/test_logger.py` with:
  - Singleton instance creation and reset
  - Log message formatting
  - Thread safety (concurrent log calls)
  - Handler assignment
**Effort:** Simple

#### MINOR: Profiling Module - Coverage Gaps
**ID:** TCG-FND-013
**Location:** `game/core/profiling.py` (300+ lines)
**Issue:** Profiling decorator and recorder have tests (`test_recording.py`, `test_persistence.py`) but missing: persistence error handling, concurrent recording, decorator with exceptions, history file corruption.
**Impact:** MINOR - Profiling is debug tool, not game logic. But: silent file I/O failures could lose profiling data, no error recovery.
**Recommendation:** Add tests for:
  - Profiling save with permission errors
  - Concurrent profiling sessions
  - Decorator with exception-throwing functions
  - History file corruption handling
**Effort:** Simple

#### MINOR: Validation Module - Error Boundary Tests
**ID:** TCG-FND-014
**Location:** `game/core/validation.py` (180+ lines)
**Issue:** Validation has basic tests (`test_validation.py`) covering common cases but missing: None/empty input handling in all validators, type coercion edge cases, boundary value validation.
**Impact:** MINOR - Validation is defensive layer. Missing: None in lists, empty dicts, numeric edge cases (0, -1, very large numbers).
**Recommendation:** Expand test coverage for:
  - None handling in all validators
  - Empty collections
  - Numeric boundaries
  - Type coercion edge cases
**Effort:** Simple

#### MINOR: Error Codes Module - Enum Coverage
**ID:** TCG-FND-015
**Location:** `game/core/error_codes.py` (100+ lines)
**Issue:** ErrorCode enum has basic tests (`test_error_codes.py`) but missing: all enum values covered, value uniqueness verification, usage in actual error paths.
**Impact:** MINOR - Error codes are metadata. But: missing enum values could indicate incomplete tests, duplicate values would be silent bugs.
**Recommendation:** Add tests for:
  - All ErrorCode enum values are unique
  - All enum members covered
  - Integration test that error raising uses defined codes
**Effort:** Simple

#### MINOR: JSON Utils Module - Edge Cases
**ID:** TCG-FND-016
**Location:** `game/core/json_utils.py` (150+ lines)
**Issue:** JSON utilities have tests (`test_json_utils.py`) but missing: very large file handling, circular reference detection, encoding edge cases (non-ASCII), malformed JSON recovery.
**Impact:** MINOR - JSON utilities are I/O layer. Missing: streaming large files, non-UTF8 encoding fallback, partial JSON recovery.
**Recommendation:** Add tests for:
  - Large JSON file handling
  - Non-ASCII character encoding
  - Malformed JSON graceful degradation
  - Circular reference detection
**Effort:** Simple

#### MINOR: Configuration Module - Edge Cases
**ID:** TCG-FND-017
**Location:** `game/core/config.py` (500+ lines)
**Issue:** Config has basic tests (`test_config.py`) but many dataclasses with limited coverage of validation, invalid config combinations, range boundaries.
**Impact:** MINOR - Config changes are infrequent. But: invalid physics constants could cause simulation divergence, untested ranges could allow invalid states.
**Recommendation:** Expand config tests:
  - Boundary value testing for all numeric configs
  - Invalid combinations (max < min)
  - Type validation for all fields
**Effort:** Simple

#### MINOR: AI Interfaces - Adapter Coverage
**ID:** TCG-FND-018
**Location:** `game/ai/interfaces/controllable.py` (200+ lines)
**Issue:** ShipControllableAdapter has tests (`controllable_interface/` tests) but missing: method call forwarding correctness, attribute access patterns, None return handling.
**Impact:** MINOR - Adapter is abstraction layer. Missing: verify all interface methods delegate correctly, return value transformations.
**Recommendation:** Add comprehensive adapter tests:
  - All interface methods delegate to underlying ship
  - Return value transformations correct
  - None/missing attribute handling
**Effort:** Simple

#### MINOR: Research Tracker - Serialization Edge Cases
**ID:** TCG-FND-019
**Location:** `game/research/data/research_tracker.py` (180+ lines)
**Issue:** ResearchTracker has basic tests (`test_research_tracker.py`) but missing: serialization round-trip with edge values (0 RP, max levels), NodeState edge cases, session seed randomness.
**Impact:** MINOR - Research state is game state. Missing: save/load with extreme values, NodeState boundary conditions.
**Recommendation:** Add tests for:
  - Serialization with edge value levels (0, 1, max_level)
  - NodeState round-trip correctness
  - Session seed consistency
  - Empty node_states dict handling
**Effort:** Simple

#### MINOR: Engine Physics - Floating Point Edge Cases
**ID:** TCG-FND-020
**Location:** `game/engine/physics.py` (250+ lines)
**Issue:** PhysicsBody has tests (`test_physics.py`) but missing: floating point precision edge cases, zero mass handling, infinite velocity/acceleration clamping.
**Impact:** MINOR - Physics is simulation layer. Missing: very small velocities (< 1e-10), very large forces, division by near-zero mass.
**Recommendation:** Add precision tests:
  - Zero/near-zero velocity handling
  - Velocity clamping with extreme forces
  - Floating point precision preservation
**Effort:** Simple

#### MINOR: Spatial Grid - Query Performance Edge Cases
**ID:** TCG-FND-021
**Location:** `game/engine/spatial.py` (36 lines)
**Issue:** SpatialGrid has basic tests (`test_spatial.py`) but missing: radius query correctness at cell boundaries, performance with large grids, negative coordinate handling.
**Impact:** MINOR - Spatial grid is optimization layer. Missing: boundary query correctness (objects exactly on cell boundary), performance characteristics.
**Recommendation:** Add edge case tests:
  - Radius queries spanning cell boundaries
  - Negative coordinates
  - Empty grid queries
  - Large radius queries performance
**Effort:** Simple

## Top 5 Priority Issues

### 1. **TCG-FND-001: Hex Math Module - No Unit Test Coverage** [CRITICAL]
Impact: Hex coordinates are foundation for galaxy generation and fleet positioning. Missing edge cases could cause pathfinding failures, coordinate wrapping bugs, or serialization data corruption.
Effort: Medium
Recommendation: Create dedicated unit test file with comprehensive hex coordinate tests (15-20 test cases).

### 2. **TCG-FND-002: AI Behaviors Module - No Unit Tests** [CRITICAL]
Impact: Behaviors drive all combat AI. Missing unit tests mean behavior initialization failures, state transitions, and edge cases are untested.
Effort: Complex
Recommendation: Create comprehensive unit test suite for all 11 behavior classes with lifecycle and state transition testing.

### 3. **TCG-FND-003: Registry Loading - No Error Path Tests** [CRITICAL]
Impact: Registry initialization is critical path. Error handling is untested, could leave registries in inconsistent state if file I/O fails.
Effort: Medium
Recommendation: Create error path tests for all 5 exception handlers with mocked file I/O failures.

### 4. **TCG-FND-005: Paths Module - No Unit Tests** [MAJOR]
Impact: Path resolution is initialization critical path. Project root discovery algorithm is untested.
Effort: Medium
Recommendation: Create dedicated unit test file for path resolution and root discovery.

### 5. **TCG-FND-006: Screenshot Manager - No Unit Tests** [MAJOR]
Impact: Singleton with clipboard integration and file I/O. Thread safety and fallback mechanisms are untested.
Effort: Medium
Recommendation: Create unit test file with singleton pattern, I/O error handling, and clipboard fallback testing.

## Coverage Summary by Module

### Core Module Coverage
- ✓ Constants (99% - basic enum tests)
- ✓ Input Actions (85% - basic enum tests)
- ✓ Input Mapper (75% - missing conflict detection)
- ✓ Protocols (90% - good protocol tests)
- ✓ Exceptions (90% - exception hierarchy tests)
- ✓ Service Injection (85% - DI tests)
- ✓ Registry (90% - fixture and manager tests)
- ✗ Hex Math (5% - integration tests only, no unit tests)
- ✗ Logger (0% - no unit tests)
- ✗ Paths (10% - indirect testing only)
- ✗ Profiling (30% - some recording tests, missing error paths)
- ✗ Resources (50% - success path only, no error paths)
- ✗ Screenshot Manager (0% - no unit tests)
- ✓ Validation (80% - missing boundary cases)
- ✓ Error Codes (70% - missing comprehensive enum coverage)

### AI Module Coverage
- ✓ Target Evaluator (85% - rules tested, missing edge cases)
- ✓ Controllable Interface (80% - adapter tests present)
- ✓ Behaviors (40% - scattered tests, no dedicated unit tests)
- ✗ AIController (60% - integration tests, missing unit coverage)
- ✗ StrategyManager (50% - basic singleton test, missing error paths)

### Research Module Coverage
- ✓ Tech Tree (90% - loading and query tests)
- ✓ Tech Node (85% - state and status tests)
- ✓ Research Tracker (75% - basic state tests, missing edge cases)
- ✓ Research Service (70% - process_turn tested, missing edge cases)

### Engine Module Coverage
- ✓ Collision (75% - raycasting tests present)
- ✓ Spatial (80% - grid basics tested)
- ✓ Physics (80% - basic movement tests)

## Recommendations

1. **Immediate (Week 1):** Address CRITICAL issues (TCG-FND-001, 002, 003)
   - Create hex_math unit tests (8-10 hours)
   - Create error path tests for resource loading (4-6 hours)
   - Begin AI behaviors unit tests (ongoing)

2. **Short Term (Week 2-3):** Address MAJOR issues
   - Paths module unit tests
   - Screenshot manager unit tests
   - Input mapper conflict detection tests
   - Expand AI controller coverage

3. **Long Term:** Address MINOR issues and expand edge case coverage
   - Logger unit tests
   - Configuration boundary value tests
   - Vector2 edge case tests
   - Research tracker serialization round-trip tests

---

**Generated:** 2026-02-11
**Test Baseline:** 7353 tests passing
**Expected Coverage Impact:** +150-200 new tests addressing CRITICAL and MAJOR gaps
