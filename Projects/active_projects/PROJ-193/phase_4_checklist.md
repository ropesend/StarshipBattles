# Phase 4: Strategy Detail Formatters [27 instances]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-193 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Type params in strategy_detail_fmt.py with Protocol types (IPlanet, IFleet, IFacility, IShipInstance). Audit other strategy screen files.

---

## Tasks

### Task 4.1: strategy_detail_fmt.py [Medium]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Add TYPE_CHECKING imports:
  ```python
  if TYPE_CHECKING:
      from game.core.protocols import IPlanet, IFleet, IFacility, IShipInstance
  ```
- [ ] Type `format_planet_info(planet: 'IPlanet')` — enables direct access to `.populations`, `.max_population`, `.facilities`, `.resources`, `.owner_id`
- [ ] Replace: `getattr(planet, 'populations', [])` → `planet.populations`
- [ ] Replace: `getattr(planet, 'max_population', 0)` → `planet.max_population`
- [ ] Replace: `getattr(planet, 'facilities', [])` → `planet.facilities`
- [ ] Replace: `hasattr(planet, 'owner_id')` → `planet.owner_id is not None`
- [ ] Replace facility getattr calls (lines 141-143): type loop variable `facility: 'IFacility'`
- [ ] Type fleet/ship formatting functions with `'IFleet'` / `'IShipInstance'`
- [ ] Replace: `getattr(ship, 'design_data', None)` → `ship.design_data`
- [ ] Replace: `getattr(ship, 'cargo_contents', {})` → `ship.cargo_contents`
- [ ] Verify: Run tests

**Notes:**

### Task 4.2: strategy_detail_formatter.py [Simple]
**File:** `game/ui/screens/strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Lines 207, 342: `hasattr(self.scene, 'current_empire')`, `hasattr(self.scene, 'turn_engine')` — **keep as-is** (scene is a composite, these check optional subsystems)
- [ ] Document decision in code comment if not already documented

**Notes:**

### Task 4.3: Other strategy screen files [Medium]
**Files:** `strategy_build_queue_manager.py`, `strategy_event_router.py`, `strategy_click_dispatcher.py`, `strategy_game_state_manager.py`, `strategy_renderer.py`, `strategy_superweapons.py`, `strategy_input_handler.py`, `strategy_screen.py`, `strategy_ui.py`, `strategy_window_manager.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Audit each file — classify every hasattr/getattr instance as:
  - **(self-guard)** `hasattr(self, 'panel')` → leave
  - **(scene-check)** `hasattr(self.scene, 'turn_engine')` → leave
  - **(fixable)** `getattr(obj, 'known_attr', default)` → type + direct access
- [ ] Add Protocol type hints where types are known
- [ ] Replace fixable getattr/hasattr with direct access
- [ ] Keep `hasattr(self.scene, ...)` for optional subsystem checks
- [ ] Verify: Run tests

**Notes:**

### Task 4.4: Run tests [Simple]
**Tests:** `pytest tests/unit/ui/ -n 4`

- [ ] Run: `pytest tests/unit/ui/ -n 4` — all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
