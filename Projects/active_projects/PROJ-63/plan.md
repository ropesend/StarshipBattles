# PROJ-63: Break Down build_queue_screen.py

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-63` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-63 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Extract BuildQueuePortraitLoader | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract BuildQueueDragHandler | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract BuildQueueController | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Cleanup & Final Verification | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-07
**Active Phase:** Phase 4
**Last Action:** Phase 3 complete - extracted BuildQueueController (114 lines removed), screen now 603 lines
**Next Action:** Begin Phase 4 - Cleanup & Final Verification
**Blockers:** None

## Overview
Decompose `game/ui/screens/build_queue_screen.py` (945 lines) into the main screen file (~400-450 lines) plus 3 extracted modules in `game/ui/panels/`. Target: main file under 500 lines.

## Goals
- Reduce `build_queue_screen.py` from 945 to under 500 lines
- Extract 3 cohesive modules with clear single responsibilities
- Preserve all existing behavior (zero functional changes)
- All 6248 tests continue to pass after each phase

## Scope
**In:** Extracting portrait loading, drag-drop handling, and queue operations into separate files
**Out:** Functional changes, layout changes, new features, test refactoring beyond import updates

## Key Files
| Component | File Path |
|-----------|-----------|
| Main screen (target) | `game/ui/screens/build_queue_screen.py` |
| Portrait loader (new) | `game/ui/panels/build_queue_portraits.py` |
| Drag handler (new) | `game/ui/panels/build_queue_drag_handler.py` |
| Queue controller (new) | `game/ui/panels/build_queue_controller.py` |
| Test conftest | `tests/integration/ui/build_queue_screen/conftest.py` |
| Test basics | `tests/integration/ui/build_queue_screen/test_basics.py` |
| Test drag-drop | `tests/integration/ui/test_build_queue_drag_drop.py` |
| Test design report | `tests/integration/ui/test_build_queue_design_report.py` |
| Test portrait logging | `tests/integration/ui/build_queue_screen/test_portrait_logging.py` |
| Test formatting | `tests/integration/ui/test_build_queue_formatting.py` |
| Test planet report | `tests/integration/ui/test_build_queue_enhanced_planet_report.py` |
| Test bug 15 | `tests/repro_issues/test_bug_15_screenshot_strategy.py` |
| Test bug 17 | `tests/repro_issues/test_bug_17_drag_preview.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
