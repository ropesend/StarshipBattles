# PROJ-417: Legacy removal — test_run_details.py shim (2026-05-13)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-417` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-417 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Migrate 2 callers and delete test_run_details.py shim | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-13
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-13_194106_legacy-audit` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Migrates 2 caller sites off the 12-line `game/ui/screens/test_lab/test_run_details.py` re-export shim onto `game.ui.screens.test_lab.details`, then deletes the shim.

Source: legacy audit `2026-05-13_194106_legacy-audit`, verified items in this bundle = 1.
Removal cluster: `test_run_details_shim`.

### Notable callouts
_(no special callouts)_

## Goals
- Migrate 2 callers and delete test_run_details.py shim

## Scope
**In:** removal cluster `test_run_details_shim` — items MIN-003.
**Out:** other clusters' contents (siblings: PROJ-413, PROJ-414, PROJ-415, PROJ-416, PROJ-418, PROJ-419, PROJ-420, PROJ-421); REJECTED and OUT_OF_SCOPE findings (none in this run; see `findings/verification_report.md`).

## Key Files
| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/ui/screens/test_lab/test_run_details.py` | Production | Delete [DELETE] | Whole 12-line shim file removed |
| `game/ui/screens/test_lab/panel_manager.py` | Production | Edit | Switch import to `.details` (only real production caller) |
| `game/ui/screens/test_lab/results_panel.py` | Production | No action | No import — only a comment reference; N/A |
| `tests/unit/test_lab/test_test_run_details_public_api.py` | Test | Edit | Migrate 4 shim-path imports to `details`; delete shim-contract test |
| `game/ui/screens/test_lab/__init__.py` | Docs | Edit | Remove stale `test_run_details.py` mention from docstring |
| `game/ui/screens/test_lab/README.md` | Docs | Edit | Remove table row and diagram entry for `test_run_details.py` |
| `game/ui/screens/test_lab/details/__init__.py` | Docs | Edit | Remove "shim module remains" note (lines 9-11) |
| `docs/02_PATTERNS.md` | Docs | Edit | Remove Pattern #36 site entry for this shim if listed |

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
