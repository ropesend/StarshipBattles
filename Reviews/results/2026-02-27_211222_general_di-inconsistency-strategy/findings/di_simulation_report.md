# DI Simulation Layer Analysis Report

**Date:** 2026-02-27
**Scope:** Simulation layer DI violations via `get_default_registry_provider()` usage
**Files Analyzed:**
- `game/simulation/entities/ship_loader.py`
- `game/simulation/entities/ship_stats.py`
- `game/simulation/components/component.py`
- `game/core/registry.py` (context)
- `game/core/__init__.py` (context)

---

## Summary

- **Total issues found:** 9
- **Critical:** 1, **Major:** 5, **Minor:** 1, **Info:** 2

The simulation layer shows a mixed DI maturity picture. The `Component` class itself has been successfully migrated to strict DI (PROJ-50), requiring `registries` in its constructor. However, the module-level loader functions (`load_components`, `load_modifiers`) and `ship_loader.py` functions still use `get_default_registry_provider()` as implicit fallbacks or direct calls, creating hidden coupling to the global singleton. The `ship_stats.py` module docstring actively teaches the anti-pattern as example usage.

---

## Findings

#### MAJOR: `get_or_create_validator()` falls back to global provider
**ID:** DI-SIM-001
**Location:** `game/simulation/entities/ship_loader.py:20-47`
**Issue:** `get_or_create_validator()` accepts an optional `registry_provider` parameter but falls back to `get_default_registry_provider()` on line 37 when `None` is passed. This function is called from 6+ locations across the codebase (Ship.add_component, ShipValidatorHelper, VehicleDesignService, ValidationService), and NONE of them pass a `registry_provider` argument -- they all rely on the implicit fallback.
**Impact:** Every caller silently depends on global state. Testing requires the global singleton to be configured. The optional parameter creates the illusion of DI support without actually being used anywhere.
**Call Chain:**
- `Ship.add_component()` -> `get_or_create_validator()` (no provider passed)
- `ShipValidatorHelper.check_validity()` -> `get_or_create_validator()` (no provider passed)
- `VehicleDesignService._validate_*()` -> `get_or_create_validator()` (no provider passed)
- `ValidationService.__init__()` -> `get_or_create_validator()` (no provider passed)
- All callers have access to `_registries` (Ship has it, VDS receives it) and could pass it
**Recommendation:** Make `registry_provider` required. All callers already have registries available:
- `Ship` has `self._registries` which contains vehicle_classes, components, modifiers
- `VehicleDesignService` stores `self._registries`
- `ShipValidatorHelper` has `self._ship._registries`
- Alternatively, inject the validator itself rather than the provider
**Effort:** Medium (6+ call sites need updating, but all have registries available)

---

#### MAJOR: `load_vehicle_classes()` falls back to global provider
**ID:** DI-SIM-002
**Location:** `game/simulation/entities/ship_loader.py:117-158`
**Issue:** `load_vehicle_classes()` accepts optional `registry_provider` parameter (line 120) and falls back to `get_default_registry_provider()` on line 153 when `None`. This function mutates the global registry directly (clears and updates vehicle_classes dict from the provider).
**Impact:** The function's purpose is explicitly to "populate the global registry" (line 123-124), so global access is somewhat expected for this composition-root-like function. However, callers like `workshop_data_loader.py` and `registry_loader.py` never pass a provider, making it untestable in isolation.
**Call Chain:**
- `app.py` -> `initialize_ship_data()` -> `load_vehicle_classes()` (composition root - acceptable)
- `registry_loader.py` -> `load_vehicle_classes(path)` (no provider)
- `workshop_data_loader.py` -> `load_vehicle_classes(path)` (no provider)
**Recommendation:** For the composition root path (`app.py` -> `initialize_ship_data`), this is close to acceptable. However, `registry_loader.py` and `workshop_data_loader.py` should pass the provider explicitly. Consider whether `initialize_ship_data()` should accept and forward a `registry_provider` parameter.
**Effort:** Simple (2 call sites in non-root paths)

---

#### MAJOR: `load_components_data()` falls back to global provider
**ID:** DI-SIM-003
**Location:** `game/simulation/components/component.py:483-555`
**Issue:** `load_components_data()` accepts optional `registries` parameter (line 486) but falls back to constructing registries from `get_default_registry_provider()` on lines 514-520 when `None`. This is a "pure function" (per its docstring) that should not access global state.
**Impact:** The docstring claims this is a "pure function" but it violates that claim by accessing the global singleton. This is misleading to developers. The function is called from `load_components()` which does pass registries explicitly (line 585), so the fallback may be dead code -- but its presence teaches the anti-pattern and could mask bugs if the caller forgets to pass registries.
**Call Chain:**
- `load_components()` -> `load_components_data(file_path, registries=registries)` (registries passed - good)
- No other callers found in production code (fallback may be dead code)
**Recommendation:** Make `registries` required (remove `Optional`, remove `= None`). If no caller uses the fallback, removing it is safe and makes the "pure function" claim truthful.
**Effort:** Simple (verify no callers use default, then remove fallback)

---

#### MAJOR: `load_components()` uses global provider directly (no parameter)
**ID:** DI-SIM-004
**Location:** `game/simulation/components/component.py:558-596`
**Issue:** `load_components()` does NOT accept a `registry_provider` or `registries` parameter at all. It calls `get_default_registry_provider()` directly on line 569 (and constructs `GameRegistries` from it on lines 579-584). This is a wrapper function that populates the global registry.
**Impact:** This function is a composition-root-style loader, so global access is somewhat expected. However, it is called from non-root contexts: `registry_loader.py:102` and `workshop_data_loader.py:138`. These callers have no way to control which registry is populated, making the function completely untestable in isolation.
**Call Chain:**
- `app.py:116` -> `load_components(Paths.COMPONENTS_FILE)` (composition root - acceptable)
- `registry_loader.py:102` -> `load_components(str(comp_path))` (not a composition root)
- `workshop_data_loader.py:138` -> `load_components(comp_path)` (not a composition root)
**Recommendation:** Add optional `registry_provider` parameter with fallback (matching `load_vehicle_classes` pattern as an intermediate step), then migrate callers to pass it explicitly.
**Effort:** Medium (add parameter, update 2 non-root callers)

---

#### MAJOR: `load_modifiers()` uses global provider directly (no parameter)
**ID:** DI-SIM-005
**Location:** `game/simulation/components/component.py:657-685`
**Issue:** `load_modifiers()` does NOT accept a `registry_provider` or `registries` parameter. It calls `get_default_registry_provider().get_modifiers()` directly on line 668. Like `load_components()`, this is a registry-population function with no DI escape hatch.
**Impact:** Same as DI-SIM-004. Called from `app.py` (composition root, acceptable), `registry_loader.py:93`, and `workshop_data_loader.py:129` (not composition roots). These callers cannot control which registry is populated.
**Call Chain:**
- `app.py:117` -> `load_modifiers(Paths.MODIFIERS_FILE)` (composition root)
- `registry_loader.py:93` -> `load_modifiers(str(mod_path))` (not composition root)
- `workshop_data_loader.py:129` -> `load_modifiers(mod_path)` (not composition root)
**Recommendation:** Add optional `registry_provider` parameter (matching `load_vehicle_classes` pattern), then migrate callers.
**Effort:** Medium (add parameter, update 2 non-root callers)

---

#### CRITICAL: `initialize_ship_data()` has no DI parameters and no registry forwarding
**ID:** DI-SIM-006
**Location:** `game/simulation/entities/ship_loader.py:161-167`
**Issue:** `initialize_ship_data()` accepts only `base_path` and has no `registry_provider` parameter. It calls `load_vehicle_classes()` without forwarding any registry context. This is the top-level facade used by `app.py` and by **13+ test fixtures and test classes** to initialize the simulation layer. None of these can control which registries are populated.
**Impact:** This is the most widely-called initialization function in the codebase (found in `conftest.py`, 10+ test files, `app.py`). Its lack of DI parameters forces ALL callers to depend on the global singleton. Test fixtures that call this must ensure the global `RegistryManager` is configured first, creating fragile implicit dependencies.
**Call Chain:**
- `app.py:124` -> `initialize_ship_data(Paths.ROOT_DIR)` (composition root - acceptable)
- `conftest.py:55` -> `initialize_ship_data(str(get_project_root()))` (test root - tolerable but not ideal)
- `tests/fixtures/common.py:29,41` -> same pattern
- `13+ individual test files` -> same pattern
**Recommendation:** Add `registry_provider=None` parameter and forward it to `load_vehicle_classes()`. For the composition root (`app.py`), the fallback is acceptable. For tests, this enables using `TestRegistryProvider` instead of the global singleton, improving test isolation.
**Effort:** Simple (add parameter, forward to `load_vehicle_classes`)

---

#### MINOR: `ship_stats.py` module docstring teaches anti-pattern
**ID:** DI-SIM-007
**Location:** `game/simulation/entities/ship_stats.py:47-49`
**Issue:** The module docstring's Example section shows:
```python
from game.core.registry import get_default_registry_provider
calculator = ShipStatsCalculator(get_default_registry_provider().get_vehicle_classes())
```
This teaches developers to use the global provider directly instead of receiving registries via DI. The `ShipStatsCalculator` class itself is well-designed (it accepts `vehicle_classes` as a constructor parameter and has no global state access), but the documentation undermines this.
**Impact:** New developers reading this module will copy the anti-pattern. The example should show proper DI usage.
**Call Chain:** N/A (documentation only)
**Recommendation:** Update the docstring example to show proper DI usage:
```python
# Receives vehicle_classes via DI (constructor parameter)
calculator = ShipStatsCalculator(registries.vehicle_classes)
calculator.calculate(ship)
```
**Effort:** Simple (docstring edit only)

---

#### INFO: `get_default_registry_provider()` definition site
**ID:** DI-SIM-008
**Location:** `game/core/registry.py:364-378`
**Issue:** This is the definition of `get_default_registry_provider()`. It is a singleton factory for `DefaultRegistryProvider` which itself delegates to `RegistryManager.instance()`. This is the legitimate definition site -- the function exists to serve as a bridge between the old singleton pattern and the newer DI pattern.
**Impact:** The function itself is correctly implemented. The issue is its overuse in non-composition-root code throughout the simulation layer.
**Call Chain:** N/A (definition site)
**Recommendation:** No changes to the definition. Focus on reducing callers in the simulation layer. Long-term, this function should only be called from true composition roots (`app.py`, test conftest).
**Effort:** N/A

---

#### INFO: `game/core/__init__.py` re-exports `get_default_registry_provider`
**ID:** DI-SIM-009
**Location:** `game/core/__init__.py:73`
**Issue:** `get_default_registry_provider` is re-exported from the `game.core` package. This is legitimate -- it makes the DI factory accessible from the top-level core package.
**Impact:** The re-export itself is fine. It does make it slightly easier for code to call the global provider (shorter import path), but this is standard Python package design.
**Call Chain:** N/A (re-export)
**Recommendation:** No change needed.
**Effort:** N/A

---

## Top 5 Priority Issues

| Rank | ID | Severity | Title | Effort | Rationale |
|------|----|----------|-------|--------|-----------|
| 1 | DI-SIM-006 | Critical | `initialize_ship_data()` has no DI parameters | Simple | Highest call count (13+ test files + app.py). Adding a parameter is trivial and unblocks test isolation improvements. |
| 2 | DI-SIM-001 | Major | `get_or_create_validator()` implicit fallback | Medium | Called from 6+ locations that ALL have registries available. The optional-with-fallback pattern creates false confidence in DI support. |
| 3 | DI-SIM-003 | Major | `load_components_data()` "pure function" with global fallback | Simple | The fallback may be dead code. Removing it makes the pure function claim truthful and prevents future misuse. |
| 4 | DI-SIM-004 | Major | `load_components()` has no DI parameter | Medium | Used by non-root callers (`registry_loader`, `workshop_data_loader`) who cannot control behavior. |
| 5 | DI-SIM-005 | Major | `load_modifiers()` has no DI parameter | Medium | Same issue as DI-SIM-004; both loader functions should be addressed together. |

---

## Remediation Strategy

### Phase 1: Quick Wins (Simple effort, high impact)
1. **DI-SIM-007**: Update `ship_stats.py` docstring to show proper DI usage
2. **DI-SIM-003**: Make `registries` required in `load_components_data()` (verify no caller uses default first)
3. **DI-SIM-006**: Add `registry_provider` parameter to `initialize_ship_data()` and forward to `load_vehicle_classes()`

### Phase 2: Loader Functions (Medium effort)
4. **DI-SIM-004**: Add `registry_provider` parameter to `load_components()`
5. **DI-SIM-005**: Add `registry_provider` parameter to `load_modifiers()`
6. **DI-SIM-002**: Update non-root callers of `load_vehicle_classes()` to pass provider

### Phase 3: Validator DI (Medium effort, most callers to update)
7. **DI-SIM-001**: Make `registry_provider` required in `get_or_create_validator()` or inject the validator itself into callers

### Design Principle
The `Component` class (PROJ-50) demonstrates the target pattern: `registries` is a **required keyword argument** in the constructor, with a `ValidationException` raised if `None`. All simulation-layer functions should converge toward this pattern: required DI parameters at the function boundary, with `get_default_registry_provider()` usage confined to true composition roots (`app.py`, test `conftest.py`).
