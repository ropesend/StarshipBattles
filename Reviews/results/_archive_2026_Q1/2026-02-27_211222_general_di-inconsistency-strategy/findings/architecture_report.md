# Architecture Review: Dependency Injection System

**Reviewer:** Architecture Review Agent
**Date:** 2026-02-27
**Scope:** Cross-cutting assessment of `get_default_registry_provider()` usage across all production files

---

## Summary

- **Total issues found:** 16
- **Critical:** 3, **Major:** 7, **Minor:** 4, **Info:** 2

The DI system has a well-designed foundation (`IRegistryProvider` protocol, `DefaultRegistryProvider`, `TestRegistryProvider`) but suffers from inconsistent adoption. The codebase is in a transitional state: some modules use strict DI (e.g., `VehicleClassService` requires a provider), while others silently fall back to the global singleton. This creates a fragile dependency graph where objects deep in the call chain reach back to the global state instead of receiving registries from their callers.

Of the **15 production files** that actually call `get_default_registry_provider()` at runtime (excluding docstrings/comments), only **2** represent legitimate composition roots. The remaining **13** are DI violations of varying severity.

---

## DI Architecture Assessment

### How the System Works

1. **`RegistryManager`** is a singleton that holds mutable dictionaries for components, modifiers, vehicle_classes, and resources.
2. **`DefaultRegistryProvider`** is a thin adapter that delegates `.get_components()` etc. to the `RegistryManager` singleton.
3. **`get_default_registry_provider()`** is a factory that returns a cached `DefaultRegistryProvider` instance.
4. **`GameRegistries`** is a frozen dataclass that bundles references to the same dictionaries, used for passing via DI.
5. **`IRegistryProvider`** is a Protocol that both `DefaultRegistryProvider` and `TestRegistryProvider` satisfy.

The **intended pattern** is:
- Composition roots (app startup, test fixtures) resolve the provider once.
- All downstream code receives registries via constructor/parameter injection.
- Test code can substitute `TestRegistryProvider` for isolation.

The **actual pattern** in many files is:
- Constructor accepts `Optional[registries] = None`
- If None, internally calls `get_default_registry_provider()`
- This defeats testability and creates hidden global coupling.

### Legitimate Composition Roots

| File | Function/Location | Justification |
|------|-------------------|---------------|
| `game/app.py` | `Game.__init__()` lines 116-136 | Application startup. Loads data, populates RegistryManager, creates `GameRegistries`. This is THE production composition root. Does NOT call `get_default_registry_provider()` directly -- uses `RegistryManager.instance()`. |
| `conftest.py` | `reset_game_state` fixture | Test composition root. Hydrates RegistryManager. Correctly relies on `get_default_registry_provider()` being backed by hydrated RegistryManager. |

**Important note:** `app.py` itself does NOT call `get_default_registry_provider()`. It populates `RegistryManager` directly and creates a `GameRegistries` instance. The comment at line 128 references it but no call is made. This is actually correct -- the composition root sets up the data, and downstream consumers resolve it.

### Violation Map

| # | File | Location | Violation Type | Severity | Layer |
|---|------|----------|---------------|----------|-------|
| 1 | `game/simulation/components/component.py` | Line 65 (import), Lines 514, 569, 668 | Module-level import + inline resolution in `load_components_data()`, `load_components()`, `load_modifiers()` | **CRITICAL** | Simulation |
| 2 | `game/simulation/entities/ship_loader.py` | Lines 37, 153 | Service fallback in `get_or_create_validator()`, `load_vehicle_classes()` | **Major** | Simulation |
| 3 | `game/strategy/data/ship_instance.py` | Lines 257-258 | Inline resolution in `get_calculated_stats()` method | **CRITICAL** | Strategy Data |
| 4 | `game/strategy/data/fleet_capability_calculator.py` | Lines 16-17 | Helper wrapper `_get_default_component_registry()` | **CRITICAL** | Strategy Data |
| 5 | `game/strategy/engine/turn_engine.py` | Line 164 | Service fallback in `__init__()` | **Major** | Strategy Engine |
| 6 | `game/strategy/facade/strategy_session_facade.py` | Lines 493, 502 | Inline resolution in `get_fleet_remaining_pods()` | **Major** | Strategy Facade |
| 7 | `game/strategy/engine/empire_economy_calculator.py` | Lines 60-61 | Docstring only (no runtime call) | **Info** | Strategy Engine |
| 8 | `game/ui/services/component_service.py` | Line 49 | Service fallback in `_get_provider()` | **Major** | UI Service |
| 9 | `game/ui/services/ship_factory.py` | Lines 56-57 | Service fallback in `_get_registries()` | **Major** | UI Service |
| 10 | `game/ui/services/design_loader_adapter.py` | Line 42 | Service fallback in `__init__()` | **Major** | UI Service |
| 11 | `game/ui/panels/planet_report_panel.py` | Lines 475-476 | Inline resolution in module-level function | **Minor** | UI Panel |
| 12 | `game/ui/screens/empire_panel_window.py` | Lines 185-186 | Inline resolution in `_build_treasury_tab()` | **Minor** | UI Screen |
| 13 | `game/ui/screens/builder/right_panel.py` | Lines 31-33 | Service fallback in `__init__()` | **Minor** | UI Screen |
| 14 | `game/ui/screens/builder/schematic_view.py` | Lines 36-38 | Service fallback in `__init__()` | **Minor** | UI Screen |
| 15 | `game/ui/screens/workshop_context.py` | Lines 69-72 | Service fallback in `__post_init__()` | **Major** | UI Screen |
| 16 | `game/simulation/entities/ship_stats.py` | Lines 47-48 | Docstring only (no runtime call) | **Info** | Simulation |

---

## Findings

### CRITICAL: ShipInstance.get_calculated_stats() resolves registries on every call
**ID:** AR-001
**Location:** `game/strategy/data/ship_instance.py:257-258`
**Issue:** `ShipInstance` is a data object that reaches into the global DI container every time `get_calculated_stats()` is called. This method is called from at least 15 different locations across strategy services, UI screens, and engine code. A data-layer object should never resolve its own dependencies.
**Impact:** ShipInstance cannot be tested with isolated registries. Every test that creates a ShipInstance and calls `get_calculated_stats()` implicitly depends on global state being correctly populated. This is the single most impactful violation because ShipInstance is one of the most frequently used objects in the entire strategy layer.
**Ideal DI Flow:**
```
GameSession(registries) -> Empire -> Fleet -> ShipInstance
ShipInstance.get_calculated_stats(registries) -- caller passes registries
```
Or: ShipInstance stores a registries reference set at construction time (via `create()` or `from_dict()` factory methods).
**Recommendation:** Add `registries: Optional[GameRegistries] = None` to `get_calculated_stats()`. Callers that already have registries (TurnEngine, fleet services, UI panels) pass them explicitly. During transition, keep the fallback but mark it deprecated.
**Effort:** Medium (many call sites to update, but each is mechanical)

---

### CRITICAL: FleetCapabilityCalculator uses helper wrapper to hide global resolution
**ID:** AR-002
**Location:** `game/strategy/data/fleet_capability_calculator.py:14-17`
**Issue:** The module-level `_get_default_component_registry()` is a private function that wraps `get_default_registry_provider().get_components()`. This is called in `ship_has_spaceyard()`, `space_shipyard_count`, and `ship_has_ability()` -- every time a fleet capability is queried. The helper wrapper pattern is the most insidious violation because it looks like clean code but hides the global dependency behind a function name that doesn't signal "global state access."
**Impact:** Fleet capability calculations are impossible to test with custom component registries. The `FleetCapabilityCalculator` is constructed by `Fleet.__init__()` with no mechanism to pass registries.
**Ideal DI Flow:**
```
GameSession(registries) -> Empire -> Fleet(registries) -> FleetCapabilityCalculator(component_registry)
```
**Recommendation:** Accept `component_registry: Dict[str, Any]` in `FleetCapabilityCalculator.__init__()`. Fleet passes it from its own stored registries. Remove the `_get_default_component_registry()` helper entirely.
**Effort:** Medium (Fleet construction + all callers of capability methods)

---

### CRITICAL: component.py has 3 separate global resolution calls in initialization functions
**ID:** AR-003
**Location:** `game/simulation/components/component.py:514, 569, 668`
**Issue:** Three functions in this file call `get_default_registry_provider()`:
1. `load_components_data()` (line 514) - fallback when `registries=None`
2. `load_components()` (line 569) - directly resolves provider to get registry dict references
3. `load_modifiers()` (line 668) - directly resolves provider to get modifier dict references

Functions 2 and 3 are called from `app.py` during startup (composition root) and from `workshop_data_loader.py` (UI). Function 1 is a "pure function" that accepts optional registries but falls back to global.
**Impact:** The `load_components()` and `load_modifiers()` functions are explicitly **initialization functions** called at startup. They populate the singleton registries. This is actually borderline-legitimate because they ARE part of the initialization pipeline. However, they bypass the composition root pattern by resolving the provider internally rather than receiving it as a parameter.
**Ideal DI Flow:**
```
app.py creates provider -> passes to load_components(provider=provider) -> populates registry
```
**Recommendation:** Add `registry_provider` parameter to `load_components()` and `load_modifiers()`. The `app.py` composition root passes its provider. The `load_components_data()` pure function should require `registries` (no fallback).
**Effort:** Simple (2 call sites for each function)

---

### MAJOR: TurnEngine constructor falls back to global provider
**ID:** AR-004
**Location:** `game/strategy/engine/turn_engine.py:164`
**Issue:** `TurnEngine.__init__()` accepts `registries: Optional[GameRegistries] = None` and falls back to `get_default_registry_provider()` when None. It is constructed in `GameSession.__init__()` (line 85) with no registries argument: `self.turn_engine = TurnEngine()`.
**Impact:** TurnEngine is the central orchestrator for all strategy turn processing. Its registries flow to sub-engines (ConflictResolutionEngine, ResourceManagementEngine, ResupplyEngine, HarvestingEngine). If the global state is wrong, all sub-engines get wrong data.
**Ideal DI Flow:**
```
GameSession.__init__() -> TurnEngine(registries=self._registries)
```
GameSession itself should hold registries received from its creator or resolved at session creation time (which IS a composition root).
**Recommendation:** GameSession should resolve registries once and pass to TurnEngine. TurnEngine should require registries (no fallback).
**Effort:** Simple (1 call site in GameSession, 1 in from_dict)

---

### MAJOR: StrategySessionFacade.get_fleet_remaining_pods() resolves inline
**ID:** AR-005
**Location:** `game/strategy/facade/strategy_session_facade.py:493-502`
**Issue:** This facade method resolves the registry provider inline, wrapped in a broad try/except that catches RuntimeError, AttributeError, ImportError, and StateException. The defensive fallback masks bugs where registries aren't properly initialized. The facade has access to `self._session` which could provide registries.
**Impact:** The facade is supposed to be the clean boundary between UI and engine. Having it reach into global state undermines the CQRS pattern. The broad exception handling means registry problems silently produce empty results instead of failing fast.
**Ideal DI Flow:**
```
StrategySessionFacade._session -> GameSession._registries -> component_registry
```
**Recommendation:** GameSession should expose a `registries` property. Facade accesses `self._session.registries.components`.
**Effort:** Simple (1 method to update, depends on AR-004 adding registries to GameSession)

---

### MAJOR: ship_loader.py has two resolution points
**ID:** AR-006
**Location:** `game/simulation/entities/ship_loader.py:37, 153`
**Issue:** `get_or_create_validator()` (line 37) and `load_vehicle_classes()` (line 153) both fall back to `get_default_registry_provider()` when no provider is passed. These are initialization-phase functions called from `app.py` and `initialize_ship_data()`.
**Impact:** Similar to AR-003, these are initialization functions. The `get_or_create_validator()` function is also a service locator anti-pattern -- it checks if a validator exists on the singleton, creates one if not, and stores it back. This combines resolution, creation, and storage in one function.
**Ideal DI Flow:**
```
app.py -> initialize_ship_data(registry_provider=provider)
  -> load_vehicle_classes(registry_provider=provider)
  -> get_or_create_validator(registry_provider=provider)
```
**Recommendation:** Pass `registry_provider` from all call sites. Already has the parameter -- just need callers to use it.
**Effort:** Simple (update callers in app.py and initialize_ship_data)

---

### MAJOR: ComponentService uses lazy fallback pattern
**ID:** AR-007
**Location:** `game/ui/services/component_service.py:49`
**Issue:** `ComponentService.__init__()` accepts `Optional[IRegistryProvider] = None` and lazily resolves in `_get_provider()`. Contrast this with `VehicleClassService` which requires the provider (strict DI, raises `ValidationException` if None).
**Impact:** Inconsistency within the same service layer. Some services are strict, some are lazy. This makes it unclear what the expected pattern is for new code.
**Ideal DI Flow:**
```
UI Screen creates ComponentService(provider) where provider comes from screen's context
```
**Recommendation:** Make `registry_provider` required (matching `VehicleClassService` pattern). Update all callers to pass provider explicitly.
**Effort:** Simple (few callers)

---

### MAJOR: ShipFactory uses triple-fallback resolution
**ID:** AR-008
**Location:** `game/ui/services/ship_factory.py:56-57`
**Issue:** `ShipFactory._get_registries()` has a three-level fallback: method parameter > stored instance > global default. The stored instance is set via constructor's `registry_provider` parameter. This triple-fallback makes it hard to reason about which registries are actually in use.
**Impact:** In testing, you must be careful to either inject at construction OR at every method call. Forgetting either level silently falls back to global.
**Ideal DI Flow:**
```
WorkshopContext(registries) -> ShipFactory(registries) -- no fallback needed
```
**Recommendation:** Require registries in constructor. Remove method-level override and global fallback.
**Effort:** Simple (update callers to pass registries)

---

### MAJOR: DesignLoaderAdapter falls back in constructor
**ID:** AR-009
**Location:** `game/ui/services/design_loader_adapter.py:42`
**Issue:** When both `design_loader` and `registry_provider` are None, falls back to global provider. This is the init path, so it only happens once per instance, but it hides the dependency.
**Impact:** All users of `DesignLoaderAdapter()` with no args silently depend on global state.
**Ideal DI Flow:**
```
WorkshopContext(registries) -> DesignLoaderAdapter(registry_provider=registries)
```
**Recommendation:** Make `registry_provider` required when `design_loader` is None.
**Effort:** Simple

---

### MAJOR: WorkshopContext.__post_init__() resolves globally
**ID:** AR-010
**Location:** `game/ui/screens/workshop_context.py:69-72`
**Issue:** `WorkshopContext` is a frozen dataclass with `registries: Optional[GameRegistries] = None`. In `__post_init__()`, if registries is None, it resolves from the global provider with a broad try/except fallback. This dataclass is created in two places: `WorkshopContext.standalone()` and `WorkshopContext.integrated()`.
**Impact:** The WorkshopContext is meant to encapsulate all configuration for the design workshop. Having it silently resolve global state in its post-init undermines the explicit configuration intent.
**Ideal DI Flow:**
```
app.py creates registries -> passes to WorkshopContext.standalone(registries=registries)
StrategyScreen context_data includes registries -> WorkshopContext.integrated(registries=registries)
```
**Recommendation:** Both factory methods should accept and pass `registries`. The `__post_init__` fallback should be removed once all callers provide registries.
**Effort:** Simple (2 factory methods + their callers in app.py)

---

### MINOR: planet_report_panel.py inline resolution in utility function
**ID:** AR-011
**Location:** `game/ui/panels/planet_report_panel.py:475-476`
**Issue:** A module-level utility function `_calculate_planet_production_rates()` resolves the provider inline to create registries for harvester info lookups.
**Impact:** Low -- this is a UI display-only function. However, it cannot be tested with custom registries.
**Ideal DI Flow:** Accept `registries` as a parameter. Caller (the panel render method) provides it from screen context.
**Recommendation:** Add `registries` parameter.
**Effort:** Simple

---

### MINOR: empire_panel_window.py inline resolution in tab builder
**ID:** AR-012
**Location:** `game/ui/screens/empire_panel_window.py:185-186`
**Issue:** `_build_treasury_tab()` resolves the provider to create registries for `EmpireEconomyCalculator`. The panel already has access to `self.empire` and potentially the game session.
**Impact:** Low -- UI display code. But it creates registries fresh every time the tab is built.
**Ideal DI Flow:** Receive registries from the screen that creates the panel (StrategyScreen -> EmpirePanelWindow).
**Recommendation:** Accept registries in constructor or method parameter.
**Effort:** Simple

---

### MINOR: builder/right_panel.py and builder/schematic_view.py fallback in constructors
**ID:** AR-013
**Location:** `game/ui/screens/builder/right_panel.py:31-33`, `game/ui/screens/builder/schematic_view.py:36-38`
**Issue:** Both builder sub-panels create a `VehicleClassService` from the global provider when no `vehicle_class_service` is injected. These are constructed by `DesignWorkshopScreen`.
**Impact:** Low -- the workshop screen could easily pass the service down.
**Ideal DI Flow:**
```
WorkshopContext(registries) -> DesignWorkshopScreen -> right_panel(vehicle_class_service), schematic_view(vehicle_class_service)
```
**Recommendation:** DesignWorkshopScreen creates VehicleClassService once and passes to sub-panels.
**Effort:** Simple

---

### INFO: ship_stats.py and empire_economy_calculator.py docstring-only references
**ID:** AR-014
**Location:** `game/simulation/entities/ship_stats.py:47-48`, `game/strategy/engine/empire_economy_calculator.py:60-61`
**Issue:** These files reference `get_default_registry_provider()` only in docstring examples, not in runtime code. The docstrings teach the fallback pattern.
**Impact:** Docstrings that demonstrate the fallback pattern normalize it. New developers read these examples and replicate the anti-pattern.
**Recommendation:** Update docstrings to show strict DI examples instead.
**Effort:** Trivial

---

## Remediation Roadmap

### Phase 1: Establish Registries on GameSession (Foundation)
**Fixes:** AR-004 (TurnEngine), AR-005 (Facade)
**Dependencies:** None -- this is the foundation
**Changes:**
1. Add `registries` property to `GameSession` that resolves once at init time
2. Pass `registries` to `TurnEngine(registries=self.registries)` in both `__init__()` and `from_dict()`
3. `StrategySessionFacade.get_fleet_remaining_pods()` accesses `self._session.registries.components`
4. Make `TurnEngine.__init__` require registries (remove Optional + fallback)

**Risk:** Low. GameSession already creates a context where registries are available. TurnEngine already accepts the parameter.

### Phase 2: Fix Strategy Data Objects (Highest Impact)
**Fixes:** AR-001 (ShipInstance), AR-002 (FleetCapabilityCalculator)
**Dependencies:** Phase 1 (registries available on GameSession path)
**Changes:**
1. Add `_registries: Optional[GameRegistries]` field to ShipInstance (init=False, set by factories)
2. `ShipInstance.create()` and `ShipInstance.from_dict()` accept and store `registries`
3. `get_calculated_stats()` uses stored registries, falls back to parameter, raises if neither
4. `FleetCapabilityCalculator.__init__()` accepts `component_registry` parameter
5. `Fleet.__init__()` passes component_registry to calculator
6. Remove `_get_default_component_registry()` helper

**Risk:** Medium. ShipInstance is used everywhere. Need to update all `ShipInstance.create()` and `ShipInstance.from_dict()` callers. FleetCapabilityCalculator is only created in Fleet.

### Phase 3: Fix Initialization Functions (Simulation Layer)
**Fixes:** AR-003 (component.py), AR-006 (ship_loader.py)
**Dependencies:** None (these are initialization-path, not runtime)
**Changes:**
1. `load_components()` and `load_modifiers()` accept optional `registry_provider` parameter
2. `app.py` passes provider to both functions
3. `load_components_data()` requires `registries` (remove fallback)
4. `load_vehicle_classes()` -- already has parameter, update callers
5. `get_or_create_validator()` -- callers pass provider
6. `initialize_ship_data()` accepts and forwards provider

**Risk:** Low. Only 3-4 call sites per function.

### Phase 4: Fix UI Services (Consistency)
**Fixes:** AR-007 (ComponentService), AR-008 (ShipFactory), AR-009 (DesignLoaderAdapter), AR-010 (WorkshopContext)
**Dependencies:** None (UI layer, independent of strategy fixes)
**Changes:**
1. `ComponentService` requires `registry_provider` (match VehicleClassService pattern)
2. `ShipFactory` requires `registry_provider` in constructor, remove triple-fallback
3. `DesignLoaderAdapter` requires `registry_provider` when no `design_loader` given
4. `WorkshopContext.__post_init__()` remove fallback; both factory methods require registries
5. `app.py` passes registries when creating `WorkshopContext.standalone()`

**Risk:** Low. All UI services already support the parameter.

### Phase 5: Fix UI Screens (Low Priority)
**Fixes:** AR-011, AR-012, AR-013
**Dependencies:** Phase 4 (WorkshopContext carries registries)
**Changes:**
1. `planet_report_panel.py` utility function accepts registries parameter
2. `empire_panel_window.py` receives registries from StrategyScreen
3. Builder sub-panels receive VehicleClassService from DesignWorkshopScreen
4. Update docstrings (AR-014)

**Risk:** Very low. Display-only code.

---

## Dependency Graph (Ideal DI Flow)

```
app.py (Composition Root)
  |
  +-> RegistryManager.instance() -- populates dictionaries
  |     |
  |     +-> load_components(provider)     [Phase 3]
  |     +-> load_modifiers(provider)      [Phase 3]
  |     +-> load_vehicle_classes(provider) [Phase 3]
  |
  +-> GameRegistries (frozen snapshot of dict references)
  |
  +-> GameSession(registries)             [Phase 1]
  |     |
  |     +-> TurnEngine(registries)        [Phase 1]
  |     |     +-> sub-engines(registries) -- already done
  |     |
  |     +-> Empire -> Fleet(component_registry) [Phase 2]
  |     |     +-> FleetCapabilityCalculator(component_registry)
  |     |     +-> ShipInstance(registries)
  |     |           +-> get_calculated_stats() uses stored registries
  |     |
  |     +-> .registries property          [Phase 1]
  |
  +-> StrategyScreen
  |     +-> StrategySessionFacade(session) [Phase 1]
  |     |     +-> uses session.registries
  |     +-> EmpirePanelWindow(registries)  [Phase 5]
  |     +-> PlanetReportPanel(registries)  [Phase 5]
  |
  +-> WorkshopContext(registries)          [Phase 4]
        +-> DesignWorkshopScreen
              +-> ShipFactory(registries)  [Phase 4]
              +-> DesignLoaderAdapter(registries) [Phase 4]
              +-> ComponentService(provider) [Phase 4]
              +-> VehicleClassService(provider) -- already strict
              +-> right_panel(vehicle_class_service) [Phase 5]
              +-> schematic_view(vehicle_class_service) [Phase 5]
```

---

## Risk Assessment: What Breaks If We Remove All Fallbacks Tomorrow?

### Would Crash (callers pass None/nothing):

1. **`GameSession.__init__()` -> `TurnEngine()`**: No registries passed. TurnEngine would crash if fallback removed. **Fix in Phase 1.**

2. **`ShipInstance.get_calculated_stats()`**: Called from ~15 places. None of them pass registries. Every strategy screen/service that accesses ship stats would crash. **Fix in Phase 2.**

3. **`FleetCapabilityCalculator` methods**: Called whenever fleet capabilities are checked (build menus, warp checks, ability queries). All go through `_get_default_component_registry()`. Would crash. **Fix in Phase 2.**

4. **`app.py` -> `load_components()`, `load_modifiers()`**: Called at startup. Would crash before the game even loads. **Fix in Phase 3.**

5. **`WorkshopContext.__post_init__()`**: Called when opening Design Workshop from menu or strategy screen. Would crash. **Fix in Phase 4.**

6. **`ComponentService()` with no args**: Called in several UI screens. Would crash. **Fix in Phase 4.**

7. **Builder sub-panels**: Created without VehicleClassService. Would crash. **Fix in Phase 5.**

### Would Silently Fail (broad exception handling):

8. **`StrategySessionFacade.get_fleet_remaining_pods()`**: Has try/except that returns empty dict. Would silently return no pods, making colonization UI show no available colony pods. **Fix in Phase 1.**

### Would Work Fine (already has callers passing registries):

9. **`EmpireEconomyCalculator`**: Its only callers (`empire_panel_window.py`) already construct it with registries.
10. **`VehicleClassService`**: Already strict DI, would raise ValidationException.

---

## Top 5 Priority Issues

1. **AR-001 (CRITICAL): ShipInstance.get_calculated_stats()** -- Most impactful. Data object with hidden global coupling, called from 15+ locations. Every strategy test implicitly depends on global state. Fix enables proper test isolation for the most commonly used strategy object.

2. **AR-002 (CRITICAL): FleetCapabilityCalculator helper wrapper** -- Second most impactful. Every fleet capability check reaches into global state. The helper wrapper pattern actively hides the dependency. Fix enables testable fleet logic.

3. **AR-004 (MAJOR): TurnEngine constructor fallback** -- Foundation fix. TurnEngine is the central orchestrator. Once GameSession passes registries to TurnEngine, the entire engine pipeline is clean. This is also the prerequisite for AR-005.

4. **AR-003 (CRITICAL): component.py initialization functions** -- Affects the boot sequence. These are initialization functions that are part of the composition root pipeline, but they should receive their provider explicitly rather than reaching for the global.

5. **AR-010 (MAJOR): WorkshopContext.__post_init__()** -- Gateway fix for all workshop UI. Once WorkshopContext requires registries, all downstream workshop components (ShipFactory, DesignLoaderAdapter, sub-panels) can receive them transitively.
