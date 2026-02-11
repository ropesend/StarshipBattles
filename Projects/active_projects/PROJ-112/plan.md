# PROJ-112: Spaghetti Code Reduction — Top 10 Complexity Offenders

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-112` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-112 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. RaceConfig.validate | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. ShipSerializer.from_dict | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. StrategyInputHandler._handle_keydown_legacy | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. ShipStatsCalculator._phase_stats_aggregation | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. get_logistics_rows | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. BuildQueueScreen.handle_event | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. ProjectileManager.update | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Galaxy.generate_warp_lanes | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. TestLabScreen (handle_input + _handle_click) | Not Started | [phase_9_checklist.md](phase_9_checklist.md) |

## Current State
**Last Updated:** 2026-02-11 14:30
**Active Phase:** Phase 1
**Last Action:** Plan approved
**Next Action:** Begin Phase 1 - RaceConfig.validate decomposition
**Blockers:** None
**Context for Next Agent:** Baseline is 8237 tests passing. Pure extract-method refactoring.

## Overview
Decompose the 10 highest cyclomatic complexity functions (CC >= 30) into smaller private helper methods, reducing each parent function's CC below 15 while keeping all public APIs unchanged.

## Goals
- Reduce CC of all 10 worst offenders below 15
- No behavioral changes, no public API changes
- All 8237+ tests continue to pass

## Scope
**In:** Extract-method decomposition of 10 specific functions
**Out:** New features, behavioral changes, test rewrites, public API changes

## Key Files
| Component | File Path |
|-----------|-----------|
| RaceConfig.validate | `game/strategy/data/race_config.py` |
| ShipSerializer.from_dict | `game/simulation/entities/ship_serialization.py` |
| StrategyInputHandler._handle_keydown_legacy | `game/ui/screens/strategy_input_handler.py` |
| ShipStatsCalculator._phase_stats_aggregation | `game/simulation/entities/ship_stats.py` |
| get_logistics_rows | `game/ui/screens/builder/stats_config.py` |
| BuildQueueScreen.handle_event | `game/ui/screens/build_queue_screen.py` |
| ProjectileManager.update | `game/simulation/projectile_manager.py` |
| Galaxy.generate_warp_lanes | `game/strategy/data/galaxy.py` |
| TestLabScreen.handle_input | `game/ui/screens/test_lab/screen.py` |
| TestLabScreen._handle_click | `game/ui/screens/test_lab/screen.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-11 | Phase order: simplest/lowest-risk first | Build confidence before complex algorithmic refactors |
| 2026-02-11 | Data-driven pattern for RaceConfig + ShipSerializer | Replaces copy-pasted if-blocks with tuple lists + loops |
| 2026-02-11 | Accumulator dict for ShipStats | Preserves atomic update semantics without new classes |
| 2026-02-11 | Gap tests before complex phases (7, 8) | Ensure safety net before touching physics/algorithms |

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (8237+ baseline)
- [ ] Radon CC < 15 on all 10 parent functions
- [ ] Audit passed
- [ ] User verified
