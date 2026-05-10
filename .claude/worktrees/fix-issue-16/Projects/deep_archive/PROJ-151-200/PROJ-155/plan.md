# PROJ-155: Test Suite Cleanup v3 - Validated Findings

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-155` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-155 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Delete Zero-Risk Files | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Merge Then Delete | Complete (PROJ-154 + PROJ-157) | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Old Directory Trees | Complete (all kept - unique coverage) | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Partial Cleanups | Complete (PROJ-154 + PROJ-157) | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Structural Improvements | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-20
**Active Phase:** All phases complete - ready for audit
**Last Action:** Completed Phase 1 (deleted update_test_ships.py), Phase 3 (verified all combat/ and entities/ files have unique coverage - KEPT), Phase 5 (renamed refactor/ → modifiers/)
**Next Action:** Audit project
**Blockers:** None
**Context:** All 5 phases complete. Phase 1: deleted 1 file. Phase 3: reviewed all ~16 files in combat/ and entities/ - all have unique integration-style coverage with no simulation/ counterparts, so all KEPT. Phase 5: renamed refactor/ → modifiers/ via git mv. Tests: 11984 passed, 144 pre-existing failures.

## Overview
Systematic removal of ~2,430 lines of confirmed-dead test code + ~12,700 lines of old directory trees + 19 data files, based on 4 independent validation reviews of the v3 test suite cleanup review. Only validated-safe deletions and merges are included. ~2,050 lines originally recommended for removal were disputed by validators and will NOT be touched.

## Goals
- Remove dead test code: empty scaffolds, import-only checks, over-mocked tests that exercise no game code
- Remove confirmed duplicate test files (subsets of more comprehensive counterparts)
- Migrate ~20 unique tests from partially-duplicate files before deleting them
- Remove 4 old directory trees confirmed as strict subsets of simulation/ tests
- Clean up partial dead code within otherwise-valuable files
- Improve test suite organization (relocations, renames)

## Scope
**In:**
- Files confirmed by validation reviews as safe to remove (12 CONFIRMED across 4 reviews)
- Files confirmed as safe to remove after merging unique tests (5 MODIFIED across 4 reviews)
- Old directory trees (services/, combat/, entities/, components/) verified as subsets
- Partial dead code removal within files (empty stubs, duplicate classes, trivial assertions)
- File relocations and directory renames

**Out:**
- 9 DISPUTED files (validators determined these should be kept)
- New test development
- Production code changes
- Save file migration or backward compatibility
- All repro_*.py files (validators confirmed these have unique coverage)
- Fixture meta-test files (validators confirmed these provide isolation verification)

## Key Files
| Component | File Path |
|-----------|-----------|
| Review report | `Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/report.md` |
| Validation 1 (UI+Strategy) | `Reviews/results/.../findings/validation_1_ui_strategy.md` |
| Validation 2 (Sim+Core) | `Reviews/results/.../findings/validation_2_simulation_core.md` |
| Validation 3 (AI+Refactor) | `Reviews/results/.../findings/validation_3_ai_refactor.md` |
| Validation 4 (Remaining+Cross) | `Reviews/results/.../findings/validation_4_remaining_crosscut.md` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (12,790+ passed, 143 pre-existing failures unchanged)
- [ ] Audit passed
- [ ] User verified
