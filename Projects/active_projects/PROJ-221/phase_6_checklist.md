# Phase 6: Verification & Cleanup [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-221 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Full verification, dead code removal, test suite pass

---

## Tasks

### Task 6.1: Remove dead code [Simple]
**Files:** Multiple
**Tests:** `pytest tests/ --testmon`

- [ ] Remove any unused imports in modified files (BuildQueueRenderer, BuildQueuePanelFactory, BuildQueueScreen)
- [ ] Remove `format_resource_cost()` from `build_queue_helpers.py` if no longer used by renderer
- [ ] Remove hardcoded column position constants if any remain
- [ ] Remove `draw_selection_highlight()` from renderer if not already done in Phase 4
- [ ] Check for dead `queue_column_positions` references anywhere
- [ ] Run `pytest tests/ --testmon` — no regressions

**Notes:** Follow CLAUDE.md eradication policy — no backward compatibility shims.

### Task 6.2: Close BUG-96 [Simple]
**File:** `Debugging/active_bugs/BUG-96.md` (if exists)

- [ ] Find BUG-96 file
- [ ] Mark as superseded by PROJ-221
- [ ] Move to resolved/closed bugs directory if applicable

**Notes:**

### Task 6.3: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: 13180+ passed (baseline was 13180 passed, 2 skipped)
- [ ] Investigate any new failures
- [ ] Verify no new skips beyond the baseline 2

**Notes:**

### Task 6.4: Documentation check [Simple]
**Files:** `docs/systems/production_system.md`

- [ ] Check if `docs/systems/production_system.md` references BuildQueueScreen column layout — update if so
- [ ] Verify no other docs reference the hardcoded column approach
- [ ] Update `docs/systems/production_system.md` UI section to mention VirtualTable integration if appropriate

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
