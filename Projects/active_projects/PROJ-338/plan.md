# PROJ-338 — UI Panels (High-Risk Characterization)

**Branch:** `feat/proj-338-ui-panels-characterization`
**Created:** 2026-05-04
**Owner:** Ross McLean

## Quick Status

| Phase | Status | Tests Planned | Tests Passing |
|---|---|---:|---:|
| Phase 1 — Characterization | Not started | ~112 | 0 |

## Current State

- **Last Updated:** 2026-05-04
- **Active Phase:** Phase 1 (only phase — single-phase project)
- **Next Action:** Author `tests/unit/ui/panels/test_build_queue_drag_handler.py` (highest-risk file, state-machine dense).
- **Blockers:** None. All testability concerns resolved by reusing existing test patterns.

## Overview

Five high-risk UI panel files in `game/ui/panels/` (and one battle-panels module
in `game/ui/`) carry significant behavior with uneven test coverage.
PROJ-338 adds characterization tests to pin current behavior so that downstream
refactors (notably PROJ-329 builder-seam work) can proceed safely.

The drag handler is the highest-priority gap: it is a state machine with no
unit-test coverage today, only end-to-end integration tests.

Per master arc and user direction: **characterization-only**. TDD does not
apply (we are testing existing behavior, not driving new). No architectural
change recommendations. The current `__new__` / `bypass_init` test pattern is
the assumed substrate.

## Goals

- One characterization test file per production file (5 files total — one
  controller test file is **extended in place** rather than replaced because
  it already carries 1108 LOC of proven PROJ-69/79/208 coverage).
- Pin every observable behavior listed in `phase_1_checklist.md`.
- Surface (do not fix) any latent bugs as observations in `decisions.md`.

## Scope

**In scope:**
- 6 test files (4 NEW, 2 EXTEND): drag handler, controller (extend), system
  tree characterization, system tree hazard (extend), planet report
  characterization, battle panels characterization.
- ~112 characterization tests total.

**Out of scope:**
- Production refactor of any panel.
- The `__init__` builder seam work (that is PROJ-329 territory).
- Bug fixes — bugs surfaced during characterization are recorded as
  observations and filed separately.

## Success Criteria

- Every behavior in `phase_1_checklist.md` has a passing test.
- Full sharded suite green: `python Tools/test_sharded/test_sharded.py`.
- `python Tools/lint_test_files.py` reports 0 violations on the new/extended
  files.
- One commit per file (drag handler lands first).

## Source Documents

- Master arc: `AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md`
  (PROJ-338 row).
- Reference shape: `Projects/active_projects/PROJ-329A/{plan,decisions,phase_1_checklist}.md`.
- Test fixtures: `tests/fixtures/` README.

## Verification Commands

```bash
# Focused per-file
pytest tests/unit/ui/panels/test_build_queue_drag_handler.py -v
pytest tests/unit/ui/panels/test_build_queue_controller.py -v
pytest tests/unit/ui/panels/test_system_tree_panel_characterization.py -v
pytest tests/unit/ui/panels/test_system_tree_panel_hazard.py -v
pytest tests/unit/ui/panels/test_planet_report_panel_characterization.py -v
pytest tests/unit/ui/test_battle_panels_characterization.py -v

# Lint
python Tools/lint_test_files.py tests/unit/ui/panels tests/unit/ui

# Full validation
python Tools/test_sharded/test_sharded.py
```

## Estimated Sessions

**4 sessions** (revised up from 3 per delegate-review CRIT-002). The
112-test target across 6 test files for 5 high-risk panels (drag handler
state machine + system tree expand/collapse + build queue controller's
PROJ-69/79/208 callback chains + planet report panel's facade-coupled
data aggregation + battle panels' rendering orchestration) implies
~28 tests/session at 4 sessions, in line with PROJ-337's measured ~27
tests/session rate. The original 3-session estimate implied ~37
tests/session — aggressive given the existing
`test_build_queue_controller.py` is already 1108 LOC for a single panel.

Breakdown:
- Session 1: Drag handler (pure state machine, ~28 tests).
- Session 2: System tree panel (719 LOC, ~22 tests).
- Session 3: Planet report panel + battle panels (~42 tests combined).
- Session 4: Build queue controller extension (~15 tests) + buffer for
  fixture-discovery surprises across the 5 panels.

If de-scoping is preferred over the +1 session, drop the
`test_system_tree_panel_hazard.py` extension and lower the drag-handler
target from ~28 → ~20 to land in 3 sessions / ~85 tests. The 4-session
budget here assumes full coverage is preferred per user priority order
(readability > maintainability > functionality > runtime).
