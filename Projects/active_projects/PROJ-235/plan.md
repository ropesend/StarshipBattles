# PROJ-235: TurnEngine Phase Timing Cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-235` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-235 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add helpers and shared constant | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Refactor _process_tick() | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Refactor process_turn() | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-03-28 22:00
**Active Phase:** Complete — awaiting user verification
**Last Action:** All 3 phases complete. Full test suite passes (13,914 passed, 17 pre-existing failures).
**Next Action:** User verification
**Blockers:** None
**Context for Next Agent:** All implementation done. `_process_tick()` reduced from ~95 lines of phase code to 47 lines. `TICKS_PER_TURN` shared between turn_engine and production_engine. 5 BUG-109 blocks consolidated into `_log_empire_state()` helper. 12 timing blocks consolidated into `_time_phase()` helper.

## Overview
`TurnEngine._process_tick()` is 119 lines of 12 copy-pasted timing blocks and 3 copy-pasted BUG-109 debug blocks. `process_turn()` adds 2 more debug blocks and a hardcoded tick loop. This project extracts a `_time_phase()` helper to eliminate the 12x timing duplication, a `_log_empire_state()` helper to eliminate the 5x debug duplication, and shares the `TICKS_PER_TURN` constant with `production_engine.py`.

## Goals
- Eliminate 12x copy-pasted timing boilerplate in `_process_tick()` via `_time_phase()` helper
- Consolidate 5x copy-pasted BUG-109 debug blocks via `_log_empire_state()` helper
- Share `TICKS_PER_TURN` constant between `turn_engine.py` and `production_engine.py`
- Reduce `_process_tick()` from ~119 lines to ~40-50 lines
- Zero test regressions (13,904 passing baseline, 17 pre-existing failures in star color mapping)

## Scope
**In:**
- `game/strategy/engine/turn_engine.py` — primary target (all changes)
- `game/strategy/engine/production_engine.py` — constant import update only (1 line)

**Out:**
- Test files (per user request)
- BUG-109 logging in `harvesting_engine.py` and `maintenance_engine.py` (other files)
- Other hardcoded `100.0` divisors in `resource_management_engine.py`, `resupply_engine.py`, `environmental_hazard_engine.py`
- Any changes to sub-engine interfaces or signatures

## Key Files
| Component | File Path |
|-----------|-----------|
| TurnEngine (primary) | `game/strategy/engine/turn_engine.py` |
| `_process_tick()` method | `turn_engine.py` lines 393-511 (119 lines) |
| `process_turn()` method | `turn_engine.py` lines 300-371 (72 lines) |
| `_reset_phase_times()` | `turn_engine.py` lines 189-196 |
| TICKS_PER_TURN source | `game/strategy/engine/production_engine.py` line 30 |
| Phase order test (CRITICAL) | `tests/unit/strategy/turn_engine/test_turn_processing.py` |
| Tick mechanics tests | `tests/unit/strategy/turn_engine/test_tick_mechanics.py` |
| DI tests | `tests/unit/strategy/turn_engine/test_dependency_injection.py` |
| Integration tests | `tests/integration/strategy/turn_engine/` (6 files) |
| Gameplay loop test | `tests/integration/gameplay_loop/test_turn_execution.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis, swarm findings, design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] `pytest tests/unit/strategy/turn_engine/ -v` — all pass
- [ ] `pytest tests/integration/strategy/turn_engine/ -v` — all pass
- [ ] `pytest tests/integration/gameplay_loop/test_turn_execution.py -v` — all pass
- [ ] `pytest tests/ -n 12` — full suite, no regressions from 13,904 baseline
- [ ] `_process_tick()` reduced to ~40-50 lines
- [ ] Audit passed
- [ ] User verified
