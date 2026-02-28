# PROJ-209: Cyclomatic Complexity Decomposition

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-209` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-209 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist | Target |
|-------|--------|-----------|--------|
| 1. SaveGameService.load_game | **Complete** | [phase_1_checklist.md](phase_1_checklist.md) | CC 26 → 5 ✅ |
| 2. ProductionEngine._process_queue_tick_dynamic | Not Started | [phase_2_checklist.md](phase_2_checklist.md) | CC 27 → ~7 |
| 3. FleetNavigationService.project_path | Not Started | [phase_3_checklist.md](phase_3_checklist.md) | CC 22 → ~10 |
| 4. ShipStatsCalculator.calculate_stats | Not Started | [phase_4_checklist.md](phase_4_checklist.md) | CC 26 → ~8 |

## Current State
**Last Updated:** 2026-02-28
**Active Phase:** Phase 2
**Last Action:** Phase 1 COMPLETE — load_game decomposed from CC=26 to CC=5
**Next Action:** Begin Phase 2 — decompose _process_queue_tick_dynamic
**Blockers:** None
**Test Baseline:** 12944 passed, 4 failed (pre-existing bug_13), 1 skipped

## Overview
Decompose 4 critically complex functions (Radon Rank D, CC 22-27) into smaller, testable methods. Each phase targets one function, ordered by risk (lowest first). The review validated proposed decomposition strategies and refined them with specific recommendations.

**Source Review:** [2026-02-27_211154_general_cyclomatic-complexity-deep-dive](../../Reviews/results/2026-02-27_211154_general_cyclomatic-complexity-deep-dive/report.md)

## Goals
1. Reduce all 4 functions below CC=10 (orchestrator) with extracted helpers CC<=8
2. Fix the latent production cost bug (AR-01/CQ-002) before decomposing production engine
3. Fill critical test gaps BEFORE decomposing (test preservation strategy)
4. Maintain facade/delegate pattern — public API unchanged, internal structure improved

## Scope
**In:**
- `game/strategy/systems/save_game_service.py` — `load_game` (CC=26)
- `game/strategy/engine/production_engine.py` — `_process_queue_tick_dynamic` (CC=27)
- `game/strategy/services/fleet_navigation_service.py` — `project_path` (CC=22)
- `game/strategy/services/ship_stats_calculator.py` — `calculate_stats` (CC=26)
- Associated test files for each function

**Out:**
- Other methods in these files (unless directly impacted)
- UI layer changes
- New feature development
- Minor/Info findings from the review (address opportunistically)

## Key Files
| Component | File Path |
|-----------|-----------|
| SaveGameService | `game/strategy/systems/save_game_service.py` |
| ProductionEngine | `game/strategy/engine/production_engine.py` |
| FleetNavigationService | `game/strategy/services/fleet_navigation_service.py` |
| ShipStatsCalculator | `game/strategy/services/ship_stats_calculator.py` |

## Design Principles
1. **Extract, don't relocate** — each extracted method must have lower CC than the original, not just move CC around
2. **Pure functions where possible** — extracted methods that can be pure (no side effects) should be pure
3. **Tests first** — fill test gaps before decomposing, preserve all existing tests as regression suite
4. **Named constants** — replace magic numbers during decomposition (epsilons, iteration limits, ticks-per-turn)
5. **Dataclasses over dicts** — introduce TypedDict/dataclass for return types where dicts are implicit contracts

## Related Documents
- [design.md](design.md) - Architecture analysis and decomposition strategies
- [decisions.md](decisions.md) - Full decisions log
- [Review Report](../../Reviews/results/2026-02-27_211154_general_cyclomatic-complexity-deep-dive/report.md) - Validated findings

## Verification
- [ ] All phase checklists complete
- [ ] All 4 functions below CC=10 (orchestrator)
- [ ] All tests passing (baseline: 7353)
- [ ] Radon re-analysis confirms improvement
- [ ] Audit passed
