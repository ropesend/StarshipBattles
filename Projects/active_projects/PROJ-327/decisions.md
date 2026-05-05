# PROJ-327: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | User direction: full unit test suite takes >2 minutes on a 12-core machine; this is a measured problem. PROJ-327 picks up all 9 PROJ-322 deferrals not addressed by PROJ-324. |
| 2026-05-04 | **D-001:** Project does NOT start until PROJ-326 reports Complete | Per user direction: "they can be deferred but when 326 is done I want to work on them." |
| 2026-05-04 | **D-002:** Phase 0 baseline measurement is mandatory before any change | Without baseline, deltas are unprovable. The user's "2-minute" pain is the input; quantified per-file/per-shard runtimes are the success metric. |
| 2026-05-04 | **D-003:** Phase 1 (`test_virtual_table.py` `@patch` sweep) is highest-leverage | 81 decorators × 17 tests = ~1.4 seconds in one file alone (~1ms per `@patch` setup/teardown). Plus all-tests overhead even when the patched dependency isn't observed. |
| 2026-05-04 | **D-004:** Phase 4 (`strategy_screen` 50-test refactor) is CONDITIONAL | Only execute if Phases 1-3 cumulative delta is insufficient. The OpenCode 322-review estimated this as a "multi-day production refactor" — not worth it if Phases 1-3 already hit the target. |
| 2026-05-04 | **D-005:** If Phase 4 estimate exceeds 3 LLM-paced sessions, stop and surface to user | Risk-mitigation against scope creep. A multi-day refactor that grows into a months-long effort should become its own scoped project, not balloon PROJ-327. |
| 2026-05-04 | **D-006:** Re-confirmation of PROJ-322 deferred items as deferred is a VALID outcome | Phase 3 (DUP-001 + HLP-001) may conclude that even with runtime context, the builder-pattern factory is still net complexity-positive. That outcome must be documented (closed with rationale), NOT silently dropped. The user directed: "I do not want the additional issues forgotten." Re-confirmation closure honors that. |
| 2026-05-04 | **D-007:** Pre-flight verification before each task | PROJ-322 deferrals are stale by the time PROJ-327 starts. Each task verifies the cited file still exists and the cited tests still exist before doing work. Obsolete tasks are marked obsolete (not silently skipped). |
| 2026-05-04 | **D-008:** Use `pytest-randomly` for Phase 2 cross-isolation testing if available | The `reset_mock()` autouse pattern (rejected by PROJ-322) is the obvious unblock for class-scoped fixtures with mutation. If used, surface the cross-isolation risk with `pytest-randomly` ordering tests. |
| 2026-05-04 | **D-009:** Run baseline measurement 3x and take the median | Sharded test runtime varies ±10% between runs. Single measurements are noise-dominated for the kinds of deltas this project will produce. |
| 2026-05-04 | **D-010:** Branch strategy: same as PROJ-324/325/326 unless those have merged to main first | If the 3 prior projects merge to main before PROJ-327 starts, branch off main. Otherwise continue on `feat/03c-phase-aware-execution`. |

## Lessons Learned (PROJ-327 Phase 5 close-out, 2026-05-04)

Future test-quality / test-runtime projects should reference this table when prioritizing techniques. Numbers are measured on this branch, this machine; treat magnitudes as ballpark rather than universal.

### Per-technique scorecard

**Reading the scorecard:** "Wall-clock delta" measures runtime impact only. "Code-quality impact" tracks readability/maintainability/coupling effects independent of runtime. The two columns can disagree — the highest-runtime win is not always the highest tech-debt win, and vice versa. Per user priority order (readability > maintainability > functionality > runtime), Code-quality impact is the load-bearing column for prioritization decisions; Wall-clock delta is the bonus.

| Technique | Where applied | Wall-clock delta | Code-quality impact | LOC touched | Risk | Rework | Verdict |
|---|---|---:|---|---:|---|---|---|
| **`@patch` decorator → autouse fixture sweep** | Phase 1 `test_virtual_table.py` (80 of 81 patches collapsed) | ~~**~3.9 s** suite-level~~ (retracted per audit S2.7 — within noise envelope; only ~30 ms file-level is verifiable) | **High** — replaces 80 stacked decorators with one fixture; readability win at top of every test | ~700 LOC of test (mechanical) | **LOW** — no production change, mocks identical | None — outcome parity verified byte-identical | **BEST ROI per LOC for code quality.** ~~runtime win~~ retracted; the readability/maintainability win stands. Prefer this when ≥10 universally-applied `@patch` decorators sit on one class. |
| **Mutable-mock fixture rescope (function → module)** | Phase 2 `test_ship_io.py`, `test_empire_treasury_panel.py` | **~330 ms** single-process (lost in shard balancing at suite level) | **Low** — adds scope-justification comments; risk of cross-test leakage if audit misses a write | ~+50 LOC scope-justification comments; -10 LOC dead helper | **MEDIUM** — requires manual mutation audit; original deferral rationale was wrong (PROJ-322 claimed mutation existed; re-audit found zero attribute writes) | Significant pre-flight: every fixture re-audited grep-by-grep | **Worth it when audit confirms no mutation.** Skip when the audit finds writes — `reset_mock()` autouse companion adds cross-isolation surface that's worse than the runtime cost. |
| **Re-confirmation of deferral with measurement** | Phase 3 DUP-001 + HLP-001 | **0 s** | **Medium** — closes the deferral loop; future audits don't re-litigate from scratch | 0 production / ~80 LOC of measurement annotation in PROJ-322 checklists | **LOWEST** | None | **Always cheap, always valuable.** Future re-audits don't re-litigate; the disposition trail closes the loop. Per Decision D-006, this is a valid project outcome. |
| **Compositional Construction (Protocol + factory + Mock fixture)** | Phase 4 `StrategyScreen` + 101-test cluster | **~no measurable change** at runtime | **Highest in this scorecard** — eliminates the `patch.object(..., '__init__', lambda...)` anti-pattern wholesale; sub-object boundary becomes a typed seam; Mock fixture is reusable across the test cluster | +14 LOC production (`strategy_screen.py`); +119 LOC test fixture; +17 smoke tests; -18 LOC monkey-patch + 8 inline MagicMock assignments removed | **MEDIUM** — production seam needs careful thought (Protocol surface, default factory) | Needed audit of every `__init__` line to identify the sub-object boundary | **Highest tech-debt-per-LOC win** (note: tech-debt, not runtime — wall-clock delta is ~zero). Prefer this for new code (canonical) over `bypass_init` retrofit. |
| **Two-stage `__init__` + `Default{Foo}DelegateFactory` + `Null/Mock UiBuilder`** | (PROJ-325 + PROJ-328 A/B/C — sibling projects, applies same lesson) | (variable — measured per-class) | **High** — separates cheap-state init from expensive UI build; tests can construct without pygame; documented as Pattern §33 | per-class: ~+50–80 LOC production + ~+100 LOC test fixtures, -200 LOC of `__new__` bypass + manual wiring | **LOW** — production change is additive (factory default preserves behaviour) | None for the recipe; high for first application (PROJ-325 PoC) | **Canonical retrofit recipe.** Once PoC landed, rolling to other UIWindow subclasses was mechanical. Use this when a UIWindow subclass cannot easily move to Compositional Construction up front. |
| **Production `bypass_init` flag alone** | PROJ-324 Phase 1 (no test migration on its own) | 0 | **None on its own** — provides a seam but adds a guard branch to production with no test-side payoff until paired with two-stage refactor | 1 line per class (5 classes) | LOW | Major — the systemic finding (commit 9e177edb7) showed the flag alone delivers 0 LOC test reduction unless paired with a two-stage refactor | **Necessary but not sufficient.** A foundation; never deploy without immediately following with the two-stage `__init__` refactor in the same project (or accept the flag as production-only with no test-side payoff). |

### Key insight: runtime is bimodal

The runtime cost of the test suite is **bimodal**:

- **The "many small tests" mode** (PROJ-322's deferral targets — fixture overhead, `@patch` decorator overhead, mock construction): contributes ~5–8 s total to the slowest shard. PROJ-327 attacked this mode and reclaimed most of it.
- **The "few heavy tests" mode** (integration tests, parametrized validation clusters, `test_game_instantiation`): contributes the rest of the runtime — and dwarfs the deferral cluster by an order of magnitude.

A project scoped only to the deferral list (PROJ-327) cannot hit a < 90 s target. Future projects targeting the heavy cluster need their own Phase 0 scoping pass and should NOT inherit PROJ-322's deferral list as their input.

### Process lesson: always measure before re-scoping

PROJ-322 Task 2.19's deferral rationale ("many tests mutate the mock ship") was wrong on re-audit — zero attribute writes existed across 54 tests. The runtime reclaim came from a path the deferral didn't anticipate. Future deferral re-audits should:

1. Grep for the cited problem before believing the deferral note.
2. Microbenchmark the cited cost before believing the cited magnitude.
3. Treat any deferral note older than 6 months as a hypothesis to test, not a fact.

### Anti-pattern surfaced

The `patch.object(Cls, '__init__', lambda *args, **kwargs: None)` monkey-patch (used in `test_strategy_screen.py` pre-Phase-4) is **strictly worse than `__new__` bypass-init**: it leaks across tests in the same module if the patch is module-scoped, and it papers over real `__init__` bugs because the test never runs the real constructor. Compositional Construction (Pattern #32) is the canonical replacement; `__new__` bypass-init via the `make_ui_widget` factory (Pattern #33) is the retrofit replacement.
