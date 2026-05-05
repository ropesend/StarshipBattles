# PROJ-313: Strategy Modal Window Base Class Refactor

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-313` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-313 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation (base class + manager methods) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Router OR-bridge | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate event-listener-only windows (6) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate dual-cleanup windows (3) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Migrate registrar-callback-only windows (5) | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Promote move_choice_window | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Migrate untracked editor windows (5) | Complete | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Demolition + docs | Complete (legacy slots kept as caller-convenience; modal-tracking fully migrated) | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State
**Last Updated:** 2026-04-28
**Active Phase:** All 8 phases complete — ready for user smoke verification
**Last Action:** PROJ-316 remediation updated this execution record, corrected Pattern #31, replaced the weak Phase 7 editor regression test, and tightened strategy-screen-only modal constructors so `window_manager` is explicit.
**Next Action:** User smoke-test — open and close every modal window on the strategy screen, confirm clicks no longer leak through (Phase 7 fix for the QA-reported food allocation bug), confirm BUG-121 mouse-wheel zoom still works after closing planet abilities window.
**Blockers:** None
**Scope deviation:** Plan called for full demolition of the legacy slot fields, `_handle_window_close`, and `TestModalSlotCleanupContract` in Phase 8. These remain as caller-convenience slot cleanup infrastructure because they are still used by `strategy_screen.rebuild_list()`, `strategy_event_router.handle_global_event()` forwarding, and the registrars' "kill before re-open" idioms. Removing them would require a separate caller refactor. The structural modal-tracking fix is complete via `StrategyModalWindow` and `iter_live_modals()`; Pattern #31 documents this explicitly under "Migration notes (legacy slot fields)".
**Test baseline:** 15998 passed, 0 failed, 0 errors via `python Tools/test_sharded/test_sharded.py` at PROJ-316 kickoff. Recorded 2026-04-28.
**Context for next agent:**
- 20 strategy modal windows now subclass `StrategyModalWindow` (auto-registered/deregistered via `iter_live_modals()`).
- Pattern #31 in `docs/02_PATTERNS.md` documents the new contract; Pattern #30 is marked superseded.
- pygame_gui's `UIWindow.kill()` is the universal funnel — every kill path (programmatic, `[X]` button, parent kill) routes through it. The new base class deregisters in `kill()` *before* `super().kill()`.

## Overview
Replace the manual 6-step modal-tracking contract on the strategy screen
with a structural one via a `StrategyModalWindow(UIWindow)` base class.
Auto-register on `__init__`, auto-deregister on `kill()`. The 16 manual
slot fields on `StrategyWindowManager` no longer provide the modal-tracking
contract. Strategy modal tracking now walks a single live list, while
legacy slots remain for caller-convenience cleanup. New modal windows can
no longer forget the dance because the dance is in the base class.

## Goals
- Eradicate the recurring click-through / stale-flag-leak bug class
  (BUG-22, BUG-69, BUG-121, BUG-122-foodallocation) structurally.
- Migrate all 20 strategy-modal windows (15 already-tracked + 5 untracked
  editors) to subclass `StrategyModalWindow`.
- Delete `_handle_window_close` event listener and the asymmetric
  `is not None` vs `.alive()` check. [deferred — see Current State scope deviation]
- Replace the false-negative-prone `TestModalSlotCleanupContract` test
  with a structural-invariant behavioural test. [partially deferred — new structural tests added at tests/unit/ui/screens/test_strategy_modal_window.py and tests/integration/ui/test_editor_click_blocking.py; legacy test retained as regression for the still-active slot-cleanup pathway]
- Update `docs/02_PATTERNS.md` to retire Pattern #30 and document the
  new contract; update `docs/06_UI_STYLE_GUIDE.md` and
  `docs/01_ARCHITECTURE.md`.

## Scope

**In:**
- New `StrategyModalWindow` base class.
- `StrategyWindowManager` API: `register_modal`, `unregister_modal`,
  `iter_live_modals`. Legacy slot fields retained as caller-convenience cleanup pointers.
- `StrategyEventRouter`: collapse `has_modal_open` and
  `_is_blocking_ui_element_at` to modal-list checks for strategy modals;
  retain non-modal checks and `_handle_window_close` for slot cleanup.
- All 16 currently-tracked strategy modal windows.
- All 5 currently-untracked editor windows that cause click-through.
- `move_choice_window` inline construction promoted to a named subclass.
- Test contract replacement.
- Documentation updates.

**Out:**
- `settings_window` — stays as a direct non-modal slot field (the only
  intentionally non-modal window).
- `_pending_confirmation_dialog` asymmetry — pre-existing latent issue,
  filed as a separate ticket.
- Z-order-aware modal-stack semantics (insertion-order is correct under
  current any-True / any-hit semantics; future "topmost wins" features
  must add z-order awareness explicitly).
- Threading concerns (pygame_gui is single-threaded).
- New windows beyond the 21 inventoried.

## Key Files
| Component | File Path | Notes |
|-----------|-----------|-------|
| Base class (NEW) | `game/ui/screens/strategy_modal_window.py` | `StrategyModalWindow(UIWindow)` |
| Window manager | `game/ui/screens/strategy_window_manager.py` | Add modal list + 3 methods; legacy slots retained for cleanup |
| Event router | `game/ui/screens/strategy_event_router.py` | Modal tracking via `iter_live_modals`; legacy close listener retained |
| Migrating windows (15 tracked + 5 untracked = 20 total) | various | See [findings/strategy_modal_window_base_class.md](findings/strategy_modal_window_base_class.md) for the inventory table |
| Contract tests | `tests/unit/ui/screens/test_strategy_window_manager_public_api.py`, `tests/unit/ui/screens/test_strategy_modal_window.py`, `tests/integration/ui/test_editor_click_blocking.py` | Legacy slot cleanup test retained; structural/modal editor tests added |
| Pattern doc | `docs/02_PATTERNS.md` | §30 retired, replaced by structural base class pattern |
| UI style guide | `docs/06_UI_STYLE_GUIDE.md` | New "Window Management" section |
| Architecture doc | `docs/01_ARCHITECTURE.md` | UI layer note |
| Triage findings | `findings/strategy_modal_window_base_class.md` | Original triage doc with full audit |

## Related Documents
- [design.md](design.md) — Architecture analysis, swarm findings, design rationale
- [decisions.md](decisions.md) — Full decisions log
- [manifest.md](manifest.md) — Per-file change inventory
- [findings/strategy_modal_window_base_class.md](findings/strategy_modal_window_base_class.md) — Origin triage with full window inventory

## Verification

### Project Start (REQUIRED)
- [x] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [x] Run full test suite: `python Tools/test_sharded/test_sharded.py` — 15893/15893 passed (baseline established 2026-04-28)

### After Each Phase
- [ ] Run `pytest tests/unit/ui/screens/ tests/unit/ui/` (incremental, fast)
- [ ] Manual smoke: open and close at least one window per phase, confirm `has_modal_open()` returns False after close (instrument with debug log if needed)
- [ ] Verify 15893 baseline preserved (Phases 7 and 8 adjust this — see phase notes)

### Final Verification (after Phase 8)
- [ ] Open every modal in turn (planet list, fleet orders, fleet report, event log, empire panel, transfer dialog, cargo quick dialog, build queue, planet abilities, planet/system/fleet selection, move choice, food allocation, atmosphere/gravity/water/radiation editors)
- [ ] For each: while open, click on the strategy map underneath at a different planet/sector — confirm map selection did not change
- [ ] Close each via title-bar `[X]` and via in-window Cancel/Apply button — confirm `has_modal_open()` returns False immediately
- [ ] Open and close any modal 5+ times consecutively — confirm strategy-screen mouse-wheel zoom continues to work (BUG-121 regression smoke)
- [ ] Multi-modal scenario: open Empire Panel, then Settings from within it — confirm both layer correctly and Settings closes back to Empire Panel without breaking event routing
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` (NOT --testmon, full verification)
- [ ] Verify changes consistent with `docs/` — `Last verified:` blockquote bumped on `02_PATTERNS.md`, `06_UI_STYLE_GUIDE.md`, `01_ARCHITECTURE.md`

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 |  |  |  |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All Phase 6 tasks checked off
- [ ] All Phase 7 tasks checked off
- [ ] All Phase 8 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing (BUG-121 mouse-wheel zoom smoke)
- [ ] Audit passed (no significant issues)
- [ ] User verified
