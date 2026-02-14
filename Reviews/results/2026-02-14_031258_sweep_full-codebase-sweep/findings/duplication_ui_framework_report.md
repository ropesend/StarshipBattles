# Duplication & Fragmentation Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 27
- **Total Issues Found:** 8
- **Critical:** 0 | **Major:** 3 | **Minor:** 4 | **Info:** 1

## Findings

#### MAJOR: Registry Provider Access Pattern Duplication
**ID:** DUP-UI2-010
**Location:** `game/ui/services/component_service.py:46-50` AND `game/ui/services/vehicle_class_service.py:50-52` AND `game/ui/services/validation_service.py:45-49`
**Issue:** Three service classes implement nearly identical `_get_provider()` / `_get_validator()` methods for lazy resolution of injected dependencies:

```python
# ComponentService pattern (with lazy fallback)
def _get_provider(self) -> IRegistryProvider:
    if self._provider is None:
        self._provider = get_default_registry_provider()
    return self._provider

# VehicleClassService pattern (strict DI, no fallback)
def _get_provider(self) -> IRegistryProvider:
    return self._provider

# ValidationService pattern (with lazy fallback)
def _get_validator(self) -> Any:
    if self._validator is None:
        self._validator = get_or_create_validator()
    return self._validator
```

**Impact:** While not exact duplicates, this represents the same pattern with inconsistent implementation (some services use strict DI via PROJ-50, others have lazy fallback). New services may copy the wrong pattern, leading to DI inconsistency.
**Recommendation:** Create a base class or mixin `LazyDIService` that standardizes this pattern, or document a clear convention and enforce it via code review.
**Effort:** Medium

---

#### MAJOR: Service Adapter Boilerplate Pattern
**ID:** DUP-UI2-011
**Location:** `game/ui/services/ship_io_adapter.py` AND `game/ui/services/design_loader_adapter.py`
**Issue:** Both adapter classes follow the exact same structural pattern:
1. Accept optional dependency in `__init__`
2. Lazy-initialize if None using a fallback factory
3. Delegate all public methods to the wrapped object

Both adapters are thin wrappers (~88-104 lines) that exist primarily to decouple the UI layer from the simulation layer. While architecturally correct, the boilerplate is duplicated.

**Impact:** Low maintenance risk since the pattern is simple, but adding new adapters requires copying and modifying boilerplate.
**Recommendation:** Consider a generic adapter factory or metaclass that generates thin wrappers from interface definitions. Alternatively, accept this as intentional simplicity - thin adapters are easy to understand.
**Effort:** Medium (if implementing generic solution) / None (if accepting as intentional)

---

#### MAJOR: Singleton Manager Pattern Duplication
**ID:** DUP-UI2-012
**Location:** `game/ui/assets/ship_theme_manager.py:11-55` AND `game/ui/renderer/sprites.py:8-26` AND `game/ui/services/screenshot_manager.py:19-46`
**Issue:** Three singleton managers share structural similarities:
- Use `SingletonMeta` metaclass
- Have `clear()` or equivalent reset methods
- Implement thread-safe initialization with locks
- Cache loaded resources in dictionaries
- Have `load_*` and `get_*` method pairs

The docstring patterns are also nearly identical:
```python
"""
Singleton manager for [X].

Thread Safety:
    - Instance creation is thread-safe via SingletonMeta

Usage:
    manager = [X]Manager.instance()
    ...

Testing:
    - Use reset() to destroy instance completely
"""
```

**Impact:** Not a bug risk, but represents boilerplate that could be centralized. When updating the singleton pattern (e.g., adding telemetry), all three must be updated.
**Recommendation:** Consider creating a `CachingAssetManager` base class that handles common patterns: thread-safe caching, reset/clear, lazy loading. Each concrete manager would only implement `_load_single_item()` and `_create_fallback()`.
**Effort:** Medium

---

#### MINOR: Battle Factory Helper Pattern
**ID:** DUP-UI2-013
**Location:** `game/ui/services/battle_factories.py:25-78`
**Issue:** The file already has extracted helpers (`_create_default_ai_factory`, `_create_controller_with_config`, `_clone_ships`) as noted in comments (PROJ-141: DUP-UI2-002, DUP-UI2-006 remediation). The current state shows good consolidation. However, the four public factory functions (`create_manual_battle`, `create_test_battle`, `create_strategy_battle`, `create_hypothetical_battle`) share 60%+ structure:
1. Create BattleConfig with mode-specific settings
2. Call `_create_controller_with_config`
3. Optionally add ships
4. Optionally start controller

**Impact:** Low - this is already well-factored. The remaining "duplication" is intentional configuration variation.
**Recommendation:** No action needed. This is an example of good DRY compliance after prior remediation.
**Effort:** None (already addressed)

---

#### MINOR: DTO Conversion Method Structure
**ID:** DUP-UI2-014
**Location:** `game/ui/services/battle_ui_service.py:141-300`
**Issue:** The `_convert_*` methods (`_convert_ship`, `_convert_component`, `_convert_projectile`, `_convert_beam`) share a common pattern:
1. Extract attributes with `getattr()` fallbacks
2. Handle optional/missing fields defensively
3. Construct immutable DTO with extracted values

Each method is distinct due to different source types, but the defensive extraction pattern is repeated (~10 `getattr(obj, 'attr', default)` calls per method).

**Impact:** Low - this is defensive coding that prevents crashes when simulation objects evolve.
**Recommendation:** No consolidation needed. The defensive extraction is appropriate for the adapter boundary.
**Effort:** None

---

#### MINOR: Image Loading Exception Handling Pattern
**ID:** DUP-UI2-015
**Location:** `game/ui/assets/ship_theme_manager.py:160-165,286-289` AND `game/ui/renderer/sprites.py:89-92`
**Issue:** Multiple image loading locations use the same exception handling pattern:
```python
except FileNotFoundError as e:
    log_error(f"... {path}: {e}")
    return self._create_fallback_image(...)
except pygame.error as e:
    log_error(f"... (pygame error): {e}")
    return self._create_fallback_image(...)
```

The exception types and handling are identical but the log messages differ.

**Impact:** Low - if pygame adds new error types, multiple locations need updating.
**Recommendation:** Consider a helper function `safe_load_image(path, fallback_factory)` that handles the try/except pattern. The `game/ui/utils.py` module would be appropriate.
**Effort:** Simple

---

#### MINOR: Empty __init__.py Files
**ID:** DUP-UI2-016
**Location:** `game/ui/renderer/__init__.py` (empty) vs `game/ui/assets/__init__.py` (exports) vs `game/ui/orchestration/__init__.py` (exports)
**Issue:** Inconsistent use of `__init__.py` files:
- `renderer/__init__.py` is empty
- `assets/__init__.py` exports `ShipThemeManager`
- `orchestration/__init__.py` exports `BattleOrchestrator`
- `services/__init__.py` has comprehensive exports
- `interfaces/__init__.py` has comprehensive exports

The renderer module relies on `game.ui.__init__.py` to import its submodules.

**Impact:** Minimal - this is a style inconsistency, not a bug.
**Recommendation:** For consistency, either all `__init__.py` files should export their public APIs, or none should. Currently it's mixed.
**Effort:** Simple

---

#### INFO: Well-Consolidated Tkinter Utilities
**ID:** DUP-UI2-017
**Location:** `game/ui/services/tkinter_utils.py`
**Issue:** This file represents a **successful consolidation** effort (noted as DUP-UI2-001 in comments). It provides:
- `get_tk_root()` - lazy singleton initialization
- `is_tkinter_available()` - availability check
- `open_save_dialog()` / `open_load_dialog()` - file dialogs
- `prompt_string()` - string input
- `copy_to_clipboard()` - clipboard operations

Other files (`ship_io.py`, `screenshot_manager.py`) now use these shared utilities instead of reimplementing Tkinter initialization.

**Impact:** Positive - demonstrates successful DRY remediation.
**Recommendation:** This is the template for future consolidation efforts. No action needed.
**Effort:** None

---

## Top 5 Priority Issues

1. **DUP-UI2-012 (MAJOR):** Singleton Manager Pattern - Three managers share significant boilerplate. A base class would reduce future maintenance burden.

2. **DUP-UI2-010 (MAJOR):** Registry Provider Access - Inconsistent DI patterns across services (some strict, some lazy). Should standardize on one approach.

3. **DUP-UI2-011 (MAJOR):** Service Adapter Boilerplate - While intentionally simple, could benefit from a generic solution for consistency.

4. **DUP-UI2-015 (MINOR):** Image Loading Exception Handling - A `safe_load_image()` utility would eliminate repeated try/except blocks.

5. **DUP-UI2-016 (MINOR):** Inconsistent `__init__.py` exports - Minor style issue that should be standardized.

---

## Notes

The UI-Framework shard (root files, services, renderer, interfaces, orchestration, assets) is well-architected with clear separation of concerns. Prior remediation efforts (DUP-UI2-001 for Tkinter, PROJ-141 for battle factories) have already addressed significant duplication.

The remaining duplication is primarily:
1. **Structural patterns** (singleton managers, service adapters) that could benefit from base classes
2. **Exception handling boilerplate** that could be extracted to utility functions
3. **Minor inconsistencies** in module initialization style

Overall code quality is high. The recommended consolidations would improve maintainability but are not blocking issues.
