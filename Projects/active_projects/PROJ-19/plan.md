# PROJ-19: Type Safety via Protocols

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-19` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-19 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Create Core Protocols | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Replace Strategy Screen Duck Typing | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Replace AI Layer Duck Typing | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Update Remaining UI Files | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Final Audit and Verification | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-01-25 Planning
**Active Phase:** Planning Complete - Ready for Approval
**Last Action:** Completed exploration, risk analysis, and detailed planning
**Next Action:** User approval of plan, then begin Phase 1
**Blockers:** None
**Context:** Pre-existing test issues: test_ui_widgets.py has ImportError (Button removed in earlier phase), test_intercept_integration is flaky but passes on retry

## Overview
Replace duck typing patterns (hasattr/getattr) with Protocol-based isinstance checks across the codebase. This is Phase 6 of the Legacy Code Cleanup project. Currently 254 hasattr() and 190 getattr() calls exist in game/; goal is to reduce hasattr to <100 by creating @runtime_checkable Protocols and TypeGuard functions.

## Goals
- Create `game/core/protocols.py` with runtime_checkable Protocol classes for strategy entities
- Create TypeGuard utility functions for clean type narrowing
- Replace duck typing clusters in strategy_screen.py, strategy_detail_fmt.py, and AI layer
- Reduce hasattr count from 254 to <100 (legitimate uses only)

## Scope
**In:** Strategy entity Protocols (Fleet, Planet, StarSystem, Star, WarpPoint), Combat entity Protocols (ICombatant), TypeGuard functions, UI layer duck typing (strategy_screen.py, strategy_detail_fmt.py, strategy_scene.py), AI layer (controller.py, behaviors.py)

**Out:** Existing IControllable ABC (different purpose), simulation layer internals, formation-related getattr (genuinely optional), app.py hasattr (lazy initialization)

## Key Files
| Component | File Path |
|-----------|-----------|
| Protocols (NEW) | `game/core/protocols.py` |
| Strategy Screen | `game/ui/screens/strategy_screen.py` |
| Detail Formatter | `game/ui/screens/strategy_detail_fmt.py` |
| AI Controller | `game/ai/controller.py` |
| Existing ABC Reference | `game/ai/interfaces/controllable.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [PHASE_6_TYPE_SAFETY_PROTOCOLS.md](../../legacy_cleanup/PHASE_6_TYPE_SAFETY_PROTOCOLS.md) - Original phase spec

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (except documented pre-existing failures)
- [ ] hasattr count < 100
- [ ] Manual test: Strategy map entity selection works
- [ ] User verified
