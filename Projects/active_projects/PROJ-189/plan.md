# PROJ-189: Storms Environmental Hazards

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-189` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-189 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Storm Data Model & Serialization | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Hex Cluster Generation & Storm Placement | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. SHIELD_CAPACITY_MULT Stat Key | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. AreaEffectManager Service | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. EnvironmentalHazardEngine (Turn Integration) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Rendering | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Combat Layer Integration | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Integration Testing & Balance | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 3
**Last Action:** Phase 2 complete - Hex cluster generation, StormGenerator, Galaxy integration, blueprint configs
**Next Action:** Begin Phase 3 - SHIELD_CAPACITY_MULT Stat Key
**Blockers:** None
**Context for Next Agent:** 12,649 tests passing, 1 skipped. Created hex_random_cluster() in hex_math.py. Created data/storms.json with 5 storm types. Created StormGenerator class. Integrated into GalaxySystemGenerator and Galaxy. Added storm configs to all system blueprints. Storms now generate during galaxy creation.

## Overview
Implement "Storms" as environmental hazards in star systems. Storms occupy 1-10 hexes (irregular shapes) and apply effects (shield interference, propulsion interference, environmental damage, fuel drain) to all ships in those hexes. Effects use data-driven multipliers that feed into the same stat pipeline as the component system. Storms are static entities generated during system creation and rendered using existing nebulae assets.

## Goals
- Create Storm entity with multi-hex zone registration (IZoneOccupant pattern)
- Implement environmental effects: shield reduction, speed reduction, tick-based damage, fuel drain
- Add SHIELD_CAPACITY_MULT to modifier system for targeted shield interference
- Create AreaEffectManager service to aggregate environmental effects at any hex
- Integrate environmental processing into the 100-tick turn loop (Phase 0f)
- Generate storms during system creation with irregular hex cluster shapes
- Render storms on strategy map using nebulae assets
- Apply shield interference during tactical combat in storm hexes

## Scope
**In:**
- Storm entity data model and serialization
- StormEffect data-driven multiplier system
- Hex random cluster generation algorithm
- Storm placement during galaxy generation
- storms.json type definitions
- system_blueprints.json storm generation config
- AreaEffectManager aggregation service
- EnvironmentalHazardEngine (Phase 0f in tick loop)
- Fleet speed reduction in storm hexes
- Environmental damage and fuel drain per tick
- Nebulae rendering on strategy map
- Storm tooltips on hover
- SHIELD_CAPACITY_MULT stat key
- Combat shield interference in storm hexes

**Out:**
- Dynamic storm creation/destruction (future superweapon feature)
- Storm movement/drift over time
- Combat layer visual effects (tactical battle rendering)
- Sensor interference mechanics
- Storm interaction with warp travel
- Sound effects / audio

## Key Files
| Component | File Path |
|-----------|-----------|
| Storm entity (NEW) | `game/strategy/data/storm.py` |
| Storm types data (NEW) | `data/storms.json` |
| Storm generator (NEW) | `game/strategy/generation/storm_generator.py` |
| AreaEffectManager (NEW) | `game/strategy/services/area_effect_manager.py` |
| Environmental engine (NEW) | `game/strategy/engine/environmental_hazard_engine.py` |
| StarSystem | `game/strategy/data/galaxy.py` |
| Turn Engine | `game/strategy/engine/turn_engine.py` |
| Stat Keys | `game/simulation/components/abilities/stat_keys.py` |
| Modifiers | `game/simulation/components/modifiers.py` |
| Strategy Renderer | `game/ui/screens/strategy_renderer.py` |
| Asset Manifest | `assets/asset_manifest.json` |
| Hex Math | `game/core/hex_math.py` |
| System Blueprints | `data/system_blueprints.json` |
| Fleet Speed Calculator | `game/strategy/services/fleet_speed_calculator.py` |
| Fleet Movement Engine | `game/strategy/engine/fleet_movement_engine.py` |
| Galaxy Entity Registry | `game/strategy/data/galaxy_entity_registry.py` |
| Galaxy System Generator | `game/strategy/data/galaxy_system_generator.py` |
| ShieldProjection ability | `game/simulation/components/abilities/defense.py` |
| Conflict Resolution Engine | `game/strategy/engine/conflict_resolution_engine.py` |
| Simulation Adapter | `game/strategy/adapters/simulation_adapter.py` |
| Engine Interfaces | `game/strategy/interfaces/engines.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Generate new game - storms appear in star systems
- [ ] Move fleet into storm hex - speed reduction works
- [ ] End turn with fleet in storm - damage and fuel drain applied
- [ ] Enter combat in storm hex - shield reduction works
- [ ] Storms render correctly with nebulae images, transparency, tooltips
- [ ] Audit passed
- [ ] User verified
