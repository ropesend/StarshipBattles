# PROJ-128: codebase-consistency

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-128` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-128 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simulation | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Strategy | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI-Framework | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. UI-Screens | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-13
**Active Phase:** Phase 4
**Last Action:** Phase 3 complete - 8 RESOLVED, 2 ACCEPTABLE, 2 INFO
**Next Action:** Begin Phase 4 UI-Framework tasks
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-13_sweep_full-codebase-sweep. Total findings selected: 73 (Critical: 1, Major: 17, Other: 55).

## Goals
- Address CON-SIM-001: ResourceRegistry Return Type Inconsisten
- Address CON-SIM-002: Duplicate Exception Handler in design_lo
- Address CON-SIM-003: Magic Numbers in Projectile Guidance Sys
- Address CON-SIM-004: Singleton Fallback Pattern in Validation
- Address CON-SIM-005: Inconsistent Parameter Naming - resource
- Address CON-SIM-006: Type Hint Gaps in Physics and Combat Mod
- Address CON-SIM-007: AIControllerFactory Uses Positional Para
- Address CON-SIM-008: Magic Numbers in Targeting and Combat Sy
- Address CON-STR-001: Logging Pattern Inconsistency - Mixed Mo
- Address CON-STR-002: Protocol Interface Decorator Inconsisten
- ...and 63 more findings

## Scope
**In:**
- BattlePanel.handle_click()
- Unknown
- game/ai/controller.py
- game/ai/interfaces/controllabl
- game/core/constants.py
- game/core/logger.py
- game/core/validation.py
- game/research/data/tech_tree.p
- game/research/ui/research_scen
- game/simulation/combat/targeti
- game/simulation/components/abi
- game/simulation/entities/abili
- game/simulation/entities/proje
- game/simulation/entities/ship_
- game/simulation/factories/ai_f
- ...and 26 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `BattlePanel.handle_click()` |
| [TBD] | `Unknown` |
| [TBD] | `game/ai/controller.py` |
| [TBD] | `game/ai/interfaces/controllabl` |
| [TBD] | `game/core/constants.py` |
| [TBD] | `game/core/logger.py` |
| [TBD] | `game/core/validation.py` |
| [TBD] | `game/research/data/tech_tree.p` |
| [TBD] | `game/research/ui/research_scen` |
| [TBD] | `game/simulation/combat/targeti` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
