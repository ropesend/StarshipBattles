# PROJ-377: PROJ-372 Phase 5 Leftovers — Golden-Save Fixture + Pathfinding Shim Sweep

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-377` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-377 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist | Depends on |
|-------|--------|-----------|------------|
| 1. Golden-save fixture (closes PROJ-372 review MAJ-001) | Complete | [phase_1_checklist.md](phase_1_checklist.md) | — |
| 2. Pathfinding shim migration sweep (closes PROJ-372 review MIN-002, partial) | Complete | [phase_2_checklist.md](phase_2_checklist.md) | Phase 1 (independent in code; serial for review continuity) |
| 3. Shim deletion or scope-rebound + AST guard | Complete | [phase_3_checklist.md](phase_3_checklist.md) | Phase 2 |

## Current State
**Last Updated:** 2026-05-07
**Active Phase:** All phases complete; ready for review.
**Last Action:** Phase 3 shipped — `tests/unit/strategy/data/test_pathfinding_shim_scope.py` AST guard pins the surviving 8 free functions + 2 helpers; `pathfinding.py` module docstring rewritten to reflect the post-PROJ-377 "permanent test-patch transparency surface" role; PROJ-372 `decisions.md` cross-link backfilled. Phase 3 also reverted Phase 2's site #3 (`superweapon_order_processor.py`) migration after the sharded run surfaced 40 regressions — tests patch the local module re-export, not the shim. Final migration count: 4 of 14 (sites #10, #11, #12, #14).
**Next Action:** OpenCode review + verifier subagent + closeout.
**Blockers:** None.

## Overview

PROJ-372 (Galaxy/Planet/Star god-class decomposition) closed Phase 5 without two deliverables its plan committed to:

1. **Golden-save fixture for the round-trip test.** `tests/integration/strategy/test_save_round_trip.py` (5 functions) is synthetic-only — every test builds a galaxy in-memory and asserts `to_dict → from_dict → to_dict` identity. No checked-in pre-decomposition save fixture is exercised, so a serialization mismatch introduced anywhere in the 8-project sequence (PROJ-368 → PROJ-372) could load existing user saves incorrectly without test failure.
2. **Pathfinding shim migration sweep.** PROJ-372 Phase 4 introduced `GalaxyPathfindingService` + `InterceptCalculator` and reduced `game/strategy/data/pathfinding.py` to 1-line forwarders. The Phase 5 plan ([phase_5_checklist.md](../PROJ-372/phase_5_checklist.md) Tasks 5.1-5.2) said to migrate all callers and delete the shim. Phase 5 closed without it; 14 production import sites and ~10 test patch sites still target the shim.

PROJ-377 closes both. Phase 1 captures a deterministic JSON snapshot from current `feat/03c-phase-aware-execution` HEAD, checks it into the test tree, and adds an idempotent reload assertion. Phase 2 migrates the shim callers that can move without breaking test-patch transparency. Phase 3 either deletes the shim (if Phase 2 reaches zero callers) or — more likely — re-bounds scope, keeps the shim explicitly as a permanent test-patch-transparency surface, and pins that decision in `decisions.md` + an AST-guard test.

The biggest design tension is **`unittest.mock.patch('game.strategy.data.pathfinding.X')`**. ~30 occurrences across ~10 test files patch the shim's free functions to mock pathfinding behavior. Removing the shim breaks every one of those patches. The migration target therefore must preserve a free-function surface OR migrate the tests in lockstep.

## Goals

- **G1.** A checked-in golden-save JSON fixture lives at `tests/fixtures/saves/galaxy_proj372_baseline.json`, captured deterministically from a known seed, with a test that asserts `Galaxy.from_dict(fixture).to_dict() == fixture` byte-for-byte (after a `_strip_storms` pre-pass equivalent to the synthetic test, until storm-serde drift is fixed in a separate ticket).
- **G2.** A second golden-fixture variant covers the high-coverage shape — multiple systems with planets, warp lanes, populated atmosphere, intrinsic abilities, owned planets — to catch field drift in serialization paths the empty / 1-system fixtures don't hit. Captured at `tests/fixtures/saves/galaxy_proj372_populated.json`.
- **G3.** Capture script lives at `tests/fixtures/saves/_capture_baseline.py` (NOT discovered as a test) so future re-captures are reproducible. Re-running it overwrites the JSON; CI verifies the JSON is unchanged from the committed copy via the round-trip identity test.
- **G4.** Of the 14 cited production shim importers, **migrate every site that can move without breaking a test patch** to call the service objects directly (`galaxy._pathfinder.X(...)`) — net target: at least 8 of 14 sites migrated; the precise list is locked at the start of Phase 2 after re-running the patch-site sweep.
- **G5.** The deferred sites (those with active `unittest.mock.patch('game.strategy.data.pathfinding.X')` usage) are **explicitly listed and justified in `decisions.md`**, not silently skipped. Each deferred site cites the test file/line that pins it.
- **G6.** A new AST-guard test at `tests/unit/strategy/data/test_pathfinding_shim_scope.py` asserts that the surviving shim free-function set is exactly the set Phase 3 freezes — preventing silent regrowth. (E.g., if Phase 2 migrates `find_path_interstellar` callers and removes its shim, the guard pins the absence.)
- **G7.** `pathfinding.py` either disappears (if Phase 3 can sweep tests too) or is renamed-in-docstring-only as the explicit "test-patch transparency surface" for the four functions test files actively patch (`find_hybrid_path`, `project_fleet_path`, `calculate_intercept_point`, `get_system_at_hex`); module docstring updated; PROJ-372 plan note marking the leftover as resolved.
- **G8.** `Galaxy._intercept` review remediation MIN-001 already landed (per PROJ-372 decisions row 2026-05-07). G8 is to confirm no new `galaxy._intercept` callers were re-added during Phase 2.
- **G9.** Save format unchanged. The golden fixture round-trips bit-identically through every Phase 2 caller-migration commit. (Phase 1 captures the fixture; subsequent phases assert it is preserved.)

## Scope

#### Phase 1 summary: Golden-save fixture (in)
- New JSON fixtures: `tests/fixtures/saves/galaxy_proj372_baseline.json`, `tests/fixtures/saves/galaxy_proj372_populated.json`.
- New capture script (NOT a pytest test): `tests/fixtures/saves/_capture_baseline.py`.
- New test functions in `tests/integration/strategy/test_save_round_trip.py` (extend existing file): `test_round_trip_golden_baseline_fixture`, `test_round_trip_golden_populated_fixture`.

#### Phase 2 summary: Shim migration sweep (in — by site)

The 14 production importers split into **safe to migrate** vs **defer (test-patched)** vs **stays in shim infrastructure**:

| # | File:line | Function | Test patches it? | Decision |
|---|-----------|----------|------------------|----------|
| 1 | `game/strategy/engine/game_session.py:321` | `find_hybrid_path`, `strip_start_hex` | YES — `test_command_handlers.py:84,310`, `turn_engine/test_basics.py:14,51` | **Defer** |
| 2 | `game/strategy/engine/game_session.py:340` | `project_fleet_path` | YES — `test_advanced_fleet_orders.py` repeatedly | **Defer** |
| 3 | `game/strategy/engine/superweapon_order_processor.py:31` | `get_system_at_hex` (~10 call sites in file) | NO direct patch on this caller; `test_strategy_superweapons.py:425` patches but exercises `strategy_superweapons.py` UI not this engine path | **Migrate** |
| 4 | `game/strategy/engine/handlers/base.py:20` | `find_hybrid_path`, `strip_start_hex` (used by `add_move_order_if_needed`) | YES — `test_command_handlers.py` patches `find_hybrid_path` and that helper is reached from a command handler | **Defer** |
| 5 | `game/strategy/services/fleet_navigation_service.py:36` | `find_hybrid_path`, `strip_start_hex` (top-level, used by `compute_path`) | YES — `test_edge_cases.py`, `test_hybrid_and_intercept.py` patch | **Defer** |
| 6 | `game/strategy/services/fleet_navigation_service.py:206` | `calculate_intercept_point` (lazy-imported inside `get_destination`) | YES — `test_advanced_fleet_orders.py:156`, `fleet_movement_engine/test_warp.py:36`, `turn_engine/test_tick_mechanics.py:80` | **Defer** |
| 7 | `game/strategy/services/intercept_calculator.py:121` | `_pf_shim.project_fleet_path` (intentional shim-route, see decisions.md) | YES (entire intercept calc is patched at the shim level) | **Stays** (shim infrastructure) |
| 8 | `game/strategy/services/intercept_calculator.py:169` | `_pf_shim.find_hybrid_path` (intentional shim-route) | YES | **Stays** (shim infrastructure) |
| 9 | `game/strategy/facade/slices/planet_slice.py:66` | `get_system_at_hex` (radius fallback) | YES — `tests/unit/strategy/facade/test_facade_robust_resolution.py:73,87` and `tests/unit/strategy/facade/slices/test_planet_slice.py:40-42` patches reach this site | **Class B (test-patched)**. Migration would require simultaneously rewriting `tests/unit/strategy/facade/test_facade_robust_resolution.py:73,87` and `tests/unit/strategy/facade/slices/test_planet_slice.py:40-42` patches. Defer per OQ-3 unless that scope expands. |
| 10 | `game/ui/screens/strategy_screen.py:436` | `find_hybrid_path` (`calculate_hybrid_path` method) | NO direct patch | **Migrate** |
| 11 | `game/ui/screens/strategy_screen.py:441` | `get_system_at_hex` (`_get_system_at_hex` method) | NO direct patch | **Migrate** |
| 12 | `game/ui/screens/strategy_screen.py:446` | `find_nearest_system` (`_find_nearest_system` method) | NO direct patch | **Migrate** |
| 13 | `game/ui/screens/strategy_superweapons.py:350` | `get_system_at_hex` | YES — `test_strategy_superweapons.py:425` patches `pathfinding.get_system_at_hex` | **Defer** |
| 14 | `game/ui/screens/strategy_colonization.py:258` | `get_system_at_hex` | NO direct patch | **Migrate** |

**Phase 2 baseline plan:** migrate sites 3, 10, 11, 12, 14 (5 sites). Verify site 9 in Task 2.1 — if `test_facade_robust_resolution.py` patches reach it, defer; otherwise migrate (target: 6 of 14). Sites 1, 2, 4, 5, 6, 13 deferred. Sites 7, 8 stay (shim infrastructure by design).

#### Phase 3 summary: Cleanup (in)
- New AST-guard test: `tests/unit/strategy/data/test_pathfinding_shim_scope.py` — asserts the surviving free-function set in `pathfinding.py` matches the Phase 2 final list.
- Update `pathfinding.py` module docstring: remove the "PROJ-376 follow-up" wording; replace with "Permanent test-patch surface; see PROJ-377 decisions.md".
- Update `Projects/active_projects/PROJ-372/decisions.md` 2026-05-07 row — mark MIN-002 closed; cross-link to PROJ-377.
- Update `docs/systems/strategy_layer.md` "Galaxy/Planet/Star Decomposition" section if it references the shim status.

### Out
- **Migrating production-and-test pairs together to direct service calls.** That work would migrate the 6 deferred production sites AND rewrite the patches in ~10 test files to patch via `mock.patch.object(galaxy._pathfinder, "find_hybrid_path", ...)`. Estimated ~30 patch rewrites; deferred to a future ticket once the test-patch convention is settled (see Open Question OQ-3 in design.md).
- **Renaming `IStockpileHolder` / `IStagingYardHolder`** (PROJ-372 review MIN-003 remediation already landed).
- **Moving `remove_warp_link` to `GalaxyWarpGenerator`** (PROJ-372 review MIN-004 remediation already landed via `decisions.md` row 2026-05-07).
- **`tectonic_activity` spelling change** (PROJ-372 review MAJ-003 was a hallucination — confirmed in PROJ-372 verifier_report.md and our own re-verification of `planet.py:68` + `planet_serde.py:44,102,151`).
- **Delete `pathfinding.py` outright.** Requires migrating ~10 test files to patch `IGalaxySystemGraph` methods via the service object instead of the shim — out of PROJ-377 scope unless the user requests it. PROJ-377 freezes the surviving shim surface and pins it via AST guard.
- **Performance regression bench updates.** PROJ-372 already updated `tests/performance/bench_galaxy_planet_star.py` and committed the baseline JSON. PROJ-377's caller migration changes only the import target, not the algorithm; no perf delta expected.

## Key Files

| Component | File Path | Type | Notes |
|-----------|-----------|------|-------|
| Existing round-trip test | `tests/integration/strategy/test_save_round_trip.py` | Test (extend) | Add 2 golden-fixture functions |
| Per-phase round-trip tests | `tests/integration/strategy/test_save_round_trip_phase{1,2,3,4}.py` | Test | **Read-only** — do NOT delete; PROJ-372 marked them "kept for now as boundary checks" |
| New baseline fixture | `tests/fixtures/saves/galaxy_proj372_baseline.json` | Fixture (NEW) | 5-system synthetic, no planets, with warp lanes |
| New populated fixture | `tests/fixtures/saves/galaxy_proj372_populated.json` | Fixture (NEW) | 10-system, planets, warp lanes, owned planets |
| New capture script | `tests/fixtures/saves/_capture_baseline.py` | Script (NEW) | Leading-underscore prevents pytest discovery |
| Shim file | `game/strategy/data/pathfinding.py` | Production (modify) | Update docstring; do NOT delete |
| Phase 2 migration target — service | `game/strategy/services/galaxy_pathfinding_service.py` | Production (read-only) | The migration destination |
| Phase 2 migration target — service | `game/strategy/services/intercept_calculator.py` | Production (read-only) | Sites 7, 8 stay shim-routed by design |
| Migrating site #3 | `game/strategy/engine/superweapon_order_processor.py` | Production (modify) | ~10 `get_system_at_hex` call sites in this file |
| Migrating site #9? | `game/strategy/facade/slices/planet_slice.py` | Production (verify-then-decide) | Phase 2 Task 2.1 |
| Migrating sites #10-12 | `game/ui/screens/strategy_screen.py` | Production (modify) | 3 import sites |
| Migrating site #14 | `game/ui/screens/strategy_colonization.py` | Production (modify) | 1 import site |
| Deferred sites | (see scope table) | Production (untouched) | 6 sites, justified in decisions.md |
| New AST guard | `tests/unit/strategy/data/test_pathfinding_shim_scope.py` | Test (NEW) | Pins surviving shim surface |
| Decisions log | `Projects/active_projects/PROJ-377/decisions.md` | Doc | Site-by-site rationale |
| PROJ-372 cross-link | `Projects/active_projects/PROJ-372/decisions.md` | Doc (modify) | Mark MAJ-001 + MIN-002 closed; cross-link |
| Strategy-layer doc | `docs/systems/strategy_layer.md` | Doc (modify if needed) | Pathfinding shim status, if mentioned |

## Related Documents

- [design.md](design.md) — site-by-site migration cost matrix, alternatives, risks, open questions
- [decisions.md](decisions.md) — pre-populated design decisions (fixture format, capture seeds, scope)
- [manifest.md](manifest.md) — file table grouped by phase
- [findings/initial_review.md](findings/initial_review.md) — site-by-site cost matrix + golden-fixture decision tree
- PROJ-372 plan + review:
  - `Projects/active_projects/PROJ-372/plan.md`
  - `Projects/active_projects/PROJ-372/decisions.md` (rows 2026-05-07)
  - `Projects/active_projects/PROJ-372/findings/initial_review.md`
  - `Projects/active_projects/PROJ-372/phase_5_checklist.md` Tasks 5.1, 5.2, 5.6
  - `Reviews/results/2026-05-07_020327_code_proj-372-galaxy-planet-star-god-class-decompositio_req-req_20260507_020326_6c1cc3/report.md` — MAJ-001, MIN-002
  - `Reviews/results/2026-05-07_020327_.../verifier_report.md` — confirmed verdicts
- Style/rigor reference: `Projects/archived_projects/PROJ-367/plan.md`

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/README.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, `docs/systems/strategy_layer.md`
- [ ] Read `Projects/protocols/01_initialize_project.md` and `Projects/protocols/03c_phase_aware_execution.md`
- [ ] Read PROJ-372 review report + verifier report (cited above) — focus on MAJ-001 and MIN-002
- [ ] Read PROJ-372 decisions.md rows for 2026-05-07 (MAJ-002, MIN-001, MIN-003, plan deviation acceptances)
- [ ] Read every line of `game/strategy/data/pathfinding.py` (104), `game/strategy/services/galaxy_pathfinding_service.py` (217), `game/strategy/services/intercept_calculator.py` (197), `tests/integration/strategy/test_save_round_trip.py` (99)
- [ ] Read this project's [findings/initial_review.md](findings/initial_review.md) for the site-by-site matrix
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` — pin baseline pass count in plan.md Current State

### After Each Phase
- [ ] Run targeted phase tests (per phase checklist's `Tests:` lines)
- [ ] Run `python Tools/test_sharded/test_sharded.py` — sharded suite green; pass count grows monotonically
- [ ] Update Current State in plan.md with handoff context for the next agent

### Final Verification (Phase 3)
- [ ] Sharded suite green; pass count ≥ baseline + 2 (the 2 new golden-fixture round-trip tests) + 1 (the AST guard) = baseline + 3
- [ ] Both golden fixtures committed and round-trip green
- [ ] All Phase 2 migrating sites no longer import from `pathfinding.py`
- [ ] All Phase 2 deferred sites still import from `pathfinding.py` (deliberate; pinned by AST guard)
- [ ] AST guard `test_pathfinding_shim_scope.py` asserts shim surface = exactly the deferred-site set + 2 shim-infrastructure functions (`_pathfinder_for`, `_intercept_for`)
- [ ] PROJ-372 `decisions.md` updated: MAJ-001 + MIN-002 closed; cross-link to PROJ-377 added
- [ ] `docs/systems/strategy_layer.md` references PROJ-377 if it mentions the shim status (if not — no change needed)

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All phase 1-3 checklists complete
- [ ] All tests passing (sharded suite green)
- [ ] Both golden fixtures pass round-trip
- [ ] AST shim-scope guard green
- [ ] PROJ-372 decisions.md cross-link backfilled
- [ ] Audit passed
- [ ] User verified
