# Testing & Test Infrastructure

**Theme:** Test organization, naming conventions, test coverage gaps, disabled tests, fixture issues, and test quality concerns.

---

## Critical Issues

### TSR-001: Disabled Integration Tests
**ID:** TSR-001
**Location:** `tests/integration/_test_formation_attack.py`, `tests/integration/_test_formation_flight.py`
**Issue:** Two integration test files are prefixed with `_test_` instead of `test_`, disabling them from the test suite
**Impact:** Critical formation flight and attack AI behavior tests are not running; potential regressions go undetected
**Recommendation:** Rename files to `test_formation_attack.py` and `test_formation_flight.py` to re-enable
**Effort:** Simple

---

### TSR-002: Incomplete Test with Dead Code
**ID:** TSR-002
**Location:** `tests/integration/_test_formation_attack.py:101`
**Issue:** Line 101 contains only `pass` statement followed by untested code; indicates incomplete test setup
**Impact:** Target dummy creation logic after `pass` is never executed
**Recommendation:** Complete the test setup or remove dead code after pass statement
**Effort:** Medium

---

### TSR-003: Non-Isolated Test Framework
**ID:** TSR-003
**Location:** `tests/unit/core/test_registry.py:23-77`
**Issue:** Multiple conftest.py files (13 total) with inconsistent fixture scope and reset strategies
**Impact:** Test isolation bugs can be hidden; registry state can leak between test classes
**Recommendation:** Standardize on function-scoped fixtures with consistent reset patterns
**Effort:** Complex

---

### TSR-004: Weak Assertion Patterns
**ID:** TSR-004
**Location:** ~24 files use generic assertions like `assert result`, `assert x`
**Issue:** 875 weak assertions identified without specific expected values
**Impact:** Tests pass without verifying actual behavior; false positives in coverage
**Recommendation:** Replace weak assertions with specific value checks
**Effort:** Medium

---

### TSR-005: Large Test Monoliths
**ID:** TSR-005
**Location:** 20 test files exceed 700+ LOC:
  - `test_ship_stats_service.py`: 1756 LOC
  - `test_ship_instance_proj08.py`: 1458 LOC
  - `test_battle_controller.py`: 1317 LOC
  - `test_fleet.py`: 1103 LOC
**Issue:** Mega-tests make it hard to isolate failures
**Impact:** Test failures are hard to diagnose; slow feedback loop
**Recommendation:** Break into smaller focused test classes with single responsibility
**Effort:** Complex

---

### TSR-006: Multiple Mock Patterns
**ID:** TSR-006
**Location:** 3011 mock/patch usages found; inconsistent between files
**Issue:** `@mock.patch`, `@patch`, `Mock()`, `MagicMock()` used interchangeably
**Impact:** Inconsistent test setup/teardown; harder to understand mock dependencies
**Recommendation:** Establish shared patterns in base test classes or fixture helpers
**Effort:** Medium

---

### TSR-007: Fixture Scope Mismatch
**ID:** TSR-007
**Location:** `tests/unit/research/conftest.py`, `tests/test_framework/services/conftest.py`
**Issue:** Mix of function-scoped, class-scoped, and module-scoped fixtures with no clear documentation
**Impact:** Tests may share state unexpectedly; cleanup doesn't happen at expected times
**Recommendation:** Document fixture scope strategy; use function-scoped by default
**Effort:** Medium

---

### TSR-008: Test Organization Inconsistency
**ID:** TSR-008
**Location:** tests directory structure
**Issue:** Tests organized both by feature and by layer, causing redundancy
**Impact:** Hard to find tests for specific features; potential for duplicate testing effort
**Recommendation:** Standardize on either feature-based or layer-based organization
**Effort:** Complex

---

### TNC-001: Non-Standard Test File Naming Convention
**ID:** TNC-001
**Location:** `tests/performance/benchmark_planet_list.py`, `tests/unit/performance/stress_test.py`, `tests/repro_issues/repro_bug_05_deep.py`
**Issue:** 18+ test/script files use non-standard prefixes: `repro_*.py`, `reproduce_*.py`, `verify_*.py`, `benchmark_*.py`
**Impact:** Inconsistent test discovery, unclear whether files are executable scripts vs. pytest-runnable tests
**Recommendation:** Standardize all test files to `test_*.py` prefix or move non-pytest scripts to separate `scripts/` directory
**Effort:** Medium

---

### TNC-002: Inverted Directory Structure Naming
**ID:** TNC-002
**Location:** `game/ui/screens/builder/ -> tests/unit/builder/`, `game/simulation/components/abilities/ -> tests/unit/abilities/`
**Issue:** Test directories collapse/flatten multi-level source structures, breaking structural parity
**Impact:** Confusion about source-to-test mapping, difficulty navigating parallel codebases
**Recommendation:** Mirror full directory structure: `tests/unit/ui/screens/builder/`, `tests/unit/simulation/components/abilities/`
**Effort:** Complex

---

### TNC-003: Disabled Test Files With Leading Underscores
**ID:** TNC-003
**Location:** `tests/integration/_test_formation_attack.py`, `tests/integration/_test_formation_flight.py`
**Issue:** Test files prefixed with `_` indicate disabled tests but aren't consistently named or documented
**Impact:** Unclear test status, potential orphaned/forgotten tests
**Recommendation:** Use `@pytest.mark.skip` or move to separate `archived/` directory
**Effort:** Simple

---

### TNC-004: Incomplete Directory Structure Mapping
**ID:** TNC-004
**Location:** Missing: `tests/unit/ui/`, `tests/unit/assets/`, `tests/unit/research/`, etc.
**Issue:** Many source directories lack corresponding test directories (14+ missing directories)
**Impact:** Tests for UI components scattered across root test directory
**Recommendation:** Create missing test subdirectories to match source structure exactly
**Effort:** Simple

---

### TNC-005: Duplicate Test Filenames
**ID:** TNC-005
**Location:** `tests/unit/core/test_logger.py` and `tests/unit/simulation/test_logger.py`
**Issue:** Two test files with identical names in different directories
**Impact:** Import confusion, difficulty with IDE navigation
**Recommendation:** Rename one to `test_simulation_logger.py`
**Effort:** Simple

---

### TNC-006: Test Class Naming - No Consistent Mapping to Source
**ID:** TNC-006
**Location:** Multiple files: `test_ai.py` contains `TestAIController`, `TestAIStrategyStates`, `TestTargetingHelpers`
**Issue:** Test file may contain multiple unrelated test classes not clearly mapped to source modules
**Impact:** Unclear which source class each test class exercises
**Recommendation:** One test class per source class; use naming convention `Test<SourceClassName>`
**Effort:** Medium

---

### TNC-007: Mixed Test and Support Code
**ID:** TNC-007
**Location:** `tests/infrastructure/session_cache.py` (utility, not a test)
**Issue:** Non-test code mixed with test files
**Impact:** Test discovery includes non-test modules
**Recommendation:** Create dedicated `tests/lib/` or `tests/utils/` for helper/infrastructure code
**Effort:** Medium

---

## Major Issues

### TSR-009: Skipped/Deferred Tests
**ID:** TSR-009
**Location:** 65 pytest.skip calls found throughout tests
**Issue:** Tests conditionally skip based on file presence
**Recommendation:** Make data setup robust or use markers instead of dynamic skips
**Effort:** Medium

---

### TSR-010: Empty/Stub Test Classes
**ID:** TSR-010
**Location:** `tests/unit/builder/test_builder_validation.py:233`
**Issue:** Test classes with only `pass` statements
**Recommendation:** Complete tests or remove them
**Effort:** Medium

---

### TSR-011: Print Statements in Tests
**ID:** TSR-011
**Location:** Multiple files like `test_seeker_range_calculation.py`
**Issue:** `print()` statements in test code for debugging
**Recommendation:** Replace with proper assertions; use logging for diagnostics
**Effort:** Simple

---

### TSR-012: Mixed Test Patterns
**ID:** TSR-012
**Location:** `tests/unit/builder/test_builder_validation.py:270-281`
**Issue:** Tests use both unittest-style methods and pytest-style functions
**Recommendation:** Use pytest fixtures exclusively
**Effort:** Medium

---

### TSR-013: Hardcoded Test Data
**ID:** TSR-013
**Location:** 537 fixture definitions with hardcoded data
**Issue:** Many fixtures inline data instead of using factories
**Recommendation:** Use factory fixtures for complex objects
**Effort:** Medium

---

### TSR-014: Duplicate Test Setup
**ID:** TSR-014
**Location:** `tests/unit/entities/`, `tests/unit/combat/`
**Issue:** Ship setup code repeated across 5+ test files
**Recommendation:** Create shared Ship factory fixtures in conftest
**Effort:** Simple

---

### TSR-015: No Docstrings for Complex Tests
**ID:** TSR-015
**Issue:** ~40% of test classes lack docstrings explaining what behavior they validate
**Recommendation:** Add docstrings to all test classes
**Effort:** Simple

---

### TNC-008: Inconsistent Fixture Naming Across Conftest Files
**ID:** TNC-008
**Location:** 13 `conftest.py` files at various levels
**Issue:** Fixtures defined at multiple levels with varying naming conventions
**Recommendation:** Document fixture hierarchy; use clear naming: `{scope}_{resource}`
**Effort:** Medium

---

### TNC-009: Mock/Stub Naming Inconsistency
**ID:** TNC-009
**Location:** `MockEventBus`, `MockMissile`, `MockPlanet`, `MockSystem`
**Issue:** Mock classes use `Mock*` prefix inconsistently
**Recommendation:** Adopt consistent pattern: `Mock*` for test doubles
**Effort:** Simple

---

### TNC-010: Factory Function Naming Not Standardized
**ID:** TNC-010
**Location:** `create_test_ship()`, `create_component()` - mixed naming patterns
**Issue:** Factory functions use `create_*()` inconsistently alongside test fixtures
**Recommendation:** Use `pytest.fixture` with factory pattern
**Effort:** Medium

---

### TNC-011: No Descriptive Test Method Naming Convention
**ID:** TNC-011
**Location:** All test methods follow simple `test_*()` pattern
**Issue:** Test methods lack behavior indicators: no `test_should_*`, `test_when_*` patterns
**Recommendation:** Adopt BDD-style naming: `test_should_*()` or descriptive names
**Effort:** Complex

---

### TC-06: Test Isolation with GameRegistries
**ID:** TC-06
**Location:** Multiple integration tests
**Issue:** Integration tests don't properly isolate singleton state
**Impact:** Tests fail non-deterministically when run in different orders
**Recommendation:** Create fixture with autouse cleanup
**Effort:** Medium

---

## Coverage Gaps

### TC-01: Untested race_setup_screen.py (1,231 LOC)
**ID:** TC-01
**Location:** `game/ui/screens/race_setup_screen.py`
**Issue:** No dedicated unit test file exists despite 1,231 lines of complex initialization logic
**Impact:** Race selection is the first major gameplay decision affecting entire run
**Recommendation:** Create comprehensive test suite for:
- Race configuration loading and validation
- Environment compatibility calculations
- Stat initialization and caching
- UI state management
**Effort:** Complex

---

### TC-02: Missing Error Path Tests in BattleController
**ID:** TC-02
**Location:** `game/simulation/battle_controller.py:183-193`
**Issue:** Critical error paths not covered:
- `add_ships_from_state()` exception handling
- Multiple `raise RuntimeError/ValueError` statements lack tests
- Retreat state transitions with edge conditions
**Impact:** Battle failures can occur with unhelpful error messages
**Recommendation:** Extend tests to cover all 7 identified error paths
**Effort:** Medium

---

### TC-03: Weak Test Assertions Across 100+ Tests
**ID:** TC-03
**Location:** Throughout unit tests
**Issue:** Generic assertions without context messages:
```python
assert result.success == True  # Doesn't explain failure
assert len(ships) == 2  # No context
```
**Impact:** Test failures are cryptic and hard to debug
**Recommendation:** Add context to assertions:
```python
assert result.success is True, f"Expected success but got: {result.errors}"
```
**Effort:** Medium

---

### TC-04: Untested fleet_report_window (1,034 LOC)
**ID:** TC-04
**Location:** `game/ui/screens/fleet_report_window.py`
**Issue:** No test file found for this complex widget
**Impact:** Fleet overview is critical for strategy gameplay; sorting/filtering untested
**Recommendation:** Create comprehensive test suite for fleet operations
**Effort:** Complex

---

### TC-05: Untested workshop_screen Integration (949 LOC)
**ID:** TC-05
**Location:** `game/ui/screens/workshop_screen.py`
**Issue:** No integration tests for ship design workflow
**Missing Tests:**
- Component placement validation
- Real-time stat recalculation
- Design save/load cycle
- Modifier interaction edge cases
**Impact:** Ship design is core to strategy layer
**Effort:** Complex

---

### TC-07: Edge Case Coverage in Battle System
**ID:** TC-07
**Location:** Battle simulation tests
**Issue:** Missing edge case tests:
- Battle with 0 ships on one team
- Simultaneous ship destruction
- Projectile targeting destroyed ships
- Weapon cooldown edge cases
**Impact:** Rare conditions can cause unhandled exceptions
**Effort:** Medium

---

### TC-08: Missing Save/Load Workflow Tests
**ID:** TC-08
**Location:** `tests/test_save_load.py`
**Issue:** Only tests basic round-trip. Missing:
- Save with partial damage
- Load and verify fleet state integrity
- Corrupted save file recovery
**Impact:** Mid-game state can be lost or corrupted
**Effort:** Medium

---

### TC-09: Research System Integration Gaps
**ID:** TC-09
**Location:** Research system tests
**Issue:** Missing:
- Tech tree unlock cascades
- Research prerequisites becoming unavailable
- Tech conflicts with active production
**Impact:** Research mechanics can fail silently
**Effort:** Medium

---

## Coverage by Module

| Module | Files | Test Files | Assessment | Gap |
|--------|-------|------------|------------|-----|
| Simulation | 45 | 22 | Good, missing edge cases | 15-20% |
| Strategy | 50 | 25 | Good, integration gaps | 10-15% |
| UI/Screens | 55 | 15 | **POOR** | 40-50% |
| AI | 6 | 9 | Excellent | <5% |
| Core | 13 | 12 | Excellent | <5% |
| Builder | 8 | 14 | Good | 10% |

---

## Naming Convention Recommendations

| Aspect | Current | Recommended |
|--------|---------|-------------|
| Test File | `test_*.py` | `test_*.py` (keep) |
| Test Class | `Test*` | `Test<SourceModuleName>` |
| Test Method | `test_*()` | `test_should_*()` or `test_when_*()` |
| Mock Class | `Mock*` | `Mock*` (standardized) |
| Fixture Function | Lowercase | `{scope}_{resource}` |
| Factory Function | `create_*()` | `{resource}_factory()` |
| Disabled Test | `_test_*.py` | `@pytest.mark.skip` |

---

## Overall Test Statistics

- **Production Code:** 237 files, ~62,724 LOC
- **Test Code:** 411 files, ~99,262 LOC
- **Test-to-Code Ratio:** 1.58x
- **Test Functions:** 4,733+
- **Rating:** Good overall with critical gaps in complex UI and edge cases

---

## Top Priority Issues

1. **TSR-001/TNC-003: Disabled Integration Tests** - CRITICAL - Tests are not running due to `_test_` prefix
2. **TSR-003: Non-Isolated Test Framework** - CRITICAL - Multiple conftest files with inconsistent fixture scope
3. **TSR-005: Large Test Monoliths** - CRITICAL - 20 tests with 700+ LOC each
4. **TSR-004/TC-03: Weak Assertion Patterns** - MAJOR - 875 weak assertions provide false confidence
5. **TC-01/TC-04/TC-05: Untested UI Screens** - MAJOR - Core gameplay screens lack test coverage
