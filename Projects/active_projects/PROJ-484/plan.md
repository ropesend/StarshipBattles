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
| 1. Zero-call-site deletions | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Single-test-caller migrations | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Audit remediation (Codex consult 2026-05-23) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** Complete
**Last Action:** Phase 3 remediated a regression Codex caught: `combat_events.py:78` referenced `DamageContext` as a type annotation but the Phase 2 deletion of line 62 left no binding. Added TYPE_CHECKING import + forward-ref string annotation (matches file's existing pattern). Tests still green.
**Next Action:** User verification, then commit.
**Blockers:** None

## Overview
Dead re-export / unused-import lines flagged by the 2026-05-20 legacy audit. After mid-project Codex audit re-check, two of the four originally-listed items (`ship.py:22` `DEFAULT_MAX_MASS`, `ship.py:23` `CombatConstants`) were REJECTED — the audit miscounted call sites because both symbols are used internally in `ship.py` itself. Remaining scope: one zero-call-site deletion (`image/__init__.py:37`) and one one-test-caller migration-plus-deletion (`combat_events.py:62` + its test), plus a test-caller migration to canonical path (`test_ship.py:472`).

## Goals
- Phase 1: Delete one zero-call-site side-effect import (`image/__init__.py:37`).
- Phase 2: Migrate two test callers to canonical imports; delete the `combat_events.py:62` re-export. Do NOT delete `ship.py:22` (live internal import).

## Scope
**In:** dead re-exports / unused side-effect imports verified against current source (post audit correction).
**Out:**
- Documented Pattern #36 re-export shims (e.g. `planetary/__init__.py`, `component.py:391-405`) — those remain until their tracked migration projects complete.
- The misleading `# Re-export for backward compatibility and convenient access` comment at `ship.py:21`. The comment is misleading (lines 22 and 23 are live internal imports, not re-exports) but harmless; correcting it is deferred to a future audit-fix project.
- Other legacy-audit clusters: see siblings PROJ-485, PROJ-486, PROJ-487, PROJ-488, PROJ-489, PROJ-490.
- REJECTED and OUT_OF_SCOPE findings: see [findings/verification_report.md](findings/verification_report.md).

## Key Files
| Component | File Path |
|-----------|-----------|
| `DamageContext` re-export [EDIT] | `game/simulation/combat/combat_events.py` |
| Unused `_null_provider` import [EDIT] | `game/ui/services/image/__init__.py` |
| Test caller of `DamageContext` re-export [EDIT] | `tests/unit/simulation/combat/test_combat_events.py` |
| Test caller of `DEFAULT_MAX_MASS` (canonical-path migration only) [EDIT] | `tests/unit/entities/test_ship.py` |

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
