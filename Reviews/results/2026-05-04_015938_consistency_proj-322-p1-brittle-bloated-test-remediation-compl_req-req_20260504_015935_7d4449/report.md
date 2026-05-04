# PROJ-322 Completion Review — Consistency Report

**Request ID:** req_20260504_015935_7d4449
**Review Type:** consistency
**Completed:** 2026-05-04T02:15:00Z

---

## 1. Deferral Audit — Are the 25 genuine?

**Verdict: All 25 deferrals are substantively justified.** No deferral should be unblocked with creative workarounds within P1 scope. The blockers are real, documented, and the rationale is self-consistent across the 6 phase checklists, the plan.md Continuation Guide, and docs/known-issues.md.

### Deferral breakdown by root cause

| Root Cause | Count | Phase(s) | Task IDs |
|---|---|---|---|
| **UIWindow super-init chain (Systemic #1)** | ~14 | P3, P5 | 3.19, 3.20, 3.21, 3.24, 3.25, 3.26, 5.6, 5.7, 5.10, 5.11, 5.12, 5.16, 5.29 |
| **LLMBackgroundCall real-thread polling (Systemic #2)** | 1 | P4 | 4.3 |
| **Shape-mismatch factories (DUP-001, HLP-001)** | 2+3 | P2, P6 | 2.8, 2.9 (dep on HLP-001), 2.15 (dep on HLP-001), 6.1, 6.4 |
| **Mutable-mock fixture cautions** | 5 | P2 | 2.6, 2.11, 2.17 (dep on 5.11), 2.19, 3.14, 3.15 |

**Hot-take candidates reviewed and sustained as deferred:**

- **Task 3.15** (empire-treasury private-attr read): The test verifies internal element-tracking list cleanup after `refresh()`. With pygame_gui mocked, there is no observable side effect to assert other than the internal lists. Removing the private-attr read would *weaken* the test. Deferred rationale is sound.

- **Task 2.6** (component-resource-manager MagicMock tree): Deferred because mocks are heavily reassigned per-test. A `reset_mock()` autouse companion fixture was considered but rejected as introducing test-isolation risk. The construction cost is negligible (~3 MagicMock() per test). **Sound.**

- **Task 2.17** (race-setup-screen class-scope): Depends on Task 5.11, which depends on the UIWindow blocker. RaceSetupScreen has 8 deeply-nested constructor dependencies. Even with a class-scoped fixture, ~100 LOC of constructor wiring would still be needed. **Sound.**

- **Task 3.14** (virtual-table @patch decorators → autouse fixture): The file has 81 @patch decorators across 17 tests with substantive per-test mock manipulation. Converting to a fixture-based approach would touch ~700 LOC of test code with high regression risk. **Sound — worth its own sesssion if cycle-time benefit is measured.**

- **Task 3.25** (strategy-screen public surface): The task's own description says "big change; consider splitting into sub-PRs" with 50 dependent tests and 8 sub-objects. **Sound — genuinely a multi-day production refactor.**

### Audited actionable-but-deferred items (from Continuation Guide)

The plan.md lists 7 Phase 2 and 8 Phase 3 items as "actionable with cycle time." Verified per-task:

- **Phase 2 (2.6, 2.8, 2.9, 2.11, 2.15, 2.17, 2.19):** All sustained. The mutable-mock risk is real — the `reset_mock()` autouse pattern has caused intermittent failures in long-running parallel runs per the deferral notes. Savings are 10-100 LOC per file for fixtures that construct cheaply.

- **Phase 3 (3.14, 3.15, 3.19, 3.20, 3.21, 3.24, 3.25, 3.26):** 3.19/3.20/3.21/3.24/3.26 are all gated by the UIWindow blocker. 3.14 and 3.25 are genuinely large (700+ LOC risk). 3.15 is the private-attr issue analyzed above.

**No deferral is misclassified as blocking when a safe pass could land it.**

---

## 2. UIWindow Unblocking Path Recommendation

### Options from docs/known-issues.md

**(a) Production `bypass_init=True` flag** — Add a class-level flag to UIWindow subclasses that skips heavy `super().__init__()` chain.
**(b) Factory enhancement** — Intercept `super().__init__()` call site via `unittest.mock.patch.object` on parent class init BEFORE construction.
**(c) Integration-test replacement** — Replace UIWindow unit tests with integration tests using headless pygame_gui session, mirroring `tests/integration/ui/build_queue_screen/`.

### Analysis of the 7 affected files

| File | Class | Inherits | Option (c) Precedent? |
|---|---|---|---|
| `test_fleet_report_window.py` | FleetReportWindow | StrategyModalWindow→UIWindow | No integration tests exist |
| `test_fleet_report_window_multi_select.py` | FleetReportWindow | StrategyModalWindow→UIWindow | Same file, ~457 LOC |
| `test_race_setup_screen.py` | RaceSetupScreen | UIWindow directly | 1464 LOC, ~150 tests |
| `test_new_game_setup_extended.py` | NewGameSetupScreen | UIWindow directly | No integration tests exist |
| `test_sub_window_hotkeys.py` | OrdersWindow, BuildQueueScreen, TransferDialog, BuildQueueListWindow | All UIWindow or StrategyModalWindow | BuildQueueScreen has integration tests |
| `test_build_queue_list_window.py` | BuildQueueListWindow | UIWindow directly | No integration tests exist |

### Evaluation of each option

**Option (a) — `bypass_init=True` flag**

- **Effectiveness: High.** Every UIWindow subclass that adds `bypass_init = True` as a class attribute would let the factory construct it. The MRO problem is avoided because the *production* `__init__` would honor the flag by skipping the pygame_gui UIWindow constructor chain.
- **Cost: Medium.** Requires modifying 5+ production classes (FleetReportWindow, RaceSetupScreen, NewGameSetupScreen, BuildQueueListWindow, StrategyModalWindow). Each class's `__init__` needs an early-exit guard: `if getattr(self.__class__, 'bypass_init', False): return`. Tests would set `Cls.bypass_init = True` before calling `make_ui_widget(Cls)`.
- **Risk: Low.** The flag only affects test paths. Production code never sets it. The guard is `getattr(cls, ...)` with a default of `False`, so it's backwards-compatible.
- **LOC win:** ~7 files × ~100-200 LOC per file = ~700-1400 LOC of bypass-init wiring removed.

**Option (b) — Factory enhancement (metaclass / `__init_subclass__`)**

- **Effectiveness: Medium.** Python's MRO is resolved at class definition time. To intercept `super().__init__()` without touching production code, the factory would need to `patch.object(UIWindow, '__init__', ...)` *before* constructing the subclass instance. The tricky part: `pygame_gui.elements.UIWindow.__init__` might be a C function or heavily guarded. The factory already patches `UIWindow` in the `pygame_gui.elements` namespace (line 97 of `ui_widget_factory.py`), but that doesn't help because MRO resolution uses the original class object, not the patched namespace.
- **Cost: High.** May require `patch.object` on multiple parent classes up the MRO chain, potentially fragile across `pygame_gui` version changes. Not guaranteed to work.
- **Risk: Medium-High.** Coupling to pygame_gui internals. Fraught with Python MRO edge cases.

**Option (c) — Integration test replacement**

- **Effectiveness: Medium.** Only works for classes where integration test harnesses can exercise the needed test surface. The `build_queue_screen` precedent (7 integration tests covering 580 LOC of deleted unit tests) is encouraging, but:
  - `RaceSetupScreen` has ~150 unit tests covering MVVM delegates, tab navigation, race config creation, validation, LLM dialog, and slider event routing. Replicating these as integration tests would be massive and likely lower-fidelity than the current unit tests.
  - `FleetReportWindow` unit tests cover filtering, sorting, multi-select, close behavior, and edge cases. Integration tests could cover some of these but at much higher cost per coverage point.
  - `NewGameSetupScreen` is a simpler candidate for integration tests, but the volume of tests is unknown (file deleted upstream).

### Recommendation: **Option (a) — production `bypass_init` flag**

**Rationale:**
1. **Lowest risk.** The bypass flag is an opt-in escape hatch. It does not change behavior for production paths. The guard is a 1-line change per class.
2. **Highest coverage yield.** Unblocks all 7 APC-001 files *plus* the 5 Phase 3 boundary-patching tasks simultaneously.
3. **No dependency on external library internals.** Option (b) couples to pygame_gui's MRO and init internals. A pygame_gui upgrade could silently break it.
4. **Option (c) does not scale.** The `build_queue_screen` precedent worked because BuildQueueScreen was simpler and had a single focused test surface. RaceSetupScreen (1464 LOC test file, MVVM delegates, LLM integration) and FleetReportWindow (multi-select, filtering, sorting, close behavior edge cases) are much richer and would lose test fidelity in integration-only form.

**Suggested implementation shape:**
```python
# In each UIWindow subclass __init__:
if getattr(type(self), 'bypass_init', False):
    return
# ... normal pygame_gui super().__init__() ...
```

The `make_ui_widget` factory already patches all `pygame_gui.elements.UI*` classes, so the widget's own `_create_content` will run against mocks even without the pygame_gui super-init chain.

**Effort estimate:** ~1-2 days. 5-7 production-class changes + 7 test-file rewrites.

---

## 3. LLMBackgroundCall Thread Refactor Analysis

### Current implementation (`game/services/llm/background.py`)

The class is well-designed for production use with strong concurrency primitives:
- `threading.Lock` guards all mutable state (status, result, error, timestamps)
- `threading.Event` for cancellation
- Module-level concurrent-call accounting with `_in_flight_lock`
- Non-daemon workers tracked in `_active_workers` for `shutdown_all_calls()`

### The blocker: polling loops in tests

The test file (`tests/unit/services/llm/test_background.py`) uses real `time.sleep()` polling loops at 6-7 locations:
- Lines 128-130: `while call.status not in (DONE, ERROR) and time.monotonic() < deadline: time.sleep(0.01)`
- Lines 147-149: same pattern
- Lines 163-165: same
- Lines 181-184: same (cancel test)
- Lines 212-214: same (double-start test)
- Lines 270-273: same (concurrent-call test)

Each polling loop has a 2-second safety deadline and polls every 10ms. Under normal conditions, tests complete in ~50-100ms. Total runtime for the file is dominated by the slow provider tests (delay=0.5), not the polling loops.

### Production refactor invasiveness

**What the production code already has:**
- `threading.Event` (`_cancel_event`) — already present for cancellation
- Thread-safe state transitions with `_state_lock`
- `status`, `result`, `error`, `elapsed_seconds` properties — all thread-safe

**What it does NOT have:**
- A "completion event" that the main thread can wait on instead of polling `status`

**What would need to change:**
1. Add a `_done_event = threading.Event()` to `LLMBackgroundCall.__init__`
2. In `_run()`, set `self._done_event.set()` after any terminal state transition (DONE, ERROR, CANCELLED)
3. Add a `wait(timeout=None)` method that calls `self._done_event.wait(timeout)`
4. **Invasiveness: +4 lines in production code.** The existing locking structure is untouched — the event is set under the lock in `_run()`, and `wait()` reads it without a lock (standard Event semantics).

### Test surface that depends on current polling shape

**Directly depends on polling:** 5-6 tests (all tests that `call.start()` then `while call.status != DONE: time.sleep(0.01)`).

**Does NOT depend on polling:** The `TestConstructionAndValidation` class (3 tests, no start), `TestLockSafety` (uses threads directly), `TestShutdownAllCalls` (uses `shutdown_all_calls()`).

**What a test-side `wait()` would enable:** Replace all `while call.status != DONE: time.sleep(0.01)` with `call.wait(timeout=2.0)`. Tests become 1 line shorter and deterministic.

### Recommendation

**The production refactor is minimal (+4 lines). The test refactor is mechanical (swap polling loops for `call.wait()`).**

**Effort estimate:** ~1 hour. This is a "deceptively simple" refactor — the infrastructure for it already exists (the class already uses `threading.Event` for cancel, has proper locking, and separates terminal from transient states). The only missing piece is the completion signal.

**Note on freezegun:** The plan-review suggestion (M-005) recommended a mocked clock instead of an Event-based refactor. The mocked-clock approach was rejected in pass 3 because patching `time.monotonic` only in the test thread would cause false timeouts. The Event-based approach is actually *simpler* than the mocked clock and has been available since the class was designed with `threading.Event` for cancellation.

**This should not require its own PROJ. It is a small change that could be bundled with the UIWindow refactor project as a Phase 1 quick win.**

---

## 4. Completed Work Quality Spot-Check

### Phase 1 — CAT-4 Duplicate Testing (18/18 done)

**Task 1.14 (superweapon edge-cases):** -315 LOC. Verified against source — the 5 fleet-not-found tests were parametrized successfully. The remaining file structure (order-processor error cases consolidated, handler-level vs processor-level concerns separated) is well-organized.

**Task 1.9 (construction-queue parametrize):** -35 LOC. Planet/Fleet variants collapsed into a parametrized fixture-factory. Clean.

**Task 1.7 (battle-state-validation parametrize):** -50 LOC. 6 field-deletion tests collapsed to one parametrized test. Standard transformation, correctly applied.

**Verdict:** Phase 1 work is genuine consolidation, not complexity-shuffling.

### Phase 2 — CAT-5 Fixture Bloat (6 done)

**Task 2.10 (astrophysics loader):** -20 LOC, 5 identical per-class fixtures → 1 module-scoped. Clean.

**Task 2.20 (camera pygame.init):** -45 LOC, 8 per-class fixtures → 1 module-scoped. Solid win. The sdl_videodriver dummy is already set by repo conftest.

**Task 2.18 (save-selection tmpdir):** -20 LOC, 3 byte-identical fixtures → 1 module-level. Good.

**Verdict:** Small but real wins. The rescopes were applied where safe (read-only fixtures, no test mutation).

### Phase 3 — CAT-6 Mocking Brittleness (12 done)

**Task 3.3 (multi-selection autouse → fixture):** Converted autouse `setup` that set attributes on `self` to a value-returning `selection_setup` fixture. This eliminates parallel-run fragility. Genuine improvement.

**Task 3.9 (battle-engine init → engine.start()):** 4 tests rewritten to drive `engine.start([ship_a], [ship_b], ai_controllers=[])`. The tests now also assert on the second ship to prove parity. Real boundary improvement — eliminates private-method coupling.

**Task 3.12 (fleet-movement DI injection):** Stopped patching `fleet_navigation_service.find_hybrid_path`; injects `nav_service=fake_nav_service` via DI. The `FleetMovementEngine` constructor already accepted the parameter — this was just a test that was patching instead of injecting. Clean fix.

**Task 3.10 (build-order-processor documentation path):** Chose documentation over refactor. The docstring explains that BUILD auto-pop is owned by `ActionExecutionEngine.process_action_ticks` (post-tick sweep), not `execute_action_order` (per-order dispatcher). This is the right call — the alternative would test a code path the engine never takes.

**Task 3.17 (modifier-logic-service public API):** 5 tests rewritten from `_get_base_firing_arc()` to `get_initial_value('turret_mount', comp)`. The "no arc found" test now asserts the public fallback to `mod_def.min_val` instead of `None`, which is the observable behavior callers rely on. Genuine improvement.

**Verdict:** Phase 3 completed work shows good judgment. The boundary-patching changes are real semantic improvements — the tests now assert on observable behavior instead of internal call patterns.

### Phase 4 — CAT-7 Sleep/Latency (4 done)

**Task 4.2 (os.utime for component-derivatives):** Replaced `time.sleep(0.01)` with explicit `os.utime()` call. Deterministic and correct.

**Task 4.7 (os.utime for auto-save):** Same pattern. Clean.

**Verdict:** Simple, correct replacements. No complexity added.

### Phase 5 — APC Cluster Remediation (13 done)

**Task 5.0 (make_ui_widget factory):** ~230 LOC factory + ~125 LOC smoke tests. This is the single highest-value addition in the project. It introspects `__init__` signatures, patches `pygame_gui.elements.UI*` in both the qualified namespace and any module-bound imports (handles `from pygame_gui.elements import UILabel`), walks the MRO for base-class modules, and supports `extra_modules` for transitively-imported helpers.

**Task 5.1-5.5, 5.8-5.9, 5.13-5.14 (APC-001 factory migrations):** All 8 migrated files follow the same clean pattern: `__new__` bypass → module-scope helper that delegates to `make_ui_widget`. Net LOC reductions range from -25 (race_summary_panel) to -140 (design_report_panel). Tests pass. The migrations are genuine improvements because the factory calls real `__init__`, so `self.panel`, `self.ui_manager`, and all `_create_content`-assigned attributes are real (or mocked pygame_gui elements).

**Task 5.15 (build_queue_screen deletion):** Deleted 580-LOC unit file. The 7 integration tests under `tests/integration/ui/build_queue_screen/` already covered the surface. Correct judgment — no duplicate test coverage remains.

**Task 5.25 (APC-002 new-game-setup):** Replaced `inspect.signature()` + `inspect.getsource()` with a behavioral default test. Genuine improvement — the test now constructs the widget and observes the default value.

**Tasks 5.17-5.19, 5.20-5.24, 5.26 (APC-002 source-inspection):** Most were already removed or obviated by upstream PROJ-321 deletions or prior changes. The phase checklist accurately marks them as `satisfied` or `obsolete`.

**Verdict:** The factory infrastructure (Task 5.0) and the 8 APC-001 migrations are real quality improvements. The completed APC-002 and APC-003 work is also genuine — tests now exercise the production surface instead of inspecting source code or patching private methods.

### Phase 6 — DUP/HLP Consolidation (5 done)

**Task 6.2 (DUP-002 fleet-not-found parametrize):** Satisfied via Phase 1 tasks 1.13/1.14. Correct cross-phase coordination.

**Task 6.3 (DUP-003 cargo_mock_ship):** Created shared factory. One consumer migrated cleanly; the other (`test_resupply_engine.py`) uses a different fuel-API surface. Correctly identified the shape mismatch and left the fuel mock file-local. Good judgment.

**Task 6.5 (HLP-002 BattleRunner conftest):** Satisfied via Phase 1 task 1.5. `_make_ship_spec` and `_make_team` in `tests/unit/simulation/conftest.py`.

**Task 6.6 (HLP-003 yard_facility):** Created shared factory with `make_planetary_yard_facility` and `make_ship_with_yard`. Two of three target files migrated. The third (`test_space_yard.py`) was already module-scoped per Task 1.15. Correct.

**Task 6.7 (HLP-004 mock_planet):** Created shared factory. One target file migrated. The second has a fuel-storage-bearing mock (different surface). The third was already deleted upstream. Correctly handled the shape divergence.

**Verdict:** Phase 6 work shows measured judgment. The shared factories were created where shapes aligned; where they diverged, the existing per-file helpers were retained with documented rationale.

### Overall quality verdict

**The completed work represents genuine improvement, not complexity-shuffling.** The boundary-patching changes (Phases 3/5) actually make tests less brittle. The factory migrations (Phase 5) replace manual attribute wiring with real construction. The parametrizations (Phase 1) reduce duplication without obfuscation. The deferred items are correctly documented and genuinely blocked, not avoided.

---

## 5. `make_ui_widget` Factory Evaluation

### Current state

The factory at `tests/fixtures/ui_widget_factory.py` (279 LOC) is the single most impactful addition from PROJ-322. It:
- Patches all `pygame_gui.elements.UI*` classes in both the canonical namespace and any module that imported them via `from X import Y`
- Walks the target class's MRO to find all modules that need patching
- Introspects `__init__` signatures to supply defaults for known parameter names (`panel`, `manager`, `ui_manager`, `container`, `rect`)
- Supports `extra_modules` for transitively-imported helpers like `ModifierImpactGrid`
- Uses `unittest.mock.patch` context managers, guaranteeing cleanup on exception

### Rough edges

1. **Documentation gap:** The factory is not referenced in `docs/02_PATTERNS.md`. The design.md mentions it as an "Opportunity Discovered" but the canonical pattern reference has not been updated.

2. **`_default_rect()` conditional import:** Lines 121-126 try to import `pygame` inside a utility function. This works because `conftest.py` force-sets `SDL_VIDEODRIVER=dummy`, making `pygame` always importable. But if any test imports the factory before pygame is initialized, the fallback to `MagicMock` kicks in silently. A docstring note about the import ordering would help next-agent users.

3. **Known limitation (well-documented):** Cannot construct UIWindow subclasses. The factory's docstring and inline comments clearly explain why (MRO resolution at class definition time). This is NOT a factory design flaw — it's a fundamental Python limitation that requires the production-side bypass flag (see Section 2).

4. **No `theme` / `object_id` kwargs:** Some pygame_gui constructors accept `theme` and `object_id`. The factory's introspection-based defaulting doesn't know about these, so callers must pass them explicitly. This is fine for now but worth documenting as a "caller must pass" note.

5. **Element class list is static:** `_PYGAME_GUI_ELEMENT_NAMES` (lines 84-102) is a hardcoded tuple. If a new production widget uses a pygame_gui element not in this list, the factory will silently let it pass through to real construction (which may fail or require pygame display). This is the correct behavior (fail loud), but the maintainability concern is that new elements must be manually added. A comment noting "add new elements here when discovered" would help.

### Promotion recommendation

**The factory SHOULD be promoted to a canonical pattern in `docs/02_PATTERNS.md`** as Pattern #32 or as a subsection of Pattern #15 (Factory). It satisfies all criteria for canonical status:
- **Used by 2+ test files** (8 APC-001 migrations use it)
- **Has documented protocol** (module docstring covers required vs optional kwargs, provides an example)
- **Has test coverage** (5 smoke tests in `tests/fixtures/test_ui_widget_factory.py`)
- **Stateless** — no module-level mutable state
- **Reusable** — works for any class that constructs `pygame_gui.elements.UI*` widgets in its `__init__`

**Suggested pattern entry:**
> **15b. UI Widget Test Factory (PROJ-322)**
> **Where:** `tests/fixtures/ui_widget_factory.py` — `make_ui_widget(Cls, extra_modules=(), **kwargs)`
> **How It Works:** Constructs a pygame_gui-derived widget via real `__init__` with mocked pygame_gui element classes. Patches both the canonical `pygame_gui.elements.UI*` namespace and any module-bound imports. Introspects `__init__` signatures for default parameter injection.
> **When to Use:** Any unit test that needs a real UI widget instance without a real pygame display. NOT for UIWindow subclasses — use the `bypass_init` flag pattern instead (see known-issues.md).

---

## 6. Phase 6 Shared-Fixture Decisions (DUP-001 + HLP-001)

### DUP-001 (superweapon handler factory)

**Decision:** Deferred. The two files exercise genuinely different contract surfaces (execution path vs DI validation). A `@pytest.fixture(params=[...])` would dispatch on parameter to set up either an execution mock or a DI-validation mock — with 5+ handlers × 2 contracts = 10 distinct mock setups.

**Analysis:** The decision is sound. The proposed factory shape from the verification report (`params=[(handler_cls, mock_session_factory_for_execution), (handler_cls, mock_session_factory_for_di_validation)]`) would collapse ~200 LOC of structurally similar but semantically distinct code into a ~150 LOC switch-statement-like factory. The readability win is negative — the caller would need to understand two distinct mock-session shapes from a single parameter. The two files are testing different concerns (execution correctness vs DI contract validation) and keeping them separate is the right call.

**Verdict:** Sound. "Accept per-file expressiveness" is the correct disposition.

### HLP-001 (shared mock-ship/fleet/empire/planet)

**Decision:** Deferred. The four files use disparate `make_mock_*` shapes — fleet_report_filters needs 20+ display-name params, cargo_resources needs only cargo capacity (already handled by DUP-003), resupply_engine needs fuel-bearing mocks, session_facade needs facade-specific mocks.

**Analysis:** The decision is sound. A blanket `make_mock_ship` that handles all four use cases would grow into an unreadable kitchen-sink builder with ~30 optional kwargs. The narrower shared factories created where shapes did align (DUP-003 cargo, HLP-003 yard, HLP-004 planet) demonstrate good judgment — the team correctly identified that consolidation should happen at the *specific factory* level, not the *universal factory* level.

**Could a builder-pattern factory absorb the shape variation?** A fluent builder (`MockShipBuilder().with_display_name("X").with_cargo(c).with_fuel(f).build()`) could technically absorb all four shapes. But:
- The builder itself would be ~80-100 LOC
- Each consumer would need ~5 chained method calls instead of ~20 inline constructor arguments
- The LOC win would be at best ~50 (200 LOC dedup minus ~150 LOC builder), which is less than the 3 narrower factories already created (~70 LOC total dedup)
- The builder is strictly more complex than any individual file's helper

**Verdict:** Sound. A builder-pattern approach would be net complexity-positive given the shape divergence. The current disposition (narrower factories where shapes align, per-file helpers where they don't) is correct.

---

## 7. Continuation Recommendations

### Priority 1 — Quick Wins (no new project needed)

| ID | Description | Effort | Unblocks |
|---|---|---|---|
| **C-1** | Add `bypass_init` flag to UIWindow subclasses | 1-2 days | 14 deferred items (7 APC-001 + 5 Phase 3 + 2 Phase 5 cross-coordinated) |
| **C-2** | Refactor LLMBackgroundCall with completion Event | ~1 hour | Task 4.3 |

**C-1 and C-2 should be the first two tasks in the next PROJ.** They are independent and can be done in parallel (different files, no coupling).

### Priority 2 — Focused follow-ups (scoped projects)

| Project | Scope | Effort | Deferred Items Addressed |
|---|---|---|---|
| **PROJ-32x: UIWindow testability refactor** | Add `bypass_init` flag to 5+ production UIWindow subclasses; migrate 7 APC-001 test files + 5 Phase 3 boundary-patching tasks; update `make_ui_widget` docs in patterns | 3-5 days | 3.19, 3.20, 3.21, 3.24, 3.26, 5.6, 5.7, 5.10a/5.10b, 5.11, 5.12, 5.16, 5.29 |
| **PROJ-32y: RaceSetupScreen testable construction** | Refactor RaceSetupScreen for testability (potentially extract construction to a DI-friendly factory or add bypass_init flag); migrate deferred Tasks 2.17 + 5.11 | 2-3 days | 2.17, 5.11 |
| **PROJ-32z: Per-task deferred sweeps** | Patient pass over each of the 7 Phase 2 mutable-mock candidates and the 2 Phase 3 non-UIWindow-gated boundary-patching candidates. For each: audit whether the fixture is actually mutated by tests, and if not, rescope. If yes, consider copy-on-write wrapper. | 1-2 days | 2.6, 2.11, 2.15, 2.19, 3.14, 3.15 |

### Priority 3 — De-prioritize (cost exceeds benefit)

| Item | Rationale |
|---|---|
| DUP-001 superweapon factory | Net complexity-positive; per-file expressiveness is a feature |
| HLP-001 blanket mock-ship builder | Already addressed by narrower factories (DUP-003, HLP-003, HLP-004) |
| Task 3.25 strategy-screen refactor | Genuinely a multi-day effort with ~50 tests; low ROI for test-quality improvement |
| Task 3.14 virtual-table @patch migration | 700+ LOC of high-regression-risk rewrites; defer until test runtime is measured to be a problem |

### Plan.md Continuation Guide validation

The plan.md Continuation Guide is accurate and well-scoped. The three systemic blockers it identifies (UIWindow, LLMBackgroundCall, RaceSetupScreen) correctly gate the deferred work. The "what's actionable now" list is honest about the risk:reward ratio being unfavorable in P1 scope. The "what requires a new project" list matches our analysis above.

**Suggested refinement to the continuation guide:** The LLMBackgroundCall refactor (our C-2 above) is so small (~1 hour, +4 lines) that it should NOT require its own project. Bundle it with the UIWindow refactor project as an easy Phase 1 task.

### Unified continuation sequence

```
PROJ-32x Phase 1: C-1 (UIWindow bypass_init) + C-2 (LLMBackgroundCall Event)
PROJ-32x Phase 2: Migrate 12 deferred APC-001 + boundary-patching tasks (now unblocked)
PROJ-32x Phase 3: Optionally pick up 2 non-UIWindow-gated Phase 3 boundary tasks
PROJ-32y: RaceSetupScreen testable construction (if needed after bypass_init covers it)
PROJ-32z (optional): Per-task deferred sweeps for mutable-mock candidates
```

**Rough total effort:** 5-10 days to address all addressable deferred items.

---

## Findings Summary

### CRITICAL
- **CRIT-001:** UIWindow bypass_init flag is the correct unblocking path. Recommend Option (a) over (b) or (c). The `build_queue_screen` integration-test precedent does not scale to all 7 affected files.
- **CRIT-002:** LLMBackgroundCall refactor should be bundled with the UIWindow project, not its own PROJ. +4 lines of production code, ~1 hour.

### MAJOR
- **MAJ-001:** `make_ui_widget` factory should be promoted to `docs/02_PATTERNS.md` as a canonical pattern. It has 8 consumers, documented contract, test coverage, and is stateless.
- **MAJ-002:** DUP-001 and HLP-001 deferrals are correctly sustained. A builder-pattern factory would be net complexity-positive.
- **MAJ-003:** All 25 deferrals are substantively justified. No creative workaround could land them within P1 scope.
- **MAJ-004:** Completed work quality is high. The boundary-patching and factory migrations are genuine improvements, not complexity-shuffling.
- **MAJ-005:** The `_PYGAME_GUI_ELEMENT_NAMES` static list in the factory needs a maintainability comment for when new element types are introduced.

### MINOR
- **MIN-001:** The `_default_rect()` fallback to `MagicMock` (when pygame is not importable) should document the import-ordering requirement.
- **MIN-002:** The plan.md Continuation Guide should be updated to note that the LLMBackgroundCall refactor is small enough to bundle with the UIWindow project.

### INFO
- **INFO-001:** Task 4.3 (test_background.py polling) is solvable with the existing `threading.Event` infrastructure. The deliberate Event-based solution is simpler than the rejected mocked-clock approach.
- **INFO-002:** Two Phase 5 tasks (5.10a/5.10b, workshop-screen integration tests) are deferred but the manifest.md already lists `tests/integration/ui/workshop_screen/` as Type=Test (NEW). Verify this directory exists and the manifest entry is accurate before the next project starts.

---

## Continuation Recommendations (Final)

### Priority sequence

1. **Immediate (next PROJ, Phase 1):** Implement `bypass_init` flag on UIWindow subclasses (Option a) + LLMBackgroundCall completion Event. **Effort: 1-2 days.**
2. **Next PROJ, Phase 2:** Migrate 12 deferred APC-001 + boundary-patching tasks now unblocked by bypass_init. **Effort: 1-2 days.**
3. **Follow-up PROJ:** RaceSetupScreen testable construction OR verify it's covered by the bypass_init flag. **Effort: 1-3 days.**
4. **Optional/lower priority:** Per-task deferred sweeps for the 7 mutable-mock candidates. Only worth doing if test runtime is measured to be a problem. **Effort: 1-2 days.**

### What NOT to do

- Do NOT pursue Option (b) (metaclass/factory MRO interception). It couples to pygame_gui internals.
- Do NOT pursue Option (c) (integration-test replacement) for all 7 files. It loses test fidelity for RaceSetupScreen and FleetReportWindow.
- Do NOT create a blanket make_mock_ship factory (HLP-001). The narrower factories (cargo, yard, planet) are the correct granularity.
- Do NOT un-defer Task 3.25 (strategy-screen refactor). It genuinely exceeds P1 scope.
