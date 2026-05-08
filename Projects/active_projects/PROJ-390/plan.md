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
| 1. Migrate ~12 callers + retire module-level shim | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-07_220621_legacy-audit` after independent verification
**Next Action:** Begin Phase 1 tasks
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
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] No remaining module-level `log_event` / `set_event_handler` / `get_event_handler` callers (`grep -rn -E "from game.core.event_logging import (log_event|set_event_handler|get_event_handler)" .`)
- [ ] No remaining process-global `_event_handler` in `event_logging.py`
- [ ] User verified
