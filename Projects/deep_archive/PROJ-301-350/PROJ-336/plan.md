# PROJ-336 — Strategy services characterization

**Branch:** `feat/03c-phase-aware-execution` (continues the test-coverage arc)
**Started:** 2026-05-04
**Source plan:** `AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md` (row 6)
**Predecessors:** PROJ-329A/B/C + PROJ-330 must land first (per master sequencing).

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Per-file characterization tests | Pending | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Phase 1 (sole phase — characterization is single-pass)
**Next Action:** Read `decisions.md` for testing approach, then start with `fleet_cargo_projector` (smallest + zero coverage = fastest validation of fixture choices).
**Blockers:** Master plan sequencing — wait for PROJ-329A/B/C + PROJ-330.

## Overview

PROJ-336 adds characterization-style tests for the four strategy-service files
flagged MED risk in the test-coverage gap audit. Per master-plan testing
philosophy: **tests pin current behavior**, no production refactors, no bug
fixes. Apparent bugs land as observations in `decisions.md` for separate triage.

The four files are not equivalent in current coverage (see manifest):
- `fleet_navigation_service.py` already has substantial unit + integration
  coverage. Scope here is **gap-filling**, not full re-characterization.
- `system_destroyer.py` and `stabilizer_registry.py` have integration coverage
  only — adding unit tests pins their public APIs at the service boundary.
- `fleet_cargo_projector.py` has zero coverage.

## Goals

- **Phase 1:** Add one new test file per production file (4 files), each
  scoped per `phase_1_checklist.md`. Total ~30-40 new tests. Each file lands
  in its own commit.

## Scope

**In:**
- `tests/unit/strategy/services/test_fleet_navigation_gaps.py` (NEW) — gap-filler only
- `tests/unit/strategy/services/test_system_destroyer.py` (NEW)
- `tests/unit/strategy/services/test_fleet_cargo_projector.py` (NEW)
- `tests/unit/strategy/services/test_stabilizer_registry.py` (NEW)

**Out:**
- Refactoring any of the four production files (per master-plan philosophy).
- Modifying existing fleet_navigation tests in `tests/unit/strategy/fleet_navigation/`.
- The 3 existing integration tests covering these services (kept as-is).
- `action_time_resolver.py`, `strategic_ability_scanner.py`, or
  `cargo_transfer_service.py` — out of scope for this project.

## Success criteria

- 4 new test files, each compiles + passes locally.
- Total new tests: ~30-40 (estimate per checklist).
- `python Tools/lint_test_files.py` reports 0 violations.
- Full sharded suite green modulo pre-existing arc baselines.
- Any "looks like a bug" finding is recorded in `decisions.md` as an
  observation — no production change in this project.

## Source documents

- [`AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md`](../../../AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md)
- [`docs/systems/strategy_layer.md`](../../../docs/systems/strategy_layer.md) — stabilizer extensibility contract
- Existing reference tests:
  - `tests/integration/strategy/test_system_destruction.py`
  - `tests/integration/strategy/test_stabilizer_blocks_superweapon.py`
  - `tests/unit/strategy/fleet_navigation/` (5 files, do not modify)

## Verification

- `pytest tests/unit/strategy/services/ -x -q` — current baseline + new tests pass.
- `python Tools/test_sharded/test_sharded.py` — full suite green.
- `python Tools/lint_test_files.py` — 0 violations.

## Estimated sessions

**~1.5 sessions.** fleet_navigation gap-fill is the heaviest item (~5-7 tests
on facade-adjacent surfaces like `_resolve_warp_exit` and the projection guard
that need careful mocking); the other three files combined are roughly equal
to fleet_navigation's gap pass.
