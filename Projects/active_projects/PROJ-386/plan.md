# PROJ-386: Legacy removal — Save-format migration eradication (2026-05-07)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-386` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-386 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Delete save-format migration code (banned by Rule 3) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** None — project complete
**Last Action:** All 4 save-format migration code blocks deleted (LEG-03-008, LEG-03-017, LEG-03-018, LEG-04-005). Tests that exercised only the legacy fallback paths deleted; tests that incidentally relied on the missing-`components` graceful degrade rewritten to feed new-format fixtures.
**Next Action:** Awaiting user verification.
**Blockers:** None

## Overview
Deletes 4 distinct save-format migration code blocks across 4 files. **All 4 are banned by CLAUDE.md Rule 3** ("No save-file migration. Old saves are disposable."). The audit's deterministic save-migration scanner found 0 — these slipped through because they don't use the word "migration" in their logic, only in comments. Sonnet's third-pass verification confirmed all 4 are reachable during normal save loading and gate on legacy shape checks.

## Goals
- Delete `_complex_toggles` legacy migration in `battle_setup/controller.py:548-568`.
- Delete `{'active': bool}` old-format branch in `component_activation_state.py:144-149`.
- Delete silent-ignore + graceful-degrade compat paths in `ship_instance_serializer.py:100-102, 127-138`.
- Delete `side_0`/`side_1` legacy emit + read in `battle_setup_state.py:257-300`.

## Scope
**In:** LEG-03-008, LEG-03-017, LEG-03-018, LEG-04-005 (all banned by CLAUDE.md Rule 3).
**Out:** Other clusters from the same audit (siblings PROJ-383, PROJ-384, PROJ-385, PROJ-387..PROJ-393); REJECTED and OUT_OF_SCOPE items recorded in [findings/verification_report.md](findings/verification_report.md) and the shared [findings/bundling_decisions.md](findings/bundling_decisions.md).

## Key Files
| Component | File Path |
|-----------|-----------|
| Save migration | `game/ui/screens/battle_setup/controller.py` |
| Save migration | `game/strategy/data/component_activation_state.py` |
| Save migration | `game/strategy/data/ship_instance_serializer.py` |
| Save migration | `game/ui/screens/battle_setup_state.py` |

## Related Documents
- [design.md](design.md) — source audit, cluster identity, severity breakdown, **Policy Notes** subsection (CLAUDE.md Rule 3 citation)
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification of audit claims
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — interactive bundling record (shared across siblings)

## Verification
- [x] All phase checklists complete
- [x] All tests passing (focused regression across all affected areas; 2 pre-existing PROJ-393-related failures in `test_order_processor_transfer.py` confirmed not caused by this work)
- [x] No remaining `if 'phase' not in data` / `side_0` / `_complex_toggles` legacy-format guards (only docstring/comment references + new-format `*_complex_toggles` field/property names remain in production)
- [ ] User verified
