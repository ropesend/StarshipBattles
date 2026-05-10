# Phase 6: Verification & Cleanup [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-221 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Full verification, dead code removal, test suite pass

---

## Tasks

### Task 6.1: Remove dead code [Simple]
**Files:** Multiple
**Tests:** `pytest tests/ --testmon`

- [x] Remove unused imports in modified files (PLANET_RESOURCES from factory, TEAM_1_TEXT from renderer)
- [x] Keep `format_resource_cost()` — still used by renderer for design list items
- [x] No hardcoded column position constants remain
- [x] `draw_selection_highlight()` removed in Phase 4
- [x] No dead `queue_column_positions` references (only in docstring comment)
- [x] Run `pytest tests/` — 13212 passed, 2 skipped

**Notes:** Follow CLAUDE.md eradication policy — no backward compatibility shims.

### Task 6.2: Close BUG-96 [Simple]
**File:** `Debugging/active_bugs/BUG-96.md` (if exists)

- [x] Found BUG-96 — already archived at `Debugging/archived_tickets/BUG-96.md`
- [x] BUG-96 was already resolved; PROJ-221 adds proper per-turn spend columns

**Notes:**

### Task 6.3: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/` — 13212 passed, 2 skipped
- [x] 32 net new tests added (13212 vs 13180 baseline)
- [x] No new failures
- [x] No new skips

**Notes:**

### Task 6.4: Documentation check [Simple]
**Files:** `docs/systems/production_system.md`

- [x] Updated `docs/systems/production_system.md` UI section to mention VirtualTable and per-turn spend columns
- [x] No other docs reference the hardcoded column approach

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Complete"
