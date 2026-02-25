# Phase 8: Remaining Scattered Instances [~40 instances]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-193 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Clean up remaining scattered hasattr/getattr instances across game/ui/. Final audit and verification.

---

## Tasks

### Task 8.1: Fleet/build queue UI [Medium]
**Files:** `game/ui/screens/fleet_orders_window.py`, `game/ui/screens/fleet_report_window.py`, `game/ui/screens/build_queue_screen.py`, `game/ui/panels/build_queue_panel_factory.py`, `game/ui/screens/empire_build_queue_formatter.py`, `game/ui/screens/build_queue_controller.py`, `game/ui/screens/build_queue_selector.py`, `game/ui/screens/build_queue_portraits.py`, `game/ui/screens/build_queue_renderer.py`, `game/ui/screens/build_queue_drag_handler.py`
**Tests:** `pytest tests/unit/ui/ -n 4`

- [ ] Audit each file for hasattr/getattr instances
- [ ] Add Protocol type hints (IFleet, IShipInstance, IEmpire, IFacility) where types are known
- [ ] Replace fixable instances with direct typed access
- [ ] Keep self-init guards and scene capability checks
- [ ] Verify: Run tests

**Notes:**

### Task 8.2: Planet list and data source [Simple]
**Files:** `game/ui/panels/planet_list_filters.py`, `game/ui/panels/planet_data_source.py`, `game/ui/screens/planet_selection_window.py`, `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/unit/ui/ -n 4`

- [ ] Add TYPE_CHECKING import: `from game.core.protocols import IPlanet`
- [ ] Type planet params with `'IPlanet'` Protocol
- [ ] Replace getattr with direct access where planet is typed
- [ ] Verify: Run tests

**Notes:**

### Task 8.3: Workshop, test lab, other panels [Simple]
**Files:** `game/ui/screens/workshop_event_router.py`, `game/ui/screens/workshop_screen.py`, `game/ui/screens/workshop_viewmodel.py`, `game/ui/screens/workshop_ship_io.py`, `game/ui/screens/test_lab/screen.py`, `game/ui/screens/test_lab/dialogs.py`, `game/ui/screens/test_lab/data_extractor.py`, `game/ui/panels/design_report_panel.py`, `game/ui/panels/design_stats_panel.py`, `game/ui/panels/modifier_impact_grid.py`, `game/ui/panels/ship_detail_panel.py`, `game/ui/panels/component_modifier_grid_panel.py`
**Tests:** `pytest tests/unit/ui/ -n 4`

- [ ] Audit each file for hasattr/getattr instances
- [ ] Add Protocol type hints where types are known
- [ ] Replace fixable instances with direct access
- [ ] Keep self-init guards, framework checks
- [ ] Verify: Run tests

**Notes:**

### Task 8.4: UI services and renderers [Simple]
**Files:** `game/ui/services/battle_factories.py`, `game/ui/services/screenshot_manager.py`, `game/ui/services/input_mapper.py`, `game/ui/services/ship_io.py`, `game/ui/renderer/game_renderer.py`, `game/ui/renderer/camera.py`, `game/ui/components/table/header.py`
**Tests:** `pytest tests/unit/ui/ -n 4`

- [ ] Audit each file for hasattr/getattr instances
- [ ] Add Protocol type hints where applicable
- [ ] Replace fixable instances
- [ ] Verify: Run tests

**Notes:**

### Task 8.5: Final audit [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Grep remaining `hasattr` in `game/ui/` — count total
- [ ] Grep remaining `getattr` in `game/ui/` — count total
- [ ] Calculate reduction: target ~155 instances eliminated (from ~224 total to ~69)
- [ ] Document remaining legitimate uses (self-init, pygame, dynamic dispatch, dynamic injection) in design.md
- [ ] Run full test suite: `pytest tests/ -n 12` — verify 12,718+ tests passing
- [ ] Manual game verification:
  - [ ] Strategy screen loads, systems/planets/fleets visible
  - [ ] Empire panel renders with race info, aptitudes, environment
  - [ ] Fleet report shows fleet details
  - [ ] Planet list shows all planets with correct data
  - [ ] Builder screen loads, ship stats display correctly
  - [ ] Battle screen renders with ship panels

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
