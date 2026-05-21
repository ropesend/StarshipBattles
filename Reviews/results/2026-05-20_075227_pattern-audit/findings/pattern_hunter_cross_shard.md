# Cross-Shard Pattern Hunter Report

## Summary
- Pattern Checks Performed: 7
- Total Findings: 14
- Critical: 2 | Major: 5 | Minor: 7

---

## Facade Integrity

### CRITICAL: UI imports strategy data objects bypassing facade read DTOs

Pattern #5 requires "UI talks to strategy through `StrategySessionFacade` DTOs and commands; UI must not mutate strategy domain objects directly." The facade exposes grouped-namespace DTOs (`FleetInfo`, `PlanetInfo`, `SystemInfo`, etc.) for read operations. However, 135+ import sites across `game/ui/` pull in raw strategy data objects directly from `game.strategy.data.*` and `game.strategy.engine.*`.

**Key bypass sites (production code, not test/dev):**

| File | Line(s) | Import | Concern |
|------|---------|--------|---------|
| `game/ui/screens/strategy_detail_fmt.py` | 290-291 | `CarriedVehicle`, `DropPod` | Reads raw data not exposed via facade DTOs |
| `game/ui/screens/strategy_detail_fmt.py` | 396 | `ActivationPhase` | Component activation state is engine internals |
| `game/ui/screens/strategy_detail_formatter.py` | 277 | `colony_has_planetary_yard` | Direct access to build queue internals |
| `game/ui/screens/planet_menu_items.py` | 24 | `FighterWing`, `SatelliteConstellation` | Deployed group dataclasses; facade should provide read DTOs |
| `game/ui/screens/fleet_menu_items.py` | 25 | `FighterWing`, `SatelliteConstellation` | Same as above |
| `game/ui/screens/fleet_data_source.py` | 241 | `FleetCapabilityCalculator` | Direct engine-class import |
| `game/ui/screens/fleet_report_filters.py` | 163, 302 | `FleetCapabilityCalculator` | Same |
| `game/ui/screens/build_queue_screen.py` | 23 | `BuildQueueSource`, `collect_build_queues_at_hex` | Strategy data object not available through facade |
| `game/ui/screens/build_queue_panel_factory.py` | 28 | `BuildQueueSource` | Same |
| `game/ui/panels/build_queue_controller.py` | 19-24 | `BuildContext`, `BuildQueueSource`, `Planet`, `Fleet`, `Galaxy`, `Empire` | Six direct strategy data imports |
| `game/ui/panels/race_summary_panel.py` | 22 | `HabitabilityFactors` | Direct data import for display |
| `game/ui/screens/race_setup/screen.py` | 24 | `RaceConfig` | Setup screen bypassing facade entirely |
| `game/ui/screens/race_setup/controller.py` | 19 | `RaceConfig` | Same |
| `game/ui/screens/new_game_setup_screen.py` | 59 | `GameConfig` | Engine config imported directly |
| `game/ui/screens/design_selector_window.py` | 29, 348, 390 | `DesignMetadata`, `DesignRoleRegistry` | Direct registry access |
| `game/ui/screens/transfer_view_model.py` | 243 | `ContainableKind` | Strategy enum for display filtering |
| `game/ui/screens/transfer_mass_preview.py` | 159 | `ContainableKind` | Same |
| `game/ui/screens/transfer_container_rows.py` | 65, 125 | `ContainableKind` | Same |
| `game/ui/screens/food_allocation_editor.py` | 40 | `Planet` | Raw planet object used for food editing |

**Mitigation context:** A static guard (`tests/static_guards/test_facade_bypass_guard.py`) blocks UI code from calling `session.handle_command()` directly — commands must route through `facade.handle_command()`. This guard effectively prevents the *write-path* bypass. However, there is no equivalent guard for the *read-path* — UI code freely imports strategy data classes for display purposes.

**Assessment:** The facade's read-path DTO coverage (FleetInfo, PlanetInfo, SystemInfo, etc.) is incomplete. UI files reach past the facade for data that the facade's grouped namespaces don't expose. This is a structural gap, not a single violation — the facade read DTOs need to cover all data the UI needs, or the architecture needs to formally acknowledge this read-path exception.

### CRITICAL: BuildQueueScreen and related UI directly construct commands AND import strategy internals for data reads

`game/ui/panels/build_queue_controller.py:19-24` imports `BuildContext`, `BuildQueueSource`, `Planet`, `Fleet`, `Galaxy`, and `Empire` directly — six strategy-layer imports in one file. While commands are dispatched through `facade.handle_command()`, the data objects are constructed and read outside the facade's read DTO pipeline. `game/ui/screens/fleet_data_source.py:241` imports `FleetCapabilityCalculator` directly.

- `game/ui/screens/build_queue_screen.py:23` — imports `BuildQueueSource` and `collect_build_queues_at_hex` directly
- `game/ui/panels/build_queue_controller.py:19-24` — six direct strategy imports
- `game/ui/screens/fleet_data_source.py:241` — `FleetCapabilityCalculator`

---

## Registry Consistency

### MAJOR: Simulation layer calls `get_default_registry_provider()` through adapter boundary

Pattern #3 (Registry DI) and Pattern #29 (Universal Ability Source) require that simulation code never call `get_default_registry_provider()`. The `battle_runner.py:321` enforces this with a runtime guard, and `ability_sources/__init__.py:18` documents the adapter rule.

However, `game/strategy/adapters/simulation_adapter.py:51-52` constructs a `get_default_registry_provider()` call and passes it into the simulation layer as the injection point. This is architecturally correct (the strategy layer injects the provider, simulation doesn't resolve it), but the adapter itself is a potential leak point.

**Verified no-violation sites** (correct injection pattern):
- `game/strategy/services/ability_sources/facility.py:8` — docstring warns against module-level registry getter; constructor injects
- `game/simulation/battle_runner.py:219-233` — production path receives injected provider
- `game/simulation/services/registry_loader.py:53` — explicit contract: "do not call `get_default_registry_provider()` from outside the Simulation layer"

### MINOR: `session_cache` used only in tests — no production drift

`session_cache` (the `SessionRegistryCache` test fixture) appears only in:
- `conftest.py:34`
- `tests/conftest.py:168`
- `tests/unit/builder/test_builder_ui_sync.py:25`

Production code consistently uses `get_default_registry_provider()` or constructor injection. No registry pattern fork detected between test and production paths.

### MINOR: Some strategy-layer service files resolve registries via module-level getter

These are in the strategy layer (allowed to call `get_default_registry_provider()`), but the `ability_sources` adapter rule explicitly prohibits it inside adapters:

- `game/strategy/services/component_layers.py:52-53` — resolves `get_default_registry_provider()` inside a method
- `game/strategy/engine/game_session.py:165` — session bootstrap resolves provider

The adapter rule is followed within `ability_sources/` itself; these are in adjacent strategy services that haven't adopted the same strict injection pattern.

---

## Event Bus Fragmentation

### MAJOR: Two incompatible EventBus implementations with stale cross-references

Two `EventBus` classes exist with fundamentally different architectures:

| Aspect | `game/core/event_logging.py::EventBus` | `game/ui/screens/builder/event_bus.py::WorkshopEventBus` |
|--------|----------------------------------------|----------------------------------------------------------|
| Scope | Strategy/simulation events | UI builder widget coordination |
| Handler model | Single callable (constructor-injected) | Pub/sub with multiple subscribers |
| Event type | String `event_type` + `**kwargs` | String event type + single `data` arg |
| Lifecycle | Session-scoped, owned by GameSession | Widget-scoped, owned by ViewModels |
| Consumers | `game/strategy/engine/session/`, `game/simulation/combat/` | `workshop_screen.py`, `build_queue_screen.py`, `test_lab/` |

The `WorkshopEventBus` docstring (`game/ui/screens/builder/event_bus.py:5`) references a stale path:
```
the canonical strategy-layer ``EventBus`` (``game/core/events/event_bus.py``)
```
This path no longer exists — the core `EventBus` was relocated to `game/core/event_logging.py` (PROJ-390). The stale reference suggests the two buses have drifted out of documented alignment.

**Assessment:** Both buses serve legitimate but non-overlapping needs. The core bus carries strategy simulation events (combat, turn events, etc.) via injection; the workshop bus decouples UI widgets. However, the divergence in:
- Pub/sub model vs single-handler
- Event payload structure
- Error handling strategy

...means there is no shared EventBus contract. If UI screens ever need to bridge between strategy events and UI updates, they can't use a common interface.

### MINOR: No strategy event bus used for UI state updates

The core `EventBus` (`game/core/event_logging.py`) is used for simulation/turn events but never for propagating state changes from strategy to UI. UI widgets either poll the facade or listen to their own `WorkshopEventBus`. There is no documented pattern for how strategy → UI event propagation should work.

---

## CQRS-lite Audit

### No violations found: Command dispatch is consistent and registry-backed

Pattern #6 (CQRS-lite) and #7 (CommandHandlerRegistry) are followed consistently:

- All 43 command classes (`game/strategy/engine/commands/__init__.py`) extend the `Command` base dataclass
- Commands are pure DTOs — no behavior, no direct state mutation
- `CommandDispatchSlice` (`game/strategy/facade/slices/command_dispatch_slice.py`) routes through `command_registry` with a cached `specs_by_facade_helper()` lookup
- UI code constructs commands and dispatches through `facade.handle_command()` (35 verified call sites)
- `FacadeCommands` grouped namespace strips `dispatch_` prefix from 36 helpers
- Static guard prevents direct `session.handle_command()` bypass (`tests/static_guards/test_facade_bypass_guard.py`)
- BUG-125 fix ensures commands don't carry empire identity — handlers gate on session context

**Verified dispatch paths** (all correct):
- `game/ui/screens/build_queue_input_router.py:112,144,178`
- `game/ui/screens/strategy_build_queue_manager.py:272,276`
- `game/ui/screens/strategy_fleet_command_router.py:315`
- `game/ui/screens/planet_abilities_controller.py:248`
- `game/ui/screens/transfer_controller.py:330`
- `game/ui/screens/strategy_superweapons.py:128,170,229,267,309,348`
- `game/ui/screens/strategy_fleet_ops.py:141,165,225`
- `game/ui/screens/strategy_colonization.py:137,214`
- `game/ui/screens/strategy_click_dispatcher.py:315`
- `game/ui/screens/fms_menu_callbacks.py:41,96`
- `game/ui/screens/empire_build_queue_window.py:438`
- `game/ui/screens/strategy_event_router.py:237,272`
- `game/ui/screens/cargo_quick_dialog_controller.py:117`
- `game/ui/screens/strategy_windows/orders_window_ctrl.py:57,64,74,81,92`
- `game/ui/screens/strategy_windows/fleet_report_ctrl.py:60`

---

## Ability Source Drift

### No violations found: All 7 adapters follow the IAbilitySource pattern

The Universal Ability Source pattern (#29) documents 7 adapters (the task description's "8" count is incorrect):

| # | Adapter | File | Source Kind |
|---|---------|------|-------------|
| 1 | `FacilityAbilitySource` | `facility.py` | `facility` |
| 2 | `StormAbilitySource` | `storm.py` | `storm` |
| 3 | `PlanetIntrinsicAbilitySource` | `planet_intrinsic.py` | `planet` |
| 4 | `StarAbilitySource` | `star.py` | `star` |
| 5 | `WarpPointAbilitySource` | `warp_point.py` | `warp_point` |
| 6 | `SystemAbilitySource` | `system_archetype.py` | `system` |
| 7 | `FleetAbilitySource` | `fleet.py` | `fleet` |

All 7:
- Implement the `IAbilitySource` protocol (`game/core/protocols/strategy_entities.py:361`)
- Expose `source_kind`, `source_label`, `source_id`, `owner_id`, `get_abilities()`
- Follow the adapter rule: registry is constructor-injected, never resolved via module-level getter
- Register through `ability_iterator.py` provider registration

**Helper utilities (not adapters):**
- `intrinsic_roll.py` — shared randomness helper for intrinsic ability templates
- `labels.py` — canonical label formatter for source display

**No new ability sources bypassing the adapter pattern detected.**

### MAJOR: `IAbilitySource.source_kind` discriminator has no enum — string-typed with 7 known values

The `source_kind` property (`game/core/protocols/strategy_entities.py:375`) returns a `str` with docstring listing 7 values: `'facility' | 'storm' | 'planet' | 'star' | 'warp_point' | 'system' | 'fleet'`. There is no `StrEnum` or `Literal` type to constrain the value space. Adding an 8th source kind would require updating the docstring in the protocol (which developers may miss) rather than adding an enum member (which would produce a type error if forgotten).

---

## Strategy Modal Window Compliance

### MAJOR: `SettingsWindow` does not subclass `StrategyModalWindow`

`game/ui/screens/settings_window.py:14`:
```python
class SettingsWindow(UIWindow):
```

`SettingsWindow` is a strategy-screen modal opened from `EmpirePanelRegistrar` (`game/ui/screens/strategy_windows/empire_panel_ctrl.py:90`). It extends `UIWindow` directly instead of `StrategyModalWindow`:

- No `window_manager` parameter in constructor
- No modal registration/deregistration
- Manual `on_close_callback` slot cleanup instead of base-class auto-cleanup
- Does NOT set `is_blocking = True`, so pygame_gui hover suppression is absent
- Bypasses `StrategyEventRouter.iter_live_modals()` — not counted in `has_modal_open()`

**Impact:** While `SettingsWindow` is open:
- Hover on background UI elements (top-bar buttons) may leak through
- Other modal tracking mechanisms (manual slot on `StrategyWindowManager.settings_window`) must be separately maintained
- Any future modal-blocking behavior added to the base class will not apply

### MAJOR: `RaceSetupScreen`, `NewGameSetupScreen` extend UIWindow directly — but may be out of strategy-screen scope

- `game/ui/screens/race_setup/screen.py:63` — `class RaceSetupScreen(pygame_gui.elements.UIWindow)`
- `game/ui/screens/new_game_setup_screen.py:125` — `class NewGameSetupScreen(pygame_gui.elements.UIWindow)`
- `game/ui/screens/race_browser_dialog.py:82` — `class RaceBrowserDialog(pygame_gui.elements.UIWindow)`

These screens are likely outside the strategy screen's modal scope (they are full-screen setup flows), so not subclassing `StrategyModalWindow` may be intentional. However, if they ever need strategy-screen modal blocking, they would need to adopt the base class.

### Confirmed compliant windows (26 classes extend StrategyModalWindow):
`PlanetListWindow`, `StarListWindow`, `EventLogWindow`, `FleetReportWindow`, `EmpirePanelWindow`, `BuildQueueListWindow`, `EmpireBuildQueueWindow`, `OrdersWindow`, `TransferDialog`, `PlanetSelectionWindow`, `SystemSelectionWindow`, `FleetSelectionWindow`, `PlanetAbilitiesWindow`, `DesignSelectorWindow`, `DefeatDialog`, `TurnFailedDialog`, `SaveSelectionWindow`, `CargoQuickDialog`, `MoveChoiceWindow`, `PlanetTargetEditor`, `FoodAllocationEditor`, + mixin-based classes (`DataListWindowMixin`, `RaceConfigResolverMixin`)

---

## Container Substrate Consistency

### No critical violations found

The Unified Container Substrate pattern (#43) replaced three legacy storage abilities (`ResourceStorage`, `CargoStorage`, `VehicleBay`) and eight legacy entity-level storage fields. Current state:

**Verified correct usage:**
- `game/strategy/data/container.py` — `Container` dataclass with three internal slices (`_resources`, `_items`, `_population`), unified `capacity_mass`, and `ContainerPolicy`
- `game/strategy/data/bay_inventory.py` — `BayInventory` uses `Container` internally per PROJ-436
- Production code stores items through `Container._items` (27 references, all correctly scoped)

**Legacy residue (already addressed per PROJ-436):**
- `game/strategy/data/ship_instance.py:79,126,170,178,549,552,572,786` — legacy `carried_items` references in comments and backward-compatible property; marked as removed/transitional
- `game/strategy/data/ship_cargo_manager.py:27,266,321,347` — comments referencing legacy `carried_items`; all mutations now go through `BayInventory`
- `game/strategy/data/carried_vehicle.py:8` — comment noting legacy untyped dict flow
- `game/strategy/data/ship_instance_serializer.py:62,118` — legacy save format references

**Assessment:** The container pattern is consistently applied. The legacy comments are documentation of the transition and don't represent active bypasses.

### MINOR: Legacy `carried_items` references in comments could be cleaned up

`ship_instance.py`, `ship_cargo_manager.py`, and `ship_instance_serializer.py` still contain legacy `carried_items` references in docstrings and comments. While the actual code paths use `BayInventory`/`Container`, these stale references create confusion for developers navigating the codebase.

---

## Prioritized Architectural Recommendations

1. **CRITICAL — Extend facade read-path DTO coverage** (Facade Integrity)
   The facade's grouped namespaces expose `FleetInfo`, `PlanetInfo`, `SystemInfo`, etc., but don't cover `BuildQueueSource`, `FleetCapabilityCalculator`, `CarriedVehicle`, `DropPod`, `DeployedGroup` subtypes, `ContainableKind`, or `RaceConfig`. UI files reach past the facade for these — either add DTOs to the facade's read surface or formally document which strategy data types are UI-safe for read-only access. Without this, the facade pattern is a write-path-only half-facade.

2. **CRITICAL — Evaluate `build_queue_controller.py` and `fleet_data_source.py` for facade integration** (Facade Integrity)
   `game/ui/panels/build_queue_controller.py` imports six strategy data classes. `game/ui/screens/fleet_data_source.py` imports `FleetCapabilityCalculator`. These are the densest single-file bypass sites and should be prioritized for facade-DTO migration or architectural exemption with explicit documentation.

3. **MAJOR — Make `SettingsWindow` extend `StrategyModalWindow`** (Strategy Modal Window)
   Add `window_manager` parameter and base-class registration. This is a straightforward 4-line change with high impact — it closes the hover-leak and modal-tracking gap for settings.

4. **MAJOR — Resolve EventBus fragmentation** (Event Bus)
   Either: (a) document the two buses as intentionally separate with non-overlapping domains and fix stale path references in comments, or (b) create a shared `EventBusProtocol` that both implementations satisfy. The stale `game/core/events/event_bus.py` reference in `WorkshopEventBus`'s docstring should be corrected regardless.

5. **MAJOR — Add `StrEnum` for `IAbilitySource.source_kind` discriminator** (Ability Source)
   Replace the string doc-comment with an enum type on the `source_kind` property. This ensures type-checker enforcement when new source kinds are added and prevents misspellings at adapter construction time.

6. **MINOR — Clean up legacy `carried_items` comments** (Container Substrate)
   Remove stale `carried_items` references from comments in `ship_instance.py`, `ship_cargo_manager.py`, and `ship_instance_serializer.py`. The transition is complete; the comments are noise.

7. **MINOR — Standardize registry resolution in strategy services** (Registry)
   Strategy-layer services like `component_layers.py` and `game_session.py` resolve `get_default_registry_provider()` at call time. Consider constructor-injecting the provider to match the `ability_sources` adapter rule pattern. This would make strategy services testable with `TestRegistryProvider` without relying on module-level defaults.

8. **MINOR — Consider a strategy → UI event propagation pattern** (Event Bus)
   Currently there's no documented mechanism for strategy state changes to push updates to UI. UI either polls the facade or uses its own `WorkshopEventBus`. If strategy events (combat results, turn completions) need to trigger UI updates, the core `EventBus` could be bridged to UI listeners.
