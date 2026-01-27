# Core Foundation Analysis Report

## Summary
- **Total issues found:** 4
- **Critical:** 1, **Major:** 2, **Minor:** 1, **Info:** 0

---

## LARGEST ISSUE

### CRITICAL: Singleton Anti-Pattern Creates Systemic Testability Hazards

**ID:** CORE-01

**Location:** `game/core/registry.py:20-247`, `game/core/logger.py:4-91`, `game/core/profiling.py:13-143`, `game/core/screenshot_manager.py:8-120`

**Issue:**
The codebase has 5+ singleton implementations using the traditional `_instance` + `instance()` pattern. The registry singleton is particularly problematic because:

1. **268 direct `RegistryManager.instance()` calls** throughout the codebase create hard dependencies on the singleton
2. **191 calls to `get_component_registry()` and similar functions** still route through the singleton
3. **Incomplete dependency injection** - Services like `ShipStatsService` and `ShipDesignValidator` call `get_component_registry()` directly, making them untestable without the global registry
4. **Test isolation complexity** - conftest.py must manually reset 5+ singletons for each test, creating a maintenance burden and brittle test setup
5. **Stale reference hazard** - The `reset()` method (lines 92-102 in registry.py) explicitly warns about "stale reference hazards"

**Impact on Maintenance/Extensibility:**
- **Testing:** Cannot easily mock registries for unit tests; must use full global state or expensive monkeypatching
- **Extensibility:** Adding new registry types requires modifying singleton class AND all test fixtures
- **Coupling:** Services are tightly coupled to global state, violating dependency inversion principle
- **Refactoring Risk:** 268+ call sites mean any registry restructuring touches the entire codebase
- **Parallelization:** Tests cannot safely run in parallel due to singleton state interference

**Recommendation:**
Introduce **constructor-based dependency injection** as a long-term strategy:
1. Phase 1: Make registry injectable in service constructors (backward compatible)
2. Phase 2: Refactor high-value services to accept registry as constructor parameter
3. Phase 3: Update test fixtures to provide test-specific registries
4. Phase 4: Gradually deprecate `RegistryManager.instance()` direct calls

**Effort:** Complex (phased approach across multiple systems)

---

## Secondary Findings

### MAJOR: Logger Singleton Uses Module-Level Instantiation

**ID:** CORE-02

**Location:** `game/core/logger.py:62` - `_logger = Logger()`

**Issue:**
Line 62 instantiates the logger globally at module import time, bypassing the `instance()` method.

**Impact:** Harder to reset logger state in tests; log files may accumulate or interfere between test runs.

**Recommendation:** Change to lazy instantiation using a proxy pattern.

**Effort:** Simple

---

### MAJOR: No Abstraction Between Services and Registries

**ID:** CORE-03

**Location:** Multiple service files importing directly from `game.core.registry` (20+ files)

**Issue:**
Services directly import and call `get_component_registry()`, creating direct dependencies on the concrete registry implementation.

**Impact:** Cannot swap registry implementations; services are untestable without full registry state.

**Recommendation:** Create protocol definitions for registry interfaces.

**Effort:** Medium

---

### MINOR: Inconsistent Singleton Reset Patterns

**ID:** CORE-04

**Location:** `game/core/registry.py:92-102`, `game/core/logger.py:24-29`, `game/core/profiling.py:59-67`

**Issue:**
Different singletons have different reset semantics (`reset()` vs `clear()`).

**Impact:** Test fixtures are fragile and confusing.

**Recommendation:** Establish a consistent singleton lifecycle policy.

**Effort:** Simple

---

## Assessment

**Overall Health:** Moderate maintenance issues with high risk of future degradation.

**Strengths:**
- Good documentation in docstrings
- Thread-safe implementation
- Protocol definitions exist for domain entities

**Critical Weaknesses:**
- Singleton anti-pattern is pervasive (268+ call sites)
- Testing is expensive (requires manual reset of 7+ singletons)
- Services have hard dependencies on global state
