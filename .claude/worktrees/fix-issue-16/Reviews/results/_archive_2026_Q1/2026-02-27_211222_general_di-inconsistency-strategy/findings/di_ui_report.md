# DI UI Layer Analysis Report

**Date:** 2026-02-27
**Scope:** Dependency Injection violations in 11 UI-layer files + app.py entry point
**Analyst:** Claude Code (Opus 4.6)

---

## Summary

- **Total issues found:** 12
- **Critical:** 1
- **Major:** 5
- **Minor:** 4
- **Info:** 2

The UI layer shows a mixed DI posture. Some files (e.g., `workshop_event_router.py`, `workshop_data_loader.py`, `vehicle_class_service.py`) have been fully migrated to strict DI during PROJ-50. Others retain the "optional parameter with fallback to `get_default_registry_provider()`" anti-pattern, where the constructor accepts an optional registry but silently falls back to global state when None is passed. Two files (`planet_report_panel.py`, `empire_panel_window.py`) resolve registries inline deep within methods, with no injection path at all.

---

## Findings

### Critical

#### DI-UI-001: Inline registry resolution in `compute_planet_production()` with no injection path
**ID:** DI-UI-001
**Location:** `game/ui/panels/planet_report_panel.py:475-482`
**Issue:** The free function `compute_planet_production()` calls `get_default_registry_provider()` inline to construct a `GameRegistries` instance. There is no parameter to inject registries, making this function impossible to test with isolated data without monkey-patching the global registry.
**Impact:** This function is described as "a shared utility used by the strategy detail panel, build queue, and planets list." A utility function used by multiple callers that hard-codes global state access is the worst-case DI violation -- it forces all downstream callers to depend on global state too, regardless of whether the callers themselves support DI.
**Context:** This is NOT at a natural DI boundary. It is a standalone utility function called from multiple contexts, some of which may already have registries available.
**Recommendation:** Add an optional `registries: Optional[GameRegistries] = None` parameter. When None, fall back to global resolution (preserving backward compatibility for existing callers). Then propagate registries from callers that already have them (strategy scene, build queue panel).
**Effort:** Medium

---

### Major

#### DI-UI-002: Optional fallback pattern in `WorkshopContext.__post_init__`
**ID:** DI-UI-002
**Location:** `game/ui/screens/workshop_context.py:68-80`
**Issue:** `WorkshopContext.__post_init__()` calls `get_default_registry_provider()` when `registries` is None, constructing a full `GameRegistries` inside a dataclass `__post_init__`. While both `standalone()` and `integrated()` factory methods accept a `registries` kwarg, none of the callers in `app.py` (lines 154, 196, 648) pass it -- so the fallback always fires in production.
**Impact:** The DI parameter exists but is never used at the primary call sites, making it dead code in production. Every `WorkshopContext` creation silently hits global state. This also means tests that create `WorkshopContext` objects must either provide registries or have global state populated.
**Context:** `WorkshopContext` is a data object created at scene-transition boundaries. The DI parameter was added (PROJ-38) but `app.py` never wires it, so the fallback is the de facto path.
**Recommendation:** In `app.py` methods `start_builder()` and `_create_workshop_context()`, pass `self.registries` to the `WorkshopContext` factory methods. This makes the existing DI parameter actually used and eliminates the fallback in production.
**Effort:** Simple

#### DI-UI-003: Optional fallback pattern in `ShipFactory._get_registries()`
**ID:** DI-UI-003
**Location:** `game/ui/services/ship_factory.py:50-63`
**Issue:** `ShipFactory._get_registries()` implements a three-tier fallback: explicit parameter > stored instance > `get_default_registry_provider()`. The constructor accepts `registry_provider` as optional, and when both the stored and parameter values are None, it falls back to global state.
**Impact:** Callers that omit the registry parameter silently get global state. The fallback makes it easy to accidentally create untestable code paths. The docstring even documents this as intentional ("If None, uses get_default_registry_provider() at method call time"), normalizing the anti-pattern.
**Context:** `ShipFactory` is a service class used by battle setup, formation editor, and test lab. Some callers may already have registries available but don't pass them.
**Recommendation:** Audit all `ShipFactory()` instantiation sites. Where registries are available (e.g., from WorkshopContext or app-level), pass them explicitly. Consider making `registry_provider` required (as was done for `VehicleClassService` in PROJ-50).
**Effort:** Medium

#### DI-UI-004: Optional fallback pattern in `DesignLoaderAdapter.__init__()`
**ID:** DI-UI-004
**Location:** `game/ui/services/design_loader_adapter.py:40-49`
**Issue:** When both `design_loader` and `registry_provider` are None, the constructor calls `get_default_registry_provider()` to build a `GameRegistries` and create a `SimulationDesignLoader`. The import of `get_default_registry_provider` is at module level (line 15), making it a hard structural dependency.
**Impact:** `DesignLoaderAdapter` is imported and used from multiple UI screens. The module-level import means even importing this module creates a dependency on the global registry infrastructure. Any caller that forgets to pass `registry_provider` silently gets global state.
**Context:** This is a service adapter at the UI boundary. Module-level imports of DI-resolution functions are a stronger coupling than lazy imports inside `__init__`.
**Recommendation:** Move `get_default_registry_provider` import to inside the `__init__` fallback branch (lazy import). Better yet, make `registry_provider` required when `design_loader` is None, matching the strict DI pattern in `VehicleClassService`.
**Effort:** Simple

#### DI-UI-005: Optional fallback pattern in `ComponentService._get_provider()`
**ID:** DI-UI-005
**Location:** `game/ui/services/component_service.py:46-49`
**Issue:** `ComponentService._get_provider()` lazily resolves `get_default_registry_provider()` when `self._provider` is None, and caches it on the instance. The module-level import (line 15) hard-couples the module to global registry infrastructure.
**Impact:** Like `DesignLoaderAdapter`, this is a service with a module-level import creating structural dependency on global state. The lazy caching means the first call's global state is frozen into the instance, which can cause stale-data bugs if registries are reloaded (e.g., during data reload in the workshop).
**Context:** The docstring explicitly notes the PROJ-50 strict DI pattern was not applied here, creating inconsistency with `VehicleClassService` which does require its provider.
**Recommendation:** Make `registry_provider` required (raise if None), matching `VehicleClassService`. Move the module-level import into a lazy fallback if backward compatibility is needed. Update all callers to pass the provider explicitly.
**Effort:** Simple

#### DI-UI-006: Inline registry resolution in `EmpirePanelWindow._build_treasury_tab()`
**ID:** DI-UI-006
**Location:** `game/ui/screens/empire_panel_window.py:185-193`
**Issue:** `_build_treasury_tab()` calls `get_default_registry_provider()` inline to construct `GameRegistries` and an `EmpireEconomyCalculator`. There is no way to inject registries into `EmpirePanelWindow` -- the constructor takes only `rect`, `manager`, `empire`, and `on_close_callback`.
**Impact:** The empire panel window is opened from the strategy screen, which has a `GameSession` with full access to registries. The registries are available in the caller's context but are not passed through, forcing this method to reach into global state.
**Context:** This is a UI window deep inside the rendering hierarchy, not at a natural DI boundary. The strategy screen that opens this window already has registries available via the session object.
**Recommendation:** Add an optional `registries: Optional[GameRegistries] = None` parameter to `EmpirePanelWindow.__init__()`. Pass registries from the strategy screen when opening the panel. Fall back to global resolution if None (for backward compatibility).
**Effort:** Medium

---

### Minor

#### DI-UI-007: Fallback DI in `SchematicView.__init__()`
**ID:** DI-UI-007
**Location:** `game/ui/screens/builder/schematic_view.py:35-38`
**Issue:** When `vehicle_class_service` is None, the constructor creates a `VehicleClassService` using `get_default_registry_provider()`. The import is lazy (inside the `if` block), which is better than module-level, but the fallback still silently resolves to global state.
**Impact:** Low. `SchematicView` is a leaf UI component deep in the rendering tree. Its primary caller (`DesignWorkshopScreen`) likely already has a `VehicleClassService` instance it could pass. The lazy import mitigates the structural coupling.
**Context:** This is a rendering-only component at the UI boundary. The fallback is reasonable for backward compatibility but represents a missed opportunity to propagate DI from the parent screen.
**Recommendation:** Ensure the parent `DesignWorkshopScreen` passes its `VehicleClassService` instance. Consider making the parameter required if all call sites can provide it.
**Effort:** Simple

#### DI-UI-008: Fallback DI in `BuilderRightPanel.__init__()`
**ID:** DI-UI-008
**Location:** `game/ui/screens/builder/right_panel.py:30-33`
**Issue:** Same pattern as DI-UI-007: optional `vehicle_class_service` with lazy fallback to `get_default_registry_provider()`.
**Impact:** Low. Same mitigation as `SchematicView` -- lazy import, leaf component. The parent screen should be passing the service.
**Context:** UI boundary component. The fallback is a safety net that should rarely fire if the parent properly injects.
**Recommendation:** Same as DI-UI-007 -- propagate from parent screen, consider making required.
**Effort:** Simple

#### DI-UI-009: `StrategyMetadataService.instance()` singleton access in `BuilderRightPanel`
**ID:** DI-UI-009
**Location:** `game/ui/screens/builder/right_panel.py:116,208`
**Issue:** `BuilderRightPanel` accesses `StrategyMetadataService.instance()` directly (singleton pattern) to populate the AI strategy dropdown. This is a different form of global state access -- not through `get_default_registry_provider()` but through another singleton.
**Impact:** Low. `StrategyMetadataService` is a metadata service that is populated once at startup and rarely changes. The singleton pattern is acceptable for read-only metadata services, but it does prevent testing with isolated strategy data.
**Context:** This is at the UI boundary and the service is read-only metadata. Less concerning than mutable registry access.
**Recommendation:** No immediate action needed. If `StrategyMetadataService` is ever refactored to support DI, this should be updated. For now, the singleton pattern for read-only metadata is acceptable.
**Effort:** Simple (if addressed)

#### DI-UI-010: `StrategyMetadataService.instance()` singleton access in `WorkshopEventRouter`
**ID:** DI-UI-010
**Location:** `game/ui/screens/workshop_event_router.py:404`
**Issue:** `_handle_ai_dropdown()` accesses `StrategyMetadataService.instance()` to look up strategy IDs. Same pattern as DI-UI-009.
**Impact:** Low. Same assessment as DI-UI-009 -- read-only metadata singleton at UI boundary.
**Context:** UI event handler, leaf code.
**Recommendation:** Same as DI-UI-009. No immediate action needed.
**Effort:** Simple (if addressed)

---

### Info

#### DI-UI-011: `app.py` creates `GameRegistries` from `RegistryManager` (legitimate entry point)
**ID:** DI-UI-011
**Location:** `game/app.py:130-136`
**Issue:** `Game.__init__()` creates a `GameRegistries` instance from `RegistryManager.instance()` and stores it as `self.registries`. This is the composition root where DI should originate.
**Impact:** None -- this is correct. The issue is that `self.registries` is created but not consistently passed to downstream consumers (see DI-UI-002, DI-UI-003).
**Context:** Legitimate composition root usage. `app.py` is the top-level entry point where global state resolution is expected.
**Recommendation:** Use `self.registries` more aggressively when creating `WorkshopContext`, `ShipFactory`, `DesignLoaderAdapter`, etc. This is the source of truth that should flow downward.
**Effort:** N/A (informational)

#### DI-UI-012: `VehicleClassService` enforces strict DI (good pattern)
**ID:** DI-UI-012
**Location:** `game/ui/services/vehicle_class_service.py:38-53`
**Issue:** `VehicleClassService.__init__()` requires `registry_provider` (raises `ValidationException` if None). This is the gold standard pattern from PROJ-50.
**Impact:** Positive. Forces all callers to explicitly provide the dependency. No silent fallback to global state.
**Context:** This is the reference implementation for how all UI services should handle DI.
**Recommendation:** Use this as the template for migrating `ComponentService`, `ShipFactory`, and `DesignLoaderAdapter` to strict DI.
**Effort:** N/A (informational -- already correct)

---

## Top 5 Priority Issues

1. **DI-UI-001** (Critical) -- `compute_planet_production()` has zero injection path. As a shared utility called from multiple places, this is the highest-impact violation. Adding a registries parameter is straightforward and unblocks DI for all callers.

2. **DI-UI-002** (Major) -- `WorkshopContext.__post_init__` fallback is the most wasteful violation because the DI infrastructure already exists (the `registries` parameter) but `app.py` never uses it. This is a one-line fix at each call site.

3. **DI-UI-006** (Major) -- `EmpirePanelWindow._build_treasury_tab()` inline resolution is problematic because the caller (strategy screen) has registries available but cannot pass them through. Adding a constructor parameter is a clean fix.

4. **DI-UI-005** (Major) -- `ComponentService` lazy fallback with module-level import and instance caching creates the risk of stale data after registry reloads. Making the provider required (matching `VehicleClassService`) is simple.

5. **DI-UI-004** (Major) -- `DesignLoaderAdapter` module-level import of `get_default_registry_provider` creates unnecessary structural coupling. Moving to strict DI or at minimum lazy import would improve testability.

---

## Architectural Observations

### What's Working Well
- **`VehicleClassService`** (DI-UI-012) is the gold standard: constructor requires the provider, raises on None. PROJ-50 got this right.
- **`WorkshopDataLoader`** has strict DI (`registries` is required in constructor, marked in PROJ-50). Good pattern.
- **`WorkshopEventRouter`** accesses registries via `self.gui.context.registries`, properly delegating to the context object. Clean DI chain.

### Systemic Pattern
The most common anti-pattern is: **"Optional parameter with fallback to `get_default_registry_provider()`"**. This was the intermediate step between PROJ-38 (add DI parameters) and PROJ-50 (make them required). Several files were updated in PROJ-38 but not fully migrated in PROJ-50:
- `ShipFactory` -- optional with 3-tier fallback
- `DesignLoaderAdapter` -- optional with fallback
- `ComponentService` -- optional with lazy caching fallback
- `WorkshopContext` -- optional with `__post_init__` fallback

### Recommended Migration Order
1. **Quick wins (Simple effort):** DI-UI-002, DI-UI-004, DI-UI-005 -- these can be fixed by wiring existing registries or making parameters required.
2. **Medium wins:** DI-UI-001, DI-UI-003, DI-UI-006 -- require adding parameters and updating callers.
3. **Low priority:** DI-UI-007, DI-UI-008 -- fallbacks in leaf UI components that rarely fire if parents inject correctly.
4. **No action needed:** DI-UI-009, DI-UI-010 -- read-only singleton access is acceptable at UI boundary. DI-UI-011, DI-UI-012 -- already correct.
