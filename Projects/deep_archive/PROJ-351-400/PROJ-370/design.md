# PROJ-370: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### What already exists

`game/core/protocols/strategy_entities.py` defines **read protocols** for the strategy data layer:

| Protocol | LOC | Defines |
|---|---|---|
| `IStarSystem` | `strategy_entities.py:14-40` | `stars`, `planets`, `warp_points`, `global_location`, `name`, `storms` |
| `IStar` | `strategy_entities.py:43-69` | `color`, `mass`, `temperature`, `luminosity`, `star_type`, `name` |
| `IPlanet` | `strategy_entities.py:72-172` | 21 read-only properties incl. `populations`, `facilities`, `stockpile`, `max_stockpile`, `owner_id`, `atmosphere`, `energy` |
| `IFleet` | `strategy_entities.py:230-301` | `ships`, `orders`, `location`, `owner_id`, `id`, `speed`, `path`, `construction_queue`, `name`, `is_building`, `capabilities`, `resources`, `battle` |
| `IOrderable` | `strategy_entities.py:175-201` | `orders`, `get_current_order`, `add_order`, `pop_order`, `clear_orders` (Fleet + Planet share) |
| `IZoneOccupant` | `strategy_entities.py:204-227` | `occupied_hexes` |
| `IWarpPoint` | `strategy_entities.py:304-314` | `destination_id`, `location` |
| `IStorm` | `strategy_entities.py:336-355` | `name`, `storm_type`, `abilities`, `occupied_hexes` |
| `IAbilitySource` | `strategy_entities.py:359-407` | source-of-truth for the abilities collector (PROJ-300) |
| `ISectorEnvironment` | `strategy_entities.py:317-332` | `local_hex`, `system`, `calculate_radiation()` |

There is **no `IFleetMutator` / `IPlanetMutator` / etc.** Any code can `import Fleet` and assign to its attributes.

`docs/02_PATTERNS.md` §2 ("Protocol + TypeGuard") establishes the convention: define `@runtime_checkable` Protocol classes in `game/core/protocols/`, pair with a `TypeGuard` function. All four mutator protocols this project introduces will follow that exact convention — `strategy_mutators.py` is the new sibling of `strategy_entities.py`.

`game/strategy/services/fleet_navigation_service.py:716-759` already proves the pattern in microcosm. `FleetNavigationService.calculate_fleet_next_hex()` is described in its own docstring as the "mutation bridge — it wraps the pure compute_next_step() function and applies the necessary mutations to the Fleet object." This is exactly the shape PROJ-370 generalizes: an explicit, named "mutation bridge" service per data type, with the mutation surface declared on a Protocol.

PROJ-87 (archived 2026-02-10, see `Projects/deep_archive/PROJ-051-100/PROJ-87/`) extracted **read-side delegates** off `Fleet` and `ShipInstance`: `FleetCapabilityCalculator`, `FleetConsumableAggregator`, `FleetBattleAdapter`, `ShipConsumableManager`, `ShipCargoManager`, `ShipDisplayFormatter`, `ShipInstanceBridge`, `ShipInstanceSerializer`. PROJ-370 is the **write-side** complement to PROJ-87.

### Write-traffic survey (heatmap)

Counts are direct attribute writes from outside the data class itself, expressed as `parameter.attribute` patterns. Sourced via `Grep` against `game/`. Counts are mutation-style: `=`, `[...]=`, `.append/.pop/.remove/.clear/.extend/.insert`. *Not* read-style accesses.

| Data class | Attribute | Outside writers | Top writer files |
|---|---|---|---|
| Fleet | `location` | 6 in 5 files | `engine/fleet_movement_engine.py:182`, `engine/order_processor.py` (×2), `engine/handlers/movement.py`, `engine/handlers/base.py`, `validation/superweapon_validator.py` |
| Fleet | `path` | from `FleetNavigationService` (already routed) | `services/fleet_navigation_service.py:755` |
| Fleet | `ships` (`.append/.remove/.extend/.clear`) | 3 in 1 file (sim) + internal | `simulation/systems/battle_engine.py:320,454,490` (sim-side, in scope only at the Post-Battle Hook) |
| Fleet | `orders` (`.append/.pop/.insert/.clear`) | 4 outside Fleet itself | `data/order_serializer.py:231`, `data/fleet_pursuer_tracker.py:141`, `engine/handlers/build.py:43`, `ui/screens/strategy_screen_order_editing.py:90` |
| Fleet | `construction_queue` | 1 outside | `ui/screens/strategy_build_queue_manager.py` |
| Fleet | `display_name` | 1 outside | `ui/screens/strategy_fleet_ops.py` |
| Fleet | `fleet_policy` | 1 outside | `ui/screens/battle_setup/controller.py` |
| Planet | `populations` (`.append`) | 2 outside | `engine/order_processor.py:514` (COLONIZE), `engine/game_initializer.py:344` |
| Planet | `facilities` (`.append`) | 3 outside | `engine/order_processor.py:645`, `engine/production_spawner.py:202`, `quickstart_builder.py:309` |
| Planet | `stockpile` (`[...] =`) | 2 outside | `engine/organics_consumption_engine.py:107`, plus the empire-deser shim in `data/empire.py:183` |
| Planet | `staging_yard` | inside Planet only (helper methods) | — (well-encapsulated already) |
| Planet | `orders` | 3 outside Planet itself | `engine/planet_command_handlers.py:134`, plus the `IOrderable` callers |
| Planet | `owner_id` | counted under empire writes (`add_colony`/`add_fleet`) | `data/empire.py` |
| Planet | `energy` / `energy_capacity` / `energy_generation` | 5 in 1 file | `engine/planet_energy_engine.py` |
| Planet | `atmosphere` / `atmosphere_target` | 2 files | `engine/atmosphere_engine.py`, `engine/game_initializer.py` |
| Planet | `gravity_target` / `water_target` / `radiation_shielding*` | 1 file | `engine/planet_modifier_effect_engine.py` (2 sites) |
| Planet | `species_configs` | accessed via `get_species_config(...)` (already encapsulated) | — |
| Empire | `colonies` (`.append/.remove/.clear`) | 6 outside Empire itself | `engine/superweapon_order_processor.py:358,606`, `services/system_destroyer.py:161`, `engine/game_initializer.py:86`, plus internal `Empire.from_dict` |
| Empire | `fleets` (`.append/.remove`) | 4 outside Empire itself | `ui/screens/battle_setup_state.py` (×3), `combat/post_battle_hook.py:214`, plus internal Empire methods |
| Empire | `_fleet_resource_pool` | 0 outside Empire (private) | — |
| Empire | `max_storage` | 1 outside | `engine/harvesting_engine.py` |
| ShipInstance | `is_alive` | 4 outside | `combat/post_battle_hook.py:121,182`, `engine/environmental_hazard_engine.py:202`, `simulation/managers/retreat_manager.py` |
| ShipInstance | `is_derelict` | 1 outside | `combat/post_battle_hook.py:183` |
| ShipInstance | `current_hp` | 3 outside | `combat/post_battle_hook.py:122`, `engine/environmental_hazard_engine.py:196,198` |
| ShipInstance | `components` (whole-dict assign) | 1 outside (canonical) | `combat/post_battle_hook.py:179` |
| ShipInstance | `cargo_contents` / `consumable_levels` | inside `ShipCargoManager` / `ShipConsumableManager` (already routed) | — |
| ShipInstance | `carried_items` | 4 outside | `engine/order_processor.py` (TRANSFER) |
| ShipInstance | `battles_survived` / `experience` / `kills` | 1 outside | `combat/post_battle_hook.py:186` |

### Top 5 surprises (vs the review's "77 files of mutations" framing)

1. The review's headline of "77 files / direct mutations" overstates the per-attribute count. The **write-attribute** surface for Fleet+Planet+Empire+ShipInstance combined is **~30 distinct files** with concentrated heat in 5–6 engines (`order_processor`, `fleet_movement_engine`, `post_battle_hook`, `production_spawner`, `harvesting_engine`, `planet_energy_engine`). The 77 figure includes the much-larger read-access surface — those don't need mutator protocols.
2. **`fleet.location = ...` happens in only 6 places.** That's small enough that the FleetNavigationService bridge can absorb 5 of them today and the 6th (`validation/superweapon_validator.py`) is a validation false-positive (reads, not writes; needs verification in Phase 2).
3. **`Planet.populations.append` happens twice in production**, both for legitimate creation (`COLONIZE` in `order_processor.py:514`, `game_initializer.py:344` for starting population). The "300+ files mutate populations" intuition is wrong; the heat is in tick processors that read populations and call `pop.count -= ...` (per-pop mutation, not per-planet).
4. **`empire.colonies.remove()` and `empire.fleets.remove()` from outside Empire are concentrated in 4 files** (system_destroyer, superweapon_order_processor, post_battle_hook, game_initializer's `clear()`). Adding `EmpireWriteService.remove_colony(...)` is a high-leverage 5-call-site change.
5. **`PostBattleHook` is a one-stop write boundary** (`combat/post_battle_hook.py`, 222 LOC) for the strategy-side battle round-trip. It's already structurally a "write service" — Phase 5 mostly adds an `IShipInstanceMutator` parameter and renames `_apply_single_outcome`'s body to call mutator methods. Low-risk migration with high boundary-test value.

## Owner-service map (target architecture)

| Data class | Read protocol (existing) | Write protocol (new) | Owner service(s) |
|---|---|---|---|
| Fleet | `IFleet` | `IFleetMutator` | `FleetNavigationService` (location/path slice — already exists), `FleetWriteService` (ships, orders, hierarchy, construction queue, display name, fleet_policy slice — new) |
| Planet | `IPlanet` | `IPlanetMutator` | `PlanetWriteService` (single owner — new) |
| Empire | (no protocol today; informal — `IEmpire` not declared) | `IEmpireMutator` | `EmpireWriteService` (single owner — new) |
| ShipInstance | (read protocol implicit via `IPostBattleShip` in `game/core/protocols/`) | `IShipInstanceMutator` | `ShipInstanceWriteService` (single owner — new); also wraps `ShipConsumableManager` and `ShipCargoManager` for the resource/cargo slices |

Empire has no `IEmpire` Protocol today (the type just gets passed around as `Empire`). PROJ-370 does NOT add `IEmpire`. Adding a read protocol for Empire is a separate concern; the mutator does not require its read-side twin to exist (read access remains via direct `Empire` reference). If an `IEmpire` read protocol is later desired, it's a 1-hour add.

## Protocol design template

All four mutator protocols use the same shape:

```python
# game/core/protocols/strategy_mutators.py
from typing import Protocol, runtime_checkable, TYPE_CHECKING
from game.core.hex_math import HexCoord

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.order_types import Order

@runtime_checkable
class IFleetMutator(Protocol):
    """Owns writes to Fleet state."""

    def set_location(self, fleet: "Fleet", new_location: HexCoord) -> None: ...
    def set_path(self, fleet: "Fleet", new_path: list[HexCoord]) -> None: ...
    def append_order(self, fleet: "Fleet", order: "Order") -> None: ...
    def insert_order(self, fleet: "Fleet", index: int, order: "Order") -> None: ...
    def pop_order(self, fleet: "Fleet", index: int = 0) -> "Order | None": ...
    def clear_orders(self, fleet: "Fleet") -> None: ...
    def add_ship(self, fleet: "Fleet", ship: "ShipInstance") -> None: ...
    def remove_ship(self, fleet: "Fleet", ship: "ShipInstance") -> bool: ...
    def set_display_name(self, fleet: "Fleet", name: str) -> None: ...
    def set_fleet_policy(self, fleet: "Fleet", policy: "CombatPolicy") -> None: ...
    def append_construction_item(self, fleet: "Fleet", item: dict) -> None: ...
    def pop_construction_item(self, fleet: "Fleet", index: int = 0) -> dict: ...
    def set_construction_queue_paused(self, fleet: "Fleet", paused: bool) -> None: ...
    def add_task_force(self, fleet: "Fleet", tf: "TaskForce") -> None: ...
    def remove_task_force(self, fleet: "Fleet", tf: "TaskForce") -> bool: ...
```

Implementations are thin — every method does the obvious assignment/append/pop on the Fleet, plus any invariant the data class already enforces today (e.g., `fleet.add_ship` triggers `trigger_speed_recalculation`; the mutator delegates to that method rather than reaching across it). **The mutator does not introduce new validation in v1** — that's a follow-up project. The point is to *seam* the writes, not to enrich them.

The Fleet's existing `add_ship` / `remove_ship` / `add_order` / `pop_order` / `clear_orders` / `merge_with` methods are kept and called by the mutator implementation. The mutator is a **named, mockable seam**, not a re-write of fleet semantics.

### Why two services for Fleet (not one)

`FleetNavigationService` already owns `location` + `path` writes via the "mutation bridge" pattern (`fleet_navigation_service.py:716-759`). It is the natural co-implementer of `IFleetMutator`'s navigation slice (`set_location`, `set_path`). Folding navigation into a new `FleetWriteService` would (a) require duplicating the navigation pure functions, (b) collide with PROJ-369's TurnEngine work, (c) create the same "UI projection vs execution" split the navigation service was specifically built to avoid (`fleet_navigation_service.py:1-23`). The right move is: `FleetWriteService` owns the non-navigation writes; `FleetNavigationService` keeps owning navigation. Both implement `IFleetMutator`. The composite is constructed in `GameSession.__init__` (citing `game/strategy/engine/game_session.py:99-108`) — a 10-line `_FleetMutatorComposite` that delegates each method to the right backend — and is passed into `TurnEngineConfig.create_default()` (post-PROJ-369) as `fleet_mutator`, or threaded directly into the engines and hooks that need it (pre-PROJ-369). (Or: a single `FleetWriteService` that holds a reference to a `FleetNavigationService` and forwards `set_location`/`set_path` to it. Equivalent. Phase 2 picks one based on which reads cleaner.)

### Production wiring — where mutators are constructed and threaded

Every mutator is **constructed inside `GameSession.__init__`** (`game/strategy/engine/game_session.py:99-108`, where `TurnEngine` is constructed today) and threaded to its consumers either via `TurnEngineConfig` (post-PROJ-369) or directly via constructor kwargs (pre-PROJ-369). Concretely:

- **Post-PROJ-369 (preferred path).** `TurnEngineConfig.create_default()` is the default-population point. The config gains four new fields — `fleet_mutator: IFleetMutator`, `planet_mutator: IPlanetMutator`, `empire_mutator: IEmpireMutator`, `ship_mutator: IShipInstanceMutator` — populated from the services constructed in `GameSession.__init__`. Engines that need a mutator pull it from `config.<x>_mutator`. The four AST-guarded write surfaces converge on a single construction site.
- **Pre-PROJ-369 (transitional path).** Each new write service is passed directly into the engines / hooks that need it (`OrderProcessor`/`order_handlers/`, `PostBattleHook`, `FleetMovementEngine`, `SuperweaponOrderProcessor`, `SystemDestroyer`, `GameInitializer`, `HarvestingEngine`, `EnvironmentalHazardEngine`) via constructor kwargs threaded from `GameSession.__init__`. The migration to `TurnEngineConfig`-routed wiring happens when PROJ-369 closes.

PROJ-370 does **not** wire mutators through any `_facade_state.py` slice. The strategy facade is a UI-projection / read-side surface; the write boundary belongs at the session-construction site so the test surface and the production surface share one wiring path. Per the joint Codex+Claude review (2026-05-06), this corrects the earlier r001 plan that had pointed at `game/strategy/facade/slices/_facade_state.py` as the wiring site.

## Alternatives considered

| Alternative | Rejected? | Reason |
|---|---|---|
| **Frozen dataclass conversion** (mark `Fleet`/`Planet`/etc. `@dataclass(frozen=True)`) | Rejected | (a) Fleet/Empire are not currently dataclasses — would require wholesale rewrite. (b) Frozen dataclasses cannot accumulate state across ticks; the per-turn mutation pattern is intrinsic to the strategy layer. (c) Forces every mutator to construct a new instance per tick; performance and identity-comparison invariants (`Fleet.__eq__`, `Empire.__eq__`) break. |
| **Full immutability via `replace(fleet, location=...)` everywhere** | Rejected | Same identity issue as frozen. The write-traffic heatmap shows ~80 sites; rewriting the engines around `replace` would be a 10× project. |
| **Event-sourced writes** (every mutation is an event applied by an event store) | Rejected for v1 | Solves a problem we don't have — undo/redo, replay reconstruction. PROJ-312's replay store already captures battle replay; strategy turns are not replayed at this granularity. The architecture is a target for *much* later (post-PROJ-372). |
| **Command pattern with undo/redo** | Rejected for v1 | Same as event-sourced — adds a layer for benefits not currently demanded. |
| **Single mega `IStrategyMutator` covering all four data types** | Rejected | Violates Interface Segregation. An engine that only writes Planet shouldn't import a mutator that exposes 50+ Fleet / Empire / ShipInstance methods. Four narrow protocols is the intentional granularity. |
| **Read DTOs replace read protocols** (push `facade/dto/` into the engine layer) | Rejected | DTOs are immutable snapshots — fine for UI but a footgun in the engine layer where staleness across a tick boundary matters. The tech-debt review #3 calls out the *write* gap, not the read gap. Read protocols stay; DTOs stay UI-only. |
| **Validate invariants in the mutator** (capacity ≥ current, population ≥ 0, etc.) | Deferred | The review's Phase 3 of its remediation suggests this. PROJ-370 keeps mutators pass-through to limit blast radius. A follow-up project — call it "Mutator Invariants" — adds validation once the seams are stable. |
| **Generate mutators from the data class via metaclass / `__init_subclass__`** | Rejected | Hidden coupling, AST-guard evasion, terrible IDE experience. Hand-written narrow protocols are 200 lines total — not worth the cleverness. |

## AST-guard policy

Each phase ships an AST-guard test entry. The harness lives at `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` and is parameterized over (target_class, attribute_set, allowlist).

**Rules enforced** (per attribute):
1. No bare `Store` to `obj.attr` outside the allowlist (i.e., `fleet.location = X` is illegal except in `data/fleet.py` and `services/fleet_navigation_service.py`).
2. No `AugStore` to `obj.attr` outside the allowlist (`fleet.path += [...]` is illegal too).
3. No `obj.attr.append/.pop/.remove/.extend/.clear/.insert(...)` outside the allowlist for collection-typed attributes.
4. No `obj.attr[key] = value` outside the allowlist for dict-typed attributes.

**The harness ignores `tests/`, `combat_lab/`, `Tools/`, `simulation_tests/`** by default (test code may legitimately stub state). It scans `game/`. The allowlist per attribute is short and explicit, defined in the test parameterization.

**Risk:** AST-guard tests are fragile when the codebase shifts. Mitigation:
- Use `ast.parse` (stdlib), not regex. The parser handles multi-line, comments, and quoted strings cleanly.
- Allowlists are **path-based** (`game/strategy/data/fleet.py`), not regex-based.
- Each AST-guard failure prints the offending file:line + the original-target attribute, with a one-line "did you mean to call `<mutator>.set_X(...)`?" hint.
- The harness is itself unit-tested with a synthetic in-memory fixture (a temp Python module containing both legal and illegal writes; the harness must catch the illegal one).

The review report names AST-guard fragility as a risk; PROJ-370 hardens the test in the same change.

## Risks

1. **Large blast radius.** ~30 files, ~80 mutation sites total. Mitigation: phased migration (one data class at a time), AST guard runs after each phase, `GameSession.__init__` (and post-PROJ-369 `TurnEngineConfig.create_default()`) wires defaults so existing tests Don't Reach For The Mutator manually.
2. **Save/load compatibility.** `to_dict`/`from_dict` round-trips happen *inside* the data class; the mutator is for write-from-outside. Save format unchanged. Mitigation: explicit out-of-scope item, plus a regression test that loads a pre-PROJ-370 savegame on a post-PROJ-370 build.
3. **Performance from indirection.** Every `fleet.location = ...` becomes a method call. For a 100-fleet × 100-tick simulation, that's 10 K extra Python frame entries per turn. Profile before declaring "no perf hit" — the budget is "no measurable regression on the 3-empire end-turn smoke" (≤ 5 % wall-time). Mitigation: hot-path mutators (`set_location`, `set_path`, per-pop count update) are 1-2 line methods; CPython inlines small frames effectively.
4. **AST-guard fragility.** See above — hardened in the same change.
5. **Scope creep into PROJ-372 (Galaxy/Planet god-class).** Planet's mutation surface overlaps with PROJ-372's structural work. Mitigation: PROJ-370 only seams the *current* mutation surface. PROJ-372 may later move some mutations into a different owner service; if so, it updates the protocol implementation, not the protocol shape. The protocol is stable. (See Decisions log entry on sequencing.)
6. **Coordination with PROJ-368.** PROJ-368 rewrites OrderProcessor — the single biggest planet/fleet writer. If both projects run in parallel, we'd have merge churn. Mitigation: **sequence them** — PROJ-368 lands first (it's already planned), then PROJ-370 Phase 3 (Planet) absorbs the new handler structure. PROJ-370's AST guard then locks the boundary going forward. (See Decisions log.)
7. **Unit-test discoverability.** New `tests/unit/strategy/services/test_*_write_service.py` files must follow the existing naming convention. Mitigation: one test file per service, mirror the existing service-test patterns (e.g., `tests/unit/strategy/services/test_fleet_navigation_service.py` if one exists, otherwise the cargo-transfer-service tests).
8. **`environmental_hazard_engine` writes both Fleet and ShipInstance.** It mutates `ship.is_alive`, `ship.current_hp` (Phase 5 surface) AND it can prune fleets via `Fleet.remove_ship` (Phase 2 surface). The two-phase migration is fine — engine takes both mutators in its ctor. Mitigation: explicit cross-phase note in `decisions.md`.

## Dependencies & sibling projects

- **PROJ-368 (OrderProcessor decomposition).** Heavy interaction. PROJ-368 rewrites the biggest writer of `Planet.populations` / `Planet.facilities` / `Fleet.ships`. **Sequencing decision: PROJ-368 lands first.** PROJ-370 Phase 3 then targets the new handler files (`order_handlers/transfer.py`, `order_handlers/colonize.py`) instead of the legacy monolith. Net code change in PROJ-370 is *smaller* if PROJ-368 lands first.
- **PROJ-369 (TurnEngine decomposition).** Light interaction. PROJ-369 changes how engines are wired (lazy → eager `TurnEngineConfig.create_default`); PROJ-370 adds new constructor kwargs (the mutator). Both projects extend the same factory site cleanly.
- **PROJ-371 (Command dispatch registry).** No interaction. Commands flow through a different layer (UI → command handler → order creation); they don't mutate strategy data directly.
- **PROJ-372 (Galaxy/Planet god-class decomposition).** Concurrent surface. PROJ-372 may extract `PlanetProductionCalculator` / `HabitabilityCalculator` services that read Planet but don't write. PROJ-370's `PlanetWriteService` is the natural mutation peer those calculators interact with. Sequencing: **PROJ-370 lands before PROJ-372**, because PROJ-372 will *use* the mutator protocol the moment it extracts a service that needs to update planet state.

## Open questions for the user

1. **Service granularity for Fleet** — split into `FleetNavigationService` + `FleetWriteService`, or fold everything into `FleetWriteService` (which depends on `FleetNavigationService` for its navigation slice)? Both work; the design doc reasons for the split. **Architect recommendation:** keep `FleetNavigationService` separate; add `FleetWriteService` for the rest; construct the composite in `GameSession.__init__` and thread it via `TurnEngineConfig` (post-PROJ-369) or direct kwargs (pre-PROJ-369) so engines see one `IFleetMutator`.
2. **Scope of `IShipInstanceMutator`** — should it cover `cargo_contents` and `consumable_levels`, even though `ShipCargoManager` and `ShipConsumableManager` already encapsulate those writes? Or should the mutator delegate to those existing managers (1-line forwarders) so the AST guard catches **all** ShipInstance writes, including the manager-internal ones? **Architect recommendation:** delegate. AST guard catches all ShipInstance writes. The managers stay. Their writes are routed through the mutator; the mutator forwards to them. Two seams, one rule.
3. **AST-guard granularity** — fail per-file (one offender per phase = test fail) or whitelist-with-warning (test passes with warning)? **Architect recommendation:** fail per-file. The review report explicitly calls "no compiler error; runtime crash in production" as the top risk; the AST guard is the compiler we don't have.
4. **Should we add `IEmpire` (read protocol) in this project?** Empire has no read protocol today; the mutator can be added without it. **Architect recommendation:** out of scope. Adding it is a 1-hour follow-up; doing it here invites scope creep.
5. **Ship in 4 PRs (one per phase) or 1 PR?** The 03c protocol opt-in handles this — phases ship as separate phase-branches with cumulative review. **Architect recommendation:** 03c per-phase branches. Each AST guard becomes a cumulative-review checkpoint.
6. **Save/load tripwire** — should the final-verification checklist include a manual "load a pre-PROJ-370 savegame" step? **Architect recommendation:** yes, add to the user smoke checklist.
7. **Performance budget** — 5 % wall-time on the 3-empire smoke? Or stricter? **Architect recommendation:** 5 %. 100 fleets × 100 ticks × ~5 mutator-routed writes/turn = ~50 K extra Python frames; CPython on a modern Windows box does ~50 ns/frame, so ~2.5 ms wall-time. Below the smoke-test noise floor.
8. **Should `FleetNavigationService` and the new write services be reachable from `StrategySessionFacade`?** Engines get them via constructor kwargs. UI today doesn't write through them — UI emits commands. **Architect recommendation:** no. Don't expose mutators on the facade; that re-opens the same write boundary the project closed.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
