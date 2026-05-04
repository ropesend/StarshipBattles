# PROJ-334 — Algorithmic correctness characterization

**Branch:** TBD (await arc sequencing per master plan)
**Started:** 2026-05-04
**Source plan:** `AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md` (Project 4 of 10-project test-coverage arc)
**Predecessors:** PROJ-329A/B/C + PROJ-330 must land first (per master plan §Sequencing).

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Coverage gap audit | Pending | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Characterization tests for gap-list | Pending | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Phase 0 (audit existing coverage before writing)
**Next Action:** Enumerate behaviors per file, intersect with existing tests, produce gap-list.
**Blockers:** PROJ-329A/B/C + PROJ-330 sequencing.

## Overview

Project 4 of the 10-project test-coverage arc. Targets two pure-algorithm
files in the strategy data layer where determinism feeds into save/load/replay
correctness:

- `game/strategy/data/pathfinding.py` (503 LOC) — A* interstellar routing,
  deep-space linedraw, hybrid path stitching, intercept calculation.
- `game/strategy/data/galaxy_system_generator.py` (354 LOC) — procedural
  generation of star systems, planets, storms, archetypes; dual-RNG seed
  derivation for determinism.

**Pre-existing coverage adjustment:** `pathfinding.py` already has 1209 LOC
of unit tests under `tests/unit/strategy/pathfinding/`. PROJ-334 starts with
a coverage gap audit (Phase 0) and only writes tests for unpinned behaviors.
Estimate revised from "12-20 per file" to "8-12 gap-fill tests for pathfinding,
12-16 fresh tests for galaxy_system_generator" — ~24-30 total.

## Goals

- **Phase 0:** Produce `findings/coverage_gap_audit.md` enumerating
  every public/module-level behavior of both files and marking each as
  Covered / Partial / Uncovered with reference to existing test class.
- **Phase 1:** Add new characterization tests covering only the Uncovered
  + Partial rows. Determinism tests for `generate_systems` get a single
  golden-hash test plus a "different seeds → different output" sanity test.

## Scope

**In:**
- New characterization tests for gap-list behaviors only.
- Determinism contract tests for `GalaxySystemGenerator.generate_systems`.
- Saturation / failure-counter behavior tests.
- Intercept-with-zero-speed and intercept-with-empty-target-path corner cases (verify if covered first).

**Out:**
- Production-side refactors. If a test reveals what looks like a bug
  (e.g. `current_sys` is reassigned twice in `find_path_interstellar`),
  document in `decisions.md` as observation, do not fix.
- Performance tests (note: `find_path_interstellar` calls
  `galaxy.get_system_by_name` which is O(n) — flagged in design.md but
  not load-tested).
- Re-organising the existing `tests/unit/strategy/pathfinding/` directory.
- Tests for transitive helpers (`_extract_chaser_info`, `_ChaserProxy`)
  unless gap audit proves they are unreachable from public-API tests.

## Success criteria

- `findings/coverage_gap_audit.md` lists every public symbol with coverage status.
- New tests live under `tests/unit/strategy/pathfinding/` (extend existing dir)
  and `tests/unit/strategy/data/test_galaxy_system_generator.py` (new file).
- Each new test asserts a specific behavior with a SPECIFIC name (no
  `test_works`, no `test_basic`).
- `GalaxySystemGenerator.generate_systems` has a golden-determinism test
  pinning a representative attribute (e.g. sorted system names + locations
  for seed=42, count=5, radius=2000) AND a different-seeds-differ test.
- Full sharded suite green; `python Tools/lint_test_files.py` 0 violations.

## Source documents

- Master plan: `AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md`
- Reference shape: `Projects/active_projects/PROJ-329A/`
- Existing coverage: `tests/unit/strategy/pathfinding/` (6 files)
- Existing partial coverage: `tests/unit/strategy/data/test_intrinsic_rng_determinism.py`

## Verification

- `pytest tests/unit/strategy/pathfinding/ -x -q` — all green pre + post.
- `pytest tests/unit/strategy/data/test_galaxy_system_generator.py -x -q` — new file green.
- `python Tools/test_sharded/test_sharded.py` — full suite green.
- `python Tools/lint_test_files.py` — 0 violations.
