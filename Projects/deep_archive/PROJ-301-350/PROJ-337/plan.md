# PROJ-337 — UI Research Subsystem Characterization

## Quick Status

| Phase | Scope | Status |
|---|---|---|
| Phase 1 | Gap-fill characterization tests for `research_scene.py`, `research_renderer.py`, `research_controls.py` | Planning complete; ready for implementation |

## Overview

This is a **gap-fill / consolidation** project, not a green-field
characterization. The original brief stated "ZERO test coverage" for the
research UI subsystem. Verification of the `tests/` tree contradicts this:

| File | Existing tests | LOC |
|---|---|---|
| `research_renderer.py` | `tests/unit/research/test_research_renderer.py` | 259 |
| `research_scene.py` | `tests/unit/research/research_scene/{test_initialization,test_callbacks,test_interaction}.py` + `tests/unit/research/test_research_scene_di.py` | 705 |
| `research_controls.py` | `tests/unit/research/research_controls/test_reset_state.py` + `conftest.py` | 357 |
| **Total** | | **~1320 LOC** |

The PROJ-147 file move did NOT lose the tests. They were updated in-place
(see PROJ-147 references in conftests and module-path patches). The gap
audit's claim was incorrect — likely the audit scanned for
`tests/unit/ui/research/` (which contains only `__init__.py`) and missed
`tests/unit/research/research_scene/` and `tests/unit/research/research_controls/`.

## Goals

Pin the ~55 missing behaviors identified across the three production files:

- ~12 missing behaviors in `research_scene.py` (handle_event routing, draw
  paint order, handle_input camera routing, handle_resize re-push of
  selected node, validate_requirements logging, _on_next_turn refresh).
- ~18 missing behaviors in `research_renderer.py` (draw orchestration,
  dependency line color/dashed branches, dashed-line geometry, node color
  by status, selection highlight widths, allocation indicator,
  zoom-conditional text, text truncation, font min-size).
- ~25 missing behaviors in `research_controls.py` (button/slider event
  routing, update_selected_node label population, clear_selection,
  budget display, auto-spread asymmetry, allocation slider range floor,
  update_turn_log per-event-type rendering, log truncation).

## Scope

**IN scope**

- Add new tests in the existing `tests/unit/research/research_*`
  directories, mirroring existing fixture patterns.
- Reuse existing fixtures: `_patched_research_scene`, `mock_pygame_gui`,
  `mock_tracker`, `mock_node`, `renderer_module`.
- One characterization commit per behavior cluster (typically one public
  method).

**OUT of scope**

- Relocating tests to `tests/unit/ui/research/` (master-plan rule
  explicitly forbids "Moving existing tests into a new layout").
- Refactoring production code for testability.
- PROJ-329-style two-stage construction or builder seam for
  `ResearchControlPanel` (deferred per user direction).
- Golden-image / pixel-level visual diffing.

## Success Criteria

- Each behavior in `phase_1_checklist.md` has a corresponding `assert` in
  a committed test.
- `pytest tests/unit/research/ -x -q` is green.
- Full sharded suite (`python Tools/test_sharded/test_sharded.py`) is green.
- `python Tools/lint_test_files.py` reports 0 violations on new test files.
- New test files each stay under 500 LOC.

## Source Documents

- `test_coverage_master_plan_v1.md` — master plan that originated PROJ-337.
- `Projects/active_projects/PROJ-329A/plan.md` — reference shape for
  artefacts.
- Existing conftest patterns:
  - `tests/unit/research/research_scene/conftest.py`
  - `tests/unit/research/research_controls/conftest.py`
  - `tests/unit/research/test_research_renderer.py` (`renderer_module`
    autouse fixture)

## Estimate

~2 sessions, ~55 mostly-mechanical pin-the-call tests.
