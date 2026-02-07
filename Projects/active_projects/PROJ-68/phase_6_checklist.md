# Phase 6: TRANSFER Order

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add OrderType.TRANSFER with command, validator, and processor. Transfers cargo between fleet and colony.

**Depends on:** Phase 1 (populations on planet), Phase 5 (cargo on ships), Phase 4 (CargoStorage ability)

---

## Tasks

### Task 6.1: Order Type & Command [Simple]
**File:** `game/strategy/data/fleet.py`
**File:** `game/strategy/engine/commands.py`
**Tests:** `pytest tests/unit/strategy/engine/test_transfer_order.py`

- [ ] Add `TRANSFER = auto()` to `OrderType` enum
- [ ] Update `FleetOrder.to_dict()` / `from_dict()` to handle TRANSFER target (dict with `direction`, `cargo_type`, `amount`, `planet_id`)
- [ ] Add `IssueTransferCommand(Command)` dataclass to commands.py:
  - `fleet_id: int`, `planet_id: int`, `cargo_type: str`, `direction: str` ("load"/"unload"), `amount: int` (0 = all)

**Notes:**

---

### Task 6.2: TransferValidator [Medium]
**New file:** `game/strategy/validation/transfer_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_transfer_validator.py`

- [ ] `TransferValidator.validate(galaxy, fleet, planet, cargo_type, direction, amount) -> ValidationResult`
  - Fleet must be at planet's system location
  - Planet must be colonized (owner_id not None)
  - For "load": colony must have population of requested type (for passengers), fleet must have cargo space
  - For "unload": fleet must have cargo to unload
  - Validate `direction` is "load" or "unload"
  - Validate `cargo_type` is recognized

**Notes:**

---

### Task 6.3: FleetOrderProcessor.process_transfer() [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_transfer_order.py`

- [ ] Add `process_transfer(fleet, empire, galaxy) -> TransferResult` method
  - Extract transfer params from order target dict
  - Validate via TransferValidator
  - For "load" passengers: subtract from colony `SpeciesPopulation.count`, add to fleet cargo via `load_cargo_to_fleet()`
  - For "unload" passengers: subtract from fleet cargo, add to colony population (find or create `SpeciesPopulation`)
  - Complete the order
- [ ] Update `process_end_turn_orders()` to handle `OrderType.TRANSFER`

**Notes:**

---

### Task 6.4: Command Dispatch [Simple]
**File:** `game/strategy/engine/game_session.py`

- [ ] Add handler for `IssueTransferCommand` in command dispatch

**Notes:**

---

### Task 6.5: Tests [Medium]
**New file:** `tests/unit/strategy/validation/test_transfer_validator.py`

- [ ] `test_valid_load_passengers`
- [ ] `test_valid_unload_passengers`
- [ ] `test_fleet_not_at_colony_fails`
- [ ] `test_uncolonized_planet_fails`
- [ ] `test_no_cargo_space_fails`
- [ ] `test_no_cargo_to_unload_fails`
- [ ] `test_invalid_direction_fails`

**New file:** `tests/unit/strategy/engine/test_transfer_order.py`

- [ ] `test_process_transfer_load_passengers_from_colony`
- [ ] `test_process_transfer_unload_passengers_to_colony`
- [ ] `test_transfer_partial_amount`
- [ ] `test_transfer_all_when_amount_zero`
- [ ] `test_transfer_creates_species_population_if_missing`
- [ ] `test_transfer_order_serialization_roundtrip`
- [ ] `test_transfer_command_dispatch`
- [ ] Verify: all test files pass
- [ ] Verify: `pytest tests/ --testmon` — no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
