# FEAT-20: Dev "Run 10 turns" button next to End Turn

## Description
Add a development button next to **End Turn** that automatically advances the
turn 10 times in a row. Each iteration runs the full end-turn flow for every
player (using whatever fleet orders / build queues are already configured)
until 10 turns have completed.

Purpose: faster iteration when testing economy / population / build queue
behaviour over multiple turns. Intended as a dev-time shortcut — to be
removed (or hidden behind a debug flag) before release.

Reproduced layout in QA Session 20260427_151244 at 15:52:

[![End Turn button location — Run 10 Turns belongs immediately to its right](../../../tools/qa_observer/session_data/20260427_151244/images/bug_capture_155251.png)](../../../tools/qa_observer/session_data/20260427_151244/images/bug_capture_155251.png)

## Required changes
- Strategy UI top bar — add "Run 10 Turns" button immediately next to "End
  Turn" (likely in `game/ui/screens/strategy_*` or
  `game/ui/screens/strategy_window_manager.py`).
- Click handler — calls the existing end-turn pipeline 10 times in sequence.
  No animations / pauses between turns; spinner or progress indicator while
  running.
- **Gate the button behind a dev flag** so it's easy to hide in builds. A
  config switch or a debug-mode environment variable is fine.
- Cancel/abort affordance — long sequences shouldn't lock the UI; allow Esc
  or a Cancel modal to stop after the current turn finishes.

## Acceptance
- Button is visible next to End Turn while in dev mode.
- Clicking advances the simulation 10 turns; UI updates between/after.
- A cancellation path stops cleanly without corrupting the save.

## Out of scope
- Configurable turn count (10 is fine for dev needs).
- Replaying or recording the run.

## Priority
Low

## Status
In-Progress (revised scope per QA Session 20260428_190154 — see User Update below)

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
- 2026-04-27: Investigation complete (`.agent_reports/deep-dive-session/investigations/FEAT-20_investigation.md`). Pipeline confirmed fully synchronous; no threading required.
- 2026-04-27: Implemented (TDD). Added `--dev` CLI flag → `BootstrapResult.dev_mode` → `ScreenRouter` → `StrategyScreen` → `StrategyUI` → `create_strategy_panels(..., dev_mode=)`. New `btn_run_10_turns` rendered at top-bar slot 10 immediately right of "End Turn" only when `dev_mode=True`. Click handler routes to `StrategyScreen.run_n_turns(10)` → `StrategyGameStateManager.run_n_turns(n)`, which loops `process_full_turn()` (renamed public from `_process_full_turn`) n times. Esc-cancellation between iterations via new `_pump_cancel_events()` (consumes only `KEYDOWN`/`QUIT`, leaves other events for the main loop). Auto-save runs at end of each turn (atomic-per-turn → cancel never corrupts saves). Per-turn event-log auto-open is suppressed during the loop via a `_suppress_event_log` flag and a single combined log opens at the end if any events occurred. Overlay text parametrised: dev runs see "PROCESSING TURN 3 / 10... (Esc to cancel)" via new `turn_processing_message` field on `StrategyScreen`.

### Files modified
- `game/app_bootstrap.py` — `--dev` CLI flag, `BootstrapResult.dev_mode: bool = False`, propagation in `bootstrap()`.
- `game/screen_router.py` — store `boot.dev_mode`, pass into all 4 `StrategyScreen(...)` construction sites.
- `game/ui/screens/strategy_screen.py` — `dev_mode` kwarg, `dev_run_cancel_requested` + `turn_processing_message` state, `run_n_turns()` delegate, draw-overlay message-arg plumbing.
- `game/ui/screens/strategy_ui.py` — `dev_mode` kwarg forwarded to panel manager.
- `game/ui/screens/strategy_panel_manager.py` — `btn_run_10_turns` field on `StrategyWidgets`, `dev_mode` kwarg on `create_strategy_panels`, conditional button at top-bar slot 10.
- `game/ui/screens/strategy_input_handler.py` — click-handler branch with `is not None` guard.
- `game/ui/screens/strategy_game_state_manager.py` — renamed `_process_full_turn` → public `process_full_turn` (returns `list` of events), added `run_n_turns()` and `_pump_cancel_events()`, `_suppress_event_log` flag.
- `game/ui/screens/strategy_renderer.py` — `draw_processing_overlay(screen, message)` accepts custom message.
- `game/ui/screens/strategy_render/overlay.py` — `draw_processing_overlay(..., message=...)` parameter.
- `docs/03_CONVENTIONS.md` — new §10 "Dev-Mode CLI Flag" documenting the convention.
- Tests: `tests/unit/test_app_bootstrap_invariants.py` (+2 dev-flag tests), `tests/unit/ui/screens/test_strategy_panel_manager.py` (NEW: 4 tests), `tests/unit/ui/screens/test_strategy_game_state_manager.py` (+7 tests for `run_n_turns` and renaming), `tests/unit/ui/screens/test_strategy_input_handler_core.py` (+2 tests for button routing), `tests/unit/ui/screens/test_strategy_screen.py` (updated 1 test for new draw-overlay signature).

### Decisions
- Dev-only widgets are absent in production (not greyed-out) to keep the top bar clean.
- Esc-only cancellation; no Cancel modal (overlay text reads "(Esc to cancel)").
- Cancellation is between-iteration only — never mid-turn — because each `process_full_turn()` ends with auto-save.
- Per-turn event-log auto-open is suppressed during the loop; a single combined log surfaces at the end. Avoids 10x modal popup on every dev run.
- `process_full_turn()` now returns `list[event]` (the per-turn events) so `run_n_turns` can aggregate them. Callers ignoring the return value are unaffected.
- Hardcoded `n=10` in the click handler; underlying method takes `n` for future variants.

### Test results
- Targeted (FEAT-20 + adjacent): 279 passed (`tests/unit/test_app_bootstrap_invariants.py` + all `tests/unit/ui/screens/test_strategy_*.py`).
- Broader UI sweep: 3607 passed (`tests/unit/ui/`).

---

### 📝 User Update [2026-04-28 19:12]

**Reason:** The button should appear unconditionally — not gated behind
`--dev`. The user reports running the game without `--dev` and not seeing
the button, which is the intended FEAT-20 design but is no longer the
desired behaviour.

QA Session 20260428_190154 [19:12:50 – 19:13:11]:

> "I want to change the 'Run 10 turns' button — I just want it to show
> up all the time. Will remove it later but I don't want it to be in the
> special dev mode that you have to run. Feature 20 — I want to update
> that."

**New scope:**

1. Remove the `--dev` CLI flag dependency from the button-render path:
   - `BootstrapResult.dev_mode` no longer gates the button (the field
     can stay if other dev-only widgets land later, or be deleted if
     this was its only consumer — decide during implementation).
   - `create_strategy_panels(...)` always renders `btn_run_10_turns`
     at top-bar slot 10.
   - `StrategyInputHandler` click branch always routes to
     `run_n_turns(10)`.
2. Decide what to do with the `--dev` plumbing if FEAT-20 was its only
   consumer. Per CLAUDE.md System Migration Policy ("ERADICATE the
   old system"), if no other dev-mode-gated widget exists, delete the
   `--dev` flag, the `BootstrapResult.dev_mode` field, and the
   propagation through `ScreenRouter` / `StrategyScreen` /
   `StrategyUI` / `create_strategy_panels`. Otherwise, leave the flag
   in place but FEAT-20 stops consuming it.
3. Update tests accordingly:
   - `test_app_bootstrap_invariants.py` dev-flag tests — delete or
     repurpose depending on (2).
   - `test_strategy_panel_manager.py` — remove the `dev_mode=False`
     branch's "no button" assertion; assert button always renders.
4. Status flips from `Awaiting Confirmation` back to `In-Progress`
   once an agent picks this up.

**No re-rejection of the original implementation** — the
synchronous-loop, Esc-cancel, per-turn auto-save behaviour is all
correct. Only the visibility gate changes.

---
