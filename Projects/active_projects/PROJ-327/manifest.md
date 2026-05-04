# PROJ-327 File Manifest

> Generated during planning. Used by `/proj-parallel` for conflict detection.
> Updated if implementation discovers additional files.

## Phase 0 (baseline measurement)

| File | Type | Change |
|------|------|--------|
| `Projects/active_projects/PROJ-327/findings/baseline_<date>.md` (NEW) | Doc | Captured baseline runtimes (sharded, per-shard, per-file durations). |

## Phase 1 (test_virtual_table.py @patch sweep — PROJ-322 Task 3.14)

| File | Type | Change |
|------|------|--------|
| `tests/unit/ui/components/test_virtual_table.py` (verify path) | Test | 81 `@patch` decorators across 17 tests → autouse fixtures + selective per-test fixtures. ~700 LOC touched. |

## Phase 2 (mutable-mock fixture rescope — PROJ-322 Tasks 2.6, 2.11, 2.15, 2.19, 3.15)

| File | Type | PROJ-322 Task | Change |
|------|------|---------------|--------|
| `tests/unit/simulation/components/test_component_resource_manager.py` | Test | 2.6 | Rescope MagicMock-tree fixtures. |
| `tests/unit/ui/panels/test_empire_treasury_panel.py` | Test | 2.11 + 3.15 | Rescope autouse fixture; resolve private-attr read. |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | Test | 2.15 | `make_mock_ship` per-file optimization. |
| `tests/unit/simulation/test_ship_io.py` | Test | 2.19 | Ship fixtures with mutation — copy-on-write or reset_mock. |
| Other files surfaced by Phase 0 profiling | Test | (discovery) | Apply same patterns as the cited 5 files. |

## Phase 3 (DUP-001 + HLP-001 reconsideration — PROJ-322 Tasks 6.1 + 6.4)

| File | Type | PROJ-322 Task | Change |
|------|------|---------------|--------|
| Multiple superweapon execution / DI test files (identify in Phase 3 Task 3.1) | Test | 6.1 / DUP-001 | Re-judge builder-pattern factory; if rejected, document re-rejection. |
| `tests/unit/ui/screens/test_fleet_report_filters.py`, `test_fleet_cargo_resources.py`, `test_resupply_engine.py`, `test_strategy_session_facade.py` | Test | 6.4 / HLP-001 | Re-judge builder-pattern `make_mock_ship`; if rejected, consider memoization (`functools.lru_cache`). |
| `tests/fixtures/<new_factory>.py` (POTENTIALLY NEW) | Production (test infra) | 6.1 / 6.4 | Only if Phase 3 GO outcome — new shared factory. |

## Phase 4 (strategy_screen refactor — CONDITIONAL — PROJ-322 Task 3.25)

**Skip Phase 4 entirely if Phases 1-3 cumulative runtime delta meets target.**

| File | Type | PROJ-322 Task | Change |
|------|------|---------------|--------|
| `game/ui/screens/strategy_screen.py` (verify path) | Production | 3.25 | Extract sub-object construction to a `StrategyScreenComposition` factory. |
| `game/ui/screens/strategy_screen_composition.py` (POTENTIALLY NEW) | Production | 3.25 | Default Composition factory. |
| `tests/fixtures/strategy_screen_composition.py` (POTENTIALLY NEW) | Production (test infra) | 3.25 | MockComposition for tests. |
| `tests/unit/ui/screens/test_strategy_screen.py` (verify path) | Test | 3.25 | Migrate 50 tests to use MockComposition. |
| `docs/02_PATTERNS.md` | Doc | 3.25 | Document "Compositional Construction" pattern. |

## Phase 5 (final measurement + documentation)

| File | Type | Change |
|------|------|--------|
| `Projects/active_projects/PROJ-327/findings/runtime_delta.md` (NEW) | Doc | Before/after deltas across all phases. |
| `docs/known-issues.md` | Doc | Note runtime improvement; mark relevant tool bugs / blockers updated. |
| `Projects/active_projects/PROJ-322/plan.md` | Doc | Final Continuation Guide update — all 9 deferrals addressed (closed or re-confirmed). |

## Files explicitly NOT touched

These are owned by sibling continuation projects (which complete before PROJ-327 starts):

| File | Owner | Why excluded |
|------|-------|--------------|
| All PROJ-324 files | PROJ-324 | UIWindow + LLM blocker work + 14 deferred-migration files |
| All PROJ-325 files | PROJ-325 | PROJ-323 corrections + Tasks 3.34/3.37 + RaceSetupScreen |
| All PROJ-326 files | PROJ-326 | Linter + SystemTreePanel + facade contract |
