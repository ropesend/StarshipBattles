# PROJ-40: Comprehensive Code Quality Remediation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-40` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-40 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist | Issues |
|-------|--------|-----------|--------|
| 1. Critical Architecture Fixes | Not Started | [phase_1_checklist.md](phase_1_checklist.md) | 3 Critical |
| 2. Quick Wins - Dead Code & Duplicates | Not Started | [phase_2_checklist.md](phase_2_checklist.md) | 15 Simple |
| 3. Core Infrastructure Improvements | Not Started | [phase_3_checklist.md](phase_3_checklist.md) | 8 Issues |
| 4. Simulation Engine Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) | 10 Issues |
| 5. Strategy Layer Refinements | Not Started | [phase_5_checklist.md](phase_5_checklist.md) | 8 Issues |
| 6. AI System Improvements | Not Started | [phase_6_checklist.md](phase_6_checklist.md) | 10 Issues |
| 7. UI Layer Remediation | Not Started | [phase_7_checklist.md](phase_7_checklist.md) | 14 Issues |
| 8. Research System Polish | Not Started | [phase_8_checklist.md](phase_8_checklist.md) | 8 Issues |
| 9. Data & Config Cleanup | Not Started | [phase_9_checklist.md](phase_9_checklist.md) | 12 Issues |
| 10. Test Infrastructure | Not Started | [phase_10_checklist.md](phase_10_checklist.md) | 18 Issues |
| 11. Original Findings Completion | Not Started | [phase_11_checklist.md](phase_11_checklist.md) | 5 Issues |

**Total Issues:** 111 (108 new + 3 remaining original findings)

## Current State
**Last Updated:** 2026-01-27
**Active Phase:** Planning
**Last Action:** Project created from update review findings
**Next Action:** Begin Phase 1 - Critical Architecture Fixes
**Blockers:** None

## Overview
This project addresses all 108 issues discovered in the comprehensive code review (`2026-01-27_update_legacy-cleanup-verification`), plus 3 remaining issues from the original legacy cleanup review. Issues are organized into 11 phases by architectural layer and complexity.

### Source Review
- **Original Review:** `Reviews/results/2026-01-27_general_legacy-cleanup-verification`
- **Update Review:** `Reviews/results/2026-01-27_update_legacy-cleanup-verification`
- **Total New Issues:** 108 (3 Critical, 28 Major, 66 Minor, 11 Info)
- **Remaining Original:** 3 (LDF-03, LPA-04, DC-03)

### Issue Breakdown by Severity
| Severity | Count | Addressed in Phases |
|----------|-------|---------------------|
| Critical | 3 | Phase 1 |
| Major | 28 | Phases 2-7 |
| Minor | 66 | Phases 2-10 |
| Info | 11 | Phases 8-10 |
| Original (remaining) | 3 | Phase 11 |

### Phase Strategy

**Phase 1: Critical Architecture Fixes**
Address the 3 critical layer violations that break architectural principles:
- NEW-CORE-001: Core → Strategy layer violation (HexCoord import)
- NEW-SIM-001: Duplicate attribute initialization in Ship
- NEW-UI-001: 37 UI → Simulation/Strategy/AI import violations

**Phase 2: Quick Wins - Dead Code & Duplicates**
Low-effort, high-impact fixes:
- Duplicate code removals (NEW-SIM-002, NEW-SIM-003)
- Dead code patterns (NEW-SIM-004, NEW-UI-006, NEW-STRAT-004)
- Unused imports cleanup

**Phases 3-8: Layer-by-Layer Remediation**
Systematic cleanup of each architectural layer

**Phase 9: Data & Config Cleanup**
JSON schema standardization, placeholder cleanup

**Phase 10: Test Infrastructure**
Test organization, fixture consolidation, framework consistency

**Phase 11: Original Findings Completion**
Complete remaining items from original legacy cleanup

## Success Criteria
1. All 3 critical layer violations resolved
2. All 28 major issues addressed
3. Test suite passes after each phase
4. No regressions introduced

## Related Documents
- [design.md](design.md) - Findings summary and design notes
- [decisions.md](decisions.md) - Architecture decisions made during remediation
- Phase checklists linked in Quick Status table
