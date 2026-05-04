# Known Issues

> Last Updated: 2026-05-03
> Sources: PROJ-321/322/323 execution logs (2026-05-03), worker pass-3 PROJ-322 disposition

## Systemic Test Infrastructure Blockers

### UIWindow super-init chain blocker

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

---

### LLMBackgroundCall real-thread polling blocker

**Affects:** PROJ-322 Phase 4 Task 4.3 (`tests/unit/services/llm/test_background.py` polling sleep loops).

**Symptom:** `test_background.py` exercises real worker threads via `LLMBackgroundCall`. Polling sleep loops are deadlines waiting for those threads to complete actual work. Mocking `time.monotonic` only in the test loop would make the deadline expire immediately while the worker thread still sleeps — false failures.

**Workaround in current code:** the existing polling sleep pattern is preserved with no test changes; deadline values were not modified.

**Unblocking paths:**
1. **Production-side change:** refactor `game/services/llm/background.py` `LLMBackgroundCall` to expose a `threading.Event` that the test can wait on instead of polling.
2. **Coordinated mocked clock:** patch `time.monotonic` in BOTH the test thread AND the worker thread simultaneously. Requires careful ordering and may break other tests in the file.
3. **Replace polling with `result()` blocking call** (if the LLMBackgroundCall API exposes one).

**Effort estimate:** small production refactor (~1 day) or a substantial test-only patching workaround.

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

## See Also

- `Projects/active_projects/PROJ-322/plan.md` — Continuation Guide section for the active deferred work
- `Projects/active_projects/PROJ-322/phase_*.md` — per-task `**DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):**` annotations with concrete blocker rationale
- `tests/fixtures/README.md` — usage of the new `make_ui_widget`, `cargo_mock_ship`, `yard_facility`, `mock_planet` factories
