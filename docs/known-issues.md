# Known Issues

> Last Updated: 2026-05-04
> Sources: PROJ-321/322/323 execution logs (2026-05-03), worker pass-3 PROJ-322 disposition; PROJ-324/325/327/328 closeout (2026-05-04).

## Systemic Test Infrastructure Blockers

### **[RESOLVED in PROJ-324 + PROJ-325 PoC + PROJ-328]** UIWindow super-init chain blocker (historical)

**Affects:** ~7 APC-001 file rewrites in PROJ-322 Phase 5 (Tasks 5.6, 5.7, 5.10, 5.11, 5.12, 5.16, 5.29) plus several boundary-patching tasks in PROJ-322 Phase 3 (e.g., Task 3.x for `BuildQueueListWindow`).

**Symptom:** The `make_ui_widget(Cls, **kwargs)` factory at `tests/fixtures/ui_widget_factory.py` works for non-UIWindow widgets but cannot construct subclasses of `pygame_gui.elements.UIWindow` (or `StrategyModalWindow` which itself inherits UIWindow). The factory's element-class patches don't intercept `super().__init__()` calls because the MRO is resolved at class definition time.

**Affected production classes (incomplete list):**
- `FleetReportWindow` (extends StrategyModalWindow → UIWindow)
- `FleetReportWindow` multi-select variant
- `RaceSetupScreen`
- `NewGameSetupScreen`
- `OrdersWindow`, `BuildQueueScreen`, `TransferDialog`, `BuildQueueListWindow` (sub_window_hotkeys cluster)
- `StrategyModalWindow` itself

**Workaround in current code:** the legacy `__new__` bypass-init helper pattern remains in those test files. Each affected PROJ-322 task is marked `**DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):**` with concrete rationale.

**Unblocking paths (pick one):**
1. **Production-side change:** add a class-level `bypass_init=True` flag to `pygame_gui.elements.UIWindow` subclasses that, when set, skips the heavy `super().__init__()` chain. Allows the factory to construct via real `__init__` with a clean override path.
2. **Factory enhancement:** modify `tests/fixtures/ui_widget_factory.py` to intercept the `super().__init__()` call site (e.g., via `unittest.mock.patch.object` on the parent class's `__init__` BEFORE construction).
3. **Test approach change:** replace UIWindow unit tests with integration tests using a headless pygame_gui session (mirror the existing `tests/integration/ui/build_queue_screen/` pattern). PROJ-322 pass 1 already deleted `tests/unit/ui/screens/test_build_queue_screen.py` for this reason — its 7 integration tests at `tests/integration/ui/build_queue_screen/` cover the same flows.

**Effort estimate:** ~1 focused project (PROJ-32x) to either implement the bypass flag or enhance the factory.

#### Resolution (2026-05-04)

Option (a) — production-side `bypass_init` flag — was selected and implemented across three projects:

- **PROJ-324 Phase 1** (commit `9ae5c4959`): added the `bypass_init=True` early-return guard to `StrategyModalWindow.__init__` (covers `FleetReportWindow`, `OrdersWindow`, `TransferDialog`, `BuildQueueListWindow` transitively), plus `RaceSetupScreen` and `NewGameSetupScreen`. Added the `bypass_init(cls)` context manager to `tests/fixtures/ui_widget_factory.py` for safe per-test scoping.
- **PROJ-324 Phase 3 systemic finding** (commit `9e177edb7`): documented that the bypass guard alone does NOT deliver test-side LOC reduction — concrete subclasses do non-trivial post-`super()` work that crashes on `self.get_container()` etc. The fix is a two-stage `__init__` split.
- **PROJ-325 Phase 3 PoC** (RaceSetupScreen): proved the two-stage pattern. Cheap state + `DefaultRaceSetupDelegateFactory` + `RaceSetupUiBuilder` seam set BEFORE the bypass guard; heavy widget tree built AFTER. Tests substitute `NullRaceSetupUiBuilder` / `MockRaceSetupUiBuilder`.
- **PROJ-328 A/B/C** (2026-05-03): rolled the same recipe across `BuildQueueListWindow`, `OrdersWindow`, `FleetReportWindow`, `NewGameSetupScreen`, `TransferDialog`. Each subclass got a `Default{Foo}DelegateFactory` + `{Foo}Delegates` bundle and matching `Null{Foo}UiBuilder` / `Mock{Foo}UiBuilder` test fixtures.

**Canonical pattern** is now documented at `docs/02_PATTERNS.md` §33 ("UI Widget Test Factory") with a cross-reference to §32 ("Compositional Construction") which is the preferred pattern for new code.

---

### **[RESOLVED in PROJ-324 + PROJ-325 PoC + PROJ-328]** LLMBackgroundCall real-thread polling blocker (historical)

**Affects:** PROJ-322 Phase 4 Task 4.3 (`tests/unit/services/llm/test_background.py` polling sleep loops).

**Symptom:** `test_background.py` exercises real worker threads via `LLMBackgroundCall`. Polling sleep loops are deadlines waiting for those threads to complete actual work. Mocking `time.monotonic` only in the test loop would make the deadline expire immediately while the worker thread still sleeps — false failures.

**Workaround in current code:** the existing polling sleep pattern is preserved with no test changes; deadline values were not modified.

**Unblocking paths:**
1. **Production-side change:** refactor `game/services/llm/background.py` `LLMBackgroundCall` to expose a `threading.Event` that the test can wait on instead of polling.
2. **Coordinated mocked clock:** patch `time.monotonic` in BOTH the test thread AND the worker thread simultaneously. Requires careful ordering and may break other tests in the file.
3. **Replace polling with `result()` blocking call** (if the LLMBackgroundCall API exposes one).

**Effort estimate:** small production refactor (~1 day) or a substantial test-only patching workaround.

#### Resolution (2026-05-04)

Option 1 — production-side change with `threading.Event` — was implemented in **PROJ-324 Phase 2** (commit `af7328281`). `LLMBackgroundCall.__init__` now creates `self._done_event: threading.Event`; `_run()` sets the event after every terminal-state transition (DONE / ERROR / CANCELLED); a new public method `wait(timeout: float | None = None) -> bool` blocks until the event fires (returns `True` on terminal-state, `False` on timeout). The method is idempotent and safe to call before `start()`.

`tests/unit/services/llm/test_background.py` migrated 5–6 polling sleep loops to `assert call.wait(timeout=2.0)` — deterministic, no real-time deadlines, no `time.sleep(0.01)` polling.

The legacy `time.sleep(0.01)` polling-window flake on `test_elapsed_seconds_is_monotonic_then_frozen` (Windows ~1-in-3 flake — see project MEMORY notes) is unrelated to the polling-loop pattern; it is a timer-resolution issue in a separate test that the new `wait()` API does not touch.

---

### Shape-mismatch shared-factory blockers (DUP-001 + HLP-001)

**Affects:** PROJ-322 Phase 6 Tasks 6.1 (DUP-001) + 6.4 (HLP-001).

**Symptom:** the cited test helpers across files have meaningfully different shapes — collapsing them into a single shared factory either loses per-file expressiveness or grows into an unreadable kitchen-sink builder.

**Specifics:**
- DUP-001: superweapon execution-path tests vs DI-validation tests use different mock-session shapes per handler. A `@pytest.fixture(params=[(handler_cls, mock_session_factory_for_execution), (handler_cls, mock_session_factory_for_di_validation)])` would dispatch on parameter to set up either an execution or DI-validation mock; with 5+ handlers × 2 contracts = 10 distinct mock setups, the factory becomes a switch statement and readability is net negative.
- HLP-001: `make_mock_ship` cited in 4 files needs 20+ display-name params in `test_fleet_report_filters.py` but only cargo capacity in `test_fleet_cargo_resources.py`, etc.

**Workaround:** PROJ-322 pass 2 created the narrower shared factories where shapes did align (`cargo_mock_ship.py`, `yard_facility.py`, `mock_planet.py`). The disparate-shape helpers stay file-local.

**Unblocking paths:**
1. Builder-with-fluent-API pattern. Cost vs. benefit unclear without a focused exploration.
2. Accept the per-file expressiveness as a feature, not a bug. (Current disposition.)

#### Re-confirmation (PROJ-327 Phase 3, 2026-05-04)

PROJ-327 Phase 3 re-judged both items with fresh measurement evidence and **RE-CONFIRMED DEFERRED** under the new context:

- **DUP-001 (superweapon factory):** measured 1.73 s for 39 tests across 2 files; setup time IS dominant (~3.6 s sum) but the 5 handlers × 2 contracts still resolve to a switch-statement factory. Sharing the session between tests requires resetting `mock_fleet.orders`, `mock_fleet.path`, and call records on every test — equivalent cost to constructing a fresh fixture, with added cross-isolation risk. See `Projects/active_projects/PROJ-327/findings/phase_3_runtime_delta.md`.
- **HLP-001 (`make_mock_ship` 4-shape consolidation):** microbenchmarked at ~627 µs/call. Per-file overhead in `test_fleet_report_filters.py` is ~72 ms (~3.6% of file runtime). The 4 cited files have confirmed-distinct call shapes (cargo / fuel / display / facade) with no shared pattern to memoize. A blanket `make_mock_ship` would still be the kitchen-sink builder rejected by PROJ-322.

Future re-audits should check the runtime-delta document before re-litigating these — the disposition is closed with measurement evidence.

---

## Tool Bugs

### `Tools/test_sharded/test_sharded.py` `\a` escape bug in worktree paths

**Symptom:** Running `python Tools/test_sharded/test_sharded.py` from a git worktree at `.claude/worktrees/agent-XXXXXX/` (path starting with `agent-`) fails because the runner inline-templates `f"'--junitxml={xml_path}', "` and Python parses `\a` as the bell escape (`\x07`) when the `agent-` substring is in the path string. All 12 shards report FAILED but no actual test failures occur.

**Workaround:** Run `python -m pytest tests/` directly (no shard parallelism, but works from any path). The coordinator runs the sharded suite from the main repo root, where the path doesn't start with `agent-`.

**Fix needed:** in `Tools/test_sharded/test_sharded.py`, use `Path(xml_path).as_posix()` or `repr(xml_path)` to escape backslashes when interpolating the path into the inline runner script.

---

### `Projects/scripts/utils/markdown_parser.py` cp1252 em-dash crash

**Symptom:** `python Projects/scripts/project_status.py PROJ-XXX` crashes with `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x97` if any `phase_N_checklist.md` contains a Windows cp1252-encoded em-dash byte (`0x97` = `—` in cp1252) instead of the UTF-8 sequence (`0xE2 0x80 0x94`).

**Workaround / fix already applied:** PROJ-323 phase_4_checklist.md was fixed inline (commit `e3dfa0027`). Future occurrences can be fixed with:
```bash
python -c "
fp = '<path-to-file>'
raw = open(fp, 'rb').read()
fixed = raw.replace(b'\\x97', '\\xe2\\x80\\x94'.encode('latin-1'))
open(fp, 'wb').write(fixed)
"
```

**Fix needed:** `Projects/scripts/utils/markdown_parser.py` could call `read_text(encoding='utf-8', errors='replace')` for graceful handling, OR a pre-commit hook could normalize encoding.

---

## Test runtime improvements (PROJ-327)

PROJ-327 picked up the 9 PROJ-322 deferrals that touched test runtime. Final cumulative reclaim: **-3.9 s median wall-clock** (127.8 s → 123.9 s, median of 3 sharded runs; see `Projects/active_projects/PROJ-327/findings/runtime_delta.md` for the full per-phase breakdown). The 90 s stretch target was NOT hit; ~34 s of gap remains. The runtime lives in integration tests + the `test_component_definitions.py` 912-test validation cluster + `test_main_integration::test_game_instantiation` (~13 s alone), not in the PROJ-322 deferrals. PROJ-327's primary deliverable per user priority order (readability > maintainability > functionality > runtime) was disposition + rationale capture for the 9 deferrals, not raw runtime reduction.

**Techniques that yielded measurable wall-clock wins:**

- **`@patch` decorator → autouse fixture sweep (Phase 1, `test_virtual_table.py`):** 80 of 81 `@patch` decorators collapsed into one autouse class-scoped fixture. ~3.9 s suite-level reclaim (~3.0%). Lowest-risk technique — no production change, no cross-isolation surface. **Best ROI per LOC touched** for files with many universally-applied `@patch` decorators.
- **Mutable-mock fixture rescope (Phase 2, `test_ship_io.py` + `test_empire_treasury_panel.py`):** 2 of 5 candidates rescoped from function to module after re-audit confirmed zero attribute writes. ~330 ms single-process reclaim. Required careful manual mutation audit — wrong on the original PROJ-322 deferral rationale ("many tests mutate the mock ship" was inaccurate).
- **Compositional Construction (Phase 4, `StrategyScreen` + `test_strategy_screen.py`):** new `StrategyScreenComposition` Protocol + `MockStrategyScreenComposition` test fixture replaces an in-test `patch.object(StrategyScreen, '__init__', lambda...)` monkey-patch and 8 inline MagicMock assignments. ~no measurable runtime change (101 tests in cluster), but **eliminates the brittle private-method-patching pattern wholesale**. Highest tech-debt-per-LOC win; the new pattern is now `docs/02_PATTERNS.md` §32.

**Techniques re-confirmed deferred with measurement (Phase 3):**

- DUP-001 + HLP-001 — see "Shape-mismatch shared-factory blockers" above. Both have measurement evidence in the runtime delta document; future re-audits should not re-litigate without new context.

---

## UIWindow retrofit deferrals (PROJ-329A)

The PROJ-321..328 audit identified two classes that were swept into the
"un-refactored UIWindow subclass" tally but turned out to be out-of-scope
for the two-stage construction recipe (`docs/02_PATTERNS.md` §33). Both
are **deferred** with concrete rationale below so future audits don't
re-litigate them.

The full inventory of UIWindow / StrategyModalWindow subclasses (24
classes — 6 done, 16 in-scope across PROJ-329A/B/C, 2 deferred) lives at
`Projects/active_projects/PROJ-329A/findings/uiwindow_inventory.md`.

### `DesignWorkshopScreen` — NOT a UIWindow subclass (factory pattern)

**File:** `game/ui/screens/workshop_screen.py` (648 LOC)
**Class signature:** `class DesignWorkshopScreen:` — bare class, no parent.

**Why it was flagged:** PROJ-322 Task 5.10 listed `test_workshop_screen.py`
in the APC-001 cluster (`__new__` bypass-init pattern). The PROJ-321..328
audit grouped it with the UIWindow retrofit batch by name similarity.

**Why it's deferred:** `DesignWorkshopScreen` is not a `UIWindow` and not a
`StrategyModalWindow` — it's an `app.py`-managed screen constructed via
factory function (`get_workshop_screen()`). The two-stage `__init__`
recipe (cheap state → bypass guard → builder) doesn't apply. A retrofit
would need a separate factory-pattern project with its own design phase.

**Reassess if:** the workshop screen's failure mode becomes testability-
constrained AND the project owner wants to invest in factory-pattern
retrofitting (a different recipe than UIWindow's two-stage). Cross-ref
PROJ-322 `plan.md` Task 5.10 ACCEPTED-DEFERRED entry.

### `SettingsWindow` — raw `UIWindow`, no tests found

**File:** `game/ui/screens/settings_window.py` (109 LOC)
**Class signature:** `class SettingsWindow(UIWindow):` — raw
`pygame_gui.elements.UIWindow` subclass (does not extend
`StrategyModalWindow`).

**Why it's deferred:** No tests exist for `SettingsWindow` in the
`tests/` tree (verified via `find tests -name "*settings_window*"`,
empty result). The retrofit value of the two-stage pattern is
proportional to existing test coverage — refactoring untested
production code adds risk (no characterization tests to detect a
behavior change) without locking any behavior in place.

**Reassess if:** SettingsWindow gains characterization tests OR is shown
to be live-wired in production with active failure modes. The retrofit
itself is small (109 LOC, raw UIWindow — closer to the BuildQueueListWindow
shape than the FleetReportWindow shape) and would land in a follow-up
PROJ-329 batch alongside the new tests.

---

## See Also

- `Projects/active_projects/PROJ-322/plan.md` — Continuation Guide section for the active deferred work
- `Projects/active_projects/PROJ-322/phase_*.md` — per-task `**DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):**` annotations with concrete blocker rationale
- `Projects/active_projects/PROJ-329A/findings/uiwindow_inventory.md` — full UIWindow / StrategyModalWindow subclass inventory (status: 6 done, 16 in-scope, 2 deferred)
- `tests/fixtures/README.md` — usage of the new `make_ui_widget`, `cargo_mock_ship`, `yard_facility`, `mock_planet` factories
