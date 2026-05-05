# PROJ-341 — Strategy engine residual coverage

**Branch:** TBD (created from `main` after the PROJ-331..340 arc lands, or runs in parallel if those projects do not touch the same files)
**Started:** TBD
**Source plan:** `AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md` (residual gap addendum)
**Predecessors:** None hard. Logically follows the PROJ-331..340 arc; the gap audit + delegate review surfaced these three strategy-engine files as missed by the original arc.

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Green-field characterization for `environmental_hazard_engine.py` | Pending | [phase_1_checklist.md](phase_1_checklist.md) §1 |
| 2. Gap-fill characterization for `superweapon_order_processor.py` | Pending | [phase_1_checklist.md](phase_1_checklist.md) §2 |
| 3. Gap-fill characterization for `action_execution_engine.py` | Pending | [phase_1_checklist.md](phase_1_checklist.md) §3 |

## Current State
**Last Updated:** 2026-05-04 (planning only)
**Active Phase:** Planning complete.
**Next Action:** Begin Phase 1 — `environmental_hazard_engine.py` is green-field (zero existing tests) and is the highest leverage starting point.
**Blockers:** None.

## Overview

This is the residual-coverage addendum to the test-coverage arc PROJ-331..340. The original arc's audit + the delegate's post-review surfaced three `game/strategy/engine/` files that the arc missed:

| File | LOC | Existing tests | Density | Gap shape |
|---|---:|---:|---:|---|
| `game/strategy/engine/superweapon_order_processor.py` | 771 | 27 | ~28 LOC/test | Thin density (typical project density 10–15 LOC/test). Stabilizer-blocking, atmosphere seeding, fleet-cleanup, and several reject-paths under-pinned. |
| `game/strategy/engine/environmental_hazard_engine.py` | 219 | **0** | n/a | Green-field. Zero tests cover storm damage, fuel drain, multi-source aggregation, or the empty-fleet/None-location guards. |
| `game/strategy/engine/action_execution_engine.py` | 215 | 19 | ~11 LOC/test | Density acceptable but `_validate_tick_inputs` (PROJ-251), the BUILD-with-non-empty-queue branch boundary, and the `ActionTimeResolver`-injection constructor path are not pinned. |

Per master plan testing philosophy (carried forward from PROJ-331):
- Characterization-style; pin observable current behavior.
- TDD does NOT apply — production code already exists.
- Don't fix bugs found; record them in `decisions.md` as observation-only entries and pin the actual behavior.
- Don't propose architectural changes; surface unavoidable refactors only as documented blockers in `decisions.md`.

## Goals

- **Phase 1 (`environmental_hazard_engine.py`)** — green-field. Pin `process_environmental_tick` happy path (storm + fuel both apply), unhappy paths (no `get_system_at_location` on galaxy, system not found, empty effects, zero rates, no combat-capable ships, None fleet location -> `ValidationException`), and corner cases (multi-source aggregation, source-label fallback to "Unknown Hazard", per-tick scaling = `damage_per_turn / 100`, damage distributed evenly across combat ships, fuel drained per-ship not divided, ship destruction at HP <= 0). `_apply_damage_to_ship` and `_drain_fuel_from_ship` get unit-level pins. ~17 new tests in a new file `tests/unit/strategy/engine/test_environmental_hazard_engine.py`.

- **Phase 2 (`superweapon_order_processor.py`)** — gap-fill. The existing 27 tests cover ship-preservation, basic event logging, "no ability ship cancels order", enemy-colony cleanup, and Dyson-Sphere zone radius. Gaps to close: stabilizer-blocking cancellation paths for each of the 5 stabilizer-checking superweapons, OPEN_WARP_POINT far-end direction math (the `direction_q/dist` round() math at `superweapon_order_processor.py:380-384` is untested), CLOSE_WARP_POINT legacy-string-target back-compat path (lines 436-438), fleet-emptying cleanup (SG-003: `empire.remove_fleet` invoked when last ship consumed during STELLERATE/SELF_DESTRUCT), reference-planet resolution (`_get_reference_planet` returns first planet or None), Dyson-Sphere fallback atmosphere when `empire.race_config is None` (lines 609-613). ~16 new tests in a new file `tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py` (kept separate from the existing 1232-LOC test file to respect the LOC ceiling).

- **Phase 3 (`action_execution_engine.py`)** — gap-fill. The existing 19 tests pin tick interval, progress accumulation, completion, order-type filtering, fleet consumption, and the parametrized "all action order types are processed" sweep. Gaps to close: `_validate_tick_inputs` happy + unhappy (None fleet location -> `ValidationException`), the `ActionTimeResolver`-injection constructor path (currently the engine is always constructed without one in tests), confirming the order-popping responsibility lives with the order processor (not the engine), `_execute_action` kwarg threading (component_registry + all_empires forwarded verbatim), and the consumed-fleet iteration safety with multiple consumed fleets per empire. ~10 new tests added to a new file `tests/unit/strategy/engine/test_action_execution_engine_gaps.py`.

## Scope

**In:**
- 3 production files (read-only references), all in `game/strategy/engine/`.
- ~43 new characterization test functions across 3 new test files (one per in-scope file).
- Reuse of existing fixtures from `tests/unit/strategy/engine/test_superweapon_order_processor.py` and `tests/unit/strategy/engine/test_action_execution_engine.py` where shape matches; create per-test synthetic state inline otherwise.
- All tests mock at boundaries (Galaxy, StarSystem, Empire, Fleet, Ship, EventBus, `system_effects_collector`, `system_destroyer`, `SuperweaponValidator`) — no real pygame, no real save files, no real LLM calls.

**Out:**
- Refactoring any production file (master plan rule).
- Adding new features.
- Tests for files outside the 3-file scope.
- Live-engine integration tests.
- AI/LLM/UI surfaces.
- Re-pinning behavior already covered by the existing 27 + 19 tests.

## Success criteria

- All ~43 new test functions land green.
- Per-file gap inventory in `manifest.md` maps 1:1 to checklist items in `phase_1_checklist.md`. Zero items dropped silently.
- One characterization test file per in-scope file (3 new files; no edits to the existing test files — separate files keep boundaries clean and dodge the 500-LOC soft ceiling on the existing 1232-LOC superweapon test file).
- `python Tools/lint_test_files.py` reports 0 violations.
- Per-file commit discipline: each new test file lands in its own commit.
- `python Tools/test_sharded/test_sharded.py` green at end.

## Source documents

- [`AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md`](../../../AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md) — testing philosophy
- [`docs/02_PATTERNS.md`](../../../docs/02_PATTERNS.md) — fixture patterns
- [`docs/03_CONVENTIONS.md`](../../../docs/03_CONVENTIONS.md) §2.4 (LOC ceiling)
- [`game/strategy/engine/superweapon_order_processor.py`](../../../game/strategy/engine/superweapon_order_processor.py) — in-scope file 1
- [`game/strategy/engine/environmental_hazard_engine.py`](../../../game/strategy/engine/environmental_hazard_engine.py) — in-scope file 2
- [`game/strategy/engine/action_execution_engine.py`](../../../game/strategy/engine/action_execution_engine.py) — in-scope file 3

## Verification

- `pytest tests/unit/strategy/engine/test_environmental_hazard_engine.py -x -v` — Phase 1
- `pytest tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py -x -v` — Phase 2
- `pytest tests/unit/strategy/engine/test_action_execution_engine_gaps.py -x -v` — Phase 3
- `python Tools/test_sharded/test_sharded.py` — full suite green at end
- `python Tools/lint_test_files.py` — 0 violations

## Estimated effort

~1.5 sessions. Phase 1 is the largest (green-field, ~17 tests; ~0.7 session). Phase 2 (~16 tests, but mostly small variations on existing fixtures; ~0.5 session). Phase 3 (~10 tests; ~0.3 session).
