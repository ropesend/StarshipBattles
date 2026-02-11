# PROJ-78: Quickstart Initial Complexes

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-78` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-78 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Create Complex Designs | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. QuickstartBuilder Method | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. App Integration | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Tests | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-08
**Active Phase:** Complete - Audit Passed
**Last Action:** Audit cycle 1 passed - all 4 phases verified, no issues found
**Next Action:** User verification
**Blockers:** None

## Overview
Add 6 new complex designs to quickstart games and spawn 7 pre-built complexes on home planets at game start. This provides players with immediate resource harvesting (Metals, Organics, Vapors, Radioactives, Exotics), fuel generation/storage, and ship building capabilities from turn 1.

## Goals
- Create 5 resource production+storage complexes (one per resource type)
- Create 1 resupply depot (fuel generation + storage)
- Spawn all 7 complexes (including existing qs_complex) as operational facilities on home planets

## Scope
**In:**
- 6 new complex JSON design files
- QuickstartBuilder.spawn_initial_complexes() method
- app.py integration to call spawning at game start
- Unit and integration tests

**Out:**
- Non-quickstart game modes (manual new game setup)
- Modifying existing qs_complex.json
- Balance tuning of harvest rates/storage capacities

## Key Files
| Component | File Path |
|-----------|-----------|
| Existing complex template | `tests/fixtures/quickstart/designs/qs_complex.json` |
| QuickstartBuilder | `game/strategy/quickstart_builder.py` |
| App startup | `game/app.py` |
| PlanetaryFacility dataclass | `game/strategy/data/planet.py` |
| DesignLibrary | `game/strategy/systems/design_library.py` |
| _spawn_complex pattern | `game/strategy/engine/production_engine.py` (line 239) |
| Component definitions | `data/components.json` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-08 | Pre-built complexes at turn 1 | Quickstart should be immediately playable |
| 2026-02-08 | Resupply depot = fuel_synthesizer + fuel_tank | Generates 300 fuel/turn and stores 50k for fleet resupply |
| 2026-02-08 | Tier 1 for all except exotics | Keep complexes small; exotics exceeds Tier 1 budget |
| 2026-02-08 | Tier 2 for exotics complex | 1040 kg > 1000 kg Tier 1 limit; use Tier 2 (2000 kg) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [x] All phase checklists complete
- [ ] Start Quickstart 1P - home planet has 7 operational facilities
- [ ] Check Planet Info panel shows all facilities
- [ ] Verify can queue ship construction (shipyard works)
- [ ] Start Quickstart 2P - both home planets have facilities
- [x] All tests passing (`pytest tests/ -n 12`) - 7294 passed
- [x] Audit passed (Cycle 1)
- [ ] User verified
