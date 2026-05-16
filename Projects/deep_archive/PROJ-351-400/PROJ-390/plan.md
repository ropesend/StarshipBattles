# PROJ-390: Legacy removal — log_event module-level compat shim retirement (2026-05-07)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-390` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-390 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Migrate ~12 callers + retire module-level shim | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Phase 1
**Last Action:** Phase 1 complete. Module-level `log_event` / `set_event_handler` / `get_event_handler` and the `_event_handler` global deleted from `game/core/event_logging.py`. Re-exports stripped from `game/core/__init__.py`. Projectile `_default_event_logger` rewritten as a no-op (PROJ-382's injectable `event_logger=` is the canonical path now). `conftest.py` cleanup hook removed. Obsolete `tests/unit/core/event_logging/test_event_logging.py` deleted. `docs/02_PATTERNS.md` §10 rewritten — "compatibility shim" sentence gone, constructor injection now documented as the only supported pattern.
**Next Action:** User verification + closeout commit
**Blockers:** None

## Overview
Retires the module-level `log_event()`, `set_event_handler()`, `get_event_handler()` functions at `game/core/event_logging.py:57-88`. These maintain a process-global `_event_handler` variable that bypasses session-scoped isolation. `docs/02_PATTERNS.md` §10 explicitly tags these as a "compatibility shim" with the directive: "new code should prefer explicit `EventBus` injection." Sonnet's third-pass verification: ~12 production callers across `game/`.

## Goals
- Migrate all production callers of `log_event()` to use an injected `EventBus` instance.
- Delete the module-level `log_event`, `set_event_handler`, `get_event_handler` functions and the `_event_handler` global.
- Update `docs/02_PATTERNS.md` §10 to remove the "compatibility shim" tag once the shim is gone.

## Scope
**In:** LEG-02-016 / LEG-03-021 (deduplicated — same finding from two shards).
**Out:** Other clusters from the same audit (siblings PROJ-383..PROJ-389, PROJ-391..PROJ-393); REJECTED and OUT_OF_SCOPE items recorded in [findings/verification_report.md](findings/verification_report.md) and the shared [findings/bundling_decisions.md](findings/bundling_decisions.md). Other singleton-pattern findings (LEG-04-014 `policy_manager`, LEG-04-015 `registry.py`) are excluded — user opted them out as a separate-project concern.

## Key Files
| Component | File Path |
|-----------|-----------|
| Production target | `game/core/event_logging.py` |
| Doc update | `docs/02_PATTERNS.md` §10 |
| Caller (representative) | `game/` (~12 sites — enumerated in Task 1.1) |

## Related Documents
- [design.md](design.md) — source audit, cluster identity, severity breakdown
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification of audit claims
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — interactive bundling record (shared across siblings)

## Verification
- [x] All phase checklists complete
- [x] All tests passing (focused: 41 event_logging/event_bus + 118 EventBus consumers + 226 projectile tests; full sharded suite to be re-run as final closeout)
- [x] No remaining module-level `log_event` / `set_event_handler` / `get_event_handler` callers in `game/`, `tests/`, `combat_lab/`, `Tools/` — only historical references in `_marked_for_deletion_2026-05-29/`, archived audits, and project-plan markdown remain.
- [x] No remaining process-global `_event_handler` in `event_logging.py`
- [ ] User verified
