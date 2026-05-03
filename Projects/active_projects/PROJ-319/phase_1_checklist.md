# Phase 1: Dead Imports / Params / Unreachable Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-319 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove the 14 verified dead imports, unused parameters, and unreachable assignments identified by audit `Reviews/results/2026-05-02_184210_audit_shrink/`. Trivial deletions, lowest blast radius — used as a fast warm-up before the function/duplication phases.

---

## Tasks

### Task 1.1: Constants — dead enum member [Simple]
**File:** `game/core/constants.py`
**Tests:** `pytest tests/ --testmon`

- [x] Remove dead enum member `GameState.FORMATION = 4` (line 29) — DEEP-01-001
- [x] Verify: `pytest tests/ --testmon` passes; LOC delta ~ -1 (full sharded suite ran: 16374 tests, 16371 passed, 3 skipped, 0 failed)

---

### Task 1.2: Context — unused module alias [Simple]
**File:** `game/context.py`
**Tests:** `pytest tests/ --testmon`

- [x] Remove unused import `_ccm_mod` (line 116, alias of `crew_capacity_mod` already imported separately at line 138 as `_ccm_module`) — C1
- [x] Verify: `pytest tests/ --testmon` passes; LOC delta ~ -1 (full sharded suite ran: 16374 tests, 16371 passed, 3 skipped, 0 failed)

---

### Task 1.3: Strategy data — galaxy.py unused parameter [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/strategy/data/`

- [x] Remove unused parameter `naming_data_path` from function at line 624 (and update all call sites if any pass it) — C2 (verified: zero callers pass it; production callers in `game_session.py:384` and `turn_state_snapshot.py:84` both single-arg)
- [x] Verify: `pytest tests/strategy/data/` passes; LOC delta ~ -3 (full sharded suite passed)

---

### Task 1.4: Strategy data — stars.py unused parameter [Simple]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/strategy/data/`

- [x] Remove unused parameter `age_ratio` from function at line 303 (all 3 callers omit it per verifier) — C3 (callers at stars.py:576, 662, 714 all single-arg; tests in test_stars.py also single-arg)
- [x] Verify: `pytest tests/strategy/data/` passes; LOC delta ~ -3 (full sharded suite passed)

---

### Task 1.5: Strategy data — planet_gen.py unused import [Simple]
**File:** `game/strategy/data/planet_gen.py`
**Tests:** `pytest tests/strategy/data/`

- [x] Remove unused import `MASS_MOON` (line 23) — C4
- [x] Verify: `pytest tests/strategy/data/` passes; LOC delta ~ -1 (full sharded suite passed)

---

### Task 1.6: Strategy data — design_metadata.py unused stdlib import [Simple]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/strategy/data/`

- [x] Remove unused `import warnings` (line 13) — DEEP-04-003
- [x] Verify: `pytest tests/strategy/data/` passes; LOC delta ~ -1 (full sharded suite passed)

---

### Task 1.7: Strategy engine — planet_action_engine.py unused import [Simple]
**File:** `game/strategy/engine/planet_action_engine.py`
**Tests:** `pytest tests/strategy/engine/`

- [x] Remove unused import `get_shield_info` (line 25) — C5
- [x] Verify: `pytest tests/strategy/engine/` passes; LOC delta ~ -1 (full sharded suite passed)

---

### Task 1.8: Strategy facade — fleet_dto.py dead TYPE_CHECKING import [Simple]
**File:** `game/strategy/facade/dto/fleet_dto.py`
**Tests:** `pytest tests/strategy/facade/`

- [x] Remove unused TYPE_CHECKING import `FleetType` (line 11). Confirm no string annotation `"FleetType"` exists in the file before deleting. — C6 (also removed now-unused `TYPE_CHECKING` from `typing` import; was the only consumer)
- [x] Verify: `pytest tests/strategy/facade/` passes; LOC delta ~ -1 (full sharded suite passed)

---

### Task 1.9: Strategy services — action_time_resolver.py unreachable return [Simple]
**File:** `game/strategy/services/action_time_resolver.py`
**Tests:** `pytest tests/strategy/services/`

- [x] Remove unreachable `return 1` (line 115) — the if/else above already returns on every branch — C7
- [x] Verify: `pytest tests/strategy/services/` passes; LOC delta ~ -1 (full sharded suite passed)

---

### Task 1.10: UI panels — modifier_impact_grid.py unused parameter [Simple]
**File:** `game/ui/panels/modifier_impact_grid.py`
**Tests:** `pytest tests/ui/panels/` (or `pytest tests/ --testmon` if no targeted path)

- [x] Remove unused parameter `sig_digits` from function at line 273 (all 3 callers omit it per verifier) — C8 (callers at lines 262, 264, 270 all single-arg; updated docstring to remove sig_digits mention)
- [x] Verify: `pytest tests/ --testmon` passes; LOC delta ~ -2 (full sharded suite passed)

---

### Task 1.11: UI screens — test_lab/screen.py unused dialog import [Simple]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** `pytest tests/ --testmon`

- [x] Remove unused import `ConfirmationDialog` (line 32). Keep paired `JSONPopup` import (still live). — C9
- [x] Verify: `pytest tests/ --testmon` passes; LOC delta ~ -1 (full sharded suite ran: 16374 tests, 16371 passed, 3 skipped, 0 failed)

---

### Task 1.12: UI services — ship_io_adapter.py dead TYPE_CHECKING import [Simple]
**File:** `game/ui/services/ship_io_adapter.py`
**Tests:** `pytest tests/ui/services/` (or `pytest tests/ --testmon` if no targeted path)

- [x] Remove unused TYPE_CHECKING import `ShipIOType` (line 19). Confirm no string annotation `"ShipIOType"` exists in the file. — C10 (also removed now-unused `TYPE_CHECKING` import; was the only consumer)
- [x] Verify: `pytest tests/ --testmon` passes; LOC delta ~ -1 (full sharded suite ran: 16374 tests, 16371 passed, 3 skipped, 0 failed)

---

### Task 1.13: UI screens — galaxy_test/system_mode.py unused constant import [Simple]
**File:** `game/ui/screens/galaxy_test/system_mode.py`
**Tests:** `pytest tests/ --testmon`

- [x] Remove unused import `STAR_FALLBACK` (line 17) — PD1 (upgraded from PRODUCT_DECISION by the audit's verifier)
- [x] Verify: `pytest tests/ --testmon` passes; LOC delta ~ -1 (full sharded suite ran: 16374 tests, 16371 passed, 3 skipped, 0 failed)

---

### Task 1.14: UI screens — build_queue_selector.py redundant assignment [Simple]
**File:** `game/ui/screens/build_queue_selector.py`
**Tests:** `pytest tests/ --testmon`

- [x] Remove the first redundant `y_offset = 0` (actually line 97; the audit listed line 99). The same assignment is repeated at line 100 with no read between, so delete the line-97 copy. — DEEP-04-005
- [x] Verify: `pytest tests/ --testmon` passes; LOC delta ~ -1 (full sharded suite ran: 16374 tests, 16371 passed, 3 skipped, 0 failed)

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] `python Tools/test_sharded/test_sharded.py` passes (16374 tests, 0 failures, 3 skipped)
- [x] Total LOC delta is ~ -19 (sum of per-task deltas)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2

_Source audit: `Reviews/results/2026-05-02_184210_audit_shrink/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
