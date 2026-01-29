# Phase 5: Registry Access Audit

**Date:** 2026-01-28
**Status:** Complete

## Overview

This document catalogs all usages of deprecated registry utility functions:
- `get_component_registry()`
- `get_modifier_registry()`
- `get_vehicle_classes()`
- `get_validator()`
- `get_resource_registry()`

**Replacement Pattern:**
```python
# Old (deprecated)
from game.core.registry import get_component_registry
components = get_component_registry()

# New (recommended)
from game.core.registry import get_default_registry_provider
provider = get_default_registry_provider()
components = provider.get_components()
```

---

## Summary Statistics

| Function | Game Code | Test Code | Total |
|----------|-----------|-----------|-------|
| `get_component_registry` | 14 | 68 | 82 |
| `get_modifier_registry` | 17 | 25 | 42 |
| `get_vehicle_classes` | 26 | 33 | 59 |
| `get_validator` | 2 | 0 | 2 |
| `get_resource_registry` | 4 | 0 | 4 |
| **Total** | **63** | **126** | **189** |

---

## 1. get_component_registry Usage

### Game Code (14 occurrences)

| File | Lines | Context |
|------|-------|---------|
| `game/simulation/battle_state.py` | 20, 250 | Import + usage in `_get_component_def()` |
| `game/simulation/components/component.py` | 64, 74, 744, 750, 765, 864, 877 | Import + module-level constant + multiple functions |
| `game/simulation/entities/ship_serialization.py` | 11, 179 | Import + usage in deserialization |
| `game/strategy/services/ship_stats_service.py` | 20, 80, 471 | Import + fallback usage |
| `game/simulation/services/vehicle_design_service.py` | 15 | Import only (not used directly) |
| `game/simulation/entities/ship.py` | 10 | Import only (not used directly) |
| `game/strategy/engine/resource_management_engine.py` | 17, 117 | Import + usage in consumption |
| `game/core/registry.py` | 6-7, 33, 52, 143, 145, 298, 308 | Definition + docstrings |

### Test Code (68 occurrences)

| File | Count | Context |
|------|-------|---------|
| `tests/unit/strategy/test_ship_stats_service.py` | 47 | All patching `get_component_registry` |
| `tests/strategy/test_turn_engine_strategy.py` | 7 | Patching resource_management_engine |
| `tests/unit/strategy/test_resource_management_engine.py` | 9 | Patching registry |
| `tests/unit/combat/test_battle_state_di.py` | 3 | Patching battle_state |
| `tests/unit/core/test_registry.py` | 3 | Testing utility function |
| `tests/unit/core/test_registry_deprecation.py` | 3 | Testing deprecation warning |
| `tests/unit/core/test_pure_loaders.py` | 2 | Testing loader functions |
| `tests/unit/strategy/conftest.py` | 2 | Fixture setup |
| `tests/regression/test_modifier_ability_snapshots.py` | 1 | Import |
| `tests/integration/test_resource_system.py` | 1 | Import |
| `tests/repro_issues/test_bug_13_clear_removes_hull.py` | 1 | Patching |

---

## 2. get_modifier_registry Usage

### Game Code (17 occurrences)

| File | Lines | Context |
|------|-------|---------|
| `game/simulation/components/component.py` | 64, 75, 88, 155, 417, 824, 830, 843 | Import + module-level + functions |
| `game/simulation/battle_state.py` | 20, 251 | Import + usage in `_get_modifier_def()` |
| `game/simulation/entities/ship_serialization.py` | 11, 180 | Import + deserialization |
| `game/simulation/entities/ship.py` | 10 | Import only |
| `game/simulation/services/modifier_service.py` | 9, 52, 98, 279, 387 | Import + multiple fallback usages |
| `game/strategy/services/ship_stats_service.py` | 20, 81, 163 | Import + fallback usage |
| `game/ui/panels/builder_widgets.py` | 10, 63 | Import + usage in ModifierListWidget |
| `game/ui/services/component_service.py` | 31, 58, 76 | Method definition + usage |
| `game/ui/screens/builder/legacy_components.py` | 89 | Via component_service |
| `game/core/registry.py` | 33, 53, 143, 146, 314, 321 | Definition + docstrings |

### Test Code (25 occurrences)

| File | Count | Context |
|------|-------|---------|
| `tests/unit/strategy/test_ship_stats_service.py` | 5 | Patching |
| `tests/unit/refactor/test_multi_ability_effects.py` | 10 | Direct usage in tests |
| `tests/unit/refactor/test_modifier_loader_v2.py` | 1 | Direct usage |
| `tests/unit/refactor/test_formula_validation.py` | 1 | Direct usage |
| `tests/unit/combat/test_battle_state_di.py` | 3 | Patching |
| `tests/unit/core/test_registry.py` | 2 | Testing utility function |
| `tests/unit/core/test_registry_deprecation.py` | 1 | Testing deprecation |
| `tests/unit/core/test_pure_loaders.py` | 2 | Testing loaders |
| `tests/regression/test_modifier_ability_snapshots.py` | 1 | Import |
| `tests/unit/repro_issues/test_slider_increment.py` | 1 | Mock setup |
| `tests/unit/ui/services/test_component_service.py` | 2 | Testing service method |

---

## 3. get_vehicle_classes Usage

### Game Code (26 occurrences)

| File | Lines | Context |
|------|-------|---------|
| `game/simulation/entities/ship.py` | 10, 26, 54, 80, 363, 435, 452, 589, 617 | Import + module-level + Ship class methods |
| `game/simulation/entities/ship_stats.py` | 47-48 | Import + usage in calculator creation |
| `game/simulation/entities/ship_loader.py` | 10, 112 | Import + usage in loader |
| `game/simulation/entities/ship_component_manager.py` | 19, 66 | Import + usage |
| `game/simulation/ship_validator.py` | 12, 265 | Import + usage |
| `game/simulation/services/vehicle_design_service.py` | 15, 88, 92, 129, 351 | Import + helper method + usages |
| `game/strategy/services/ship_stats_service.py` | 20, 82, 158-162 | Import + fallback usage |
| `game/ui/screens/workshop_screen.py` | 17, 158, 162, 403, 626, 644 | Import + helper method + usages |
| `game/ui/screens/workshop_event_router.py` | 18, 39, 43, 397 | Import + helper method + usage |
| `game/ui/screens/workshop_data_loader.py` | 13, 209 | Import + usage |
| `game/ui/services/vehicle_class_service.py` | 58 | Via provider (correct pattern!) |
| `game/core/registry.py` | 54, 147, 327, 334, 427, 474 | Definition + protocol methods |
| `game/core/protocols.py` | 71 | Protocol definition |

### Test Code (33 occurrences)

| File | Count | Context |
|------|-------|---------|
| `tests/unit/ui/services/test_vehicle_class_service.py` | 16 | Testing via provider mock |
| `tests/unit/core/test_registry_provider.py` | 9 | Protocol testing |
| `tests/unit/core/test_registry.py` | 3 | Testing utility function |
| `tests/unit/core/test_pure_loaders.py` | 1 | Testing loaders |
| `tests/unit/core/test_registry_deprecation.py` | 1 | Testing deprecation |
| `tests/unit/builder/test_ship_validator_di.py` | 3 | Patching |
| `tests/unit/combat/test_multitarget.py` | 2 | Direct usage |
| `tests/repro_issues/test_bug_13_clear_removes_hull.py` | 2 | Patching |
| `tests/infrastructure/session_cache.py` | 1 | Protocol implementation |

---

## 4. get_validator Usage

### Game Code (2 occurrences)

| File | Lines | Context |
|------|-------|---------|
| `game/simulation/entities/ship_loader.py` | 10, 17 | Import + usage |
| `game/ui/services/validation_service.py` | 42, 59, 71 | Helper method (uses provider) |
| `game/core/registry.py` | 55, 276, 340, 347, 351 | Definition |

### Test Code (0 occurrences)
None found - tests use DI or mock the ValidationService.

---

## 5. get_resource_registry Usage

### Game Code (4 occurrences)

| File | Lines | Context |
|------|-------|---------|
| `game/core/resources.py` | 8, 92 | Import + usage in `get_resource_display_name()` |
| `game/simulation/components/abilities/resources.py` | 45, 68, 87, 102 | Helper method + usages |
| `game/core/registry.py` | 56, 353, 360 | Definition |

### Test Code (0 occurrences)
None found directly calling the deprecated function.

---

## Prioritized Migration Plan

### Priority 1: High-Impact Game Code (Tasks 5.2-5.4)

Files with multiple direct calls that affect core gameplay:

1. **`game/simulation/components/component.py`** - 8 calls
   - Module-level constants: `COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`
   - Multiple functions using deprecated calls

2. **`game/simulation/entities/ship.py`** - 9 calls
   - Module-level constant: `VEHICLE_CLASSES`
   - Ship class methods

3. **`game/simulation/services/modifier_service.py`** - 5 calls
   - Fallback pattern in multiple methods

4. **`game/strategy/services/ship_stats_service.py`** - 6 calls
   - Fallback pattern usage

5. **`game/ui/screens/workshop_screen.py`** - 6 calls
   - Via helper method (already has abstraction layer)

### Priority 2: Supporting Game Code

Files with 1-2 calls:
- `game/simulation/battle_state.py`
- `game/simulation/entities/ship_serialization.py`
- `game/simulation/entities/ship_loader.py`
- `game/strategy/engine/resource_management_engine.py`
- `game/ui/panels/builder_widgets.py`
- `game/core/resources.py`

### Priority 3: Test Code (Task 5.5)

Most test code uses patching (`patch('module.get_component_registry')`), which:
- Works correctly with current code
- Will need updating when deprecated functions are removed
- Can be migrated to use mock providers instead

---

## Recommendations

1. **Module-Level Constants**: The pattern of `COMPONENT_REGISTRY = get_component_registry()` should be removed. Use lazy initialization or dependency injection instead.

2. **Helper Methods**: Several files already have helper methods like `_get_vehicle_classes()` that wrap the deprecated call. These are good migration points - just update the helper to use the provider.

3. **Fallback Patterns**: Many usages follow the pattern:
   ```python
   if reg is not None and hasattr(reg, 'get_components'):
       components = reg.get_components()
   else:
       components = get_component_registry()
   ```
   These can be simplified to always use `get_default_registry_provider()`.

4. **Test Code Strategy**: For tests that patch the deprecated functions, consider:
   - Using `TestRegistryProvider` for unit tests
   - Updating patches to point to provider methods
   - Or leaving patches until deprecated functions are removed (then bulk update)

---

## 6. Singleton .instance() Usage Audit (Task 5.6)

**Total occurrences:** 71 in game code (30 files), 329 in test code (102 files)

### Game Code Singletons (71 occurrences in 30 files)

| Singleton Class | Files Using | Acceptable | Notes |
|-----------------|-------------|------------|-------|
| `RegistryManager.instance()` | 14 in registry.py + various | Yes | Central registry - singleton appropriate |
| `AssetManager.instance()` | 3 in asset_manager.py | Yes | Global asset cache |
| `StrategyManager.instance()` | 4 in strategy_manager.py | Yes | AI strategy coordination |
| `Profiler.instance()` | 5 in profiling.py | Yes | Performance profiling |
| `ScreenshotManager.instance()` | 2 in screenshot_manager.py | Yes | Screenshot handling |
| `ShipThemeManager.instance()` | 2 in ship_theme_manager.py | Yes | Theme asset management |
| `SpriteManager.instance()` | 2 in sprites.py | Yes | Sprite caching |
| UI Manager singletons | ~30 in UI screens | Mixed | Some could use DI |

### Categories

1. **Acceptable Singletons** (keep as-is):
   - `RegistryManager` - Central data registry, singleton appropriate
   - `AssetManager` - Resource caching, singleton appropriate
   - `Profiler` - Cross-cutting concern, singleton appropriate
   - `ScreenshotManager` - Utility, singleton appropriate

2. **Consider for DI Migration** (future work):
   - UI component services accessing singletons directly
   - Could be injected via constructor for better testability

3. **Already Addressed**:
   - `get_component_registry()` → `get_default_registry_provider()` ✓
   - `get_modifier_registry()` → `get_default_registry_provider()` ✓
   - `get_vehicle_classes()` → `get_default_registry_provider()` ✓

### Recommendation

The existing `.instance()` usages are mostly appropriate singleton patterns:
- Central managers (Registry, Assets, Profiler)
- UI service coordination
- No immediate action required for Phase 5

Future phases could migrate UI code to use DI for better testability, but this is not blocking for the current architecture remediation.
