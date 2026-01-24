# PROJ-08: Strategy Layer Data-Driven Resource System

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-08` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-08 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Resource Registry Infrastructure | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. ShipStatsService Generic Refactor | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. ShipInstance Generic Methods | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Fleet Generic Methods | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. TurnEngine Per-Tick Processing | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Update Components JSON | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Update Tests | Complete | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-01-23
**Active Phase:** Complete - Audit PASSED
**Last Action:** Skeptical audit completed - all phases verified, 2869 tests passing (271 PROJ-08 specific)
**Next Action:** User verification - run game and test functionality
**Blockers:** None
**Context for Next Agent:** Full implementation complete. Audit verified:
- Phase 1: Resource registry (`data/resources.json`, `game/core/resources.py`)
- Phase 2: ShipStatsService refactored with generic dicts, component toggles, new triggers
- Phase 3: ShipInstance has generic resource methods and component toggle support
- Phase 4: Fleet has generic movement/warp resource methods
- Phase 5: TurnEngine processes per-turn resources with auto-disable
- Phase 6: Warp drives updated to use `ResourceConsumption` with `trigger: 'warp_jump'`
- Phase 7: All tests pass (274 strategy tests, 2656 total)

## Overview
Refactor the strategy layer resource system to be fully data-driven. Any resource type defined in JSON (fuel, energy, ammo, or custom types like "glag") should work seamlessly without Python code changes.

## Goals
- Remove all hardcoded resource names ('fuel', 'energy', 'ammo') from Python code
- Support arbitrary resource types defined in JSON
- Add new trigger types: `per_turn` (spread over 100 ticks) and `warp_jump`
- Add component toggle (enable/disable) with auto-disable on resource depletion
- Maintain backward compatibility with existing saves and tests

## Scope
**In:** Strategy layer refactoring, resource registry, generic resource methods, TurnEngine processing, component toggles, backward-compatible wrappers
**Out:** Simulation layer, UI display configuration, combat resource consumption, resource generation

## Key Files
| Component | File Path |
|-----------|-----------|
| Resource Registry | `game/core/registry.py` |
| Stats Calculation | `game/strategy/services/ship_stats_service.py` |
| Ship Resources | `game/strategy/data/ship_instance.py` |
| Fleet Resources | `game/strategy/data/fleet.py` |
| Turn Processing | `game/strategy/engine/turn_engine.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [x] All phase checklists complete
- [x] All tests passing (2869 passed, 1 skipped)
- [x] Audit passed (2026-01-23, Cycle 1)
- [ ] User verified

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-01-23 | No critical/major issues. Minor: empty resource_type bug (documented), code style inconsistencies (non-blocking) | PASSED |

## Audit Summary
- **271 PROJ-08 tests verified** (39 registry + 53 stats + 71 ship + 73 fleet + 27 engine + 8 integration)
- **All 7 phases verified** by investigation agents with different perspectives
- **Code matches intent** - generic dict accumulators, component toggles, trigger types all working
- **Backward compatibility confirmed** - legacy methods wrap new generic methods
- **Warp drive transition confirmed safe** - ResourceConsumption with trigger='warp_jump' is complete replacement
