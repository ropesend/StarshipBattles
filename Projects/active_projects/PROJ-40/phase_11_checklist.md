# Phase 11: Original Findings Completion

**Status:** Not Started
**Estimated Effort:** 2-3 hours
**Priority:** Low

## Overview
Complete remaining items from the original legacy cleanup review that were not fully addressed.

---

## Tasks

### 11.1 Consolidate CrewCapacity Logic (LDF-03)
**Location:** 3 locations with duplicated fallback logic
**Status:** Still Present
**Effort:** Medium

- [ ] Identify all 3 locations with CrewCapacity fallback pattern
- [ ] Create single `get_crew_capacity()` function
- [ ] Place in appropriate module (game/simulation/utils.py?)
- [ ] Update all callers to use single function
- [ ] Add deprecation warning for legacy format
- [ ] Run: `pytest tests/ -v -k crew`

---

### 11.2 Remove _ValidatorProxy (LPA-04)
**Location:** `game/simulation/entities/ship.py` (lines 26-31 approx)
**Status:** Still Present
**Effort:** Simple

- [ ] Verify `_ValidatorProxy` has 0 usages in codebase
- [ ] Search: `grep -r "_ValidatorProxy" game/`
- [ ] Delete the class definition
- [ ] Run: `pytest tests/unit/entities/test_ship.py -v`

---

### 11.3 Delete modifiers_v1_backup.json (DC-03)
**Location:** `data/modifiers_v1_backup.json`
**Status:** Still Present
**Effort:** Simple

- [ ] Verify file has 0 references in codebase
- [ ] Search: `grep -r "modifiers_v1_backup" .`
- [ ] Delete the file
- [ ] Ensure git history preserves the content
- [ ] Run: `pytest tests/ -v -k modifier`

---

### 11.4 Clean Remaining Tools/ Scripts (DC-04)
**Location:** `Tools/` directory
**Status:** Partially Fixed
**Effort:** Simple

- [ ] List all scripts in Tools/
- [ ] Identify which are actively used
- [ ] Remove unused scripts
- [ ] Document remaining scripts
- [ ] Run any remaining tools to verify they work

---

### 11.5 Complete PROJ Comment Cleanup (MIG-01)
**Location:** 237 instances across 14 files
**Status:** Partially Fixed (84% reduction achieved)
**Effort:** Medium

- [ ] List remaining PROJ comment files
- [ ] Review each comment for relevance
- [ ] Remove completed/obsolete PROJ comments
- [ ] Update any that are still valid
- [ ] Run: `grep -r "PROJ-" game/ | wc -l`

---

## Verification

- [ ] Run full test suite: `pytest`
- [ ] Verify no dead code references
- [ ] Check for any new issues introduced

---

## Summary of Original Review Progress

| ID | Severity | Title | Original Status | Action |
|----|----------|-------|-----------------|--------|
| LDF-03 | Major | CrewCapacity fallback logic | Still duplicated 3x | Task 11.1 |
| LPA-04 | Minor | _ValidatorProxy unused | Still present, 0 usages | Task 11.2 |
| DC-03 | Minor | modifiers_v1_backup.json | Still present, 0 references | Task 11.3 |
| DC-04 | Minor | Debug scripts in Tools/ | Some remain | Task 11.4 |
| MIG-01 | Minor | PROJ comment cleanup | 84% done (237 remain) | Task 11.5 |

---

## Notes
- These are relatively simple cleanup tasks
- All were identified in the original review but not completed
- Completing these will achieve 100% remediation of original findings
