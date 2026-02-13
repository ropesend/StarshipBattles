# PROJ-132: Architecture Layer Violations

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-132` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-132 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simulation | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Strategy | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI-Framework | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. UI-Screens | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-13
**Active Phase:** All Phases Complete - Ready for Audit
**Last Action:** Phase 5 complete - 5 fixes (facade accessor, public method, cache accessor, clear_selection), 6 accepted as-is (god classes already decomposed, internal coupling patterns)
**Next Action:** Run audit (Protocol 04)
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-13_092036_sweep_full-codebase-sweep. Total findings selected: 24 (Critical: 2, Major: 10, Other: 12).

## Goals
- Address ADR-FND-001: Research UI layer imports from game.ui
- Address ADR-SIM-001: Simulation imports AI layer in factory f
- Address ADR-STR-001: Galaxy Class Exceeds Size Threshold (God
- Address ADR-STR-002: ProductionEngine Exceeds Size Threshold
- Address ADR-UI2-001: Direct Simulation Layer Import in ship_i
- Address ADR-UI1-001: TestLabScreen God Class
- Address ADR-UI1-002: FleetReportWindow God Class
- Address ADR-UI1-003: BuildQueueScreen Large Class
- Address ADR-UI1-004: StrategyScreen Large Class
- Address ADR-UI1-005: Private Facade Access in Dialogs
- ...and 14 more findings

## Scope
**In:**
- game/ai/interfaces/controllabl
- game/core/protocols.py
- game/research/ui/research_scen
- game/simulation/battle_control
- game/simulation/components/com
- game/simulation/entities/ship.
- game/simulation/systems/battle
- game/strategy/data/galaxy.py
- game/strategy/data/ship_instan
- game/strategy/engine/productio
- game/strategy/services/ship_st
- game/ui/screens/battle_ui.py
- game/ui/screens/build_queue_sc
- game/ui/screens/cargo_quick_di
- game/ui/screens/fleet_report_w
- ...and 7 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `game/ai/interfaces/controllabl` |
| [TBD] | `game/core/protocols.py` |
| [TBD] | `game/research/ui/research_scen` |
| [TBD] | `game/simulation/battle_control` |
| [TBD] | `game/simulation/components/com` |
| [TBD] | `game/simulation/entities/ship.` |
| [TBD] | `game/simulation/systems/battle` |
| [TBD] | `game/strategy/data/galaxy.py` |
| [TBD] | `game/strategy/data/ship_instan` |
| [TBD] | `game/strategy/engine/productio` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
