# Phase 4: DTO Enhancements & Read Path

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-208 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Enhance DTOs and facade query methods to reduce raw domain access
**Priority:** Minor — read-path improvements, lower risk than write-path fixes
**Findings Addressed:** DCA-007, DCA-008, DCA-010, DCA-011, DCA-012

---

## Task 4.1: Add capabilities field to FleetInfo DTO [Simple]
**File:** `game/strategy/facade/dto/fleet_dto.py`
**Addresses:** DCA-012

- [x] Add `capabilities: Tuple[str, ...] = field(default_factory=tuple)` to FleetInfo
- [x] Update FleetInfo factory/creation to populate from `fleet.capabilities.list_abilities()`
- [x] Write tests for the new field
- [x] Verify: `pytest tests/ -n 12`

**Notes:**
- Added `list_abilities()` method to FleetCapabilityCalculator
- Added `list_ship_abilities()` function to component_inspector
- Added capabilities field to FleetInfo dataclass
- 8 new tests in test_fleet_dto_capabilities.py

### Task 4.2: Replace isinstance checks with protocol guards [Simple]
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Addresses:** DCA-008

- [x] Replace `isinstance(selected_object, Planet)` with `is_planet(selected_object)` (lines 48-49)
- [x] Replace `isinstance(selected_object, Fleet)` with `is_fleet(selected_object)` (lines ~210-211)
- [x] Remove Planet/Fleet imports if no longer needed
- [x] Verify tests pass

**Notes:** Planet/Fleet imports kept in TYPE_CHECKING for type hints. Test mocks patched to handle Protocol isinstance.

### Task 4.3: Use facade.get_fleets_at_hex() in fleet_ops [Simple]
**File:** `game/ui/screens/strategy_fleet_ops.py`
**Addresses:** DCA-010

- [x] Replace raw `emp.fleets` iteration in `get_fleet_at_hex()` (lines 48-62)
- [x] Use `self.facade.get_fleets_at_hex(hex_coord)` instead
- [x] Convert callers to work with FleetInfo DTOs (use fleet_id for command dispatch)
- [x] Verify tests pass

**Notes:**
- get_fleet_at_hex() now returns Optional[FleetInfo] instead of Fleet
- Updated execute_intercept() to use target_fleet.fleet_id
- Updated handle_join_designation() to use target_fleet_info.fleet_id
- Updated tests to mock facade.get_fleets_at_hex() and use fleet_id attribute

### Task 4.4: Add facade methods for game state queries [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Addresses:** DCA-011

- [x] Add `get_scuttle_events(turn: int) -> List[dict]` to facade
- [x] Add `get_save_path() -> Optional[str]` to facade
- [x] Update `strategy_game_state_manager.py` to use new facade methods
- [x] Write tests for new facade methods
- [x] Verify tests pass

**Notes:**
- get_scuttle_events() returns list of dicts (not ScuttleEvent objects)
- Updated _show_scuttle_notifications() to use dict access
- 5 new tests in TestGameStateQueries class

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] FleetInfo has capabilities field
- [x] No isinstance(obj, Planet/Fleet) in build_queue_manager
- [x] fleet_ops uses facade.get_fleets_at_hex()
- [x] Full test suite passes: `pytest tests/ -n 12` (12929 passed, 4 bug_13 failures pre-existing)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Project Complete"
