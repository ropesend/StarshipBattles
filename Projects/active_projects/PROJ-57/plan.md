# PROJ-57: Test Lab Screen God Class Decomposition

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-57` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-57 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Setup & Extract Leaf Nodes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Composite Nodes | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract Screen & Wire Up Package | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Update External References | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Verification & Documentation | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-07
**Active Phase:** Complete - Ready for Audit
**Last Action:** Phase 5 complete - Verification passed, README.md written
**Next Action:** Run audit (Protocol 04)
**Blockers:** None
**Context for Next Agent:** All 5 phases complete. 6246 tests passing. Package fully functional. README documented. Ready for audit.

## Overview
Decompose `game/ui/screens/test_lab_screen.py` (4,703 lines, 11 classes) into a well-organized `game/ui/screens/test_lab/` package. This is the single largest file in the project and contains the entire Combat Lab UI. The decomposition follows existing `builder/` and `formation/` package precedents.

## Goals
- Reduce cognitive load: no file over ~830 lines (except orchestrator at ~2460)
- Enable independent editing of UI widgets without touching unrelated code
- Follow existing codebase patterns (`builder/` package structure)
- Zero test regressions (baseline: 6114 passed, 5 skipped)
- Clean documentation for AI agent maintainability

## Scope
**In:**
- Decompose all 11 classes from `test_lab_screen.py` into separate modules
- Delete legacy `test_lab.py` (verified dead code)
- Update all imports and patch paths in production and test code
- Write package README documentation

**Out:**
- Further decomposition of `TestLabScreen` class itself (~2460 lines) — future project
- Refactoring internal logic of any extracted class
- Changes to test behavior or coverage

## Key Files
| Component | File Path |
|-----------|-----------|
| Source file (to decompose) | `game/ui/screens/test_lab_screen.py` |
| Legacy file (to delete) | `game/ui/screens/test_lab.py` |
| Production import site | `game/app.py:30` |
| Test file (18 patches) | `tests/unit/test_lab/test_data_paths.py` |
| Test file (7 patches) | `tests/unit/test_lab/test_visual_run.py` |
| Package pattern reference | `game/ui/screens/builder/__init__.py` |
| Package pattern reference | `game/ui/screens/formation/__init__.py` |

## Target Package Structure
```
game/ui/screens/test_lab/
    __init__.py              (~15 lines)   Re-exports TestLabScreen
    dialogs.py               (~250 lines)  JSONPopup + ConfirmationDialog
    json_viewer.py           (~110 lines)  ScrollableJSONViewer
    component_dropdown.py    (~140 lines)  ComponentDropdown
    ship_panels.py           (~240 lines)  ShipPanel + TabbedShipPanel + ComponentPanel
    test_run_card.py         (~370 lines)  TestRunCard
    test_run_details.py      (~830 lines)  TestRunDetailsPanel
    results_panel.py         (~245 lines)  ResultsPanel
    screen.py                (~2460 lines) TestLabScreen + get_test_data_dir()
```

## Related Documents
- [design.md](design.md) - Architecture analysis, dependency graph, swarm findings
- [decisions.md](decisions.md) - Full decisions log with rationale

## Verification
- [x] All phase checklists complete
- [x] `pytest tests/ -x -q` — 6246 tests passing
- [x] `pytest tests/unit/test_lab/ -v` — 35 tests passing
- [x] `pytest tests/unit/ui/test_lab_scene/ -v` — 79 tests passing
- [x] Manual: Import verification proves package works
- [ ] Audit passed
- [ ] User verified
