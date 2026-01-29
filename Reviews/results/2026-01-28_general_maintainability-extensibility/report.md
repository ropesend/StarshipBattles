# Review Report: Maintainability & Extensibility

## Metadata
- **Date:** 2026-01-28
- **Type:** General Review
- **Description:** Comprehensive review focused on top 5 issues affecting maintainability and extensibility
- **Scope:** Entire codebase (237 files, ~62,724 LOC)
- **Agents Used:** 7 (Code Quality, Architecture, Dead Code, Error Handling, Test Coverage, Documentation, Performance)

## Executive Summary
- **Total Findings:** 160+
- **Critical:** 27 | **Major:** 57 | **Minor:** 67 | **Info:** 14
- **Overall Assessment:** Needs Attention

The codebase has a solid foundation with good test coverage (1.58x ratio) and clear layered architecture. However, significant maintainability and extensibility issues exist, primarily in:
1. **God classes** - Several files exceed 800-1200 LOC with too many responsibilities
2. **Global mutable state** - Registries create hidden dependencies and block parallel testing
3. **Layer violations** - UI directly manipulates simulation objects
4. **Dead code** - Broken imports and orphaned files
5. **Documentation gaps** - Critical systems lack documentation

---

## TOP 5 PRIORITY ISSUES

### 1. 🔴 CRITICAL: God Classes Block Maintainability

**Primary Locations:**
- [component.py](../../game/simulation/components/component.py) (878 LOC)
- [race_setup_screen.py](../../game/ui/screens/race_setup_screen.py) (1,231 LOC)
- [builder/main.py](../../game/ui/screens/builder/main.py) (1,100 LOC)

**Issue:** These classes handle too many responsibilities - initialization, rendering, state management, validation, and business logic all in single files. The Component class has 40+ methods spanning abilities, modifiers, stats, damage, and resources.

**Impact on Maintainability:**
- New developers need days to understand the flow
- Any change risks cascading regressions
- Testing requires extensive mocking
- Features are blocked by complexity

**Recommendation:**
```
Phase 1: Extract Component into:
- AbilityManager (ability lookup, activation)
- ModifierManager (modifier application, formula evaluation)
- StatsCalculator (stat recalculation, damage thresholds)

Phase 2: Extract UI screens using ViewModel pattern:
- RaceSetupViewModel (state, data transformations)
- RaceSetupView (rendering only)
```

**Effort:** Complex (2-3 week sprint per class)

---

### 2. 🔴 CRITICAL: Global Mutable State Blocks Extensibility

**Primary Locations:**
- [registry.py](../../game/core/registry.py) - Global COMPONENT_REGISTRY, MODIFIER_REGISTRY
- [component.py:74-75](../../game/simulation/components/component.py#L74) - Direct global access
- 77 files import from game.core.config

**Issue:** Shared global state (`COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, `VEHICLE_CLASSES`) exposed as module-level variables. Registry state persists between tests and scenes.

**Impact on Extensibility:**
- Cannot run tests in parallel
- Cannot swap implementations for testing
- Hidden dependencies across codebase
- Shotgun surgery when refactoring

**Recommendation:**
```python
# Current (problematic):
from game.core.registry import COMPONENT_REGISTRY
components = COMPONENT_REGISTRY.get_all()

# Target (dependency injection):
class Component:
    def __init__(self, data: dict, registries: GameRegistries):
        self._registries = registries
        components = self._registries.components.get_all()
```

**Effort:** Complex (requires systematic migration across 77+ files)

---

### 3. 🔴 CRITICAL: UI Layer Violates Architecture Boundaries

**Primary Locations:**
- [setup.py:94-128](../../game/ui/screens/setup.py#L94) - Creates Ship objects directly
- [builder/main.py:90](../../game/ui/screens/builder/main.py#L90) - Manipulates component layers
- [workshop_screen.py:18-38](../../game/ui/screens/workshop_screen.py#L18) - Accesses ship internals

**Issue:** UI code directly creates `Ship` objects and accesses/modifies internal attributes (`.position`, `.angle`, `.components`). Builder performs validation logic that belongs in simulation layer.

**Impact on Extensibility:**
- Cannot test UI without full simulation
- Cannot swap simulation implementations
- Changes to Ship class break UI
- Duplicate validation logic

**Recommendation:**
```
1. Create UI-facing DTOs (ShipViewDTO, ComponentViewDTO)
2. Use Command pattern for mutations (SetPositionCommand, AddComponentCommand)
3. Extract business logic to ShipDesignService
4. UI depends on interfaces, not implementations
```

**Effort:** Complex (requires adapter layer design)

---

### 4. 🟡 MAJOR: Broken Imports and Dead Code

**Primary Locations:**
- [app.py:28-29](../../game/app.py#L28) - Imports non-existent modules
- `ui/test_lab_scene.py.backup` - 2,731 line backup committed
- `_marked_for_deletion_2026-01-27/` - Orphaned directory

**Issue:** Main application imports modules that don't exist at referenced paths. Backup files and marked-for-deletion directories clutter repository.

**Impact on Maintainability:**
- Runtime ImportError when certain game states activated
- Repository bloat and confusion
- Incomplete cleanup from refactoring

**Recommendation:**
```bash
# Quick wins (< 1 hour):
1. Delete ui/test_lab_scene.py.backup
2. Delete _marked_for_deletion_2026-01-27/
3. Fix or remove imports in app.py lines 28-29
```

**Effort:** Simple (immediate cleanup possible)

---

### 5. 🟡 MAJOR: Critical Systems Lack Documentation

**Primary Locations:**
- [event_bus.py](../../game/ui/screens/builder/event_bus.py) - No documentation at all
- [modifier_logic.py:10-100](../../game/ui/screens/builder/modifier_logic.py#L10) - Complex ability detection undocumented
- [weapons.py](../../game/simulation/components/abilities/weapons.py) - Formula parsing logic undocumented

**Issue:** Critical pub/sub pattern (EventBus), ability detection logic, and formula evaluation have zero documentation. New developers cannot understand the flow without reverse-engineering.

**Impact on Maintainability:**
- Onboarding takes 3x longer
- Bugs introduced when modifying undocumented code
- Knowledge trapped in original authors

**Recommendation:**
```
Priority documentation targets:
1. EventBus - Add module docstring explaining event flow
2. WeaponAbility - Document formula string format ('=' prefix, fallbacks)
3. ModifierLogic - Explain ability detection strategy
4. BattleController - Document BattleResult structure
```

**Effort:** Medium (2-3 days for critical systems)

---

## Quick Wins (Simple Fixes)

| Issue | Location | Fix | Effort |
|-------|----------|-----|--------|
| Delete backup file | `ui/test_lab_scene.py.backup` | Remove file | 1 min |
| Delete orphaned dir | `_marked_for_deletion_2026-01-27/` | Remove directory | 1 min |
| Fix broken imports | `app.py:28-29` | Update import paths | 30 min |
| Extract image scaling | 10+ UI files | Create `scale_to_fit()` utility | 1 hour |
| Add assertion context | 100+ test files | Add f-string context | 2-3 hours |
| Replace bare except | `scripts/apply_resource_costs.py:96` | Specific exception | 15 min |

---

## Findings by Category

### Code Quality (23 findings)
- Critical: 3 (God classes, complexity)
- Major: 8 (Duplication, magic numbers, naming)
- Minor: 12 (Inconsistencies, unused params)

### Architecture (15 findings)
- Critical: 4 (Layer violations, global state, coupling)
- Major: 7 (Missing abstractions, scattered validation)
- Minor: 4 (Bloat, inconsistent patterns)

### Dead Code (11 findings)
- Critical: 2 (Broken imports)
- Major: 4 (Orphaned files, incorrect paths)
- Minor: 4 (Unused exports)
- Info: 1 (Debug scripts)

### Error Handling (42 findings)
- Critical: 5 (Bare except, swallowed exceptions)
- Major: 12 (Missing context, silent failures)
- Minor: 18 (Inconsistent patterns)
- Info: 7 (Minor improvements)

### Test Coverage (12 findings)
- Critical: 2 (Untested 1000+ LOC screens)
- Major: 5 (Edge cases, isolation issues)
- Minor: 4 (Research, save/load gaps)
- Info: 1 (Integration opportunities)

### Documentation (47 findings)
- Critical: 8 (No docs on critical systems)
- Major: 18 (Incomplete algorithms, patterns)
- Minor: 15 (Missing docstrings)
- Info: 6 (Style improvements)

### Performance (10 findings)
- Critical: 3 (Hot path inefficiencies)
- Major: 5 (Memory churn, O(n²) algorithms)
- Minor: 2 (Unnecessary allocations)

---

## Agent Reports

| Agent | Findings | Critical | Major |
|-------|----------|----------|-------|
| [Code Quality](findings/code_quality_report.md) | 23 | 3 | 8 |
| [Architecture](findings/architecture_report.md) | 15 | 4 | 7 |
| [Dead Code](findings/dead_code_report.md) | 11 | 2 | 4 |
| [Error Handling](findings/error_handling_report.md) | 42 | 5 | 12 |
| [Test Coverage](findings/test_coverage_report.md) | 12 | 2 | 5 |
| [Documentation](findings/documentation_report.md) | 47 | 8 | 18 |
| [Performance](findings/performance_report.md) | 10 | 3 | 5 |

---

## Recommended Remediation Path

### Phase 1: Quick Wins (Week 1)
- Delete dead code and orphaned files
- Fix broken imports in app.py
- Extract image scaling utility
- Add exception handling context to bare except clauses

### Phase 2: Documentation Sprint (Week 2)
- Document EventBus, ModifierLogic, WeaponAbility formula
- Add BattleResult structure documentation
- Create module README files for major directories

### Phase 3: Architecture Improvements (Weeks 3-6)
- Introduce GameRegistries dependency injection container
- Create UI-facing DTOs for Ship, Component
- Extract ShipDesignService from workshop_screen

### Phase 4: Refactoring (Weeks 7-12)
- Break Component class into focused classes
- Apply ViewModel pattern to large UI screens
- Improve test coverage for critical paths

---

## Next Steps

1. **Create Project from Findings?** - Convert critical issues into a tracked project
2. **Discuss Specific Findings?** - Deep dive on any particular issue
3. **Archive Review?** - Save for reference

---
*Report generated: 2026-01-28 16:25*
*Review Coordinator: Code Review Coordinator*
