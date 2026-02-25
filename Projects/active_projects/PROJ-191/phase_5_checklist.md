# Phase 5: Miscellaneous Cleanup [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-191 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Address remaining scattered duck typing patterns (~15 instances).

---

## Tasks

### Task 5.1: Command handlers and game session [Simple]
**Files:** `game/strategy/engine/command_handlers.py` (L300-303), `game/strategy/engine/game_session.py` (L172), `game/strategy/services/area_effect_manager.py` (L74)
**Tests:** `pytest tests/unit/strategy/engine/ tests/unit/strategy/services/ -n 12`

- [ ] `command_handlers.py` L300-303: Replace defensive getattr chain `getattr(session, 'turn_engine', None)` → `getattr(turn_engine, '_registries', None)` → `getattr(registries, 'components', None)` with direct access: `session.turn_engine._registries.components` (GameSession always has turn_engine after initialization)
- [ ] `game_session.py` L172: Remove `hasattr(fleet, 'can_use_warp')` — Fleet always has `can_use_warp()` method
- [ ] `game_session.py` L118-119: Keep `hasattr(category, 'value')` / `hasattr(event_type, 'value')` — these handle both Enum and string args
- [ ] `area_effect_manager.py` L74: Remove `hasattr(galaxy, 'get_zones_at_global_hex')` — Galaxy always has this since PROJ-189
- [ ] Run tests

**Notes:**

### Task 5.2: Fleet navigation service (3 instances) [Simple]
**File:** `game/strategy/services/fleet_navigation_service.py`
**Tests:** `pytest tests/unit/strategy/fleet_navigation/ -n 12`

- [ ] L151: `hasattr(target_fleet, 'location')` → `target_fleet is not None` (Fleet always has location)
- [ ] L454: `getattr(fleet.orders[0], 'execution_progress', 0)` → `fleet.orders[0].execution_progress` (FleetOrder always has execution_progress, default 0)
- [ ] L636: `hasattr(target_fleet, 'location')` → `target_fleet is not None`
- [ ] Run tests

**Notes:**

### Task 5.3: Cargo transfer service (5 instances) [Simple]
**File:** `game/strategy/services/cargo_transfer_service.py`
**Tests:** `pytest tests/unit/strategy/services/test_cargo_transfer_service.py`

- [ ] L40: `hasattr(fleet, 'location')` → `fleet.location` (FleetInfo DTO always has location field)
- [ ] L70: `getattr(fleet_info, 'passengers_current', 0)` → `fleet_info.passengers_current` (FleetInfo always has this field)
- [ ] L100: `hasattr(planet_info, 'population_details')` → direct access (PlanetInfo always has this field)
- [ ] L112: `getattr(planet_info, 'total_population', 0)` → `planet_info.total_population` (PlanetInfo always has this)
- [ ] L139-167 (`get_inventory_items`): Replace hasattr type discrimination with `isinstance(obj_info, FleetInfo)` / `isinstance(obj_info, PlanetInfo)` checks; add imports for FleetInfo, PlanetInfo
- [ ] Run tests

**Notes:** FleetInfo has `passengers_current` (default 0). PlanetInfo has `total_population` (default 0) and `population_details` (default empty tuple).

### Task 5.4: Full test suite verification [Simple]
- [ ] `pytest tests/ -n 12` — verify baseline maintained (12699+ passed)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` — baseline maintained
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
