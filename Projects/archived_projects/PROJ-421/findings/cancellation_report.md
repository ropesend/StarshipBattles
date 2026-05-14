# PROJ-421 Cancellation Report

**Cancelled:** 2026-05-13
**Reason:** Load-bearing premise invalidated by codex consult.

---

## What the project was supposed to do

Remove 7 slot-nulling operations from `_handle_window_close` in
`game/ui/screens/strategy_event_router.py:427-460`, framed as "Pattern #31
auto-deregistration already handles cleanup, so the slot-nulls are redundant."

## Why it was cancelled

The third-pass verifier (in this skill's Phase C) made an explicit claim that
"no caller code reads the slots for None." That claim was the **sole**
justification for the user-included reframing of LEG-02-001 out of the
UNCERTAIN bucket. A subsequent codex consult re-grepped and found the claim
false. The cleanup is unsafe as planned.

### Evidence of slot-readers found by the consult

| File | Line | Pattern |
|------|------|---------|
| `game/ui/screens/strategy_event_router.py` | 103-104 | `if wm.fleet_orders_window:` truthiness check |
| `game/ui/screens/strategy_screen_selection.py` | 52-53 | `if wm.transfer_dialog:` truthiness check |
| `game/ui/screens/strategy_screen_order_editing.py` | 73-74 | `if wm.fleet_orders_window:` rebuild guard |
| `game/ui/screens/strategy_input_handler.py` | 70-71 | explicit `if wm.planet_list_window is not None:` |
| `game/ui/screens/strategy_window_manager.py` | 231-259 | `iter_snapshot_windows()` builds `slot_candidates` and checks `w is None` before yielding |
| `game/ui/screens/strategy_windows/build_queue_windows.py` | — | registrar controller reads named slot for kill-before-reopen |
| `game/ui/screens/strategy_windows/fleet_report_ctrl.py` | — | same pattern |
| `game/ui/screens/strategy_windows/transfer_dialogs.py` | — | same pattern |
| `game/ui/screens/strategy_windows/orders_window_ctrl.py` | — | same pattern |
| `game/ui/screens/strategy_windows/event_log_window_ctrl.py` | — | same pattern |
| `game/ui/screens/strategy_windows/empire_panel_ctrl.py` | — | same pattern |
| `game/ui/screens/strategy_windows/list_windows.py` | — | same pattern |

### Compound problem

`pygame_gui.UIWindow` has no `__bool__` or `__len__`. A killed window remains
truthy (its instance is still a non-empty object). If the slot-null is
removed, `if wm.fleet_orders_window:` would call `handle_global_event()` on a
dead window after close. Pattern #31 auto-deregistration removes the window
from the `_modals` list but does **not** null the named slot fields.

### Test contract

`tests/unit/ui/screens/test_strategy_window_manager_public_api.py:300-373`
parameterises every router slot and explicitly asserts each becomes `None`
after a close event. Removing any `= None` branch from the router would fail
that test contract without first rewriting the test — and rewriting the test
would require already having the production behaviour change in hand, which
this project's premise made unsafe.

### Count

The verifier said 7 slot-nulls; the actual count is 9 bare `= None`
assignments in `_handle_window_close`. Two of those (`build_queue_list_window`,
`fleet_report_window`) have an independent registrar-callback nulling path
inside the window's own `kill()`; the other 7 do not. The other 7 are
load-bearing sentinel cleanups, not legacy.

## Audit history of LEG-02-001

This finding has now been invalidated **three times**:

1. **Audit Phase 1 scan (Shard 02)** classified it as MAJOR with the rationale
   "8 non-modal slots need migration."
2. **The audit's own internal verifier** caught the "8 non-modal" claim as
   **FATAL ANALYSIS ERROR** — all 9 referenced windows ARE `StrategyModalWindow`
   subclasses. But it kept the core "redundant slot-nulling" observation as
   plausible.
3. **The third-pass verifier (in this skill)** added "no caller reads slots
   for None" and reframed the finding as actionable.
4. **The codex consult** disproved the no-readers claim with 12+ live sites.

Net: there is no legacy here. The slot-null pattern is the project's actual
"is window open?" sentinel mechanism for windows whose lifecycle is owned by
`strategy_event_router` rather than by their own registrar controller.

## Possible future projects

Two narrower follow-ups exist but are not opened by this cancellation:

1. **Rescope to the 2 callback-backed slots only.** `build_queue_list_window`
   and `fleet_report_window` have independent registrar-callback nulling.
   Removing those 2 `= None` branches from the router would be a small TDD
   project (rewrite the corresponding parameterised test cases first, prove the
   slot still clears via the controller path, then remove).
2. **Reframe as an API change.** Introduce `wm.is_window_active(<name>)` or
   `wm.has_<name>()` predicates, migrate the 4+ reader sites off slot-null
   sentinels, then the slot-nulls become genuinely removable. This is an API
   change project, not a legacy cleanup, and it is substantially larger.

Neither follow-up is opened automatically. The user can open one explicitly
via `/claude-proj-start` if desired.

## What this implies for the audit / verifier pipeline

The third-pass verifier (Phase C of `/claude-proj-from-legacy-audit`) needs
its slot-coverage analysis hardened. Specifically:

- When a finding hinges on "no caller reads X for None / for truthy", the
  verifier must grep for `if X is None`, `if not X`, `if X:`, AND build a
  list of unique reader sites — and a one-line evidence sentence per site.
  This run's verifier wrote "no readers" without enumeration, and the claim
  was false.
- Findings that survived a prior verifier rewrite (LEG-02-001 was already on
  its second framing when it entered Phase C) should get extra skepticism.
  Two consecutive failed verification framings is a strong signal the
  observation isn't actually legacy.

This is fed back to `ocode-legacy-audit` via the existing refinement proposal
at `.opencode/skills/ocode-legacy-audit/refinement_proposals/2026-05-13_2026-05-13_194106_legacy-audit.md`,
amended to note the cancellation.
