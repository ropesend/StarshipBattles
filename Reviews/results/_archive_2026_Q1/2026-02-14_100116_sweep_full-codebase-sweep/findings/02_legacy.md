# Legacy System Holdovers Sweep: Antigravity

## Summary
- **Shard:** Antigravity (Full Sweep)
- **Files Scanned:** 370+
- **Total Issues Found:** 2
- **Critical:** 0 | **Major:** 1 | **Minor:** 1 | **Info:** 0

## Findings

#### MAJOR: Widespread Singleton Usage Violating DI
**ID:** LEG-AG-001
**Location:** Multiple files (`game/ui/services/*.py`, `game/assets/*.py`)
**Issue:** Many services (`ShipFactory`, `AssetManager`, `RegistryLoader`) use `SingletonMeta` and `.instance()` access instead of Dependency Injection.
**Impact:** Violation of "Dependency injection over singletons" rule in CLAUDE.md. Makes testing harder (requires `reset()` hacks) and couples components tightly.
**Recommendation:** Refactor these services to be instantiated and passed via context/registries, removing `SingletonMeta`.
**Effort:** Complex (requires updating many call sites)

#### MINOR: Legacy Comments and Todos
**ID:** LEG-AG-002
**Location:** General Codebase
**Issue:** `grep` showed no explicit "deprecated" tags, but the presence of singleton resets and "lazy" global accessors suggests incomplete migration to strict DI.
**Impact:** Maintenance burden entrained by mixed access patterns (some DI, some Singleton).
**Recommendation:** Enforce DI usage in new code and incrementally refactor old singletons.
**Effort:** Medium

## Top Priority Issues
1. **Singleton Elimination**: The project has committed to DI, but core services like `AssetManager` remain global singletons.
