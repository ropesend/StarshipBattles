# PROJ-233: Refactor ProductionEngine - Extract Oversized Methods and Deduplicate Spawn Logic

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-233` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-233 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. QueueItemAction Enum | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Shared Formula | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract Spawner Module | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Clean Orchestrator | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Type Hints & Interface | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-03-28 21:20
**Active Phase:** Planning — Plan complete, awaiting user approval
**Last Action:** Protocol 01 completed — all planning artifacts written (plan.md, design.md, decisions.md, 5 phase checklists, manifest.md)
**Next Action:** User approves plan → begin Phase 1 implementation via "Continue Project" prompt
**Blockers:** None
**Context for Next Agent:** Test baseline 13904 passed / 17 pre-existing failures (star color, asset manager, menu — none production-related). PROJ-209 already refactored `_process_queue_tick_dynamic` into helpers; the main loop is clean. Focus is on spawn extraction (Phase 3 = biggest impact) and hygiene (Phases 1, 2, 4, 5).

## Overview
`production_engine.py` (864 lines) exceeds the 500-line target. The file was partially refactored in PROJ-209 but still contains duplicated spawn logic, a bloated orchestrator method, magic string validation, missing type hints, and a duplicated formula with `construction_forecast.py`. This project extracts spawning to a new module, consolidates shared math, and brings the file within conventions.

## Goals
- Reduce `production_engine.py` from 864 to ~590 lines
- Extract spawn logic to new `production_spawner.py` (~250 lines)
- Deduplicate limiting-resource formula into `production_math.py` (~30 lines)
- Replace string-based validation returns with `QueueItemAction` enum
- Add comprehensive type hints
- Remove stale `harvesting_engine` parameter from `IProductionEngine` interface

## Scope
**In:**
- `game/strategy/engine/production_engine.py` — primary refactor
- `game/strategy/engine/construction_forecast.py` — shared formula
- `game/strategy/interfaces/engines.py` — stale interface cleanup
- Test file updates for new module paths
- New `production_spawner.py` and `production_math.py` modules

**Out:**
- No behavioral changes to production logic
- No changes to `TurnEngine` integration beyond what it already does
- No changes to public API (`IProductionEngine.process_construction_tick`)
- No refactoring of `_process_queue_tick_dynamic` core loop (already well-structured from PROJ-209)

## Key Files
| Component | File Path |
|-----------|-----------|
| Primary target | `game/strategy/engine/production_engine.py` |
| New spawner | `game/strategy/engine/production_spawner.py` |
| New math utils | `game/strategy/engine/production_math.py` |
| Forecast (shared formula) | `game/strategy/engine/construction_forecast.py` |
| Interface | `game/strategy/interfaces/engines.py` |
| Spawning tests | `tests/unit/strategy/production_engine/test_spawning.py` |
| Event emission tests | `tests/unit/strategy/test_engine_event_emission.py` |
| Production refactor tests | `tests/unit/strategy/engine/test_production_refactor.py` |
| New math tests | `tests/unit/strategy/engine/test_production_math.py` |
| Mock engines | `tests/unit/strategy/mocks/mock_engines.py` |
| Interface tests | `tests/unit/strategy/interfaces/test_engine_interfaces.py` |

## Initial Analysis

### File Structure (864 lines)
- Lines 1-53: Imports, constants, TickExpenditure NamedTuple
- Lines 55-107: Class init + `_calculate_design_cost`
- Lines 109-202: `process_construction_tick` (77 lines — 30 are an inline comment)
- Lines 204-306: `_process_queue_tick_dynamic` (102 lines — well-structured from PROJ-209)
- Lines 307-558: PROJ-209 extracted helpers (validation, expenditure, affordability, consumption, completion, turns)
- Lines 560-592: `_complete_item` dispatch
- Lines 594-864: **Spawn methods (270 lines — extraction target)**

### Key Findings
1. `_process_queue_tick_dynamic` is **not** the problem — it was refactored in PROJ-209 and reads well
2. The spawn methods (`_spawn_ship`, `_spawn_fleet_ship`, `_spawn_complex`, `_spawn_fleet_complex`, `_create_and_place_facility`, `_load_design`, `_load_and_create_ship`) are 270 lines of cohesive spawn responsibility
3. Location resolution (galaxy → system → global hex) is duplicated between `_create_and_place_facility` (lines 646-657) and `_spawn_ship` (lines 748-757)
4. `_validate_queue_item` returns magic strings `"valid"`, `"skip"`, `"stop"`
5. Limiting-resource formula in `_calculate_tick_expenditure` (lines 399-410) is duplicated in `construction_forecast.py` (lines 68-78)
6. `IProductionEngine` interface still has stale `harvesting_engine` parameter (removed from implementation in PROJ-161)
7. Missing type hints throughout (empire, galaxy, colony_or_fleet all untyped)

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-28 | Don't split `_process_queue_tick_dynamic` further | Already well-decomposed by PROJ-209; helpers are tightly coupled to the loop |
| 2026-03-28 | Extract spawner as class, not free functions | Spawner needs `_registries` state; class is natural container |
| 2026-03-28 | Inline `_spawn_complex` rather than move it | It's a 1-line delegation to `_create_and_place_facility` |
| 2026-03-28 | Use `ticks_per_turn=1` in forecast's call to shared formula | Forecast works in turn fractions, not tick fractions; simplest adapter |
| 2026-03-28 | Keep 30-line fleet queue comment as 2-line summary | The conclusion is clear (multiple yards = more speed, not parallel queues); implementation already reflects this |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] `production_engine.py` under 600 lines
- [ ] `production_spawner.py` and `production_math.py` each under 300 lines
- [ ] No new test failures beyond pre-existing 17
- [ ] Audit passed
- [ ] User verified
