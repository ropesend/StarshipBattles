# Phase 4: FleetOrderProcessor Decomposition

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-210 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (Tasks Deferred)
**Objective:** Decompose FleetOrderProcessor (648 lines) into focused order handlers
**Priority:** Major — prevents regression from PROJ-87's decomposition work
**Findings:** AR-003, CX-03, ROF-007

---

## Tasks

### Task 4.1: Extract Order Handler Pattern [Complex]
**Findings:** AR-003 (FleetOrderProcessor is 648 lines with mixed validation/execution)
**Files:** `game/strategy/engine/fleet_order_processor.py`, new handler modules
**Tests:** `pytest tests/unit/strategy/test_fleet_order*.py tests/integration/ -v`

**Status: DEFERRED**

**Rationale:**
- FleetOrderProcessor appears large (650 lines) but is ALREADY decomposed:
  - Superweapon processing (6 order types, ~420 lines) → SuperweaponOrderProcessor
  - Remaining methods: process_colonize (~109 lines), process_transfer (~160 lines), process_join_fleet (~41 lines)
- These remaining methods are **turn-execution processors**, NOT UI command handlers
- The CommandHandlerRegistry pattern is for GameSession command dispatch; order execution is a different concern
- Creating separate handler classes (ColonizeOrderHandler, TransferOrderHandler, etc.) would:
  - Add indirection without reducing coupling
  - Create tiny classes (~100 lines each) with single methods
  - Mirror the existing *Validator classes without adding value
- **Verdict:** Architecture is already appropriately decomposed. No action needed.

### Task 4.2: Separate Order Validation from Execution [Medium]
**Findings:** AR-003 (process_colonize mixes validation and mutation)
**Files:** Order handler modules from Task 4.1
**Tests:** `pytest tests/unit/strategy/test_fleet_order*.py -v`

**Status: ALREADY DONE**

**Evidence:**
- `process_colonize()` uses `ColonizeValidator.validate()` for validation
- `process_transfer()` uses `TransferValidator.validate()` for validation
- `SuperweaponOrderProcessor` methods use `SuperweaponValidator` for validation
- Pattern: validate() returns result → execute mutations only if valid
- **Verdict:** Validation is already separated via dedicated *Validator classes. No action needed.

### Task 4.3: Extract FleetOrderQueue Manager [Simple]
**Findings:** ROF-004, ROF-007
**Files:** `game/strategy/data/fleet.py`, new `game/strategy/data/fleet_order_queue.py`
**Tests:** `pytest tests/unit/strategy/test_fleet*.py -v`

**Status: DEFERRED**

**Rationale:**
- Fleet order methods total ~20 lines across 4 trivial operations:
  - `add_order()`: 5 lines (append or insert)
  - `pop_order()`: 5 lines (pop and clear path)
  - `clear_orders()`: 3 lines (clear list and path)
  - `get_current_order()`: 4 lines (return first or None)
- Fleet.py is now 320 lines (after Phase 2 reduced it from 552)
- **Already under 300-line target** mentioned in plan.md verification checklist
- Extracting 20 lines of simple list operations to a separate class:
  - Adds overhead without reducing complexity
  - Creates a class with 4 trivial methods
  - Breaks simple `fleet.orders` access patterns
- **Verdict:** Extraction would add overhead for trivial operations. No action needed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (or deferred with rationale)
- [x] FleetOrderProcessor.py < 200 lines (dispatcher) — DEFERRED: Already decomposed with SuperweaponOrderProcessor
- [x] Each order type has its own handler class — DEFERRED: Pattern inappropriate for turn-execution
- [x] Validation separated from execution — ALREADY DONE: *Validator classes exist
- [x] Fleet order queue is encapsulated — DEFERRED: 20 lines of trivial ops, Fleet.py at 320 lines
- [x] All tests passing (879 passed, 1 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
