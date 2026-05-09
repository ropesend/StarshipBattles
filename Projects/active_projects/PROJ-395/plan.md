# PROJ-395: PROJ-381 remediation — review CRITICAL + MAJOR findings

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-395` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-395 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. CRITICAL — B-5 modal, registry exception, test assertions | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. MAJOR — 14 follow-up findings | Complete (12 closed, 2 deferred) | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Closeout
**Last Action:** Phase 1 (3 CRIT) + Phase 2 (12 of 14 MAJOR) closed across commits 59ee0442e + 793f592e0. MAJ-013 (EventBus shim) and MAJ-014 (defensive EnginePhaseError catch) deferred — see commit messages.
**Next Action:** Final closeout commit + user verification of focused tests.
**Blockers:** None

## Overview
PROJ-381 (error-handling cleanup, 27 audit items) shipped end-to-end across 3 phases. OpenCode's review (`Reviews/results/2026-05-08_230318_code_proj-381-error-handling-cleanup-strategy-ui-assets_req-req_20260508_230317_779973/`) flagged 3 CRITICAL findings that genuinely need addressing and 14 MAJOR follow-ups. This project closes the CRITICAL items in Phase 1 and the MAJORs in Phase 2.

## Goals
### Phase 1 (CRITICAL)
- **CRIT-001:** Replace raw `pygame_gui.windows.UIMessageWindow` in `_show_turn_failed_dialog()` with a `TurnFailedDialog` subclass of `StrategyModalWindow` (Pattern #31). The current implementation bypasses modal tracking — players can advance the turn while the error dialog is visible.
- **CRIT-002:** Replace bare `ValueError` at `game/strategy/engine/commands/registry.py:191` with `ValidationException(code=ErrorCode.DUPLICATE_COMMAND.value, context={...})`. Callers catching `ValidationException` from registration won't catch the bare form.
- **CRIT-003:** Add `code` and `context` assertions to 3 `ValidationException` tests in `tests/unit/strategy/test_command_handlers.py:551-620`. Pattern matches `tests/unit/strategy/engine/test_base_command_handler.py`.

### Phase 2 (MAJOR — 14 items)
See [findings/source_review.md](findings/source_review.md) for the full per-item plan.

## Scope
**In:** Findings from `Reviews/results/2026-05-08_230318_code_proj-381-error-handling-cleanup-strategy-ui-assets_req-req_20260508_230317_779973/report.md` rated CRITICAL or MAJOR.

**Out:** MINOR (18) and INFO (7) findings — captured for future cleanup but not in this remediation pass.

## Key Files
| Component | File Path |
|-----------|-----------|
| B-5 modal dialog | `game/ui/screens/strategy_game_state_manager.py` |
| `TurnFailedDialog` (new) | `game/ui/screens/turn_failed_dialog.py` (TBD path) |
| Registry exception | `game/strategy/engine/commands/registry.py` |
| Test assertions | `tests/unit/strategy/test_command_handlers.py` |
| Pattern #31 base | `game/ui/screens/strategy_modal_window.py` |

## Related Documents
- [design.md](design.md) — review summary + remediation strategy
- [decisions.md](decisions.md) — full decisions log
- [findings/source_review.md](findings/source_review.md) — pointer to OpenCode review

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (especially the new B-5 dialog regression test from PROJ-381 still passes with the new modal class)
- [ ] User verified

_Source review: `Reviews/results/2026-05-08_230318_code_proj-381-error-handling-cleanup-strategy-ui-assets_req-req_20260508_230317_779973/`_
