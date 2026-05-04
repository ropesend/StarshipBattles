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
| 2. CAT-5 Fixture Bloat (20 items) | Complete (6 done; 3 N/A; 4 obsolete; 7 deferred-out-of-scope) | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. CAT-6 Mocking Brittleness (26 items) | Complete (12 done — pass 3 added 5; 7 obsolete; 7 deferred-out-of-scope) | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. CAT-7 Sleep/Latency (9 items) | Complete (4 done; 4 obsolete; 1 deferred-out-of-scope) | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. APC cluster remediation (APC-001 16 + APC-002 10 + APC-003 8 = 34 items) | Complete (13 done — pass 3 added 3 APC-003 via cross-coordination; 4 satisfied via earlier phases; 10 obsolete; 7 deferred-out-of-scope (UIWindow-inheritance cluster + 1 high-touch RaceSetupScreen)) | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. DUP/HLP consolidation (DUP-001..3 + HLP-001..4 = 7 cluster items) | Complete (5 done — pass 2 added 3 shared factories; 2 satisfied via Phase 1; 2 deferred-out-of-scope (DUP-001/HLP-001 shape-mismatch)) | [phase_6_checklist.md](phase_6_checklist.md) |

> Phase 5 must NOT begin until Phase 3 (CAT-6 mocking brittleness) is complete. 11 Phase 5 tasks reference Phase 3 tasks (e.g., "Coordinate with Task 3.17"); applying APC fixes before the boundary-patching refactor would undo Phase 3 work.

## Current State
**Last Updated:** 2026-05-03 (pass 3)
**Active Phase:** All phases now Complete (or deferred-out-of-scope with concrete blockers)
**Pass 3 disposition summary (47 deferred items walked):**
- **5 newly addressed** in Phase 3 + Phase 5 (cross-coordinated):
  - Task 3.3 / S02-CAT6-004: converted `test_multi_selection_logic.py` autouse `setup(self.X = ...)` to value-returning `selection_setup` fixture.
  - Task 3.9 / 5.28 / S02-CAT6-002: rewrote `test_battle_engine_init_ship.py` (4 tests) to drive `engine.start()` public API instead of `_initialize_ship()` private helper.
  - Task 3.10 / S10-CAT6-001: documentation alternative — strengthened design-intent docstring on `test_build_order_auto_completes_when_queue_empties`.
  - Task 3.12 / 5.33 / S08-CAT6-002: rewrote `test_basics` (fleet_movement_engine) to inject `nav_service` via DI instead of patching module-level `find_hybrid_path`.
  - Task 3.17 / 5.27 / S02-CAT6-001: rewrote `TestGetBaseFiringArc` (5 tests) in `test_modifier_logic_service.py` to use public `get_initial_value('turret_mount', comp)` instead of calling `_get_base_firing_arc` private helper.
- **17 marked obsolete** (target file no longer exists — deleted by PROJ-321 cleanup or earlier rationalization):
  - Phase 2: Tasks 2.1, 2.3, 2.14, 2.16
  - Phase 3: Tasks 3.1, 3.5, 3.7, 3.8, 3.18, 3.23
  - Phase 4: Tasks 4.4, 4.5, 4.6a, 4.6b
  - Phase 5: Task 5.34
- **24 marked deferred-out-of-scope** with concrete blocker text (UIWindow-inheritance cluster, mutable-mock fixture rescopes that risk pollution, multi-day production refactors, shape-mismatch shared-factory consolidations):
  - Phase 2: Tasks 2.6, 2.8, 2.9, 2.11, 2.15, 2.17, 2.19
  - Phase 3: Tasks 3.14, 3.15, 3.19, 3.20, 3.21, 3.24, 3.25, 3.26
  - Phase 4: Task 4.3 (real-thread polling incompatible with test-only mocked clock)
  - Phase 5: Tasks 5.6, 5.7, 5.10, 5.11, 5.12, 5.16, 5.29 (UIWindow inheritance) — well-documented blocker
  - Phase 6: Tasks 6.1 (DUP-001), 6.4 (HLP-001) — shape-mismatch shared-factory rationale
- **1 obviated** (work already accomplished by earlier task): Phase 2 Task 2.14 obviated by Task 5.15 deletion.
**Net delta pass 3:** 5 substantive task items completed across 5 test files. 24 items formally documented as deferred-out-of-scope with concrete blockers (vs. the prior generic "deferred — out of safe-pass scope" notes). 17 obsolete items closed-out with file-no-longer-exists rationale.
**Final tally:** 71/113 task items complete (1 obviated counted), 17 obsolete-skipped, 25 formally deferred-out-of-scope.
**Test result:** All affected files green; sharded run pending.
**Blockers (formally tracked for future PROJ):**
- UIWindow super-init chain incompatibility — affects ~7 APC-001 file rewrites + several boundary-patching tasks. Unblocking requires either (a) production-side bypass flag in UIWindow subclasses, or (b) factory enhancement that intercepts the `super().__init__()` call site.
- Real-thread LLM polling — Task 4.3 needs the `LLMBackgroundCall` thread-coordination refactor (production change) before mocked-clock can replace the polling loops.

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
