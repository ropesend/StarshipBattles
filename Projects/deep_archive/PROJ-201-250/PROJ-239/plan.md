# PROJ-239: Strategy Layer Health Remediation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-239` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-239 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical Fixes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Architecture Boundary Fixes | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Code Quality & Dead Code Cleanup | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Documentation Updates | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-05 14:15
**Active Phase:** Project Complete
**Last Action:** Completed Phase 4 — all 4 documentation update tasks
**Next Action:** None — all 14 tasks across 4 phases are complete
**Blockers:** None
**Context for Next Agent:**
- Phases 1-2 complete: 5 tasks done, 22 new tests added
- Phase 2 summary:
  - AR-003: `_colony_has_planetary_yard` moved from engine to `build_queue_source.py` as public `colony_has_planetary_yard`. `_RegistriesFromProvider` adapter replaces `RegistryManager.instance()`. Note: 19 pre-existing test failures in `test_build_queue_source.py` (not caused by our changes — confirmed by running original code).
  - AR-004: `IssueTransferCommand` import moved to TYPE_CHECKING + late import in `build_transfer_command()`. Fixed 2 test patches in `test_cargo_quick_dialog.py`.
  - AR-005: All 8 engines now inherit their interface ABCs. 12 parametrized tests.
- Full test suite: 14,297 passed, 10 failed (all pre-existing quickstart design mismatches)
- New test files: `test_data_layer_boundaries.py`, `test_engine_inheritance.py`, `test_no_ai_import.py`, `test_turn_error_handling.py`

## Overview
Systematic remediation of the top 10 priority issues found in the strategy layer general health review. 14 findings total (2 Critical, 12 Major) organized into 4 phases by category: critical fixes first, then architecture boundaries, code quality, and documentation.

**Source review:** [report.md](../../Reviews/results/2026-04-05_110710_general_strategy-layer-health/report.md)

## Goals
1. Eliminate crash risk from unhandled turn engine exceptions (ERR-001)
2. Fix architecture layer violation — Strategy importing from AI (AR-001)
3. Restore subpackage boundary discipline — data/→engine/, services/→engine/ (AR-003, AR-004)
4. Make sub-engines implement their declared interfaces (AR-005)
5. Deduplicate superweapon stabilizer checks and eliminate mock hack (CQ-003, CQ-004)
6. Remove ~190 lines of dead code (DC-003, DC-004, DC-005)
7. Bring orders_system.md and strategy_layer.md up to date (DOCC-001, DOCC-002, DOCC-003)
8. (Deferred — tracked, not in scope) Facade bypass cleanup (AR-002) — complex, cross-cutting

## Scope
**In:**
- `game/strategy/engine/turn_engine.py` — error handling (ERR-001)
- `game/strategy/adapters/simulation_adapter.py` — AI import fix (AR-001)
- `game/strategy/data/build_queue_source.py` — engine dependency removal (AR-003)
- `game/strategy/services/cargo_transfer_service.py` — engine command dependency (AR-004)
- `game/strategy/interfaces/engines.py` + 8 engine files — interface inheritance (AR-005)
- `game/strategy/engine/superweapon_order_processor.py` — stabilizer dedup (CQ-003)
- `game/strategy/services/fleet_navigation_service.py` — mock hack removal (CQ-004)
- `game/strategy/engine/planet_energy_engine.py` — dead method removal (DC-003)
- `game/strategy/generation/loaders/astrophysics_loader.py` — dead method removal (DC-004)
- `game/strategy/data/empire.py` — dead method removal (DC-005)
- `game/strategy/engine/game_session.py` — dead method removal (DC-005)
- `game/strategy/systems/design_library.py` — dead method removal (DC-005)
- `docs/systems/orders_system.md` — FleetOrder→Order rename, missing order types (DOCC-001, DOCC-002)
- `docs/systems/strategy_layer.md` — missing commands, engines (DOCC-003, DOCC-004)

**Out:**
- AR-002 (facade bypass) — complex, cross-cutting refactor; tracked but deferred
- Other Minor/Info findings from the review
- New feature development

## Key Files
| Component | File Path |
|-----------|-----------|
| Turn engine | `game/strategy/engine/turn_engine.py` |
| Battle resolver adapter | `game/strategy/adapters/simulation_adapter.py` |
| Build queue source | `game/strategy/data/build_queue_source.py` |
| Cargo transfer service | `game/strategy/services/cargo_transfer_service.py` |
| Engine interfaces | `game/strategy/interfaces/engines.py` |
| Superweapon processor | `game/strategy/engine/superweapon_order_processor.py` |
| Fleet navigation service | `game/strategy/services/fleet_navigation_service.py` |
| Planet energy engine | `game/strategy/engine/planet_energy_engine.py` |
| Astrophysics loader | `game/strategy/generation/loaders/astrophysics_loader.py` |
| Empire | `game/strategy/data/empire.py` |
| Game session | `game/strategy/engine/game_session.py` |
| Design library | `game/strategy/systems/design_library.py` |
| Orders system doc | `docs/systems/orders_system.md` |
| Strategy layer doc | `docs/systems/strategy_layer.md` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [Source review report](../../Reviews/results/2026-04-05_110710_general_strategy-layer-health/report.md)

## Verification
- [x] All phase checklists complete
- [x] All tests passing (`python scripts/test_sharded.py`) — 14,297+ passed, same 10 pre-existing quickstart failures
- [x] Documentation updated in same commits as code changes
- [ ] User verified
