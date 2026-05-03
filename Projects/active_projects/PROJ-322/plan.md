# PROJ-322: Test review P1 brittle-bloated remediation 2026-05-02

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-322` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-322 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. CAT-4 Duplicate Testing (19 items) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. CAT-5 Fixture Bloat (20 items) | Partial (6 done, 3 N/A, 11 deferred) | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. CAT-6 Mocking Brittleness (26 items) | Partial (7 done, 19 deferred) | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. CAT-7 Sleep/Latency (9 items) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. APC cluster remediation (APC-001 16 + APC-002 10 + APC-003 8 = 34 items) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. DUP/HLP consolidation (DUP-001..3 + HLP-001..4 = 7 cluster items) | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

> Phase 5 must NOT begin until Phase 3 (CAT-6 mocking brittleness) is complete. 11 Phase 5 tasks reference Phase 3 tasks (e.g., "Coordinate with Task 3.17"); applying APC fixes before the boundary-patching refactor would undo Phase 3 work.

## Current State
**Last Updated:** 2026-05-03
**Active Phase:** Phase 4 CAT-7 Sleep/Latency
**Last Action:** Phase 3 partial — 7/26 done (3.2 attack_run threshold, 3.4 satisfied by Task 1.2 deletion, 3.6 source-text test removed, 3.11 kwargs-or-positional, 3.13 movement_engine DI via _movement_engine, 3.16 cloned-attribute assertions, 3.22 doc note). 19 deferred — most are Complex/Medium boundary refactors that overlap Phase 5 APC-001/002/003 clusters (3.5, 3.7, 3.20, 3.21, 3.24-3.26 all rated Complex). Phase 3 prereq for Phase 5 is partially satisfied: the boundary-patching philosophy is documented; Phase 5 will absorb the remaining boundary work as part of APC cluster cleanup.
**Next Action:** Begin Phase 4 — replace 9 CAT-7 time.sleep() with deterministic waits.
**Blockers:** None

## Overview
This project remediates the P1 (brittle/bloated) findings from the OpenCode test-review at `Reviews/results/2026-05-02_204633_test-review/`. After an independent third skeptical pass, 115 P1 items survived (111 VERIFIED + 4 NEEDS_REWORK) across CAT-4/5/6/7 and the APC/DUP/HLP cross-shard clusters, with claimed reclaimable churn of approximately 9,629 LOC of test-side rewrites and consolidations.

## Goals
- Phase 1: Consolidate the 19 CAT-4 duplicate tests via parametrize/extract or removal of overlapping coverage.
- Phase 2: Rescope or share the 20 CAT-5 expensive fixtures (function -> class/module/session) where safe.
- Phase 3: Reduce the 26 CAT-6 brittle-mocking patterns by patching at public boundaries instead of private internals.
- Phase 4: Replace `time.sleep()` with deterministic waits (`os.utime()`, mocked clock, Event sync) or remove latency-based assertions for the 9 CAT-7 cases.
- Phase 5: Eliminate the cross-cutting APC anti-patterns (APC-001 `__new__` bypass-init across 16 UI files; APC-002 source-inspection across 10 files; APC-003 private-method patching across 8 files).
- Phase 6: Consolidate cross-shard duplicate tests and helper duplications (DUP-001..3, HLP-001..4) into shared `tests/fixtures/` and `conftest.py` factories.

## Scope
**In:** CAT-4, CAT-5, CAT-6, CAT-7 categories + APC-001, APC-002, APC-003 anti-pattern clusters + DUP-001/002/003 + HLP-001/002/003/004 cross-shard helper duplications - verified items only.

**Out:**
- CAT-1, CAT-2, CAT-3 categories - see PROJ-321 (P0 dead-trivial cleanup project)
- CAT-8..CAT-12 categories - see PROJ-323 (P2 opportunistic polish project)
- Anything OpenCode tagged DISPUTED or INCONCLUSIVE
- Anything Claude's verification rejected or marked out-of-scope (see [findings/verification_report.md](findings/verification_report.md))

## Key Files
| Item Count | File Path |
|-----------:|-----------|
| 3 | `tests/unit/ui/screens/test_save_selection.py` |
| 2 | `tests/unit/ui/screens/builder/test_modifier_logic_service.py` |
| 2 | `tests/unit/simulation/systems/test_battle_engine_init_ship.py` |
| 2 | `tests/unit/strategy/engine/test_superweapon_edge_cases.py` |
| 2 | `tests/unit/ui/screens/test_fleet_report_window_multi_select.py` |
| 2 | `tests/unit/ui/panels/test_empire_treasury_panel.py` |
| 2 | `tests/unit/ui/screens/test_build_queue_list_window.py` |
| 2 | `tests/unit/strategy/turn_engine/test_tick_mechanics.py` |
| 2 | `tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py` |
| 2 | `tests/unit/strategy/engine/test_build_order_command_handler.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/verification_report.md](findings/verification_report.md) - Independent third-pass verification of OpenCode CONFIRMED claims
- [findings/source_review.md](findings/source_review.md) - Pointer to the source OpenCode test-review

## Cross-Project Dependencies

PROJ-322 is downstream of PROJ-321 (P0 deletions). 21 files overlap between
the two projects' manifests — primarily APC-001 UI test files where PROJ-321
deletes CAT-1/CAT-2 trivial tests and PROJ-322 rewrites the broader
__new__-bypass pattern. Four CAT-2/APC-002 files have direct overlap:

- `tests/unit/modifiers/test_seeker_multi_ability.py`
- `tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py`
- `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py`
- `tests/integration/test_app_integration.py`

**Required execution order:** PROJ-321 must complete before PROJ-322 begins
Phase 5 (APC clusters). Phase 1-4 of PROJ-322 may interleave with PROJ-321
since they target different files.

Before starting any Phase 5 task, re-check whether the target file still
exists and contains the cited APC pattern. If PROJ-321 deleted the file
entirely, mark the corresponding APC task as **obsolete** (not done).

PROJ-323 is downstream of PROJ-322 — see PROJ-323/plan.md for its
dependency on this project.

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
