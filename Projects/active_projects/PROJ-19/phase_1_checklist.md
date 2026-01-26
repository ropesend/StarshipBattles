# Phase 1: Create Core Protocols

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-19 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Establish the Protocol foundation with all type definitions and TypeGuard utilities

---

## Tasks

### Task 1.1: Create game/core/protocols.py [Medium]
**File:** `game/core/protocols.py` (new file)
**Tests:** `pytest tests/unit/core/test_protocols.py -v` (after Task 1.4)

- [ ] Create file with module docstring explaining purpose
- [ ] Add imports: `Protocol, runtime_checkable, Optional, List, Tuple, Dict, Any, TypeVar, TYPE_CHECKING, TypeGuard`
- [ ] Add TYPE_CHECKING imports for HexCoord (avoid circular imports)
- [ ] Define `ILocatable` Protocol: `location` property
- [ ] Define `INamed` Protocol: `name` property
- [ ] Define `IOwnable` Protocol: `owner_id: Optional[int]` property
- [ ] Define `IStarSystem` Protocol: `stars`, `planets`, `warp_points`, `global_location`, `name`
- [ ] Define `IStar` Protocol: `color`, `mass`, `temperature`, `luminosity`, `star_type`, `name`
- [ ] Define `IPlanet` Protocol: `planet_type`, `resources`, `owner_id`, `name`, `location`
- [ ] Define `IFleet` Protocol: `ships`, `orders`, `location`, `owner_id`, `id`
- [ ] Define `IWarpPoint` Protocol: `destination_id`, `location`
- [ ] Define `ISectorEnvironment` Protocol: `local_hex`, `system`, `calculate_radiation` method
- [ ] Define `ICombatant` Protocol: `team_id`, `is_alive`, `position`
- [ ] Define `IDamageable` Protocol: `current_hp`, `max_hp`, `is_derelict`
- [ ] Verify: File imports without errors

**Notes:**

---

### Task 1.2: Create TypeGuard Functions [Simple]
**File:** `game/core/protocols.py` (append to file)
**Tests:** Manual verification with isinstance checks

- [ ] Add `is_star_system(obj: Any) -> TypeGuard[IStarSystem]`
- [ ] Add `is_star(obj: Any) -> TypeGuard[IStar]`
- [ ] Add `is_planet(obj: Any) -> TypeGuard[IPlanet]`
- [ ] Add `is_fleet(obj: Any) -> TypeGuard[IFleet]`
- [ ] Add `is_warp_point(obj: Any) -> TypeGuard[IWarpPoint]`
- [ ] Add `is_sector_environment(obj: Any) -> TypeGuard[ISectorEnvironment]`
- [ ] Add `is_combatant(obj: Any) -> TypeGuard[ICombatant]`
- [ ] Verify: `python -c "from game.core.protocols import is_fleet; print('OK')"`

**Notes:**

---

### Task 1.3: Update game/core/__init__.py exports [Simple]
**File:** `game/core/__init__.py`
**Tests:** `python -c "from game.core.protocols import IFleet, is_fleet; print('OK')"`

- [ ] Check if __init__.py exists and what it exports
- [ ] Add protocols to exports if needed (or just use direct imports)
- [ ] Verify: No import errors when importing from protocols

**Notes:**

---

### Task 1.4: Create Protocol Unit Tests [Medium]
**File:** `tests/unit/core/test_protocols.py` (new file)
**Tests:** `pytest tests/unit/core/test_protocols.py -v`

- [ ] Create tests/unit/core/ directory if needed
- [ ] Create test_protocols.py with test class
- [ ] Test that Fleet instance satisfies IFleet Protocol (isinstance check)
- [ ] Test that Planet instance satisfies IPlanet Protocol
- [ ] Test that StarSystem instance satisfies IStarSystem Protocol
- [ ] Test that Star instance satisfies IStar Protocol
- [ ] Test that WarpPoint instance satisfies IWarpPoint Protocol
- [ ] Test TypeGuard functions return correct boolean (True for correct type, False for wrong type)
- [ ] Test that None does not satisfy any Protocol
- [ ] Test with mock objects using spec=ClassName
- [ ] Verify: All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run: `pytest tests/unit/core/test_protocols.py -v` - all pass
- [ ] Run: `pytest tests/ --testmon -q` - no regressions
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
