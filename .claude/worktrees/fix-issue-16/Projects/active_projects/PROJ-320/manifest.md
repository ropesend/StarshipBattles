# PROJ-320 File Manifest

> Generated during planning, updated during implementation.
> Used by `/proj-parallel` for conflict detection.

## Production files

| File | Phase | Notes |
|------|-------|-------|
| `game/strategy/engine/conflict_resolution_engine.py` | 3, 4 | **Phase 3:** `_resolve_combat_at_hex` uses `Dict[int, List[Fleet]]`; `_collect_team_modifiers` rewritten for per-empire grouping. **Phase 4:** new `_should_trigger_combat_for_fleet(fleet, tick, moved_fleet_ids) -> bool` predicate; `resolve_all_conflicts` extended with `tick=` + `moved_fleet_ids=` kwargs (early-return on `tick is None`); `_resolve_conflicts` rewritten with per-fleet iteration in deterministic `(empire_id, fleet_id)` order, live liveness re-check, live contested-hex re-derivation per round; legacy hex-map scan deleted; module + `_resolve_combat_at_hex` docstrings updated. |
| `game/strategy/engine/turn_engine.py` | 4 | `_process_tick` snapshots fleet locations before Phase 3, diffs after Phase 3 to derive `moved_fleet_ids`, threads `tick=` + `moved_fleet_ids=` into the Phase-4 `conflict_engine.resolve_all_conflicts` call. |
| `game/strategy/interfaces/engines.py` | 4 | `IConflictEngine.resolve_all_conflicts` abstract signature extended with `*, tick: Optional[int] = None, moved_fleet_ids: Optional[set] = None` kwargs (backward-compat defaults). PROJ-320 docstring added. |
| `game/strategy/combat/spec_compiler.py` | 3 | `build_strategy_battle_spec` groups fleets by `owner_id` (was: one team per fleet). New `_team_spec_for_fleet_group(owner_fleets, ...)` replaces `_team_spec_for_fleet`. `_build_strategy_post_battle_hook` mirrors per-owner grouping. Insertion-order grouping for MagicMock-test compatibility. |
| `game/strategy/data/fleet.py` | 2 | NO production change shipped — Phase 2 audit confirmed `Fleet.merge_with` already calls `trigger_speed_recalculation`. The `Fleet.from_dict` no-recalc design choice was attempted then reverted (broke 19 round-trip tests); pinned by regression test instead. |
| `game/strategy/engine/order_processor.py` | 2 | NO production change. Audit confirmed `_execute_fleet_merge` already triggers speed recalc via `Fleet.merge_with` (line 459). |

## New test files

| File | Phase | Purpose |
|------|-------|---------|
| `tests/unit/strategy/engine/test_conflict_round_budget.py` | 1 | 5 unit tests for `_should_trigger_combat_for_fleet` — opportunity-tick + idle / action-order / leaving / non-opportunity / blocked-pathfind cases. All pass post-Phase-4. |
| `tests/integration/strategy/test_combat_round_budget.py` | 1, 3 | Integration tests via 100-tick `_NonDestructiveResolver` loop: sum-of-speeds round count, three-team stalemate, fleet-leaves-mid-turn count change, multi-fleet-per-empire participation, event payload includes all fleets. All pass post-Phase-4. |
| `tests/unit/strategy/engine/test_order_processor_fleet_merge.py` | 1 | Regression guard: `Fleet.merge_with` calls `target.trigger_speed_recalculation()`; `OrderProcessor._execute_fleet_merge` delegates to `Fleet.merge_with`. Both passed on Phase 1 (confirmed the suspected pre-existing bug doesn't exist). |
| `tests/unit/strategy/engine/test_fleet_speed_invariants.py` | 2 | Pins `Fleet.from_dict` no-recalc design choice (broke 19 round-trip tests when attempted; reverted). |
| `tests/performance/test_contested_hex_round_budget.py` | 5 | Performance regression gate: speed-5 vs speed-5 stalemate = 10 dispatches; 5-hex × 3-empire × 2-fleet ≤ 150 dispatches. |

## Modified test files

| File | Phase | Notes |
|------|-------|-------|
| `tests/unit/strategy/mocks/mock_engines.py` | 4 | `MockConflictEngine.resolve_all_conflicts` accepts and ignores the new kwargs (protocol parity). |
| `tests/unit/strategy/conflict_resolution/test_core.py` | 4 | 5 tests updated: fleets given `.id` + `.speed`; `_resolve_conflicts` calls pass `tick=20, moved_fleet_ids=set()`; `assert_called_once` loosened to `>= 1` for opportunity-tick coincidences. |
| `tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py` | 4 | `_fleet` helper given `speed=5` default; 4 `resolve_all_conflicts` callers updated; `fleets_destroyed` assertion loosened to set comparison. |
| `tests/unit/strategy/combat/test_spec_compiler.py` | 3 | Added `test_compiler_groups_multi_fleet_per_empire_into_one_team` — passes after the per-owner grouping change. |
| `tests/integration/strategy/test_three_empire_battle.py` | 4 | `_make_fleet` given `speed=5` default; 3 `resolve_all_conflicts` calls updated. PROJ-275 invariant re-asserted as "every dispatch is N-team". |
| `tests/integration/strategy/test_fleet_registration_lifecycle.py` | 4 | Single `resolve_all_conflicts` call updated to pass `tick=6, moved_fleet_ids=set()`. |
| `tests/integration/strategy/test_combat_shortcut_paths.py` | 1, 4 | Phase 1: PROJ-320 marker added. Phase 4: `TestReEngagementOnSubsequentTick` class DELETED with tombstone comment. |

## Documentation

| File | Phase | Notes |
|------|-------|-------|
| `docs/systems/strategy_layer.md` | 6 | §3 Phase-4-row description extended with PROJ-320 triggering rule. `Last verified:` bumped. |
| `docs/systems/combat_simulation.md` | 6 | §9 "Performance follow-up (out of BUG-126 scope)" replaced with "PROJ-320 (closed)" closure note. `Last verified:` bumped. |
| `docs/guides/testing_infrastructure.md` | 5 | Performance test row referenced new `test_contested_hex_round_budget.py`. `Last verified:` bumped. |

## Project files (mechanical updates throughout)

| File | Phase | Notes |
|------|-------|-------|
| `Projects/active_projects/PROJ-320/plan.md` | All | Quick Status table + Current State updated as each phase closes. |
| `Projects/active_projects/PROJ-320/decisions.md` | All | Locked-in decisions + the merge-non-bug correction (Phase 1 trust-but-verify lesson). |
| `Projects/active_projects/PROJ-320/phase_*_checklist.md` | All | All 6 phase checklists ticked + closure notes. |

## Parallelism Notes

- Phases 2, 3, and 4 modify overlapping files (`conflict_resolution_engine.py`, `turn_engine.py`); they MUST run sequentially.
- Phases 5 + 6 could in principle run in parallel after Phase 4 (perf test vs docs); in this session they ran sequentially in a single agent pass.
- Phase 1 (TDD scaffolding) is pre-production: no overlap with anything else.
