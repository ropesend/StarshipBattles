# PROJ-211: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-27_211222_general_di-inconsistency-strategy](../../Reviews/results/2026-02-27_211222_general_di-inconsistency-strategy/)
- **Type:** General Review (DI-focused)
- **Date:** 2026-02-27
- **Report:** [View Full Report](../../Reviews/results/2026-02-27_211222_general_di-inconsistency-strategy/report.md)
- **Agents:** 5 review agents + 3 validators = 8 total

## Problem Statement

The codebase has a well-designed DI foundation (`IRegistryProvider`, `DefaultRegistryProvider`, `TestRegistryProvider`, `GameRegistries`) but is stuck in a half-migrated state from PROJ-38/PROJ-50. The pattern: PROJ-38 added `Optional[registries] = None` parameters, PROJ-50 was supposed to make them required but only partially completed. Result: 13 production files silently fall back to `get_default_registry_provider()` global state.

### Anti-Patterns Found
1. **Optional-with-fallback**: Constructor accepts `Optional[registries]`, falls back to global when None
2. **Inline resolution**: Method calls `get_default_registry_provider()` directly, no parameter at all
3. **Helper wrapper**: Module-level function wraps global access, hiding the dependency
4. **Silent error swallowing**: try/except around global resolution masks real failures
5. **Docstring teaching**: Examples in docstrings demonstrate the anti-pattern

### Gold Standard Pattern
`VehicleClassService` (PROJ-50): requires `registry_provider`, raises `ValidationException` if None.

## Ideal DI Flow (Target Architecture)

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

## Full Findings Inventory

### Strategy Layer (DI Strategy Analyst - 8 findings)
| ID | Severity | Location | Issue |
|----|----------|----------|-------|
| DI-S-001 | **Critical** | `ship_instance.py:239-271` | `get_calculated_stats()` has NO registries param, 20+ call sites |
| DI-S-002 | **Critical** | `fleet_capability_calculator.py:14-17` | Module-level `_get_default_component_registry()` helper, no DI path |
| DI-S-003 | Major | `turn_engine.py:161-170` | Optional registries with fallback, GameSession never passes |
| DI-S-004 | Major | `strategy_session_facade.py:493-506` | Inline resolution + silent try/except error swallowing |
| DI-S-005 | Major | `ship_instance.py:514-570` | `to_ship()` optional registries, planned "Phase 6" never completed |
| DI-S-006 | Minor | `empire_economy_calculator.py:59-68` | Docstring teaches global registry pattern |
| DI-S-007 | Info | `turn_engine.py:128-129` | Docstring documents fallback as API contract |
| DI-S-008 | Info | `empire_economy_calculator.py:79-86` | Optional without fallback (good but should be required) |

### Simulation Layer (DI Simulation Analyst - 9 findings, 3 downgraded by validators)
| ID | Severity | Location | Issue |
|----|----------|----------|-------|
| DI-SIM-006 | **Critical** | `ship_loader.py:161-167` | `initialize_ship_data()` no DI params, 13+ test callers |
| DI-SIM-001 | Major | `ship_loader.py:37` | `get_or_create_validator()` fallback + service locator |
| DI-SIM-002 | Major | `ship_loader.py:153` | `load_vehicle_classes()` fallback |
| DI-SIM-003 | Minor* | `component.py:514` | `load_components_data()` fallback (downgraded: init function) |
| DI-SIM-004 | Minor* | `component.py:569` | `load_components()` global resolution (downgraded: init function) |
| DI-SIM-005 | Minor* | `component.py:668` | `load_modifiers()` global resolution (downgraded: init function) |
| DI-SIM-007 | Minor | `ship_stats.py:47-48` | Docstring teaches anti-pattern |

### UI Layer (DI UI Analyst - 12 findings)
| ID | Severity | Location | Issue |
|----|----------|----------|-------|
| DI-UI-001 | **Critical** | `planet_report_panel.py:475-482` | `compute_planet_production()` zero injection path |
| DI-UI-002 | Major | `workshop_context.py:68-80` | Optional fallback in `__post_init__`, app.py never passes |
| DI-UI-003 | Major | `ship_factory.py:50-63` | Triple-fallback resolution pattern |
| DI-UI-004 | Major | `design_loader_adapter.py:40-49` | Module-level import + fallback |
| DI-UI-005 | Major | `component_service.py:46-49` | Lazy fallback with caching (stale data risk) |
| DI-UI-006 | Major | `empire_panel_window.py:185-193` | Inline resolution, session has registries available |
| DI-UI-007 | Minor | `schematic_view.py:35-38` | VehicleClassService fallback |
| DI-UI-008 | Minor | `right_panel.py:30-33` | VehicleClassService fallback |
| DI-UI-009 | Minor | `right_panel.py:116,208` | StrategyMetadataService.instance() (acceptable) |
| DI-UI-010 | Minor | `workshop_event_router.py:404` | StrategyMetadataService.instance() (acceptable) |
| DI-UI-011 | Info | `app.py:130-136` | Legitimate composition root (correct) |
| DI-UI-012 | Info | `vehicle_class_service.py:38-53` | Gold standard strict DI (correct) |

### Test Isolation (14 findings, several downgraded/rejected by validators)
| ID | Severity | Location | Issue |
|----|----------|----------|-------|
| TI-005 | **Critical** | `test_protocols_boundary.py` | `simple_ship` fixture uses global state |
| TI-006 | Minor | `test_workshop_context_di.py` | Backward-compat test verifies fallback |
| TI-007 | Minor | `test_design_loader_adapter.py:80` | Tests fallback behavior |

## Phase Design Rationale

Phases ordered to minimize churn and maximize leverage:

1. **Phase 1 (Foundation)**: GameSession gets registries property, wires to TurnEngine and Facade. This is the keystone -- once the session carries registries, everything downstream can access them.

2. **Phase 2 (Highest Impact)**: ShipInstance and FleetCapabilityCalculator are the two most-called DI violators. Complex but highest payoff for testability.

3. **Phase 3 (Boot Sequence)**: Initialization functions in component.py and ship_loader.py. These run at startup and populate registries. Low risk, independent of runtime path.

4. **Phase 4 (UI Services)**: ComponentService, ShipFactory, DesignLoaderAdapter, WorkshopContext. All follow the same pattern: make parameter required, wire from app.py.

5. **Phase 5 (Leaf UI + Cleanup)**: planet_report_panel, empire_panel_window, builder sub-panels, docstrings. Display-only code, very low risk.

## Risk Assessment

### Would crash if fallbacks removed today:
1. `GameSession -> TurnEngine()` -- no registries passed (Phase 1)
2. `ShipInstance.get_calculated_stats()` -- 15+ call sites (Phase 2)
3. `FleetCapabilityCalculator` methods -- all fleet capability queries (Phase 2)
4. `app.py -> load_components(), load_modifiers()` -- startup crash (Phase 3)
5. `WorkshopContext.__post_init__()` -- Design Workshop open (Phase 4)
6. `ComponentService()` with no args -- several UI screens (Phase 4)
7. Builder sub-panels -- VehicleClassService fallback (Phase 5)

### Would silently fail:
8. `StrategySessionFacade.get_fleet_remaining_pods()` -- returns empty dict (Phase 1)

## Dependencies & Risks
1. **Phase 2 is complex** -- ShipInstance is used everywhere. Requires updating `create()`, `from_dict()`, and all 3 delegate managers. Plan for 20+ call site updates.
2. **Fleet constructor change** -- `Fleet.__init__()` needs registries, Fleet is created in many places
3. **Test fixture updates** -- Tests that create ShipInstance/Fleet directly will need registries
4. **Phases 1, 3-5 are all Simple effort** -- could be done in a single session
