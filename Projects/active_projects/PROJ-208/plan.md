# PROJ-208: CQRS Facade Bypass Remediation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-208` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-208 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fleet Management Commands | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Build Queue Commands | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Research & Misc Commands | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. DTO Enhancements & Read Path | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-28
**Active Phase:** Phase 4
**Last Action:** Phase 3 complete - Facade routing fixed in strategy_window_manager.py (4 callbacks), strategy_build_queue_manager.py (3 sites), build_queue_screen.py, empire_build_queue_window.py. Research commands (3.1-3.4) DEFERRED - research scene is standalone sandbox not integrated with strategy layer.
**Next Action:** Phase 4 - DTO Enhancements & Read Path
**Blockers:** None

## Overview

Systematic remediation of CQRS/facade bypass violations found in the UI layer. The `StrategySessionFacade` is designed as the single entry point for UI-to-engine communication, but three major subsystems bypass it entirely.

**Source Review:** [2026-02-27_211111_general_facade-bypass-layering-violations](../../Reviews/results/2026-02-27_211111_general_facade-bypass-layering-violations/)

### Violation Summary
- **54 validated findings** (10 Critical, 22 Major, 14 Minor, 8 Info)
- **10 new commands** needed to close all gaps
- **3 violation clusters:** Fleet management, Build queue, Research
- **Root cause:** `StrategyScreen` exposes raw domain objects to all sub-modules

### Test Baseline
Run full suite before starting: `pytest tests/ -n 12`
Expected: **7353+ tests passing**

## Goals
1. Create missing commands for all state-mutating UI operations
2. Route all UI mutations through `facade.handle_command()`
3. Eliminate direct domain object mutation from UI layer
4. Enhance DTOs to reduce need for raw domain access on read path

## Scope

**In:**
| Cluster | Files | New Commands |
|---------|-------|-------------|
| Fleet Management | `fleet_report_window.py`, `fleet_orders_window.py` | `SplitFleetCommand`, `DeleteFleetOrderCommand`, `ReorderFleetOrderCommand` |
| Build Queue | `build_queue_controller.py`, `build_queue_drag_handler.py`, `build_queue_screen.py`, `empire_build_queue_window.py` | `AddToConstructionQueueCommand`, `RemoveFromConstructionQueueCommand`, `ReorderConstructionQueueCommand` |
| Research | `research_controls.py` | `SetResearchBudgetCommand`, `SetResearchAllocationCommand`, `SpreadResearchRPCommand` |
| Routing Fixes | `strategy_window_manager.py`, `strategy_build_queue_manager.py` | N/A (route through facade) |

**Out:**
- Renderer domain access (read-only, performance concern — separate project)
- StrategyScreen raw property exposure (root cause — too large for this project)
- Superweapon capability checks (need FleetInfo.capabilities DTO enhancement first)
- Minor/Info findings (DTO gaps, enum imports, dev tools)

## Key Files
| Component | File Path |
|-----------|-----------|
| Facade | `game/strategy/facade/strategy_session_facade.py` |
| Commands | `game/strategy/engine/commands.py` |
| Command Handlers | `game/strategy/engine/command_handlers.py` |
| Fleet Report Window | `game/ui/screens/fleet_report_window.py` |
| Fleet Orders Window | `game/ui/screens/fleet_orders_window.py` |
| Build Queue Controller | `game/ui/panels/build_queue_controller.py` |
| Build Queue Drag Handler | `game/ui/panels/build_queue_drag_handler.py` |
| Build Queue Screen | `game/ui/screens/build_queue_screen.py` |
| Empire Build Queue Window | `game/ui/screens/empire_build_queue_window.py` |
| Research Controls | `game/ui/research/research_controls.py` |
| Strategy Window Manager | `game/ui/screens/strategy_window_manager.py` |
| Strategy Build Queue Manager | `game/ui/screens/strategy_build_queue_manager.py` |
| Fleet DTO | `game/strategy/facade/dto/fleet_dto.py` |

## Related Documents
- [design.md](design.md) - Command specifications and architecture decisions
- [decisions.md](decisions.md) - Full decisions log
- [Review Report](../../Reviews/results/2026-02-27_211111_general_facade-bypass-layering-violations/report.md)
- [Command Gap Analysis](../../Reviews/results/2026-02-27_211111_general_facade-bypass-layering-violations/findings/command_gap_analyst_report.md)
- [DTO Coverage Analysis](../../Reviews/results/2026-02-27_211111_general_facade-bypass-layering-violations/findings/dto_coverage_analyst_report.md)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] No direct domain mutation remaining in scoped UI files
- [ ] All new commands have handler tests
- [ ] Audit passed
