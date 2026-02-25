# Phase 4: Strategy Detail Formatters [27 instances]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-193 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Type params in strategy_detail_fmt.py with Protocol types (IPlanet, IFleet, IFacility, IShipInstance). Audit other strategy screen files.

---

## Tasks

### Task 4.1: strategy_detail_fmt.py [Medium]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Add TYPE_CHECKING imports:
  ```python
  if TYPE_CHECKING:
      from game.core.protocols import IPlanet, IFleet, IFacility, IShipInstance
  ```
- [x] Type `format_planet_info(planet: 'IPlanet')` — enables direct access to `.populations`, `.max_population`, `.facilities`, `.resources`, `.owner_id`
- [x] Replace: `getattr(planet, 'populations', [])` → `planet.populations`
- [x] Replace: `getattr(planet, 'max_population', 0)` → `planet.max_population`
- [x] Replace: `getattr(planet, 'facilities', [])` → `planet.facilities`
- [x] Replace: `hasattr(planet, 'owner_id')` → `planet.owner_id is not None`
- [x] Replace facility getattr calls (lines 141-143): type loop variable `facility: 'IFacility'`
- [x] Type fleet/ship formatting functions with `'IFleet'` / `'IShipInstance'`
- [x] Replace: `getattr(ship, 'design_data', None)` → `ship.design_data`
- [x] Replace: `getattr(ship, 'cargo_contents', {})` → `ship.cargo_contents`
- [x] Verify: Run tests

**Notes:**
- Added `get_calculated_stats()` method to IShipInstance protocol
- Fixed test_facilities_display to use `is_operational` instead of `status`
- Kept intentional getattr for order.target (polymorphic) and fleet.construction_queue (optional)

### Task 4.2: strategy_detail_formatter.py [Simple]
**File:** `game/ui/screens/strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Lines 207, 342: `hasattr(self.scene, 'current_empire')`, `hasattr(self.scene, 'turn_engine')` — **keep as-is** (scene is a composite, these check optional subsystems)
- [x] Document decision in code comment if not already documented

**Notes:**
- Added comments documenting intentional hasattr for optional scene subsystems

### Task 4.3: Other strategy screen files [Medium]
**Files:** `strategy_build_queue_manager.py`, `strategy_event_router.py`, `strategy_click_dispatcher.py`, `strategy_game_state_manager.py`, `strategy_renderer.py`, `strategy_superweapons.py`, `strategy_input_handler.py`, `strategy_screen.py`, `strategy_ui.py`, `strategy_window_manager.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Audit each file — classify every hasattr/getattr instance as:
  - **(self-guard)** `hasattr(self, 'panel')` → leave
  - **(scene-check)** `hasattr(self.scene, 'turn_engine')` → leave
  - **(fixable)** `getattr(obj, 'known_attr', default)` → type + direct access
- [x] Add Protocol type hints where types are known
- [x] Replace fixable getattr/hasattr with direct access
- [x] Keep `hasattr(self.scene, ...)` for optional subsystem checks
- [x] Verify: Run tests

**Notes:**
Fixes made:
- strategy_renderer.py: `hasattr(sys, 'storms')` → `sys.storms` (added storms to IStarSystem)
- strategy_renderer.py: `getattr(planet, 'diameter_hexes', 11.0)` → `planet.diameter_hexes`
- strategy_camera_nav.py: `hasattr(obj, 'location')` → `is_planet(obj) or is_warp_point(obj)`
- strategy_screen.py: `hasattr(obj, 'location')` → `is_planet(obj) or is_warp_point(obj)`
- strategy_build_queue_manager.py: `getattr(fleet, 'id', id(fleet))` → `fleet.id` with IFleet type

Intentional patterns kept (scene/self guards, optional subsystems):
- strategy_build_queue_manager.py: hasattr(self._screen, 'build_queue_screen'), getattr(session, 'save_path')
- strategy_event_router.py: hasattr(ui.scene, ...) for optional callbacks
- strategy_click_dispatcher.py: hasattr(self.scene, 'galaxy')
- strategy_colonization.py: hasattr/getattr for scene.galaxy zone lookups
- strategy_game_state_manager.py: getattr for turn_engine, last_scuttle_events
- strategy_input_handler.py: hasattr for optional build_queue_screen, modal checks
- strategy_renderer.py: getattr for scene.input_mode (optional)
- strategy_superweapons.py: hasattr for UI methods
- strategy_ui.py: hasattr for self.system_tree, scene._get_object_asset, current_empire
- strategy_window_manager.py: hasattr for scene.facade

### Task 4.4: Run tests [Simple]
**Tests:** `pytest tests/unit/ui/ -n 4`

- [x] Run: `pytest tests/unit/ui/ -n 4` — all pass

**Notes:**
- 12711 passed, 1 skipped

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
