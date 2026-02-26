# Phase 5: Miscellaneous Cleanup [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-191 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address remaining scattered duck typing patterns (~15 instances).

---

## Tasks

### Task 5.1: Command handlers and game session [Simple]
**Files:** `game/strategy/engine/command_handlers.py` (L300-303), `game/strategy/engine/game_session.py` (L172), `game/strategy/services/area_effect_manager.py` (L74)
**Tests:** `pytest tests/unit/strategy/engine/ tests/unit/strategy/services/ -n 12`

- [x] `command_handlers.py` L300-303: Replace defensive getattr chain `getattr(session, 'turn_engine', None)` → `getattr(turn_engine, '_registries', None)` → `getattr(registries, 'components', None)` with direct access: `session.turn_engine._registries.components` (GameSession always has turn_engine after initialization)
- [x] `game_session.py` L172: Remove `hasattr(fleet, 'can_use_warp')` — Fleet always has `can_use_warp()` method
- [x] `game_session.py` L118-119: Keep `hasattr(category, 'value')` / `hasattr(event_type, 'value')` — these handle both Enum and string args (kept as-is, legitimate dual-type handling)
- [x] `area_effect_manager.py` L74: Remove `hasattr(galaxy, 'get_zones_at_global_hex')` — Galaxy always has this since PROJ-189
- [x] Run tests — 424 passed

**Notes:** Removed defensive hasattr/getattr patterns. Galaxy always has get_zones_at_global_hex.

### Task 5.2: Fleet navigation service (3 instances) [Simple]
**File:** `game/strategy/services/fleet_navigation_service.py`
**Tests:** `pytest tests/unit/strategy/fleet_navigation/ -n 12`

- [x] L151: `hasattr(target_fleet, 'location')` → `target_fleet is not None` (Fleet always has location)
- [x] L454: `getattr(fleet.orders[0], 'execution_progress', 0)` → `fleet.orders[0].execution_progress` (FleetOrder always has execution_progress, default 0)
- [x] L636: `hasattr(target_fleet, 'location')` → `target_fleet is not None`
- [x] Run tests — 74 passed (2 obsolete tests deleted)

**Notes:** Deleted 2 obsolete tests testing "target lacking location" - Fleet always has location. test_get_destination_move_to_fleet_no_target covers None target case.

### Task 5.3: Cargo transfer service (5 instances) [Simple]
**File:** `game/strategy/services/cargo_transfer_service.py`
**Tests:** `pytest tests/unit/strategy/services/test_cargo_transfer_service.py`

- [x] L40: `hasattr(fleet, 'location')` → `fleet.location` (FleetInfo DTO always has location field)
- [x] L70: `getattr(fleet_info, 'passengers_current', 0)` → `fleet_info.passengers_current` (FleetInfo always has this field)
- [x] L100: `hasattr(planet_info, 'population_details')` → direct access (PlanetInfo always has this field)
- [x] L112: `getattr(planet_info, 'total_population', 0)` → `planet_info.total_population` (PlanetInfo always has this)
- [x] L139-167 (`get_inventory_items`): Replace hasattr type discrimination with `isinstance(obj_info, FleetInfo)` / `isinstance(obj_info, PlanetInfo)` checks; add imports for FleetInfo, PlanetInfo
- [x] Run tests — 21 passed

**Notes:** Deleted 1 obsolete test (fleet without location). Updated get_inventory_items tests to use actual FleetInfo/PlanetInfo dataclass instances instead of generic MagicMocks.

### Task 5.4: Full test suite verification [Simple]
- [x] `pytest tests/ -n 12` — 12697 passed, 1 skipped

**Notes:**
- Deleted 1 obsolete test: test_target_fleet_without_location_cancels_order (Fleet always has location)
- Added get_zones_at_global_hex() to 2 MockGalaxy classes in integration tests (Galaxy always has this since PROJ-189)
- Total obsolete tests deleted this phase: 4

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` — baseline maintained (12697 passed, 1 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
