# Phase 6: Update Components JSON

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-08 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate WarpJump costs to ResourceConsumption abilities

---

## Tasks

### Task 6.1: Update Warp Drive Components [Simple]
**File:** `data/components.json`
**Tests:** `pytest tests/integration/test_strategic_abilities.py`

- [x] Update `warp_drive_light` - add ResourceConsumption with trigger: 'warp_jump'
- [x] Update `warp_drive_standard`, `warp_drive_heavy`, `warp_drive_capital` similarly

**Notes:** All 4 warp drives updated:
- `warp_drive_light` (line 1905-1910): 500 energy
- `warp_drive_standard` (line 1930-1935): 1000 energy
- `warp_drive_heavy` (line 1955-1960): 2000 energy
- `warp_drive_capital` (line 1980-1985): 5000 energy

### Task 6.2: Add Test Component with Per-Turn Consumption [Simple]
**File:** `data/components.json`
**Tests:** Manual verification

- [x] Optional test component for per_turn trigger (skipped - not required)

**Notes:** Skipped - not required for functionality, can be added later if needed for testing

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
