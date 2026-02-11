# PROJ-105: Visual Regression Testing for UI Panels

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-105` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-105 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Core Infrastructure | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Mock Data & Panel Registry | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Image Comparison & Test Runner | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Capture Baselines & Verify | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-10 22:30
**Active Phase:** Planning
**Last Action:** Swarm review complete, plan drafted
**Next Action:** User approval, then begin Phase 1
**Blockers:** None
**Baseline Tests:** 8167 passed, 0 failures, 2 warnings

## Overview
Add a pre/post refactor visual regression testing tool for battle UI panels. The system renders panels with deterministic mock data to a headless Pygame surface, saves PNG snapshots, and compares them pixel-by-pixel using Pillow. This catches subtle rendering regressions during the ongoing god class decomposition projects (PROJ-86/87/88/89).

## Goals
- Detect unintentional visual changes to battle panels after refactoring
- Provide a simple two-command workflow: `--update-baselines` before, compare after
- Generate side-by-side diff images when regressions are detected
- Make it trivial to add new panels to the test registry

## Scope
**In:**
- ShipStatsPanel (collapsed + expanded views)
- SeekerMonitorPanel (with seekers in various states)
- BattleControlPanel (ongoing + victory states)
- Pillow-based pixel diff with configurable thresholds
- pytest integration with `--update-baselines` flag
- Baseline PNGs committed to git

**Out:**
- pygame_gui panels (StrategyScreen, BuilderScreen) — future phase
- Full-screen composite screenshots
- CI/CD integration (local dev workflow only)
- Cross-platform baseline compatibility

## Key Files
| Component | File Path |
|-----------|-----------|
| Battle panels | `game/ui/panels/battle_panels.py` |
| Ship stats renderer | `game/ui/panels/ship_stats_renderer.py` |
| Battle UI DTOs | `game/ui/interfaces/battle_ui.py` |
| UIConfig constants | `game/core/config.py` |
| Root conftest (Pygame init) | `conftest.py` |
| Existing mock service | `tests/unit/ui/mocks/mock_battle_ui_service.py` |
| Existing regression pattern | `tests/regression/modifier_ability_snapshots/conftest.py` |
| VR conftest (NEW) | `tests/visual_regression/conftest.py` |
| VR mock data (NEW) | `tests/visual_regression/mock_data.py` |
| VR panel registry (NEW) | `tests/visual_regression/panel_registry.py` |
| VR image compare (NEW) | `tests/visual_regression/image_compare.py` |
| VR test runner (NEW) | `tests/visual_regression/test_visual_regression.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] `pytest tests/visual_regression/ --update-baselines` creates baseline PNGs
- [ ] `pytest tests/visual_regression/` passes (baselines match)
- [ ] Trivial color change in panel causes test failure with diff image
- [ ] Revert change → tests pass again
- [ ] Audit passed
- [ ] User verified
