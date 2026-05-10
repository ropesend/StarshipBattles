# PROJ-113: Architecture Layer Violations

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-113` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-113 [phase]` before stopping
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
**Last Updated:** 2026-02-12
**Active Phase:** Phase 5
**Last Action:** Phase 4 complete - 4 ALREADY FIXED (Phase 1), 2 FALSE POSITIVE, 2 ARCHITECTURAL PATTERN, 1 ACCEPTABLE, 1 INFO
**Next Action:** Begin Phase 5 (UI-Screens findings)
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-11_sweep_full-codebase-sweep. Total findings selected: 52 (Critical: 9, Major: 14, Other: 29).

## Goals
- Address ADR-FND-001: Pygame imported in game/core/input_mappe
- Address ADR-FND-002: Pygame imported in game/core/screenshot_
- Address ADR-FND-003: Research scene imports from game.ui (Lay
- Address ADR-SIM-001: AIControllerFactory runtime imports from
- Address ADR-SIM-002: persistence.py imports tkinter UI framew
- Address ADR-UI2-001: Pygame in Core Layer -- ScreenshotManage
- Address ADR-UI2-002: Pygame in Core Layer -- InputMapper
- Address ADR-UI1-001: Test Lab UI Imports From test_framework
- Address ADR-UI1-002: Simulation Layer Imports tkinter GUI Fra
- Address ADR-FND-004: Core protocols.py TYPE_CHECKING import f
- ...and 42 more findings

## Scope
**In:**
- Unknown
- game/ai/controller.py
- game/ai/interfaces/controllabl
- game/core/config.py
- game/core/constants.py
- game/core/input_mapper.py
- game/core/protocols.py
- game/core/screenshot_manager.p
- game/engine/collision.py
- game/research/data/
- game/research/ui/research_cont
- game/research/ui/research_scen
- game/simulation/battle_config.
- game/simulation/battle_state.p
- game/simulation/components/abi
- ...and 24 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `Unknown` |
| [TBD] | `game/ai/controller.py` |
| [TBD] | `game/ai/interfaces/controllabl` |
| [TBD] | `game/core/config.py` |
| [TBD] | `game/core/constants.py` |
| [TBD] | `game/core/input_mapper.py` |
| [TBD] | `game/core/protocols.py` |
| [TBD] | `game/core/screenshot_manager.p` |
| [TBD] | `game/engine/collision.py` |
| [TBD] | `game/research/data/` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
