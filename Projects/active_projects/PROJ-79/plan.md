# PROJ-79: Build Queue Screen & Production System Rework

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-79` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-79 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Rename + Build Yards List Improvements | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Build Time from Cost + Tick-Granular Production | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Queue Item Display + Column Headers + Resource Icons | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Complex Target Planet Selection | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Empire Build Queue Window Sync + Final Audit | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-08 18:00
**Active Phase:** Planning
**Last Action:** Plan approved by user
**Next Action:** Begin Phase 1 - Rename + Build Yards List Improvements
**Blockers:** None
**Context for Next Agent:** Full codebase analysis completed. Build queue system well-understood. Key decisions made on build rate formula (2000/3000 units/turn), tick-granular production, proportional mid-turn harvesting, and planet selection reuse.

## Overview
Rework the build queue screen and production system to: rename "Build Queues" to "Build Yards" with Planetary Yard / Shipyard distinction, calculate build time from vehicle resource cost instead of hardcoding to 1 turn, implement tick-granular production so items complete mid-turn, show daily resource cost and resource icons in queue display, enforce complex-to-planet restrictions for fleet shipyards, and generalize the planet selection window for reuse.

## Goals
- Rename "Build Queues" to "Build Yards" with clear Planetary Yard vs Shipyard distinction
- Calculate build time from vehicle resource cost (2000 units/turn for planetary yards, 3000/turn for shipyards)
- Move production completion from end-of-turn to per-tick (100 ticks/turn) for granular construction
- Show per-turn resource cost per queue item with resource portrait icons as column headers
- Fleet shipyards at multi-colony hexes must prompt for target planet when queuing complexes
- Improve Build Yards selector: wider panel, build rate display, clear selection indication
- Newly spawned facilities produce proportionally for remaining ticks in the turn

## Scope
**In:**
- BuildQueueScreen UI rework (rename, widen, selection highlighting, column headers, resource icons)
- BuildQueueSource data model (add build_rate, planet_id fields)
- BuildQueueController (build time calculation from cost, cost tracking population)
- ProductionEngine (tick-granular completion, mid-turn spawning, partial harvest)
- PlanetSelectionWindow generalization (reuse for complex target planet)
- EmpireBuildQueueWindow sync (rename, build rate column)

**Out:**
- Ship designer changes
- New component types
- Save game migration (old saves get default behavior)
- Build queue AI decisions
- Fleet order changes beyond BUILD mode

## Key Files
| Component | File Path |
|-----------|-----------|
| Build Queue Screen UI | `game/ui/screens/build_queue_screen.py` |
| Build Queue Source data | `game/strategy/data/build_queue_source.py` |
| Build Queue Controller | `game/ui/panels/build_queue_controller.py` |
| Planet Selection Window | `game/ui/screens/planet_selection_window.py` |
| Colonization System | `game/ui/screens/strategy_colonization.py` |
| Production Engine | `game/strategy/engine/production_engine.py` |
| Turn Engine | `game/strategy/engine/turn_engine.py` |
| Harvesting Engine | `game/strategy/engine/harvesting_engine.py` |
| Design Metadata | `game/strategy/data/design_metadata.py` |
| SpaceShipyard Ability | `game/simulation/components/abilities/harvester.py` |
| Empire Build Queue Window | `game/ui/screens/empire_build_queue_window.py` |
| Planet data model | `game/strategy/data/planet.py` |
| Resource Portraits | `assets/Images/Resource Portraits/` |
| Build Queue Controller tests | `tests/unit/ui/panels/test_build_queue_controller.py` |
| Build Queue Source tests | `tests/unit/strategy/data/test_build_queue_source.py` |
| Production Engine tests | `tests/unit/strategy/production_engine/` |

## Decisions Log (Summary)
See [decisions.md](decisions.md) for the full log with rationale.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-08 | Build rate: 2000/turn (Planetary Yard), 3000/turn (Shipyard) | User specified. Uses max-resource proportional formula. |
| 2026-02-08 | Tick-granular production with mid-turn spawning | User wants items to complete at exact tick, next starts immediately |
| 2026-02-08 | Proportional mid-turn harvesting for new facilities | User wants completed harvesters to produce for remaining fraction of turn |
| 2026-02-08 | Use resource portrait icons from assets/Images/Resource Portraits/ | Icons already exist, user confirmed |
| 2026-02-08 | Planet selection popup immediately for fleet+complex at multi-colony hex | User confirmed immediate popup |
| 2026-02-08 | Generalize PlanetSelectionWindow for both colonization and complex target | Reuse same code with parameterized title/labels |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Manual test: build queue screen shows Build Yards, build rates, resource icons
- [ ] Manual test: calculated build times match formula
- [ ] Manual test: items complete mid-turn, next starts immediately
- [ ] Manual test: fleet shipyard at multi-colony hex prompts for planet
- [ ] Manual test: newly spawned harvesters produce proportionally
- [ ] Audit passed
- [ ] User verified
