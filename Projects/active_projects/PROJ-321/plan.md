# PROJ-321: Test review P0 dead-trivial cleanup 2026-05-02

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-321` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-321 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. CAT-1 Trivial Pass (46 items) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. CAT-2 Tests Nothing Real (26 items) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. CAT-3 Dead Test Code (8 items, 1 relocate + 7 delete) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-03
**Active Phase:** Phase 1 CAT-1 Trivial Pass
**Last Action:** Project created from 2026-05-02_204633_test-review after independent verification (3rd skeptical pass)
**Next Action:** Begin Phase 1 tasks: delete or pytest.skip 46 verified CAT-1 trivial-pass tests
**Blockers:** None

## Overview
This project implements the P0 dead-trivial cleanup recommendations from the OpenCode test-review at `Reviews/results/2026-05-02_204633_test-review/`. Independent verification (third skeptical pass) confirmed 80 P0 items (79 verified + 1 needs-rework) across CAT-1 (trivial-pass), CAT-2 (tests-nothing-real), and CAT-3 (dead-test-code), representing approximately 5,038 LOC of reclaimable test bloat.

## Goals
- Delete or convert to pytest.skip 46 verified CAT-1 trivial-pass tests
- Delete or rewrite 26 verified CAT-2 tests-nothing-real tests/files
- Delete or relocate 8 verified CAT-3 dead-test-code files / sections (Task 3.5 relocates `test_bug_12_energy_gen.py` to `tests/regression/`; the other 7 delete)

## Scope
**In:** CAT-1, CAT-2, CAT-3 - verified items only.
**Out:** CAT-4..CAT-7 + APC/DUP/HLP categories - see PROJ-322 (P1 project); CAT-8..CAT-12 categories - see PROJ-323 (P2 project); Anything OpenCode tagged DISPUTED or INCONCLUSIVE; Anything Claude's verification rejected or marked out-of-scope (see findings/verification_report.md).

## Key Files
| File | Item Count |
|------|------------|
| `tests/unit/ui/screens/test_event_log_window.py` | 6 item(s) |
| `tests/unit/ui/panels/test_race_identity_panel.py` | 3 item(s) |
| `tests/integration/test_app_integration.py` | 3 item(s) |
| `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py` | 3 item(s) |
| `tests/unit/ui/test_race_summary_panel.py` | 3 item(s) |
| `tests/unit/services/llm/test_package_imports.py` | 2 item(s) |
| `tests/unit/ui/screens/battle_setup/test_view_model.py` | 2 item(s) |
| `tests/unit/strategy/generation/test_layout_scaling.py` | 2 item(s) |
| `tests/unit/strategy/test_commands.py` | 2 item(s) |
| `tests/unit/ui/screens/test_strategy_window_manager_public_api.py` | 2 item(s) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/verification_report.md](findings/verification_report.md) - Independent verification of OpenCode CONFIRMED claims
- [findings/source_review.md](findings/source_review.md) - Source review reference

## Cross-Project Dependencies

PROJ-321 is the upstream of PROJ-322 (P1) and PROJ-323 (P2). Several files
appear in multiple projects:

- 21 files overlap between PROJ-321 (CAT-1/2/3 deletions) and PROJ-322
  (APC-001/002/003 cluster rewrites and CAT-4..7 fixes).
- 4 files (`test_testruncard_propulsion.py`, `test_commands.py`,
  `test_build_queue_screen.py`, etc.) overlap with PROJ-323 (P2 polish).

**Required execution order:** PROJ-321 → PROJ-322 → PROJ-323. The downstream
projects assume PROJ-321 has completed; if PROJ-321 deletes a file or test,
the downstream task on that file should be marked obsolete (not retried).

Each phase in PROJ-322 and PROJ-323 should re-check whether its target files
still exist and contain the cited tests before starting.

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
