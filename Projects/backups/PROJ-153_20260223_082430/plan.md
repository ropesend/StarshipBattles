# PROJ-153: test_coverage_ui_builder

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-153` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-153 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. UI-Framework | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. UI-Screens | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-02-14 04:04
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-14_031258_sweep_full-codebase-sweep. Total findings selected: 11 (Critical: 0, Major: 3, Other: 8).

## Goals
- Address TCG-UI1-004: InteractionController (drag-drop for shi
- Address TCG-UI1-012: builder/ subpackage has no test files at
- Address TCG-UI1-013: test_lab/ subpackage has minimal direct
- Address TCG-UI2-005: ShipThemeManager Missing Tests for Concu
- Address TCG-UI2-007: InputMapper Missing Tests for Numpad Key
- Address TCG-UI2-008: ScreenshotManager Missing Tests for Very
- Address TCG-UI2-009: ShipFactory Missing Tests for Invalid De
- Address TCG-UI1-017: DesignSelectorWindow tests don't cover r
- Address TCG-UI1-018: GalaxyTestScreen (galaxy_test/ subpackag
- Address TCG-UI1-021: workshop_event_router.py, workshop_data_
- ...and 1 more findings

## Scope
**In:**
- game/ui/assets/ship_theme_mana
- game/ui/screens/builder/*.py
- game/ui/screens/builder/intera
- game/ui/screens/galaxy_test/*.
- game/ui/screens/setup_renderer
- game/ui/screens/test_lab/*.py
- game/ui/screens/workshop_event
- game/ui/services/input_mapper.
- game/ui/services/screenshot_ma
- game/ui/services/ship_factory.
- tests/unit/ui/screens/test_des

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `game/ui/assets/ship_theme_mana` |
| [TBD] | `game/ui/screens/builder/*.py` |
| [TBD] | `game/ui/screens/builder/intera` |
| [TBD] | `game/ui/screens/galaxy_test/*.` |
| [TBD] | `game/ui/screens/setup_renderer` |
| [TBD] | `game/ui/screens/test_lab/*.py` |
| [TBD] | `game/ui/screens/workshop_event` |
| [TBD] | `game/ui/services/input_mapper.` |
| [TBD] | `game/ui/services/screenshot_ma` |
| [TBD] | `game/ui/services/ship_factory.` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
