# Phase 1: Quick Wins (ValidationResult + CrewRequired + Validator Primitives)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-176 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add ValidationResult factory methods and migrate all 83 call sites, fix last CrewRequired legacy pattern, create composable validator primitives
**Priority:** Immediate
**Estimated Time:** ~4-6 hours
**Net Lines Saved:** ~71

---

## Tasks

### Task 1.1: Add ValidationResult Factory Methods [Simple]
**File:** `game/core/validation.py`
**Tests:** `pytest tests/unit/core/ -n 4`

- [ ] Read `game/core/validation.py` to confirm current `ValidationResult` dataclass structure
- [ ] Add `success()` static factory method returning `ValidationResult(is_valid=True)`
- [ ] Add `error(message: str)` static factory method returning `ValidationResult(is_valid=False, errors=[message])`
- [ ] Add `errors(messages: List[str])` static factory method returning `ValidationResult(is_valid=False, errors=list(messages))`
- [ ] Write unit tests in `tests/unit/core/test_validation.py`:
  - `test_validation_result_success()` — verify `is_valid=True`, `errors=[]`
  - `test_validation_result_error()` — verify `is_valid=False`, `errors=[msg]`
  - `test_validation_result_errors()` — verify `is_valid=False`, `errors=[msg1, msg2]`
- [ ] Verify: `pytest tests/unit/core/ -n 4` — all pass

**Notes:** [Filled during implementation]

### Task 1.2: Fix CrewRequired Legacy Value Extraction [Simple]
**File:** `game/simulation/components/abilities/crew.py:73`
**Tests:** `pytest tests/unit/simulation/components/abilities/ -n 4`

- [ ] Grep all component JSON data for `"CrewRequired"` with `"amount"` key:
  ```
  grep -r '"amount"' game/data/ simulation_tests/data/ --include="*.json" | grep -i crew
  ```
- [ ] If NO `"amount"` usage found: replace line 73 with `self.amount = int(self._parse_primary_value(data))`
- [ ] If `"amount"` usage IS found: add `fallback_keys` parameter to `_parse_primary_value()` in `base.py` and use `self.amount = int(self._parse_primary_value(data, fallback_keys=('amount',)))`
- [ ] Verify: `pytest tests/unit/simulation/components/abilities/test_crew_abilities.py -v` — all pass
- [ ] Verify: `pytest tests/ -k "crew" -n 4` — all pass

**Notes:** [Filled during implementation]

### Task 1.3: Migrate ValidationResult Call Sites — Strategy Validators [Simple]
**Files:** `game/strategy/validation/superweapon_validator.py` (24 calls), `game/strategy/validation/transfer_validator.py` (17 calls), `game/strategy/validation/colonize_validator.py` (9 calls)
**Tests:** `pytest tests/unit/strategy/validation/ -n 4`

- [ ] In `superweapon_validator.py`: Replace all `ValidationResult(is_valid=False, errors=[...])` with `ValidationResult.error(...)` or `.errors(...)` (24 sites)
- [ ] In `superweapon_validator.py`: Replace all `ValidationResult()` or `ValidationResult(True)` with `ValidationResult.success()`
- [ ] In `transfer_validator.py`: Replace all verbose constructor calls with factory methods (17 sites)
- [ ] In `colonize_validator.py`: Replace all verbose constructor calls with factory methods (9 sites)
- [ ] Verify: `pytest tests/unit/strategy/validation/ -n 4` — all pass

**Notes:** [Filled during implementation]

### Task 1.4: Migrate ValidationResult Call Sites — Command Handlers [Simple]
**Files:** `game/strategy/engine/command_handlers.py` (24 calls), `game/strategy/engine/superweapon_command_handlers.py` (20 calls)
**Tests:** `pytest tests/unit/strategy/engine/ -n 4`

- [ ] In `command_handlers.py`: Replace all verbose constructor calls with factory methods (24 sites)
- [ ] In `superweapon_command_handlers.py`: Replace all verbose constructor calls with factory methods (20 sites)
- [ ] Verify: `pytest tests/unit/strategy/engine/ -n 4` — all pass

**Notes:** [Filled during implementation]

### Task 1.5: Migrate ValidationResult Call Sites — Remaining Files [Simple]
**Files:** `game/simulation/validation/ship_validator.py` (10), `game/ui/screens/race_validator.py` (9), `game/strategy/facade/strategy_session_facade.py` (5), `game/simulation/validation/base.py` (2), `game/strategy/data/race_config.py` (1)
**Tests:** `pytest tests/unit/simulation/validation/ tests/unit/ui/screens/test_race_validator.py tests/unit/strategy/ -n 4`

- [ ] In `ship_validator.py`: Replace verbose constructor calls (10 sites)
- [ ] In `race_validator.py`: Replace verbose constructor calls (9 sites)
- [ ] In `strategy_session_facade.py`: Replace verbose constructor calls (5 sites)
- [ ] In `simulation/validation/base.py`: Replace verbose constructor calls (2 sites)
- [ ] In `race_config.py`: Replace verbose constructor call (1 site)
- [ ] Verify: `pytest tests/unit/simulation/validation/ tests/unit/strategy/ -n 4` — all pass
- [ ] Verify: grep codebase for remaining `ValidationResult(is_valid=False` — should be zero in game/ (tests can keep old style)

**Notes:** [Filled during implementation]

### Task 1.6: Create Validator Shared Primitives [Simple]
**File:** NEW `game/strategy/validation/primitives.py`
**Tests:** NEW `tests/unit/strategy/validation/test_primitives.py`

- [ ] Create `game/strategy/validation/primitives.py` with:
  - `require_fleet(session, fleet_id, empire_id) -> Optional[ValidationResult]`
  - `require_planet(session, planet_id) -> Optional[ValidationResult]`
  - `require_system_at_location(galaxy, location) -> Optional[ValidationResult]`
- [ ] Create `tests/unit/strategy/validation/test_primitives.py` with tests:
  - `test_require_fleet_not_found()` — returns error when fleet doesn't exist
  - `test_require_fleet_wrong_owner()` — returns error when fleet belongs to different empire
  - `test_require_fleet_success()` — returns None when fleet is valid
  - `test_require_planet_not_found()` — returns error
  - `test_require_planet_success()` — returns None
  - `test_require_system_at_location_not_found()` — returns error
  - `test_require_system_at_location_success()` — returns None
- [ ] Verify: `pytest tests/unit/strategy/validation/test_primitives.py -v` — all pass

**Notes:** [Filled during implementation]

### Task 1.7: Adopt Validator Primitives in Strategy Validators [Simple]
**Files:** `game/strategy/validation/superweapon_validator.py`, `game/strategy/validation/colonize_validator.py`, `game/strategy/validation/transfer_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/ -n 4`

- [ ] In `superweapon_validator.py`: Replace inline fleet/planet/system resolution with `require_fleet()`, `require_planet()`, `require_system_at_location()` calls
- [ ] In `colonize_validator.py`: Replace inline fleet/planet resolution with primitive calls
- [ ] In `transfer_validator.py`: Replace inline fleet resolution with primitive calls
- [ ] Verify: `pytest tests/unit/strategy/validation/ -n 4` — all pass

**Notes:** [Filled during implementation]

### Task 1.8: Phase 1 Full Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12` — all pass
- [ ] Verify no remaining `ValidationResult(is_valid=False` in game/ code (grep check)
- [ ] Verify `primitives.py` is used in all 3 validators (grep check)
- [ ] Record test count — should match or exceed baseline

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
