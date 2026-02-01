# Phase 2: High Priority Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-41 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update documentation with medium-impact accuracy issues

---

## Tasks

### Task 2.1: Update PATTERNS.md [Simple]
**File:** `docs/architecture/PATTERNS.md`
**Source:** DOC-AR-002 in Architecture Doc Analyst Report

**Issues to fix:**
- [ ] Update Event Bus example signature from `emit(event_type, *args, **kwargs)` to `emit(event_type, data=None)`
- [ ] Verify actual implementation in `game/ui/screens/builder/event_bus.py`

**Verify:**
- [ ] Event Bus example matches actual code
- [ ] All other patterns still accurate (spot-check 2)

**Notes:** [Filled during implementation]

---

### Task 2.2: Update reorg_proposal_ui.md [Simple]
**File:** `docs/architecture/reorg_proposal_ui.md`
**Source:** DOC-AR-005 in Architecture Doc Analyst Report

**Issues to fix:**
- [ ] Mark Phase 1 (Relocation) as COMPLETED
- [ ] Add note documenting what actually happened vs what was proposed
- [ ] Clarify status of Phase 2-4 (implemented, deferred, or abandoned)
- [ ] Consider adding "Status: PARTIALLY_COMPLETED" header

**Verify:**
- [ ] Document clearly indicates what was done vs planned
- [ ] Reader can understand current state of UI reorganization

**Notes:** [Filled during implementation]

---

### Task 2.3: Verify bug_tracker.md [Simple]
**File:** `docs/bug_tracker.md`
**Source:** DOC-OP-001 in Operational Doc Analyst Report

**Issues to fix:**
- [ ] Check if "Heavy Hull mass calculation" bug is still reproducible
- [ ] If not reproducible, move to Resolved Issues section
- [ ] If it's just a placeholder/example, either mark clearly as [EXAMPLE] or remove
- [ ] Consider adding note about GitHub Issues as alternative

**Verify:**
- [ ] Active Issues section contains only actual active bugs
- [ ] No placeholder bugs unmarked

**Notes:** [Filled during implementation]

---

### Task 2.4: Update workshop_refactoring_plan.md [Simple]
**File:** `docs/refactoring/workshop_refactoring_plan.md`
**Source:** DOC-RF-014 in Refactoring Doc Analyst Report

**Issues to fix:**
- [ ] Update status from "Planning Complete - Ready for Implementation" to "COMPLETED"
- [ ] Add completion date
- [ ] Add note that this now serves as historical reference

**Verify:**
- [ ] Status clearly indicates work is done
- [ ] Document useful as reference

**Notes:** [Filled during implementation]

---

### Task 2.5: Update LARGE_FILE_SPLIT_PLAN.md [Simple]
**File:** `docs/refactoring/LARGE_FILE_SPLIT_PLAN.md`
**Source:** DOC-RF-003 in Refactoring Doc Analyst Report

**Issues to fix:**
- [ ] Add note that strategy_scene.py split was COMPLETED (documented in STRATEGY_SCENE_SPLIT_PLAN.md)
- [ ] Mark status for each of the 14 files listed (DONE/PENDING/DEFERRED)
- [ ] Add reference to STRATEGY_SCENE_SPLIT_PLAN.md for details on completed split

**Verify:**
- [ ] Each file in the list has clear status
- [ ] Cross-references to other docs are accurate

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Spot-check: Open `PATTERNS.md` and verify Event Bus signature
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
