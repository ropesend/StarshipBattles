# Phase 3: Layer Coupling

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-11 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Establish clean layer boundaries between UI, Strategy, and Simulation
**Priority:** MAJOR

---

## Tasks

### Task 3.1: AR-02/MOD-UI-04 - Create GameFacade for UI [High]
**Files:** `game/ui/screens/battle_scene.py`, `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/unit/ui/`

**Issue:** UI directly accesses game internals (engine.ships, engine.projectiles, turn_engine methods).

**Implementation:**
- [ ] Define BattleViewInterface with clear contracts:
  - `get_live_ships() -> List[ShipInfo]`
  - `get_projectiles() -> List[ProjectileInfo]`
  - `is_simulation_over() -> bool`
- [ ] Define StrategyViewInterface:
  - `validate_order(fleet, order) -> ValidationResult`
  - `request_order(fleet, order) -> Result`
  - `get_galaxy_view() -> GalaxyInfo`
- [ ] Implement facades that wrap game objects
- [ ] Update UI to use facades instead of direct access
- [ ] Create DTOs (Data Transfer Objects) for UI consumption

**Notes:** UI should never import game entity classes directly.

---

### Task 3.2: AR-04 - Fix UI-to-Strategy Coupling [Medium]
**Files:** 20+ imports from UI to Strategy
**Tests:** `pytest tests/unit/ui/`

**Issue:** UI screens directly depend on strategy data classes (Planet, Fleet, DesignMetadata).

**Implementation:**
- [ ] Create ViewModel layer for strategy data:
  - `PlanetViewModel` - UI representation of Planet
  - `FleetViewModel` - UI representation of Fleet
  - `DesignViewModel` - UI representation of Design
- [ ] ViewModels created from_entity() in facade layer
- [ ] UI imports only viewmodels
- [ ] Strategy module doesn't know about UI

**Notes:** ViewModels are simple dataclasses with display-ready data.

---

### Task 3.3: MOD-STR-06 - Fix Strategy-to-UI Violation [Simple]
**File:** `game/strategy/data/fleet.py:140`
**Tests:** `pytest tests/unit/strategy/test_fleet.py`

**Issue:** Fleet module imports from UI layer (`from game.ui.screens.fleet_report_filters import has_warp_capability`).

**Implementation:**
- [ ] Move `has_warp_capability` to FleetMobilityService
- [ ] Update Fleet to use service method
- [ ] Remove UI import from strategy layer
- [ ] Verify no other strategy→UI imports exist

**Notes:** Quick fix - 1 hour. Low risk.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No UI→Game direct imports (only facades)
- [ ] No Strategy→UI imports
- [ ] ViewModel layer established
- [ ] All tests passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
