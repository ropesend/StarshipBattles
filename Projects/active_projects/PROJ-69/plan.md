# PROJ-69: Multi Build Queue Restructure

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-69` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-69 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Data Model - Facility Queues | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Production Engine - Parallel Processing | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Build Queue Screen - Layout Restructure | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Controller & Drag Handler - Multi-Queue | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Strategy Screen Integration | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Test Updates & Integration Testing | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-07
**Active Phase:** Complete - All phases done, ready for audit
**Last Action:** Phase 6 complete - Test Updates & Integration Testing
**Next Action:** Audit (Protocol 04)
**Blockers:** None
**Context for Next Agent:** All 6 phases complete. Phase 6 added 14 new tests: 2 E2E integration tests (parallel shipyard processing, facility queue save/load) and 12 controller tests (single-queue, multi-queue, mode transitions, compatibility filtering). Full suite: 6575 passed, 1 pre-existing failure (IFleet mock spec). Manual smoke test deferred to user verification.

## Overview
Restructure the build queue system to support multiple simultaneous build queues per hex. Each shipyard facility on a planet generates its own build queue, and each fleet space yard has its own queue. A new queue selector UI column allows players to view and manage all queues at a hex, with support for single-queue viewing and multi-queue batch adding.

## Goals
- Each shipyard facility produces an independent build queue (parallel construction)
- Unified UI showing all build queues at a hex location
- Single-select: view and manage one queue (same as current behavior)
- Multi-select: add designs to multiple queues simultaneously
- Each queue processes independently each turn (2 shipyards = 2 ships building at once)

## Scope
**In:**
- PlanetaryFacility gets its own `construction_queue` field
- Planet keeps base queue (complexes only) + shipyard facility queues
- Fleet keeps single queue (one yard per fleet)
- New `BuildQueueSource` data class + `collect_build_queues_at_hex()` function
- Production engine processes all facility queues independently
- Build queue screen layout restructured with queue selector column
- Controller and drag handler updated for multi-queue support
- Strategy screen passes hex context to build queue screen

**Out:**
- User-renamable queues (auto-generated names only)
- Inactive/paused queue display (queues disappear when source entity removed)
- Save file migration (saves are disposable per CLAUDE.md)
- Fleet spatial index optimization (existing O(n*m) iteration acceptable)

## Key Files
| Component | File Path |
|-----------|-----------|
| Planet model | `game/strategy/data/planet.py` |
| Fleet model | `game/strategy/data/fleet.py` |
| BuildContext protocol | `game/strategy/data/build_context.py` |
| Production engine | `game/strategy/engine/production_engine.py` |
| Build queue screen | `game/ui/screens/build_queue_screen.py` |
| Build queue controller | `game/ui/panels/build_queue_controller.py` |
| Build queue drag handler | `game/ui/panels/build_queue_drag_handler.py` |
| Strategy screen | `game/ui/screens/strategy_screen.py` |
| Strategy UI | `game/ui/screens/strategy_ui.py` |
| Production tests (unit) | `tests/unit/strategy/production_engine/` |
| Production tests (integration) | `tests/integration/strategy/production/` |
| BuildQueueSource (NEW) | `game/strategy/data/build_queue_source.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Manual test: planet with 2 shipyards shows 3 queues (base + 2 shipyard)
- [ ] Manual test: multi-select adds to all selected queues
- [ ] Manual test: each queue processes independently per turn
- [ ] Manual test: save/load preserves facility queues
- [ ] Audit passed
- [ ] User verified
