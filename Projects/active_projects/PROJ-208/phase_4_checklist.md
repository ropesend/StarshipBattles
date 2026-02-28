# Phase 4: DTO Enhancements & Read Path

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-208 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Enhance DTOs and facade query methods to reduce raw domain access
**Priority:** Minor — read-path improvements, lower risk than write-path fixes
**Findings Addressed:** DCA-007, DCA-008, DCA-010, DCA-011, DCA-012

---

## Task 4.1: Add capabilities field to FleetInfo DTO [Simple]
**File:** `game/strategy/facade/dto/fleet_dto.py`
**Addresses:** DCA-012

- [ ] Add `capabilities: Tuple[str, ...] = field(default_factory=tuple)` to FleetInfo
- [ ] Update FleetInfo factory/creation to populate from `fleet.capabilities.list_abilities()`
- [ ] Write tests for the new field
- [ ] Verify: `pytest tests/ -n 12`

**Notes:** This eliminates 6 raw Fleet accesses in `strategy_superweapons.py`.

### Task 4.2: Replace isinstance checks with protocol guards [Simple]
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Addresses:** DCA-008

- [ ] Replace `isinstance(selected_object, Planet)` with `is_planet(selected_object)` (lines 48-49)
- [ ] Replace `isinstance(selected_object, Fleet)` with `is_fleet(selected_object)` (lines ~210-211)
- [ ] Remove Planet/Fleet imports if no longer needed
- [ ] Verify tests pass

**Notes:** Protocol guards already exist and are used elsewhere (strategy_screen.py).

### Task 4.3: Use facade.get_fleets_at_hex() in fleet_ops [Simple]
**File:** `game/ui/screens/strategy_fleet_ops.py`
**Addresses:** DCA-010

- [ ] Replace raw `emp.fleets` iteration in `get_fleet_at_hex()` (lines 48-62)
- [ ] Use `self.facade.get_fleets_at_hex(hex_coord)` instead
- [ ] Convert callers to work with FleetInfo DTOs (use fleet_id for command dispatch)
- [ ] Verify tests pass

**Notes:** Low-hanging fruit — facade method already exists.

### Task 4.4: Add facade methods for game state queries [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Addresses:** DCA-011

- [ ] Add `get_scuttle_events(turn: int) -> List[dict]` to facade
- [ ] Add `get_save_path() -> Optional[str]` to facade
- [ ] Update `strategy_game_state_manager.py` to use new facade methods
- [ ] Write tests for new facade methods
- [ ] Verify tests pass

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] FleetInfo has capabilities field
- [ ] No isinstance(obj, Planet/Fleet) in build_queue_manager
- [ ] fleet_ops uses facade.get_fleets_at_hex()
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
