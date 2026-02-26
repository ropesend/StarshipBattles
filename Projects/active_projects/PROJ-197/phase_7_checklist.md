# Phase 7: Final Audit & Cleanup [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-197 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Verify zero raw tuples remain, final test suite run, cleanup

---

## Tasks

### Task 7.1: Raw Tuple Audit [Simple]
**Tests:** N/A (audit only)

- [ ] Search all `game/ui/` files for raw RGB tuple patterns `(\d+, \d+, \d+)`
- [ ] Verify ONLY hits are in `game/ui/colors.py` and `game/ui/screens/test_lab/theme.py` definitions
- [ ] If any raw tuples remain in other files, fix them
- [ ] Document count: "X remaining definition-only files"

**Notes:**

### Task 7.2: Import Cleanup [Simple]
**Tests:** `pytest tests/ --testmon`

- [ ] Check no unused color imports exist in modified files
- [ ] Check `game/ui/colors.py` has no orphan constants (all used somewhere)
- [ ] Verify no circular imports introduced
- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 7.3: Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run `pytest tests/ -n 12` (full suite, not testmon)
- [ ] Verify: 12,734+ passed, 0 failures
- [ ] Document final test count

**Notes:**

### Task 7.4: Regression Test Check [Simple]
**Tests:** `pytest tests/regression/ -v`

- [ ] Check if regression tests need updates for new color conventions
- [ ] Run `pytest tests/regression/ -v` explicitly

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Zero raw tuples outside definition files
- [ ] Full test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
