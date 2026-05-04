# PROJ-327: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source

- User direction: full unit test suite takes >2 minutes on a 12-core machine; this is a measured problem worth opportunistic-scope work.
- All 9 deferred PROJ-322 items not closed by PROJ-324
- OpenCode 322-review: `Reviews/results/2026-05-04_015938_consistency_proj-322-p1-brittle-bloated-test-remediation-compl_req-req_20260504_015935_7d4449/report.md` — per-deferral analysis
- Continuation plan: [`AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md`](AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md)

## Why this project exists

PROJ-322's OpenCode review explicitly recommended NOT pursuing 9 deferred items in P1 polish scope, with one specific carve-out: *"defer until test runtime is measured to be a problem."* The user has confirmed test runtime IS a measured problem (>2 minutes on a 12-core machine for unit tests). This project addresses those 9 items, with measurement bracketing the work to verify the deltas are real.

The user also directed: *"I do not want the additional issues forgotten, they can be deferred but when 326 is done I want to work on them."* PROJ-327 is the explicit owner of all 9 items so the audit trail is intact and no one drops them.

## Phase 0 — Baseline measurement

Before changing any test, capture:

1. **Sharded suite wall-clock.** `time python Tools/test_sharded/test_sharded.py` — capture user/sys/wall.
2. **Per-shard runtime.** Sharded runner already produces per-shard times; capture the JSON.
3. **20 slowest test files.** `pytest tests/ --durations=20 --no-header` (single-process).
4. **20 slowest individual tests.** Same with `--durations=20 --durations-min=1.0`.

Save all four to `Projects/active_projects/PROJ-327/findings/baseline_<date>.md`. Repeat after each phase to capture incremental delta.

**Success metric:** the user has not specified an explicit target. Surface the baseline and ask the user what target to aim for. Reasonable: ≤90 seconds (50% reduction) on the same 12-core machine. Realistically Phases 1-2 alone may not hit that — Phase 4 (strategy_screen refactor) becomes load-bearing if so.

## Phase 1 — `test_virtual_table.py` `@patch` sweep

### Why this is high-leverage

PROJ-322 deferral annotation: *"81 @patch decorators across 17 tests."* Each `@patch` adds ~1ms of setup/teardown overhead per test invocation (start/stop the patch context). 81 × 17 × ~1ms = ~1.4 seconds in *one file alone*. Plus the patches run on every test even when most don't observe the patched dependency.

### Approach

1. Read the file. Identify which patches are universal (apply to all tests) vs. test-specific.
2. Universal patches → single `autouse=True` fixture at module scope.
3. Test-specific patches → either keep as `@patch` decorator (if 1-2 tests) or migrate to a fixture used by those tests explicitly.
4. Verify: the same set of mocks is in scope for each test. NO test should silently lose a patch.
5. Re-run the file: `pytest tests/unit/ui/components/test_virtual_table.py --durations=20`. Compare to baseline.

### Risks

1. **Regression risk.** 81 decorators × 17 tests is a lot of patch contexts to migrate without breaking. Each test must end up with the same patches applied — verify by running the file before AND after with `pytest -v` and diffing test outcomes.
2. **Patch-order sensitivity.** Some patches depend on each other's order (rare but possible). Audit each patch ordering before consolidating.

## Phase 2 — Mutable-mock fixture rescope

### Per-task strategy

For each of the 5 fixtures (PROJ-322 Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.15):

1. **Audit:** does any test in the file actually mutate the fixture? Search via `grep` + AST for attribute assignment on the fixture variable.
2. **No mutation found:** rescope to class/module/session. Cheap win.
3. **Mutation found, narrow:** wrap mutation in copy-on-write — return a deep copy from the fixture, mutate the copy. Or use `pytest.fixture(params=...)` for variants.
4. **Mutation found, broad:** keep function-scoped but identify the most-mutated attributes; pre-build a parametrized fixture that produces variants.

### `reset_mock()` autouse companion pattern (if used)

If a class-scoped fixture is rescoped but tests still need fresh mock state per test:

```python
@pytest.fixture(scope="class")
def mock_session():
    return MockSession()

@pytest.fixture(autouse=True)
def reset_mock_session(mock_session):
    mock_session.reset_mock()
    yield
```

This pattern was rejected by PROJ-322 because the OpenCode review found it "introduces test-isolation risk." If this project uses it, document the cross-isolation risk explicitly + add a regression test that runs the file with `--randomly-seed` to surface ordering bugs (`pytest-randomly` plugin if available).

## Phase 3 — DUP-001 + HLP-001 reconsideration

### What was rejected before

PROJ-322 + OpenCode 322-review both rejected pursuing these because:
- DUP-001: 5 handlers × 2 contracts = 10 distinct mock setups; a parametrize-based factory would become a switch statement and lose readability.
- HLP-001: 4 disparate `make_mock_*` shapes (20+ display params, cargo capacity, fuel-bearing planets, facade-specific mocks) — a kitchen-sink builder would be net complexity-positive.

### What changes with runtime context

For DUP-001, the runtime concern is per-test mock-session construction overhead. If each handler test constructs a fresh mock session, that's 5 × N (contracts) × thousands of test invocations. A shared session fixture (rescoped) might capture most of the win without the readability hit.

For HLP-001, the runtime concern is the construction cost of the `make_mock_ship` calls. With ~150 fleet-report tests each calling `make_mock_ship(...)` from scratch, a memoization layer (LRU cache keyed on the most-common parameter sets) could cut construction overhead.

### Phase 3 outcome possibilities

1. **Builder pattern still rejected.** Document the re-rejection with updated runtime context.
2. **Targeted fixture-rescope wins.** Even without a builder, share fixtures more aggressively where shapes align (continuing PROJ-322 Phase 6's approach).
3. **Memoization wins.** Wrap `make_mock_ship` in `functools.lru_cache` for common parameter sets.

## Phase 4 — strategy_screen refactor (CONDITIONAL)

### When this triggers

Only execute if the cumulative Phases 1-3 runtime delta is insufficient against the user's target. The OpenCode 322-review described this as a "multi-day production refactor" and recommended NOT doing it in P1 — but with measured runtime as the driver, the calculus changes.

### Approach (sketch — refine in Phase 4 design)

`strategy_screen` has 50 dependent tests + 8 sub-objects. Test brittleness comes from private-method patching the sub-object construction. Refactor:

1. Extract sub-object construction to a `StrategyScreenComposition` factory.
2. Production callers use the default factory.
3. Tests pass a `MockComposition` — no more private-method patching.
4. Migrate the 50 tests to use `MockComposition`.

This is the same pattern as PROJ-325 NO-GO RaceSetupScreen (PanelRegistry extraction). If both end up needed, document a shared "Compositional Construction" pattern in `docs/02_PATTERNS.md`.

### Phase 4 trigger criterion

Define explicitly in Phase 0 baseline: "If after Phases 1-3 the sharded suite wall-clock exceeds <user-set target>, execute Phase 4." Otherwise document the strategy_screen refactor as deferred to a future PROJ with this project's runtime baseline as evidence the deferral is sound.

## Phase 5 — Final measurement + documentation

- Re-run all baseline measurements from Phase 0.
- Document deltas in `findings/runtime_delta.md`.
- Update `docs/known-issues.md` to note the runtime improvement.
- Write a "lessons learned" note in `decisions.md` for future test-quality projects: which patterns yielded the biggest wins.

## Architecture

This project introduces NO new architectural patterns unless Phase 4 lands the `Composition` extraction (in which case document it). All other phases are mechanical refactor.

## Risks

1. **Stale deferred items.** PROJ-322 deferrals are ~weeks/months stale by the time PROJ-327 starts. Each task has a pre-flight verification step (test file still exists, cited tests still exist). If 30%+ are obsolete, the runtime delta from deferrals alone may be small — Phase 4 becomes more important.

2. **Regression risk in Phase 1.** The `test_virtual_table.py` file is the highest-risk migration. Use diff-based test outcome verification (run before, run after, compare exact pass/fail/skip lists).

3. **Phase 2 cross-test pollution.** Rescoping mutable mocks is the historical reason PROJ-322 deferred these. The `reset_mock()` autouse pattern has known fragility. Test thoroughly with `pytest-randomly` if available.

4. **Phase 4 scope creep.** A "multi-day refactor" can balloon. Set a hard time budget — if Phase 4 exceeds 3 LLM-paced sessions, stop and notify the user (don't let it become a months-long PROJ-32y).

5. **Measurement noise.** Sharded test runtime varies ±10% between runs. Run baseline 3 times, take the median. Same for post-phase measurements.

## Patterns That May Be Introduced

- **`reset_mock()` autouse companion** (Phase 2, if needed) — document with cross-isolation risk warning.
- **Memoized mock factory** (Phase 3, if used) — `functools.lru_cache` wrapper for common-parameter-set construction.
- **Compositional Construction** (Phase 4, if executed) — extract sub-object factory; default in production, mock in tests. Same shape as PROJ-325 PanelRegistry.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
