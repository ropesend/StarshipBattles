# Phase 1: Critical Architecture Fixes

**Status:** Complete
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
**Location:** `game/simulation/entities/ship.py:125, 167` (was 92, 135 before line shifts)
**Issue:** `total_defense_score` initialized twice with different values (0.0 then 1.0).

- [x] Identify correct initial value for `total_defense_score`
- [x] Remove duplicate assignment (keep line 167 with value 1.0 based on usage)
- [x] Add comment explaining why default is 1.0 (not 0.0)
- [x] Search for any code that depends on 0.0 default
- [x] Run tests: `pytest tests/unit/entities/test_ship.py -v`

**Acceptance:** Single initialization with documented rationale

**Notes:**
- Removed line 125 (`self.total_defense_score = 0.0`)
- Kept line 167 (`self.total_defense_score: float = 1.0`)
- Added comment explaining 1.0 is neutral baseline before ShipStatsCalculator computes actual value
- Added new test class `TestTotalDefenseScoreInitialization` in `tests/unit/entities/test_ship.py`
- No code depended on the 0.0 initial value

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

- [x] Run ship tests: `pytest tests/unit/entities/test_ship.py -v`
- [x] Verify no import errors: `python -c "from game.simulation.entities.ship import Ship"`

---

## Notes
- This phase is now a quick win (30 minutes)
- Proceed to Phase 2 after completion
