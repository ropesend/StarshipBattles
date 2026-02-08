# PROJ-75: Resource Harvesting & Economy System

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-75` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-75 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Empire Resource Pool Foundation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Harvesting Engine | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Storage Aggregation | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Production Resource Consumption | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Maintenance System | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Integration & UI | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-08
**Active Phase:** Phase 5 Complete - Ready for Phase 6
**Last Action:** Maintenance System: MaintenanceEngine with 5% build cost deduction, facility/ship scuttling, IMaintenanceEngine interface, TurnEngine Phase 0b wiring, 27 new tests
**Next Action:** Begin Phase 6 - Integration & UI
**Blockers:** None

## Overview
Implement a complete economy system with planetary resource harvesting, global empire resource pools, resource-based construction costs, and maintenance requirements. All 5 planetary resources (Metals, Organics, Vapors, Radioactives, Exotics) will be used for construction. Building progresses in 100-tick increments with proportional resource consumption. Ships and complexes require 5% maintenance per turn with instant scuttling on failure.

## Goals
- Harvesting components extract planetary resources based on quality
- Global empire resource pool with storage limits
- Build queues consume resources proportionally over 100 ticks
- 5% maintenance costs with instant scuttle on failure
- Fully moddable via JSON (per-component resource costs)

## Scope
**In Scope:**
- Empire-level resource pool (global, instant access)
- Harvesting components for planetary facilities
- Storage components defining empire capacity
- Per-component resource costs in JSON
- 100-tick granular build processing
- Maintenance costs (5% of build cost per turn)
- Instant scuttling when maintenance unaffordable

**Out of Scope:**
- Transport logistics (future feature)
- Trade between empires
- Resource market/pricing
- Partial maintenance (all-or-nothing)

## Key Files
| Component | File Path |
|-----------|-----------|
| Empire data | `game/strategy/data/empire.py` |
| Turn orchestration | `game/strategy/engine/turn_engine.py` |
| Production | `game/strategy/engine/production_engine.py` |
| Resource abilities | `game/simulation/components/abilities/resources.py` |
| Harvester ability | `game/simulation/components/abilities/harvester.py` |
| Harvesting engine | `game/strategy/engine/harvesting_engine.py` |
| Engine interfaces | `game/strategy/interfaces/engines.py` |
| Planet data | `game/strategy/data/planet.py` |
| Component JSON | `data/components.json` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-07 | All 5 planetary resources for construction | User preference - comprehensive economy |
| 2026-02-07 | Instant scuttle on maintenance failure | Simple, predictable behavior |
| 2026-02-07 | True global pool (no logistics) | Simpler implementation for MVP |
| 2026-02-07 | Per-component costs in JSON | Flexible, moddable, follows existing pattern |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [x] Test baseline established: 6652 passed, 1 unrelated failure
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
