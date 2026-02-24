# PROJ-163: Move Automation Loops to Projects Directory

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-163` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-163 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Update refactor_loop internal paths | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Update continuous_loop internal paths | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Update all external references | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Execute git moves and verify | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-23
**Current Phase:** All phases complete - awaiting final test suite run
**Last Agent Action:** Phase 4 complete - git mv done, all verifications passed
**Next Action:** Run final test suite, then project is ready for user verification
**Blockers:** None
**Context for Next Agent:** All 4 phases complete. Both directories moved via `git mv`. WORKSPACE depth verified at runtime. Zero stale references. Git status shows clean renames.

## Overview
Move `refactor_loop/` and `continuous_loop/` from the project root into `Projects/refactor_loop/` and `Projects/continuous_loop/`. These are automation infrastructure for the Projects system and belong under that umbrella. All changes are mechanical path string replacements - no behavioral changes.

## Goals
- Cleaner root directory - automation loops consolidated under Projects/
- Architectural clarity - automation infra lives with the system it serves
- All path references updated so both loop systems continue to function identically

## Scope
**In Scope:**
- All path references to `refactor_loop/` and `continuous_loop/` across the repo
- Python `WORKSPACE` depth calculations in 3 continuous_loop scripts
- The `git mv` operations for both directories
- Exclusion lists in sweep prompts and skill files

**Out of Scope:**
- Log files in `continuous_loop/logs/` (historical, do not edit)
- `Reviews/results/*/scope.md` files (historical sweep results, do not edit)
- Any behavioral changes to the loop systems
- Game code or test code (none affected)

## Key Files Reference
| Component | File Path | Notes |
|-----------|-----------|-------|
| Refactor loop runner (PS) | `refactor_loop/loop_runner.ps1` | 4 path refs |
| Refactor loop runner (Bash) | `refactor_loop/loop_runner.sh` | 5 path refs |
| Refactor worker prompt | `refactor_loop/WORKER.md` | 5 path refs |
| Refactor loop docs | `refactor_loop/REFACTOR_LOOP_README.md` | 25+ refs (global replace) |
| Continuous outer loop | `continuous_loop/continuous_loop.ps1` | 6 path vars |
| Continuous inner loop | `continuous_loop/inner_loop.ps1` | 5 path refs |
| Continuous cycle worker | `continuous_loop/CYCLE_WORKER.md` | 6 path refs |
| Continuous sweep worker | `continuous_loop/SWEEP_WORKER.md` | 3 path refs |
| Populate cycle plan | `continuous_loop/populate_cycle_plan.py` | WORKSPACE depth + 5 refs |
| Trim execution log | `continuous_loop/trim_execution_log.py` | WORKSPACE depth + 5 refs |
| Compute quality score | `continuous_loop/compute_quality_score.py` | WORKSPACE depth + 4 refs |
| Trigger audit script | `Projects/scripts/trigger_audit.py` | 1 ref (line 103) |
| Protocol 08 | `Projects/protocols/08_automated_loop_protocol.md` | 2 refs |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Update paths before moving (not after) | Cleaner git history; paths are correct at time of move |
| 2026-02-23 | Skip log files and historical scope.md files | Historical records, not worth updating |
| 2026-02-23 | Keep Debugging/, Features/, Reviews/ at root | Active workflow systems, not documentation |
| 2026-02-23 | One commit per phase | Clean rollback points if issues found |

## Initial Analysis
Comprehensive codebase grep identified all references to `refactor_loop/` and `continuous_loop/`. The references fall into 4 categories:
1. **Internal files** (move with directory, need path updates): 4 in refactor_loop, 8 in continuous_loop
2. **External files** (stay put, reference the old path): ~18 files across skills, protocols, prompts
3. **Exclusion lists** in sweep prompts and skill files: 6 files mentioning `refactor_loop/` in exclude patterns
4. **Historical files** (do not edit): log files and old review scope.md files

## Swarm Findings Summary
### Architecture
Both directories are purely infrastructure - no game code imports or depends on them. The `continuous_loop/` directory has 3 Python scripts with `Path(__file__).parent.parent` calculations that must be adjusted for the new depth.

### Key Patterns to Reuse
- **Global find-replace**: `refactor_loop/` → `Projects/refactor_loop/` covers 90% of changes
- **WORKSPACE depth pattern**: `Path(__file__).parent.parent` → `.parent.parent.parent` for all 3 Python files

### Risks Identified
1. **Python WORKSPACE depth** - If `.parent` count is wrong, scripts silently resolve to wrong directory. Mitigation: Phase 4 has explicit runtime verification.
2. **Double-prefixing** - Global replace could create `Projects/Projects/refactor_loop/` if run twice. Mitigation: verification step checks for this.

---

## Phases

### Phase 1: Update refactor_loop Internal Paths [Simple]
**Objective:** Update self-referencing paths in all 4 files inside `refactor_loop/`
**Status:** Complete
**Details:** See [phase_1_checklist.md](phase_1_checklist.md)

#### Task 1.1: Update `refactor_loop/WORKER.md` [Simple]
**File:** `refactor_loop/WORKER.md`
- [x] Lines 21, 72, 102, 118, 195: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`

#### Task 1.2: Update `refactor_loop/loop_runner.ps1` [Simple]
**File:** `refactor_loop/loop_runner.ps1`
- [x] Lines 7, 86, 87, 102: update all `refactor_loop/` → `Projects/refactor_loop/`

#### Task 1.3: Update `refactor_loop/loop_runner.sh` [Simple]
**File:** `refactor_loop/loop_runner.sh`
- [x] Lines 9, 73, 85, 86, 112: update all `refactor_loop/` → `Projects/refactor_loop/`

#### Task 1.4: Update `refactor_loop/REFACTOR_LOOP_README.md` [Medium]
**File:** `refactor_loop/REFACTOR_LOOP_README.md`
- [x] Global replace: all 25+ occurrences of `refactor_loop/` → `Projects/refactor_loop/`
- [x] Verify no double-prefixing

#### Task 1.5: Verify Phase 1 [Simple]
- [x] Grep all 4 files for bare `refactor_loop/` not preceded by `Projects/` - expect zero

### Phase 2: Update continuous_loop Internal Paths [Medium]
**Objective:** Update self-referencing paths in all 8 files inside `continuous_loop/` and fix Python WORKSPACE depth
**Status:** Complete
**Details:** See [phase_2_checklist.md](phase_2_checklist.md)

#### Task 2.1-2.5: Update PS1, MD files [Simple each]
- [x] `continuous_loop.ps1` lines 30, 51-55: 6 path vars
- [x] `inner_loop.ps1` lines 2, 13, 14, 16, 134: 5 refs
- [x] `CYCLE_WORKER.md` lines 5, 23, 74, 104, 120, 197: 6 refs
- [x] `SWEEP_WORKER.md` lines 10, 216, 219: 3 refs
- [x] `README.md`: global replace + verify

#### Task 2.6: Fix Python WORKSPACE depth [CRITICAL]
- [x] `populate_cycle_plan.py` line 27: `.parent.parent` → `.parent.parent.parent`
- [x] `populate_cycle_plan.py` line 30: `WORKSPACE / "continuous_loop"` → `WORKSPACE / "Projects" / "continuous_loop"`
- [x] `trim_execution_log.py` line 21: `.parent.parent` → `.parent.parent.parent`
- [x] `trim_execution_log.py` lines 22-23: add `"Projects" /` to path
- [x] `compute_quality_score.py` line 24: `.parent.parent` → `.parent.parent.parent`
- [x] `compute_quality_score.py` line 25: add `"Projects" /` to path
- [x] Update docstrings in all 3 files

#### Task 2.7: Verify Phase 2 [Simple]
- [x] Grep for bare `continuous_loop/` and `refactor_loop/` in all modified files

### Phase 3: Update All External References [Simple]
**Objective:** Update ~18 files outside both directories
**Status:** Complete
**Details:** See [phase_3_checklist.md](phase_3_checklist.md)

#### Task 3.1: CLAUDE.md [Simple]
- [x] Line 5: `refactor_loop/WORKER.md` → `Projects/refactor_loop/WORKER.md`

#### Task 3.2: Projects/scripts/trigger_audit.py [Simple]
- [x] Line 103: `Path("refactor_loop/refactor_plan.md")` → `Path("Projects/refactor_loop/refactor_plan.md")`

#### Task 3.3-3.4: Protocols and Prompts [Simple]
- [x] 2 protocol files, 1 prompt file: update `refactor_loop/` and `continuous_loop/` refs

#### Task 3.5-3.6: Skill files (.claude/ and .agent/) [Simple]
- [x] 9 skill files total: all `refactor_loop/` → `Projects/refactor_loop/`

#### Task 3.7: Review sweep prompts [Simple]
- [x] 5 `Reviews/Prompts/Sweep - *.txt` files: exclusion list `refactor_loop/` → `Projects/refactor_loop/`

#### Task 3.8: Verify Phase 3 [Simple]
- [x] Full repo grep for stale references

### Phase 4: Execute Git Moves and Verify [Simple]
**Objective:** Perform `git mv` for both directories and run all verification checks
**Status:** Complete
**Details:** See [phase_4_checklist.md](phase_4_checklist.md)

#### Task 4.1-4.2: Git moves [Simple]
- [x] `git mv refactor_loop Projects/refactor_loop`
- [x] `git mv continuous_loop Projects/continuous_loop`

#### Task 4.3: Verify Python WORKSPACE [CRITICAL]
- [x] Runtime check that all 3 Python scripts resolve WORKSPACE to project root

#### Task 4.4-4.5: Final grep and git status [Simple]
- [x] Zero stale references, zero double-prefixing
- [x] `git status` shows clean renames

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - all tests pass (establishes baseline) — 11994 passed, 1 skipped

### After Each Phase
- [x] Grep verification confirms no stale paths in modified files
- [x] No double-prefixing (`Projects/Projects/`) exists

### Final Verification
- [x] Python WORKSPACE runtime check on all 3 scripts
- [x] Full repo grep for bare `refactor_loop/` and `continuous_loop/` (excluding logs/historical)
- [x] `git status` shows clean renames (R status)
- [x] Run full test suite: `pytest tests/` (verify no tests reference these paths) — 11994 passed, 1 skipped

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All Phase 3 tasks checked off
- [x] All Phase 4 tasks checked off
- [x] All tests passing
- [x] Grep verification clean
- [ ] User verified

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
