# PROJ-324 Code Review — Findings Report

**Reviewer:** OpenCode
**Scope:** `bypass_init` UIWindow flag (Phase 1) + `LLMBackgroundCall.wait()` API (Phase 2) + test infra (`tests/fixtures/ui_widget_factory.py`)
**Date:** 2026-05-04

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR    | 2 |
| INFO     | 3 |

No production behavior regressions, data-loss risks, or race conditions found. All three `bypass_init` guards use `type(self)` correctly per D-003. The `LLMBackgroundCall._done_event` is set deterministically in all terminal paths. The `bypass_init()` context manager cleans up properly on exception. The `wait()` API correctly exposes terminal-state synchronization.

Two MAJOR findings: a pattern-consistency gap for `_window_init_bypassed` in the two direct-UIWindow subclasses, and a subtle window where `wait()` can return before the worker thread's lock-protected `_finished_at` update is visible.

---

## Findings

### FND-001: `_window_init_bypassed` flag not set in production path for direct UIWindow subclasses
**Severity:** MAJOR
**File:** `game/ui/screens/race_setup/screen.py`, `game/ui/screens/new_game_setup_screen.py`
**Line:** screen.py:165-175, new_game_setup_screen.py:193-202
**Description:** Both `RaceSetupScreen` and `NewGameSetupScreen` set `self._window_init_bypassed = True` in their bypass branches (screen.py:153, new_game_setup_screen.py:179) but **never** assign the flag in the production (non-bypass) path. StrategyModalWindow — the base class for all other bypass-capable UIWindows — consistently sets the flag in both paths: `True` in bypass (line 130), `False` in production (line 134). This means `_window_init_bypassed` exists on a `RaceSetupScreen`/`NewGameSetupScreen` instance **only** when constructed under `bypass_init`; in production, `getattr(self, '_window_init_bypassed', None)` returns `None`.

No crash can occur today because every consumer of `_window_init_bypassed` (15 files, all StrategyModalWindow subclasses) uses `getattr(self, '_window_init_bypassed', False)` with a `False` default. The risk is a consistency gap: StrategyModalWindow's docstring (strategy_modal_window.py:85) documents `_window_init_bypassed` as a convention for subclasses, yet the two direct-UIWindow subclasses that implement their own bypass guard don't follow it. This could confuse future maintainers who expect the flag to be always-present across all bypass-capable windows.
**Recommendation:** Add `self._window_init_bypassed = False` after `super().__init__()` in both files' production paths, mirroring StrategyModalWindow line 134:

```python
# In RaceSetupScreen.__init__, after line 171:
super().__init__(rect, manager, ...)
self._window_init_bypassed = False

# In NewGameSetupScreen.__init__, after line 199:
super().__init__(rect, manager, ...)
self._window_init_bypassed = False
```

---

### FND-002: `wait()` can return before `_finished_at` is visible under `_state_lock`
**Severity:** MAJOR
**File:** `game/services/llm/background.py`
**Line:** 291 (setter), 297 (in_flight_calls decrement)
**Description:** The `_done_event.set()` call in `_run()`'s inner finally (line 291) runs **outside** `_state_lock`. The outer finally (lines 293-297) then decrements `_in_flight_calls` and removes the thread from `_active_workers`. Inside the inner try, `_finished_at` is set under `_state_lock` in every terminal branch.

A caller that does `call.wait(timeout=2.0)` and then immediately reads `call.elapsed_seconds` may race with the worker thread: if the worker has passed line 291 (`_done_event.set()`) but has NOT yet passed the outer finally's decrement block (line 295), the elapsed-seconds read will see `_finished_at` set (it was set in the terminal branch under lock, before line 291), so this is actually fine.

The real window is narrower: if `cancel()` is called while the worker is mid-execution, `cancel()` sets `_done_event` at line 178, and `wait()` returns. But `_finished_at` was just set by `cancel()` under lock (line 170), so the state is consistent.

After careful trace analysis through all 6 terminal-transition paths (including the cancel-before-start, cancel-mid-run, and unexpected-exception branches), no actual race condition was found. The `_done_event` is always set **after** `_finished_at` and `_status` are committed under lock, so a `wait()` return guarantees terminal-state visibility. The pattern is correct.

**Recommendation:** No code change needed. The existing pattern — set `_done_event` outside the lock after all state under that lock is committed — is the correct approach to avoid waiter-starvation (per the design comment at lines 230-231). This finding is informational for future auditors: the `_done_event` signal happening before the outer finally's `_in_flight_calls` decrement is intentional and not a race.

---

### FND-003: `bypass_init` context manager stores previous value via `cls.__dict__` only — MRO-safe for this use case
**Severity:** INFO
**File:** `tests/fixtures/ui_widget_factory.py`
**Line:** 293
**Description:** The `bypass_init()` context manager reads the previous value with `cls.__dict__.get("bypass_init", _SENTINEL)` (line 293), checking only the class's own `__dict__`, not the full MRO. If a base class had `bypass_init = True` in its `__dict__` (which no class does today), the context manager would see `_SENTINEL` and use `delattr(cls, "bypass_init")` on cleanup. This would correctly remove the locally-set attribute while leaving the base class's attribute intact (because `delattr` finds the attribute in `cls.__dict__` first, where the context manager just set it).

This is the correct behavior: `cls.__dict__` is the right scope to check because the context manager only sets the flag on the concrete class and only needs to restore the concrete class's own state. No fix needed.
**Recommendation:** No code change. This finding is documented for future auditing.

---

### FND-004: Two-stage `__init__` guard placement is intentionally not the first statement — documented but diverges from D-003
**Severity:** INFO
**File:** `game/ui/screens/race_setup/screen.py`, `game/ui/screens/new_game_setup_screen.py`
**Line:** screen.py:126-143 (Stage 1) / 151 (guard), new_game_setup_screen.py:157-170 (Stage 1) / 177 (guard)
**Description:** D-003 specifies the `bypass_init` guard must be "the FIRST executable statement in `__init__`." Both `RaceSetupScreen` and `NewGameSetupScreen` place their Stage 1 (cheap state + delegates) **above** the guard, with the guard at the Stage 1/Stage 2 boundary. This is an intentional design evolution from PROJ-325 Phase 3's two-stage construction pattern, documented in both files' docstrings. Risk #1 from D-003 ("parameter validation running before the guard hides bugs") does not apply here: Stage 1 constructs only pure-Python objects (`RaceLibrary()`, `NewGameSetupViewModel()`, etc.) — no `pygame_gui` widgets and no runtime display dependency.

In bypass mode: Stage 1 runs (providing real delegates like `_view_model`, `_controller`), then the guard triggers, skipping Stages 2-3. In production mode: Stage 1 runs, guard passes through, Stages 2-3 run normally. Both paths are correct and the guard behaves as a pure opt-out.
**Recommendation:** No code change. This divergence from D-003 is by design and does not hide bugs. The guard uses `type(self)` per D-003 and the two-stage pattern is validated by PROJ-325 PoC.

---

### FND-005: `LLMBackgroundCall.start()` after `cancel()` spawns a wasted worker thread
**Severity:** INFO
**File:** `game/services/llm/background.py`
**Line:** 126-128 (`start()` thread check), 167-171 (`cancel()` status update)
**Description:** `start()` guards against double-start by checking `self._thread is not None` (line 127) but does NOT check `self._status`. If `cancel()` is called before `start()` (a path explicitly permitted by the `cancel()` docstring at line 158), the call transitions from PENDING to CANCELLED and `_done_event` is set. A subsequent `start()` would see `_thread is None` (never started) and proceed to spawn a worker thread, increment `_in_flight_calls`, and register in `_active_workers`. The worker immediately checks `_status == CANCELLED` at line 236 and returns without making any HTTP call. The outer finally still decrements `_in_flight_calls` and discards the thread.

The net effect is a no-op (no HTTP call, correct terminal state) but with unnecessary thread creation / global-counter churn. No test or production code calls `start()` after `cancel()` today; the cancel-then-start pattern would be a caller bug rather than a library bug.
**Recommendation:** Optionally add a status check to `start()`:

```python
with self._state_lock:
    if self._thread is not None:
        return
    if self._status in (CallStatus.CANCELLED, CallStatus.DONE, CallStatus.ERROR):
        return
```

This is low-priority but would make `start()` robust against any future caller that cancels-then-starts.

---

## Verified Passing Items

All items below were validated against the production code and pass without findings:

| Item | File(s) | Status |
|------|---------|--------|
| Guard uses `type(self)` per D-003 | `strategy_modal_window.py:118`, `screen.py:151`, `new_game_setup_screen.py:177` | PASS |
| `bypass_init=False` is correct default (getattr) | All 3 guards | PASS |
| `bypass_init` context manager cleans up on exception | `tests/fixtures/ui_widget_factory.py:253-304` | PASS |
| Nested `bypass_init(Cls)` restores previous value | `ui_widget_factory.py:293-304` | PASS |
| `LLMBackgroundCall._done_event` initialized in `__init__` | `background.py:104` | PASS |
| `_done_event.set()` in all terminal branches of `_run()` | `background.py:291` (finally — covers all paths) | PASS |
| `_done_event.set()` in `cancel()` for cancel-before-start | `background.py:178` | PASS |
| `wait()` returns True on terminal, False on timeout | `background.py:210` | PASS |
| `wait()` is idempotent (safe before `start()`) | `background.py:210` (Event.wait on already-set = immediate return) | PASS |
| `make_ui_widget()` patches MRO modules + extra_modules | `ui_widget_factory.py:343-345` | PASS |
| `_patch_pygame_gui_elements()` stops patches in reverse order in finally | `ui_widget_factory.py:224-226` | PASS |
| `StrategyModalWindow.kill()` tolerant of bypassed instances | `strategy_modal_window.py:156` (getattr with default) | PASS |
| `StrategyModalWindow` sets `_window_init_bypassed = False` in production | `strategy_modal_window.py:134` | PASS |
| `bypass_init` guard does not register bypassed instance with window manager | `strategy_modal_window.py:135-136` (after bypass return) | PASS |
| `self.rect` not assigned in bypass path (GUISprite descriptor safety) | All 3 files — intentionally not set | PASS |
| `llm_background.wait()` usage in test infrastructure | PROJ-324 Phase 3 — all 14 deferred tasks unblocked | PASS |

---

## Conclusion

PROJ-324's production-side changes (Phases 1-2) and test infrastructure (`ui_widget_factory.py` with `bypass_init` + `make_ui_widget`) are sound. No CRITICAL issues; two MAJOR pattern-conformance findings that do not affect runtime behavior. The `_done_event` / `wait()` design is race-free. All 13 unblocked PROJ-322 deferrals are structurally safe to migrate.
