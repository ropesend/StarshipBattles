# PROJ-212: Deferred Import Cleanup & Coupling Reduction

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-212` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-212 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Quick Wins (Simple fixes) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. OrderType/FleetOrder Extraction | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. DI & Service-Locator Fixes | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-27
**Active Phase:** All phases complete - Ready for Audit
**Last Action:** Phase 3 complete - DI & service-locator fixes
**Next Action:** Trigger audit (Protocol 04)
**Blockers:** None
**Baseline:** 12866 passed, 1 skipped (+ 4 pre-existing bug_13 failures)

## Overview
Systematic remediation of 9 Major findings from the Circular Dependency & Deferred Import review (2026-02-27). The review validated that the codebase has strong architectural layer discipline (zero top-level layer violations), but accumulated deferred import debt — particularly around `fleet.py`'s OrderType/FleetOrder and inconsistent import patterns in UI and engine files.

## Goals
1. Eliminate unnecessary deferred imports where no circular dependency exists
2. Extract OrderType/FleetOrder from monolithic fleet.py to break transitive import chains
3. Fix facade bypass in strategy_build_queue_manager.py
4. Replace service-locator anti-pattern in fleet_capability_calculator.py
5. Consolidate duplicate inline imports (DRY cleanup)

## Scope
**In:**
- `game/strategy/data/fleet.py` — OrderType/FleetOrder extraction
- `game/strategy/engine/command_handlers.py` — 11 deferred fleet imports
- `game/ui/screens/strategy_build_queue_manager.py` — duplicate imports + facade bypass
- `game/ui/screens/strategy_fleet_ops.py` — unnecessary deferred command imports
- `game/simulation/components/abilities/weapons.py` — 7x formula_system imports
- `game/strategy/data/fleet_capability_calculator.py` — service-locator pattern
- `game/core/registry` consumers — 12 files with deferred registry imports

**Out:**
- `game/app.py` lazy loading (intentional, Info-level)
- TYPE_CHECKING imports (standard Python, not defects)
- Strategy data layer internal coupling (tracked by PROJ-87)
- Minor/Info findings from the review (18 Minor, 6 Info — deferred)

## Key Files
| Component | File Path |
|-----------|-----------|
| Fleet data model | `game/strategy/data/fleet.py` |
| Command handlers | `game/strategy/engine/command_handlers.py` |
| Build queue UI | `game/ui/screens/strategy_build_queue_manager.py` |
| Fleet ops UI | `game/ui/screens/strategy_fleet_ops.py` |
| Weapon abilities | `game/simulation/components/abilities/weapons.py` |
| Fleet capability calc | `game/strategy/data/fleet_capability_calculator.py` |
| Core registry | `game/core/registry.py` |

## Phase Strategy
- **Phase 1:** Quick wins — promote deferred imports to top-level, consolidate duplicates, fix facade bypass. All Simple effort, zero architectural change.
- **Phase 2:** Extract OrderType/FleetOrder from fleet.py into a new lightweight module. Medium effort, highest leverage — eliminates 15+ unnecessary deferred imports across the codebase.
- **Phase 3:** Replace service-locator in fleet_capability_calculator.py with constructor DI. Audit and fix deferred registry imports where safe. Medium effort.

## Overlap with Other Projects
- **PROJ-87** (Strategy Data Tier): IIA-006 (strategy data internal coupling) is explicitly deferred to PROJ-87. The OrderType extraction in Phase 2 is complementary — it reduces fleet.py's surface area, which helps PROJ-87.
- **PROJ-86** (Critical UI Tier): RS-004 (facade bypass) and CA-002 (duplicate imports) touch UI files that PROJ-86 may also refactor.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [Review Report](../../Reviews/results/2026-02-27_211243_general_circular-dependency-deferred-imports/report.md)

## Verification
- [x] All phase checklists complete
- [x] All tests passing (baseline: 12866)
- [ ] Audit passed
- [ ] User verified
