# Phase 1: Create Core Protocols

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-19 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Establish the Protocol foundation with all type definitions and TypeGuard utilities

---

## Tasks

### Task 1.1: Create game/core/protocols.py [Medium]
**File:** `game/core/protocols.py` (new file)
**Tests:** `pytest tests/unit/core/test_protocols.py -v` (after Task 1.4)

- [x] Create file with module docstring explaining purpose
- [x] Add imports: `Protocol, runtime_checkable, Optional, List, Tuple, Dict, Any, TypeVar, TYPE_CHECKING, TypeGuard`
- [x] Add TYPE_CHECKING imports for HexCoord (avoid circular imports)
- [x] Define `ILocatable` Protocol: `location` property
- [x] Define `INamed` Protocol: `name` property
- [x] Define `IOwnable` Protocol: `owner_id: Optional[int]` property
- [x] Define `IStarSystem` Protocol: `stars`, `planets`, `warp_points`, `global_location`, `name`
- [x] Define `IStar` Protocol: `color`, `mass`, `temperature`, `luminosity`, `star_type`, `name`
- [x] Define `IPlanet` Protocol: `planet_type`, `resources`, `owner_id`, `name`, `location`
- [x] Define `IFleet` Protocol: `ships`, `orders`, `location`, `owner_id`, `id`
- [x] Define `IWarpPoint` Protocol: `destination_id`, `location`
- [x] Define `ISectorEnvironment` Protocol: `local_hex`, `system`, `calculate_radiation` method
- [x] Define `ICombatant` Protocol: `team_id`, `is_alive`, `position`
- [x] Define `IDamageable` Protocol: `current_hp`, `max_hp`, `is_derelict`
- [x] Verify: File imports without errors

**Notes:** Created game/core/protocols.py with 11 Protocol definitions and proper TYPE_CHECKING guards.

---

### Task 1.2: Create TypeGuard Functions [Simple]
**File:** `game/core/protocols.py` (append to file)
**Tests:** Manual verification with isinstance checks

- [x] Add `is_star_system(obj: Any) -> TypeGuard[IStarSystem]`
- [x] Add `is_star(obj: Any) -> TypeGuard[IStar]`
- [x] Add `is_planet(obj: Any) -> TypeGuard[IPlanet]`
- [x] Add `is_fleet(obj: Any) -> TypeGuard[IFleet]`
- [x] Add `is_warp_point(obj: Any) -> TypeGuard[IWarpPoint]`
- [x] Add `is_sector_environment(obj: Any) -> TypeGuard[ISectorEnvironment]`
- [x] Add `is_combatant(obj: Any) -> TypeGuard[ICombatant]`
- [x] Verify: `python -c "from game.core.protocols import is_fleet; print('OK')"`

**Notes:** 7 TypeGuard functions added. Each wraps isinstance() with Protocol for IDE type narrowing.

---

### Task 1.3: Update game/core/__init__.py exports [Simple]
**File:** `game/core/__init__.py`
**Tests:** `python -c "from game.core.protocols import IFleet, is_fleet; print('OK')"`

- [x] Check if __init__.py exists and what it exports
- [x] Add protocols to exports if needed (or just use direct imports)
- [x] Verify: No import errors when importing from protocols

**Notes:** Direct imports from protocols module work fine. Following existing codebase pattern of direct module imports.

---

### Task 1.4: Create Protocol Unit Tests [Medium]
**File:** `tests/unit/core/test_protocols.py` (new file)
**Tests:** `pytest tests/unit/core/test_protocols.py -v`

- [x] Create tests/unit/core/ directory if needed
- [x] Create test_protocols.py with test class
- [x] Test that Fleet instance satisfies IFleet Protocol (isinstance check)
- [x] Test that Planet instance satisfies IPlanet Protocol
- [x] Test that StarSystem instance satisfies IStarSystem Protocol
- [x] Test that Star instance satisfies IStar Protocol
- [x] Test that WarpPoint instance satisfies IWarpPoint Protocol
- [x] Test TypeGuard functions return correct boolean (True for correct type, False for wrong type)
- [x] Test that None does not satisfy any Protocol
- [x] Test with mock objects using spec=ClassName
- [x] Verify: All tests pass

**Notes:** Created 25 comprehensive tests. Written FIRST following TDD. All tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run: `pytest tests/unit/core/test_protocols.py -v` - all pass (25 tests)
- [x] Run: `pytest tests/ --testmon -q` - no regressions (26 affected tests pass)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
