# Cross-System Duplicate-Systems Report

## Summary
- Pairs Analyzed: 12
- Clear Legacy: 0
- Ambiguous: 2
- Intentional Split (NOT findings): 8
- Total Findings: 2
- Critical: 0 | Major: 1 | Minor: 1 | Info: 0

---

## Phase 1 Name-Pair Drift Validation

### P-1: ModifierManager vs ModifierService
- **Manager**: `game/simulation/components/modifier_manager.py:30`
- **Service**: `game/simulation/services/modifier_service.py:16`
- **Phase 1 shared method**: `__init__` (weak signal — constructor overlap only)

**Verdict: INTENTIONAL SPLIT** — NOT a finding.

| Dimension | ModifierManager | ModifierService |
|---|---|---|
| Role | Component delegate (stateful) | Simulation-layer service (stateless rule engine) |
| Owns | `_modifiers: list[ApplicationModifier]` | `_modifiers: dict` (registry reference) |
| Key methods | `add_modifier`, `remove_modifier`, `get_modifier`, `get_all_effects`, `get_stat_summary` | `is_modifier_allowed`, `get_mandatory_modifiers`, `get_initial_value`, `ensure_mandatory_modifiers`, `get_local_min_max` |
| Consumer | `Component` class delegate | `ShipComponentManager` (late import) |
| Pattern | Facade/Delegate (#5) — per-component modifier lifecycle | Service — modifier validation rules for the registry |

`ModifierManager` manages per-component modifier instances (add/remove/aggregate effects). `ModifierService` validates modifier compatibility against component types and ensures mandatory modifiers are applied. These are complementary, not overlapping — the Facade/Delegate pattern (#5) documents this split intentionally.

---

## Narrative Pairs (Phase 1 did not catch)

### F-1: ModifierService vs ModifierLogicService + ComponentService — Triplicate Modifier Validation

**Severity: MAJOR**

Three classes implement overlapping modifier-allowed-checking logic at different layers:

| Class | Location | Layer | Key methods |
|---|---|---|---|
| `ModifierService` | `game/simulation/services/modifier_service.py:16` | Simulation | `is_modifier_allowed`, `get_mandatory_modifiers`, `is_modifier_mandatory`, `get_initial_value`, `ensure_mandatory_modifiers`, `get_local_min_max` |
| `ModifierLogicService` | `game/ui/screens/builder/modifier_logic.py:34` | UI/Builder | `is_modifier_allowed` (via ComponentService), `get_mandatory_modifiers`, `is_modifier_mandatory`, `get_initial_value`, `ensure_mandatory_modifiers`, `get_local_min_max`, `calculate_snap_value` |
| `ComponentService` | `game/ui/services/component_service.py:22` | UI/Services | `is_modifier_allowed` (inline), `get_modifier_registry`, `get_modifier_definition` |

**Overlap evidence — method-by-method:**

`is_modifier_allowed(mod_id, component) -> bool` exists in all three:
- `ModifierService:62` — checks `allow_types`, `deny_types`, `allow_abilities` against the modifier registry directly.
- `ComponentService:88` — same three restriction checks, nearly identical code shape.
- `ModifierManager:87` — inline `deny_types`/`allow_types` check inside `add_modifier()` (incomplete: doesn't check `allow_abilities`).

`get_mandatory_modifiers(component) -> list` exists in two:
- `ModifierService:108` — iterates all modifiers in the registry, checks `is_modifier_allowed`.
- `ModifierLogicService:70` — same logic through `ComponentService.get_modifier_registry()`.

`get_initial_value(mod_id, component) -> float` exists in two:
- `ModifierService:181` — if/elif chain for `simple_size_mount`, `hardened_mount`, `efficiency_mount`, `range_mount`, `facing`, `precision_mount`, plus generic `_has_arc_set_effect` detection.
- `ModifierLogicService:84` — dispatch table (`_INITIAL_VALUE_DEFAULTS`) covering `simple_size_mount`, `range_mount`, `facing`, `precision_mount`, plus hardcoded `turret_mount` arc_set handling.

`ensure_mandatory_modifiers(component) -> None` exists in two:
- `ModifierService:222` — identical body shape: call `get_mandatory_modifiers`, check `component.get_modifier`, call `component.add_modifier`, set initial value.
- `ModifierLogicService:121` — same algorithm, calls its own `get_mandatory_modifiers` and `get_initial_value`.

`get_local_min_max(mod_id, component) -> tuple` exists in two:
- `ModifierService:239` — generic `_has_arc_set_effect` detection for min clamping.
- `ModifierLogicService:105` — hardcoded `turret_mount` arc_set handling.

`_get_base_firing_arc(component) -> float | None` exists in two:
- `ModifierService:158` (static) — iterates abilities dict by `values()`.
- `ModifierLogicService:131` (instance) — iterates by known `_WEAPON_ABILITY_TYPES` tuple.

**Call-site counts (production only):**

| Class | Import sites | Caller files |
|---|---|---|
| `ModifierService` | 2 (late imports in `ShipComponentManager`) | `game/simulation/entities/ship_component_manager.py` |
| `ModifierLogicService` | 4 | `game/ui/screens/workshop_screen.py`, `game/ui/screens/builder/detail_panel.py`, `game/ui/screens/builder/modifier_row.py`, `game/ui/panels/builder_widgets.py` |
| `ComponentService.is_modifier_allowed` | 1 (via ModifierLogicService) | `game/ui/screens/builder/modifier_logic.py` |

**Classification: AMBIGUOUS** — Both `ModifierService` and `ModifierLogicService` are in active production use. Neither carries a deprecation marker. However, there is a clear architectural problem: the simulation-layer `ModifierService` is the canonical location per the layered architecture, and the UI-layer `ModifierLogicService` is a re-implementation that duplicates 80%+ of its surface.

**Cyclomatic divergence:**
- `ModifierService.get_initial_value` uses `_has_arc_set_effect` (generic arc_set detection) while `ModifierLogicService` hardcodes `turret_mount` and does NOT have generic detection. Any new arc_set modifier would be covered by `ModifierService` but silently fall through to `mod_def.default_val` in `ModifierLogicService`.
- `ModifierService` handles `hardened_mount` and `efficiency_mount` initial values; `ModifierLogicService` does not.
- `ModifierLogicService` adds `calculate_snap_value` (UI snap-button math — legitimate UI-only concern).

**Consolidation cost:**
- Move `is_modifier_allowed`, `get_mandatory_modifiers`, `get_initial_value`, `get_local_min_max`, and `ensure_mandatory_modifiers` from `ModifierLogicService` to delegate to `ModifierService` (instantiate one with `modifier_registry=provider.get_modifiers()`).
- Keep `calculate_snap_value` in the UI builder layer (it has no simulation equivalent).
- Migrate 4 UI files to import `ModifierService` instead of constructing a separate `ModifierLogicService`.
- Estimated effort: 1 PR, ~4 files touched.
- Behaviour reconciliation: must align the `_has_arc_set_effect` generic approach with the `turret_mount` special case. The generic approach is preferred — the hardcoded `turret_mount` in `ModifierLogicService` should adopt `_has_arc_set_effect` (which is already in `ModifierService`).

In addition, the inline restriction check in `ModifierManager.add_modifier:112-117` is a third implementation of the same logic and should be unified through `ModifierService.is_modifier_allowed` rather than inlined.

---

### F-2: WorkshopDataLoader vs RegistryLoader.reload_registries_from_directory — Duplicate Registry Loading Paths

**Severity: MINOR**

Two modules load the same JSON registries (modifiers.json, components.json, vehicleclasses.json):

| Aspect | `WorkshopDataLoader` | `RegistryLoader.reload_registries_from_directory` |
|---|---|---|
| Location | `game/ui/screens/workshop_data_loader.py:33` | `game/simulation/services/registry_loader.py:31` |
| Layer | UI | Simulation |
| Files loaded | modifiers.json, components.json, vehicleclasses.json, targeting/movement policies | modifiers.json, components.json, vehicleclasses.json |
| File fallback | User directory -> test_ prefix -> default data dir | test_ prefix -> standard name |
| Additional | Policy loading, default class detection | Registry-manager freeze guard |
| Production callers | 1 (`workshop_data_reloader.py`) | 0 (all call sites are in tests only) |

**Evidence:** Both independently:
1. Clear registries (`components.clear()`, `modifiers.clear()`, `vehicle_classes.clear()`)
2. Call `load_modifiers(path, registry_provider=...)`
3. Call `load_components(path, registry_provider=...)`
4. Call `load_vehicle_classes(path, registry_provider=...)`

**Classification: MINOR** — `RegistryLoader.reload_registries_from_directory` exists as the simulation-layer canonical loader but has **zero production callers** (all 57 references are test code). Production reloads go through `WorkshopDataLoader`, which adds workshop-specific concerns (policy loading, default class detection) on top of the same registry-population calls. The simulation-layer path is the correct home per architecture rules; `WorkshopDataLoader` should delegate to `reload_registries_from_directory` for the base registry load and layer its workshop-specific additions on top.

**Consolidation cost:**
- Make `WorkshopDataLoader.load_all()` call `reload_registries_from_directory` for the common registry load, keeping only policy loading and default-class detection as workshop-specific additions.
- Estimated effort: 1 file (`workshop_data_loader.py`), ~20 LOC removed.
- No behavioral risk: the underlying `load_modifiers`/`load_components`/`load_vehicle_classes` calls are identical.

---

## Intentional Splits (Reviewed, NOT findings)

These pairs were investigated and confirmed as architecturally intentional:

| # | Pair | Reason |
|---|---|---|
| IS-1 | `DesignRepository` vs `DesignCatalog` | Repository/cache CQRS-lite split (PROJ-427). Repository = filesystem; Catalog = in-memory. Catalog delegates save/load to Repository. |
| IS-2 | `EmpireEconomyService` vs `EmpireEconomyCalculator` | Facade (#5) over engine-layer calculator (PROJ-292). Service = UI-safe read surface; Calculator = engine implementation. |
| IS-3 | `GalaxyPathfindingService` vs `FleetNavigationService` | `FleetNavigationService` composes `GalaxyPathfindingService` for graph algorithms, adding fleet-specific order processing, speed-dependent movement, warp resolution, and path projection. Layered architecture. |
| IS-4 | `ValidationService` vs `ShipDesignValidator` | `ValidationService` is a UI-layer adapter over `ShipDesignValidator` (simulation). Thin facade — delegates `validate_addition` and `validate_design` directly. |
| IS-5 | `DesignLoaderAdapter` vs `SimulationDesignLoader` | `DesignLoaderAdapter` is a UI facade over `SimulationDesignLoader`, delegating `load_ship_from_design_data` and `load_ship_from_file`. |
| IS-6 | `VehicleClassService` vs `VehicleDesignService` | `VehicleClassService` = read-only registry access (UI layer). `VehicleDesignService` = ship creation/mutation service (simulation layer). Different responsibilities. |
| IS-7 | `ShipFactory` vs `ShipInstanceFactory` | `ShipFactory` creates simulation `Ship` entities for workshop/battle. `ShipInstanceFactory` creates strategy `ShipInstance` entities for the galaxy map. Different layers, different types. |
| IS-8 | `_facility_has_ability` (validator) vs `_facility_has_ability` (UI) | Strategy version checks component abilities via direct data inspection; UI version checks via `IAbilitySource` adapter (detects storm/fleet/system effects too). Different scopes — scopes produce different results, so they are not interchangeable. |
| IS-9 | `EventBus` (workshop) vs `EventBus` (core) | Workshop scope (UI builder events) vs simulation/strategy scope (structured event logging). Pattern #10 documents both. |
| IS-10 | `ComponentResourceManager` vs `ShipResourceManager` | Component-level activation costs vs ship-level resource state initialization. Different scopes. |
| IS-11 | `FleetCapabilityCalculator` vs `FleetConsumableAggregator` | Capability checks (spaceyards, warp, build types) vs resource aggregation (movement/warp costs, cargo). Completely different method surfaces — 0 overlapping methods. |
| IS-12 | `ResourceRegistry` (simulation) vs `ResourceCatalog` (core) | Runtime resource state tracking (combat) vs resource definition catalog (static). Different layers, different responsibilities. |

---

## Prioritized Consolidation Plan

| Priority | Finding | Severity | Prod Call Sites (legacy) | Est. PRs | Action |
|---|---|---|---|---|---|
| 1 | F-1: ModifierService vs ModifierLogicService + ComponentService | MAJOR | 4 UI imports of ModifierLogicService, 1 UI import of ComponentService.is_modifier_allowed, 2 simulation imports of ModifierService | 1 | Consolidate ModifierLogicService to delegate to ModifierService for shared methods. Keep `calculate_snap_value` in UI. Also inline `ModifierManager.add_modifier` restriction check through `ModifierService`. |
| 2 | F-2: WorkshopDataLoader vs RegistryLoader | MINOR | 1 (WorkshopDataLoader) | 1 | Make WorkshopDataLoader.load_all() delegate base registry reload to `reload_registries_from_directory`. |
