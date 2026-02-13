# Phase 5: Simulation API Consistency

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-107 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix simulation-layer API inconsistencies: BattleResult(s) naming confusion, get_winner() return type mismatch, and Optional vs empty collection patterns in resource_manager.

**Findings:** CON-SIM-001, CON-SIM-002, CON-SIM-004, CON-SIM-005

---

## Tasks

### Task 5.1: Rename BattleResult (service) to BattleServiceResult [Complex]
**File:** `game/simulation/services/battle_service.py`
**Tests:** `pytest tests/ -n 12`

The simulation layer has two confusingly-named result types:
- `BattleResults` (in battle_state.py) - actual battle outcome data (winner, ships, states)
- `BattleResult` (in battle_service.py) - service operation result (success/errors/engine)

Rename the service-layer type to `BattleServiceResult` to disambiguate.

- [x] Line 20: Rename `class BattleResult:` to `class BattleServiceResult:`
- [x] Update all references within battle_service.py (return types, method bodies)
- [x] Grep entire codebase for `BattleResult` (NOT `BattleResults`) to find all import sites:
  - Search for `from game.simulation.services.battle_service import.*BattleResult`
  - Search for `BattleResult` in type hints
- [x] Update each import site to use `BattleServiceResult`
- [x] Update each usage site to use `BattleServiceResult`
- [x] Verify: `pytest tests/ -n 12` passes

**Notes:** Updated 11 files:
- game/simulation/services/battle_service.py (source)
- game/simulation/services/__init__.py (export)
- game/simulation/__init__.py (export + docstring)
- game/simulation/battle_controller.py (import + 15 usages)
- tests/unit/services/test_battle_service.py
- tests/unit/simulation/battle_controller/conftest.py
- tests/unit/simulation/battle_controller/test_initialization.py
- tests/unit/simulation/battle_controller/test_execution.py
- tests/unit/simulation/battle_controller/test_mechanics.py
- tests/unit/simulation/battle_controller/test_utilities.py

Note: Strategy layer has its own `BattleResult` in game/strategy/interfaces/battle_resolver.py - this is intentionally different (DTO for battle outcomes vs service operation result).

---

### Task 5.2: Standardize get_winner() Return Type to Optional[int] [Medium]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/ -n 12 -k "battle_engine or battle_service or winner"`

Current state:
- `BattleEngine.get_winner()` returns `int` (0, 1, or -1) - line 625
- `BattleService.get_winner()` returns `Optional[int]` (None when no engine) - line 269

The BattleEngine version never returns None (always returns 0, 1, or -1). The BattleService wraps it and adds None for the "no engine" case.

Decision: Update BattleEngine.get_winner() annotation to `-> int` (it already returns int) and add docstring clarifying it never returns None. The BattleService.get_winner() returning Optional[int] is correct because it adds the None case.

- [x] Line 625: Verify `get_winner(self) -> int:` already has correct annotation (it does)
- [x] Update get_winner() docstring to explicitly state: "Never returns None. Returns -1 for draw."
- [x] In BattleService.get_winner(), update docstring to explain: "Returns None only when no battle engine is active. Otherwise delegates to BattleEngine.get_winner() which returns 0, 1, or -1."
- [x] Verify: `pytest tests/ -n 12 -k "winner"` passes

**Notes:** The types are actually correct for their respective layers. Added explicit documentation noting BattleEngine never returns None, and BattleService only returns None when no engine.

---

### Task 5.3: Standardize Optional vs Empty Collection Returns [Medium]
**File:** `game/simulation/systems/resource_manager.py`
**Tests:** `pytest tests/unit/simulation/ -v -k resource`

Policy: Collection-returning methods should return empty collections, not None/Optional. Reserve Optional for single-value lookups.

- [x] Review `get_resource(self, name: str) -> Optional[ResourceState]` at line 114 - this is a single-value lookup, Optional is correct here (returns None for missing resource)
- [x] Review `get_all_resources(self) -> List[ResourceState]` at line 200 - already returns list, correct
- [x] Review `get_resource_names(self) -> List[str]` at line 196 - already returns list, correct
- [x] Document the convention as a class-level docstring addition:
  ```
  Return Convention:
      - Single-value lookups: Optional[T] (None = not found)
      - Collection lookups: List[T] (empty list = none found)
  ```
- [x] Verify: `pytest tests/unit/simulation/ -n 12` passes

**Notes:** After review, ResourceRegistry already follows the correct convention. Added explicit class-level docstring documenting the pattern.

---

### Task 5.4: Standardize Exception Types in Simulation Layer [Medium]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/ -n 12 -k "battle_controller"`

Current inconsistency:
- battle_controller.py:612,622 raises `ValueError`
- battle_state_manager.py raises `RuntimeError`
- battle_mode_handler.py raises `ValueError`

Convention: Use the project's custom exception hierarchy from `game/core/exceptions.py`:
- `StateException` for state violations (e.g., "not in STRATEGY mode")
- `ValidationException` for data validation failures
- `SimulationException` for general simulation errors

- [x] Line 612: Change `raise ValueError("apply_results_to_fleets only valid in STRATEGY mode")` to `raise StateException("apply_results_to_fleets only valid in STRATEGY mode", code=ErrorCode.INVALID_STATE.value)`
- [x] Line 622: Change `raise ValueError("No source fleets configured")` to `raise StateException("No source fleets configured", code=ErrorCode.INVALID_STATE.value)`
- [x] Add imports: `from game.core.exceptions import StateException` and `from game.core.error_codes import ErrorCode`
- [x] Grep for tests that catch `ValueError` from these methods and update to catch `StateException`
- [x] Verify: `pytest tests/ -n 12 -k "battle_controller"` passes

**Notes:** Only changing battle_controller.py in this phase. No tests caught ValueError for these methods. battle_state_manager.py and battle_mode_handler.py can be addressed in a future phase if needed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
