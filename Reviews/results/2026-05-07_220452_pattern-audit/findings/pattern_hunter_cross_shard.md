# Cross-Shard Pattern Hunter Report

## Summary
- Pattern Checks Performed: 5
- Total Findings: 14
- Critical: 3 | Major: 8 | Minor: 3

---

## Facade Integrity (Pattern #5)

### CRITICAL: `build_queue_screen.py` and `empire_build_queue_window.py` bypass the facade with session fallback

**Files:**
- `game/ui/screens/build_queue_screen.py:88,426-429,463-466,498-501`
- `game/ui/screens/empire_build_queue_window.py:179,423-426`

Both screens hold `self.session` AND `self.facade`, with a dual-dispatch pattern:

```python
# build_queue_screen.py
self.session = session    # line 88
self.facade = facade      # line 89

# Dispatch fallback (lines 425-429):
if self.facade:
    self.facade.handle_command(cmd)
else:
    self.session.handle_command(cmd)
```

`StrategySessionFacade` is the documented single entry point from UI to strategy (Pattern #5, Architecture docs: "only UI-to-strategy entry point"). Every conditional `self.session.handle_command(cmd)` branch is a Facade bypass. The fallback is flagged as `# PROJ-208 Phase 3: Route through facade if available, fallback to session` — but the pattern doc (Pattern #5, Pattern #6) is clear: UI must go through Facade; GameSession should never be touched directly.

**Impact:** UI code can silently-drift from the facade contract, risk double-dispatch (different code paths for facade-present vs absent), and make facade refactoring harder because callers depend on session shape.

### CRITICAL: `StrategyScreen.__init__` directly constructs `GameSession` without facade mediation

**File:** `game/ui/screens/strategy_screen.py:81-83`

```python
from game.strategy.engine.game_session import GameSession
from game.ai.ai_factory import AIControllerFactory
self.session = GameSession(ai_factory=AIControllerFactory())
```

This is the composition root, so direct construction of the session is architecturally necessary here. However, the screen holds `self.session` (line 83) and passes it to downstream screens (BuildQueueScreen line 88, EmpireBuildQueueWindow line 163), which creates the session-bypass chains documented above. The screen should only expose `self._facade` and inject facade — not session — into child screens.

### MAJOR: UI layer imports from `game.strategy.services`, `game.strategy.systems`, and `game.strategy.data` directly

**127** UI imports from `game.strategy.data.*` or `game.strategy.engine.*` (full list truncated for report length). Representative samples:

| UI File | Strategy Import | Bypass Class |
|---|---|---|
| `game/ui/screens/strategy_screen.py:81` | `from game.strategy.engine.game_session import GameSession` | Session construction |
| `game/ui/screens/strategy_colonization.py:20` | `from game.strategy.engine.commands import IssueColonizeCommand, QueueColonizeMissionCommand` | Command DTO construction |
| `game/ui/screens/strategy_fleet_ops.py:17` | `from game.strategy.engine.commands import IssueMoveCommand, IssueInterceptCommand, IssueJoinFleetCommand` | Command DTO construction |
| `game/ui/screens/strategy_event_router.py:184,255,263,271` | `from game.strategy.engine.commands import SetAtmosphereTargetCommand, SetGravityTargetCommand, SetWaterTargetCommand, SetRadiationShieldTargetCommand` | Command DTO construction |

**40** UI imports from `game.strategy.services.*`:

| UI File | Service Import |
|---|---|
| `game/ui/screens/build_queue_panel_factory.py:18` | `from game.strategy.services.planet_economy_projector import compute_planet_production` |
| `game/ui/panels/system_tree_panel.py:438-599` | `from game.strategy.services.system_effects_collector import collect_system_effects, collect_sector_effects` |
| `game/ui/screens/planet_list_window.py:36-47` | `from game.strategy.services.system_effects_collector import ...` + `compute_planet_production` |
| `game/ui/screens/empire_panel_window.py:26` | `from game.strategy.services.empire_economy_service import EmpireEconomyService` |
| `game/ui/screens/cargo_quick_dialog_controller.py:22` | `from game.strategy.services.cargo_transfer_service import CargoTransferService` |
| `game/ui/screens/transfer_controller.py:87` | `from game.strategy.services.cargo_transfer_service import ...` |
| `game/ui/screens/planet_abilities_controller.py:108,138` | `from game.strategy.services.component_inspector import ...` |
| `game/ui/screens/strategy_detail_formatter.py:21,305` | `compute_planet_production` + `extract_abilities_from_component` |
| `game/ui/screens/strategy_render/cursor.py:10` | `from game.strategy.services.cargo_transfer_service import project_fleet_position` |
| `game/ui/screens/strategy_fleet_command_router.py:250` | `from game.strategy.services.component_inspector import extract_abilities_from_component` |
| `game/ui/screens/fleet_report_filters.py:12-310` | Multiple component inspector imports |
| `game/ui/screens/fleet_data_source.py:227-261` | `FleetSpeedCalculator`, component inspector |
| `game/ui/panels/race_description_panel.py:32` | `RaceDescriptionLLMController` |
| `game/ui/screens/race_setup/controller.py:30` | `RaceDescriptionLLMController` |

**26** UI imports from `game.strategy.systems.*`:

| UI File | Systems Import |
|---|---|
| `game/ui/screens/build_queue_screen.py:34` | `from game.strategy.systems.design_library import DesignLibrary` |
| `game/ui/screens/strategy_build_queue_manager.py:22` | `DesignLibrary` |
| `game/ui/screens/design_selector_window.py:21` | `DesignLibrary` |
| `game/ui/screens/race_setup/screen.py:26` | `RaceLibrary` |
| `game/ui/screens/race_setup/screen.py:30` | `RaceRandomizer` |
| `game/ui/screens/new_game_setup_screen.py:65` | `RaceLibrary` |
| `game/ui/screens/strategy_event_router.py:197,313,342` | `RaceLibrary` |
| `game/ui/screens/strategy_game_state_manager.py:94` | `SaveGameService` |
| `game/ui/screens/strategy_screen_lifecycle.py:131` | `SaveGameService` |
| `game/ui/screens/save_selection_window.py:194,209,432` | `SaveGameService` |
| `game/ui/panels/build_queue_controller.py:26` | `DesignLibrary` |
| `game/ui/panels/build_queue_portraits.py:52` | `DesignLibrary` |
| `game/ui/panels/build_queue_drag_handler.py:24` | `DesignLibrary` |
| `game/ui/screens/workshop_ship_io.py:16` | `DesignLibrary` |

**6** UI imports from `game.strategy.generation.*` (in `galaxy_test/` screens only — test-only screens are lower priority).

**Nuance:** Many `from game.strategy.engine.commands import *Command` imports are technically "pass-through" — the UI constructs a Command DTO and then routes through `facade.handle_command(cmd)`. This is a partial bypass: the UI is importing strategy-engine internals to construct the command object, even though the facade provides `dispatch_*` helpers that wrap this construction. The facade's `CommandDispatchSlice.__getattr__` generates one `dispatch_<helper_name>` method per registered `CommandSpec` — these are the intended UI-to-facade write path.

**Impact:** Direct service/system imports create a tight coupling between UI and strategy internals. If a service signature changes, UI code breaks. The facade's DTO read path was designed to decouple these layers but is being sidestepped for performance-critical or DTO-not-yet-available reads (e.g., `compute_planet_production` is computational, not state retrieval).

---

## Registry Consistency (Pattern #4)

### No issues found

- No `session_cache` usage detected anywhere in the codebase.
- `DefaultRegistryProvider` is consistently used for production paths; `TestRegistryProvider` for test paths.
- Registry DI via `IRegistryProvider` is followed in simulation code (no global `get_default_registry_provider()` calls in simulation).
- `GameRegistries.__post_init__()` supplies empty `ResourceCatalog` as documented convenience fallback.
- The ability source adapter package correctly avoids `get_default_registry_provider()` (documented as a static guard in Pattern #29).

**Status:** Pattern consistent across layers. No cross-shard divergence.

---

## Event Bus Fragmentation (Pattern #10)

### MAJOR: Dual-path event logging in strategy data classes creates pattern fork

**Files:**
- `game/strategy/data/empire.py:107-127`
- `game/strategy/data/fleet.py:395-454`

Both `Empire` and `Fleet` data classes contain a dual-dispatch pattern:

```python
# empire.py
if event_bus:
    event_bus.log_event(EventType.FLEET_JOIN_CANCELLED, ...)
else:
    from game.core.event_logging import log_event
    log_event(EventType.FLEET_JOIN_CANCELLED, ...)
```

This uses the module-level `log_event()` compatibility shim as a fallback when `event_bus` is not available. The documented intent (Pattern #10) is that `log_event()` is a "compatibility shim; new code should prefer explicit EventBus injection." Yet Fleet and Empire — core strategy data classes — contain this duplicate branching logic in every event emission site.

The same dual-path exists in `fleet.py` at lines 408-427 and 437-454 (two separate event emission blocks with identical `if event_bus: ... else: log_event(...)` structure).

### MAJOR: Module-level `log_event()` still used in production simulation code

**File:** `game/simulation/entities/projectile.py:97,116`

```python
from game.core.event_logging import log_event
...
log_event("SEEKER_EXPIRE", ...)
```

The simulation layer should use an injected EventBus per Pattern #10 ("simulation/strategy events"), but projectile.py uses the deprecated module-level shim directly. This is a Pattern #10 violation — new code should prefer explicit EventBus injection.

### No issues found with Workshop EventBus

The UI builder EventBus (`game/ui/screens/builder/event_bus.py`) is properly scoped. It is used by:
- `game/ui/screens/workshop_screen.py`
- `game/ui/screens/builder/weapons_viewmodel.py`
- `game/ui/screens/builder/weapons_panel.py`
- `game/ui/screens/test_lab/screen.py`
- `game/ui/screens/empire_build_queue_window.py`
- `game/ui/screens/empire_build_queue_viewmodel.py`
- `game/ui/screens/empire_build_queue_sidebar.py`
- `game/ui/screens/build_queue_viewmodel.py`

All consumers are UI-internal (workshop and build-queue MVVM components). No cross-contamination between Workshop EventBus and Core EventBus detected.

---

## CQRS-lite Audit (Pattern #6)

### MINOR: `GameSession.handle_command()` has a dead-path guard

**File:** `game/strategy/engine/game_session.py:343-355`

```python
def handle_command(self, command: Any) -> Any:
    if command.type == command.type.ISSUE_ORDER:
        return self._command_registry.dispatch(command.name, self, command)
    return None
```

All 40 command DTOs inherit from `Command`, whose `__post_init__()` sets `type = CommandType.ISSUE_ORDER`. The `CommandType` enum has only one value (`ISSUE_ORDER`), making the `if command.type == command.type.ISSUE_ORDER` guard a tautology. The `return None` branch is unreachable in production but silently masks future command types if `CommandType` ever gains new values.

### No issues found with command-handler coverage

The command registry is self-registering via `@command_spec` decorator (metadata-only contract). `seed_default_commands()` in `game/strategy/engine/commands/registry.py:331-363` imports 7 handler modules:

| Module | Commands Covered |
|---|---|
| `handlers/movement.py` | Colonize, Move, Intercept, Join, Warp |
| `handlers/order_queue.py` | ColonizeMission, ClearOrders, SplitFleet, DeleteOrder, ReorderOrder |
| `handlers/transfer.py` | Transfer |
| `handlers/build.py` | BuildOrder, RemoveBuildOrder |
| `handlers/construction_queue.py` | AddToConstructionQueue, RemoveFromConstructionQueue, ReorderConstructionQueue, SetBuildQueuePaused |
| `planet_command_handlers.py` | IssuePlanetOrder, ClearPlanetOrders, DeletePlanetOrder, SetAtmosphereTarget, SetGravityTarget, SetWaterTarget, SetRadiationShieldTarget |
| `superweapon_command_handlers.py` | IssueImplodePlanet, IssueStellerateStar, IssueOpenWarpPoint, IssueCloseWarpPoint, IssueCreateDysonSphere, IssueSelfDestruct, and their Queue variants |

**Status:** All 40 command DTOs have registered handlers. The `@command_spec` metadata-only decorator + per-module `register()` pattern eliminates the risk of commands without handlers. The `CommandRegistry` is the single source of truth for command metadata.

### Cross-layer command dispatch chain

The full flow for a command, traced end-to-end:

```
UI (e.g. strategy_colonization.py)
  → constructs IssueColonizeCommand(fleet_id=..., planet_id=...)
  → self.facade.handle_command(cmd)
  → CommandDispatchSlice.handle_command(cmd)   [facade slice]
  → GameSession.handle_command(cmd)             [strategy engine]
  → CommandHandlerRegistry.dispatch(name, session, cmd)  [runtime dispatch]
  → ColonizeCommandHandler.execute(session, cmd)         [handler]
  → session.active_empire.fleets[].add_order(...)        [state mutation]
  → returns ValidationResult
```

This chain is architecturally sound for commands that go through the facade. The facade also auto-generates `dispatch_*` helpers via `__getattr__` for callers that prefer the convenience method over manual DTO construction.

---

## Ability Source Drift (Pattern #29)

### No issues found

**7 documented adapters** in `game/strategy/services/ability_sources/`:

| Adapter | File | PROJ |
|---|---|---|
| `FacilityAbilitySource` | `facility.py` | PROJ-300 |
| `StormAbilitySource` | `storm.py` | PROJ-300 |
| `PlanetIntrinsicAbilitySource` | `planet_intrinsic.py` | PROJ-301 |
| `StarAbilitySource` | `star.py` | PROJ-302 |
| `WarpPointAbilitySource` | `warp_point.py` | PROJ-303 |
| `SystemAbilitySource` | `system_archetype.py` | PROJ-304 |
| `FleetAbilitySource` | `fleet.py` | PROJ-305 |

All 7 adapters:
- Implement `IAbilitySource` protocol (`game/core/protocols/strategy_entities.py:360`)
- Register through `register_source_provider_at_hex` and `register_source_provider_in_system` in `game/strategy/services/ability_iterator.py:303-316`
- Avoid calling `get_default_registry_provider()` — compliance with the documented adapter rule

**Zero class-level `IAbilitySource` implementations found outside `game/strategy/services/ability_sources/`.** The protocol-and-adapter pattern is highly consistent across all source types.

**Note on count:** Pattern #29 docs reference "8 documented adapters" but the `__init__.py` exports 7 classes. The `intrinsic_roll.py` module provides `roll_intrinsic_abilities()` (a helper function, not an adapter class) and `labels.py` provides `format_intrinsic_source_label()`. The documented count of 8 likely refers to 7 adapter classes plus the `roll_intrinsic_abilities` function as a shared utility. This is a documentation alignment issue, not a pattern violation.

### Consistency score across adapters

All adapters expose the same surface:
- `source_kind` (string: `"facility"`, `"storm"`, `"planet_intrinsic"`, `"star"`, `"warp_point"`, `"system"`, `"fleet"`)
- `source_label` (user-visible name via `labels.py`)
- `source_id` (entity identifier)
- `owner_id` (owner empire, or None for neutral/celestial)
- `get_abilities()` → list of ability dicts
- `affects_hex(hex_coord)` → bool
- `affects_system(system_id)` → bool
- Activation state fields (where applicable)

No adapter deviates from the protocol surface. No ad-hoc ability sources bypass the adapter pattern.

---

## Prioritized Architectural Recommendations

### 1. Eliminate session-fallback dispatch paths (CRITICAL — Facade)
**Files:** `build_queue_screen.py`, `empire_build_queue_window.py`
- Remove `self.session` attribute from both screens.
- Make `self.facade` required (non-optional).
- Route all command dispatch through `self.facade.handle_command()` or `self.facade.dispatch_*()` helpers.
- The `# PROJ-208 Phase 3: fallback to session` comments indicate this is acknowledged technical debt.

### 2. Remove session injection from StrategyScreen child propagation (CRITICAL — Facade)
**File:** `game/ui/screens/strategy_screen.py`
- `StrategyScreen` should not expose `self.session` to child screens.
- Child screens that currently take `session=` should receive `facade=` instead.
- The `GameSession` construction at line 81-83 (composition root) can remain, but the session ref should stay private to the screen/facade pair.

### 3. Collapse dual-path event logging (MAJOR — Event Bus)
**Files:** `empire.py`, `fleet.py`, `projectile.py`
- Empire and Fleet should receive `EventBus` injection consistently. Remove the `if event_bus: ... else: log_event(...)` fallback.
- `projectile.py` should receive an injected `EventBus` instead of the module-level `log_event()`.
- Once all callers are migrated, remove the module-level `log_event()` / `set_event_handler()` compatibility shim from `game/core/event_logging.py`.

### 4. Route service reads through facade DTOs (MAJOR — Facade)
**Affected:** 40 service imports in UI files
- `compute_planet_production` is called in 4 separate UI files. A `PlanetInfo.production_summary` or similar DTO field should be exposed through the facade, removing the direct import.
- `system_effects_collector` reads are used by `system_tree_panel.py`, `planet_list_window.py`, `planet_list_sidebar.py`, `planet_list_filters.py`. A facade DTO should encapsulate these effect aggregates.
- `component_inspector` calls (`extract_abilities_from_component`, `ship_has_ability`, `has_warp_capability`) are used by 7 UI files. These should be wrapped behind facade DTO fields or dedicated facade query methods.
- `cargo_transfer_service` (`project_fleet_position`) in `game/ui/screens/strategy_render/cursor.py` should go through facade projection.

### 5. Route system library access through facade (MINOR — Facade)
**Affected:** 26 imports from `game.strategy.systems.*`
- `DesignLibrary` is imported in 8 UI files. Since the facade owns design-related queries, `DesignLibrary` should be resolved indirectly via the facade.
- `SaveGameService` and `RaceLibrary` are used by lifecycle/event-router code — these are cross-cutting concerns that could be injected via the facade.
- `RaceRandomizer` in `race_setup/screen.py` and `race_setup_screen.py` is a UI-side randomizer; the import may be intentional.

### 6. Replace tautology guard in handle_command (MINOR — CQRS-lite)
**File:** `game/strategy/engine/game_session.py:353`
- Replace `if command.type == command.type.ISSUE_ORDER` with an explicit type-assertion or remove the guard entirely (all commands are `ISSUE_ORDER`).
- If `CommandType` is expected to gain new values, route each type explicitly; otherwise simplify to unconditional dispatch.
