# Agent C — PROJ-324 Code & Docs Audit

**Date:** 2026-05-04  
**Review scope:** bypass_init guard placement, factory robustness, LLMBackgroundCall edge cases, documentation drift

---

## FOCUS AREA 1: bypass_init guard placement

### FND-C01 (WARN) — Pattern doc §33 "MUST be first statement" rule contradicted by two-stage pattern

**File:** `docs/02_PATTERNS.md:1831`
**Evidence:**
```
The guard MUST be the first executable statement in `__init__`.
Anything before the guard runs even when bypass is active — that's
almost always a bug (see PROJ-324 systemic finding 2026-05-04).
```
Yet lines 1794-1809 in the same §33 explicitly document the two-stage pattern where cheap state + delegate construction runs BEFORE the bypass guard:

```python
# Stage 1: cheap state + delegates (always runs)
self._race_config = ...
delegates = (delegate_factory or DefaultRaceSetupDelegateFactory()).build(self)
self._controller = delegates.controller
self._view_model = delegates.view_model
self._renderer = delegates.renderer
if getattr(type(self), "bypass_init", False):
    return  # Stage 2 skipped; delegates are real and exercise-able
```

**Actual state on disk:** `RaceSetupScreen` (race_setup/screen.py:151) and `NewGameSetupScreen` (new_game_setup_screen.py:177) both run significant work BEFORE their `bypass_init` guard — by design. This is NOT a bug; it's the intended two-stage construction. The §33 text has an unresolved internal contradiction: the absolute "MUST be first" admonition in the Migration notes contradicts the canonical two-stage example in the "How It Works" section.

**Recommendation:** Reword lines 1831-1832 to: "The guard SHOULD be the first point where `UIWindow.__init__` is avoided. Any code above the guard runs in both production and test modes and MUST be cheap (no pygame_gui widget construction, no `self.get_container()`, no display-dependent calls)."

---

### FND-C02 (INFO) — StrategyModalWindow bypass_init guard is correctly placed

**File:** `game/ui/screens/strategy_modal_window.py:118`

The guard is the first executable statement in `__init__` (line 118). Uses `getattr(type(self), 'bypass_init', False)` — uses `type(self)`, matching the design.md requirement. Sets `self._window_manager`, `self.ui_manager`, `self._window_init_bypassed = True` before returning. Correct.

---

### FND-C03 (INFO) — RaceSetupScreen: guard is NOT first statement (by design)

**File:** `game/ui/screens/race_setup/screen.py:151`

The guard at line 151 is preceded by ~25 lines of Stage 1 setup (lines 126-143):
- `self._init_state(...)` — assigns `race_config`, `race_library`, callbacks, `_asset_loader`
- `self._init_widget_refs()` — assigns 15+ widget slots to None
- `DefaultRaceSetupDelegateFactory().build(self)` — constructs ViewModel, Renderer, Controller, InputHandler, LLMDialogService

This is intentional two-stage construction per PROJ-325 Phase 3. All Stage 1 work is pure-Python, no pygame_gui widgets. The guard at line 151: `if getattr(type(self), 'bypass_init', False):` then sets `self.ui_manager = manager` and `self._window_init_bypassed = True`. Does NOT assign `self.rect` (correctly, per PROJ-325 PoC finding 1 — `pygame_gui`'s `GUISprite` descriptor would crash on uninitialized `blit_data`).

---

### FND-C04 (INFO) — NewGameSetupScreen: same two-stage pattern

**File:** `game/ui/screens/new_game_setup_screen.py:177`

Guard at line 177 uses `getattr(type(self), 'bypass_init', False)`. Stage 1 (lines 157-170) runs `_init_state()`, `_init_widget_refs()`, creates `NewGameSetupViewModel()` and `NewGameSetupController(...)`. Guard then sets `self.ui_manager = manager`, `self._window_init_bypassed = True`. Correct two-stage pattern. Does NOT assign `self.rect` (same rationale as RaceSetupScreen). 

---

### FND-C05 (INFO) — BuildQueueListWindow relies on transitive guard only

**File:** `game/ui/screens/build_queue_list_window.py:165`

No own `bypass_init` guard. Relies on `StrategyModalWindow.__init__` guard transitively via `super().__init__(...)` at line 165. Stage 1 cheap state (lines 158-162: `self.empire`, `self.on_close_callback`, `self._mapper`, `self.row_labels`, `self._row_collector`) runs BEFORE the `super().__init__()` call. When bypass_init is active, the base class returns immediately (setting `_window_init_bypassed=True`), and the post-super code at line 177 checks `getattr(self, '_window_init_bypassed', False)` to short-circuit widget construction. Safe — crashes avoided via the `_window_init_bypassed` check and the conditional `ui_builder` gate.

---

### FND-C06 (INFO) — FleetReportWindow relies on transitive guard only

**File:** `game/ui/screens/fleet_report_window.py:192`

Same pattern as BuildQueueListWindow. No own guard. Stage 1 state (lines 163-189: fleet, empire, callbacks, layout constants, view_model, column_manager, selection, widget ref placeholders) set before `super().__init__()` at line 192. Post-super check at line 201: `getattr(self, '_window_init_bypassed', False)`. Safe.

---

### FND-C07 (INFO) — OrdersWindow relies on transitive guard only

**File:** `game/ui/screens/orders_window.py:340`

No own guard. Stage 1 state (lines 317-332: entity, entity_type, callbacks, `_initial_rect`, `_order_describer`, `_list_renderer`, placeholder lists) set before `super().__init__()` at line 340. Post-super check at line 350: `_window_init_bypassed`. Safe.

---

### FND-C08 (INFO) — TransferDialog relies on transitive guard only

**File:** `game/ui/screens/transfer_dialog.py:147`

No own guard. Stage 1 state (lines 124-144: source_fleet, hex_coord, scene, facade, renderer, view_model, controller, pod names, widget refs) set before `super().__init__()` at line 147. Post-super check at line 158: `_window_init_bypassed`. Safe.

---

### FND-C09 (INFO) — Zero per-class guards added; transitive pattern works differently than systemic finding warned

The PROJ-324 systemic finding (commit `9e177edb7`) warned that "subclasses WITHOUT their own guard CRASH." The four `StrategyModalWindow` subclasses (BuildQueueListWindow, FleetReportWindow, OrdersWindow, TransferDialog) resolved this NOT by adding per-class guards but by checking `self._window_init_bypassed` (set by the base class under bypass) after `super().__init__()` returns. The pattern doc §33 Migration notes (line 1831) says the guard MUST be the first statement but does not document this alternative approach — the per-subclass `_window_init_bypassed` check pattern is entirely undocumented in §33.

**Recommendation:** Add to §33 Migration notes: "For `StrategyModalWindow` subclasses, a per-class guard is not needed if the subclass checks `self._window_init_bypassed` (set by the base class) after `super().__init__()` returns. This is the pattern used by `BuildQueueListWindow`, `FleetReportWindow`, `OrdersWindow`, and `TransferDialog`."

---

## FOCUS AREA 2: make_ui_widget factory robustness

### FND-F01 (GAP) — No bypass_init on UIWindow subclass → silent crash if used via make_ui_widget alone

**File:** `tests/fixtures/ui_widget_factory.py`

`make_ui_widget(Cls, **kwargs)` patches `pygame_gui.elements.UI*` classes but does NOT intercept `super().__init__()` resolution through the MRO. For any `UIWindow` subclass without a `bypass_init` guard, the factory's element patches leave `super().__init__(self, ...)` calling the real `pygame_gui.elements.UIWindow.__init__`, which requires a live pygame display → crash. This is by design (the docs say use `bypass_init` for UIWindow subclasses), but the factory itself has no explicit guard or informative error. A caller who doesn't read the docs gets a cryptic pygame-internal error rather than a clear message.

**Recommendation:** Add a runtime check in `make_ui_widget`: if `cls` is a subclass of `UIWindow` and `cls.__dict__.get('bypass_init') is None` (no guard), issue a `logger.warning("UIWindow subclass %s has no bypass_init guard; construction will fail without 'with bypass_init(cls):'")`. Not a hard error — some UIWindow subclasses may have lightweight init that works.

---

### FND-F02 (OK) — Conflicting kwargs: caller wins

**File:** `tests/fixtures/ui_widget_factory.py:329`
```python
defaults = _build_default_kwargs(cls)
defaults.update(kwargs)
```
`dict.update` means caller-supplied `kwargs` overwrite introspected defaults. Documented correctly in module docstring line 35: "Any parameter the caller passes takes priority." Correct behavior.

---

### FND-F03 (OK) — `*args` and `**kwargs` in `__init__` handled

**File:** `tests/fixtures/ui_widget_factory.py:150-154`
```python
if param.kind in (
    inspect.Parameter.VAR_POSITIONAL,
    inspect.Parameter.VAR_KEYWORD,
):
    continue
```
Variadic parameters are skipped. No attempt to generate mocks for them. Correct.

---

### FND-F04 (OK) — Inherited `__init__` handled via `inspect.signature`

`_build_default_kwargs` calls `inspect.signature(cls.__init__)`. Python's `__init__` resolution follows MRO, so inherited `__init__` signatures are correctly introspected. For classes whose `__init__` traces to `object.__init__(self, /, *args, **kwargs)`, all parameters are variadic → return `{}`. The actual construction call `cls(**defaults)` would then pass no kwargs. This is correct for the trivial case.

---

### FND-F05 (OK) — Context manager exception safety: try/finally

**File:** `tests/fixtures/ui_widget_factory.py:282-292`
```python
previous = cls.__dict__.get("bypass_init", _SENTINEL)
cls.bypass_init = True
try:
    yield
finally:
    if previous is _SENTINEL:
        try:
            delattr(cls, "bypass_init")
        except AttributeError:
            pass
    else:
        cls.bypass_init = previous
```
`try/finally` guarantees flag cleanup on exception. `previous is _SENTINEL` restores the pre-context state (absent → delete; present → restore prior value). Correct.

---

### FND-F06 (OK) — Nested bypass_init contexts: handled

The sentinel-based restore correctly handles nesting:
1. Outer ctx: `previous = _SENTINEL`, sets `cls.bypass_init = True`
2. Inner ctx: `previous = True` (from `cls.__dict__`), sets `cls.bypass_init = True` (no-op)
3. Inner finally: restores `cls.bypass_init = True` (what it was before inner)
4. Outer finally: `previous` was `_SENTINEL` → `delattr(cls, "bypass_init")`

After all contexts exit, `bypass_init` is absent (original state). Correct.

---

### FND-F07 (GAP) — pygame_gui element list coverage

**File:** `tests/fixtures/ui_widget_factory.py:84-102`

The `_PYGAME_GUI_ELEMENT_NAMES` tuple has 17 entries. All element types used in `game/ui/` production `__init__`-time widget construction are covered:
- `UIPanel`, `UILabel`, `UIButton`, `UIImage`, `UITextEntryLine`, `UITextEntryBox`, `UITextBox`, `UIDropDownMenu`, `UIScrollingContainer`, `UIHorizontalSlider`, `UIWindow` — all verified in use.

Entries NOT used in current production code (but safe to include): `UISelectionList`, `UIVerticalScrollBar`, `UIStatusBar`, `UIScreenSpaceHealthBar`, `UIProgressBar`, `UITooltip` — no matches found in `game/ui/` for element construction calls. These are forward-looking coverage. Not a bug.

One notable gap: `UIConfirmationDialog` (from `pygame_gui.windows`, not `pygame_gui.elements`) is used in `orders_window.py:440`. It is created dynamically in `show_clear_confirmation()`, not during `__init__`, so it does not affect factory-based construction. The factory's docstring correctly says "anything outside [the list] is simply left alone (the production code will then attempt the real construction and fail loudly, which is the correct signal)." Correct design.

---

### FND-F08 (GAP) — No test for factory on a UIWindow subclass WITHOUT bypass_init

The test file `tests/fixtures/test_ui_widget_factory.py` should include a negative test: constructing a `StrategyModalWindow` subclass without `bypass_init` should either produce a clear error or be documented as a known limitation. Currently, callers who forget `with bypass_init(Cls):` get a cryptic pygame-internal crash. Whether this is tested is unknown from the current review scope (test file not fully read), but worth flagging.

---

## FOCUS AREA 3: LLMBackgroundCall completion Event

### FND-L01 (OK) — `_done_event.set()` is outside `_state_lock`

**File:** `game/services/llm/background.py:267`

The `_done_event.set()` call at line 267 is inside the inner `finally` block (line 265), which is outside ALL `_state_lock` contexts. The lock is held for status transitions at lines 233-237, 242-246, 248-254, 258-263, but released before `self._done_event.set()`. Matches the design requirement. 

---

### FND-L02 (BUG) — Unexpected exception in `_provider.complete()` sets `_done_event` but leaves `_status` at RUNNING

**File:** `game/services/llm/background.py:240,267`

If `self._provider.complete(...)` at line 240 raises an exception that is NOT `LLMCancelled` or `LLMException` (e.g., `TypeError`, `ValueError`, `KeyboardInterrupt`), the flow is:
1. `_status` set to `RUNNING` at line 237 (inside lock)
2. `_provider.complete(...)` raises unexpected exception
3. Inner `finally` (line 265): `_done_event.set()` — event IS set
4. Outer `finally` (lines 268-273): counter decremented, thread cleaned up
5. Exception propagates, worker thread dies

Result: `_done_event` is set → `wait()` returns `True`. But `_status` is still `RUNNING`. Caller checks `call.status` expecting a terminal state (DONE/ERROR/CANCELLED) but sees RUNNING. This violates the `wait()` API contract: "Returns True if a terminal state (DONE, ERROR, or CANCELLED) was reached."

**Reproduction path:** A provider that raises `TypeError` or a third-party exception type that is a subclass of `Exception` but not `LLMException`.

**Recommendation:** In the inner `finally` block or the outer `finally` block, capture any unhandled exception, transition `_status` to `ERROR`, and store the exception in `self._error`:

```python
finally:
    self._done_event.set()
```
→
```python
except BaseException as e:
    with self._state_lock:
        if self._status not in (CallStatus.CANCELLED, CallStatus.DONE):
            self._status = CallStatus.ERROR
            if not isinstance(self._error, LLMException):
                self._error = LLMException(
                    f"Unexpected error: {e}",
                    code=ErrorCode.LLM_UNKNOWN.value,
                )
            self._finished_at = time.monotonic()
finally:
    self._done_event.set()
```

Note: `BaseException` catch should be narrowed to `Exception` to avoid catching `SystemExit`/`KeyboardInterrupt`, which are OS-signal-level and should propagate.

---

### FND-L03 (ACCEPTABLE GAP) — Worker thread killed externally → `_done_event` never set

If the OS kills the worker thread externally (e.g., `Process Explorer` kill, `taskkill /F`, segfault), `_done_event` is never set. `wait(timeout=None)` blocks forever. `wait(timeout=N)` times out and returns `False`. This is inherent to thread-level termination — no mitigation possible in Python. The caller must always use a timeout for robustness. The `shutdown_all_calls(5.0)` timeout pattern provides a model (abandon hung workers). Not a bug, but worth documenting as a known limitation.

---

### FND-L04 (OK) — `wait(timeout)` edge cases

- **`timeout=None`**: blocks indefinitely. ✓
- **`timeout=0`**: `threading.Event.wait(0)` returns immediately with current state. ✓
- **Thread safety**: `threading.Event.wait()` is thread-safe. ✓

---

### FND-L05 (OK) — Idempotency of `_done_event.set()`

`threading.Event.set()` is idempotent — calling it multiple times (e.g., `cancel()` at line 177 + `_run()` inner finally at line 267) is a no-op. Correct.

---

### FND-L06 (GAP) — `wait()` before `start()` without `cancel()` blocks forever

**File:** `game/services/llm/background.py:196-209`

If a caller calls `wait()` before `start()`, the `_done_event` has never been set (unless `cancel()` was called first). With `timeout=None`, this blocks forever. The docstring says "Returns immediately if already in a terminal state" but does not warn about the pre-start case. PENDING is NOT a terminal state, so `wait()` correctly blocks — but the caller may not expect this.

**Recommendation:** Add to the `wait()` docstring: "If neither `start()` nor `cancel()` has been called, `wait(timeout=None)` blocks forever. Callers should always call `start()` first or use a timeout."

---

### FND-L07 (OK) — Test migration: all polling loops migrated

**File:** `tests/unit/services/llm/test_background.py`

Verified: all polling patterns (`while call.status != DONE: time.sleep(...)`) have been replaced with `assert call.wait(timeout=2.0)`. Confirmed in tests: `test_completes_with_result` (line 128), `test_elapsed_seconds_is_monotonic_then_frozen` (line 145), `test_propagates_llm_exception_to_error_field` (line 160), `test_cancel_marks_status_cancelled` (line 176), `test_double_start_does_not_spawn_two_workers` (line 204), `test_completed_calls_free_up_slots` (line 261).

Remaining `time.sleep()` calls (4 total) are NOT polling loops:
- Line 63: inside `_SlowProvider.complete()` — fake provider implementation
- Line 141: `time.sleep(0.01)` — one-shot wait for worker to start
- Line 149: `time.sleep(0.05)` — one-shot verify `elapsed_seconds` freeze
- Line 174: `time.sleep(0.02) # let worker actually start` — one-shot

All correct. Migration complete.

---

## FOCUS AREA 4: Documentation drift

### FND-D01 (DRIFT) — Pattern doc §33 "MUST be first statement" contradicts its own two-stage example

**File:** `docs/02_PATTERNS.md:1831-1832`

See FND-C01. The Migration notes admonition is directly contradicted by the canonical code example in the same section. This is an internal inconsistency within a single document section, not a cross-document drift.

---

### FND-D02 (DRIFT) — Pattern doc §33 does NOT mention zero LOC reduction

The PROJ-324 systemic finding documented that the Phase 1 `bypass_init` guard alone delivered zero test-side LOC reduction. Pattern doc §33 references "PROJ-324 systemic finding 2026-05-04" (line 1832) but does not explicitly state the zero-LOC conclusion. The sentence "Almost always a bug" implicitly invokes the finding but doesn't convey the key takeaway: bypass_init alone is insufficient without two-stage construction.

**Recommendation:** Add: "Note: the Phase 1 guard alone delivered zero test-side LOC reduction (PROJ-324 systemic finding). The two-stage pattern below is required for actual test-code shrinkage."

---

### FND-D03 (OK) — Cross-references to PROJ-325/PROJ-328 accurate

Pattern doc §33 correctly references:
- PROJ-325 Phase 3 RaceSetupScreen two-stage refactor → verified on disk at `game/ui/screens/race_setup/screen.py`
- PROJ-328 A/B/C per-class refactors → verified on disk (BuildQueueListWindow, OrdersWindow, FleetReportWindow, NewGameSetupScreen, TransferDialog)
- Per-class Null/Mock UI-builder fixtures → verified in doc references at lines 1752-1755

All references resolve to existing files.

---

### FND-D04 (OK) — Known-issues.md: UIWindow blocker marked RESOLVED, text accurate

**File:** `docs/known-issues.md:8-41`

Resolution section (lines 31-40) accurately describes:
- PROJ-324 Phase 1 bypass_init guard → `StrategyModalWindow.__init__:118` ✓
- PROJ-324 Phase 3 systemic finding (two-stage needed) → `9e177edb7` commit reference ✓
- PROJ-325 Phase 3 PoC (RaceSetupScreen) → `race_setup/screen.py` two-stage __init__ ✓
- PROJ-328 A/B/C roll-out → verified across 5 subclasses ✓

No contradictions with PROJ-324 systemic finding.

---

### FND-D05 (OK) — Known-issues.md: LLMBackgroundCall blocker marked RESOLVED, text accurate

**File:** `docs/known-issues.md:44-65`

Resolution section (lines 59-64) accurately describes:
- `self._done_event: threading.Event` → `background.py:103` ✓
- `_run()` sets event after terminal transitions → `background.py:267` ✓
- `wait(timeout)` public method → `background.py:196-209` ✓
- Test migration: 5-6 polling loops → `call.wait(timeout=2.0)` → verified at FND-L07 ✓

---

### FND-D06 (DRIFT) — PROJ-322 plan.md tally: "71 substantive done" does not sum from phase totals

**File:** `Projects/active_projects/PROJ-322/plan.md:33`

The Final tally line claims: "71 substantive done, 17 obsolete-skipped, 25 formally deferred-out-of-scope."

Summing from the Phase Disposition Summary (lines 26-31):
| Phase | Done | N/A (aka substantive) | Satisfied | Obsolete | Deferred | Total |
|-------|------|----------------------|-----------|----------|----------|-------|
| 1 (19) | 18 | 0 | 0 | 1 | 0 | 19 |
| 2 (20) | 6 | 3 | 0 | 4 | 7 | 20 |
| 3 (26) | 12 | 0 | 0 | 7 | 7 | 26 |
| 4 (9) | 4 | 0 | 0 | 4 | 1 | 9 |
| 5 (34) | 13 | 0 | 4 | 10 | 7 | 34 |
| 6 (9) | 5 | 0 | 2 | 0 | 2 | 9 |

- **Done (direct):** 18 + 6 + 12 + 4 + 13 + 5 = 58
- **N/A (counted as substantive resolved):** 0 + 3 + 0 + 0 + 0 + 0 = 3
- **Satisfied via earlier phases:** 0 + 0 + 0 + 0 + 4 + 2 = 6
- **Substantive total:** 58 + 3 + 6 = **67**
- **Obsolete-skipped:** 1 + 4 + 7 + 4 + 10 + 0 = **26** (claimed 17)
- **Deferred:** 0 + 7 + 7 + 1 + 7 + 2 = **24** (claimed 25)

Discrepancies:
1. Substantive: **67** vs claimed **71** (off by 4)
2. Obsolete: **26** vs claimed **17** (off by 9)
3. Deferred: **24** vs claimed **25** (off by 1)
4. Phase 6 header claims "7 cluster items" (DUP-001..3 + HLP-001..4 = 7) but disposition lists 9 items (5 done + 2 satisfied + 2 deferred). Suggests 2 items are double-counted from Phase 1.

Additionally: `71 + 17 + 25 = 113`, but the claimed item manifest is 115-117 items total (depending on Phase 6 count). The totals don't self-consistently sum.

**Recommendation:** Re-audit the tally against `phase_N_checklist.md` files. The errors appear to be in the "obsolete-skipped" column (off by largest margin) and possibly in "satisfied via earlier phases" double-counting. Use `git log --stat` on the checklist files to get precise per-task dispositions.

---

### FND-D07 (DRIFT) — PROJ-324 phase_3_checklist.md: marked Complete but all tasks unchecked

**File:** `Projects/active_projects/PROJ-324/phase_3_checklist.md`

Status header (line 8): `**Status:** Complete`  
All 9 tasks (3.1-3.9): `- [ ]` (unchecked)  
Task Notes: Tasks 3.1, 3.2, 3.3, 3.5, 3.6, 3.7, 3.8 have empty Notes sections (no implementation record). Only Task 3.4 has substantial GO/NO-GO documentation.

The status text explains this: "closed as production foundation only; 14 test migrations re-routed to PROJ-325 Phase 3 PoC + PROJ-328 A/B/C." So the phase is Complete in the sense that a decision was made (not executable), but the checklist was never worked through. The "Complete" status is misleading — what was completed was a GO/NO-GO decision, not task execution.

**Recommendation:** Either:
1. Check all boxes as N/A with rationale: `- [x] N/A — rerouted to PROJ-325/PROJ-328 per systemic finding`
2. Or change status to `**Status:** Closed (rerouted)` and leave boxes as-is with an explanatory note

The current state (Complete + unchecked boxes + empty Notes) appears incomplete at a glance.

---

### FND-D08 (DRIFT) — Pattern doc §32 exists and is accurate

**File:** `docs/02_PATTERNS.md:1676-1732`

Pattern §32 (Compositional Construction) exists and accurately describes:
- `StrategyScreenComposition` Protocol + `StrategyScreenCompositionFactory` → verified against `game/ui/screens/strategy_screen_composition.py`
- `MockStrategyScreenComposition` test fixture → path resolves correctly
- Relationship to §33 (bypass_init is the retrofit for §32's canonical pattern) → correctly stated at line 1737

The PROJ-322 plan.md Continuation Guide (line 51) says Task 3.25 was resolved by PROJ-327 Phase 4 (Compositional Construction). This matches on-disk reality.

---

## Summary

| ID | Severity | Area | Description |
|----|----------|------|-------------|
| FND-L02 | **BUG** | LLMBackgroundCall | Unexpected provider exception sets `_done_event` but leaves `_status=RUNNING` — violates `wait()` contract |
| FND-C01 | WARN | Docs | Pattern doc §33 has internal contradiction: "MUST be first statement" vs documented two-stage pattern |
| FND-D06 | DRIFT | Docs | PROJ-322 tally math doesn't sum from phase totals (67 vs 71 substantive, 26 vs 17 obsolete) |
| FND-D07 | DRIFT | Docs | PROJ-324 phase 3 checklist marked Complete but all tasks unchecked with empty Notes |
| FND-L06 | GAP | LLMBackgroundCall | `wait()` before `start()` without `cancel()` blocks forever, undocumented |
| FND-F01 | GAP | Factory | No warning when `make_ui_widget` used on UIWindow subclass without bypass_init |
| FND-C09 | GAP | Docs | `_window_init_bypassed` check pattern (used by 4 subclasses) is undocumented |
| FND-F08 | GAP | Tests | No explicit negative test for factory-on-UIWindow-without-bypass |
| FND-D02 | DRIFT | Docs | Pattern doc §33 references systemic finding but doesn't state zero-LOC conclusion |

**Verdict:** One verified bug (FND-L02: unexpected exception path leaves `_status=RUNNING`). Two docs contradictions. Two docs tally errors. Three gaps (undocumented patterns, missing tests, missing warning). The bypass_init guard placements are all correct on disk; the two-stage pattern is well-implemented. The factory is robust for its documented use cases. Test migration for `wait()` is complete.
