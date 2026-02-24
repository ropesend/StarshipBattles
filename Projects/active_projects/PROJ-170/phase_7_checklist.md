# Phase 7: Catch Quality Cleanup + Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-170 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix remaining catch quality issues and perform final verification.
**Estimated Effort:** 45 min

---

## Tasks

### Task 7.1: Fix bare except in scripts [Simple]
**File:** `scripts/apply_resource_costs.py`
**Tests:** N/A (script file)

- [ ] Find the bare `except: pass` block
- [ ] Replace with specific exception type (likely `except (ValueError, KeyError) as e: logger.warning(...)`)
- [ ] Verify script still runs: `python scripts/apply_resource_costs.py --help` (or similar)

**Notes:**

### Task 7.2: Add logging to silent fallbacks [Simple]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/ -k battle_panel`

- [ ] Find silent `except` block(s) that swallow errors without logging
- [ ] Add `logger.warning(f"...: {e}")` to each
- [ ] Verify: no crash on normal gameplay path

**File:** `game/ui/panels/race_environment_panel.py`
**Tests:** `pytest tests/unit/ui/ -k race_environment`

- [ ] Find silent `except` block(s) that swallow errors without logging
- [ ] Add `logger.warning(f"...: {e}")` to each
- [ ] Verify: no crash on normal gameplay path

**Notes:**

### Task 7.3: Final Audit [Medium]
**Tests:** Full test suite

- [ ] Run full test suite: `pytest tests/ -n 12` — must match or exceed baseline (12,016 passed)
- [ ] Grep verification — generic raises remaining should only be KEEP items:
  ```
  rg "raise ValueError" game/ --count
  rg "raise RuntimeError" game/ --count
  rg "raise TypeError" game/ --count
  ```
  Expected: only protocol-compliant raises (HexCoord math, take_damage, subscribe, dict-like lookups)
- [ ] Grep verification — custom exception adoption:
  ```
  rg "raise (Validation|State|Frozen|Resource|Missing|Persistence|Simulation|Component|Formula)Exception" game/ --count
  ```
  Expected: ~90+ occurrences (28 existing + 63 migrated)
- [ ] Grep verification — error code adoption:
  ```
  rg "ErrorCode\." game/ --count
  ```
  Expected: ~80+ occurrences
- [ ] Document final counts in plan.md Current State

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes: 12,016+ passed
- [ ] Generic raise count verified (only KEEP items remain)
- [ ] Custom exception count verified (~90+)
- [ ] Error code usage count verified (~80+)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete — awaiting audit"
- [ ] Update plan.md Completion Checklist
