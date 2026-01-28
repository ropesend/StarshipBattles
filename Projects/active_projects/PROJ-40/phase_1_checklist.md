# Phase 1: Critical Architecture Fixes

**Status:** Not Started
**Estimated Effort:** 30 minutes
**Priority:** Highest - Address first

## Overview
Address the critical duplicate initialization issue in Ship class.

> **Note:** This phase was reduced from 3 tasks to 1 after Category 3 audit verification:
> - Task 1.1 (NEW-CORE-001) REMOVED - TYPE_CHECKING guard is already correct
> - Task 1.3 (NEW-UI-001) MOVED to Phase 12 - UI layer violations consolidated

---

## Tasks

### 1.1 Fix Duplicate Attribute Initialization (NEW-SIM-001)
**Location:** `game/simulation/entities/ship.py:92, 135`
**Issue:** `total_defense_score` initialized twice with different values (0.0 then 1.0).

- [ ] Identify correct initial value for `total_defense_score`
- [ ] Remove duplicate assignment (keep line 135 with value 1.0 based on usage)
- [ ] Add comment explaining why default is 1.0 (not 0.0)
- [ ] Search for any code that depends on 0.0 default
- [ ] Run tests: `pytest tests/unit/entities/test_ship.py -v`

**Acceptance:** Single initialization with documented rationale

---

## Removed Tasks (Audit Verification)

### ~~1.1 Fix Core → Strategy Layer Violation (NEW-CORE-001)~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** The import is correctly guarded by `TYPE_CHECKING` at line 36-37 in protocols.py. This is the proper pattern for type-only imports.

### ~~1.2 Fix UI → Internal Layer Violations (NEW-UI-001)~~
**Status:** MOVED to Phase 12
**Reason:** Consolidated with all UI layer remediation tasks. See [phase_12_checklist.md](phase_12_checklist.md).

---

## Verification

- [ ] Run ship tests: `pytest tests/unit/entities/test_ship.py -v`
- [ ] Verify no import errors: `python -c "from game.simulation.entities.ship import Ship"`

---

## Notes
- This phase is now a quick win (30 minutes)
- Proceed to Phase 2 after completion
