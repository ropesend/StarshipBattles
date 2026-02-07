# PROJ-67: Fleet Space Yards

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-67` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-67 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fleet Space Yard Component & Data Model | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. BUILD Order & Movement Blocking | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Fleet Production Engine | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. BuildContext Abstraction & UI Generalization | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Strategy Screen Integration | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Save/Load & Edge Cases | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-07
**Active Phase:** Phase 6
**Last Action:** Phase 5 complete - Fleet build button, BUILD order UI, move blocking
**Next Action:** Begin Phase 6 - Save/Load & Edge Cases
**Blockers:** None

## Overview
Add fleet-based space yard capability to the game. Ships with a space yard component allow their fleet to build other ships, fighters, satellites, and (when near a planet) complexes. This extends the existing planet-based production system to work with fleets, reusing as much code as possible.

## Goals
- Create a `fleet_space_yard` component that can be equipped on ships
- Add `OrderType.BUILD` to lock building fleets in place
- Extend `ProductionEngine` to process fleet build queues
- Generalize `BuildQueueScreen` to work with both planets and fleets
- Enforce: complexes only buildable at same hex as a planet; ships/fighters/satellites always
- Built ships join the building fleet directly

## Scope
**In:**
- New `fleet_space_yard` component using existing `SpaceShipyardAbility`
- `OrderType.BUILD` with movement blocking
- Fleet `construction_queue` field with serialization
- `Fleet.has_space_shipyard` property
- `BuildContext` protocol for UI abstraction
- Generalized `BuildQueueScreen`, `BuildQueueController`
- Fleet production processing in `ProductionEngine`
- Strategy screen integration (open build queue for fleet)
- Save/load support for fleet build queues
- Comprehensive TDD test coverage

**Out:**
- Resource costs for fleet building (deferred - time-only for now)
- Construction speed bonuses affecting build time (deferred)
- Max ship mass validation (deferred)
- AI fleet building behavior
- Fleet yard combat implications (yard destruction during build)

## Key Files
| Component | File Path |
|-----------|-----------|
| Space Yard Ability | `game/simulation/components/abilities/harvester.py` |
| Ability Registry | `game/simulation/components/abilities/__init__.py` |
| Components JSON | `data/components.json` |
| Fleet Data | `game/strategy/data/fleet.py` |
| Planet Data | `game/strategy/data/planet.py` |
| Production Engine | `game/strategy/engine/production_engine.py` |
| Fleet Order Processor | `game/strategy/engine/fleet_order_processor.py` |
| Fleet Movement Engine | `game/strategy/engine/fleet_movement_engine.py` |
| Turn Engine | `game/strategy/engine/turn_engine.py` |
| Build Queue Screen | `game/ui/screens/build_queue_screen.py` |
| Build Queue Controller | `game/ui/panels/build_queue_controller.py` |
| Build Queue Portraits | `game/ui/panels/build_queue_portraits.py` |
| Build Queue Drag Handler | `game/ui/panels/build_queue_drag_handler.py` |
| Strategy Screen | `game/ui/screens/strategy_screen.py` |
| Fleet DTO | `game/strategy/facade/dto/fleet_dto.py` |
| Strategy Facade | `game/strategy/facade/strategy_session_facade.py` |
| Strategy Interfaces | `game/strategy/interfaces/engines.py` |
| Fleet Speed Calculator | `game/strategy/services/fleet_speed_calculator.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Fleet Space Yard Component & Data Model [Medium]
**Objective:** Create the fleet space yard component, add construction_queue to Fleet, add has_space_shipyard property.
**Status:** Not Started

#### Task 1.1: Add `fleet_space_yard` Component to components.json [Simple]
**File:** `data/components.json`
**Tests:** `pytest tests/unit/simulation/components/ -k space`
- [ ] Add new component entry `fleet_space_yard` near existing `space_shipyard` (~line 1893)
- [ ] Set `allowed_vehicle_types: ["Ship"]` (different from complex's `["Planetary Complex"]`)
- [ ] Set `type: "SpaceShipyard"` (same type string)
- [ ] Use `SpaceShipyard` ability with `construction_speed_bonus: 1.0, max_ship_mass: 100000`
- [ ] Add appropriate mass, hp, crew, resource cost values
- [ ] Add `major_classification: "Production"`
- [ ] Verify component loads correctly: run `pytest tests/unit/simulation/components/`

#### Task 1.2: Add `construction_queue` to Fleet [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k fleet`
- [ ] Add `self.construction_queue: list = []` in `Fleet.__init__()` (after line 62)
- [ ] Add `construction_queue` to `Fleet.to_dict()` serialization (line ~571)
- [ ] Add `construction_queue` restoration in `Fleet.from_dict()` (line ~597)
- [ ] Write test: fleet initializes with empty construction_queue
- [ ] Write test: fleet serialization round-trips construction_queue

#### Task 1.3: Add `has_space_shipyard` Property to Fleet [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k "fleet and shipyard"`
- [ ] Add `has_space_shipyard` property to Fleet class
- [ ] Implementation: check if any ship in fleet has a component with `SpaceShipyard` ability
- [ ] Use `ShipInstance.get_calculated_stats()` or inspect `design_data` layers (follow Planet.has_space_shipyard pattern)
- [ ] Write test: fleet without yard ship returns False
- [ ] Write test: fleet with yard ship returns True
- [ ] Write test: fleet with destroyed yard ship returns False (if ship not combat_capable)

#### Task 1.4: Add `can_build_type()` Method to Fleet [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k "fleet and build_type"`
- [ ] Add `can_build_type(self, vehicle_type: str, galaxy=None) -> bool` method
- [ ] Ships/fighters/satellites: always True if has_space_shipyard
- [ ] Complexes: True only if has_space_shipyard AND at same hex as a planet (requires galaxy param)
- [ ] Write test: fleet with yard can build ships
- [ ] Write test: fleet without yard cannot build ships
- [ ] Write test: fleet with yard at planet hex can build complexes
- [ ] Write test: fleet with yard NOT at planet hex cannot build complexes

**Notes:** The galaxy parameter is needed for planet-proximity checks. For tests, mock a galaxy with `get_planets_at_global_hex()`.

---

### Phase 2: BUILD Order & Movement Blocking [Medium]
**Objective:** Add OrderType.BUILD, integrate with fleet order processing, block movement while building.
**Status:** Not Started

#### Task 2.1: Add OrderType.BUILD [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k order`
- [ ] Add `BUILD = auto()` to `OrderType` enum (after line 14)
- [ ] Update `FleetOrder.to_dict()` - BUILD orders don't need a target (line ~27)
- [ ] Update `Fleet.from_dict()` order restoration to handle BUILD type (line ~615)
- [ ] Write test: BUILD order serializes/deserializes correctly

#### Task 2.2: Movement Blocking for BUILD Order [Medium]
**File:** `game/strategy/engine/fleet_movement_engine.py`
**Tests:** `pytest tests/unit/strategy/ -k movement`
- [ ] In `collect_movements()`: skip fleets whose current order is BUILD
- [ ] Write test: fleet with BUILD order is NOT included in movement collection
- [ ] Write test: fleet with MOVE order IS still included
- [ ] Write test: fleet with BUILD order followed by MOVE doesn't move until BUILD is popped

#### Task 2.3: BUILD Order Processing in FleetOrderProcessor [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/ -k "order_processor and build"`
- [ ] Add BUILD handling in `process_end_turn_orders()` method
- [ ] BUILD order should NOT be auto-completed (it stays until player cancels or queue empties)
- [ ] If fleet's construction_queue becomes empty, auto-complete the BUILD order
- [ ] Write test: BUILD order persists across turns while queue has items
- [ ] Write test: BUILD order auto-completes when queue empties
- [ ] Write test: BUILD order can be manually cancelled (pop_order)

#### Task 2.4: Prevent Movement Orders While Building [Medium]
**File:** `game/strategy/data/fleet.py` (or fleet validation service)
**Tests:** `pytest tests/unit/strategy/ -k "fleet and order"`
- [ ] Add `is_building` property to Fleet: `return self.get_current_order() and self.get_current_order().type == OrderType.BUILD`
- [ ] Determine where to block MOVE orders (UI layer vs data layer) - UI layer preferred
- [ ] Write test: `is_building` returns True when BUILD is current order
- [ ] Write test: `is_building` returns False when no order or MOVE order

#### Task 2.5: Update Fleet DTO [Simple]
**File:** `game/strategy/facade/dto/fleet_dto.py`
**Tests:** `pytest tests/unit/strategy/facade/ -k fleet`
- [ ] Add `is_building: bool` to `FleetInfo` dataclass
- [ ] Add `has_space_shipyard: bool` to `FleetInfo` dataclass
- [ ] Add `construction_queue_size: int` to `FleetInfo` dataclass
- [ ] Update `FleetInfo.from_fleet()` to populate new fields
- [ ] Write tests for new DTO fields

---

### Phase 3: Fleet Production Engine [Medium]
**Objective:** Extend ProductionEngine to process fleet build queues. Built ships join the building fleet.
**Status:** Not Started

#### Task 3.1: Add Fleet Production Processing [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`
- [ ] Add `process_fleet_production()` method to ProductionEngine
- [ ] Iterate empires → fleets → fleets with BUILD order and non-empty construction_queue
- [ ] For each fleet: same queue processing as planets (decrement turns, spawn on completion)
- [ ] Shipyard check: fleet must still have space_shipyard (not destroyed mid-build)
- [ ] Write test: fleet with BUILD order and queue item gets turns decremented
- [ ] Write test: fleet without BUILD order is skipped
- [ ] Write test: fleet without shipyard pauses production

#### Task 3.2: Fleet Ship Spawning [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`
- [ ] Add `_spawn_fleet_ship()` method
- [ ] Create ShipInstance from design (same as `_spawn_ship` pattern)
- [ ] Add ship to building fleet via `fleet.add_ship_instance()`
- [ ] Increment design's times_built counter
- [ ] Write test: completed ship joins the building fleet
- [ ] Write test: fleet speed recalculates after ship added

#### Task 3.3: Fleet Complex Spawning [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`
- [ ] Add `_spawn_fleet_complex()` method
- [ ] Validate fleet is still at planet hex (galaxy lookup)
- [ ] If valid: create PlanetaryFacility and add to planet.facilities (same as `_spawn_complex`)
- [ ] If not valid (fleet moved): log warning, skip (item already removed from queue)
- [ ] Write test: complex spawns to planet when fleet is at planet hex
- [ ] Write test: complex spawn fails gracefully when fleet not at planet

#### Task 3.4: Integrate Fleet Production into TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/`
- [ ] Call `self.production_engine.process_fleet_production()` after `process_production()` in `process_turn()` (line ~201)
- [ ] Pass `empires`, `galaxy`, `save_path` parameters
- [ ] Write test: turn processing includes fleet production phase

#### Task 3.5: Update IProductionEngine Interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** N/A (interface only)
- [ ] Add `process_fleet_production()` to `IProductionEngine` interface
- [ ] Match signature: `(self, empires: List, galaxy: Any = None, save_path: Optional[str] = None) -> None`

---

### Phase 4: BuildContext Abstraction & UI Generalization [Complex]
**Objective:** Create BuildContext protocol, refactor BuildQueueScreen/Controller to work with both planets and fleets.
**Status:** Not Started

#### Task 4.1: Create BuildContext Protocol [Simple]
**File:** `game/strategy/data/build_context.py` (new file)
**Tests:** `pytest tests/unit/strategy/ -k build_context`
- [ ] Create `BuildContext` Protocol class with properties: `name`, `construction_queue`, `has_space_shipyard`, `owner_id`
- [ ] Add `can_build_type(vehicle_type: str) -> bool` method
- [ ] Add `context_type` property returning `"planet"` or `"fleet"` (for UI branching)
- [ ] Write test: Planet satisfies BuildContext protocol
- [ ] Write test: Fleet satisfies BuildContext protocol

#### Task 4.2: Add BuildContext Compliance to Planet [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/ -k planet`
- [ ] Add `can_build_type()` method to Planet (complexes always, ships only if has_space_shipyard)
- [ ] Add `context_type` property returning `"planet"`
- [ ] Write test: planet.can_build_type("complex") always True
- [ ] Write test: planet.can_build_type("ship") requires has_space_shipyard

#### Task 4.3: Generalize BuildQueueController [Medium]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/ -k build_queue` and `pytest tests/integration/ui/build_queue_screen/`
- [ ] Change `self.planet` to `self.build_context` (or use Union type)
- [ ] Update `__init__` parameter: `planet: Planet` → `build_context` (accepts Planet or Fleet)
- [ ] Update `add_to_queue()`: use `self.build_context.can_build_type()` instead of hardcoded `has_space_shipyard` check (line 129)
- [ ] Update diagnostic logging to use `self.build_context.name` instead of `self.planet` specifics
- [ ] For fleet context: skip facility-specific logging (lines 119-126)
- [ ] Write test: controller works with Planet build context
- [ ] Write test: controller works with Fleet build context
- [ ] Write test: controller blocks complex for fleet not at planet

#### Task 4.4: Generalize BuildQueueScreen [Complex]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/`
- [ ] Change constructor: `planet: Planet` → `build_context` (accept Planet or Fleet)
- [ ] Store `self.build_context` instead of `self.planet`
- [ ] Update `_create_planet_report_panel()`: conditionally show planet report OR fleet info panel
- [ ] For fleet context: create a simple fleet info header instead of PlanetReportPanel
- [ ] Update `_refresh_queue_display()`: use `self.build_context.construction_queue`
- [ ] Update `handle_event()`: reference `self.build_context` instead of `self.planet`
- [ ] Pass `self.build_context` to controller and drag handler
- [ ] Update category filtering: hide "Complexes" category when fleet is not at planet
- [ ] Write test: screen initializes with Planet context (existing behavior preserved)
- [ ] Write test: screen initializes with Fleet context

#### Task 4.5: Update BuildQueueDragHandler [Simple]
**File:** `game/ui/panels/build_queue_drag_handler.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/`
- [ ] Update method signatures that accept `planet` parameter to accept build_context
- [ ] `handle_mouse_down()`, `handle_mouse_motion()`, `handle_mouse_up()` - update planet refs
- [ ] Write test: drag handler works with fleet context

---

### Phase 5: Strategy Screen Integration [Medium]
**Objective:** Wire up fleet build queue access from the strategy screen UI.
**Status:** Not Started

#### Task 5.1: Add "Build" Button for Fleets [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** Manual testing + `pytest tests/integration/ui/ -k strategy`
- [ ] When a fleet is selected and has_space_shipyard: show "Build" button
- [ ] Add `on_fleet_build_click()` handler (similar to `on_build_yard_click()` for planets, ~line 344)
- [ ] Create BuildQueueScreen with fleet as build_context
- [ ] Add close callback to refresh fleet display
- [ ] Write test: build button visible when fleet has shipyard
- [ ] Write test: build button hidden when fleet lacks shipyard

#### Task 5.2: Issue BUILD Order from UI [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/integration/ui/ -k strategy`
- [ ] When build queue screen closes with items in queue: auto-issue BUILD order to fleet
- [ ] If fleet already has BUILD order, don't duplicate
- [ ] Show BUILD order in fleet orders display
- [ ] Write test: closing build queue with items issues BUILD order
- [ ] Write test: closing empty build queue does not issue BUILD order

#### Task 5.3: Update Fleet Orders Display [Simple]
**File:** `game/ui/screens/fleet_orders_window.py`
**Tests:** `pytest tests/integration/ui/ -k fleet_orders`
- [ ] Add BUILD order description: "Building (X items in queue)"
- [ ] Write test: BUILD order renders correctly in orders window

#### Task 5.4: Block Move Commands While Building [Simple]
**File:** `game/ui/screens/strategy_fleet_ops.py`
**Tests:** `pytest tests/integration/ui/ -k fleet_ops`
- [ ] In `handle_move_designation()`: check if fleet `is_building`, show warning if so
- [ ] Write test: move command rejected for building fleet with appropriate message

---

### Phase 6: Save/Load & Edge Cases [Medium]
**Objective:** Ensure fleet build queues persist across save/load and handle edge cases.
**Status:** Not Started

#### Task 6.1: Save/Load Integration Testing [Simple]
**Tests:** `pytest tests/integration/strategy/ -k save`
- [ ] Write test: save game with fleet that has construction_queue items
- [ ] Write test: load game restores fleet construction_queue
- [ ] Write test: save game with fleet BUILD order, load, fleet still has BUILD order
- [ ] Write test: round-trip save/load preserves full fleet state

#### Task 6.2: Edge Case: Yard Ship Destroyed Mid-Build [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`
- [ ] In `process_fleet_production()`: if fleet no longer has_space_shipyard, pause production
- [ ] Log appropriate warning
- [ ] Write test: production pauses when yard ship destroyed
- [ ] Write test: production resumes when new yard ship joins fleet

#### Task 6.3: Edge Case: Fleet Enters Combat While Building [Simple]
**File:** `game/strategy/engine/conflict_resolution_engine.py` (review only)
**Tests:** `pytest tests/unit/strategy/ -k conflict`
- [ ] Verify: building fleet CAN still be attacked (no special protection)
- [ ] After battle: if fleet survives but yard destroyed, production pauses
- [ ] Write test: building fleet participates in combat when enemy arrives

#### Task 6.4: Edge Case: Complex in Queue, Fleet Moves Away [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`
- [ ] In `process_fleet_production()`: for complex items, validate fleet at planet hex
- [ ] If not at planet: skip/pause the complex item (don't decrement turns)
- [ ] Non-complex items in queue continue normally
- [ ] Write test: complex pauses when fleet not at planet
- [ ] Write test: ship items continue even when not at planet

#### Task 6.5: Full Integration Test [Medium]
**Tests:** `pytest tests/integration/strategy/`
- [ ] Write end-to-end test: create fleet with yard → issue BUILD → advance turns → ship spawns in fleet
- [ ] Write end-to-end test: fleet at planet → build complex → complex appears on planet
- [ ] Write end-to-end test: fleet with BUILD order → try to move → blocked
- [ ] Run full test suite: `pytest tests/ -n 12`

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - baseline established (6244 passed, 2 pre-existing failures)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] No regressions in existing planet build queue tests
- [ ] No regressions in fleet movement tests

### Final Verification
- [ ] End-to-end: fleet with yard can build ships
- [ ] End-to-end: fleet at planet can build complexes
- [ ] End-to-end: fleet not at planet cannot build complexes
- [ ] End-to-end: building fleet cannot move
- [ ] End-to-end: save/load preserves fleet build state
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All Phase 6 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
