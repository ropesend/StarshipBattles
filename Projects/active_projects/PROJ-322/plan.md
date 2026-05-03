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
| 1. CAT-4 Duplicate Testing (19 items) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. CAT-5 Fixture Bloat (20 items) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. CAT-6 Mocking Brittleness (26 items) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. CAT-7 Sleep/Latency (9 items) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. APC cluster remediation (APC-001 16 + APC-002 10 + APC-003 8 = 34 items) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. DUP/HLP consolidation (DUP-001..3 + HLP-001..4 = 7 cluster items) | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-05-03
**Active Phase:** Phase 1 CAT-4 Duplicate Testing
**Last Action:** Project created from 2026-05-02_204633_test-review after independent verification (3rd skeptical pass)
**Next Action:** Begin Phase 1 tasks: consolidate 19 verified CAT-4 duplicate tests
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

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
