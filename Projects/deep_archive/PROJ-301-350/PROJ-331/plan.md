# PROJ-331 — Combat / save-load characterization

**Branch:** TBD (created from `main` after PROJ-329A/B/C + PROJ-330 land)
**Started:** TBD (gated; see master plan)
**Source plan:** `AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md` (Tier 1 / PROJ-331)
**Predecessors:** PROJ-329A/B/C + PROJ-330 must land first.

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Characterization tests for battle_state.py gaps | Pending | [phase_1_checklist.md](phase_1_checklist.md) §1 |
| 2. Characterization tests for battle_controller.py gaps | Pending | [phase_1_checklist.md](phase_1_checklist.md) §2 |
| 3. Characterization tests for conflict_resolution_engine.py gaps | Pending | [phase_1_checklist.md](phase_1_checklist.md) §3 |

## Current State
**Last Updated:** 2026-05-04 (planning only)
**Active Phase:** Planning complete; awaiting predecessor projects.
**Next Action:** None until PROJ-329A/B/C + PROJ-330 land.
**Blockers:** Sequencing — see master plan.

## Overview

Tier 1 of the test-coverage arc. The three in-scope files together carry CRITICAL risk because they are the surfaces through which battles are saved, restored, and dispatched from the strategy layer. A regression in any of them silently corrupts player saves or dispatches the wrong battle.

Audit reality check (executed during planning, recorded in `decisions.md` D-001): all three files already carry meaningful coverage. PROJ-331 is a **gap-closure** project, not a "pin from zero" project.

Per master plan testing philosophy:
- Characterization-style; pin observable current behavior.
- TDD does NOT apply (production code already exists).
- Don't fix bugs found; document in `decisions.md` and pin the actual behavior.
- Don't propose architectural changes; surface unavoidable refactors in `decisions.md`.

## Goals

- **Phase 1 (`battle_state.py`):** Pin `to_ship`/`from_ship`/`from_component`/`from_projectile`/`to_projectile`/`capture_from_engine` and the 7 query methods. ~16 new tests in a new file `tests/unit/simulation/test_battle_state_live_object_bridges.py` (existing serialization-test file is 1395 LOC and at the soft 500-LOC ceiling already; new file keeps boundaries clean).

- **Phase 2 (`battle_controller.py`):** Close gaps in `start_from_spec`, `load_state` projectile path, `_require_registries_for_state_restore`, partial-failure behavior in `add_ships_from_state`, and `_extract_outcome_on_battle_end` replay-id capture. ~12 new tests added to `tests/unit/simulation/battle_controller/test_state.py` (state-related) and a new `tests/unit/simulation/battle_controller/test_start_from_spec.py` (the unified entry point).

- **Phase 3 (`conflict_resolution_engine.py`):** Pin `_validate_tick_inputs`, `_log_combat_result` storm-name extraction, `_lookup_environmental_effects` paths, `_collect_team_modifiers` exception path, `resolve_all_conflicts` with `tick=None`, multi-fleet-per-empire ordering, `replay_unavailable_reason` plumbing. ~13 new tests in a new file `tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py` (existing files cover different concerns; new file keeps separation clean).

## Scope

**In:**
- 3 production files (read-only references): `battle_state.py`, `battle_controller.py`, `conflict_resolution_engine.py`.
- ~41 new characterization test functions across 3 new test files + edits to 1 existing test file.
- Test fixtures: reuse existing `tests/fixtures/strategy_entities.py` and `tests/unit/simulation/battle_controller/conftest.py` where shape matches; create per-test synthetic state inline otherwise.
- All tests mock at boundaries (Ship, Projectile, BattleEngine, IBattleResolver, Galaxy) — no real pygame, no real save files, no real LLM calls.

**Out:**
- Refactoring any production file (master plan rule).
- Adding new features.
- Tests for files outside the 3-file scope.
- Live-engine integration tests (those already exist under `tests/integration/`).
- AI/LLM/UI surfaces.

## Success criteria

- All ~41 new test functions land green (modulo the pre-existing failures the master plan documents).
- For each of the 3 in-scope files: gap inventory (in `manifest.md`) maps 1:1 to a checklist item in `phase_1_checklist.md`. Zero items dropped silently.
- One characterization test file per production-file scope where boundary stays clean (3 new files + 1 file edit, see `manifest.md`).
- `python Tools/lint_test_files.py` reports 0 violations.
- Per-class commit discipline: each new test file lands in its own commit.
- `python Tools/test_sharded/test_sharded.py` green at end.

## Source documents

- [`AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md`](../../../AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md) — testing philosophy
- [`docs/02_PATTERNS.md`](../../../docs/02_PATTERNS.md) — fixture patterns
- [`docs/03_CONVENTIONS.md`](../../../docs/03_CONVENTIONS.md) §2.4 (LOC ceiling)
- [`game/simulation/battle_state.py`](../../../game/simulation/battle_state.py) — primary in-scope file 1
- [`game/simulation/battle_controller.py`](../../../game/simulation/battle_controller.py) — primary in-scope file 2
- [`game/strategy/engine/conflict_resolution_engine.py`](../../../game/strategy/engine/conflict_resolution_engine.py) — primary in-scope file 3

## Verification

- `pytest tests/unit/simulation/test_battle_state_live_object_bridges.py -x -v` — new Phase 1 tests
- `pytest tests/unit/simulation/battle_controller/test_state.py tests/unit/simulation/battle_controller/test_start_from_spec.py -x -v` — Phase 2
- `pytest tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py -x -v` — Phase 3
- `python Tools/test_sharded/test_sharded.py` — full suite green at end
- `python Tools/lint_test_files.py` — 0 violations

## Estimated effort

~3 sessions (per master plan). Phases 1, 2, 3 sequential; each ~1 session.
