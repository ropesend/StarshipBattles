# PROJ-421: Legacy removal — Pattern #30 slot cleanup in strategy_event_router (2026-05-13) — **CANCELLED**

> **🚫 CANCELLED 2026-05-13**
>
> This project was cancelled after a codex consult (see
> `AgentCoordination/Scratchpad/Consult/20260514T035631Z_proj-421_legacy_review/response.md`)
> proved the load-bearing premise wrong: the third-pass verifier's claim that
> "no caller code reads the slots for None" is incorrect. Independent grep
> finds 6+ production callers that read the slot fields as
> "is-this-window-open?" sentinels (`strategy_event_router.py:103-104`,
> `strategy_screen_selection.py:52-53`, `strategy_screen_order_editing.py:73-74`,
> `strategy_input_handler.py:70-71`, `strategy_window_manager.py:231-259`, and
> 7+ registrar controllers). Killed `pygame_gui.UIWindow` objects have no
> `__bool__` and stay truthy, so removing the slot-nulls would cause method
> calls on dead windows in production.
>
> The slot-nulls are load-bearing sentinel cleanups, not legacy.
> LEG-02-001 is **dropped entirely** — neither the audit's original framing
> ("migrate 8 non-modal slots") nor the verifier's reframing ("remove
> redundant slot-nulls") survives skeptical review. The audit's own internal
> verifier had already flagged the original framing as a "FATAL ANALYSIS
> ERROR"; the third-pass verifier replaced one wrong premise with another.
>
> Two narrower follow-ups are possible but not opened in this run:
> 1. Rescope to the 2 slots (`build_queue_list_window`, `fleet_report_window`)
>    that have independent registrar-callback nulling — small TDD project.
> 2. Expose `is_window_active()` predicates and migrate the 4+ reader sites
>    off slot-null sentinels — different (larger) project, not a legacy cleanup.
>
> See `findings/cancellation_report.md` for the full reasoning and evidence.

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Remove redundant slot-nulls from _handle_window_close | **Cancelled** | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-13
**Active Phase:** **Cancelled**
**Last Action:** Cancelled after codex consult revealed unsafe premise (see findings/cancellation_report.md)
**Next Action:** None — project closed without implementation
**Blockers:** Premise invalidated

## Overview
Removes the 7 redundant slot-nulling operations in `game/ui/screens/strategy_event_router.py::_handle_window_close` (lines 427-460). All 9 windows are `StrategyModalWindow` subclasses; Pattern #31 auto-deregistration on `kill()` already handles cleanup, and no caller code reads the slots for None. Audit's original 'migrate 8 non-modal slots' framing was fabricated — verifier rewrote it as a redundant-cleanup removal.

Source: legacy audit `2026-05-13_194106_legacy-audit`, verified items in this bundle = 1.
Removal cluster: `pattern30_slot_cleanup`.

### Notable callouts
- ⓘ Reframes LEG-02-001 from the audit's fabricated 'migrate 8 non-modal slots' framing to the verifier-confirmed 'remove redundant slot-nulls'.

## Goals
- Remove redundant slot-nulls from _handle_window_close

## Scope
**In:** removal cluster `pattern30_slot_cleanup` — items LEG-02-001.
**Out:** other clusters' contents (siblings: PROJ-413, PROJ-414, PROJ-415, PROJ-416, PROJ-417, PROJ-418, PROJ-419, PROJ-420); REJECTED and OUT_OF_SCOPE findings (none in this run; see `findings/verification_report.md`).

## Key Files
| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/ui/screens/strategy_event_router.py` | Production | Edit | Delete 7 redundant slot-nulls in _handle_window_close (lines 427-460) |

## Related Documents
- [design.md](design.md) — architecture analysis and design rationale
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification output
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — Phase D interactive bundling record

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
