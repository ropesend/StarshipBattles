# Swarm 01 — Architecture: Per-Tick and End-of-Turn Phase Map

> Source: parallel Explore agent (architecture analyst). Captured here because Explore agents are read-only.

Reference context: `TURN PERF` logs from QA session `20260510_165332` show **total ~7-8 s/turn** on the tiny scenario (2 empires, 2 planets, handful of ships), of which harvesting alone is **~3.9 s (≈50%)** and **~2.5–3.7 s is unaccounted for** between the named phase buckets.

## Per-Tick Phases (15 × 100 = 1500 invocations / turn)

| # | Phase key | Sub-engine (file:line) | Work per tick on tiny scenario | Mid-turn invalidator | Cheap skip candidate |
|---|-----------|------------------------|--------------------------------|----------------------|----------------------|
| 0 | `harvesting` | `HarvestingEngine.process_harvesting_tick` ([harvesting_engine.py:204](../../../../game/strategy/engine/harvesting_engine.py#L204)) | 2 empires → each colony → all facilities → component scan for `LocalStorage` (storage re-aggregation) + `ResourceHarvester` + scoped `ResourceHarvestBooster` (4 scopes × every harvester) | facility added / destroyed / `is_operational` flipped | `no_facility_mutations_since_last_tick` |
| 0b | `resources` | `ConsumableManagementEngine.process_per_turn_consumption` (consumable_management_engine.py:80) | 2 empires → each fleet → each ship → component lookup for `ResourceConsumption`; auto-disable on shortage | component added/removed; ship damage flips state | skip if all ships unchanged |
| 0c | `fuel_gen` | `ResupplyEngine.process_fuel_generation` (resupply_engine.py:86) | 2 empires → each colony → each facility → `ResourceGeneration` lookup (fuel) | facility destroyed / disabled | `no_fuel_facility_changes` |
| 0c1 | `planet_energy` | `PlanetEnergyEngine.process_energy_tick` | scans all facilities for energy gen + storage every tick; auto-deactivates shields on depletion | facility destroyed; shield toggled | `no_shields_active_and_no_facility_changes` |
| 0d | `resupply` | `ResupplyEngine.process_fleet_resupply` (resupply_engine.py:177) | 2 empires → each fleet → galaxy lookup for co-located planets → equalize fuel across ships | fleet moves mid-tick; facility fuel emptied | `all_fleets_same_location` |
| 0e | `production` | `ProductionEngine.process_construction_tick` (production_engine.py:182) | 2 empires → each colony → base queue (if PlanetaryYard) + each shipyard facility queue independently; consume 1/100 cost; detect completions | queue item completes; queue paused/unpaused; shipyard destroyed | `no_active_queues` (hard pre-check) |
| 0f | `environmental` | `EnvironmentalHazardEngine.process_environmental_tick` (environmental_hazard_engine.py:84) | 2 empires → each fleet → galaxy lookup (system at fleet hex) → storm effects query | storm appears/disappears; fleet leaves system | `no_fleets_in_hostile_systems` |
| 1 | `instant_orders` | `OrderProcessor.process_instant_orders` (order_processor.py:131) | iterates all fleets w/ `JOIN_FLEET` orders | new join order added; fleet destroyed | `no_join_orders_queued` |
| 1.5 | `actions` | `ActionExecutionEngine.process_action_ticks` (action_execution_engine.py:81) | iterates each empire's fleets with action orders; dispatches handler | order consumed; new order added; fleet destroyed | `no_action_orders_queued` |
| 1.6 | `planet_actions` | `PlanetActionEngine.process_planet_actions_tick` (planet_action_engine.py:76) | iterates colonies with planet action orders; instant abilities pop immediately | planet order completed/added | `no_planet_orders_queued` |
| 1.7 | `activation_timers` | `ComponentActivationEngine.process_activation_tick` (component_activation_engine.py:48) | 2 empires → each colony → each facility → all `ComponentActivationState`s; ticks down timers | component activation toggled; facility destroyed | `no_components_in_transition` |
| 1.8 | `planet_modifier_effects` | `PlanetModifierEffectEngine.process_modifier_effects_tick` (planet_modifier_effect_engine.py:42) | each colony scanned for active `GravityModifier` / `RadiationShield`; applies/reverts gravity & radiation overrides; fresh engine per tick | modifier activated/deactivated mid-tick | `no_gravity_or_radiation_modifiers_active` |
| 2 | `movement_calc` | `FleetMovementEngine.collect_movements` (fleet_movement_engine.py:231) | each fleet → effective speed + interval check → pathfind next hex → push (fleet, hex) | fleet speed changed; path changed; storm multiplier change | `all_fleets_same_speed_location_path` (tick-dependent interval check complicates) |
| 3 | `movement_apply` | `FleetMovementEngine.apply_movements` (fleet_movement_engine.py:361) | drains queue from phase 2; logs `MovementResult`; computes `moved_fleet_ids` | move queue empty; fleet destroyed mid-apply | `move_queue_empty` |
| 4 | `combat` | `ConflictResolutionEngine.resolve_all_conflicts` (conflict_resolution_engine.py:188) | **OUT OF SCOPE for PROJ-412** | n/a | n/a |

## End-of-Turn Phases (6 × 1 / turn, ctx.tick = 0)

| # | Phase key | Sub-engine (file:line) | Work | Skip candidate |
|---|-----------|------------------------|------|----------------|
| EOT-1 | `organics_consumption` | `OrganicsConsumptionEngine.process_consumption` (organics_consumption_engine.py:90) | drain food per species per population; cache `last_food_ratio` for happiness | `no_populations_or_stockpiles_changed` |
| EOT-2 | `happiness` | `HappinessEngine.process_happiness` (happiness_engine.py:101) | per population: habitability × food ratio + surplus bonus, clamped [0, 3] | n/a |
| EOT-3 | `population_growth` | `PopulationEngine.process_population_growth` (population_engine.py:75) | PROJ-284 growth formula | `all_populations_saturated_or_zero_rate` |
| EOT-4 | `quality_improvement` | `QualityEngine.process_quality_improvement` (quality_engine.py:41) | scan facilities for `QualityImprovement`; cap at QUALITY_CAP | `no_quality_improvers_on_any_facility` |
| EOT-5 | `atmosphere` | `AtmosphereEngine.process_atmosphere` (atmosphere_engine.py:49) | scan `AtmosphereModifier` facilities; linear toward `atmosphere_target` | `atmosphere_current_equals_target` |
| EOT-6 | `water_modification` | `WaterEngine.process_water_modification` (water_engine.py:28) | scan `WaterModifier` facilities; linear toward `water_target` | `water_current_equals_target` |

## Surprises

1. **Harvesting** rescans component abilities every tick even though facilities rarely change mid-turn. `recalculate_storage` re-aggregates 100×/turn whether anything mutated or not.
2. **PlanetEnergyEngine** also rescans facility energy abilities every tick — same pattern, same caching opportunity.
3. **`PlanetModifierEffectEngine` is constructed *fresh* per tick** inside the turn engine — allocation churn that the agent flagged for verification.
4. **Movement_calc** pathfinds every eligible fleet every tick; with stable fleet speeds and galaxy map this is deterministic and partially memoizable.
5. **EnvironmentalHazardEngine** queries system effects for every fleet every tick even when no storms exist — a `no_active_storms_on_galaxy` short-circuit would be free.
6. End-of-turn phases run **once** per turn; they are not the source of the 2.5–3.7 s unaccounted overhead.

The strongest candidates for **redundant per-tick work** are (in approximate cost order): harvesting → planet_energy → environmental → movement_calc.
