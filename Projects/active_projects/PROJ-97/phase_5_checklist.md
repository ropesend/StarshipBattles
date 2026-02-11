# Phase 5: Remove Shipyard ResourceStorage

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-97 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove dead ResourceStorage abilities from shipyard components

---

## Tasks

### Task 5.1: Remove ResourceStorage from components.json [Simple]
**File:** `data/components.json`
**Tests:** `pytest tests/ -n 12`

- [ ] Remove `"ResourceStorage": {"Metals": 1000, "Organics": 500}` from `space_shipyard` abilities
- [ ] Remove `"ResourceStorage": {"Metals": 500, "Organics": 250}` from `fleet_space_yard` abilities
- [ ] Run full test suite to confirm zero breakage

**Notes:** Confirmed dead code by swarm analysis: never read by any engine, UI, or test.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
