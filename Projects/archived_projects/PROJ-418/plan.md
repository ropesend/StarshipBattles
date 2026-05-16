# PROJ-418: Legacy removal — to_roman wrapper (2026-05-13)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-418` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-418 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Inline 1 caller and delete to_roman wrapper | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-13
**Active Phase:** Phase 1
**Last Action:** Phase 1 complete — inlined caller at planet_naming.py:64, deleted to_roman wrapper, removed TestToRoman from test_planet_naming.py
**Next Action:** Audit ready
**Blockers:** None

## Overview
Inlines the single internal caller of the `to_roman()` wrapper in `game/strategy/data/planet_naming.py`, then deletes the 13-line wrapper function. The wrapper adds zero logic over `NameRegistry.to_roman()`.

Source: legacy audit `2026-05-13_194106_legacy-audit`, verified items in this bundle = 1.
Removal cluster: `to_roman_wrapper`.

### Notable callouts
_(no special callouts)_

## Goals
- Inline 1 caller and delete to_roman wrapper

## Scope
**In:** removal cluster `to_roman_wrapper` — items LEG-01-003.
**Out:** other clusters' contents (siblings: PROJ-413, PROJ-414, PROJ-415, PROJ-416, PROJ-417, PROJ-419, PROJ-420, PROJ-421); REJECTED and OUT_OF_SCOPE findings (none in this run; see `findings/verification_report.md`).

## Key Files
| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/strategy/data/planet_naming.py` | Production | Edit | Inline 1 caller at line 64; delete wrapper lines 16-28 |

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
