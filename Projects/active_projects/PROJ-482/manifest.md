# PROJ-482 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/engine/game_session.py | Production | Phase 1: 10-property combined fix (annotations + remove ignores). Phase 2: `handle_command` |
| game/strategy/engine/commands/order_metadata_view.py | Production | Phase 1: `_registry` static method |
| game/strategy/engine/superweapon_order_processor.py | Production | Phase 1: `_get_nav_service`. Phase 2: `_get_empire_mutator` |
| game/strategy/data/star_system.py | Production | Phase 1: `primary_star` property |
| game/strategy/engine/harvesting_engine.py | Production | Phase 2: 2 mutator helpers |
| game/strategy/engine/order_handlers/base.py | Production | Phase 2: 2 mutator helpers |
| game/strategy/engine/environmental_hazard_engine.py | Production | Phase 2: `_get_ship_mutator` |
| game/strategy/engine/planet_modifier_effect_engine.py | Production | Phase 2: `_get_planet_mutator` |
| game/strategy/engine/production_spawner.py | Production | Phase 2: `_get_planet_mutator` |
| game/strategy/engine/handlers/base.py | Production | Phase 2: 3 resolvers + colonize target |
| game/strategy/engine/game_initializer.py | Production | Phase 2: 2 nested generators |

> Note: 2026-05-22 post-merge — PROJ-473 (commit `f94e6a1ef`) added `name_rng`/`physics_rng`/`image_rng` parameter threading around lines 81-95 and 253+. PROJ-482's planned narrowing of the two nested generators is unaffected, but re-verify surrounding context and line refs during implementation.

| game/strategy/services/ability_sources/fleet.py | Production | Phase 2: `_walk_strategic_abilities` generator |
| game/app_bootstrap.py | Production | Phase 2: `_replay_combat_lab_fallback` closure |
| game/strategy/engine/superweapon_handlers/open_warp_point.py | Production | Phase 3: 2 closures |
| game/strategy/engine/superweapon_handlers/stellerate_star.py | Production | Phase 3: 2 closures |
| game/strategy/engine/superweapon_handlers/close_warp_point.py | Production | Phase 3: 2 closures |
| game/strategy/engine/superweapon_handlers/create_dyson_sphere.py | Production | Phase 3: 2 closures |
| game/strategy/engine/superweapon_handlers/implode_planet.py | Production | Phase 3: 1 closure |
| game/strategy/engine/handlers/construction_queue.py | Production | Phase 3: `_resolve_design_data` |
| game/strategy/services/planet_write_service.py | Production | Phase 3: `pop_construction_item` (coordinate with PROJ-483 Protocol narrowing) |
| game/strategy/services/replay_verification_coordinator.py | Production | Phase 3: `_json_safe` |
| game/strategy/engine/atmosphere_engine.py | Production | Phase 3: `_get_planet_mutator` |
| game/strategy/adapters/simulation_adapter.py | Production | Phase 3: `_lookup` + `_build_capture_context` (with new ReplayCaptureContext type) |
| game/strategy/data/deployed_group.py | Production | Phase 3: decorator factory + inner |

> Note: 2026-05-22 post-merge — PROJ-465 (commit `d3c38ab7e`) moved `_from_dict_payload` from `FighterWing`/`SatelliteConstellation` up to `_ShipBearingDeployedGroup` (around lines 306-328). PROJ-482's `_register_type` decorator target is unaffected; re-verify line refs during implementation.

| game/strategy/systems/design_catalog.py | Production | Phase 3: `load_design_data` |

**Explicitly out of scope:** `game/strategy/data/fleet_serde.py` — new sibling of `fleet.py` (PROJ-459, already on main); not part of PROJ-482's narrowing surface.
