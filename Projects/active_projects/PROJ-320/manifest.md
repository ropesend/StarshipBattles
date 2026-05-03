# PROJ-320 File Manifest

> Generated during planning. Used by `/proj-parallel` for conflict detection.
> Update if implementation discovers additional files.

## Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/engine/conflict_resolution_engine.py` | Production | 3, 4 | Core change: multi-fleet-per-empire batching (Phase 3); per-fleet-tick triggering predicate `_should_trigger_combat_for_fleet` + `_resolve_conflicts` rewrite + delete legacy hex-map scan (Phase 4) |
| `game/strategy/engine/turn_engine.py` | Production | 4 | Compute `moved_fleet_ids` between Phase 3 and Phase 4; pass to `conflict_engine.resolve_all_conflicts` |
| `game/strategy/engine/order_processor.py` | Production | 2 | Bug fix: `_execute_fleet_merge` must call `FleetSpeedCalculator.update_fleet_speed(target_fleet)` after merging ships |
| `game/strategy/interfaces/engines.py` | Production | 4 | Extend `IConflictEngine.resolve_all_conflicts` signature with optional `moved_fleet_ids: Optional[set[int]] = None` |
| `tests/unit/strategy/engine/test_conflict_round_budget.py` | Test (NEW) | 1, 4 | Unit tests for `_should_trigger_combat_for_fleet` (Phase 1 red, Phase 4 green) — five cases: opportunity-tick + idle, opportunity-tick + action-order, opportunity-tick + leaving, non-opportunity tick, blocked-pathfind |
| `tests/integration/strategy/test_combat_round_budget.py` | Test (NEW) | 1, 3, 4 | Integration tests: sum-of-speeds round count (Phase 1 red, Phase 4 green); multi-fleet-per-empire participation (Phase 1 red, Phase 3 green); fleet-leaves-mid-turn count change (Phase 4 green); event payload includes all participating fleets (Phase 3 green) |
| `tests/unit/strategy/engine/test_order_processor_fleet_merge.py` | Test (NEW or extend) | 1, 2 | Unit test: post-merge target fleet speed equals min of merged-ship speeds (Phase 1 red, Phase 2 green) |
| `tests/integration/strategy/test_combat_shortcut_paths.py` | Test (modify) | 1, 4 | Phase 1: add `# PROJ-320` markers on assertions whose expected counts will change. Phase 4: update assertions to new round-budget semantics or delete tests of legacy per-tick behavior |
| `tests/integration/strategy/test_event_log_integration.py` | Test (modify) | 1, 4 | Same: marker in Phase 1, update in Phase 4 if any event-count assertions inside |
| `tests/unit/strategy/combat/test_strategy_spec_compiler.py` | Test (NEW or extend) | 3 | Verification: `build_strategy_battle_spec` groups multi-fleet-per-empire into one TeamSpec |
| `tests/performance/test_contested_hex_round_budget.py` | Test (NEW) | 5 | Performance regression gate: 5 contested hexes × 3 empires × 2 fleets, assert ≤150 battle invocations per turn (legacy: 500+); plus duplicate-of-Phase-1 stalemate count gate |
| `tests/unit/strategy/engine/test_fleet_speed_invariants.py` | Test (NEW, conditional) | 2 | Only created if Phase 2 Task 2.2 audit surfaces additional `Fleet.ships`-mutation sites missing the recalc — regression coverage for those fix sites |
| `docs/systems/strategy_layer.md` | Documentation | 6 | §3 "Per-Tick Phase Execution Order" Phase 4 row description updated with PROJ-320 triggering rule. `Last verified:` bumped |
| `docs/systems/combat_simulation.md` | Documentation | 6 | §9 "Performance follow-up (out of BUG-126 scope)" paragraph replaced with "PROJ-320 (closed)" closure note. `Last verified:` bumped |
| `docs/guides/testing_infrastructure.md` | Documentation | 5 | Note added under performance regression tests for `tests/performance/test_contested_hex_round_budget.py`. `Last verified:` bumped |
| `Projects/active_projects/PROJ-320/plan.md` | Project | All | Update Quick Status table + Current State as each phase closes |
| `Projects/active_projects/PROJ-320/decisions.md` | Project | All | Append rows for any in-flight decision discovered during implementation |
| `Projects/active_projects/PROJ-320/phase_*_checklist.md` | Project | All | Tick boxes; record file:line discoveries in Notes sections |

## Parallelism Notes

- **Phases 2, 3, and 4 modify overlapping files** (`conflict_resolution_engine.py`, `turn_engine.py`). They MUST run sequentially in a single worktree.
- **Phase 5 and Phase 6 can run in parallel after Phase 4** (Phase 5 is test/perf, Phase 6 is docs — no production-code overlap).
- **Phase 1 can be done in a dedicated TDD pre-commit** before any production work — no production files modified, only test files added/marked.
