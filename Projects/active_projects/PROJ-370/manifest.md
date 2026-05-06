# PROJ-370 File Manifest

> Generated during planning. Used by `/proj-parallel` for conflict detection.
> Updated if implementation discovers additional files.
> Per phase: heavy on tests + one new module/service file. Engines are touched in-place.

## Phase 1: Mutator-protocol foundation + AST guard harness

| File | Type | Notes |
|------|------|-------|
| `game/core/protocols/strategy_mutators.py` | Production (NEW) | 4 `@runtime_checkable` Protocol classes: `IFleetMutator`, `IPlanetMutator`, `IEmpireMutator`, `IShipInstanceMutator`. Skeletons only — methods declared, no implementations bound yet. |
| `game/core/protocols/__init__.py` | Production (modify) | Re-export the new protocols for `from game.core.protocols import IFleetMutator` ergonomics. |
| `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` | Test (NEW) | Parameterized AST-guard harness. 4 parameter cases — Fleet, Planet, Empire, ShipInstance — each with `attribute_set` and `allowlist`. Phase 1 ships with empty disallowlists (test passes trivially). |
| `tests/unit/strategy/data/test_mutator_boundary_ast_guard_self_test.py` | Test (NEW) | Sanity test for the AST harness itself: synthetic in-memory module containing both legal and illegal writes; harness must catch the illegal one. |
| `docs/02_PATTERNS.md` | Doc (modify) | New pattern entry: "Read/Write Protocol Pair" — references `IFleet`/`IFleetMutator`, `IPlanet`/`IPlanetMutator`, etc. as the canonical examples. |

## Phase 2: Fleet — `IFleetMutator` + route engine writes

| File | Type | Notes |
|------|------|-------|
| `game/core/protocols/strategy_mutators.py` | Production (modify) | Flesh out `IFleetMutator` method signatures (kept as a Protocol — abstract). |
| `game/strategy/services/fleet_write_service.py` | Production (NEW) | `FleetWriteService` — implements `IFleetMutator` for orders, ships, hierarchy, construction queue, display name, fleet_policy slice. ~150 LOC. |
| `game/strategy/services/fleet_navigation_service.py` | Production (modify) | Add `IFleetMutator`-conforming method aliases (`set_location`, `set_path`) on top of the existing `calculate_fleet_next_hex` mutation bridge. ~10 LOC delta. |
| `game/strategy/engine/fleet_movement_engine.py` | Production (modify) | Constructor accepts `fleet_mutator: IFleetMutator`. `fleet.location = next_hex` (line 182) → `self._fleet_mutator.set_location(fleet, next_hex)`. |
| `game/strategy/engine/order_processor.py` | Production (modify) | Constructor accepts `fleet_mutator`. Routed writes: `fleet.location` (×2 sites). |
| `game/strategy/engine/conflict_resolution_engine.py` | Production (modify) | Constructor accepts `fleet_mutator`. Routed writes for any fleet location/path mutation in conflict resolution. |
| `game/strategy/engine/handlers/movement.py` | Production (modify) | Routed: `fleet.location` write. |
| `game/strategy/engine/handlers/base.py` | Production (modify) | Routed: `fleet.location` and `fleet.orders` writes. |
| `game/strategy/engine/handlers/order_queue.py` | Production (modify) | Routed: `fleet.orders` mutations (3 sites). |
| `game/strategy/engine/handlers/build.py` | Production (modify) | Routed: `fleet.orders.insert(0, build_order)` (line 43). |
| `game/strategy/data/order_serializer.py` | Production (modify) | Routed: `fleet.orders.pop(i)` (line 231). |
| `game/strategy/data/fleet_pursuer_tracker.py` | Production (modify) | Routed: `pursuer.orders.pop(i)` (line 141). |
| `game/strategy/validation/superweapon_validator.py` | Production (verify) | Suspected read-only — verify in Phase 2 task; if true, no change. |
| `game/strategy/engine/game_session.py` | Production (modify) | Construct `FleetWriteService` and pass into `TurnEngineConfig` (post-PROJ-369) or directly into `OrderProcessor`/`PostBattleHook`/etc. constructors (pre-PROJ-369). Sequencing-dependent — PROJ-369 lands first per joint review. |
| `tests/unit/strategy/services/test_fleet_write_service.py` | Test (NEW) | ≥ 8 unit tests against `FleetWriteService` with a real Fleet. |
| `tests/unit/strategy/services/test_fleet_navigation_service_mutator.py` | Test (NEW) | Verify `FleetNavigationService` satisfies the `IFleetMutator` navigation slice. |
| `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` | Test (modify) | Fleet AST guard goes hot. Allowlist: `game/strategy/data/fleet.py`, `game/strategy/services/fleet_navigation_service.py`, `game/strategy/services/fleet_write_service.py`. Disallowlist: `location`, `path`, `ships`, `orders`, `construction_queue`, `display_name`, `fleet_policy`, `_task_forces`. |

## Phase 3: Planet — `IPlanetMutator` + route engine writes

| File | Type | Notes |
|------|------|-------|
| `game/core/protocols/strategy_mutators.py` | Production (modify) | Flesh out `IPlanetMutator` method signatures. |
| `game/strategy/services/planet_write_service.py` | Production (NEW) | `PlanetWriteService` — single owner of Planet writes. ~200 LOC. |
| `game/strategy/engine/order_processor.py` | Production (modify) | NOTE: PROJ-368 reshapes this file; PROJ-370 Phase 3 targets the post-PROJ-368 `order_handlers/` package. Routed: `planet.populations.append`, `planet.facilities.append`, `planet.staging_yard.pop`, `planet.owner_id = ...`. |
| `game/strategy/engine/order_handlers/colonize.py` | Production (modify) | (Post-PROJ-368) Routes population/facility/owner writes through `IPlanetMutator`. |
| `game/strategy/engine/order_handlers/transfer.py` | Production (modify) | (Post-PROJ-368) Routes staging-yard, populations, ship.carried_items writes through `IPlanetMutator` + `IShipInstanceMutator`. |
| `game/strategy/engine/production_spawner.py` | Production (modify) | Routed: `planet.facilities.append(facility)` (line 202). |
| `game/strategy/engine/production_engine.py` | Production (modify) | Routed: any direct stockpile/construction_queue mutations. |
| `game/strategy/engine/harvesting_engine.py` | Production (modify) | Routed: stockpile additions on harvest output. |
| `game/strategy/engine/planet_energy_engine.py` | Production (modify) | Routed: 5 sites mutating `energy`/`energy_capacity`/`energy_generation`. |
| `game/strategy/engine/atmosphere_engine.py` | Production (modify) | Routed: `atmosphere`/`atmosphere_target` writes. |
| `game/strategy/engine/organics_consumption_engine.py` | Production (modify) | Routed: `colony.stockpile[resource_id] = available - supplied` (line 107). |
| `game/strategy/engine/planet_modifier_effect_engine.py` | Production (modify) | Routed: `gravity_target`/`water_target`/`radiation_shielding_target` mutations. |
| `game/strategy/engine/planet_command_handlers.py` | Production (modify) | Routed: `planet.orders.pop(cmd.order_index)` (line 134). |
| `game/strategy/engine/game_initializer.py` | Production (modify) | Routed: `home_planet.populations.append(initial_pop)` (line 344) + `empire.colonies.clear()` (line 86 — Phase 4 territory but flagged). |
| `game/strategy/quickstart_builder.py` | Production (modify) | Routed: `home_planet.facilities.append(facility)` (line 309). |
| `game/strategy/engine/game_session.py` | Production (modify) | Construct `PlanetWriteService` and pass into `TurnEngineConfig` (post-PROJ-369) or directly into `OrderProcessor`/`PostBattleHook`/etc. constructors (pre-PROJ-369). Sequencing-dependent — PROJ-369 lands first per joint review. |
| `tests/unit/strategy/services/test_planet_write_service.py` | Test (NEW) | ≥ 10 unit tests against `PlanetWriteService` with a real Planet. |
| `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` | Test (modify) | Planet AST guard goes hot. Allowlist: `game/strategy/data/planet.py`, `game/strategy/services/planet_write_service.py`. Disallowlist: `populations`, `facilities`, `stockpile`, `staging_yard`, `construction_queue`, `orders`, `owner_id`, `atmosphere`, `atmosphere_target`, `gravity_target`, `water_target`, `radiation_shielding_target`, `energy`, `energy_capacity`, `energy_generation`, `species_configs`. |

## Phase 4: Empire — `IEmpireMutator` + route engine writes

| File | Type | Notes |
|------|------|-------|
| `game/core/protocols/strategy_mutators.py` | Production (modify) | Flesh out `IEmpireMutator` method signatures. |
| `game/strategy/services/empire_write_service.py` | Production (NEW) | `EmpireWriteService` — single owner. ~120 LOC. Includes the post-battle empty-fleet pruning (today inline at `combat/post_battle_hook.py:200-218`). |
| `game/strategy/combat/post_battle_hook.py` | Production (modify) | `_prune_empty_fleets` becomes `EmpireWriteService.prune_empty_fleets`. Hook accepts `empire_mutator` injected via spec compiler. |
| `game/strategy/engine/superweapon_order_processor.py` | Production (modify) | Routed: `emp.colonies.remove(target_planet)` (lines 358, 606). |
| `game/strategy/services/system_destroyer.py` | Production (modify) | Routed: `emp.colonies.remove(planet)` (line 161). |
| `game/strategy/engine/game_initializer.py` | Production (modify) | Routed: `empire.colonies.clear()` (line 86), `empire.colonies.append(...)` if any. |
| `game/strategy/engine/harvesting_engine.py` | Production (modify) | Routed: `empire.max_storage` writes. |
| `game/strategy/data/empire.py` | Production (modify) | The deserialization shim `colonies[0].stockpile = dict(value)` at line 183 — verify whether this needs to route through `PlanetWriteService` (Phase 3 territory) or stays inside `Empire.from_dict` as data-class-owned (preferred). |
| `game/strategy/engine/game_session.py` | Production (modify) | Construct `EmpireWriteService` and pass into `TurnEngineConfig` (post-PROJ-369) or directly into `OrderProcessor`/`PostBattleHook`/etc. constructors (pre-PROJ-369). Sequencing-dependent — PROJ-369 lands first per joint review. |
| `tests/unit/strategy/services/test_empire_write_service.py` | Test (NEW) | ≥ 6 unit tests against `EmpireWriteService` with a real Empire. |
| `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` | Test (modify) | Empire AST guard goes hot. Allowlist: `game/strategy/data/empire.py`, `game/strategy/services/empire_write_service.py`. Disallowlist: `colonies`, `fleets`, `_fleet_resource_pool`, `max_storage`, `built_ship_designs`. |

## Phase 5: ShipInstance — `IShipInstanceMutator` + post-battle hook

| File | Type | Notes |
|------|------|-------|
| `game/core/protocols/strategy_mutators.py` | Production (modify) | Flesh out `IShipInstanceMutator` method signatures. |
| `game/strategy/services/ship_instance_write_service.py` | Production (NEW) | `ShipInstanceWriteService` — single owner. Forwards `cargo_contents`/`consumable_levels` writes to existing `ShipCargoManager`/`ShipConsumableManager`. ~150 LOC. |
| `game/strategy/combat/post_battle_hook.py` | Production (modify) | `_apply_survivor_outcome` and `_apply_single_outcome` route writes (`is_alive`, `is_derelict`, `current_hp`, `components`, `battles_survived`) through `IShipInstanceMutator`. Hook signature accepts `ship_instance_mutator`. |
| `game/strategy/engine/environmental_hazard_engine.py` | Production (modify) | Routed: `ship.current_hp = new_hp` (line 196), `ship.is_alive = False` (line 202). Note this engine *also* needs `IFleetMutator` for `Fleet.remove_ship` in cascade — already wired in Phase 2. |
| `game/strategy/engine/order_processor.py` | Production (modify) | (Post-PROJ-368: `order_handlers/transfer.py`) Routed: `ship.carried_items.append/.pop`. |
| `game/strategy/data/ship_consumable_manager.py` | Production (modify) | `IShipInstanceMutator.set_consumable_level` forwards here. May not need direct change — depends on whether the manager already accepts an `IShipInstanceMutator` (it doesn't today; minor refactor). |
| `game/strategy/data/ship_cargo_manager.py` | Production (modify) | Same as above for cargo. |
| `game/simulation/managers/retreat_manager.py` | Production (verify) | Mutates `ship.is_alive` — verify whether this is a *simulation-side* `Ship`, not the strategy-side `ShipInstance`. If sim-side, out of scope. |
| `game/strategy/engine/game_session.py` | Production (modify) | Construct `ShipInstanceWriteService` and pass into `TurnEngineConfig` (post-PROJ-369) or directly into `OrderProcessor`/`PostBattleHook`/etc. constructors (pre-PROJ-369). Sequencing-dependent — PROJ-369 lands first per joint review. |
| `tests/unit/strategy/services/test_ship_instance_write_service.py` | Test (NEW) | ≥ 8 unit tests, including a "post-battle round-trip" integration that drives `apply_outcome_to_fleets` end-to-end through the mutator. |
| `tests/unit/strategy/combat/test_post_battle_hook.py` | Test (modify) | Existing tests parameterized over `IShipInstanceMutator` (real + mock). |
| `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` | Test (modify) | ShipInstance AST guard goes hot. Allowlist: `game/strategy/data/ship_instance.py`, `game/strategy/services/ship_instance_write_service.py`, `game/strategy/data/ship_consumable_manager.py`, `game/strategy/data/ship_cargo_manager.py`, `game/strategy/data/ship_instance_serializer.py`, `game/strategy/data/ship_instance_bridge.py`. Disallowlist: `is_alive`, `is_derelict`, `current_hp`, `components`, `cargo_contents`, `carried_items`, `consumable_levels`, `component_toggles`, `activation_states`, `experience`, `kills`, `battles_survived`. |

## Cross-phase

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/turn_engine_config.py` | Production (modify) | If PROJ-369 has landed, add `fleet_mutator: IFleetMutator`, `planet_mutator: IPlanetMutator`, `empire_mutator: IEmpireMutator`, `ship_mutator: IShipInstanceMutator` fields with `create_default()` populating them from the constructed services. |
| `docs/01_ARCHITECTURE.md` | Doc (modify) | New section: "Strategy mutator services" under the strategy-layer architecture. |
| `docs/02_PATTERNS.md` | Doc (modify) | New pattern: "Read/Write Protocol Pair". |
| `docs/systems/strategy_layer.md` | Doc (modify) | New "Write services" subsection naming the owner service per data class. |
| `Projects/active_projects/PROJ-370/decisions.md` | Project (modify) | Decision-log entries during implementation. |
