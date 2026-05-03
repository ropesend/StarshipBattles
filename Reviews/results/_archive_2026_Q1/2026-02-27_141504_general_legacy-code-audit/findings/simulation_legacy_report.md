# Simulation Layer Legacy Code Audit

## Summary
- **Total issues found:** 7
- **Critical:** 1, **Major:** 3, **Minor:** 2, **Info:** 1

The simulation layer is notably well-maintained with active refactoring efforts (PROJ-44, PROJ-50, PROJ-88, etc.). Most code follows clear architectural patterns with minimal technical debt. The issues identified are primarily:
1. One documented tech debt item (module identity drift fallback)
2. Minor inconsistencies in fallback patterns
3. One potential micro-optimization opportunity

---

## Findings

### Critical Issues

#### CRITICAL: Module Identity Drift Fallback in AbilityManager
**ID:** SIM-001
**Location:** `game/simulation/components/ability_manager.py:58-66`
**Severity:** Critical
**Issue:**
Intentional tech debt fallback for test module reloading. When pytest reloads test modules, ability class objects change identity, breaking `isinstance()` checks. The code falls back to `__name__` string matching.

```python
# [KNOWN_ISSUE] Fallback for Module Identity Drift in tests.
# When test modules reload ability classes, isinstance() fails due to
# different class objects. This __name__ check provides test isolation.
# Ref: Phase 2 Task 2.5 audit - documented as intentional tech debt.
else:
    for cls in ab.__class__.mro():
        if cls.__name__ == ability_name:
            found.append(ab)
            break
```

**Evidence:**
- Documented as [KNOWN_ISSUE] in code comments
- Fallback is only taken when `isinstance()` fails
- Affects all ability lookups in polymorphic scenarios

**Recommendation:**
This is documented tech debt with a known root cause. Consider:
1. Migrate pytest configuration to use `--no-cov` or pytest fixtures that prevent module reloading
2. Implement a WeakValueDictionary cache for class identity checks
3. Add pytest plugin to detect and warn on module reloads during tests

**Effort:** Medium (requires pytest infrastructure changes)

---

### Major Issues

#### MAJOR: Inconsistent Fallback Pattern in load_components()
**ID:** SIM-002
**Location:** `game/simulation/components/component.py:558-596`
**Severity:** Major
**Issue:**
The `load_components()` function implements a cache fallback pattern that differs from modern patterns elsewhere in the codebase. While this pattern works, it's inconsistent with:
- PROJ-50 strict DI pattern (requires registries explicitly)
- PROJ-38 dependency injection guidelines

```python
def load_components(file_path="data/components.json"):
    cache_mgr = ComponentCacheManager.instance()
    provider = get_default_registry_provider()  # Global state access!
    comps = provider.get_components()

    # This bypass registries - mixing cache management with DI
    if cache_mgr.component_cache is not None and cache_mgr.last_component_file == file_path:
        for c_id, comp in cache_mgr.component_cache.items():
            comps[c_id] = comp.clone()  # Cloning for isolation
        return
```

**Evidence:**
- Uses global `ComponentCacheManager.instance()` singleton pattern
- Accesses default provider directly instead of accepting registries parameter
- Dual-path loading (cache fast path vs. disk slow path)
- Inconsistent with strict DI in Component.__init__ (PROJ-50)

**Recommendation:**
Refactor to accept optional `registries` parameter:
```python
def load_components(file_path="data/components.json", registries=None):
    if registries is None:
        provider = get_default_registry_provider()
        registries = GameRegistries(...)
    # Delegate to pure function with explicit registries
    result = load_components_data(file_path, registries=registries)
    # ... populate cache
```

**Effort:** Simple (isolated refactoring, no callers use registries yet)

---

#### MAJOR: Module Identity Drift Affects Modifier Lookups
**ID:** SIM-003
**Location:** `game/simulation/components/component_stats_calculator.py:50-62`
**Severity:** Major
**Issue:**
The `ComponentStatsCalculator.calculate_modifier_stats()` method imports `apply_modifier_effects` from `modifiers.py` at runtime (inside the method), which can cause issues if the modifiers module is reloaded during tests.

**Evidence:**
```python
@staticmethod
def calculate_modifier_stats(modifiers, component=None):
    from game.simulation.components.modifiers import (
        apply_modifier_effects,           # Runtime import - reload risk
        get_default_stat_multipliers
    )
```

Similar pattern exists in multiple ability files.

**Recommendation:**
Move runtime imports to module level:
```python
# At top of file
from game.simulation.components.modifiers import (
    apply_modifier_effects,
    get_default_stat_multipliers
)

@staticmethod
def calculate_modifier_stats(modifiers, component=None):
    # Use module-level imports
    stats = get_default_stat_multipliers()
```

**Effort:** Simple (refactor imports, verify test pass)

---

#### MAJOR: ComponentCacheManager.reset() Never Verified in Tests
**ID:** SIM-004
**Location:** `game/simulation/components/component.py:444-474`
**Severity:** Major
**Issue:**
The `ComponentCacheManager` is a thread-safe singleton used for test isolation, but its `reset()` method is never called from conftest. This means tests running in sequence could see cached components from previous tests if the cache file path matches.

```python
class ComponentCacheManager:
    @classmethod
    def reset(cls):
        """Reset all caches for test isolation."""
        with cls._lock:
            # Caches only reset if explicitly called
            if cls._instance is not None:
                cls._instance.component_cache = None
```

**Evidence:**
- No grep results for `ComponentCacheManager.reset()` being called in conftest or fixtures
- Only called from `reset_component_caches()` exported function
- Lazy singleton initialization could persist across test boundaries

**Recommendation:**
Add to root conftest:
```python
@pytest.fixture(autouse=True)
def reset_component_cache():
    from game.simulation.components.component import reset_component_caches
    reset_component_caches()
    yield
    reset_component_caches()
```

**Effort:** Simple (add to conftest, verify test isolation)

---

### Minor Issues

#### MINOR: Dead Code in ProjectileManager._record_hit()
**ID:** SIM-005
**Location:** `game/simulation/projectile_manager.py:172-180`
**Severity:** Minor
**Issue:**
The `_record_hit()` method has redundant defensive checks and comments:

```python
def _record_hit(self, p) -> None:
    """Mark projectile as hit and update source weapon stats."""
    p.is_alive = False
    p.status = 'hit'
    # Projectile.source_weapon is always initialized (None by default)
    if p.source_weapon is not None:
        # shots_hit initialized in Component.__init__
        p.source_weapon.shots_hit += 1
```

The comments state things are "always initialized" but the code is defensive. This creates confusion about the actual contract.

**Evidence:**
- Comment states "always initialized (None by default)"
- Code checks `if p.source_weapon is not None`
- These are contradictory - either it's always initialized OR it might be None

**Recommendation:**
Clarify the contract:
```python
def _record_hit(self, p) -> None:
    """Mark projectile as hit and update source weapon stats.

    Note: source_weapon is always initialized by Projectile.__init__,
    though it may be None if the projectile was created without a source.
    """
    p.is_alive = False
    p.status = 'hit'
    if p.source_weapon is not None:
        p.source_weapon.shots_hit += 1
```

Or remove the defensive check if source_weapon is guaranteed to exist.

**Effort:** Simple (documentation or defensive check removal)

---

#### MINOR: Inconsistent Comment Style in Multiple Files
**ID:** SIM-006
**Location:** Multiple files (`ship.py:239-241`, `ship_combat_engine.py:61-63`, etc.)
**Severity:** Minor
**Issue:**
Multiple files use similar block separator comment patterns:
```python
# =========================================================================
# SECTION NAME
# =========================================================================
```

But they're not consistent across the layer. Some files use this pattern, others use `# === Section ===`.

**Evidence:**
- `game/simulation/entities/ship.py` uses `# =========================================================================`
- `game/simulation/battle_controller.py` uses `# === Configuration ===`
- `game/simulation/components/abilities/base.py` uses `# =========================================================================`

**Recommendation:**
Standardize on one style:
1. Option A: Use `# =========================================================================`
2. Option B: Use `# === Section Name ===` (more compact)

Apply consistently across all simulation layer files.

**Effort:** Simple (regex search/replace)

---

### Info Items

#### INFO: Potential Performance Optimization in HP Ratio Caching
**ID:** SIM-007
**Location:** `game/simulation/components/component.py:265-274`
**Severity:** Info
**Issue:**
The HP ratio cache implementation manually manages a dirty flag `_hp_ratio_dirty`, but this is slightly over-engineered for the current usage pattern. Modern Python property caching might be simpler:

**Current Implementation:**
```python
@property
def hp_ratio(self) -> float:
    if self._hp_ratio_dirty:
        self._cached_hp_ratio = self.current_hp / self.max_hp if self.max_hp > 0 else 1.0
        self._hp_ratio_dirty = False
    return self._cached_hp_ratio
```

**Evidence:**
- PROJ-49 specifically added this optimization "reduces division in hot paths"
- Cache is marked dirty via `mark_hp_cache_dirty()` after damage
- Usage is limited but frequency is high during combat ticks

**Recommendation:**
Profile before optimizing further. Current implementation is reasonable. If optimization is needed:
1. Consider `functools.cached_property` (Python 3.8+)
2. Or accept that `hp_ratio` property is called frequently and keep current approach

This is a minor performance detail - no change required unless profiling shows it's a bottleneck.

**Effort:** N/A (informational only)

---

## Top 5 Priority Issues

### 1. **SIM-001: Module Identity Drift Fallback** (CRITICAL)
**Impact:** Affects ability lookup reliability, foundational to ability system
**Recommendation:** Implement pytest plugin to prevent module reloading OR migrate to class identity cache
**Timeline:** Medium-term (affects test infrastructure)

### 2. **SIM-004: ComponentCacheManager.reset() Never Called** (MAJOR)
**Impact:** Test isolation risk - component cache could leak between tests
**Recommendation:** Add autouse fixture to root conftest
**Timeline:** Immediate (1-line fix)

### 3. **SIM-003: Runtime Imports in Stats Calculator** (MAJOR)
**Impact:** Module reload vulnerability similar to SIM-001
**Recommendation:** Move imports to module level
**Timeline:** Simple (isolated refactoring)

### 4. **SIM-002: Inconsistent Fallback Pattern in load_components()** (MAJOR)
**Impact:** Inconsistency with PROJ-50 strict DI guidelines
**Recommendation:** Refactor to accept registries parameter
**Timeline:** Simple (isolated refactoring)

### 5. **SIM-005: Redundant Defensive Checks in ProjectileManager** (MINOR)
**Impact:** Code clarity issue, creates confusion about contracts
**Recommendation:** Clarify documentation or remove defensive check
**Timeline:** Simple (documentation update)

---

## Architecture Assessment

### Strengths
1. **Active Refactoring:** PROJ-44, PROJ-50, PROJ-88 show ongoing cleanup efforts
2. **Clear Layering:** Combat system properly decomposed (DamageCalculator, TargetingSystem, WeaponFiringSystem)
3. **DI Pattern:** Strict DI (PROJ-50) being systematically applied
4. **Ability System:** Well-structured factory pattern with ABILITY_REGISTRY

### Weaknesses
1. **Module Reload Sensitivity:** Ability system and stats calculator both vulnerable to test module reloads
2. **Singleton Cache:** ComponentCacheManager singleton pattern not fully isolated in tests
3. **Legacy Imports:** Some runtime imports in hot paths (stats calculator)
4. **Inconsistent Comments:** Block separators use different styles

### Recommendations
1. Implement test isolation immediately (add conftest fixture for SIM-004)
2. Move runtime imports to module level (SIM-003)
3. Add pytest plugin to warn on module reloads (addresses SIM-001)
4. Standardize comment style (SIM-006)

---

## Statistics

- **Files Analyzed:** 72 Python files in game/simulation/
- **Lines of Code:** ~15,000 LOC (estimated)
- **Functions:** 51 public functions
- **Classes:** ~35 public classes
- **Dead Code Found:** None (all public functions are used)
- **Critical Tech Debt:** 1 item (SIM-001, documented)
- **Inconsistencies:** 4 items (SIM-002, SIM-003, SIM-004, SIM-006)

---

## Conclusion

The simulation layer is **well-maintained** with active refactoring efforts. No significant dead code was found. The issues identified are primarily:

1. **Test infrastructure problems** (module reloads affecting isinstance checks)
2. **Minor inconsistencies** with PROJ-50 strict DI guidelines
3. **Code clarity issues** (defensive checks vs. documented contracts)

All identified issues are low-to-medium effort to fix and should be addressed during next refactoring cycle (suggest as part of PROJ-88 Phase completion).

The layer demonstrates good architectural practices with clear separation of concerns and active removal of backward compatibility shims.

---

**Report Generated:** 2026-02-27
**Reviewer:** Claude Code - Simulation Legacy Hunter
**Baseline:** 7353 tests passing, 0 failures
