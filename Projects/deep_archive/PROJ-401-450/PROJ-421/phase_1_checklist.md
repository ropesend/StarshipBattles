# Phase 1: Remove redundant slot-nulls from _handle_window_close

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-421 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete the 7 redundant slot-nulling operations in `_handle_window_close` once it is confirmed that Pattern #31 auto-deregistration covers every window referenced. Verifier already confirmed no caller code reads the slots for None, but re-grep before removal as a safety check.

Severity tier: Major (in-place deletion; verify no callers read slots).

---

## Tasks

### Task 1.1: Confirm no slot-readers, then delete the 7 slot-nulls
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/ -k strategy_event_router && pytest tests/ -k strategy_window`

- [ ] Re-grep `event_router\.\w*_window is None`, `event_router\.\w*_dialog is None`, `window_manager\.\w*_window is None`, etc. across game/, tests/. Verify zero readers. Document the grep results in `findings/no_slot_readers.md` for the implementation PR.
- [ ] Confirm `strategy_modal_window.py:148-170` `kill()` still calls `wm.unregister_modal(self)` before `super().kill()` (Pattern #31 invariant)
- [ ] Delete the 7 slot-nulling lines in `_handle_window_close` (lines 436, 440, 442, 444, 452, 454, 456-460 per verifier; re-confirm exact lines at implementation time)
- [ ] Trim any dead helper code that existed only to support the slot-nulls
- [ ] Verify: `pytest tests/ -k strategy_event_router && pytest tests/ -k strategy_window` passes; `grep -n '_window = None\|_dialog = None' game/ui/screens/strategy_event_router.py` returns zero hits inside `_handle_window_close`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

---

_Source audit: `Reviews/results/2026-05-13_194106_legacy-audit/`. See `findings/source_audit.md` for the link._
