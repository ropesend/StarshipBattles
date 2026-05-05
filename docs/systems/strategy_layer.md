# Strategy Layer System

> **Last verified:** 2026-05-04 — PROJ-366: extended § 5 Replay Persistence with a "Background Verification Sidecars" subsection covering the `ReplayVerificationCoordinator` listener API, sidecar lifecycle, `verification_status` field on `ReplayLookup`, and production wiring at `app_bootstrap.py`. Earlier same-day pass: Coverage backfill (T3-23 / T3-24): added § 1 "Facade Slice Architecture" subsection (PROJ-309 sub-phase 3.7, 9 internal slices behind the public facade with delegation pattern + cache-invalidation timing); added § 5 "Replay Persistence — `ReplayStore` + `ReplayResolver`" subsection (PROJ-312 strategy-side persistence + UI graceful-degradation contract). Earlier same-day pass: doc-audit fix (`IOrderable` protocol path → `game/core/protocols/strategy_entities.py`). 2026-05-02 — PROJ-320: documented per-fleet movement-opportunity combat dispatch in §3 Per-Tick Phase Execution Order Phase 4 row. Replaces the legacy per-tick contested-hex scan with per-fleet `tick % get_tick_interval(fleet.speed) == 0` triggering, gated by whether the fleet left its hex this tick (TurnEngine derives `moved_fleet_ids` from a pre/post Phase-3 location diff). Multi-fleet-per-empire encounters: spec compiler groups by `owner_id` so allied fleets share a team. ~10× reduction in combat invocations at typical contested sectors. Earlier same-day pass — Issue #7: documented `TurnEngine.process_turn`'s new `progress_callback: Optional[Callable[[int, int], None]]` keyword-only parameter (see §3 "Per-Tick Progress Callback"). Plumbed identically through `GameSession.process_turn` and `StrategySessionFacade.process_turn`. The strategy screen wires a closure that runs `pygame.event.pump()` + redraw + `display.flip()` every tick so the "PROCESSING TURN..." overlay can show a live "Tick N / 100" sub-line. Engine-side guard: callback exceptions are caught with `# Intentional broad catch:` (PROJ-308 convention) and logged at WARNING; a buggy UI callback never breaks turn execution. Per-call state cleared via `try/finally` in `process_turn`. Mid-turn Esc cancellation is NOT supported (event.pump() flushes the OS queue but does not consume Esc) — only inter-turn Esc cancel still works during `run_n_turns`. Earlier same-day pass — Issue #8: Updated §5 "Replay Wiring (FEAT-26)" to reflect the differentiated `SimulationBattleResolver` shortcut branches. The legacy `shortcut_no_capable` branch (both fleets have ships, no team has weapons) now runs the simulator at the truncated `_BRIEF_RUN_TICK_BUDGET` so a real (brief) replay is captured; only `sole_survivor` and the defensive `no_ships` keep the shortcut, both shipping `BattleResult.replay_unavailable_reason` so the Event Log button shows an honest disabled-tooltip instead of "older save." Earlier verification (2026-04-29): FEAT-28: Added "Mutual-Pursuit Rendezvous Routing" subsection under FleetPursuerTracker. Two mutually-pursuing fleets (each head order is `MOVE_TO_FLEET`/`JOIN_FLEET` targeting the other) now bypass `calculate_intercept_point` and pathfind directly to the target's current hex; both move toward each other along the shortest line at their own speeds. `FleetMovementEngine.collect_movements` adds a `_filter_jump_past_collisions` post-processor that drops the larger fleet's queue entry on swap-hex parity (mirrors BUG-122 `_elect_canonical_merges` tiebreak). Earlier same-day pass: Added §6 "Galaxy Size Contract" subsection documenting FEAT-27: `DEFAULT_SYSTEM_COUNT = 2` single-source-of-truth in `game_config.py`, `1 ≤ system_count ≤ 150` validation, N=1 shared-system mode (multiple empires on distinct planets, no warp lanes, planet-shortage retry loop), N≥2 distinct-system invariant with hard error on E>N, hand-rolled linspace home-index distribution, per-system planet counter, and the continuous quadratic slider curve `value = 1 + 149 * (t / SLIDER_T_MAX) ** 2`. Concurrently backfilled BUG-123 + FEAT-26 deferred sections in §5 Event System. BUG-123: `EventLog.get_events_for_empire(empire_id, *, include_global=True)` + the `current_empire.id` UI scoping convention + the `empire_id == -1` broadcast sentinel + the optional `empire_id` kwarg added to `get_events_for_turn` / `get_events_by_category` + the empire-name window-title threading on `StrategyUI` / `StrategyWindowManager`. FEAT-26: strategy-side replay wiring (Replay button column, `EventLogWindow` click flow, `ReplayResolver` graceful-degradation states, `Game.start_replay` forwarder, `BattleConfig.replay_mode` with `screen_router.start_battle(config=...)` widening, `BattleScreen` REPLAY MODE label). BUG-125 fix from same-day verification still current: `Command.empire_id` field removed (Q5=DROP); `session.player_empire` renamed to `session.active_empire` and now rotated by `StrategyGameStateManager.advance_turn` on each hot-seat turn change. Fleet command handlers gate on `session.active_empire.id` via the new `BaseCommandHandler._resolve_player_fleet` helper; planet handlers continue to gate on `session.active_empire.id` (now correct in hot-seat). Earlier verification (2026-04-28): BUG-122 fix: `redirect_pursuers` gains an `exclude=` kwarg and returns `(redirected, excluded)`; `Fleet.merge_with` excludes the absorbing fleet to prevent self-target cycles. Earlier same-day pass: BUG-119 storm coordinate-frame note (`StormAbilitySource.system` field for global-frame translation), FEAT-17 per-yard `construction_queue_paused` flag on Planet, PlanetaryFacility, and Fleet noted alongside `construction_queue` in the data-model sections, FEAT-19 surplus-food happiness bonus.

System documentation for the turn-based strategy layer.

---

## 1. StrategySessionFacade

**File:** `game/strategy/facade/strategy_session_facade.py`

CQRS-lite pattern: the single point of access for all UI-to-engine communication.
The UI layer never accesses `GameSession` internals directly.

### Write Path (Commands)

All state mutations go through `handle_command(command) -> ValidationResult`.
The facade delegates to `GameSession.handle_command()`, which dispatches
to the `CommandHandlerRegistry`.

`process_turn()` advances the game by one turn (delegates to `GameSession.process_turn()`).

### Read Path (Queries)

All queries return **immutable DTOs**, never domain objects.

**PROJ-254 Performance:** `_get_planet_by_id()` uses a lazy-built index dict.
`get_all_stars()` caches results per turn. These avoid O(n) scans on every call.

DTO types (defined in `game/strategy/facade/dto/` package, with submodules `fleet_dto.py`, `system_dto.py`, `planet_dto.py`, `empire_dto.py`, re-exported via `__init__.py`):
- `FleetInfo` -- fleet state snapshot (includes `name`, `composition_summary`, `carried_items_summary`, `pod_storage_capacity`, `pod_storage_used`)
- `FleetSummary` -- lightweight fleet overview
- `StarInfo` -- star data with system context (PROJ-231)
- `SystemInfo` -- star system data
- `PlanetInfo` -- planet details (includes `staging_yard_summary`; `shield_active` is now populated from `active_abilities['PlanetaryShield']`)
- `EmpireInfo` -- empire state
- `ColonySummary` -- colony overview
- `FleetOrderInfo` -- order display data (type, target, progress)
- `ShipInfo` -- ship instance summary for fleet display
- `WarpPointInfo` -- warp point data (destination, location)

Each DTO has a `from_<domain_object>()` class method for conversion.

### Query Categories

| Category | Methods |
|----------|---------|
| Fleet | `get_fleet()`, `get_fleets_at_hex()`, `get_fleet_path_preview()`, `get_fleet_path_projection()` |
| System | `get_all_systems()`, `get_all_stars()`, `get_system_at_hex()`, `get_system_near_hex()`, `get_system_containing_fleet()` |
| Planet | `get_planet()`, `get_planets_at_hex()` |
| Empire | `get_all_empires()`, `get_empire()`, `get_empire_colonies()`, `get_empire_fleets()` |
| Game State | `get_turn_number()`, `get_human_player_ids()`, `get_save_path()` |
| Events | `get_turn_events()`, `get_all_events()`, `get_events_by_category()` |
| Validation | `can_colonize()`, `can_move_to()`, `get_fleet_remaining_pods()` |
| Environment | `get_storm_names_at_hex()` |
| Race Registry (PROJ-287) | `get_race_registry()` -- returns the session-scoped `IRaceRegistry` (a `CachedRaceRegistry` over `RaceLibrary`) for resolving `race_id -> RaceConfig` without per-call filesystem reads. Lazy-init; one instance per facade. See [04_SERVICES.md § Race Registry](../04_SERVICES.md#race-registry-proj-287). |
| Colony Demographics (PROJ-288) | `get_colony_demographic_view(planet_id) -> Optional[ColonyDemographicView]` -- one-shot snapshot of per-species (race_id, count, habitability, happiness, projected growth rate, food ratio, food allocation) + per-resource (`ResourceProjection` from `PlanetEconomyProjector`) + summed `total_upkeep` for one colony. Species ordered largest count first; unresolvable race_ids dropped. Returns `None` for unowned/missing planets. See [04_SERVICES.md § Planet Economy Projector](../04_SERVICES.md#planet-economy-projector-proj-288). |

### Facade Slice Architecture (PROJ-309)

`StrategySessionFacade` is the public entry point (53 query/dispatch
methods total), but its body is intentionally thin: each method is a
one-line forwarder to one of **9 internal slices** under
`game/strategy/facade/slices/`. PROJ-309 sub-phase 3.7 split the original
922-line facade for the explicit reason that "splitting into per-domain
slices makes the facade hard to grow back into a single god-class."

| Slice | File | Responsibility |
|-------|------|----------------|
| `FacadeSessionState` | `_facade_state.py` | Shared per-turn caches: planet index dict (PROJ-254), fleets-by-hex cache, all-stars cache, lazy `IRaceRegistry`. Constructed once by the facade and passed by reference into every other slice. |
| `CommandDispatchSlice` | `command_dispatch_slice.py` | The 28 `dispatch_*` typed-command helpers + the universal `handle_command()` entry point. Owns write-path delegation. |
| `FleetSlice` | `fleet_slice.py` | Fleet queries (`get_fleet`, `get_fleets_at_hex`), path-preview helpers, `can_move_to`, colony-pod state. |
| `PlanetSlice` | `planet_slice.py` | Planet queries (`get_planet`, `get_planets_at_hex`) and planet-shaped validation (`can_colonize`). |
| `SystemSlice` | `system_slice.py` | Star-system / map queries (`get_all_systems`, `get_all_stars`, `get_system_at_hex`, `get_storm_names_at_hex`). |
| `EmpireSlice` | `empire_slice.py` | Empire-scoped queries (`get_all_empires`, `get_empire`, `get_empire_colonies`, `get_empire_fleets`) and build-queue aggregation. |
| `EconomySlice` | `economy_slice.py` | Heavy demographic snapshot (`get_colony_demographic_view`), lazy race-registry resolution, economy-config wiring. |
| `EventSlice` | `event_slice.py` | Event-log queries (`get_turn_events`, `get_all_events`, `get_events_by_category`) with per-empire scoping (BUG-123), plus plain session state (`get_turn_number`, `get_save_path`, `get_human_player_ids`). |

**Composition pattern — delegation, not inheritance.** The facade
constructs every slice in `__init__`, passing the shared
`FacadeSessionState` to each. Slices never reach into each other; any
cross-domain lookup goes through the shared state object. Public-facing
methods on `StrategySessionFacade` are thin: `get_fleet(id)` is literally
`return self._fleet_slice.get_fleet(id)`.

**Authoring rule — callers use facade methods, not slices directly.**
Reaching into a slice from outside the facade is a layer violation. The
`_planet_index`, `_fleets_by_hex_cache`, `_all_stars_cache`, and
`_race_registry` `@property` forwarders on the facade exist purely to
keep legacy tests working and should not be added to in new code.

**Cache invalidation timing.** `FacadeSessionState` caches are scoped to
the active turn; per-turn invalidation happens inside `process_turn()`
before the new turn's commands run. Slices that materialise expensive
DTOs (notably `EconomySlice.get_colony_demographic_view`) recompute on
each call — those callers are expected to be UI-driven and infrequent.

---

## 2. Command Dispatch

**File:** `game/strategy/engine/command_handlers.py`

### Architecture

```
UI -> StrategySessionFacade.handle_command(cmd)
       -> GameSession.handle_command(cmd)
           -> CommandHandlerRegistry.dispatch(cmd_name, session, cmd)
               -> ICommandHandler.execute(session, cmd) -> ValidationResult
```

### ICommandHandler Protocol

```python
class ICommandHandler(Protocol):
    def execute(self, session: GameSession, command: Command) -> ValidationResult: ...
```

### Command Ownership Validation (BUG-125)

`Command` DTOs do **not** carry an empire identifier. Identity is session
context — handlers gate on `session.active_empire.id`. The UI must never
supply identity through a request body; doing so was the root cause of
the original cross-empire-orders bug (UI passed `empire_id=fleet.owner_id`,
handler checked `cmd.empire_id == fleet.owner_id`, a tautology that
authorized any selectable fleet).

**The active-empire rotation contract:**
`session.active_empire` (renamed from `session.player_empire` in
BUG-125) is the empire whose turn it currently is. It defaults to
`empires[0]` at session creation and is rotated by
`StrategyGameStateManager.advance_turn` on each hot-seat turn change
(via `_sync_active_empire`). Save/load resets to `empires[0]`; the UI
rotation index lives in `StrategyScreen.current_player_index`.

**Authorization helper:** every fleet-command handler calls
`BaseCommandHandler._resolve_player_fleet(session, fleet_id)`, which
loads the fleet and checks `fleet.owner_id == session.active_empire.id`.
Use the lower-level `_resolve_fleet(empire_id=None)` only for the rare
case of a legitimate cross-empire fleet lookup (e.g. the
intercept-target fleet — the source-fleet command authorization always
flows through `_resolve_player_fleet`).

Planet handlers gate on `planet.owner_id == session.active_empire.id`
inline; before BUG-125 they read `session.player_empire.id`, which never
rotated and silently broke planet-command authorization in hot-seat
for player 2.

### BaseCommandHandler

Mixin providing resolution helpers used by all handlers:
- `_resolve_player_fleet(session, fleet_id)` -- BUG-125 standard
  authorization path: returns `(Fleet, None)` if
  `fleet.owner_id == session.active_empire.id`, else
  `(None, ValidationResult.error(...))`. Use this for source-fleet
  resolution in every fleet handler.
- `_resolve_fleet(session, fleet_id, empire_id?)` -- returns
  `(Fleet, None)` or `(None, ValidationResult)`. Validates
  `fleet.owner_id == empire_id` when `empire_id` is not None.
  `empire_id=None` is the intercept-target path (cross-empire targets
  are legitimate; the source-fleet authorization is the gate).
- `_resolve_fleet_required(session, fleet_id, empire_id?)` -- returns
  Fleet or raises ValueError.
- `_resolve_planet(session, planet_id)` -- returns `(Planet, None)` or
  `(None, ValidationResult)`.
- `_resolve_planet_optional(session, planet_id, required?)` -- returns
  Planet or None/raises.

### CommandHandlerRegistry

Registry pattern with `register(command_name, handler)` and `dispatch(command_name, session, cmd)`.

Factory: `create_default_registry()` registers all handlers.

### Registered Handlers

| Command | Handler | Purpose |
|---------|---------|---------|
| `IssueMoveCommand` | `MoveCommandHandler` | Queue MOVE order with pathfinding |
| `IssueColonizeCommand` | `ColonizeCommandHandler` | Direct colonize (deploy pod, claim planet) |
| `QueueColonizeMissionCommand` | `ColonizeMissionCommandHandler` | Chain: MOVE + COLONIZE (population/cargo transferred via explicit TRANSFER orders) |
| `IssueInterceptCommand` | `InterceptCommandHandler` | MOVE_TO_FLEET order |
| `IssueJoinFleetCommand` | `JoinCommandHandler` | MOVE_TO_FLEET + JOIN_FLEET |
| `IssueTransferCommand` | `TransferCommandHandler` | Cargo transfer with auto-MOVE |
| `IssueWarpCommand` | `WarpCommandHandler` | Warp transit with auto-MOVE to warp point |
| `ClearOrdersCommand` | `ClearOrdersCommandHandler` | Clear all orders and path |
| `IssueBuildOrderCommand` | `BuildOrderCommandHandler` | INSERT BUILD order at front |
| `RemoveBuildOrderCommand` | `RemoveBuildOrderCommandHandler` | Remove BUILD orders |
| `SplitFleetCommand` | `SplitFleetCommandHandler` | Split ships into new fleet |
| `DeleteOrderCommand` | `DeleteOrderCommandHandler` | Remove specific order by index |
| `ReorderOrderCommand` | `ReorderOrderCommandHandler` | Swap order positions |
| `AddToConstructionQueueCommand` | `AddToConstructionQueueCommandHandler` | Add item to build queue |
| `RemoveFromConstructionQueueCommand` | `RemoveFromConstructionQueueCommandHandler` | Remove queue item |
| `ReorderConstructionQueueCommand` | `ReorderConstructionQueueCommandHandler` | Move queue item |
| `IssuePlanetOrderCommand` | `IssuePlanetOrderCommandHandler` | Issue planet action order (shield, stabilizer) |
| `ClearPlanetOrdersCommand` | `ClearPlanetOrdersCommandHandler` | Clear planet orders |
| `DeletePlanetOrderCommand` | `DeletePlanetOrderCommandHandler` | Remove specific planet order |
| `SetAtmosphereTargetCommand` | `SetAtmosphereTargetCommandHandler` | Set atmosphere modification target for planet |
| Superweapon commands (11 total) | `superweapon_command_handlers.py` | Implode planet, stellerate star, warp points, dyson sphere, self-destruct |

### Shared Helpers

- `add_move_order_if_needed(session, fleet, target_hex, start_hex?)` -- chain-aware MOVE queuing

---

## 3. Turn Engine

**File:** `game/strategy/engine/turn_engine.py`

### Overview

TurnEngine is a lightweight orchestrator that delegates to 13 specialized sub-engines.
All sub-engines are dependency-injected: `registries` is a **required** keyword-only parameter (no default), while other engine parameters are optional with lazy defaults.

`process_turn(empires, galaxy, save_path)` runs one full turn:
1. **100-tick subturn loop** -- each tick runs all phases below
2. **Population growth** -- runs once after the loop

### Per-Tick Phase Execution Order

| Phase | Engine | Description |
|-------|--------|-------------|
| 0 | `HarvestingEngine` | Planetary resource extraction to planet.stockpile (1/100th per tick). Also aggregates `StagingYard` capacity per colony into `colony.max_staging_mass`. |
| 0b | `ConsumableManagementEngine` | Per-turn resource consumption (1/100th per tick) |
| 0c | `ResupplyEngine` | Fuel generation at facilities |
| 0c1 | `PlanetEnergyEngine` | Planet energy generation, consumption, auto-deactivation. **PROJ-253:** Caches facility scan results per planet (fingerprint-based invalidation). |
| 0d | `ResupplyEngine` | Fleet resupply from facilities |
| 0e | `ProductionEngine` | Construction from local stockpile/fleet cargo + mid-turn completion |
| 0f | `EnvironmentalHazardEngine` | Storm damage, fuel drain |
| 1 | `OrderProcessor` | Instant orders (JOIN_FLEET) |
| 1.5 | `ActionExecutionEngine` | Action orders (COLONIZE, TRANSFER, superweapons) |
| 1.6 | `PlanetActionEngine` | Planet action orders (shield activation, etc.) — all consecutive planet action orders dispatch instantly on the same tick |
| 2 | `FleetMovementEngine` | Calculate paths/next moves |
| 3 | `FleetMovementEngine` | Apply all movements simultaneously |
| 4 | `ConflictResolutionEngine` | Combat detection and resolution. **PROJ-320:** combat is dispatched per-fleet on each fleet's movement-opportunity tick (`tick % get_tick_interval(fleet.speed) == 0`), gated by whether the fleet successfully left its hex on that tick (TurnEngine snapshots fleet locations pre/post-Phase-3 and passes the diff as `moved_fleet_ids`). Multiple fleets per empire all participate (spec compiler groups by `owner_id`); allied fleets share a team. Replaces the legacy per-tick contested-hex scan that fired ~100 battles per turn at any stalemated sector. See `_should_trigger_combat_for_fleet` and `_resolve_conflicts` in `conflict_resolution_engine.py`. |

After the 100-tick loop:
- `PopulationEngine.process_population_growth(empires)`
- `QualityEngine.process_quality_improvement(empires)` — planetary quality improvement
- `AtmosphereEngine.process_atmosphere(empires)` — atmosphere modification toward targets

### Sub-Engine Interfaces

All sub-engines implement interfaces from `game/strategy/interfaces/engines.py`:

| Interface | Default Implementation |
|-----------|----------------------|
| `IMovementEngine` | `FleetMovementEngine` |
| `IProductionEngine` | `ProductionEngine` |
| `IOrderProcessor` | `OrderProcessor` |
| `IConflictEngine` | `ConflictResolutionEngine` |
| `IConsumableEngine` | `ConsumableManagementEngine` |
| `IPopulationEngine` | `PopulationEngine` |
| `IResupplyEngine` | `ResupplyEngine` |
| `IHarvestingEngine` | `HarvestingEngine` |
| `IActionExecutionEngine` | `ActionExecutionEngine` |
| `IEnvironmentalHazardEngine` | `EnvironmentalHazardEngine` |
| `IPlanetEnergyEngine` | `PlanetEnergyEngine` |
| `IPlanetActionEngine` | `PlanetActionEngine` |
| `IComponentActivationEngine` | `ComponentActivationEngine` |

### Dependency Injection

```python
# Production code
engine = TurnEngine(registries=registries)

# Test code -- inject mocks for fast, isolated tests
engine = TurnEngine(
    registries=test_registries,
    movement_engine=mock_movement,
    production_engine=mock_production,
    conflict_engine=mock_conflict,
)
```

Factory function: `create_default_turn_engine(registries)` for standard initialization.

### Performance Tracking

TurnEngine accumulates per-phase timing and logs a summary after each turn
at WARNING level for profiling.

### Per-Tick Progress Callback (Issue #7)

`TurnEngine.process_turn(...)` accepts an optional keyword-only argument:

```python
progress_callback: Optional[Callable[[int, int], None]] = None
```

When supplied, the callback is invoked at the top of every `_process_tick`
with `(current_tick, TICKS_PER_TURN)`. The strategy screen uses this hook
to repaint the "PROCESSING TURN..." overlay between ticks so the player
sees a live "Tick N / 100" sub-line while the otherwise-synchronous
100-tick loop runs.

**Plumbing chain** (each layer adds `*, progress_callback=None` and
forwards it):

```
StrategyGameStateManager.process_full_turn   # builds the closure
  → StrategySessionFacade.process_turn       # forwards the kwarg
    → GameSession.process_turn               # forwards the kwarg
      → TurnEngine.process_turn              # stashes on self._progress_callback
        → TurnEngine._process_tick           # invokes per tick
```

**Engine-side guard:** the per-tick invocation is wrapped in a
`try/except` with the `# Intentional broad catch:` justification
(PROJ-308 convention); failures are logged at WARNING and suppressed so
a buggy UI callback cannot break turn execution. The callback reference
is stashed on `self._progress_callback` inside a `try/finally` block so
it is cleared between calls (no leakage between successive `process_turn`
invocations on the same engine instance).

**UI-side closure** (in `StrategyGameStateManager.process_full_turn`):

```python
def _on_tick(current: int, total: int) -> None:
    self._screen.current_tick = current
    self._screen.total_ticks = total
    pygame.event.pump()                  # keep OS event queue drained
    surface = pygame.display.get_surface()
    if surface is not None:
        self._screen.draw(surface)
        pygame.display.flip()
```

`StrategyScreen` carries `current_tick: int | None` and `total_ticks:
int | None` fields. They are set to `None` in a `finally` block once the
turn finishes (or aborts) so the overlay's secondary line is hidden when
no turn is mid-flight.

**Known limitation:** `pygame.event.pump()` flushes the OS event queue
but does not consume Esc. Mid-turn Esc cancellation is NOT supported —
only inter-turn Esc cancel still works during `run_n_turns`. Adding
mid-turn cancel would require a re-entrant cancel path that interrupts
the engine's tick loop; out of scope for issue #7.

**Renderer + overlay:** `StrategyRenderer.draw_processing_overlay` and
`game/ui/screens/strategy_render/overlay.py::draw_processing_overlay`
both accept keyword-only `current_tick` and `total_ticks` parameters.
When both are non-None, the overlay renders a smaller (size 28
non-bold) "Tick N / 100" line 24px below the main 48-bold label.

---

## 4. Fleet System

**File:** `game/strategy/data/fleet.py`

### Fleet Class

Core state:
- `id` -- globally unique int from `Galaxy.get_next_fleet_id()` (not per-empire)
- `display_name: str` -- renamable label (auto-set to "Fleet N" per-empire at creation)
- `name` property -- returns `display_name` if set, else `"Fleet {id}"` fallback
- `composition_summary` property -- ship composition string for tooltips
- `owner_id`, `location: HexCoord`
- `ships: List[ShipInstance]` -- canonical flat list of all ships
- `orders: List[Order]`, `path: List[HexCoord]`
- `speed: float` -- minimum of all combat-capable ships' speeds
- `construction_queue: List[Dict]` -- for fleets with space yards
- `construction_queue_paused: bool` -- FEAT-17 per-fleet pause flag; when True, `ProductionEngine.process_construction_tick` skips ticking this fleet's queue and Treasury / Planet-detail forecasts treat its drain as zero. Fleet yards share one queue, so this is per-fleet (not per-yard). Mirror flags exist on `Planet.construction_queue_paused` (planetary-yard base queue) and `PlanetaryFacility.construction_queue_paused` (each shipyard facility queue, independently)

**Fleet ID generation:** `Galaxy.get_next_fleet_id()` produces globally unique
sequential IDs across all empires. This prevents ID collisions in the galaxy-wide
`fleets_by_id` registry. Per-empire display numbering uses
`Empire.get_next_fleet_display_number()` for cosmetic naming only.

Fleet hierarchy (organizational overlay for combat behavior):
- `task_forces: List[TaskForce]` -- task forces containing squadrons
- `fleet_policy: CombatPolicy` -- fleet-level combat policy defaults
- `get_unassigned_ships()` -- ships not in any task force

The hierarchy is a **3-level tree**: Fleet → TaskForce → Squadron → Ships.
Task forces and squadrons reference ships from `fleet.ships` by `instance_id`.
Ships can exist at any level (lone ships in a task force, or unassigned at
fleet level). Each level can set independent policies for targeting, movement,
and retreat. Unset policies inherit from the parent level.

See `game/strategy/data/fleet_hierarchy.py` (BattleRole, CombatPolicy,
FleetHierarchyNode), `game/strategy/data/task_force.py`, and
`game/strategy/data/squadron.py`.

### Design Roles

**Data file:** `data/design_roles.json` (PROJ-278 Phase 2: ported to `{"roles": [{...}, ...]}` shape with field names `display_name` / `vehicle_type_filter`)
**Registry accessor:** `game/strategy/data/design_role_registry.py` — `get_default_design_role_registry() -> RoleRegistry`
**Schema + machinery:** `game/core/roles.py` — `Role`, `RoleRegistry`, `RoleRegistryReadOnlyError` (PROJ-278)
**Enum + classifier:** `game/strategy/data/design_role.py` — `DesignRole`, `classify_design_role`, `classify_from_design_data`

Design roles are classification labels assigned to vehicle designs. They
drive auto-suggestion for fleet organization and UI grouping but have no
direct combat behavior effect. The player assigns a role in the Design
Workshop via a dropdown.

**27 roles** defined in `data/design_roles.json`, each with:
- `id` — string identifier (e.g., `"line_combatant"`)
- `display_name` — display name (e.g., `"Line Combatant"`)
- `description` — tooltip text
- `vehicle_type_filter` — which vehicle types can use this role (e.g., `["Ship", "Satellite"]`); empty tuple = no restriction

Role categories:
- **Ship combat** (6): line_combatant, fleet_escort, interceptor, assault_ship, missile_platform, raider
- **Ship support** (4): carrier, support_ship, scout, command_ship
- **Universal** (4): general_purpose, shield_projector, sensor_platform, stellar_protector
- **Planetary complex** (5): resource_harvester, production_facility, defensive_platform, planetary_modifier, research_facility
- **Specialized** (8): transport, superweapon_platform, megastructure_builder, enrichment_facility, resupply_depot, construction_accelerator, colony_pod, assault_pod

**Layered loading** (PROJ-278): `_build_default()` in `design_role_registry.py` loads in priority order — base `data/design_roles.json` (required) → `mods/<mod_name>/design_roles.json` (optional directory) → `output/design_roles_overlay.json` (optional user overlay). Later sources override earlier ones for the same role id.

**Runtime add:** the design_role registry is constructed with `allow_runtime_add=True`, so subsystems can call `registry.add_user_role(role)` to register player-added roles. (UI for player runtime-add is a future project.)

**Authoring rule for new role-derived caches (PROJ-278 Phase 5):** If you add code that caches data derived from `design_role_registry` (e.g. a precomputed lookup keyed on role id, an archetype mapping table, a filtered-design-list cache), you MUST register an invalidation callback via `registry.register_invalidation_callback(self._invalidate_cache)` so the cache is dropped when a player adds a custom role at runtime. See [tests/unit/strategy/data/test_design_role_registry_invalidation.py](../../tests/unit/strategy/data/test_design_role_registry_invalidation.py) for a worked example.

> Phase 5 audit (2026-04-18) found zero current cachers — `_DESIGN_ROLE_TO_ARCHETYPE` in `formation.py` is a hardcoded module-level dict, not a cache; `game/ai/` doesn't consume design_role; `DesignLibrary.filter_designs` filters in-line. The invalidation API is in place for future use, with the smoke test above as a regression guard.

**RoleRegistry API** (replaces deleted `DesignRoleRegistry` class):
- `get(role_id) -> Role` — raises `KeyError` on miss (dict-like API)
- `all() -> List[Role]` — sorted by id for deterministic iteration
- `get_roles_for_vehicle_type(vehicle_type) -> List[Role]` — sorted by `display_name`; roles with empty filter match any type
- `add_user_role(role)` — runtime mutation; fires invalidation callbacks
- `load_from_file(path, source_tag)` / `load_from_file_optional(path, source_tag)`
- `register_invalidation_callback(cb)`

**Reverse lookup pattern** (was `get_role_id_by_name(display_name)`): `next((r.id for r in registry.all() if r.display_name == name), None)`

**Auto-classification** (unchanged by PROJ-278):
- `classify_design_role(abilities, mass)` — classify from ability set + mass
- `classify_from_design_data(design_data, component_registry)` — classify from full design

**Ship field:** `Ship.design_role: str` — stored in design JSON, defaults to `"general_purpose"`

**ShipInstance fields:**
- `design_role: Optional[str]` — from design data
- `role_override: Optional[str]` — player override per instance
- `effective_role` property — returns override if set, else design_role

### TaskForce.formation (PROJ-269 Phase 4)

`TaskForce.formation: Optional[FormationSpec]` stores the combat
formation authored for the task force. `None` means "use the
design-role default" — resolved at battle start by
`FormationResolver.resolve(...)` consuming `resolve_default_for_task_force`.

Serialized on `TaskForce.to_dict()` / `from_dict()`. Missing key in
legacy saves deserializes to `None` (the project "saves are disposable"
rule applies).

See `docs/systems/combat_simulation.md` §0 "Formation System" for the
8 shapes, rotation pipeline, and design-role-to-default mapping.

### Per-Component HP Persistence (PROJ-269 Phase 2)

`ShipInstance.components: Dict[str, ComponentState]` tracks per-component
state across battles. Keyed by `"{component_id}#{instance_index}"` so
multiple identical components on a ship (e.g. three seeker missiles)
are disambiguated. `ComponentState` carries `component_id`,
`instance_index`, `current_hp`, `is_active`.

The round-trip: the strategy battle compiler
([game/strategy/combat/spec_compiler.py](../../game/strategy/combat/spec_compiler.py))
translates `ShipInstance.components` into `BattleSpec.ships[...].components`
(tuple of `ComponentStateSpec`). After the battle, `BattleSpec.post_battle_hook`
(defaults to `apply_outcome_to_fleets` from
[game/strategy/combat/post_battle_hook.py](../../game/strategy/combat/post_battle_hook.py))
writes the post-battle HP back into `ShipInstance.components`. See
`docs/systems/combat_simulation.md` §0 for the full flow.

Ships accumulate damage across battles — no automatic repair between
strategy turns. Repair is a future project.

`ShipInstance.components: Dict[str, ComponentState]` is the sole source
of truth for per-instance HP. The legacy single-instance
`component_damage: Dict[str, int]` dict was removed in PROJ-276, which
closed out the PROJ-269 Phase 2 transition. `ComponentState` carries
`current_hp`, `max_hp`, `is_active`, with an `is_damaged` property
driving UI damage indicators.

**DesignMetadata field:** `design_role: str` — extracted during `from_design_file()`,
used by `DesignSelectorWindow` role filter dropdown.

**UI integration:**
- **Design Workshop** right panel: "Role:" dropdown after "AI:" dropdown, filtered by current vehicle type. Updates when vehicle type changes.
- **Design Selector** (load dialog): "Design Role:" filter dropdown in sidebar. Defaults to "All Roles", filters design list when a specific role is selected.
- **Build Queue Screen**: "Roles" panel in the left column provides a scrollable list of all roles for the current category. Selecting a role filters the "Available Designs" center list.

All 25 QS starter designs have `design_role` assigned.

### Group Combat Policies

**Data file:** `data/group_policies.json`
**Registry:** `game/strategy/data/group_policy_registry.py`

Group policies define combat behavior for fleet hierarchy nodes. Three
independent axes, each with preset IDs:

**Targeting** (7 presets): `focus_strongest`, `focus_nearest`, `focus_weakest`,
`distributed`, `anti_fighter`, `anti_capital`, `opportunistic`.
Focus modes coordinate group fire on one target; distributed lets ships
pick independently.

**Movement** (7 presets): `advance`, `hold_range`, `hold_position`, `pursue`,
`hit_and_run`, `ram`, `evasive`. Each maps to a per-ship movement policy
from `movement_policies.json`.

**Retreat** (7 presets): `group_25`, `group_50`, `individual_15`, `individual_30`,
`flagship_lost`, `ammo_depleted`, `never`. Group mode triggers when
aggregate HP drops; individual mode uses per-ship thresholds.

`GroupPolicyRegistry.validate_policy(combat_policy)` returns error messages
for invalid preset IDs.

### Spatial Behaviors

**Package:** `game/ai/spatial_behaviors/`

Spatial behaviors define how ships position relative to an anchor (ship,
group centroid, or zone). Each behavior computes a target position; the
AI controller navigates the ship there.

| Behavior | Type | Description |
|----------|------|-------------|
| `FreeManeuverBehavior` | Loose | No spatial constraints |
| `BattleLineBehavior` | Rigid | Line/wedge/echelon perpendicular to leader facing |
| `ColumnBehavior` | Rigid | Single file behind leader |
| `ScreenBehavior` | Loose | Orbit around anchor point at radius |
| `EscortBehavior` | Loose | Stay near anchor ship |
| `PatrolZoneBehavior` | Loose | Cover a circular zone |

Factory: `create_spatial_behavior(type_str, **kwargs)` creates behavior by
type string. Unknown types default to `FreeManeuverBehavior`.

### Deployment Zones

**File:** `game/strategy/services/deployment_zone_calculator.py`

Maps `BattleRole` to positions on the 100000x100000 battlefield.
Team 0 deploys on the left, Team 1 mirrors on the right.

| Role | Team 0 X | Y Offset | Purpose |
|------|----------|----------|---------|
| RESERVE | 10000 | 0 | Held back |
| MAIN_BODY | 25000 | 0 | Primary battle line |
| SCREEN | 35000 | 0 | Between vanguard and main |
| VANGUARD | 42000 | 0 | Forward deployment |
| FLANKER_LEFT | 25000 | -15000 | Wide left envelopment |
| FLANKER_RIGHT | 25000 | +15000 | Wide right envelopment |

- `DeploymentZoneCalculator.get_zone_center(role, team_id)` — zone center as Vector2
- `DeploymentZoneCalculator.compute_positions(count, role, team_id)` — ship positions as (x,y) tuples

### Group Coordination

**File:** `game/ai/group_target_coordinator.py`

Stateless utility for group-level combat decisions:

- `select_focus_target(enemies, priority, reference_position)` — pick one target for focus fire
  - Priorities: `strongest` (mass), `most_damaged` (HP ratio), `nearest` (distance), `largest`
- `compute_group_hp_ratio(ships)` — aggregate HP/maxHP for a group
- `should_commit_reserve(main_body_ships, threshold)` — True when main body HP <= threshold
- `find_flagship_successor(ships, has_cnc_check)` — heaviest alive ship with C&C

### Auto-Suggestion

**File:** `game/strategy/services/task_group_suggester.py`

`suggest_task_groups(ships)` examines `effective_role` on each ship and groups them:

| Role | Suggested Group | Battle Role |
|------|----------------|-------------|
| line_combatant, assault_ship, command_ship | Battle Line | MAIN_BODY |
| fleet_escort, interceptor | Escort Screen | SCREEN |
| raider, scout | Vanguard | VANGUARD |
| carrier, support_ship | Support Group | RESERVE |

Each group gets default targeting and movement policies matching its role.

### Fleet Hierarchy DTOs

**File:** `game/strategy/facade/dto/fleet_hierarchy_dto.py`

Immutable DTOs for UI display of the fleet hierarchy:

- `TaskForceInfo` — name, battle_role, policies, squadrons tuple, ship counts
- `SquadronInfo` — name, battle_role, policies, spatial_behavior, ship count
- `ShipInfoExtended` — extends ShipInfo with `effective_role`

Factory methods: `TaskForceInfo.from_task_force()`, `SquadronInfo.from_squadron()`,
`ShipInfoExtended.from_ship_instance()`.

### Fleet Delegates

Fleet uses composition with 4 delegates:

#### FleetConsumableAggregator (`fleet.resources`)

**File:** `game/strategy/data/fleet_consumable_aggregator.py`

Handles fleet-wide resource calculations across all combat-capable ships:

- `get_movement_resource_costs()` -- total cost per hex of movement
- `has_resources_for_movement()` -- verify all ships can afford 1 hex
- `consume_movement_resources(hexes)` -- atomic consume (all-or-nothing)
- `get_warp_resource_costs()` / `has_resources_for_warp()` / `consume_warp_resources()`
- `fuel_endurance()` -- minimum hexes before any ship runs dry (-1 = unlimited)
- `warp_jumps_remaining()` -- minimum jumps available (0 = can't warp)
- Cargo: `get_fleet_cargo_capacity()`, `load_cargo_to_fleet()`, `unload_cargo_from_fleet()`

Internal helpers:
- `_accumulate_ship_costs(cost_getter)` -- loop-over-ships accumulation
- `_verify_and_consume_resources(cost_getter, consume, multiplier)` -- atomic verify+consume

#### FleetCapabilityCalculator (`fleet.capabilities`)

**File:** `game/strategy/data/fleet_capability_calculator.py`

Queries about what the fleet can do:

- `has_space_shipyard` / `space_shipyard_count` -- checks for SpaceShipyard ability
- `can_build_type(vehicle_type, galaxy?)` -- ship/fighter/satellite/complex buildability
- `can_use_warp()` -- ALL combat-capable ships must have WarpJump with sufficient tonnage
- `get_warp_limiting_ship()` -- first ship without warp capability
- `has_ability(ability_name)` / `ships_with_ability(ability_name)` -- generic ability checks
- `list_abilities()` -- all unique ability names across fleet

Uses `component_inspector` service for ship-level ability lookups (including
`has_warp_capability()` and `get_ability_list()`).
Requires component registry via DI (constructor or ship's `_registries`).

#### FleetBattleAdapter (`fleet.battle`)

**File:** `game/strategy/data/fleet_battle_adapter.py`

Bridges strategy Fleet with simulation Ship for combat:

- `to_battle_ships(team_id, formation_positions?, registries?)` -- converts
  `ShipInstance` list to simulation `Ship` objects with deployment positions
  (default: Team 0 at x=20000, Team 1 at x=80000, 2000px vertical spacing;
  use `DeploymentZoneCalculator` for hierarchy-aware positioning)

PROJ-269 Phase 6 deleted `update_from_battle_results`. Fleet updates
now flow via `game.strategy.combat.post_battle_hook.apply_outcome_to_fleets`,
which the strategy spec compiler attaches to the `BattleSpec` and
`run_battle` invokes after `extract_outcome`. Callers (the strategy
adapter, `ConflictResolutionEngine`) treat the returned `BattleResult`
as a read-only report.

`to_battle_ships` is still used by `FleetBattleSetupScreen` (manual
battle setup); the strategy adapter's `_make_ship_builder` closure
materializes ships per-`ShipSpec` via `ShipInstance.to_ship` directly.

#### FleetPursuerTracker (`fleet.pursuer_tracker`)

**File:** `game/strategy/data/fleet_pursuer_tracker.py`

Tracks fleets pursuing this fleet via `MOVE_TO_FLEET`/`JOIN_FLEET` orders (PROJ-222):

- `pursuers` -- read-only `FrozenSet` of all pursuing fleets
- `pursuer_count` -- number of active pursuers
- `add_pursuer(fleet)` / `remove_pursuer(fleet)` -- register/unregister
- `redirect_pursuers(new_target, *, exclude=frozenset())` -- on merge, redirect all pursuers to new fleet, returning `(redirected, excluded)`. Pursuers in `exclude` are dropped (BUG-122: prevents self-target cycle when `new_target` is itself a pursuer of the merging fleet). The caller is responsible for emitting `FLEET_JOIN_CANCELLED(reason="self_target_after_redirect")` for each excluded pursuer.
- `notify_target_destroyed()` -- on destruction, cancel all pursuit orders

Not serialized — rebuilt from order targets on load.

#### Mutual-Pursuit Rendezvous Routing (FEAT-28)

**Files:**
- `game/strategy/services/fleet_navigation_service.py` (`_is_mutual_pursuit`, `get_destination`)
- `game/strategy/engine/fleet_movement_engine.py` (`_filter_jump_past_collisions`)

When two fleets are mutually pursuing each other (each fleet's current head order is `MOVE_TO_FLEET` or `JOIN_FLEET` targeting the other), `FleetNavigationService.get_destination` bypasses `calculate_intercept_point` and pathfinds directly to the **target's current hex**. The intercept evaluator is asymmetric for mutual pursuit — it ranks "stay still" (chaser_turns=0 at the chaser's own location) as the best intercept, so one fleet sits while the other chases. Routing both fleets to the other's current hex makes them converge along the shortest line at their own speeds; warp routing falls out for free via the existing `find_hybrid_path`.

The detection predicate `_is_mutual_pursuit(self_fleet, target_fleet)` reads the target's head order directly (the order queue is canonical; the pursuer tracker is a derived index that can lag). `self_fleet` is threaded through `compute_next_step` / `_resolve_path_for_order` from `calculate_fleet_next_hex` and the UI projection path; legacy callers without a Fleet identity pass the default `self_fleet=None` and fall back to today's intercept-based behavior.

**Jump-past safeguard (`_filter_jump_past_collisions` in `FleetMovementEngine.collect_movements`):** when both fleets in a mutual-pursuit pair would swap hexes on the same tick (parity speed at distance 1: A→B's hex, B→A's hex), the **larger fleet** (more ships; smaller `fleet.id` breaks ties — the same election rule used by `OrderProcessor._elect_canonical_merges` for BUG-122) is dropped from the move queue this tick. Next tick they co-locate and `OrderProcessor.process_instant_orders` Phase 1 fires the merge.

v1 covers swap parity only. The broader leapfrog case (e.g. distance 3, both speed 2 → both move 2, they pass through but neither lands on the other's start) is deferred — fleets at distance 3 land 1 hex apart and merge naturally next tick. Speed-balanced rendezvous (where the meet hex shifts toward the slower fleet so both arrive simultaneously) is a follow-up; v1 has each fleet move at its own speed toward the other's then-current location.

### ShipInstance Stat Calculation

**File:** `game/strategy/data/ship_instance.py`

`ShipInstance.get_calculated_stats()` returns a cached stats dict computed by
`calculate_design_stats()` from `game/simulation/entities/ship_design_stats.py`.
This delegates to `Ship.from_dict()` + `recalculate_stats()` — the simulation
layer is the single source of truth for all stats.

**Stats dict keys:** `max_hp`, `mass`, `resource_storage`, `cargo_storage`,
`pod_storage_mass`, `strategic_movement`, `warp_max_tonnage`, `warp_resource_costs`,
`resource_consumption_per_hex`, `resource_consumption_per_turn`.

**Cache invalidation:** Call `ship.invalidate_stats_cache()` after damage, repair,
or component toggle changes. The next `get_calculated_stats()` call recomputes.

**Component toggles:** Toggled-off components are excluded from the design before
Ship creation, so their stats don't contribute. Component damage is applied to
the Ship's components before recalculation.

**Anti-pattern:** Do NOT compute stats by iterating design components manually —
use `get_calculated_stats()` or `calculate_design_stats()`. See Pattern 3 in
`02_PATTERNS.md` ("Unified Stat Calculation") for details.

### Order System (PROJ-238: Unified)

Order types defined in `game/strategy/data/order_types.py`:
- Movement: `MOVE`, `MOVE_TO_FLEET`, `WARP` (fleet-only)
- Actions: `COLONIZE`, `TRANSFER`, `LOAD_POPULATION`, superweapons (fleet)
- Planet actions: `ACTIVATE_ABILITY`, `DEACTIVATE_ABILITY` (planet; generic ability toggles)
- Fleet: `JOIN_FLEET`, `BUILD`

Both Fleet and Planet implement the `IOrderable` protocol (`game/core/protocols/strategy_entities.py`),
providing a unified interface: `orders` list, `get_current_order()`, `add_order()`,
`pop_order()`, `clear_orders()`.

The unified `Order` class (renamed from `FleetOrder` in PROJ-238) and `OrderType`
enum are used by both entity types. Import from `game.strategy.data.order_types`.

**Planet orders** are processed by `PlanetActionEngine` (every tick, no speed concept).
**Fleet orders** are processed by `ActionExecutionEngine` (speed-based tick interval).

### Fleet Position Projection

**File:** `game/strategy/services/cargo_transfer_service.py`

`project_fleet_position(fleet)` walks the fleet's order queue and returns the
hex where the fleet will be after all queued MOVE/WARP orders execute. Returns
`fleet.location` if no movement orders are queued.

Used by:
- `CargoTransferService.resolve_colonies()` — fallback when no colonies at primary hex
  or fleet location; checks projected destination
- `TransferDialog._populate_initial_data()` — finds colonies at projected position
  for transfer orders queued after MOVE orders
- `StrategyRenderer._draw_move_preview()` — draws preview line from projected position
  (handles MOVE→WARP chains, not just the last MOVE target)

### Planet Energy System (PROJ-237/238)

**File:** `game/strategy/engine/planet_energy_engine.py`

Each planet tracks an energy pool fed by `StrategicResourceGeneration` abilities
and bounded by `ResourceStorage` abilities (both scanned from facility components
via registry lookup). Active planetary shields consume energy per turn.

**Turn processing (100 ticks per turn):**
1. Recalculate capacity from `ResourceStorage` abilities (per resource type)
2. Recalculate generation from `StrategicResourceGeneration` abilities
3. Generate: `energy += generation_rate / 100`
4. Consume: if shield active, `energy -= drain_rate / 100`
5. Auto-deactivate shield if energy depleted
6. Clamp energy to `[0, capacity]`

**Critical:** Uses `get_default_registry_provider()` for ability lookup on facility
components. See Pattern 3 in `02_PATTERNS.md` for the registry lookup requirement.

### Per-Component Activation Architecture

**Source of truth:** `facility.component_states[component_key]` (ComponentActivationState)

Each activatable component on a facility has an independent activation state tracked
by a composite key in format `"LAYER:INDEX:COMP_ID"` (e.g., `"OUTER:0:geologic_stabilizer_sector"`).

**`planet.active_abilities`** is a **derived property** (not a stored field). It scans
all `facility.component_states` for entries with `phase == "active"` and returns a
summary dict `{ability_name: True}`. This means:
- Multiple components with the same ability can be active simultaneously
- No stale state — the property always reflects current component_states
- Not serialized — derived on access from facility.component_states (which IS serialized)

**Component-key flow:**
1. UI identifies `component_key` from `iter_keyed_components(facility.design_data)`
2. `IssuePlanetOrderCommand` carries `component_key` to the handler
3. Handler stores `component_key` in `order.target` dict
4. `PlanetActionEngine._resolve_component_key()` uses it directly (no search needed)
5. `ComponentActivationEngine` ticks the state at `facility.component_states[component_key]`
6. `PlanetEnergyEngine` sums drain rates from all draining component_states entries

**Validator checks at component granularity** when `component_key` is provided —
prevents activating the same component twice, but allows different components with
the same ability name to be activated independently.

**Stabilizer protection requires ACTIVE phase:** `StabilizerRegistry.find_blocking_stabilizer()`
passes `require_active=True` to `find_abilities_in_scope()`, which checks
`facility.get_activation_state(comp_key).is_functionally_active` for each component.
A stabilizer that is installed but not activated provides **no protection**. Only the
`ACTIVE` phase counts — `ACTIVATING` and `DEACTIVATING` do not protect.

**UI abilities panel** (`game/ui/screens/planet_abilities_window.py`) shows one row per
activatable component instance (no dedup by ability name). When multiple instances of
the same ability exist, they get numbered labels (e.g., "Geologic Stabilizer (Facility #1)").

The abilities panel also provides **environment editor buttons** at the top for setting
planet modification targets. Buttons are shown conditionally based on facility presence:
- **Atmosphere** — shown when planet has `AtmosphereModifier` facility
- **Gravity** — shown when planet has `GravityModifier` facility
- **Water** — shown when planet has `WaterModifier` facility
- **Radiation** — shown when planet has `RadiationShield` facility

Each button opens the corresponding target editor window. The editors open via a callback
from `strategy_window_manager.py` which delegates to the event router's `_open_*_editor()`
methods. The standalone atmosphere button was removed from the strategy detail panel —
all environment editors are now accessed exclusively through the abilities window.

**Species selector for multi-species planets:** All 4 editors include a dropdown
(from `game/ui/screens/species_selector_mixin.py`) when the planet has multiple species
populations. The dropdown lists species sorted by population count; "Species Ideal"
uses the selected species' preferences from `RaceConfig`. Single-species planets show
no dropdown.

### System & Sector Effects Display

**File:** `game/strategy/services/system_effects_collector.py`

Effects are split between two UI panels based on scope:
- **System effects** → shown in the **System panel** (top) — affects all hexes in the star system
- **Sector effects** → shown in the **Sector panel** (middle) — affects a single hex only

**Scope sets:**
- `_SYSTEM_SCOPES`: `system`, `allied_system`, `player_system`, `enemy_system`
- `_SECTOR_SCOPES`: `sector`, `allied_sector`, `player_sector`, `enemy_sector`

**Functions:**
- `collect_system_effects(system, empire_id, registries)` — scans all colonies in the
  system, returns effects with system-level scopes only
- `collect_sector_effects(system, hex_coord, empire_id, registries)` — scans colonies
  at the specific hex, returns effects with sector-level scopes only
- Both delegate to `_collect_effects(planets, empire_id, registries, allowed_scopes)` —
  shared scanning/aggregation logic

**Supported ability types** (in `SYSTEM_EFFECT_ABILITIES`): GeologicStabilizer,
StellarStabilizer, WarpFieldStabilizer, ResourceHarvestBooster, BuildRateBooster,
QualityImprovement, ShieldModifier, DamageModifier.

**Two categories:**
- **Activatable** (have activation_time): status from ComponentActivationState
  (Active/Inactive/Activating N/Deactivating N)
- **Passive** (no activation_time): always "Active" when facility is operational

**Aggregation:** Values use two-phase stacking (intra-group MAX, inter-group MULTIPLY)
via `aggregate_multipliers()` from `strategic_ability_scanner.py`.

**UI rendering:** `SystemTreePanel` uses shared `_add_effects_group()` to render
collapsible effect groups. `_add_system_effects()` calls it for the system panel;
`_add_sector_effects()` calls it for the sector panel. Each effect type is a group
header with aggregate status and value. Expanding shows individual provider facilities.

### Atmosphere Modification Pipeline

**Files:**
- `game/strategy/engine/atmosphere_engine.py` -- per-turn atmosphere processing
- `game/strategy/engine/commands.py` -- `SetAtmosphereTargetCommand`
- `game/strategy/engine/planet_command_handlers.py` -- `SetAtmosphereTargetCommandHandler`
- `game/ui/screens/atmosphere_target_editor.py` -- gas slider UI
- `game/strategy/data/planet.py` -- `atmosphere`, `atmosphere_target`, `surface_pressure` fields

Atmosphere modification is a once-per-turn system that gradually changes a planet's
gas composition toward a player-set target. It runs after the 100-tick loop, alongside
population growth and quality improvement.

**Data model:**
- `planet.atmosphere: Dict[str, float]` -- gas formula (e.g., "O2") to partial pressure (Pa)
- `planet.atmosphere_target: Dict[str, float]` -- target partial pressures per gas
- `planet.surface_pressure: float` -- total atmospheric pressure (sum of all partial pressures)

**Command flow:**
1. Player opens Atmosphere Target Editor from planet detail (button shown only if planet has operational `AtmosphereModifier` facility)
2. Editor provides sliders for 10 gases (N2, O2, CO2, H2O, CH4, H2, He, Ar, NH3, SO2), range 0-150 kPa
3. Presets: "Species Ideal" (reads `race_config.preferences["gas.<formula>"].setpoint` for each gas — PROJ-283), "Match Current", "Clear Target"
4. "Apply" dispatches `SetAtmosphereTargetCommand(planet_id, atmosphere_target)` via facade
5. Handler validates ownership, sets `planet.atmosphere_target` (empty dict clears target)

**Per-turn processing algorithm** (`AtmosphereEngine.process_atmosphere()`):
1. For each empire's colony, check if `atmosphere_target` is set
2. Sum `modification_rate` (kg/turn) from all operational facilities with `AtmosphereModifier`
3. Convert between mass and pressure using planet physics: `Pa_per_kg = gravity / surface_area`
4. Calculate delta (target - current) for each gas, convert to mass
5. Distribute available modification rate proportionally across gases by mass delta
6. Apply changes without overshooting target values
7. Update `surface_pressure` as sum of all partial pressures

**Physics notes:**
- Small planets change atmosphere faster than large planets (less mass per Pa)
- Earth-like planet at default rate (7.8e15 kg/turn): ~150 Pa/turn, ~1000 turns to reach 150 kPa
- Multiple facilities stack additively

**Related:** `AtmosphereModifier` ability in [ability_reference.md](ability_reference.md#atmospheremodifier); race gas preferences in [§7 Race Preferences & Habitability](#7-race-preferences--habitability-proj-283) — gas factors keyed `gas.O2`, `gas.N2`, ... store partial pressure in Pa directly. `GAS_NAME_TO_FORMULA` / `GAS_FORMULA_TO_NAME` constants in `race_config.py` are kept for the few legacy display-name → formula translations that still exist in the UI layer (PROJ-283 Phase 4 dropped most callers).

### Water Modification Pipeline

**File:** `game/strategy/engine/water_engine.py`

Same pattern as AtmosphereEngine but simpler — a single float (`surface_water`) instead of a gas dict. Runs once per turn after the 100-tick loop.

- Target: `planet.water_target` (0.0-1.0, None = no modification)
- Rate: sum of `modification_rate` from operational `WaterModifier` facilities
- Change: moves `surface_water` toward target, clamped to [0.0, 1.0], no overshoot
- Permanent: changes persist even if facility removed

### Planet Modifier Effect Engine

**File:** `game/strategy/engine/planet_modifier_effect_engine.py`

Handles instant-apply/revert for activatable planet modifiers (GravityModifier, RadiationShield). Runs once per tick as Phase 1.8 after ComponentActivationEngine:

- **GravityModifier:** When ACTIVE + `gravity_target` set, stores original in `gravity_original` and overrides `surface_gravity`. Reverts when INACTIVE or facility destroyed.
- **RadiationShield:** When ACTIVE + `radiation_shielding_target` set, applies to `radiation_shielding`. Reverts to 0.0 when INACTIVE or facility destroyed.
- **Habitability:** `score_planet_for_race()` and the underlying registry-driven `calculate_habitability()` (PROJ-283 — see [§7 Race Preferences & Habitability](#7-race-preferences--habitability-proj-283)) read `surface_gravity`, `surface_water`, `radiation_shielding`, `magnetic_field`, etc. directly via the per-factor extractors in `FACTOR_REGISTRY`. After PROJ-283, `radiation` and `magnetic` are independent factors (v1 had merged them as `magnetic_field + radiation_shielding`); a `RadiationShield` facility now pulls the `radiation` factor's score up directly without touching the `magnetic` factor's score.

### Strategic-to-Combat Bridge

**File:** `game/strategy/services/combat_modifier_collector.py`

Collects strategic combat modifiers (ShieldModifier, DamageModifier, scoped ShieldProjection) for fleets entering combat. Returns `FleetCombatModifiers(shield_mult, damage_mult, flat_shield_bonus)`. **Scope routing (PROJ-271):** enemy-scope (`enemy_sector` / `enemy_system`) effects are pre-computed INTO the RECEIVING fleet's `FleetCombatModifiers` before the strategy spec compiler runs. The compiler therefore emits each entry to `per_team[receiver_id]` trivially, with no runtime scope lookup. New enemy-scope abilities must extend the collector, not the compiler.

Passed into `SimulationBattleResolver.resolve_battle(fleets,
modifiers={team_id: FleetCombatModifiers}, environmental_effects=...)`
(PROJ-275 Phase 7: signature widened from the legacy `(fleet1, fleet2,
team0_modifiers, team1_modifiers)` form to a single `fleets` sequence
plus a `modifiers` mapping, enabling native N-team calls).

PROJ-269 Phase 6 + PROJ-270 Phase 6 changed how these effects flow
into the engine:

- Pre-PROJ-269: the resolver mutated ship attributes directly
  (`_apply_shield_interference` raised `ship.max_shields *= mult`,
  `_apply_strategic_modifiers` set `ship.damage_output_mult`, etc.) BEFORE
  handing ships to the engine.
- Post-PROJ-269 Phase 6: the resolver passes `environmental_effects` and
  a per-team modifier mapping into `build_strategy_battle_spec`, which
  translates each into `ModifierEntry` records on the spec's
  `ModifierStack`. PROJ-269 Phase 5.5 initially emitted these as
  `stat_key="placeholder"` — recorded in the forensic trace but with
  NO effect on battle math (a real gameplay regression).
- **Post-PROJ-270 Phase 6 Track A + PROJ-271 Track B:** the strategy compiler emits
  REAL stat_keys for all modifier sources: storm `shield_capacity_mult` →
  `StatKey.SHIELD_CAPACITY_MULT`; fleet `shield_mult` →
  `StatKey.SHIELD_CAPACITY_MULT`; fleet `damage_mult` → `StatKey.DAMAGE_MULT`;
  fleet `flat_shield_bonus` → `StatKey.SHIELD_BONUS_ADD` (additive, ship-level).
  Enemy-scope suppressors are pre-computed into the RECEIVER fleet's
  `FleetCombatModifiers` by `CombatModifierCollector` before compile, so
  routing at compile time is trivial. `FleetAuraManager._recalculate`
  applies entries to `ship.external_stats` and respects `stack_group`
  (same-group MAX, different-group SUM). PROJ-271 Phase 9 deleted the
  dead-with-landmine `_entries_from_modifier_source` placeholder path.

All `find_abilities_in_scope()` calls use `require_active=True` — only abilities in the
ACTIVE activation phase contribute to combat modifiers. Inactive or activating abilities
have no effect. This means planetary complex ShieldModifier/DamageModifier/ShieldProjection
must be manually activated before they affect combat.

Wired from `ConflictResolutionEngine._resolve_combat_at_hex()` which
collects per-team modifiers for every participating fleet (allied
boosters from the fleet's own empire, enemy suppressors from all
opposing empires' facilities) and passes the full `{team_id: modifiers}`
mapping to `IBattleResolver.resolve_battle(fleets, modifiers, ...)` as a
single N-team call. PROJ-275 collapsed the legacy sequential 2-fleet
decomposition into one N-team battle per contested hex.

#### Battle Setup Complex-Toggle Compilation (PROJ-271 Phase 2)

The Battle Setup screen lets users toggle complex designs onto either side without those complexes being real ships in the battle. `game/ui/screens/battle_setup/spec_compiler.py::_complex_to_entries` translates a toggled complex design into `ModifierEntry` entries by walking the design JSON's components and delegating each non-SELF-scoped ability to `emit_entries_for_ability` from the shared registry. Currently-mapped abilities:

| Ability class in complex design | Emitted stat_key | Operation |
|---------------------------------|------------------|-----------|
| `ShieldProjection` | `shield_bonus_add` | add |
| `ShieldModifier` | `shield_capacity_mult` | multiply |
| `DamageModifier` | `damage_mult` | multiply |

Routing is handled inside `emit_entries_for_ability` via the shared `OPPONENT_SCOPES` constant (`{"enemy_sector", "enemy_system"}` in `game/simulation/combat/ability_stat_registry.py`). Enemy scopes fan out to all non-owner teams (N-team forward-compat); other scopes route to the owner's team. Adding a new combat-affecting ability is now a one-line edit to `ABILITY_STAT_REGISTRY` in the registry module — the glob-driven test in `tests/unit/simulation/combat/test_ability_stat_registry.py` picks up new `qs_*_complex.json` designs automatically. Adding a new enemy-scope value requires extending `OPPONENT_SCOPES` AND adding a scope-routing test.

Unlike the strategy path (where `CombatModifierCollector` pre-computes enemy-scope routing before compile), the Battle Setup compiler does per-ability scope routing at compile time because complex toggles are synthetic inputs — there's no `CombatModifierCollector` equivalent for Battle Setup. Both paths share the same `ABILITY_STAT_REGISTRY` / `emit_entries_for_ability` entry-emission code since PROJ-273.

### Activatable Abilities & Stabilizer Pattern

**Files:**
- `game/strategy/engine/component_activation_engine.py` -- tick-based activation state machine
- `game/strategy/engine/planet_energy_engine.py` -- energy drain for active abilities
- `game/strategy/services/strategic_ability_scanner.py` -- scope-based ability discovery
- `game/strategy/engine/superweapon_order_processor.py` -- stabilizer protection checks
- `game/ui/screens/planet_abilities_window.py` -- activation toggle UI

Some strategic abilities require manual activation, consume energy while active, and
take multiple ticks to transition between states. These share a common architecture.

**Activation state machine** (`ComponentActivationEngine`):

```
INACTIVE --[activate order]--> ACTIVATING --[N ticks]--> ACTIVE
ACTIVE   --[deactivate order]--> DEACTIVATING --[N ticks]--> INACTIVE
```

- State tracked per component instance in `facility.component_states[component_key]`
- `component_key` format: `"LAYER:INDEX:COMP_ID"` (e.g., `"CORE:0:stellar_stabilizer"`)
- Each tick, `ComponentActivationEngine` increments `progress_ticks` for ACTIVATING/DEACTIVATING components
- Transition to ACTIVE/INACTIVE when `progress_ticks >= required_ticks`
- ACTIVATING and DEACTIVATING phases provide **no protection** -- only ACTIVE counts

**Energy system integration:**
- `PlanetEnergyEngine` sums `energy_drain_rate / 100` per tick from all ACTIVE draining components
- If energy depletes, active abilities auto-deactivate
- Energy generation comes from `StrategicResourceGeneration` abilities, storage from `ResourceStorage`

**Current activatable abilities:**

| Ability | Blocks | Default Scope | Activation | Deactivation | Energy Drain |
|---------|--------|---------------|------------|--------------|--------------|
| `PlanetaryShield` | Planet bombardment | system | varies | varies | varies |
| `GeologicStabilizer` | IMPLODE_PLANET | planet/sector/system | varies | varies | varies |
| `StellarStabilizer` | STELLERATE_STAR, CREATE_DYSON_SPHERE | system | 250 ticks | 150 ticks | 250/turn |
| `WarpFieldStabilizer` | OPEN_WARP_POINT, CLOSE_WARP_POINT | system | 250 ticks | 150 ticks | 150/turn |
| `GravityModifier` | — (modifies planet gravity) | self | 15 ticks | 5 ticks | 30/turn |
| `RadiationShield` | — (adds radiation shielding) | self | 15 ticks | 5 ticks | 20/turn |
| `ShieldModifier` | — (modifies fleet shields in combat) | varies | 15-25 ticks | 5-10 ticks | 30-50/turn |
| `DamageModifier` | — (modifies fleet damage in combat) | varies | 15-25 ticks | 5-10 ticks | 30-50/turn |
| `ShieldProjection` | — (adds flat shields in combat) | varies | 15-25 ticks | 5-10 ticks | 30-50/turn |

The list of activatable ability keys is maintained in `planet_energy_engine.py:_ACTIVATABLE_ABILITIES`.

**Stabilizer protection pattern (PROJ-277):**

Stabilizers are data-driven via `game/strategy/services/stabilizer_registry.py`.
Each `StabilizerSpec` declares `ability_name`, `scopes`, and the tuple of
`OrderType`s it blocks. Adding a new stabilizer or extending an existing
one to cover a new superweapon is a single edit to the `STABILIZERS` tuple.

```
STABILIZERS = (
    StabilizerSpec("GeologicStabilizer", ("planet", "sector", "system"), (OrderType.IMPLODE_PLANET,)),
    StabilizerSpec("StellarStabilizer",  ("sector", "system"), (OrderType.STELLERATE_STAR, OrderType.CREATE_DYSON_SPHERE)),
    StabilizerSpec("WarpFieldStabilizer",("sector", "system"), (OrderType.OPEN_WARP_POINT, OrderType.CLOSE_WARP_POINT)),
)
```

Check flow:

1. Superweapon handler calls `self._check_blocking_stabilizer(order_type, ref_planet, galaxy, empires, component_registry)`.
2. That delegates to `stabilizer_registry.find_blocking_stabilizer(...)`.
3. For every spec whose `blocks` tuple contains `order_type`, the registry calls `find_abilities_in_scope(require_active=True)` across each scope, threading `component_registry` (**required** — see below).
4. First ACTIVE hit returns the `StabilizerSpec`; the handler cancels the order and reports the blocker's `ability_name`.

**`component_registry` MUST be threaded through every superweapon handler.**
Real facility `design_data` stores bare component IDs
(`{"id": "stellar_stabilizer", "modifiers": [...]}`) — the ability payload
lives in the component registry, not inline on the design. The scanner's
`_extract_ability` delegates to `component_inspector.extract_abilities_from_component`,
which accepts either a `GameRegistries` or a plain components dict.
Without a registry, the scanner returns nothing and every stabilizer is
silently ineffective (this was the PROJ-277 regression — the UI's
`system_effects_collector` DID thread the registry, which is why the
"Active" status was displayed correctly while the actual block never
fired). The integration test
`tests/integration/strategy/test_stabilizer_blocks_superweapon.py::test_without_component_registry_no_stabilizer_found`
guards against regression.

**Scope resolution** (`strategic_ability_scanner.py`):
- `find_abilities_in_scope()` accepts `require_active=True` to filter to ACTIVE phase only
- SYSTEM scope: all empire-owned planets in the star system
- SECTOR scope: all planets in the same hex
- Returns ability data dicts with scope metadata for aggregation

**System destruction pattern (PROJ-277):**

Superweapons that tear down an entire star system (STELLERATE_STAR)
route through `game/strategy/services/system_destroyer.py`, which uses a
**collect-then-mutate** protocol:

1. `collect_system_contents(system, galaxy, empires)` returns an immutable
   `SystemDestructionPlan` listing every planet, star, and fleet the
   operation will remove. Fleet membership is determined by hex distance
   (any fleet within `SYSTEM_RADIUS_HEXES = 50` of the system's
   `global_location` is included) — this is strictly broader than
   `GalaxySpatialIndex.get_all_fleets_in_system`, which only saw hexes
   containing a placed entity (planet/star/warp point).
2. `destroy_system(plan, galaxy, empires)` executes the removals against
   the snapshot. Because the plan is local, it doesn't matter what order
   mutations happen in — the old "remove planets, THEN scan planets for
   system hexes" ordering bug can't recur.

Adding a new system-destroying superweapon = call `collect_system_contents`
then `destroy_system`. Do not hand-roll fleet enumeration.

**Adding a new activatable ability:**
1. Define ability class in `planetary.py` with `energy_drain_rate`, `activation_time`, `deactivation_time`, `scope` parameters
2. Register in `ABILITY_REGISTRY` (`abilities/__init__.py`)
3. Add to `_ACTIVATABLE_ABILITIES` list in `planet_energy_engine.py`
4. PROJ-351A T6.4: discovery for the abilities window is now data-driven. Any ability whose component data carries an `activation_time` field is automatically picked up by `PlanetAbilitiesController.scan_abilities()` (`game/ui/screens/planet_abilities_controller.py:128-183`). No registration in a hardcoded ability list is required. Display name humanizes from CamelCase by default; if the natural humanization doesn't match the established UI label, add an entry to `ABILITY_DISPLAY_NAME_OVERRIDES` (`planet_abilities_controller.py:45-47`).
5. Add display name to `_ACTIVATABLE_DISPLAY_NAMES` in `strategy_detail_fmt.py` (this list is independent of the abilities-window scanner; PROJ-351A T6.4 did not migrate this surface).
6. If it blocks superweapons: add a `StabilizerSpec` entry to the `STABILIZERS` tuple in `game/strategy/services/stabilizer_registry.py`. No code changes in `superweapon_order_processor.py` are needed — existing handlers route through `StabilizerRegistry` automatically.
7. Add to `SYSTEM_EFFECT_ABILITIES` in `system_effects_collector.py` if system or sector scope — system-scoped abilities show in the System panel via `_SYSTEM_SCOPES`, sector-scoped abilities show in the Sector panel via `_SECTOR_SCOPES`
8. If it affects combat: add to `combat_modifier_collector.py` with `require_active=True`
9. Add keyboard toggle binding in `strategy_fleet_command_router.py`
10. Create component in `components.json` with `energy_drain_rate`, `activation_time`, `deactivation_time` in the ability data — `activation_time` IS LOAD-BEARING for abilities-window discovery (see step 4)
11. Create QS complex design in `data/designs/` with `design_role` field
12. Write tests in `tests/unit/simulation/components/abilities/` and `tests/unit/strategy/engine/`
13. Update `docs/systems/ability_reference.md` and `docs/systems/strategy_layer.md` activatable abilities table

**Adding a new environment editor (planet-modifier ability with its own editor window):**
1. Add the editor window class (follow `gravity_target_editor.py` + `species_selector_mixin`)
2. Add `(ability_key, label)` entry to `ENVIRONMENT_EDITORS` in `game/ui/screens/planet_abilities_controller.py:54-59`. This is an intentional UI editor-routing list — NOT a behavior gate per ability, but a closed list of which environment domains have dedicated editors. Adding a 5th env editor is the natural trigger to evaluate replacing this list with a registry/data-driven mechanism.
3. Add an `_open_*_editor()` method to `strategy_event_router.py`
4. Wire the editor in `strategy_window_manager.py:_open_planet_editor()`

### Build Queue Source DI

**File:** `game/strategy/data/build_queue_source.py`

Functions that collect build queue sources accept an optional `registries` parameter
(GameRegistries) threaded via DI from callers. This replaces the former pattern of
calling `get_default_registry_provider()` internally with an adapter shim.

```python
collect_build_queues_at_hex(hex_coord, galaxy, empire, registries=None)
collect_all_build_queues_for_empire(empire, registries=None)
_collect_planet_sources(planet, sources, galaxy, empire, registries=None)
```

Callers pass `session.registries`:
- `BuildQueueScreen` passes `self.session.registries`
- `EmpireBuildQueueWindow` passes `session.registries`
- `StrategyDetailFormatter` passes `self.scene.session.registries`

`colony_has_planetary_yard(colony, registries)` requires `GameRegistries` for
registry-based ability lookup (design JSONs don't store abilities inline).

### Strategy UI Widget Architecture

**File:** `game/ui/screens/strategy_ui.py`

`StrategyUI` stores the `StrategyWidgets` dataclass directly and delegates attribute
access via `__getattr__`. This eliminates manual button unpacking — new buttons added
to `StrategyWidgets` are automatically accessible on `StrategyUI` without code changes.

```python
self._widgets = widgets  # StrategyWidgets dataclass from create_strategy_panels()

def __getattr__(self, name):
    widgets = self.__dict__.get('_widgets')
    if widgets is not None and hasattr(widgets, name):
        return getattr(widgets, name)
    raise AttributeError(...)
```

`StrategyDetailFormatter` uses the same pattern — accepts `StrategyWidgets` directly
and delegates lookups via `__getattr__` instead of a manually-curated widget dict.

---

## 5. Event System

**Files:**
- `game/strategy/events/event_types.py` -- enums
- `game/strategy/events/event_log.py` -- Event dataclass + EventLog collection

### EventType Enum

```
SHIP_BUILT, COMPLEX_BUILT, COLONY_FOUNDED, COMBAT_RESOLVED,
PLANET_DESTROYED, STAR_DESTROYED, WARP_POINT_OPENED, WARP_POINT_CLOSED,
DYSON_SPHERE_CREATED, SHIPS_SELF_DESTRUCTED, RESOURCE_SHORTAGE,
FLEET_JOINED, FLEET_JOIN_REDIRECTED, FLEET_JOIN_CANCELLED,
SHIELD_ACTIVATED, SHIELD_DEACTIVATED, SHIELD_AUTO_DEACTIVATED
```

### EventCategory Enum

```
PRODUCTION, COLONIES, COMBAT, SUPERWEAPONS, FLEET_OPERATIONS, PLANET_OPERATIONS, ALL
```

### Event Dataclass

```python
@dataclass
class Event:
    event_type: str       # EventType value
    category: str         # EventCategory value
    turn: int             # Turn number when event occurred
    empire_id: int        # Empire that owns/triggered the event
    message: str          # Human-readable description
    details: Dict[str, Any]  # Structured data specific to event type
```

Serializable via `to_dict()` / `from_dict()`.

### EventLog Collection

- `append(event)` -- add event
- `get_events_for_turn(turn, *, empire_id=None)` -- filter by turn number; optional empire scope (BUG-123)
- `get_events_by_category(category, *, empire_id=None)` -- filter by category (ALL returns everything); optional empire scope (BUG-123)
- `get_all_events()` -- return all events (unscoped; UI consumers should use `get_events_for_empire` instead)
- `get_events_for_empire(empire_id, *, include_global=True)` -- BUG-123: empire-scoped query for the Event Log UI
- Serializable via `to_dict()` / `from_dict()`

Events are created by sub-engines during turn processing and surfaced to the UI
via `StrategySessionFacade.get_turn_events()` (returns dicts, not domain objects).

**Shield events** (SHIELD_ACTIVATED, SHIELD_DEACTIVATED, SHIELD_AUTO_DEACTIVATED) are
generated by `PlanetActionEngine` (activation/deactivation) and `PlanetEnergyEngine`
(auto-deactivation on energy depletion). Both engines accept an `event_bus` parameter
wired by `TurnEngine`'s lazy init.

### Per-Empire Event Log Scoping (BUG-123)

In hot-seat / multi-empire play, the Event Log filters to the active
empire. `Event.empire_id` is set at emission for every event (the
default `-1` sentinel is treated as "broadcast to all empires" — used
for environmental hazards / star destruction / other galaxy-wide
events without a single owner).

**UI scoping convention** (matches `StrategyBuildQueueManager`,
`StrategyDetailFormatter`): UI consumers read
`scene.current_empire.id` (a property on `StrategyScreen` that
recomputes from `current_player_index` each access — the active
turn-taker, not the original session creator). Server-side
authorization gates use `session.active_empire.id`; UI scoping
gates use `scene.current_empire.id`. Both refer to the same empire
during normal play but the UI accessor is preferred from UI code
because it never caches.

**Filter sentinel:** `EventLog.get_events_for_empire(empire_id, *,
include_global=True)`. With `include_global=True` (the default),
events carrying `empire_id == -1` are visible to every empire.
Setting `include_global=False` hides them — useful for spectator /
debug views that want strict per-empire isolation.

**Wiring:**
- `EventLogRegistrar.open_all` reads `c.scene.current_empire.id` and
  passes it through `facade.get_all_events(empire_id=...)`.
- `StrategyGameStateManager.process_full_turn` reads
  `current_empire.id` and threads it into `get_turn_events(turn=...,
  empire_id=...)`. The per-turn auto-popup is suppressed when the
  active empire produced zero events that turn (consistent with
  "each player only sees their own log").
- `EventLogWindow` accepts an optional `empire_name: str | None`
  kwarg; when present the window title becomes
  `"Event Log — <name> Empire"` so the player can verify the filter
  is active. Forwarders on `StrategyUI.open_event_log_with_events`
  and `StrategyWindowManager.open_event_log_with_events` thread the
  kwarg through.

### Replay Persistence — `ReplayStore` + `ReplayResolver` (PROJ-312)

The strategy layer owns the persistence and lookup half of the replay
system; the simulation half (capture sink protocol, JSON-safe DTOs,
playback engine) lives under `game/simulation/replay/` and is documented
in [combat_simulation.md § 11 Replay Capture & Playback](combat_simulation.md).

**`ReplayStore`** — `game/strategy/services/replay_store.py`

Implements the simulation-side `IReplayCaptureSink` protocol so it can
receive `on_battle_started(replay_spec, context) → replay_id` and
`on_battle_ended(replay_id, outcome)` callbacks during a battle. Persists
each completed battle as a JSON sidecar at
`output/saves/<save>/replays/replay_<uuid>.json`.

| Concern | Behaviour |
|---------|-----------|
| Storage layout | One sidecar JSON per battle, named by replay UUID, scoped to the active save folder. |
| Atomic writes | Uses `save_json()` (`game/core/json_utils.py`) — temp-file + `os.replace`. Same atomic guarantee as the rest of the project. |
| Capacity policy | Ring-buffer eviction: write-then-evict (the new replay is always persisted; oldest sidecars are pruned afterwards). Cap is loaded from `output/replay_settings.json` via `load_replay_settings()`; default 50 replays per save. |
| Active-save coupling | `set_save_root(path)` / `clear_save_root()` move the store's persistence target. `SaveGameService.save_game()` and `.load_game()` notify the store via `_notify_replay_store_save_or_load()` so the replay folder always pairs with the active save. |
| Settings | `ReplaySettings` (`replay_store.py:57`) captures the replay cap; missing settings file → defaults silently. |
| Pending-capture bookkeeping | `_PendingCapture` (line 94) tracks in-flight battles between `on_battle_started` and `on_battle_ended` so a battle that never ends does not leak a half-written sidecar. |

**`ReplayResolver`** — `game/strategy/services/replay_resolver.py`

Read-side wrapper around `ReplayStore.load(replay_id)` that gives the UI
a single call (`resolve(replay_id) → ReplayLookup`) and absorbs every
failure mode without raising. Five outcomes:

| `ReplayLookup` shape | Meaning | UI action |
|----------------------|---------|-----------|
| `found=False, reason="missing"` | Sidecar not on disk. | Disabled button + tooltip. |
| `found=False, reason="corrupt"` | JSON parse failed. | Disabled button + tooltip; resolver does **not** delete the file. |
| `found=False, reason="version_drift"` | `REPLAY_SCHEMA_VERSION` mismatch. | Disabled button + tooltip. |
| `found=True, registry_drift=True` | Components-registry hash mismatch (data files moved since capture). | Confirmation dialog warning the player that components have changed; on Continue, launch. |
| `found=True, registry_drift=False` | Healthy. | Direct launch. |

The resolver never raises on bad input — every error path returns a
`ReplayLookup`. This is the contract that lets the Event Log button
state be a pure function of resolver result without try/except in the
UI.

**Tests:**
- `tests/unit/strategy/test_replay_store.py` — round-trip persistence,
  ring-buffer eviction, settings fallback, atomic-write semantics.
- `tests/unit/strategy/test_replay_resolver.py` — every degradation
  state.
- Integration end-to-end through `tests/integration/strategy/test_event_log_replay_e2e.py`.

### Background Verification Sidecars (PROJ-354B + PROJ-366)

Each persisted `replay_<uuid>.json` is paired with a verification
sidecar `replay_<uuid>.verification.json` once the
`ReplayVerificationCoordinator` (subscribed to the store via
`add_on_record_persisted_listener` at bootstrap) has finished
processing the record. The sidecar carries the verification status
(`PASSED`/`FAILED`/`ERROR`/`SKIPPED_DISABLED`/`SKIPPED_QUEUE_FULL`),
duration, an optional diff for `FAILED` cases, and an optional
diagnostic for `ERROR` cases. Schema lives in
`game/strategy/services/replay_verification_sidecar.py`.

**Sidecar lifecycle:**
- Written by the coordinator after a record is persisted (post-write,
  pre-eviction). Atomic write via `save_json()`.
- Deleted by `ReplayStore.delete(replay_id)` and by ring-buffer
  eviction so a sidecar can never outlive its replay record.

**Listener API:**
- `ReplayStore.add_on_record_persisted_listener(callback)` — register
  a `Callable[[ReplayRecord, Path], None]`. Idempotent. Listeners run
  AFTER atomic write succeeds and BEFORE ring-buffer eviction.
- `ReplayStore.remove_on_record_persisted_listener(callback)` —
  tolerant to unknown callables.
- Listener exceptions are caught and logged so one bad subscriber
  cannot block others or cause `persist()` to fail.

**`ReplayResolver.resolve(replay_id)` `verification_status` field:**
extends `ReplayLookup` with a verification status string. The UI can
read this to surface a per-row badge ("PASSED" / "FAILED" / "ERROR" /
"SKIPPED" / unknown) without a second resolver call.

**Production wiring (PROJ-366):** `game/app_bootstrap.py` constructs
the `ReplayVerificationCoordinator` with the production
`AIControllerFactory` + `get_default_registry_provider()` + shared
`replay_settings` + Combat Lab fallback adapter, then calls
`coordinator.start()`. `RunLoop.run()` calls
`shutdown_all_coordinators(timeout=5.0)` between
`shutdown_all_calls(timeout=5.0)` and `pygame.quit()`. See
[combat_simulation.md § 11 Background Verification](combat_simulation.md)
for the full pipeline, sidecar schema, no-recursion guarantee, and
test inventory. See `Projects/active_projects/PROJ-354B/` and
`Projects/active_projects/PROJ-366/` for full design context.

### Replay Wiring (FEAT-26)

Strategy-layer combat events carry a `replay_id: Optional[str]`
field in `Event.details["replay_id"]`. The UI surfaces a Replay
button on each combat-category row of the Event Log (the new
`replay_action` single-button column type added to `VirtualTable`,
visible by default; non-combat rows render the cell empty/disabled).

**Capture flow** (full plumbing path documented in
`docs/systems/combat_simulation.md`):

```
SimulationBattleResolver.resolve_battle(...)
    → run_battle(spec, capture_context=...)
    → BattleOutcome.replay_id        ← extract_outcome reads engine.replay_id
    → BattleResult.replay_id         ← populated for simulator + truncated
    → BattleResult.replay_unavailable_reason ← issue #8: tooltip key for shortcuts
    → ConflictResolutionEngine._log_combat_result(replay_id=...,
        replay_unavailable_reason=...)
    → COMBAT_RESOLVED.details["replay_id" / "replay_unavailable_reason"]
```

Issue #8 (2026-05-02): the legacy `shortcut_no_capable` branch — both
fleets have ships but no team has weapons — now runs the simulator at
the truncated `_BRIEF_RUN_TICK_BUDGET` (2 000 ticks) so a real (brief)
replay is captured. Only `sole_survivor` (one team starts with 0 ships)
and the defensive `no_ships` (both fleets empty) keep the shortcut;
those events ship `replay_unavailable_reason="sole_survivor"` /
`"no_ships"` so the disabled Replay button shows an honest tooltip
instead of the generic "older save." wording reserved for legacy
saves.

`Event.details=kwargs` carries both fields through saves with no
schema change. Older saves without the keys resolve to `None` and
the Replay button renders disabled with a "No replay available —
older save" tooltip.

**Click flow:**
1. `EventLogWindow.process_event` detects the action-button press
   via `virtual_table.check_action_button_press(event.ui_element)`.
2. The handler reads the row's `replay_id` from
   `EventLogDataSource.get_cell_replay_id(row_index)`.
3. `ReplayResolver.resolve(replay_id)` returns a `ReplayLookup` with
   graceful-degradation states:
   - `found=True, registry_drift=False` → launch directly.
   - `found=True, registry_drift=True` → modal confirm dialog →
     on Continue → launch.
   - `found=False, reason in {"missing", "corrupt", "version_drift"}`
     → `pygame_gui.windows.UIMessageWindow` with reason text; no
     crash.
4. Launch path: `EventLogRegistrar._on_launch_replay(record)`
   builds `BattleConfig(replay_mode=True, replay_id=...,
   captured_telemetry_level=...)` and dispatches via
   `Game.start_replay(record)` (forwarder on `Game` that owns
   `screen_router`). `screen_router.start_battle(spec, *,
   headless=False, config=None)` accepts the explicit
   `BattleConfig` for replay mode; default callers continue
   building the config inline as before.
5. While replay is active, `BattleScreen` mounts a top-center
   `pygame_gui.elements.UILabel` reading `"REPLAY MODE"`. The
   label is hidden / killed on battle exit.

**Resolver service location:**
`game/strategy/services/replay_resolver.py`. Backed by the
`ReplayStore` per-save sidecar at
`output/saves/<save>/replays/replay_<uuid>.json` (ring-buffered to
50 per save by PROJ-312). The capture/persistence/playback
infrastructure pre-dated FEAT-26; this feature was the UI-side
follow-up explicitly deferred during PROJ-312 Phase 6.

**Out of scope for FEAT-26 (deferred to follow-up tickets):**
- Replay scrubbing / pause / fast-forward / playback-speed.
- A standalone Replay Browser screen.
- Combat Lab + Battle Setup capture (the field exists on every
  `BattleResult` but only strategy-layer battles currently capture
  replays — adding capture to Combat Lab + Battle Setup is a
  loose-acceptance follow-up).

---

## 6. Galaxy Generation

**Files:**
- `game/strategy/data/galaxy.py` -- `Galaxy`, `StarSystem`, `WarpPoint`
- `game/strategy/data/galaxy_system_generator.py` -- `GalaxySystemGenerator`
- `game/strategy/data/galaxy_warp_generator.py` -- `GalaxyWarpGenerator`
- `game/strategy/generation/placement_strategies.py` -- placement algorithms
- `game/strategy/generation/region_classifier.py` -- arm/cluster classification
- `game/strategy/data/stars.py` -- `StarGenerator`, `Star`, `StarType`, `Spectrum`
- `game/strategy/data/planet_gen.py` -- `PlanetGenerator`
- `game/strategy/generation/storm_generator.py` -- `StormGenerator`
- `game/strategy/data/classification_config.py` -- `ClassificationConfig` (planet classification thresholds)
- `game/strategy/data/resource_generation_config.py` -- `ResourceGenerationConfig` (data-driven resource parameters)
- `game/strategy/data/star_generation_config.py` -- `StarGenerationConfig` (star type weights, mass distribution, companion spacing)
- `game/strategy/data/orbital_generation_config.py` -- `OrbitalGenerationConfig` (orbital placement, moon system, surface flags)
- `game/strategy/generation/loaders/astrophysics_loader.py` -- `AstrophysicsLoader` (loads `data/astrophysics.json`)
- `data/astrophysics.json` -- central data file for all generation parameters

### Galaxy Structure

`Galaxy` uses composition with extracted subsystems:
- `GalaxyEntityRegistry` -- planet/fleet ID lookups
- `GalaxySpatialIndex` -- hex-to-system spatial queries
- `GalaxyWarpGenerator` -- warp point creation
- `GalaxySystemGenerator` -- star system placement

`StarSystem` contains:
- `name`, `global_location: HexCoord`, `region_id: Optional[int]`
- `stars: List[Star]`, `planets: List[Planet]`, `warp_points: List[WarpPoint]`
- `storms: List[Storm]`

### Placement Strategies

**Protocol:** `ISystemPlacementStrategy`
- `sample_location(radius, existing_systems, min_dist, rng, max_attempts, spatial_index)`

**Implementations:**

| Strategy | Algorithm |
|----------|-----------|
| `RandomPlacementStrategy` | Uniform random within hex radius, reject if too close |
| `DensityBasedPlacementStrategy` | Rejection sampling weighted by `DensityMap`; higher density = higher acceptance probability |

Both use `SpatialIndex` for O(1) average-case minimum distance checks.

### Density System

Density maps (`game/strategy/generation/density/density_map.py`) define probability
distributions for system placement. The `DensityBasedPlacementStrategy` evaluates
`density_map.evaluate(q, r)` and accepts candidates probabilistically.

### Region Classifier

**File:** `game/strategy/generation/region_classifier.py`

Classifies star systems into named regions based on layout configuration.

`RegionInfo` dataclass: `region_id`, `region_type` (arm/cluster/core/bar/ring), `name`.

`RegionClassifier(layout_config, galaxy_radius)`:
- `classify(coord) -> int` -- assigns region ID to a hex coordinate
- `regions` -- list of all `RegionInfo`
- `get_region_neighbors()` -- adjacency map for connectivity

Layout detection:
- **Spiral:** Classifies by nearest arm using log-spiral math; core region if within sigma threshold
- **Cluster:** Classifies by nearest cluster center (sigma-weighted distance)
- **Ring/Bar:** Simple region assignment

### Generation Pipeline

1. **System placement** -- `GalaxySystemGenerator` uses `ISystemPlacementStrategy` to place N systems
2. **Star generation** -- `StarGenerator` creates stars per system
3. **Planet generation** -- `PlanetGenerator` creates planets with types, atmospheres, resources
4. **Warp point generation** -- `GalaxyWarpGenerator` connects systems via warp points
5. **Storm generation** -- `StormGenerator` places environmental hazards
6. **Region classification** -- `RegionClassifier` assigns region IDs to systems
7. **Planet images** -- `PlanetImageRegistry` assigns visual assets

### Planet Resource Generation

**Files:**
- `game/strategy/data/planet_gen.py` -- `PlanetGenerator._generate_resources(mass, planet_type)`
- `game/strategy/data/resource_generation_config.py` -- `ResourceGenerationConfig`, `get_resource_generation_config()`
- `data/astrophysics.json` -- `resource_generation` section

Resource generation is fully data-driven via `astrophysics.json`. All parameters are loaded through `ResourceGenerationConfig` (follows the `ClassificationConfig` pattern with `@lru_cache` singleton and hardcoded defaults as fallback).

**Parameters (in `astrophysics.json` → `resource_generation`):**
- `mass_scaling` -- log10(kg) bounds for normalizing planet mass to a 0-1 size_factor
- `quantity` -- `earth_mass_baseline` (default 10M), determinism/randomness weights, minimum floor
- `quality` -- max quality (0-100), determinism/randomness weights, minimum floor
- `planet_type_affinities` -- per-planet-type resource multiplier matrix (e.g., MAGMA: Radioactives×2.5, Organics×0.2)

**Resource generation formula:**
1. Compute `size_factor` from log10(mass) normalized to `[min_log_mass, max_log_mass]`
2. Calibrate so Earth-mass yields `earth_mass_baseline` quantity per resource
3. For each resource: `quantity = (size_factor * determinism + random * randomness) * calibration * affinity`
4. Quality inversely correlates: `quality = (1 - size_factor) * determinism + random * randomness`
5. Both have minimum floors to prevent zero values

**Affinity design:** Moderate specialization (1.5-2.5× favored, 0.3-0.8× reduced). Every planet has some of each resource. Thematic mapping:
- Gas giants (JOVIAN, ICE_GIANT) → high Vapors, low Metals
- Volcanic (MAGMA, CHTHONIAN) → high Metals + Radioactives, low Organics
- Ocean/temperate (PELAGIC, CONTINENTAL) → high Organics
- Cold/exotic (CRYOPLANET, ICE_DWARF) → high Vapors + Exotics

### Star Generation Config

**Files:**
- `game/strategy/data/stars.py` -- `StarGenerator._determine_type_and_radius()`, `_generate_mass()`, `_generate_random_stars()`
- `game/strategy/data/star_generation_config.py` -- `StarGenerationConfig`, `get_star_generation_config()`
- `data/astrophysics.json` -- `star_generation` section

Star generation parameters are data-driven via `astrophysics.json`. Follows the same `@lru_cache` singleton + hardcoded defaults pattern as `ClassificationConfig`.

**Parameters (in `astrophysics.json` → `star_generation`):**
- `type_weights` -- probability weights for star type selection (8 types, sum to ~1.0)
- `mass_generation` -- log-normal distribution parameters (sigma, min/max mass, max attempts)
- `system_probabilities` -- multi-star system count thresholds, age generation range
- `companion_spacing` -- companion star hex placement (ring multiplier, jitter, collision limit)

Stefan-Boltzmann types (RED_GIANT, BROWN_DWARF, WHITE_DWARF) share a common luminosity formula and are parameterized in `DEFAULT_STEFAN_BOLTZMANN_TYPES` with per-type mass adjustment, radius, temperature range, and fixed color.

### Orbital Generation Config

**Files:**
- `game/strategy/data/planet_gen.py` -- `PlanetGenerator._generate_orbital_slots()`, `_calculate_moon_chance()`, `_generate_surface_flags()`
- `game/strategy/data/orbital_generation_config.py` -- `OrbitalGenerationConfig`, `get_orbital_generation_config()`
- `data/astrophysics.json` -- `orbital_generation` section

Orbital generation parameters are data-driven via `astrophysics.json`. Follows the same pattern as `ClassificationConfig` and `StarGenerationConfig`.

**Parameters (in `astrophysics.json` → `orbital_generation`):**
- `orbital` -- safe start offset, max orbital distance, planet count range, triangular distribution mode, hot Jupiter forcing parameters
- `mass_generation` -- log-normal mu/sigma per bias type (small, large, default), max iterations
- `moon_system` -- mass threshold log-interpolation (Jupiter/Earth/Ceres breakpoints and chances), moon mass ratio bounds, max moons per body
- `surface` -- tectonic activity and magnetic field ranges per body mass class, water temperature thresholds

### Galaxy Size Contract (FEAT-27)

**Files:**
- `game/strategy/engine/game_config.py` -- `GameConfig`, `DEFAULT_SYSTEM_COUNT`, `MIN_SYSTEM_COUNT`, `MAX_SYSTEM_COUNT`
- `game/strategy/engine/game_initializer.py` -- `GameInitializer.initialize`, `_setup_initial_scenario`, `_empire_home_indices`
- `game/ui/screens/new_game_setup_screen.py` -- `system_count_slider_curve`, `system_count_slider_inverse`

`GameConfig.system_count` is bounded `MIN_SYSTEM_COUNT ≤ N ≤ MAX_SYSTEM_COUNT` (1–150), enforced in `__post_init__`. The dataclass field default is `DEFAULT_SYSTEM_COUNT = 2` and is the **single source of truth** for the new-game default. The New Game Setup UI imports `DEFAULT_SYSTEM_COUNT` rather than hardcoding a value, so changing the constant updates both surfaces.

Two galaxy-size modes:

- **N = 1 (shared-system mode):** every empire colonises the lone star system on a *different* planet. No warp lanes are generated (`GalaxyWarpGenerator.generate_warp_lanes` early-returns at `len(systems) < 2`). The empire-vs-system count check in `__post_init__` is bypassed — `len(players) > 1` at `N = 1` is intentional. If the lone system rolls fewer planets than empires, `GameInitializer.initialize` re-rolls the layout up to 10 times (perturbing `galaxy_seed` by the attempt index via `dataclasses.replace`) before raising `ValidationException`. `Empire.colonies` is cleared between attempts so a partially-applied placement does not persist.
- **N ≥ 2 (separated mode):** every empire owns a *distinct* system. `__post_init__` rejects `len(players) > system_count`. `_setup_initial_scenario` calls `_empire_home_indices(num_empires, num_systems)` which returns a hand-rolled linspace `[round(i * (N-1) / (E-1)) for i in range(E)]` so empires are spread evenly across the galaxy (e.g. `E=4, N=8 → [0, 2, 5, 7]`, not the old stair-step `[0, 2, 4, 6]` that clustered at the low end).

A per-system `next_planet_in_system` counter ensures shared-system mode never silently overwrites `Planet.owner_id` — each empire is handed a different planet index. Defensive fallback: if a planet supply is somehow exhausted, the assignment is skipped with a `WARNING` log rather than overwriting another empire's home.

The New Game Setup slider runs over an internal integer range `[0, SLIDER_T_MAX]` (1000) and maps to `system_count` via `system_count_slider_curve(t)`:

```python
value = max(1, min(150, int(round(1 + 149 * (t / SLIDER_T_MAX) ** 2))))
```

The quadratic curve is fine-grained at the low end (each pixel near `t=0` produces a 1-system change, so `1 → 2 → 3` are individually selectable) and coarser at the high end (the top 10% of slider travel covers ~28× as many systems as the bottom 10%). The inverse `system_count_slider_inverse(value)` is used to position the thumb when seeding the slider from a default `system_count`.

## 7. Race Preferences & Habitability (PROJ-283)

PROJ-283 replaced an ad-hoc set of `_ideal`/`_tolerance` field pairs on `RaceConfig` (one for gravity, one for temperature, one for water, one for radiation, plus a free-form `atmosphere_preferences: Dict[gas_name, score]`) with a **registry-driven preference model**. Every habitability axis — gravity, temperature, water, total surface pressure, tectonic activity, magnetic field, radiation shielding, and each of 10 atmospheric gases — is now represented by one entry in `FACTOR_REGISTRY`. The habitability formula and the race-setup UI both iterate the registry, so adding a new axis is a single data-edit.

### Core data model

**Files:**
- `game/strategy/data/environmental_preference.py` — `EnvironmentalPreference` dataclass
- `game/strategy/data/habitability_factors.py` — `HabitabilityFactor`, `FACTOR_REGISTRY`, factor iterators
- `game/strategy/data/race_config.py` — `RaceConfig.preferences`, `base_reproduction_rate`, `base_happiness`
- `game/strategy/formulas/habitability.py` — `calculate_habitability(planet, race_config)`, `score_planet_for_race()`

```python
@dataclass
class EnvironmentalPreference:
    setpoint: float       # the race's preferred value (free; no point cost)
    tolerance: float      # Gaussian sigma for habitability scoring (costs points to deviate from default)
    min_value: float      # legal slider range
    max_value: float      # legal slider range
    step: float           # one unit of the tolerance cost curve

@dataclass(frozen=True)
class HabitabilityFactor:
    id: str               # e.g. "gravity", "gas.O2"
    display_name: str
    unit: str             # "m/s^2", "K", "Pa", "fraction", "earth_equiv"
    display_scale: float  # multiplier for UI display (Pa→kPa = 0.001, m/s²→g = 1/9.81)
    weight: float         # weight in the weighted geometric mean
    default_setpoint: float
    default_tolerance: float
    min_value: float
    max_value: float
    step: float
    extractor: Callable[[Planet], Optional[float]]
    scorer:    Callable[[Optional[float], EnvironmentalPreference], float]
```

### `FACTOR_REGISTRY` contents

7 scalar factors + 10 gas factors = 17 total. Per-factor weights:

| Factor id     | Display name        | Unit  | Weight | Default setpoint | Default tolerance |
|---------------|---------------------|-------|--------|------------------|-------------------|
| `gravity`     | Gravity             | m/s²  | 1.0    | 9.81             | 2.0               |
| `temperature` | Temperature         | K     | 1.0    | 293.0            | 50.0              |
| `pressure`    | Surface Pressure    | Pa    | 0.9    | 101325.0         | 20000.0           |
| `water`       | Water Coverage      | frac  | 0.8    | 0.5              | 0.2               |
| `radiation`   | Radiation Shielding | —     | 0.6    | 0.0              | 50.0              |
| `magnetic`    | Magnetic Field      | EE    | 0.6    | 1.0              | 0.3               |
| `tectonic`    | Tectonic Activity   | frac  | 0.4    | 0.3              | 0.2               |
| `gas.O2`      | Oxygen              | Pa    | 0.15   | 21000.0          | 5000.0            |
| `gas.N2`      | Nitrogen            | Pa    | 0.15   | 79000.0          | 20000.0           |
| `gas.CO2` …   | (8 more gases)      | Pa    | 0.15   | 0.0              | 10000.0           |

Total weight = 6.8 (1.0 + 1.0 + 0.9 + 0.8 + 0.6 + 0.6 + 0.4 + 1.5). Per-gas weight is `1.5/10 = 0.15` so the gas bucket sums to 1.5.

`gas.N2` has a non-zero default setpoint because Earth-derived life requires an inert dilutent — without that default, an unconfigured "Earth-like default race" would silently flunk every Earth-like planet (8σ N2 mismatch dragging composite score from 1.0 to 0.82). The other non-O2/non-N2 gases keep `setpoint=0` ("don't want this gas").

### Habitability formula (weighted geometric mean)

`calculate_habitability(planet, race_config)` at [habitability.py:50-94](../../game/strategy/formulas/habitability.py#L50-L94):

```python
log_sum = 0.0
weight_sum = 0.0
for factor_id, factor in FACTOR_REGISTRY.items():
    pref  = race_config.preferences.get(factor_id) or factory_default(factor)
    value = factor.extractor(planet)
    score = factor.scorer(value, pref)               # in [0, 1]
    log_sum    += factor.weight * math.log(max(score, 1e-10))
    weight_sum += factor.weight
return math.exp(log_sum / weight_sum)
```

Numerical floor `1e-10` matches v1; with total weight 6.8, a single weight-1.0 factor at score 0 drags composite to ~0.034 (`exp(-23 × 1.0 / 6.8)`). The default scorer is `_default_gaussian_scorer`: `exp(-0.5 × ((value - setpoint) / tolerance)²)` with `value=None` coerced to `0.0`.

**Tank-all property by axis weight:**
- A single high-weight scalar (gravity, temperature) at score 0 → composite ≈ 0.034 (strong tank).
- A single low-weight gas at score 0 → composite ≈ 0.6 (weak tank — the gas-bucket weight allocation deliberately bounds individual gas impact). This is by design: a race with full life-support tech can survive a missing critical gas at reduced productivity. If a future requirement is "missing critical gas → uninhabitable", promote the relevant gas to a scalar weight≥1.0.

**Lazy import:** `calculate_habitability` lazy-imports `FACTOR_REGISTRY` and `EnvironmentalPreference` to break the otherwise-circular dependency (`habitability_factors.py` already imports `_gaussian_factor` from `habitability.py`).

### Adding a new factor

Single-edit recipe — add an entry to `_SCALAR_FACTORS` (or `_GAS_FORMULAS`) in `habitability_factors.py`:

```python
HabitabilityFactor(
    id="solar_flux",
    display_name="Solar Flux",
    unit="W/m^2",
    display_scale=1.0,
    weight=0.5,
    default_setpoint=1361.0,    # Earth's solar constant
    default_tolerance=200.0,
    min_value=0.0, max_value=5000.0, step=50.0,
    extractor=_make_scalar_extractor("solar_flux"),
    scorer=_default_gaussian_scorer,
),
```

After this single edit:
- `calculate_habitability` automatically includes the new factor.
- `RaceConfig.__post_init__` automatically backfills `preferences["solar_flux"]` with the registry default for every existing race.
- `RacePointBudget.calculate_preferences_cost` automatically prices tolerance deviations on the new axis.
- `RaceEnvironmentPanel` automatically renders a new `PreferenceRow` (no panel-side change).
- Homeworld presets that don't list `solar_flux` keep the registry default.

### Race point budget

`RacePointBudget` (`game/strategy/data/race_point_budget.py`) iterates `race_config.preferences` to compute the per-axis cost contribution. Setpoint is **free** — moving the slider anywhere in `[min_value, max_value]` costs 0 points. Tolerance deviation from the registry default costs `_exponential_cost(steps) = 2^steps - 1` per axis, where `steps = round(|tolerance - default_tolerance| / step)`. Direction-symmetric: tighter and wider both cost.

Method index:

| Method | Returns | Notes |
|--------|---------|-------|
| `calculate_aptitude_cost(rc)` | int | Sum across the 7 paid aptitudes (Phase 3 dropped `happiness` and `population_growth`). |
| `calculate_preferences_cost(rc)` | int | Sum of per-axis tolerance-deviation costs across all 17 factors. |
| `calculate_reproduction_cost(rate)` | int | `_exponential_cost(steps)` above default 3%; linear refund (2 pts per 1% step) below default down to 0.5% floor. |
| `calculate_total_cost(rc)` | int | Sum of the three above. |
| `get_remaining_points(rc)` | int | `total_budget − total_cost`. |
| `get_breakdown(rc)` | Dict[str, int] | Flat per-source dict: `aptitude:strength`, `pref:gravity`, `reproduction`, etc. Sum equals `calculate_total_cost(rc)`. |

**Reproduction-rate refund** uses linear-in-rate math (not integer-step) so the 0.5% floor returns exactly -5 points: Python's banker's `round(-2.5) == -2` would yield -4 instead. See `decisions.md` (PROJ-283 2026-04-18, Phase 3 entry).

### Homeworld presets

`data/homeworld_presets.json` declares 11 planet-type presets in the registry-native shape:

```json
{
  "id": "CONTINENTAL",
  "name": "Continental",
  "description": "Earth-like world with varied terrain and temperate climate",
  "preferences": {
    "gravity":     { "setpoint": 9.81,    "tolerance": 2.94 },
    "temperature": { "setpoint": 293.0,   "tolerance": 50.0 },
    "water":       { "setpoint": 0.6,     "tolerance": 0.2 },
    "gas.O2":      { "setpoint": 21000.0, "tolerance": 5000.0 },
    "gas.N2":      { "setpoint": 79000.0, "tolerance": 20000.0 }
  }
}
```

`apply_preset_to_config(preset, race_config)` iterates the preset's `preferences` map and overlays each entry onto `race_config.preferences`. Factors not listed are not touched — this is a partial-override semantic that minimises preset-edit churn when adding a new factor to the registry.

### `RaceConfig` field reference (post-Phase 4)

The legacy `gravity_ideal`, `gravity_tolerance`, `temperature_ideal`, `temperature_tolerance`, `water_ideal`, `water_tolerance`, `atmosphere_preferences`, `radiation_tolerance`, `aptitude_happiness`, `aptitude_population_growth` fields are **GONE**. Code that references them will `AttributeError`.

| Old field | Replacement |
|-----------|-------------|
| `race.gravity_ideal` (g) | `race.preferences["gravity"].setpoint / 9.81` |
| `race.gravity_tolerance` (g) | `race.preferences["gravity"].tolerance / 9.81` |
| `race.temperature_ideal` | `race.preferences["temperature"].setpoint` |
| `race.temperature_tolerance` | `race.preferences["temperature"].tolerance` |
| `race.water_ideal` | `race.preferences["water"].setpoint` |
| `race.water_tolerance` | `race.preferences["water"].tolerance` |
| `race.atmosphere_preferences[gas_name]` | `race.preferences[f"gas.{formula}"].setpoint` (Pa) |
| `race.radiation_tolerance` | `race.preferences["radiation"].tolerance` (and `setpoint` for shielding-target prefs) |
| `race.aptitude_happiness` | `race.base_happiness` (0.0–1.0; PROJ-284 derives `pop.happiness` from this seed) |
| `race.aptitude_population_growth` | `race.base_reproduction_rate` (0.005–0.10; PopulationEngine reads directly) |

### UI surface

`RaceEnvironmentPanel` (`game/ui/panels/race_environment_panel.py`) iterates `iter_scalar_factors()` + `iter_gas_factors()` and renders one `PreferenceRow` per factor. The `PreferenceRow` widget (`game/ui/widgets/preference_row.py`) is reusable: `PreferenceRow.format_value(factor, raw)` handles unit-aware display (Pa → kPa, m/s² → g, fraction → %) and `PreferenceRow.calculate_factor_cost(factor, pref)` mirrors the budget cost curve for the per-row cost label.

The four planet-modifier editor windows (`gravity_target_editor.py`, `water_target_editor.py`, `radiation_shield_editor.py`, `atmosphere_target_editor.py`) read `race_config.preferences[<id>].setpoint` for their "Species Ideal" / "Auto" buttons.

### 7.x — LLM Race Description Generator (PROJ-299)

**Files:** `game/strategy/data/race_caption_loader.py`, `game/strategy/services/race_description_prompt_builder.py`, `game/strategy/services/race_description_llm_controller.py`. Tools at `Tools/captioning/`.

The Description tab on `RaceSetupScreen` can populate `race_config.bio_description` and `race_config.socio_description` from the player's prior race choices via DeepSeek (or any provider registered with PROJ-296's `LLMProviderFactory`).

- **Captions** are pre-baked externally: the user runs `Tools/captioning/prompts/{flag,portrait,theme}_prompt.md` against Gemini's vision model and saves the JSON output to `<image>.caption.json` sidecars. `Tools/captioning/validate_captions.py` reports missing/malformed sidecars.
- **`RaceCaptionLoader`** reads sidecars at runtime; returns `None` on missing/malformed (graceful degradation — the prompt substitutes a `{"note": "no visual reference"}` marker so the LLM doesn't invent visual details).
- **`build_bio_prompt(race_config, captions)` / `build_socio_prompt(...)`** are pure module-level functions that assemble the chat-completion `list[Message]`. Both system prompts include one few-shot example (cached on the provider side).
- **`RaceDescriptionLLMController`** is a pygame-free state machine (PROJ-299 reference consumer of Pattern #28 — see `docs/02_PATTERNS.md`). Owns one `LLMBackgroundCall` per field (bio + socio), translates `CallStatus` → `FieldStatus`, exposes `on_change` callback for UI rebuild, and supports `cancel_all()` from `RaceSetupScreen.kill()`.

The runtime LLM (DeepSeek by default, `MAX_CONCURRENT_CALLS=3`) is text-only; vision-model cost is paid once during caption authoring rather than per-generation.

## 8. Colony Demographics Loop (PROJ-284 + PROJ-286)

Per-turn pipeline that converts a colony's multi-resource upkeep stockpile + per-species sliders into population growth. Runs AFTER the 100-tick loop in `TurnEngine.process_turn`, BEFORE `QualityEngine`:

```
[100-tick loop]
  → OrganicsConsumptionEngine.process_consumption
  → HappinessEngine.process_happiness
  → PopulationEngine.process_population_growth
  → QualityEngine / AtmosphereEngine / WaterEngine (unchanged)
```

### Data model

`ColonySpeciesConfig` (`game/strategy/data/colony_species_config.py`) is a per-colony per-species dataclass attached to `Planet.species_configs: Dict[race_id, ColonySpeciesConfig]`. Fields:

- `food_allocation: float = 1.0` — player-set linear scalar. Default 1.0 ("normal rations"). Range 0 to ∞ (UI slider capped at 5.0 with typed-input override). Scales BOTH upkeep consumption (across EVERY declared resource) AND the derived happiness/reproduction chain.
- `last_consumption_ratios: Dict[str, float]` — **TRANSIENT** per-resource supply-ratio dict written by `OrganicsConsumptionEngine` each turn. Keys are resource ids declared in `EconomyConfig.population_consumption`; values are `supplied / needed` per resource. NOT serialized — `ColonySpeciesConfig.to_dict` excludes it and `from_dict` always resets to `{}`. Downstream readers rely on the engine overwriting every entry every turn; the engine writes 1.0 per declared resource for zero-population / zero-allocation edge cases to prevent stale values.
- `last_food_ratio: float` — **computed `@property`** returning `min(last_consumption_ratios.values())` with a 1.0 fallback when the dict is empty. Read by `HappinessEngine` and `PopulationEngine` unchanged — their source files don't change when upgrading from single-resource (PROJ-284) to multi-resource (PROJ-286) consumption. Models Liebig's Law of the Minimum: the colony is "as well-fed as its worst-supplied resource". A 100%-organics / 0%-metals colony has aggregate ratio 0 and is treated as starving. No setter — callers must write to `last_consumption_ratios` directly.
- `last_food_surplus: float` — **computed `@property`** (FEAT-19) returning `food_allocation × min(last_consumption_ratios.values())` with a 1.0 fallback when the dict is empty. Unbounded; only exceeds 1.0 when allocation > 1.0 AND every declared resource's supply meets the elevated demand. Read by `HappinessEngine` to award an additive surplus-food happiness bonus. Identity: each per-resource ratio is `supplied / (count × allocation × rate)`, so multiplying by `allocation` yields `supplied / (count × rate)` — i.e. "supplied / needed_at_1x". No setter — pure derivation from `food_allocation` + `last_consumption_ratios`.

`Planet.get_species_config(race_id)` is a lazy-create-and-store helper — callers can read or mutate the returned config without checking for absence first.

### Data-driven population-consumption dict

`data/economy.json` declares every resource population consumes and the per-pop-per-turn rate for each:

```json
{
    "population_consumption": {
        "organics": 0.001,
        "metals": 0.0001,
        "radioactives": 0.00001
    },
    "surplus_food_bonus_per_x": 0.20,
    "surplus_food_bonus_cap": 0.20
}
```

`EconomyConfig` (`game/strategy/config/economy_config.py`) loads this dict via the project `get_default_* / set_default_*` module-accessor pattern. Graceful fallback to a hardcoded `{"organics": 0.001}` default (PROJ-284-equivalent) on missing JSON, malformed JSON, or `population_consumption` present but not a dict. The `primary_resource` convenience property returns the first key in insertion order (Python 3.7+), used by UI titles that want a single "main food" label. PROJ-291 C2 retired the legacy `population_food_resource` shim; `FoodAllocationEditor` reads `primary_resource` directly.

**FEAT-19 surplus-food coefficients.** `surplus_food_bonus_per_x` (default 0.20) is the additive happiness reward per +1.0 of `last_food_surplus` above 1.0; `surplus_food_bonus_cap` (default 0.20) is the per-turn ceiling on that bonus. Both are optional in the JSON — the loader provides the same defaults so existing files keep working unchanged. Tunable via data edit; balance lever for the over-feeding strategy.

### Formulas

- **Consumption** (`OrganicsConsumptionEngine`): per species per colony, the engine `clear()`s `cfg.last_consumption_ratios` then iterates `economy.population_consumption.items()`. For each `(resource_id, per_pop_rate)`: `needed = pop.count * cfg.food_allocation * per_pop_rate`; drains `min(needed, available)` from `planet.stockpile[resource_id]`; writes `cfg.last_consumption_ratios[resource_id] = supplied / needed` (or 1.0 when `needed == 0`).
- **Happiness** (`HappinessEngine`): `raw = race.base_happiness * cfg.last_food_ratio * habitability`. **FEAT-19**: when `cfg.last_food_surplus > 1.0`, an additive bonus `min(economy.surplus_food_bonus_cap, economy.surplus_food_bonus_per_x * (cfg.last_food_surplus - 1.0))` is added to `raw` BEFORE the clamp. Final `happiness = clamp(raw, 0, 3)`. The surplus bonus participates in the same [0, 3] clamp — it does not bypass it. `last_food_ratio` is the MIN across declared resources — if any upkeep resource is at 0%, happiness collapses to 0 regardless of the others (the bonus also vanishes because surplus = allocation × MIN ratio = 0). Unbounded above 1.0 on purpose — over-supply + ideal habitability + surplus bonus can push happiness past neutral. Clamp at 3 prevents runaway values. The bonus reaches population growth indirectly through `pop.happiness` — neither `PopulationEngine` nor `colony_output.projected_growth_rate` was touched.
- **Population growth** (`PopulationEngine`): `growth = (race.base_reproduction_rate * last_food_ratio) * P * (1 - P/K_eff) * happiness + decline_term`, where `K_eff = max(1.0, planet.max_population * habitability)` and `decline_term = -DECLINE_RATE * P * (1 - last_food_ratio)` when `last_food_ratio < 1.0` else 0. `DECLINE_RATE = 0.02` in `population_engine.py`. The defensive `min(1.0, happiness)` clamp from the pre-PROJ-284 formula was removed so the new [0, 3] happiness range is honored — `happiness=3` triples the logistic term. Via the MIN aggregation, a colony starving on even one declared resource sees full decline_term.

### Multi-species engine resolution (PROJ-291 Phase 2)

`HappinessEngine` and `PopulationEngine` each accept an optional `race_registry: Optional[IRaceRegistry] = None` kwarg (mirroring the PROJ-285 pattern already established for `HarvestingEngine` / `ProductionEngine`). When supplied, `_get_race_config(race_id, empire)` resolves `pop.race_id → RaceConfig` via `registry.get_race(race_id)`, so multi-species colonies compute each species' happiness + growth using its OWN `base_happiness` / `base_reproduction_rate`. When the kwarg is None (legacy callers + MagicMock-empire test fixtures), the resolver falls back to `empire.race_config`, returning that config ONLY when the requested `race_id` matches the empire's primary race — non-matching species are gracefully skipped (the species' count/happiness stays unchanged).

PROJ-291 closed a silent dual-return bug where the legacy fallback returned the empire's primary `RaceConfig` regardless of whether `race_id` matched, so any non-primary species on a multi-species colony silently used the wrong `base_happiness` / `base_reproduction_rate`. The bug predated PROJ-287 (which built the registry) but was only reachable post-PROJ-284/286/289 once multi-species colonies became real gameplay state.

Wiring: `GameSession.race_registry` is a lazy property that constructs a session-scoped `CachedRaceRegistry(RaceLibrary())`. Session passes it to `TurnEngine(race_registry=...)` on construction. `TurnEngine` threads it through to `HappinessEngine` + `PopulationEngine` during their lazy-init properties.

### UI surface

`FoodAllocationEditor` (`game/ui/screens/food_allocation_editor.py`) is a pygame_gui window with one row per species on a colony. Each row: slider (0.0–5.0, step 0.05) + typed input (accepts any non-negative value) + live multi-resource consumption preview. Title auto-derives from `ResourceCatalog.get(economy.primary_resource).name` — default label reads "Organics Allocation — {planet.name}". Apply writes to `planet.get_species_config(race_id).food_allocation`.

The button appears on `PlanetAbilitiesWindow` when the colony has at least one population (unlike the facility-gated environment editors). Routed via `StrategyEventRouter._open_food_allocation_editor` → direct mutation on `ColonySpeciesConfig` (no command dispatch — food allocation is a player-facing dial, not a strategy-layer command with replay semantics).

PROJ-291 C2 rewired the editor's preview. `compute_consumption_preview(pop, allocation, population_consumption: Dict[str, float]) -> Dict[str, float]` returns one entry per resource declared in `EconomyConfig.population_consumption`; `_preview_text` joins them into a single "Preview: 0.100 organics, 0.010 metals/turn" label. Single-resource economies render identically to the pre-migration UI.

### Swapping the population-consumption dict

Modders and designers can change which resources populations consume without touching code. Recipe:

1. **Edit `data/economy.json`** — add, remove, or retune any entry in `population_consumption`. Example adding ammonia and halving the default rates:
   ```json
   {
       "population_consumption": {
           "organics": 0.0005,
           "metals": 0.00005,
           "radioactives": 0.000005,
           "ammonia": 0.0002
       }
   }
   ```
2. **Ensure every referenced resource exists in `data/resources.json`** and is harvestable somewhere in the game (some existing ResourceHarvester ability must target it, or the colony stockpile will never fill that slot → MIN aggregation collapses to 0 → species starves). Quality-bearing (`has_quality: true`) is preferred but not required.
3. **Restart the game** so `get_default_economy_config()` re-reads the JSON. In tests and at runtime, `set_default_economy_config(new_config)` swaps the cached singleton without restart.

Aggregation behavior: the species' `last_food_ratio` becomes the MIN across all declared resources. A colony without any ammonia stockpile at all → `last_consumption_ratios["ammonia"] = 0.0` → aggregate = 0 → happiness = 0 → full decline term applies. This is the correct Liebig's-Law gameplay: add new required resources cautiously and make sure new empires can realistically produce them.

Dict insertion order controls which resource is "primary" for UI labels — put the flagship food resource first.

Cross-reference: [§7 Race Preferences & Habitability](strategy_layer.md#7-race-preferences--habitability-proj-283) is where the `habitability` factor in the happiness formula comes from.

## 9. Colony Economy Multiplier (PROJ-285)

Habitability also scales colony **harvest** and **production** rates via `planet_habitability_multiplier(planet, race_registry)` at `game/strategy/formulas/colony_output.py`. Population-weighted mean across all species on the colony — the exact same weighting algorithm PROJ-284 uses for per-species food ratios, but aggregated planet-wide instead of per-species.

Integration points:
- `HarvestingEngine._harvest_resource` multiplies the multiplier into the harvest formula AFTER quality and booster stacking, BEFORE `tick_fraction`.
- `ProductionEngine._process_queue_tick_dynamic` scales the `production_rate` dict up front so all downstream per-tick math (limiting-resource, tick-capacity, affordability) honors the multiplier without further code changes.
- `TurnEngine.process_turn` calls `set_current_turn(session.turn_number)` on both engines before the 100-tick loop so the per-planet cache on `Planet.get_cached_habitability_multiplier` invalidates on each turn boundary.

Net effect after PROJ-283 + PROJ-284 + PROJ-285: habitability is the single numeric axis that drives population carrying capacity (via `K_eff = max_population * habitability`), happiness (via `base_happiness * last_food_ratio * habitability`), harvest rate, AND production rate. See [docs/systems/production_system.md § Habitability Multiplier](production_system.md#habitability-multiplier-proj-285) for the full formula, edge cases, and caching contract.

### Projection helpers (PROJ-288)

Engine methods like `PopulationEngine._grow_species` and `OrganicsConsumptionEngine._process_colony` MUTATE state — they're built for the per-turn engine loop, not for UI panels that need to display "what would happen next turn?". PROJ-288 extracts pure projection helpers that read the same inputs and return the same numbers WITHOUT mutating:

- **`projected_growth_rate(planet, pop, race_config, cfg) -> float`** at `game/strategy/formulas/colony_output.py` — per-capita next-turn rate. Multiply by `pop.count` for the absolute Δpop the engine would apply.
- **`PlanetEconomyProjector.project(planet) -> Dict[resource_id, ResourceProjection]`** at `game/strategy/services/planet_economy_projector.py` — per-resource harvest / upkeep / yard / net for one planet.
- **`StrategySessionFacade.get_colony_demographic_view(planet_id)`** — facade-level DTO bundling per-species + per-resource state for one colony in one read; consumed by PROJ-289 / PROJ-290 UI panels.

**Equivalence contract**: the projection math tracks the engine math. `tests/integration/strategy/test_growth_rate_equivalence.py` runs a 12-cell matrix asserting `projected_growth_rate(...) * pop.count` equals `PopulationEngine._grow_species`'s observed Δpop (within int-cast tolerance + the engine's `max(0, ...)` floor) for every combination of food_ratio × happiness × P/K_eff. `tests/integration/strategy/test_projector_drain_matches_engine.py` similarly pins that `_project_yard_drain` per-turn output equals `ProductionEngine._calculate_tick_expenditure × 100` for every resource the queue item costs. If either side drifts, CI fails — the fix is to update BOTH together, not to silence the test.

**BUG-120 (2026-04-27)**: `_project_yard_drain` previously summed each yard's full per-resource `build_rate` (capacity), producing ghost drain rows for resources the queued items didn't actually cost. It now delegates to the canonical `forecast_queue_turn_spend` helper (the same one `EmpireEconomyCalculator._aggregate_construction_expenses` uses for Treasury) so the Planet detail "Yard" row matches the build queue panel's per-item per-turn rate.

See [docs/04_SERVICES.md § Planet Economy Projector](../04_SERVICES.md#planet-economy-projector-proj-288) for the full service catalog entries.

### Planet report panel UI surface (PROJ-289)

The planet report panel (`game/ui/panels/planet_report_panel.py`) consumes the `ColonyDemographicView` directly so all per-species + per-resource displays read from one source of truth (no per-frame re-projection):

- **Per-species sub-block** — when a `view: ColonyDemographicView` is passed, `format_planet_info(planet, view=view)` (`game/ui/screens/strategy_detail_fmt.py`) replaces the legacy single-line `- {race_id}: {count} [+/~/-]` rendering with an indented sub-block per species: header line (race_name, count, happiness category) + 3 metric lines (Habitability + Happiness, Growth + Food ratio, Allocation). Growth is rendered as a signed percentage: `format_signed_float(s.growth_rate * 100, decimals=1)` then composed into `Growth: {growth_pct}% / turn`. Happiness category labels come from `_happiness_category(happiness)`: `Content` ≥ 1.5, `Settled` ≥ 0.5, else `Unhappy`. Species iteration honours `view.species` ordering (PROJ-288 already sorts largest count first; PROJ-292 m5 also enforces this in `ColonyDemographicView.__post_init__`).
- **Per-resource transposed grid** — `_build_resource_grid` renders an icon-column grid: each resource in `_displayed_resources` (sourced from `ResourceCatalog.by_display_group("planetary"|"operational")` via `game/ui/utils/resource_display.get_displayed_resource_ids`) is a column with a 20px icon header above a 3-letter abbreviation. Below the header are 8 metric rows: `Qty / Qual / Harvest / Upkeep / Yard / Net / Stored / Cap`. Adding a resource to `data/resources.json` adds a column with no UI code change. Cell text comes from the pure helper `_projection_grid_rows(planet, view, displayed_ids)` (testable without pygame). Display sign convention for the flow rows: harvest as-is, upkeep + yard rendered as drains via negation, net as-is. Cells with no projection signal (operational resources, or any resource when `view is None`) render `"-"`; deposit cells (`Qty`/`Qual`) read from `planet.deposits`; storage cells (`Stored`/`Cap`) read from `planet.stockpile` / `planet.max_stockpile` and work for every resource regardless of whether it has projections. Net row cells get sign-coloured tinting via `_net_cell_color`: `HP_HEALTHY` positive, `HP_CRITICAL` negative, `TEXT_LIGHT` zero (only applied to cells whose resource has a real projection).
- **Unowned-planet rendering** — when `view is None` (no `ColonyDemographicView`, e.g. unowned planet), the same transposed grid renders with the flow rows blank (`-`) but `Qty`, `Qual`, `Stored`, `Cap` populated from the planet's intrinsic data. This replaces the pre-2026-04-26 fallback path that re-rendered a separate legacy grid; there is now exactly one render path. The strategy screen wires the facade call from `strategy_detail_formatter._show_planet_report`: `view = facade.get_colony_demographic_view(obj.id)` when `obj.owner_id is not None`.
- **PROJ-292 H1 coverage completion** — PROJ-292 Phase 1 backfilled the view-threading pattern into [game/ui/screens/planet_list_window.py](../../game/ui/screens/planet_list_window.py) and [game/ui/screens/build_queue_panel_factory.py](../../game/ui/screens/build_queue_panel_factory.py), so the per-species sub-block now renders in all three colonized-context `PlanetReportPanel` callers (strategy detail, planet list, build queue). `PlanetSelectionWindow` is uncolonized-only by design (colonization-flow filter) and intentionally untouched. `PlanetListWindow.__init__` and `BuildQueuePanelFactory.__init__` accept an optional `facade: StrategySessionFacade = None` kwarg; construction sites in `strategy_window_manager._open_planet_list_window` and `BuildQueueScreen.__init__` pass it through.

### Treasury & Planet Detail UI Integration (PROJ-290)

Two UI surfaces consume the PROJ-286/287/288 infrastructure:

- **Empire Treasury → Population Upkeep row.** `EmpireEconomySnapshot.total_population_upkeep: Dict[str, float]` aggregates per-resource drain across every empire colony via `PlanetEconomyProjector._project_upkeep`. `EmpireTreasuryPanel` renders the aggregate as one expense row labeled "Population Upkeep" with signed-negative cells; the row is HIDDEN when all values are zero or the dict is empty (fresh game with no populations yet). Production wiring: `empire_panel_window._build_treasury_tab` threads `get_default_economy_config()` + `facade.get_race_registry()` into `EmpireEconomyCalculator(economy_config=..., race_registry=...)`. When either dep is missing the calculator short-circuits upkeep aggregation to `{}` — backward-compat for legacy callers that only pass `registries=`.

- **Uncolonized-planet habitability list.** `format_uncolonized_habitability_for_empire(planet, empire, race_registry)` at `game/ui/screens/strategy_detail_fmt.py` emits an HTML section listing every `empire.resident_species()` entry with a 0-100 integer habitability score, sorted BEST-FIT FIRST. Score formula: `int(round(score_planet_for_race(planet, race_config) * 100))`. The section renders only when all three conditions hold: `planet.owner_id is None` AND `empire is not None` AND `race_registry is not None`. Display-name resolution follows the PROJ-287 convention: `race_config.race_name` → `race_config.name` → `race_id`. `race_id` values whose `registry.get_race()` returns None are silently skipped (save-drift defense, same as `planet_habitability_multiplier`). Production wiring: `PlanetReportPanel.__init__` + `update_planet` accept `empire` + `race_registry` kwargs — they stack with PROJ-289's `view` kwarg in the same panel signature; `strategy_window_manager._open_planet_list_window` pulls `facade.get_race_registry()` and threads it through `PlanetListWindow` → `PlanetReportPanel`.


## 10. Universal IAbilitySource Framework (PROJ-300)

After PROJ-300, "things at a hex/system project effects" flows through one path. Storms, planetary facilities, and (post-PROJ-301..305) planets-themselves, stars, warp points, system archetypes, and fleets all plug in by satisfying the `IAbilitySource` protocol.

**Pipeline:**

```
[entities at hex/system]
        ↓ adapters (IAbilitySource)
[FacilityAbilitySource, StormAbilitySource, ...]
        ↓ ability_iterator (registered providers)
iter_ability_sources_at_hex(system, hex_coord)
        ↓ system_effects_collector
collect_sector_effects() / collect_system_effects()
        ↓ aggregate_multipliers / aggregate_rates
[effect rows: ability_name, kind, aggregate_value, providers[]]
        ↓ consumers
fleet_movement_engine, environmental_hazard_engine, spec_compiler, system_tree_panel
```

**Key files:**
- `game/core/protocols/strategy_entities.py` — `IAbilitySource` protocol + `is_ability_source` TypeGuard
- `game/strategy/services/ability_sources/` — adapter package (`FacilityAbilitySource`, `StormAbilitySource`, plus the shared `roll_intrinsic_abilities` and `format_intrinsic_source_label` helpers used by PROJ-301..304). Per-ability `chance` field (FEAT-15, default `1.0`) on registry templates gates whether each declared ability fires for a given entity at galaxy generation; today only `data/planet_types.json` populates it (planet effects are rare flavour, e.g. CRYOPLANET `ThrustModifier` chance=0.10). Templates without `chance` consume zero extra RNG draws so stars/warps/archetypes remain byte-identically deterministic.
- `game/strategy/services/ability_iterator.py` — provider registration + iterator
- `game/strategy/services/system_effects_collector.py` — aggregation pipeline + `find_sector_effect`/`aggregate_value_or` helpers
- `game/strategy/services/strategic_ability_scanner.py` — `aggregate_multipliers` (intra-MAX, inter-MULTIPLY) and `aggregate_rates` (intra-MAX, inter-SUM)

**Storm migration:** Storms now declare `abilities: Dict[str, Any]` matching components.json. Five storm types in `data/storms.json` v2.0 declare ShieldModifier, ThrustModifier, StrategicSpeedModifier, EnvironmentalDamage (with damage_type), FuelDrain. Overlapping storms multiply per-provider (decisions.md D6) — `tests/integration/strategy/test_overlapping_storm_combat.py` locks in 0.5x · 0.5x = 0.25x for two ion storms.

**Storm coordinate frame (BUG-119):** `StormAbilitySource` carries an optional `system: Any` field set by `_storm_provider`. `affects_hex(hex_coord)` translates the storm's local position via `sys_loc + storm.location + offset` and compares against the global query hex. This mirrors the planet/star/warp-point sibling adapters; without it, every storm in a system whose `global_location` is non-zero — i.e. every storm in a real galaxy — silently produced an empty Sector Effects panel because `Storm.occupied_hexes` is in **local-system coordinates** while the UI passes the **global-galaxy hex**. Test fixtures must use a non-zero `system.global_location` to make the local-vs-global distinction meaningful (three test fixtures were updated for this reason).

**Combat consumption:** `_entries_from_sector_effects(sector_effects)` in `spec_compiler.py` emits one `ModifierEntry` per ACTIVE provider. ShieldModifier, DamageModifier, and ThrustModifier (PROJ-300 D14) flow through the same path with the appropriate stat_keys via `ABILITY_STAT_REGISTRY`.

**Eradicated in Phase 7:** `AreaEffectManager`, `EnvironmentalEffects`, `StormEffect` dataclass, `Storm.effects` field, `IStorm.effects` property, `_entries_from_environmental_effects`. Old saves with the legacy `effects` shape FAIL TO LOAD per decisions.md D19 — save files are disposable.
