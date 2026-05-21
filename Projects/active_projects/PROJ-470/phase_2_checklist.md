# Phase 2: Major - StrategyScreen.session, SettingsWindow, EventBus

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-470 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (Task 2.1 / FAC-003 deferred -> PROJ-472)
**Objective:** Resolve the three verified MAJOR findings from audit `2026-05-20_075227_pattern-audit`: the `StrategyScreen.session` read-path bypass (Pattern #5), `SettingsWindow` non-conformance with Pattern #31, and the `EventBus` stale-path/doc drift (Pattern #10).

---

## Tasks

### Task 2.1: Route StrategyScreen.session read-path consumers through the facade [Complex] — DEFERRED -> PROJ-472
**File:** `game/ui/screens/strategy_screen.py`
**Pattern:** #5 (Facade / Delegate)
**Status:** Deferred -> PROJ-472 Task 1.4

> **SCOPE REVISION 2026-05-20 (Protocol 06/07):** FAC-003 is part of the facade read-path
> migration program deferred to **PROJ-472**. It depends on the read-path policy + static guard
> (PROJ-472 Phase 1 Tasks 1.1/1.2) which do not exist under PROJ-470. Migrating these 4
> `.session.<x>` consumers without the policy/guard would be ad-hoc. Subtasks preserved below as
> historical context; do NOT implement under PROJ-470.

- [ ] (Deferred -> PROJ-472) Add facade accessor methods (registries / active_empire / turn / empires) so UI no longer reads `screen.session.<x>` directly (FAC-003; `strategy_screen.py:242-257`)
- [ ] (Deferred -> PROJ-472) Migrate consumer `game/ui/screens/strategy_detail_formatter.py:112` (`self.scene.session.registries`)
- [ ] (Deferred -> PROJ-472) Migrate consumer `game/ui/screens/strategy_detail_formatter.py:395-396` (`self.scene.session.turn_engine`)
- [ ] (Deferred -> PROJ-472) Migrate consumer `game/ui/screens/strategy_windows/list_windows.py:69` (`c.scene.session.empires`)
- [ ] (Deferred -> PROJ-472) Migrate consumer `game/ui/screens/hex_outlines.py:30` (`r.scene.session.active_empire.id`)
- [ ] (Deferred -> PROJ-472) Extend the read-path static guard to fail on new `.session.<read>` access from `game/ui/`

### Task 2.2: Convert SettingsWindow to StrategyModalWindow [Medium]
**File:** `game/ui/screens/settings_window.py`
**Pattern:** #31 (Strategy Modal Window Base Class)
**Tests:** `pytest tests/ -k settings` (write a failing modality test first)

- [x] Wrote failing modality tests: `tests/unit/ui/screens/test_settings_window_modal.py` (subclass, keyword-only window_manager, registration, kill-callback+deregister)
- [x] Changed `class SettingsWindow(UIWindow)` to subclass `StrategyModalWindow`; added keyword-only `window_manager`; two-stage init (Stage-1 cheap state, Stage-3 widgets guarded by `_window_init_bypassed`). `is_blocking=True` now comes from the base class on construction.
- [x] Kept the registrar `on_close_callback` for slot cleanup (invoked from `kill()` before `super().kill()`, which deregisters) — matches the `EmpirePanelWindow` convention.
- [x] Updated `SettingsRegistrar.open()` in `empire_panel_ctrl.py` to pass `window_manager=c`; updated `test_empire_panel_ctrl.py` assertion.
- [x] Verify: modality tests + registrar tests + full UI-screens suite green (3394 passed). Background hover/click block now inherited from `StrategyModalWindow.is_blocking`.

### Task 2.3: Fix the EventBus stale path and reconcile Pattern #10 doc [Simple]
**File:** `game/ui/screens/builder/event_bus.py`
**Pattern:** #10 (Event Bus)
**Tests:** `pytest tests/ -k event_bus`

- [x] Fixed stale docstring path at `event_bus.py:5` → `game/core/event_logging.py` (EVT-001). Confirmed `game/core/events/event_bus.py` does not exist; canonical `EventBus` is at `game/core/event_logging.py:40`.
- [x] Updated Pattern #10 in `docs/02_PATTERNS.md`: names `WorkshopEventBus` and `EventBus` explicitly, documents the two-bus divergence as INTENTIONAL (different domains, different payload contracts), and states no shared `EventBusProtocol` is planned.
- [x] Verify: no remaining production references to `game/core/events/event_bus.py` (only historical audit/project docs); doc + code agree. event_bus tests green (57 passed).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes checked (Task 2.1/FAC-003 deferred -> PROJ-472; 2.2/2.3 done)
- [x] Status set to `Complete`
- [x] plan.md phase table row updated
- [x] plan.md Current State updated

_Source audit: `Reviews/results/2026-05-20_075227_pattern-audit/`. See `findings/source_audit.md` for the link._
