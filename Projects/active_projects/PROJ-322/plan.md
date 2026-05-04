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
| 2. CAT-5 Fixture Bloat (20 items) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. CAT-6 Mocking Brittleness (26 items) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. CAT-7 Sleep/Latency (9 items) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. APC cluster remediation (APC-001 16 + APC-002 10 + APC-003 8 = 34 items) | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. DUP/HLP consolidation (DUP-001..3 + HLP-001..4 = 7 cluster items) | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

> Phase 5 must NOT begin until Phase 3 (CAT-6 mocking brittleness) is complete. 11 Phase 5 tasks reference Phase 3 tasks (e.g., "Coordinate with Task 3.17"); applying APC fixes before the boundary-patching refactor would undo Phase 3 work.

## Phase Disposition Summary
- **Phase 1 (CAT-4):** 18/18 done, 1 obsolete
- **Phase 2 (CAT-5):** 6 done + 3 N/A + 4 obsolete + 7 deferred (mutable-mock / shape-mismatch)
- **Phase 3 (CAT-6):** 12 done + 7 obsolete + 7 deferred (UIWindow blocker / multi-day production refactor)
- **Phase 4 (CAT-7):** 4 done + 4 obsolete + 1 deferred (LLM thread refactor)
- **Phase 5 (APC):** 13 done + 4 satisfied via earlier phases + 10 obsolete + 7 deferred (UIWindow blocker cluster)
- **Phase 6 (DUP/HLP):** 5 done + 2 satisfied via Phase 1 + 2 deferred (shape-mismatch shared-factory)

**Final tally:** 71 substantive done, 17 obsolete-skipped, 25 formally deferred-out-of-scope.

## Current State
**Last Updated:** 2026-05-04 (final close-out)
**Active Phase:** All phases Complete; ALL 25 formally deferred items now have current dispositions via PROJ-324 / PROJ-325 / PROJ-327 / PROJ-328.
**Last Action:** PROJ-324 Phase 4 + PROJ-327 Phase 5 closeout — Continuation Guide updated with Final disposition summary; `docs/known-issues.md` UIWindow + LLM blockers marked RESOLVED; `docs/02_PATTERNS.md` §33 documents the `make_ui_widget` + `bypass_init` retrofit pattern.
**Next Action:** None — project is closed. All sibling continuation projects (324, 325, 326, 327, 328) Complete.
**Blockers:** None — both systemic blockers resolved. See `## Continuation Guide` Final disposition summary.

## Continuation Guide

> **Status as of 2026-05-04 (final close-out): ALL 25 PROJ-322 deferrals now have current dispositions.** PROJ-324 + PROJ-325 + PROJ-327 + PROJ-328 collectively closed every deferred item, either as RESOLVED (via production refactor + test migration) or as RE-CONFIRMED DEFERRED (with measurement evidence). The original deferral analysis is preserved below for audit-trail context; the **Final disposition summary** at the top is the current state.

### Final disposition summary (2026-05-04)

| Origin (PROJ-322 phase / task) | Disposition | Closed by |
|---|---|---|
| 14 UIWindow / LLM-blocked deferrals (Phase 3 + 4 + 5 boundary-patching cluster) | **RESOLVED** | PROJ-324 Phases 1+2 production foundation (`bypass_init` guard + `LLMBackgroundCall.wait()`) → PROJ-325 Phase 3 PoC (RaceSetupScreen two-stage `__init__` + delegate factory) → PROJ-328 A/B/C (`BuildQueueListWindow`, `OrdersWindow`, `FleetReportWindow`, `NewGameSetupScreen`, `TransferDialog` rolled out the same recipe). |
| Task 3.25 (`strategy_screen` 50-test refactor) | **RESOLVED** | PROJ-327 Phase 4 (Compositional Construction pattern: `StrategyScreenComposition` Protocol + `MockStrategyScreenComposition` fixture). |
| Tasks 2.11 + 2.19 + 2.15 (mutable-mock fixture rescopes) | **RESOLVED** | PROJ-327 Phase 2 (rescoped to module after audit confirmed zero attribute writes; 2.15 subsumed under HLP-001 re-judgment). |
| Tasks 2.6 + 3.15 (private-attr read + component_resource_manager) | **RE-CONFIRMED DEFERRED** with measurement evidence | PROJ-327 Phase 2 — runtime is import-bound, not fixture-bound; `reset_mock` cannot restore re-bound attributes. |
| Tasks 6.1 (DUP-001) + 6.4 (HLP-001) | **RE-CONFIRMED DEFERRED** with measurement evidence | PROJ-327 Phase 3 — measurement confirms construction is dominant but disparate shapes still resolve to a switch-statement factory; readability cost > LOC win. See `Projects/active_projects/PROJ-327/findings/phase_3_runtime_delta.md`. |
| PROJ-323 leftovers (Tasks 3.34 + 3.37, doc corrections, Task 5.19 precision mismatch) | **RESOLVED** | PROJ-325 Phases 1 + 2. |
| Linter for zero-game-import test files | **RESOLVED** | PROJ-326 (preventive linter + allowlist). |

**Net result:**
- All ~7 APC-001 UIWindow deferrals closed via production-side refactor (no longer blocked).
- All 9 PROJ-327-scoped deferrals dispositioned (3 RESOLVED + 4 RE-CONFIRMED DEFERRED with measurement; Task 2.15 subsumed; Task 3.25 RESOLVED).
- Both systemic blockers (UIWindow super-init chain, LLMBackgroundCall polling) are now marked **RESOLVED** in `docs/known-issues.md`.
- `tests/fixtures/ui_widget_factory.py` and the new Compositional Construction pattern are documented at `docs/02_PATTERNS.md` §32 + §33.

### Original deferral analysis (preserved for historical context)

This section is the entry point for a fresh agent picking up the remaining 25 deferred items. The work breaks into two systemic blockers that gate most of the deferrals, plus a small set of items that are independent and actionable now.

#### Systemic blockers

1. **UIWindow super-init chain.** *(Now RESOLVED — see Final disposition summary above.)* The shared `make_ui_widget` factory cannot patch through `super().__init__()` calls because Python's MRO is resolved at class-definition time — the factory's element-class patches don't intercept the chain. This blocks ~7 APC-001 file rewrites (Tasks 5.6, 5.7, 5.10, 5.11, 5.12, 5.16, 5.29) and several Phase 3 boundary-patching tasks that need to drive UIWindow subclasses without a real pygame surface. **Where the unblocking work would happen:** either (a) production-side change to UIWindow subclasses (e.g., a class-level `bypass_init=True` flag honored by `__init__`), or (b) factory enhancement that intercepts the `super().__init__()` call site (likely via metaclass or `__init_subclass__`).

2. **LLMBackgroundCall real-thread polling.** *(Now RESOLVED — see Final disposition summary above.)* Task 4.3 needs production-thread coordination to be refactored before a mocked clock can replace the `time.sleep()`-based polling loops. **Where the unblocking work would happen:** the production `LLMBackgroundCall` class itself — replace the polling loop with an `Event`/`Future`-based wait, then the test can drive completion deterministically without real threads.

#### What's actionable now (does NOT depend on systemic blockers)

These deferred items have rationale captured in the phase checklists but may be addressable with cycle time even though the cost-benefit was unfavorable in the P1 polish scope:

- **Phase 2 fixture-rescope candidates** (Tasks 2.6, 2.8, 2.9, 2.11, 2.15, 2.17, 2.19) — deferred mainly because the candidate fixtures hold mutable state and naive class/module/session rescoping risks cross-test pollution. A careful per-fixture audit (does the test actually mutate it? can the mutation be wrapped in a copy?) could unlock several.
- **Phase 3 boundary-fix candidates** (Tasks 3.14, 3.15, 3.19, 3.20, 3.21, 3.24, 3.25, 3.26) — deferred because the public-API boundary doesn't exist yet or is awkward to drive. A patient pass over each one to design the right boundary (sometimes a small production refactor, sometimes a new public method) could land most of these.

For per-task blocker rationale, see the inline `**DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):** ...` annotations in each `phase_N_checklist.md` file.

#### What requires a new project

These are not single-task items — they are scoped efforts that need their own project plan:

- **UIWindow refactor** — production-side change to make UIWindow subclasses testable without a real pygame display. Once landed, the 7 Phase 5 deferrals plus the cross-coordinated Phase 3 boundary tasks unlock.
- **LLMBackgroundCall thread refactor** — replace polling with event/future coordination. Unblocks Task 4.3.
- **RaceSetupScreen testable construction** — the lone non-UIWindow APC-001 deferral that is high-touch in its own right (large constructor surface, many collaborators).

#### Pointers

- **Per-task blocker rationale:** inline `**DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):** ...` annotations in each `phase_N_checklist.md`.
- **Systemic context** (UIWindow chain analysis, freezegun/thread incompatibility, tool bugs encountered): `docs/known-issues.md`.
- **Resolution context** (post-2026-05-04): the `bypass_init` retrofit pattern is documented at `docs/02_PATTERNS.md` §33; the Compositional Construction long-term pattern is documented at `docs/02_PATTERNS.md` §32. Per-task RESOLVED / RE-CONFIRMED DEFERRED annotations live inline in each `phase_N_checklist.md` next to the original deferral text.

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
- [x] All phase checklists complete
- [x] All tests passing
- [ ] Audit passed
- [ ] User verified
