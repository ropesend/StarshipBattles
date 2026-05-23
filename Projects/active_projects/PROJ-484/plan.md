# PROJ-484: Legacy removal — dead re-export sweep (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-484` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-484 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Zero-call-site deletions | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Single-test-caller deletions | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-22
**Active Phase:** Phase 1
**Last Action:** Project created from `Reviews/results/2026-05-20_210635_legacy-audit/` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Four dead re-export / unused-import lines flagged by the 2026-05-20 legacy audit and independently re-verified. The cluster targets the "legacy import-path preservation" pattern in `combat_events.py`, `ship.py`, and `image/__init__.py`. Two items have zero callers (single-PR deletion) and two have exactly one test-file caller each.

## Goals
- Phase 1: Delete two zero-call-site re-exports / unused imports as a single quick-PR sweep.
- Phase 2: Update the two single-test-caller imports to the canonical path, then delete the re-export lines.

## Scope
**In:** dead re-exports / unused side-effect imports verified against current source.
**Out:**
- Documented Pattern #36 re-export shims (e.g. `planetary/__init__.py`, `component.py:391-405`) — those remain until their tracked migration projects complete.
- Other legacy-audit clusters: see siblings PROJ-485, PROJ-486, PROJ-487, PROJ-488, PROJ-489, PROJ-490.
- REJECTED and OUT_OF_SCOPE findings: see [findings/verification_report.md](findings/verification_report.md).

## Key Files
| Component | File Path |
|-----------|-----------|
| `DamageContext` re-export [EDIT] | `game/simulation/combat/combat_events.py` |
| `CombatConstants` + `DEFAULT_MAX_MASS` re-exports [EDIT] | `game/simulation/entities/ship.py` |
| Unused `_null_provider` import [EDIT] | `game/ui/services/image/__init__.py` |
| Test caller of `DamageContext` re-export [EDIT] | `tests/unit/simulation/combat/test_combat_events.py` |
| Test caller of `DEFAULT_MAX_MASS` re-export [EDIT] | `tests/unit/entities/test_ship.py` |

## Related Documents
- [design.md](design.md) — source audit, cluster identity, quick-wins
- [decisions.md](decisions.md) — bundling decision log
- [findings/verification_report.md](findings/verification_report.md) — full verifier output
- [findings/source_audit.md](findings/source_audit.md) — link to source audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — Phase D bundling record

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
