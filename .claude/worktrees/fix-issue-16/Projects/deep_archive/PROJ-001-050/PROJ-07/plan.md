# PROJ-07: Strategy Layer Stats Calculation Refactor

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-07` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-07 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Ship Stats Service | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Caching in ShipInstance | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Refactor ShipInstance Methods | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Refactor Fleet Mobility Service | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Refactor Fleet Report Filters | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Update Tests | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-01-23 (migrated to new structure)
**Active Phase:** COMPLETE - Ready for Archive
**Last Action:** All 6 phases implemented, 2656 tests passing
**Next Action:** Archive project using `python Projects/scripts/archive_project.py PROJ-07`
**Blockers:** None

## Overview
Refactor the strategy layer to calculate ship stats from actual components instead of reading from cached `expected_stats` values. The current implementation incorrectly treats `expected_stats` as runtime data rather than its intended purpose: load-time validation only.

## Goals
- Remove all game logic reads from `expected_stats` in strategy layer
- Create a calculation service that computes stats from component definitions
- Support dynamic stat calculation that respects component damage
- Preserve `expected_stats` usage ONLY for load-time validation

## Scope
**In:** ShipInstance methods, fleet_report_filters.py, fleet_mobility_service.py, component-based stat calculation, damage-aware calculations
**Out:** Simulation layer, expected_stats serialization format, combat-layer stats, modifier effects

## Key Files
| Component | File Path |
|-----------|-----------|
| Ship Stats Service | `game/strategy/services/ship_stats_service.py` |
| ShipInstance | `game/strategy/data/ship_instance.py` |
| Fleet Report Filters | `game/ui/screens/fleet_report_filters.py` |
| Fleet Mobility | `game/strategy/services/fleet_mobility_service.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [x] All phase checklists complete
- [x] All tests passing (2656 passed)
- [x] Audit passed
- [x] User verified
