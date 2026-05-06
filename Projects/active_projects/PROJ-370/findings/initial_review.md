# PROJ-370 — Initial Review (Write-Traffic Heatmap)

> Source: write-traffic survey of `game/strategy/data/` mutations performed during planning, 2026-05-05.
> Cross-reference: `AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md` (target #3).
> ≤ 2 pages by design — the heatmap is the deliverable, not narrative.

## Method

For each candidate data class (`Fleet`, `Planet`, `Empire`, `Galaxy`, `ShipInstance`, `Star`, `StarSystem`), grep `game/` for direct attribute writes from outside the data class itself. Patterns counted: `obj.attr = ...`, `obj.attr += ...`, `obj.attr[k] = ...`, `obj.attr.append/.pop/.remove/.extend/.clear/.insert(...)`. Reads (e.g., `if fleet.location == X`) are excluded.

## Heatmap (sortable)

| Rank | Data class × attribute | Outside writers | Top writer files | In scope? |
|---|---|---|---|---|
| 1 | Planet × `populations` (collection ops) | 2 | `engine/order_processor.py:514` (COLONIZE), `engine/game_initializer.py:344` | YES — Phase 3 |
| 2 | Planet × `facilities` (collection ops) | 3 | `engine/order_processor.py:645`, `engine/production_spawner.py:202`, `quickstart_builder.py:309` | YES — Phase 3 |
| 3 | Planet × `stockpile` (`[k] = v`) | 1 outside Planet+Empire | `engine/organics_consumption_engine.py:107`. Empire-deser shim at `data/empire.py:183` is data-class-internal. | YES — Phase 3 |
| 4 | Planet × `energy` family | 5 in 1 file | `engine/planet_energy_engine.py` (5 sites) | YES — Phase 3 |
| 5 | Planet × `atmosphere` / `atmosphere_target` | 2 files | `engine/atmosphere_engine.py`, `engine/game_initializer.py` | YES — Phase 3 |
| 6 | Planet × modifier targets (`gravity_target`, `water_target`, `radiation_shielding*`) | 1 file | `engine/planet_modifier_effect_engine.py` (2 sites) | YES — Phase 3 |
| 7 | Planet × `staging_yard` | inside Planet only | (well-encapsulated already via `add_to_staging_yard` / `remove_from_staging_yard`) | Allowlist-only |
| 8 | Planet × `orders` (collection ops) | 1 outside | `engine/planet_command_handlers.py:134` | YES — Phase 3 |
| 9 | Fleet × `location` (`= ...`) | 6 in 5 files | `engine/fleet_movement_engine.py:182`, `order_processor.py` (×2), `engine/handlers/movement.py`, `engine/handlers/base.py`, `validation/superweapon_validator.py` (verify — likely read-only) | YES — Phase 2 |
| 10 | Fleet × `path` (`= ...`) | 1 (already routed) | `services/fleet_navigation_service.py:755` (the canonical mutation bridge) | YES — already routed; protocol-conformance only |
| 11 | Fleet × `orders` (collection ops) | 4 outside Fleet itself | `data/order_serializer.py:231` (allowlist), `data/fleet_pursuer_tracker.py:141` (allowlist), `engine/handlers/build.py:43`, `ui/screens/strategy_screen_order_editing.py:90` | YES — Phase 2 |
| 12 | Fleet × `ships` (collection ops, inside fleet) | 5 sites in `data/fleet.py` itself + `simulation/systems/battle_engine.py` (sim-side) + `combat/post_battle_hook.py` (via `Fleet.remove_ship`) | `combat/post_battle_hook.py:192` calls `fleet.remove_ship` (already a method) | YES — Phase 2 (already mostly routed via `Fleet.add_ship`/`remove_ship`) |
| 13 | Fleet × `display_name` | 1 outside | `ui/screens/strategy_fleet_ops.py` | YES — Phase 2 |
| 14 | Fleet × `fleet_policy` | 1 outside | `ui/screens/battle_setup/controller.py` | YES — Phase 2 |
| 15 | Fleet × `construction_queue` | 1 outside | `ui/screens/strategy_build_queue_manager.py` | YES — Phase 2 |
| 16 | Empire × `colonies` (collection ops) | 4 outside | `engine/superweapon_order_processor.py:358,606`, `services/system_destroyer.py:161`, `engine/game_initializer.py:86` | YES — Phase 4 |
| 17 | Empire × `fleets` (collection ops) | 4 outside Empire itself | `combat/post_battle_hook.py:214`, plus `ui/screens/battle_setup_state.py` (×3, but those are UI-state-only — verify) | YES — Phase 4 |
| 18 | Empire × `_fleet_resource_pool` | 0 outside | (private — already encapsulated via `add_resources` / `consume_resources`) | Out — already private |
| 19 | Empire × `max_storage` | 1 outside | `engine/harvesting_engine.py` | YES — Phase 4 |
| 20 | ShipInstance × `is_alive` | 4 outside (3 in scope, 1 sim) | `combat/post_battle_hook.py:121,182`, `engine/environmental_hazard_engine.py:202`, `simulation/managers/retreat_manager.py` (sim — verify Ship vs ShipInstance) | YES — Phase 5 |
| 21 | ShipInstance × `is_derelict` | 1 outside | `combat/post_battle_hook.py:183` | YES — Phase 5 |
| 22 | ShipInstance × `current_hp` | 3 outside | `combat/post_battle_hook.py:122`, `engine/environmental_hazard_engine.py:196,198` | YES — Phase 5 |
| 23 | ShipInstance × `components` (whole-dict) | 1 outside (canonical) | `combat/post_battle_hook.py:179` | YES — Phase 5 |
| 24 | ShipInstance × `cargo_contents` / `consumable_levels` | inside `ShipCargoManager`/`ShipConsumableManager` | (already encapsulated in managers — allowlist) | YES — Phase 5 (allowlist managers) |
| 25 | ShipInstance × `carried_items` (collection ops) | 4 in 1 file | `engine/order_processor.py` (TRANSFER family — line 582, 613, 635) | YES — Phase 5 |
| 26 | ShipInstance × `battles_survived` / `experience` / `kills` | 1 outside | `combat/post_battle_hook.py:186` | YES — Phase 5 |
| 27 | Galaxy × all mutations | already routed through `GalaxyEntityRegistry` + `GalaxySpatialIndex` (PROJ-87 Phase 6) | `data/galaxy.py:286-398` | OUT — PROJ-372 territory |
| 28 | StarSystem × all mutations | generation-time only (no engine writes after build) | (`data/galaxy.py`, `data/galaxy_system_generator.py`) | OUT — no engine leverage |
| 29 | Star × all mutations | generation-time only | (`data/stars.py`, `data/galaxy_system_generator.py`) | OUT — no engine leverage |

**Total in-scope mutation sites**: ~80 across ~30 files. Concentrated in 5 engines (`order_processor`, `post_battle_hook`, `fleet_movement_engine`, `planet_energy_engine`, the planet modifier engines), with ~10 single-site UI/handler outliers.

## Top 5 surprises

1. **The review's "77 files of mutations" framing overstates the write surface.** Counting only writes (not reads) reduces the file count to ~30, with concentrated heat in 5–6 engines. The 77 figure includes the read surface, which is already protocol-covered (`IFleet`, `IPlanet`, etc.).
2. **`fleet.location = ...` happens in only 6 places.** Five of them are clearly engine-side; the sixth (`validation/superweapon_validator.py`) needs a Phase 2 verification pass — likely a false positive (read access on the LHS of a comparison).
3. **`PostBattleHook` is an unusually clean choke point.** `combat/post_battle_hook.py` is structurally already a "write service" — 222 LOC, single entry point (`apply_outcome_to_fleets`), all writes flow through `_apply_single_outcome` and `_apply_survivor_outcome`. Phase 5 is mostly a parameter add + 7 line replacements + AST guard. Highest leverage per line of work in the project.
4. **PROJ-87 already extracted the Fleet/ShipInstance read-side delegates** (`FleetCapabilityCalculator`, `FleetConsumableAggregator`, `ShipCargoManager`, `ShipConsumableManager`, etc., 2026-02-10). PROJ-370 is the **write-side complement**. The naming convention is set; the new services follow it (`FleetWriteService`, `ShipInstanceWriteService`, etc.).
5. **`FleetNavigationService.calculate_fleet_next_hex`** (`services/fleet_navigation_service.py:716-759`) is *already* the canonical "mutation bridge" pattern PROJ-370 generalizes. Its docstring literally says "the mutation bridge — it wraps the pure compute_next_step() function and applies the necessary mutations to the Fleet object". The whole project is "do this for the other three data types, and AST-guard the result."

## Owner-service decision (target architecture, mirrored from `design.md`)

| Data class | Read protocol (existing) | Write protocol (new) | Owner service(s) | Phase |
|---|---|---|---|---|
| Fleet | `IFleet` | `IFleetMutator` | `FleetNavigationService` (location/path) + `FleetWriteService` (everything else) | 2 |
| Planet | `IPlanet` | `IPlanetMutator` | `PlanetWriteService` (single owner) | 3 |
| Empire | (none today; out-of-scope add) | `IEmpireMutator` | `EmpireWriteService` | 4 |
| ShipInstance | (implicit — `IPostBattleShip`) | `IShipInstanceMutator` | `ShipInstanceWriteService` (forwards cargo/consumables to existing managers) | 5 |
| Galaxy | `IStarSystem` (per-system) | OUT | (PROJ-372) | — |

## AST-guard plan (4 parameter cases)

- Phase 1: ship the harness with empty disallowlists; the test passes structurally.
- Phase 2: flip Fleet's disallowlist — 10 attributes, 8 allowlist paths.
- Phase 3: flip Planet's disallowlist — 21 attributes, 2 allowlist paths.
- Phase 4: flip Empire's disallowlist — 6 attributes, 2 allowlist paths.
- Phase 5: flip ShipInstance's disallowlist — 16 attributes, 6 allowlist paths.

Total: 53 attribute names, 18 distinct allowlisted file paths, 4 AST-guard parameter cases.
