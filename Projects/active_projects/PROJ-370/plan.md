# PROJ-370: Strategy: Data Layer Boundary Protocols (separate model from mutation)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-370` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-370 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status

| Phase | Status | Checklist | Depends on |
|-------|--------|-----------|------------|
| 1. Mutator-protocol foundation + AST guard harness (no behavior change) | Complete | [phase_1_checklist.md](phase_1_checklist.md) | — |
| 2. Fleet: `IFleetMutator` + route engine writes + AST guard | Complete | [phase_2_checklist.md](phase_2_checklist.md) | phase_1 |
| 3. Planet: `IPlanetMutator` + route engine writes + AST guard | Not Started | [phase_3_checklist.md](phase_3_checklist.md) | phase_1 |
| 4. Empire: `IEmpireMutator` + route engine writes + AST guard | Not Started | [phase_4_checklist.md](phase_4_checklist.md) | phase_2, phase_3 |
| 5. ShipInstance: `IShipInstanceMutator` + post-battle hook + AST guard | Not Started | [phase_5_checklist.md](phase_5_checklist.md) | phase_2 |

## Current State
**Last Updated:** 2026-05-06
**Active Phase:** Phase 3 (Planet)
**Last Action:** Phase 2 complete. `FleetWriteService` at `game/strategy/services/fleet_write_service.py` implements `IFleetMutator` (non-nav slice); `FleetNavigationService` gained `set_location` / `set_path` methods (nav slice). Wiring at `GameSession.__init__` (constructs nav + write services and threads `fleet_mutator` through `TurnEngineConfig.create_default()` — TurnEngineConfig grew from 18 to 22 fields). Routed writes: `fleet_movement_engine.py:182`, `engine/handlers/base.py:79`, `handlers/movement.py:119`, `handlers/build.py:55+58`, `handlers/order_queue.py:244+249`, `handlers/construction_queue.py:302` (polymorphic Fleet branch only), `ui/screens/strategy_screen_order_editing.py:65+90`. AST walker hardened to skip `self.X`/`cls.X` patterns (avoids false positives from WarpPoint, simulation BattleEngine). Fleet AST guard live with 9 attributes + 13 allowlisted paths (incl. Planet data class & planet command handler for shared `orders`/`construction_queue` attribute names). 4730 strategy tests pass. New `swap_orders` mutator method added (1 swap site in handlers/order_queue.py).
**Next Action:** Phase 3 — implement `PlanetWriteService`, route Planet writes (16 attributes), flip Planet AST guard hot.
**Blockers:** None.

## Overview

`game/core/protocols/strategy_entities.py` already declares **read protocols** (`IFleet`, `IPlanet`, `IEmpire`-equivalent via `IOrderable`, `IStar`, `IStarSystem`, `IZoneOccupant`, `IAbilitySource`). What is missing — and what the strategy-layer tech-debt review at `AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md` (target #3) calls out — are **write/mutator protocols** with named owner services. Engines today reach across the model with raw attribute writes:

- `fleet_movement_engine.py:182` does `fleet.location = next_hex`
- `order_processor.py:514` does `planet.populations.append(species_pop)`
- `order_processor.py:645` does `planet.facilities.append(facility)`
- `combat/post_battle_hook.py:121,179,182` does `instance.is_alive = False`, `instance.components = new_components`, `instance.is_derelict = bool(...)`
- `organics_consumption_engine.py:107` does `colony.stockpile[resource_id] = available - supplied`
- `superweapon_order_processor.py:358` does `emp.colonies.remove(target_planet)`

PROJ-370 introduces narrow **write-protocol seams** for the four highest-traffic data types — **Fleet, Planet, Empire, ShipInstance** — names the **owner service** for each, and routes engines through that service. The read-protocol surface (`IFleet`, `IPlanet`, etc.) is **kept and extended** as the canonical query interface; engines may continue to read directly through the read protocol or through the existing read-DTOs in `game/strategy/facade/dto/`. Per phase, an **AST guard test** locks in zero direct attribute writes from outside the mutator and the data class itself, so the boundary cannot regress silently.

**Galaxy is explicitly out of this project** — its mutation surface is already small and routed through `GalaxyEntityRegistry` + `GalaxySpatialIndex`, and the deeper question of what Galaxy *should* look like is the planning premise of **PROJ-372** (Galaxy/Planet/Star god-class decomposition). Pulling Galaxy into PROJ-370 would re-litigate PROJ-372 in this project. **Star/StarSystem are also out** — their write surface today is generation-only (no engine writes them after galaxy build), so the protocol carries no leverage.

## Goals

- **Phase 1 (Foundation):** A new module `game/core/protocols/strategy_mutators.py` exists exporting `IFleetMutator`, `IPlanetMutator`, `IEmpireMutator`, `IShipInstanceMutator` Protocol skeletons. A reusable AST-guard harness lives at `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` with a parameterized fixture: given a target class, a set of attribute names, and an allowlist of files, it walks every `.py` under `game/` and fails if any other file performs `Store`/`AugStore`/`Subscript-assign`/`.append/.pop/.extend/.remove/.clear/.insert` against those attributes. The harness is configured but the four AST-guard tests start with empty allowlists/disallowlists and pass trivially. **Zero behavior change in this phase.**
- **Phase 2 (Fleet):** `IFleetMutator` is a real Protocol implemented by `FleetNavigationService` (existing — already the canonical "mutation bridge" at `fleet_navigation_service.py:716-759`) and a new `FleetWriteService` for the writes that aren't navigation (orders, ships, hierarchy, construction queue, display name). Engines and handlers stop writing `fleet.location`, `fleet.path`, `fleet.ships`, `fleet.orders`, `fleet.construction_queue`, `fleet.display_name`, `fleet.fleet_policy` directly; the AST guard goes hot. Read access via `IFleet` is unchanged. `Fleet` itself is allowed to write its own attributes (data classes own their internal state).
- **Phase 3 (Planet):** `IPlanetMutator` is a real Protocol implemented by a new `PlanetWriteService`. Routes the 13 mutation surfaces (`stockpile`, `populations`, `facilities`, `staging_yard`, `construction_queue`, `orders`, `owner_id`, `atmosphere`, `atmosphere_target`, `gravity_target`/`water_target`/`radiation_shielding_target`, `energy`, `species_configs`). Heaviest writers (`order_processor.py`, `production_spawner.py`, `harvesting_engine.py`, `planet_energy_engine.py`, `atmosphere_engine.py`, `organics_consumption_engine.py`, `planet_modifier_effect_engine.py`) route through it. AST guard goes hot.
- **Phase 4 (Empire):** `IEmpireMutator` implemented by a new `EmpireWriteService` covering `colonies`, `fleets`, `_fleet_resource_pool`, `max_storage`, `built_ship_designs`. Includes the post-battle empty-fleet pruning currently in `combat/post_battle_hook.py:200-218`. The 4 sites that mutate `empire.colonies`/`empire.fleets` from outside (`superweapon_order_processor.py`, `system_destroyer.py`, `post_battle_hook.py`, `game_initializer.py`) route through it. AST guard goes hot.
- **Phase 5 (ShipInstance):** `IShipInstanceMutator` implemented by a new `ShipInstanceWriteService` and used by `combat/post_battle_hook.py` (the canonical battle→strategy write boundary) and `environmental_hazard_engine.py`. The protocol covers `is_alive`, `is_derelict`, `current_hp`, `components`, `cargo_contents`, `carried_items`, `consumable_levels`, `component_toggles`, `activation_states`, `experience`, `kills`, `battles_survived`. AST guard goes hot.

Cross-cutting goals (every phase):

- **Zero behavior change.** Every test passes at every phase boundary. The pruning order, event-bus emission order, and side-effect sequencing inside `apply_outcome_to_fleets` and `OrderProcessor` are bit-identical.
- **Read protocol is canonical.** Engines that do not need to write keep reading through `IFleet`/`IPlanet`/etc. directly. The read-DTOs in `facade/dto/` keep their UI-only role; this project does not push them into the engine layer.
- **Owner service per protocol.** The "who owns the write?" answer is named in the design doc (one production class per mutator protocol). Engines accept the protocol, not the concrete service, in their constructors. Mutators are constructed in `GameSession.__init__` and passed via `TurnEngineConfig` (post-PROJ-369) or direct kwargs.
- **Per-phase mutator unit tests.** Each phase ships ≥ 6 focused unit tests around its mutator that drive a real data instance, verifying one mutation per test. These are the first unit-testable seams over the four data types.

## Scope

**In:**

- New module: `game/core/protocols/strategy_mutators.py` — 4 `Protocol` classes (`IFleetMutator`, `IPlanetMutator`, `IEmpireMutator`, `IShipInstanceMutator`), each `@runtime_checkable`.
- New module: `game/strategy/services/fleet_write_service.py` — implements `IFleetMutator` for the non-navigation writes (orders, ships, hierarchy, construction queue, display name, fleet policy). `FleetNavigationService` already implements the navigation slice (`location` + `path`) and is treated as a co-implementer.
- New module: `game/strategy/services/planet_write_service.py` — implements `IPlanetMutator`.
- New module: `game/strategy/services/empire_write_service.py` — implements `IEmpireMutator`.
- New module: `game/strategy/services/ship_instance_write_service.py` — implements `IShipInstanceMutator`.
- Modified files (~14): `game/strategy/engine/fleet_movement_engine.py`, `order_processor.py`, `superweapon_order_processor.py`, `production_engine.py`, `production_spawner.py`, `harvesting_engine.py`, `planet_energy_engine.py`, `atmosphere_engine.py`, `organics_consumption_engine.py`, `planet_modifier_effect_engine.py`, `planet_command_handlers.py`, `environmental_hazard_engine.py`, `game_initializer.py`, `combat/post_battle_hook.py`, `services/system_destroyer.py`, plus the engine `handlers/` subpackage (5 files).
- Modified `game/strategy/engine/game_session.py` (`GameSession.__init__`, citing `game/strategy/engine/game_session.py:99-108`) to construct the four new write services. Post-PROJ-369: also `game/strategy/engine/turn_engine_config.py` to add `fleet_mutator` / `planet_mutator` / `empire_mutator` / `ship_mutator` fields populated by `TurnEngineConfig.create_default()`.
- New tests:
  - `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` (Phase 1; 4 parameterized AST-guard cases — Fleet/Planet/Empire/ShipInstance).
  - `tests/unit/strategy/services/test_fleet_write_service.py` (Phase 2).
  - `tests/unit/strategy/services/test_planet_write_service.py` (Phase 3).
  - `tests/unit/strategy/services/test_empire_write_service.py` (Phase 4).
  - `tests/unit/strategy/services/test_ship_instance_write_service.py` (Phase 5).
- Doc updates: `docs/01_ARCHITECTURE.md` (mutator-protocol seam in the strategy layer), `docs/02_PATTERNS.md` (new pattern entry: "Read/Write Protocol Pair"), `docs/systems/strategy_layer.md` (write-services section).

**Out:**

- **Galaxy / StarSystem / Star / WarpPoint / Storm / SectorEnvironment.** Galaxy mutations already route through `GalaxyEntityRegistry`/`GalaxySpatialIndex`; the further god-class break-up is **PROJ-372**.
- **Other strategy-layer data classes:** `TaskForce`, `Squadron`, `PlanetaryFacility`, `SpeciesPopulation`, `ColonySpeciesConfig`, `Storm`, `Star`, `Order`, `RaceConfig`, `DesignMetadata`. These are smaller, mostly value-object-shaped, or written from a single owner already.
- **Combat/simulation layer (`game/simulation/`)** — `Ship`, `Component`, `BattleState`, etc. The battle engine writes its own internal model; only the strategy↔simulation hook (`PostBattleHook`) is in scope, because it writes back into the strategy `ShipInstance`.
- **UI layer** — `BattleSetupState`, panels. UI mutates strategy state through the existing facade/command stream; the strategy-side write services are the constraint, not the UI side.
- **Read DTO redesign.** `facade/dto/` stays UI-only.
- **Persistence/save format changes.** `to_dict`/`from_dict` are reads, not writes — the data class itself owns its serialization.
- **Removing the read protocols** (`IFleet`, `IPlanet`, etc.). They stay; this project adds the write twin.
- **Frozen dataclass conversion**, **event-sourced writes**, **command-pattern undo/redo**. All considered and rejected for v1 — see `design.md` § "Alternatives considered".

## Today's vs. target diff (one engine, illustratively)

**Today** (`game/strategy/engine/fleet_movement_engine.py:181-182`):
```python
old_location = fleet.location
fleet.location = next_hex
```

**Target** (Phase 2):
```python
old_location = fleet.location           # read still direct via IFleet
self._fleet_mutator.set_location(fleet, next_hex)
```

`FleetMovementEngine.__init__` accepts `fleet_mutator: IFleetMutator`. The mutator is constructed in `GameSession.__init__` (citing `game/strategy/engine/game_session.py:99-108`) and threaded via `TurnEngineConfig` (post-PROJ-369) or direct kwargs (pre-PROJ-369). The AST guard at `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` parses every file under `game/` and fails if `fleet.location = ...` appears anywhere outside `game/strategy/data/fleet.py` and `game/strategy/services/fleet_navigation_service.py`.

## Key Files

| Component | File Path |
|-----------|-----------|
| Existing read protocols | `game/core/protocols/strategy_entities.py` |
| New mutator protocols | `game/core/protocols/strategy_mutators.py` *(new)* |
| Existing canonical "mutation bridge" | `game/strategy/services/fleet_navigation_service.py` (lines 716-759) |
| New Fleet write service | `game/strategy/services/fleet_write_service.py` *(new)* |
| New Planet write service | `game/strategy/services/planet_write_service.py` *(new)* |
| New Empire write service | `game/strategy/services/empire_write_service.py` *(new)* |
| New ShipInstance write service | `game/strategy/services/ship_instance_write_service.py` *(new)* |
| Top fleet writer | `game/strategy/engine/fleet_movement_engine.py` |
| Top planet writer | `game/strategy/engine/order_processor.py` (also rewritten by PROJ-368) |
| Top ship-instance writer | `game/strategy/combat/post_battle_hook.py` |
| Empire pruning writer | `game/strategy/combat/post_battle_hook.py` (lines 200-218) |
| AST guard harness | `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` *(new)* |
| Pattern doc | `docs/02_PATTERNS.md` (new section: "Read/Write Protocol Pair") |
| Strategy layer doc | `docs/systems/strategy_layer.md` |

## Related Documents

- [design.md](design.md) — write-traffic heatmap, owner-service map, AST-guard policy, alternatives considered, dependencies/siblings, open questions.
- [decisions.md](decisions.md) — bounding decisions (which classes, which order, why) + open-questions log.
- [manifest.md](manifest.md) — file table grouped by phase.
- [findings/initial_review.md](findings/initial_review.md) — initial write-traffic heatmap and top surprises from the survey.
- Source review: `AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md` (target #3).
- Sibling projects: PROJ-368 (OrderProcessor decomposition — the biggest single writer of `Planet`), PROJ-369 (TurnEngine decomposition — orchestrator), PROJ-371 (Command dispatch registry), PROJ-372 (Galaxy/Planet/Star god-class — interacts on Planet's write surface).

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS) and `docs/systems/strategy_layer.md`
- [ ] Read the source review at `AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md` (target #3)
- [ ] Read `game/core/protocols/strategy_entities.py` to internalize the read-protocol pattern this project mirrors
- [ ] Read `game/strategy/services/fleet_navigation_service.py` lines 716-759 — the canonical "mutation bridge" the new services follow
- [ ] Read `game/strategy/combat/post_battle_hook.py` end-to-end — the most-impactful single writer in the project
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` — capture baseline pass count

### After Each Phase
- [ ] Run `pytest tests/unit/strategy/ -v --testmon` — strategy unit tests pass
- [ ] Run `pytest tests/integration/strategy/ -v --testmon` — strategy integration tests pass
- [ ] Run `python Tools/test_sharded/test_sharded.py` — sharded suite green; pass count grows monotonically
- [ ] AST guard test for the phase's data class is GREEN (and starts FAILING if a regression is introduced)
- [ ] Update `Current State` in this plan with handoff context for the next phase worker

### Final Verification
- [ ] Sharded suite green; pass count ≥ baseline + new tests (≥ 30 new mutator-service tests + 4 AST-guard parameter cases)
- [ ] All four AST guards GREEN (`fleet.location`, `planet.populations`, `empire.colonies`, `instance.is_alive` and the rest enumerated per phase)
- [ ] `git grep -nE "fleet\.location\s*=" game/` returns hits only in `fleet.py` and `fleet_navigation_service.py`
- [ ] `git grep -nE "planet\.(populations|facilities|stockpile|staging_yard)\." game/strategy/engine/` returns zero `.append/.pop/.remove/.clear/.insert` results
- [ ] `git grep -nE "instance\.(is_alive|is_derelict|components)\s*=" game/` returns hits only in `ship_instance.py` and `ship_instance_write_service.py`
- [ ] `docs/02_PATTERNS.md` has a new section "Read/Write Protocol Pair" with the four protocol/service pairs as worked examples
- [ ] `docs/systems/strategy_layer.md` has a "Write services" subsection naming the owner service per data class
- [ ] User-led smoke: 3-empire end-turn produces bit-identical event log compared to baseline (the closest thing to a behavior-change tripwire)

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off (foundation + AST harness)
- [ ] All Phase 2 tasks checked off (Fleet)
- [ ] All Phase 3 tasks checked off (Planet)
- [ ] All Phase 4 tasks checked off (Empire)
- [ ] All Phase 5 tasks checked off (ShipInstance)
- [ ] All tests passing (sharded suite green)
- [ ] All four AST guards GREEN
- [ ] Audit passed (no significant issues)
- [ ] User verified
