# PROJ-324: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source

- Continuation review of PROJ-321 / 322 / 323 dated 2026-05-04
- Independent OpenCode delegate review of PROJ-322: `Reviews/results/2026-05-04_015938_consistency_proj-322-p1-brittle-bloated-test-remediation-compl_req-req_20260504_015935_7d4449/report.md`
- Continuation plan: [`AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md`](../../../AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md)
- Required reading: [`docs/known-issues.md`](../../../docs/known-issues.md) — UIWindow + LLM blocker context

## Initial Analysis

PROJ-322 created a shared `make_ui_widget(Cls, **kwargs)` factory at [`tests/fixtures/ui_widget_factory.py`](tests/fixtures/ui_widget_factory.py) (~279 LOC) that successfully replaced the `__new__` bypass-init pattern across 8 of the 16 APC-001 cluster files. The factory works for non-UIWindow widgets by patching `pygame_gui.elements.UI*` classes in both the canonical namespace and any module-bound imports, then calling the real `__init__`.

**It cannot construct UIWindow subclasses.** When `__init__` calls `super().__init__()`, Python uses the MRO resolved at class-definition time. The factory's runtime patches don't affect the parent class object that the `super()` call dispatches to. Result: `super().__init__()` runs the real `pygame_gui.UIWindow.__init__`, which requires a real pygame display.

This blocked 14 PROJ-322 tasks across 7 production classes. PROJ-322 documented three unblocking options in [`docs/known-issues.md`](docs/known-issues.md):

| Option | Effectiveness | Risk | Cost |
|---|---|---|---|
| (a) Production `bypass_init=True` flag | High | Low (opt-in escape hatch) | Medium (~5 production class edits) |
| (b) Factory enhancement (intercept super-call site via metaclass / `patch.object`) | Medium | Med-High (couples to pygame_gui internals) | High |
| (c) Replace UIWindow unit tests with integration tests | Variable | Low | Variable (loses fidelity for RaceSetupScreen / FleetReportWindow) |

**Decision: Option (a).** The independent OpenCode 322-review (CRIT-001) and Claude's Explore-agent investigation independently arrived at the same recommendation. Rationale:

1. **Lowest risk.** The flag is an opt-in escape hatch. Production code never sets it. The guard is `if getattr(type(self), 'bypass_init', False): return` — `getattr` with default `False` is backwards-compatible.
2. **Highest coverage yield.** Unblocks all 7 APC-001 files plus 5 Phase 3 boundary tasks simultaneously.
3. **No coupling to pygame_gui internals.** Option (b) would couple to library version-specific MRO and `__init__` internals; a `pygame_gui` upgrade could silently break it.
4. **Option (c) doesn't scale.** The `tests/integration/ui/build_queue_screen/` precedent (5 files / 1498 LOC replacing 580 LOC of unit tests) worked because BuildQueueScreen has a focused test surface. RaceSetupScreen has ~150 unit tests across MVVM delegates, tab navigation, race config validation, LLM dialog, slider event routing — converting these to integration tests loses fidelity.

## Implementation Pattern (UIWindow flag)

```python
# In each affected UIWindow subclass __init__:
def __init__(self, ...):
    if getattr(type(self), 'bypass_init', False):
        return
    super().__init__(...)  # normal pygame_gui chain
    # ... rest of init
```

Tests then:

```python
# Either set the flag explicitly:
FleetReportWindow.bypass_init = True
window = make_ui_widget(FleetReportWindow, fleet=mock_fleet, empire=mock_empire)
FleetReportWindow.bypass_init = False  # always reset

# Or (PREFERRED) wrap in a context manager / fixture:
with bypass_init(FleetReportWindow):
    window = make_ui_widget(FleetReportWindow, ...)
```

The cleanup-on-exception form is critical to prevent test bleed. **Bare assignment in test bodies is a CR-block** — implementations MUST add a `bypass_init(Cls)` context manager (or pytest fixture) to `tests/fixtures/ui_widget_factory.py` before any test code uses the flag.

**StrategyModalWindow first.** `FleetReportWindow`, `OrdersWindow`, `TransferDialog`, `BuildQueueListWindow` all inherit from `StrategyModalWindow`, which inherits from `UIWindow`. Adding the guard to `StrategyModalWindow.__init__` covers all 4 subclasses transitively — but the guard must check `type(self)` (the concrete subclass), not `StrategyModalWindow`, so the flag set on `FleetReportWindow.bypass_init = True` is honored by the inherited `StrategyModalWindow.__init__`.

## LLMBackgroundCall Implementation Pattern

Current state of [`game/services/llm/background.py`](game/services/llm/background.py):

- `threading.Lock` (`_state_lock`) guards mutable state.
- `threading.Event` (`_cancel_event`) used for cancellation — already present.
- Module-level concurrent-call accounting with `_in_flight_lock`.
- Non-daemon workers tracked in `_active_workers` for `shutdown_all_calls()`.

What's missing: a completion event the main thread can wait on instead of polling `status`.

```python
# In LLMBackgroundCall.__init__ (after existing fields):
self._done_event = threading.Event()

# In _run() — after each terminal-state transition (DONE, ERROR, CANCELLED):
self._done_event.set()

# New public method:
def wait(self, timeout: float | None = None) -> bool:
    """Block until the call reaches a terminal state, or until timeout. Returns True if reached, False on timeout."""
    return self._done_event.wait(timeout)
```

Test migration is mechanical:

```python
# Before:
deadline = time.monotonic() + 2.0
while call.status not in (CallStatus.DONE, CallStatus.ERROR) and time.monotonic() < deadline:
    time.sleep(0.01)
assert call.status == CallStatus.DONE

# After:
assert call.wait(timeout=2.0), "call did not complete within 2s"
assert call.status == CallStatus.DONE
```

5–6 polling loops in [`tests/unit/services/llm/test_background.py`](tests/unit/services/llm/test_background.py) convert this way.

## Architecture

### `make_ui_widget` factory (introduced PROJ-322 Phase 5, retained as-is)

Location: [`tests/fixtures/ui_widget_factory.py`](tests/fixtures/ui_widget_factory.py)

The factory itself is unchanged by this project. The only addition is documentation and a `bypass_init(Cls)` context manager. The factory:

- Patches all `pygame_gui.elements.UI*` classes in canonical namespace + module-bound imports (handles `from pygame_gui.elements import UILabel` style).
- Walks target class MRO to find all modules that need patching.
- Introspects `__init__` signatures for default parameter injection.
- Supports `extra_modules` for transitively-imported helpers.
- Uses `unittest.mock.patch` context managers for cleanup-on-exception.

### Affected production class inheritance graph

```
pygame_gui.elements.UIWindow
├── StrategyModalWindow                        (game/ui/screens/strategy_modal_window.py:27)
│   ├── FleetReportWindow                      (game/ui/screens/fleet_report_window.py:32)
│   ├── OrdersWindow                           (game/ui/screens/orders_window.py:36)
│   ├── TransferDialog                         (game/ui/screens/transfer_dialog.py:45)
│   └── BuildQueueListWindow                   (game/ui/screens/build_queue_list_window.py:18)
├── RaceSetupScreen                            (game/ui/screens/race_setup/screen.py:60)
└── NewGameSetupScreen                         (game/ui/screens/new_game_setup_screen.py:84)

(standalone, NOT a UIWindow but tested in same cluster:)
BuildQueueScreen                               (game/ui/screens/build_queue_screen.py:38)
```

`BuildQueueScreen` is NOT a UIWindow subclass — its unit test was deleted by PROJ-322 Phase 5 in favor of integration tests at `tests/integration/ui/build_queue_screen/`. Confirm in Phase 3 that no Phase 3 task targets it; if so, the integration tests already cover the surface.

### Key Patterns to Reuse

- **`make_ui_widget` factory**: [`tests/fixtures/ui_widget_factory.py`](tests/fixtures/ui_widget_factory.py) — call real `__init__` with patched dependencies. After this project, also works for UIWindow subclasses via `bypass_init` context manager.
- **Boundary patching** (Phase 3 tasks): drive tests through public surface (`handle_event`, `update`, `draw`, domain methods like `engine.start()`) rather than patching private helpers. PROJ-322 examples: [`tests/unit/simulation/systems/test_battle_engine_init_ship.py`](tests/unit/simulation/systems/test_battle_engine_init_ship.py).
- **`threading.Event` completion signaling**: pattern PROJ-324 introduces in `LLMBackgroundCall`; reuse for any other test that polls a worker thread.

## Risks

1. **`type(self)` vs `__class__` semantics.** The guard must consult the concrete subclass, not the class that defines `__init__`. If `StrategyModalWindow.__init__` does `if getattr(StrategyModalWindow, 'bypass_init', False): return`, the flag set on `FleetReportWindow.bypass_init = True` is ignored. **Always use `type(self)` or `self.__class__`.**

2. **Test bleed from forgotten flag.** A test that sets `Cls.bypass_init = True` and crashes before unsetting it leaves the flag set for the rest of the run. Use the `bypass_init` context manager / fixture, not bare assignment.

3. **Partial guard coverage.** If `RaceSetupScreen.__init__` does work BEFORE the guard check (e.g., parameter validation), the guard skips that work — possibly hiding a real bug. The guard must be the FIRST executable statement in `__init__` (after the docstring).

4. **`super().__init__()` alternative paths.** Some subclasses may call `pygame_gui.elements.UIWindow.__init__(self, ...)` explicitly instead of via `super()`. Audit each affected class for explicit parent-class calls — the guard handles `super()` but not explicit ancestor calls.

5. **LLMBackgroundCall lock ordering.** The `_done_event.set()` call must be outside `_state_lock` to avoid waiter starvation if a `wait()`-er blocks while holding the lock indirectly. Standard `threading.Event` semantics handle this — but verify with the existing `TestLockSafety` tests after the change.

6. **Cross-project file conflict.** Phase 3 modifies test files that may also be touched by PROJ-325 (RaceSetupScreen) and PROJ-327 (mutable-mock fixture rescopes). The manifest documents per-file ownership; coordinate before editing.

## Patterns to Promote (Phase 4)

Per OpenCode 322-review MAJ-001, `make_ui_widget` should be promoted to `docs/02_PATTERNS.md` as a canonical pattern. Suggested entry:

> **15b. UI Widget Test Factory (PROJ-322 / PROJ-324)**
>
> **Where:** [`tests/fixtures/ui_widget_factory.py`](tests/fixtures/ui_widget_factory.py) — `make_ui_widget(Cls, extra_modules=(), **kwargs)`
>
> **How It Works:** Constructs a pygame_gui-derived widget via real `__init__` with mocked `pygame_gui.elements.UI*` classes. Patches both the canonical namespace and any module-bound imports. Introspects `__init__` signatures for default parameter injection. For UIWindow subclasses, use the `bypass_init(Cls)` context manager during construction.
>
> **When to Use:** Any unit test that needs a real UI widget instance without a real pygame display.
>
> **When NOT to Use:** Integration testing of widget interactions — use `tests/integration/ui/` patterns instead.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
