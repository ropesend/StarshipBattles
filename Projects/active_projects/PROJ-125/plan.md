# PROJ-125: PROJ-F_code-consistency

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-125` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-125 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Strategy | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. UI-Framework | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Other | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-13
**Active Phase:** Phase 2
**Last Action:** Phase 1 complete - 23 tasks reviewed, all FALSE POSITIVE or INFORMATIONAL
**Next Action:** Begin Phase 2 tasks
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-13_sweep_full-codebase-sweep. Total findings selected: 78 (Critical: 0, Major: 20, Other: 58).

## Goals
- Address CON-FND-004: Inconsistent Method Naming for Position/
- Address CON-FND-005: Class Naming Suffix Inconsistency - Serv
- Address CON-UI2-003: Mixed Return Type Patterns for Error Han
- Address CON-UI2-004: Inconsistent Parameter Naming for Regist
- Address CON-UI2-005: Missing Type Hints on Public Functions
- Address CON-UI2-006: Docstring Inconsistency - Some Use Googl
- Address CON-UI2-007: Inconsistent Module-Level vs Class-Level
- Address SP-001: Inconsistent Constructor Parameter Order
- Address DUP-FND-001: Clamp Function Duplication
- Address DUP-FND-002: Entity Position/State Access Patterns in
- ...and 68 more findings

## Scope
**In:**
- BattlePanel.handle_click()
- Unknown
- game/ai/behaviors.py
- game/ai/combat_utils.py
- game/ai/controller.py
- game/ai/interfaces/controllabl
- game/ai/strategy_manager.py
- game/core/
- game/core/constants.py
- game/core/logger.py
- game/core/math.py
- game/core/paths.py
- game/core/validation.py
- game/research/data/research_tr
- game/research/data/tech_tree.p
- ...and 25 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `BattlePanel.handle_click()` |
| [TBD] | `Unknown` |
| [TBD] | `game/ai/behaviors.py` |
| [TBD] | `game/ai/combat_utils.py` |
| [TBD] | `game/ai/controller.py` |
| [TBD] | `game/ai/interfaces/controllabl` |
| [TBD] | `game/ai/strategy_manager.py` |
| [TBD] | `game/core/` |
| [TBD] | `game/core/constants.py` |
| [TBD] | `game/core/logger.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
