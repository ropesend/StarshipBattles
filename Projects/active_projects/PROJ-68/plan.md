# PROJ-68: Population System & Generic Cargo

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-68` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-68 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Population Data Model | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Habitability Scoring | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Population Growth Engine | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Cargo Ability Layer | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Cargo State Tracking | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. TRANSFER Order | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Colonization Integration | Complete | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. UI Updates | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Initial Population Seeding | Not Started | [phase_9_checklist.md](phase_9_checklist.md) |

## Current State
**Last Updated:** 2026-02-07
**Active Phase:** Phase 8 — UI Updates
**Last Action:** Phase 7 complete — Colonization transfers passengers as founding population, seeds 100 units minimum if no passengers, 7 new tests
**Next Action:** Begin Phase 8 — UI Updates
**Blockers:** None

## Overview
Add a multi-species population system to colonies, a generic cargo/transport system (passengers first, extensible to goods/resources), fleet TRANSFER orders for loading/unloading, and colonization integration where founding population comes from ship passenger cargo.

## Goals
- Multi-species population tracking per colony with per-species happiness
- Habitability scoring (planet properties vs race preferences)
- Logistic population growth per turn
- Generic cargo system on ships (passengers first, future: resources, hardware)
- TRANSFER fleet order for load/unload operations
- Colonization uses ship passengers as founding population
- UI displays for population and cargo

## Scope
**In:**
- SpeciesPopulation data model on Planet
- RaceConfig stored on Empire (multi-species ready)
- Habitability scoring function
- PopulationEngine with logistic growth
- CargoStorage ability (generic, passengers first)
- ShipInstance/Fleet cargo tracking
- TRANSFER order type with validation
- Colonization passenger transfer
- UI: planet population display, fleet cargo display
- Initial population seeding for game start

**Out:**
- Workforce/labor requirements for production
- Food/supply consumption by population
- Immigration between colonies (automatic)
- Diplomacy effects on population
- Cargo types beyond passengers (future project)
- Population-based research bonuses

## Key Files
| Component | File Path |
|-----------|-----------|
| Planet data model | `game/strategy/data/planet.py` |
| Empire data | `game/strategy/data/empire.py` |
| Game config | `game/strategy/engine/game_config.py` |
| Game session | `game/strategy/engine/game_session.py` |
| Habitability formulas | `game/strategy/formulas/habitability.py` (NEW) |
| Population engine | `game/strategy/engine/population_engine.py` (NEW) |
| Engine interfaces | `game/strategy/interfaces/engines.py` |
| Turn engine | `game/strategy/engine/turn_engine.py` |
| Cargo ability | `game/simulation/components/abilities/cargo.py` (NEW) |
| Ability registry | `game/simulation/components/abilities/__init__.py` |
| Stats calculator | `game/strategy/services/ship_stats_calculator.py` |
| Components data | `data/components.json` |
| Ship instance | `game/strategy/data/ship_instance.py` |
| Fleet | `game/strategy/data/fleet.py` |
| Commands | `game/strategy/engine/commands.py` |
| Transfer validator | `game/strategy/validation/transfer_validator.py` (NEW) |
| Fleet order processor | `game/strategy/engine/fleet_order_processor.py` |
| Planet DTO | `game/strategy/facade/dto/planet_dto.py` |
| Empire DTO | `game/strategy/facade/dto/empire_dto.py` |
| Fleet DTO | `game/strategy/facade/dto/fleet_dto.py` |
| Detail formatter | `game/ui/screens/strategy_detail_fmt.py` |
| Fleet orders UI | `game/ui/screens/fleet_orders_window.py` |
| Quickstart | `game/strategy/quickstart_builder.py` |

## Design Decisions
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-07 | 1 pop unit = 1,000 people | Granular enough for transport (ships carry 1-10K units), manageable numbers |
| 2026-02-07 | 100 pop/km² max density | Earth-like ~50M units (50B people). Good gameplay range |
| 2026-02-07 | Ship cargo determines colony start pop | Requires passenger quarters for effective colonization. Strategic ship design choice |
| 2026-02-07 | Full RaceConfig on Empire | Avoids file I/O at runtime. Clean access to all race data for growth/habitability |
| 2026-02-07 | Multi-species per colony from start | Design data model for multiple races per colony immediately. Avoid refactor later |
| 2026-02-07 | Generic cargo system now | CargoStorage ability with cargo_type param. Passengers first, future: resources, hardware |
| 2026-02-07 | Logistic growth (S-curve) | Natural feeling growth that slows near capacity. Standard population dynamics |
| 2026-02-07 | Per-species happiness | Each species tracks own happiness based on habitability, crowding, tolerance |
| 2026-02-07 | Single TRANSFER order type | One order with direction/cargo_type/amount params. Clean and extensible |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Phase Dependency Graph
```
Phase 1 (Data Model) ──┬──> Phase 2 (Habitability) ──> Phase 3 (Growth Engine)
                       │                                        │
                       │                                        v
Phase 4 (Cargo Ability)──> Phase 5 (Cargo State) ──> Phase 6 (Transfer Order)
                       │                                        │
                       │                                        v
                       └──────────────────────────> Phase 7 (Colonize Integration)
                       │
                       ├──> Phase 8 (UI Updates) <── Phase 5
                       │
                       └──> Phase 9 (Seeding) <── Phase 3
```

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing: `pytest tests/ -n 12`
- [ ] Manual: Start quickstart → home colony has population
- [ ] Manual: Process turn → population grows
- [ ] Manual: Build ship with passenger quarters → cargo capacity shown
- [ ] Manual: TRANSFER order → population moves between colony and fleet
- [ ] Manual: Colonize with passengers → founding population transfers
- [ ] Audit passed
- [ ] User verified
