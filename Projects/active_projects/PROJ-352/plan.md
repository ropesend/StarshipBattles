# PROJ-352: Closeout follow-up - UI cleanup (T6.6 Strategy load dialog modal tracking + T4.7 NewGameSetup builder docstring)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-352` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. T4.7 — NewGameSetup builder docstring fix (small) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. T6.6 — Strategy load dialog modal tracking (project-shaped) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Awaiting Verification
**Last Action:** Phase 2 (T6.6) Shape A migration landed — `SaveSelectionWindow` now subclasses `StrategyModalWindow`; `strategy_screen_lifecycle.show_load_game_dialog` passes `screen.ui.window_manager`; new regression test pins live-list participation. Full unit suite (15767 passed, 2 skipped) + lint clean.
**Next Action:** User manual smoke per Verification checklist — open load dialog mid-strategy-screen, confirm hex/sidebar input is blocked while the dialog is alive.
**Blockers:** None
**Context for Next Agent:** Both items deferred from earlier sprints per Codex review consensus (`AgentCoordination/Scratchpad/Discussion/20260505T020232Z_proj343-349-codex-review/plans/proj343_349_remaining_plan_r003.md`). T4.7 docstring fix landed first; T6.6 picked Shape A (migrate to `StrategyModalWindow`) per `decisions.md` rationale.

## Overview

Two UI-layer follow-ups deferred from earlier closeout sprints. T4.7 is the smaller and lands first as a confidence-builder. T6.6 is the substantive item: the strategy load dialog isn't tracked as a blocking modal, so it can coexist with strategy-screen input/scroll in ways other modal windows can't.

## Goals

- T4.7: `new_game_setup_screen.py` docstring at lines 20-28 corrected. Currently the comment claims the builder "owns the widget tree"; in fact `build()` is a one-line passthrough to `screen._create_ui()` (per Codex r003 plan). Codex's correction (vs. the original synthesis): KEEP the builder seam (Pattern §33-compliant test-substitution surface), just fix the docstring. Optional incremental widget extraction is low-priority polish, NOT this project's scope unless explicitly time-permits.
- T6.6: `show_load_game_dialog()` at `strategy_screen_lifecycle.py:64-77` creates a raw `SaveSelectionWindow` and discards the instance. `SaveSelectionWindow` subclasses raw `pygame_gui.elements.UIWindow`. Strategy modal detection at `strategy_event_router.py:47-73` only checks menu/build queue and `StrategyWindowManager.iter_live_modals()`; the load dialog isn't in either. Retrofit: register the load dialog with `StrategyWindowManager` (add a slot per `:122-143`) OR migrate `SaveSelectionWindow` to `StrategyModalWindow` so the existing modal plumbing tracks it.

## Scope

**In (T4.7):**
- `game/ui/screens/new_game_setup_screen.py:20-28` — docstring fix.

**In (T6.6):**
- `game/ui/screens/strategy_screen_lifecycle.py:64-77` — `show_load_game_dialog` instance lifecycle.
- `game/ui/screens/save_selection_window.py:96-100` — possibly migrate to `StrategyModalWindow`.
- `game/ui/screens/strategy_window_manager.py:122-143` — possibly add a load-dialog slot.
- `game/ui/screens/strategy_event_router.py:47-73` — modal detection includes the load dialog.
- New regression test asserting load dialog blocks strategy input.

**Out:**
- Wider modal-management refactor.
- Migrating other dialogs to `StrategyModalWindow` (only `SaveSelectionWindow` is in scope here unless the slot-only approach is chosen).
- The "incremental widget extraction" Codex mentioned for NewGameSetup — explicitly NOT in this project.

## Key Files

| Component | File Path |
|-----------|-----------|
| T4.7 | `game/ui/screens/new_game_setup_screen.py:20-28` |
| T4.7 reference | `game/ui/screens/new_game_setup_ui_builder.py:37-38` (build() passthrough) |
| T6.6 dialog show | `game/ui/screens/strategy_screen_lifecycle.py:64-77` |
| T6.6 dialog class | `game/ui/screens/save_selection_window.py:96-100` |
| T6.6 modal manager | `game/ui/screens/strategy_window_manager.py:122-143` |
| T6.6 modal detection | `game/ui/screens/strategy_event_router.py:47-73` |
| T6.6 reference modal | `game/ui/screens/strategy_modal_window.py` (the base class to migrate to or the slot pattern to follow) |

## Related Documents

- [design.md](design.md) — context analysis
- [decisions.md](decisions.md) — decisions log
- [manifest.md](manifest.md) — file manifest
- Codex review consensus: `AgentCoordination/Scratchpad/Discussion/20260505T020232Z_proj343-349-codex-review/plans/proj343_349_remaining_plan_r003.md`

## Verification

- [ ] All phase checklists complete
- [ ] `pytest tests/unit/ui/screens/ -x -q` — all pass
- [ ] Manual smoke (T6.6): open load dialog mid-strategy-screen, confirm strategy input is blocked while dialog is alive
- [ ] `python Tools/lint_test_files.py` — 0 violations
- [ ] User verified
