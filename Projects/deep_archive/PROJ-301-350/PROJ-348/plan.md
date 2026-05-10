# PROJ-348: Closeout Sprint 6 - Controller boundary cleanup from PROJ-329C review

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-348` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Controller boundary fixes (T5.1 .. T5.4) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Planning (awaiting implementation kickoff)
**Last Action:** Project scaffolded
**Next Action:** Begin Phase 1
**Blockers:** PROJ-343 must land first if T1.5 (CargoQuickDialog teardown) overlaps with T5.1/T5.2 (CargoQuickDialog controller boundary). Implementer should sequence accordingly.

## Overview

Four controller-boundary violations in the new PROJ-329C controllers. T5.1 + T5.2 are CargoQuickDialog (controller reads UI sliders directly; Stage 1 reaches `scene.facade`). T5.3 is `PlanetListController.navigate_to()` — defined but never called. T5.4 removes the `__new__` test seam in `planet_list_window.py`. All file-disjoint with the production-bug fixes in PROJ-343 (different concerns at the same files).

## Goals

- T5.1: `CargoQuickDialogController.issue_orders` no longer reads pygame_gui widgets directly. Slider reads happen in the dialog; resolved values dict is passed to controller.
- T5.2: `CargoQuickDialog.__init__` Stage 1 (cheap-pure) does NOT touch `scene.facade`.
- T5.3: `PlanetListController.navigate_to()` is either deleted (if dead) or wired through (if intended).
- T5.4: `planet_list_window.py:687-701` `_resolve_demographic_view` fallback for `__new__`-bypass tests is removed; tests construct via the bypass path instead.

## Scope

**In:**
- `game/ui/screens/cargo_quick_dialog.py` (T5.1)
- `game/ui/screens/cargo_quick_dialog_controller.py` (T5.1, T5.2)
- `game/ui/screens/planet_list_controller.py` (T5.3)
- `game/ui/screens/planet_list_window.py:687-701` (T5.4)
- `tests/unit/ui/screens/test_planet_list_window*.py:38-50` and other `__new__` test sites (T5.4)
- New characterization tests asserting controller never touches widgets (T5.1)

**Out:**
- Any non-Tier-5 finding.

## Key Files

| Component | File Path |
|-----------|-----------|
| T5.1 dialog | `game/ui/screens/cargo_quick_dialog.py:172-181, 300-306` |
| T5.1 controller | `game/ui/screens/cargo_quick_dialog_controller.py:9-13, 69-79, 100-102` |
| T5.2 facade reach | `game/ui/screens/cargo_quick_dialog.py:__init__` Stage 1 |
| T5.3 dead method | `game/ui/screens/planet_list_controller.py:navigate_to` |
| T5.3 caller path | `game/ui/screens/planet_list_window.py` `self.on_navigate_callback(loc)` site |
| T5.4 test seam | `game/ui/screens/planet_list_window.py:687-701` (`_resolve_demographic_view`) |
| T5.4 test sites | `tests/unit/ui/screens/test_planet_list_window.py:38-50` |

## Verification

- [ ] All Phase 1 tasks checked
- [ ] `pytest tests/unit/ui/screens/ -x -q` — all pass
- [ ] `python Tools/lint_test_files.py` — 0 violations
- [ ] User verified
