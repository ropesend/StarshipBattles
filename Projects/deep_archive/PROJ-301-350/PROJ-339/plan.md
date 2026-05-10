# PROJ-339 — UI panels mid-risk characterization

**Branch:** TBD (after PROJ-338 merges per master arc sequencing)
**Started:** 2026-05-04 (planning artefacts only)
**Source plan:** `AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md`
**Predecessors:** PROJ-329A/B/C, PROJ-330, PROJ-331..338

## Quick Status

| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. UI panels characterization (single phase) | Pending | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State

**Last Updated:** 2026-05-04
**Active Phase:** Phase 1 (planning complete; execution pending PROJ-338 merge)
**Next Action:** After PROJ-338 lands, branch from main and start phase 1 checklist top-to-bottom.
**Blockers:** Sequenced behind PROJ-338 per master arc.

## Overview

This is the mid-risk panel batch from the test_coverage master arc. Six
`game/ui/panels/*.py` files compose most of the race-setup, design-workshop,
and empire-treasury surfaces. Five have meaningful test coverage already; one
(`design_stats_panel.py`) only tests its inner `StatRow` helper and leaves the
panel-level construction / build / update / needs_rebuild paths uncovered.

The work is pure characterization: pin observable behavior of the existing
implementations, add coverage for the gaps surfaced in the per-file analysis,
and make zero production-code changes. Bugs found during characterization get
filed as separate tickets, not patched in this project.

## Goals

- **Phase 1:** Add ~22-30 NEW characterization tests across the 6 panel test
  files. Top three behaviors per file (18 total) are guaranteed to land; the
  remaining ~12 are gap-fillers per the per-file analysis. No new test files —
  append to the 6 existing test modules.

## Scope

**In:**
- `game/ui/panels/race_summary_panel.py` (733 LOC) — ship-preview branches,
  callback gating, missing-preference edge.
- `game/ui/panels/design_stats_panel.py` (516 LOC) — biggest gap; panel
  construction, `_build_layout`, `needs_rebuild` diff, `update_stats` layer
  population, requirements rendering, collapse toggling.
- `game/ui/panels/modifier_impact_grid.py` (514 LOC) — consumed-stats filter,
  sig-digit precision tiers, neutral-color path, scroll gating.
- `game/ui/panels/race_identity_panel.py` (493 LOC) — dropdown empty handling,
  override detection on load.
- `game/ui/panels/race_environment_panel.py` (337 LOC) — preset-not-found
  path, points-display exception swallow.
- `game/ui/panels/empire_treasury_panel.py` (333 LOC) — icon-missing skip,
  `_format_value` rounding boundary.

**Out:**
- Production refactors of any panel file.
- New abstractions, new fixtures, new test modules.
- Bug fixes surfaced during characterization (file as separate tickets).
- `draw()`-output pixel comparisons for `modifier_impact_grid` (impractical;
  pin data preparation in `update()` and the formatting helpers instead).

## Success criteria

- ~22-30 NEW characterization tests landing in the 6 existing test files
  under `tests/unit/ui/panels/` and `tests/unit/ui/`.
- Each new test maps to a documented behavior in `phase_1_checklist.md`.
- Pre-existing ~93 panel tests remain green.
- Full sharded suite green: `python Tools/test_sharded/test_sharded.py`.
- 0 production-code changes (verify via `git diff --stat game/`).
- `python Tools/lint_test_files.py` reports 0 violations.

## Source documents

- `AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md` — master arc.
- Reference shape: `Projects/active_projects/PROJ-329A/{plan,decisions,phase_1_checklist}.md`.
- `tests/unit/ui/panels/test_design_stats_panel.py` — existing fixtures and
  pygame_gui mock pattern to reuse.
- `tests/unit/ui/test_race_summary_panel.py` — existing ship-preview mock pattern.
- `docs/02_PATTERNS.md` (Compositional / two-stage UIWindow context for
  panel hosts).

## Verification

- `pytest tests/unit/ui/panels/ tests/unit/ui/test_race_summary_panel.py tests/unit/ui/test_modifier_impact_grid.py tests/unit/ui/test_race_environment_panel.py -x -q`
- `python Tools/test_sharded/test_sharded.py` — full suite green.
- `python Tools/lint_test_files.py` — 0 violations.
- `git diff --stat game/` after Phase 1 — empty.

## Estimated sessions

~2 sessions. Most of the time is in `design_stats_panel.py` (8-10 new tests
against a real `UIScrollingContainer`) and `modifier_impact_grid.py` (4-6
new tests for consumed-stat filtering and sig-digit boundaries). The other
four files need only 2-3 corner-case tests each.
