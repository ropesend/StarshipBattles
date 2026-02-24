# Phase 1: Quick Wins (ValidationResult + CrewRequired + Validator Primitives)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-176 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add ValidationResult factory methods and migrate all 83 call sites, fix last CrewRequired legacy pattern, create composable validator primitives
**Priority:** Immediate
**Estimated Time:** ~4-6 hours
**Net Lines Saved:** ~71

---

## Tasks

### Task 1.1: Add ValidationResult Factory Methods [Simple]
**File:** `game/core/validation.py`
**Tests:** `pytest tests/unit/core/ -n 4`

- [x] Read `game/core/validation.py` to confirm current `ValidationResult` dataclass structure
- [x] Add `success()` static factory method returning `ValidationResult(is_valid=True)`
- [x] Add `error(message: str)` static factory method returning `ValidationResult(is_valid=False, errors=[message])`
- [x] Add `with_errors(messages: List[str])` static factory method (renamed from `errors()` to avoid shadowing dataclass field)
- [x] Write unit tests in `tests/unit/core/test_validation.py`:
  - `test_validation_result_success()` — verify `is_valid=True`, `errors=[]`
  - `test_validation_result_error()` — verify `is_valid=False`, `errors=[msg]`
  - `test_validation_result_with_errors()` — verify `is_valid=False`, `errors=[msg1, msg2]`
- [x] Verify: `pytest tests/unit/core/ -n 4` — all pass

**Notes:** [Filled during implementation]

### Task 1.2: Fix CrewRequired Legacy Value Extraction [Simple]
**File:** `game/simulation/components/abilities/crew.py:73`
**Tests:** `pytest tests/unit/simulation/components/abilities/ -n 4`

- [x] Grep all component JSON data for `"CrewRequired"` with `"amount"` key — tests expect `amount` fallback support
- [x] Added `fallback_keys` parameter to `_parse_primary_value()` in `base.py`
- [x] Updated CrewRequired to use `self.amount = int(self._parse_primary_value(data, fallback_keys=('amount',)))`
- [x] Verify: `pytest tests/unit/simulation/components/abilities/test_crew_abilities.py -v` — 55 passed
- [x] Verify: `pytest tests/ -k "crew" -n 4` — all pass

**Notes:** [Filled during implementation]

### Task 1.3: Migrate ValidationResult Call Sites — Strategy Validators [Simple]
**Files:** `game/strategy/validation/superweapon_validator.py` (24 calls), `game/strategy/validation/transfer_validator.py` (17 calls), `game/strategy/validation/colonize_validator.py` (9 calls)
**Tests:** `pytest tests/unit/strategy/validation/ -n 4`

- [x] In `superweapon_validator.py`: Replaced all verbose constructor calls with factory methods (24 error + 7 success)
- [x] In `transfer_validator.py`: Replaced all verbose constructor calls with factory methods (17 sites)
- [x] In `colonize_validator.py`: Replaced all verbose constructor calls with factory methods (9 sites)
- [x] Verify: `pytest tests/unit/strategy/validation/ -n 4` — 72 passed

**Notes:** [Filled during implementation]

### Task 1.4: Migrate ValidationResult Call Sites — Command Handlers [Simple]
**Files:** `game/strategy/engine/command_handlers.py` (24 calls), `game/strategy/engine/superweapon_command_handlers.py` (20 calls)
**Tests:** `pytest tests/unit/strategy/engine/ -n 4`

- [x] In `command_handlers.py`: Replaced all verbose constructor calls with factory methods (24 sites)
- [x] In `superweapon_command_handlers.py`: Replaced all verbose constructor calls with factory methods (20 sites)
- [x] Verify: `pytest tests/unit/strategy/engine/ -n 4` — 308 passed

**Notes:** Complete — all command handlers migrated

### Task 1.5: Migrate ValidationResult Call Sites — Remaining Files [Simple]
**Files:** `game/simulation/validation/ship_validator.py` (10), `game/ui/screens/race_validator.py` (9), `game/strategy/facade/strategy_session_facade.py` (5), `game/simulation/validation/base.py` (2), `game/strategy/data/race_config.py` (1)
**Tests:** `pytest tests/unit/simulation/validation/ tests/unit/ui/screens/test_race_validator.py tests/unit/strategy/ -n 4`

- [x] In `ship_validator.py`: Replace verbose constructor calls (10 sites)
- [x] In `race_validator.py`: Replace verbose constructor calls (9 sites)
- [x] In `strategy_session_facade.py`: Replace verbose constructor calls (5 sites)
- [x] In `simulation/validation/base.py`: Replace verbose constructor calls (1 site - other was docstring)
- [x] In `race_config.py`: Replace verbose constructor call (1 site)
- [x] Verify: `pytest tests/unit/simulation/validation/ tests/unit/strategy/ -n 4` — 2123 passed
- [x] Verify: grep codebase for remaining `ValidationResult(is_valid=False` — only in validation.py factory methods

**Notes:** All 5 files migrated successfully.

### Task 1.6: Create Validator Shared Primitives [Simple]
**File:** NEW `game/strategy/validation/primitives.py`
**Tests:** NEW `tests/unit/strategy/validation/test_primitives.py`

- [x] Create `game/strategy/validation/primitives.py` with:
  - `require_fleet(session, fleet_id, empire_id) -> Optional[ValidationResult]`
  - `require_planet(session, planet_id) -> Optional[ValidationResult]`
  - `require_system_at_location(galaxy, location) -> Optional[ValidationResult]`
- [x] Create `tests/unit/strategy/validation/test_primitives.py` with tests:
  - `test_require_fleet_not_found()` — returns error when fleet doesn't exist
  - `test_require_fleet_wrong_owner()` — returns error when fleet belongs to different empire
  - `test_require_fleet_success()` — returns None when fleet is valid
  - `test_require_planet_not_found()` — returns error
  - `test_require_planet_success()` — returns None
  - `test_require_system_at_location_not_found()` — returns error
  - `test_require_system_at_location_success()` — returns None
- [x] Verify: `pytest tests/unit/strategy/validation/test_primitives.py -v` — 7 passed

**Notes:** Primitives created. Will be used in Phase 2 command handlers, not validators (see Task 1.7 notes).

### Task 1.7: Adopt Validator Primitives in Strategy Validators [Skipped]
**Files:** `game/strategy/validation/superweapon_validator.py`, `game/strategy/validation/colonize_validator.py`, `game/strategy/validation/transfer_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/ -n 4`

- [x] **SKIPPED**: Strategy validators receive resolved objects (fleet, planet, galaxy) as parameters, NOT IDs. They do not call `session._get_fleet_by_id()` or similar lookup methods.
- [x] The primitives (`require_fleet`, `require_planet`, `require_system_at_location`) are designed for guard-clause validation when resolving IDs to objects.
- [x] These primitives will be used in **command handlers** (Phase 2) instead, where ID resolution happens.

**Notes:** Design mismatch - validators have objects already resolved; primitives designed for ID-to-object guard clauses in command handlers.

### Task 1.8: Phase 1 Full Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12` — 12153 passed, 1 skipped
- [x] Verify no remaining `ValidationResult(is_valid=False` in game/ code — only in validation.py factory methods
- [x] Verify `primitives.py` exists and has tests (used in Phase 2) — 7 tests
- [x] Record test count — 12153 passed (up from 12146 baseline)

**Notes:** Phase 1 complete. +7 new tests for primitives.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
