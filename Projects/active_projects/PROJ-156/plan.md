# PROJ-156: Test Suite Cleanup - AI/Research/Combat/Builder/Systems

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-156` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-156 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Straight Deletes | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Partial Cleanup | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Merge Then Delete | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Directory Cleanup & Final Verify | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-16 17:30
**Active Phase:** Planning Complete - Ready for Implementation
**Last Action:** Full plan created with 4 phases from validation review findings
**Next Action:** Begin Phase 1 - delete 9 dead test files
**Blockers:** None
**Context for Next Agent:** Baseline is 12,788 passed, 145 failed (pre-existing UI failures in build queue/cargo/transfer areas, unrelated to this project). All file paths have been verified. See design.md for path corrections from original review.

## Overview
Systematic cleanup of confirmed dead/duplicate/scaffold test code across the AI, Research, Combat, Builder, and Systems test directories. Based on Validation Review 3 which examined 30 findings from agents 5 and 6, confirmed 12 for deletion, 13 for partial removal, and disputed 5 (kept as-is). Total estimated savings: ~2,800+ lines.

## Goals
- Delete 9 files that test no production code (mocks-on-mocks, local reimplementations, hasattr checks)
- Remove empty stubs, trivial constant checks, and duplicate classes from 7 existing files
- Merge 50+ unique tests from 8 source files into 6 target files, then delete sources
- Clean up emptied directories
- Preserve ALL unique test coverage throughout

## Scope
**In:**
- Files confirmed for removal by validation review 3
- Merge operations where unique tests are identified and preserved
- Directory cleanup after file removals

**Out:**
- UI test cleanup (covered by separate validation reviews 1 & 2)
- Simulation test cleanup (covered by separate validation review 2)
- Refactor/ directory rename to modifiers/ (cosmetic, deferred)
- Any changes to disputed files (research tracker edge cases, AI controller files, refactor/ tests)
- test_persistence.py rename (cosmetic, deferred)

## Key Files
| Component | File Path | Role |
|-----------|-----------|------|
| Behavior merge target | `tests/unit/ai/test_behavior_units.py` | Receives 7 tests from test_ai_behaviors.py |
| Eval rules merge target | `tests/unit/ai/test_target_evaluator_rules.py` | Receives 11 tests incl. bug-documenting class |
| Eval edge merge target | `tests/unit/ai/test_target_evaluator_edge_cases.py` | Receives 11 tests from integration file |
| Adapter merge target | `tests/unit/ai/test_controllable_adapter_edge_cases.py` | Receives 7 tests from 2 source files |
| Spatial merge target | `tests/unit/systems/test_spatial.py` | Receives 5 tests from extended file |
| Collision merge target | `tests/unit/engine/collision_edge_cases/test_beam_ramming.py` | Receives 6 tests from collision system |

## Related Documents
- [design.md](design.md) - Path corrections, merge details, risk analysis
- [decisions.md](decisions.md) - Full decisions log
- Source review: `Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/findings/validation_3_ai_refactor.md`

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (baseline: 12,788 passed, 145 pre-existing failures)
- [ ] No new test failures introduced
- [ ] All unique tests preserved in merge targets
- [ ] Emptied directories cleaned up
