# Test Naming Consistency Report

## Summary
- **Total issues found:** 25
- **Critical:** 7, **Major:** 10, **Minor:** 6, **Info:** 2

---

## Critical Issues

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
**Location:** `game/ui/screens/builder/ → tests/unit/builder/`, `game/simulation/components/abilities/ → tests/unit/abilities/`
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

### TNC-008: Inconsistent Fixture Naming Across Conftest Files
**Location:** 13 `conftest.py` files at various levels
**Issue:** Fixtures defined at multiple levels with varying naming conventions
**Recommendation:** Document fixture hierarchy; use clear naming: `{scope}_{resource}`
**Effort:** Medium

### TNC-009: Mock/Stub Naming Inconsistency
**Location:** `MockEventBus`, `MockMissile`, `MockPlanet`, `MockSystem`
**Issue:** Mock classes use `Mock*` prefix inconsistently
**Recommendation:** Adopt consistent pattern: `Mock*` for test doubles
**Effort:** Simple

### TNC-010: Factory Function Naming Not Standardized
**Location:** `create_test_ship()`, `create_component()` - mixed naming patterns
**Issue:** Factory functions use `create_*()` inconsistently alongside test fixtures
**Recommendation:** Use `pytest.fixture` with factory pattern
**Effort:** Medium

### TNC-011: No Descriptive Test Method Naming Convention
**Location:** All test methods follow simple `test_*()` pattern
**Issue:** Test methods lack behavior indicators: no `test_should_*`, `test_when_*` patterns
**Recommendation:** Adopt BDD-style naming: `test_should_*()` or descriptive names
**Effort:** Complex

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

## Top 5 Priority Issues

1. **TNC-002: Inverted Directory Structure** - Collapses source hierarchy, breaking structural parity
2. **TNC-001: Non-Standard Test File Names** - 18+ files with inconsistent prefixes
3. **TNC-004: Incomplete Directory Mapping** - 14+ missing test directories
4. **TNC-006: Test Class Not Mapped to Source** - Multiple test classes per file with no clear source mapping
5. **TNC-011: No Descriptive Test Method Naming** - Test purpose unclear; BDD patterns would improve clarity
