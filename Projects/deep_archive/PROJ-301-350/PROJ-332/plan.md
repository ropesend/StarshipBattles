# PROJ-332 — Turn engine characterization

**Branch:** `feat/03c-phase-aware-execution`
**Started:** 2026-05-04
**Source plan:** `AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md` (PROJ-332 row)
**Reference shape:** `Projects/active_projects/PROJ-329A/` (plan/decisions/checklist layout)

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Characterization tests for `turn_engine.py` (27 new tests across 7 files) | Pending | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Phase 1 (characterization).
**Next Action:** Write `test_turn_engine_init_precedence.py` (4 tests) to pin the kwarg-vs-config precedence and frozen-dict slot init.
**Blockers:** None. Four locally-constructed engines (Quality / Atmosphere / Water / PlanetModifierEffect) are a known testability limitation handled via `unittest.mock.patch` at the import site (see D-004).

## Overview

`game/strategy/engine/turn_engine.py` is 795 LOC and orchestrates 15 injectable engines plus 4 locally-constructed ones across a 100-tick × 14-phase loop and a 6-step end-of-turn block. Existing coverage in `tests/unit/strategy/turn_engine/` and `tests/unit/strategy/engine/test_turn_engine_*.py` totals ~53 tests but leaves real gaps:

- `__init__` config-vs-kwarg precedence is not pinned.
- 10 of 15 lazy properties have no idempotency or default-class assertions.
- `_time_phase` failure-path timing accumulation, `_NullBattleResolver.resolve_battle`, snapshot-capture failure swallowing, and the PROJ-320 `moved_fleet_ids` derivation are all untested.
- End-of-turn engine call order (organics → happiness → population → quality → atmosphere → water) is only partially pinned.

This project pins observed behavior. No production refactors. No new architectural proposals. The 4 locally-constructed engines are documented as a testability limitation and tested via `patch`, not refactored.

## Goals

- **Phase 1:** Add 27 characterization tests across 7 new test files in `tests/unit/strategy/turn_engine/` that pin the gaps enumerated in [manifest.md](manifest.md) and the surface inventory in [design.md](design.md). One commit per test file (D-006).

## Scope

**In:**
- 7 new test files under `tests/unit/strategy/turn_engine/` covering: init precedence, lazy-property defaults + idempotency, phase timing, snapshot integration, end-of-turn ordering, PROJ-320 movement diff, validation delegation.
- Reuse of existing `conftest.py` fixtures (`turn_engine`, `mock_empire`, `mock_galaxy`).
- Mocks via `MagicMock(spec=I*Engine)` for the 15 injectable engines.
- `unittest.mock.patch` at import site for the 4 locally-constructed engines.

**Out:**
- Any edit to `game/strategy/engine/turn_engine.py` (production code is out of scope per master-plan characterization discipline).
- Any edit to the 6 existing test files (they stay byte-identical).
- Refactoring the 4 locally-constructed engines to be injectable (documented as observation D-007, not a fix).
- Wrapping end-of-turn or Phase 1.8 phases in `_time_phase` (documented as D-007/D-008 observations).
- `tests/unit/strategy/engine/test_turn_engine_config.py` — covers `TurnEngineConfig` dataclass, not the engine itself.

## Success criteria

- 7 new test files exist under `tests/unit/strategy/turn_engine/`, each <500 LOC.
- All 27 new tests pass on a clean run.
- Existing 53 tests stay green and unmodified.
- `python Tools/lint_test_files.py` reports 0 violations.
- Each new test file is its own commit.
- `manifest.md` lists every gap → test mapping.

## Source documents

- [`game/strategy/engine/turn_engine.py`](../../../game/strategy/engine/turn_engine.py) — production surface (795 LOC).
- [`AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md`](../../../AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md) — PROJ-332 row + characterization discipline rules.
- [`tests/unit/strategy/turn_engine/conftest.py`](../../../tests/unit/strategy/turn_engine/conftest.py) — shared fixtures (`turn_engine`, `mock_empire`, `mock_galaxy`).
- Existing test files (inventoried, not edited): see [manifest.md](manifest.md).
- [`Projects/active_projects/PROJ-329A/plan.md`](../PROJ-329A/plan.md) — reference artefact shape.

## Verification

- `pytest tests/unit/strategy/turn_engine/ -x -q` — expect existing ~53 + 27 new = ~80 tests green.
- `pytest tests/unit/strategy/ -x -q` — full strategy slice green.
- `python Tools/test_sharded/test_sharded.py` — full sharded suite stays green (modulo pre-existing unrelated failures).
- `python Tools/lint_test_files.py` — 0 violations.
