# Phase 1: Type Hints on Engine/Service Signatures [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-191 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add explicit type annotations to all strategy engine and service method signatures. Zero runtime impact — uses TYPE_CHECKING imports only.

---

## Tasks

### Task 1.1: Add TYPE_CHECKING imports and type hints to engine files [Simple]
**Files:** `game/strategy/engine/empire_economy_calculator.py`, `harvesting_engine.py`, `population_engine.py`, `maintenance_engine.py`, `fleet_order_processor.py`, `superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/ -n 12`

- [x] `empire_economy_calculator.py`: Add `TYPE_CHECKING` block with `Empire` import; annotate `calculate(self, empire: 'Empire')`, `_aggregate_colony_production(self, empire: 'Empire')`, `_aggregate_maintenance(self, empire: 'Empire')`
- [x] `harvesting_engine.py`: Already has TYPE_CHECKING block with Empire, Planet, PlanetaryFacility imports
- [x] `population_engine.py`: Already has TYPE_CHECKING block; existing type hints are complete
- [x] `maintenance_engine.py`: Add TYPE_CHECKING block; annotate `_process_empire()`, `_process_colony_facilities()`, `_process_fleet_ships()`, `_cleanup_empty_fleets()` params
- [x] `fleet_order_processor.py`: Add TYPE_CHECKING block; annotate `process_join_fleet()`, `process_colonize()`, `process_transfer()`, `_execute_load()`, `_execute_unload()`, `_transfer_founding_population()`, `process_end_turn_orders()`, `process_instant_orders()` params
- [x] `superweapon_order_processor.py`: Add TYPE_CHECKING block; annotate all `process_*` method empire params
- [x] Run `pytest tests/unit/strategy/engine/ -n 12` — 372 passed
- [x] Verify no circular import issues by importing the modules

**Notes:** All engine files now have proper TYPE_CHECKING imports and type annotations

### Task 1.2: Add type hints to service and validator files [Simple]
**Files:** `game/strategy/services/component_inspector.py`, `game/strategy/validation/colonize_validator.py`, `game/strategy/services/action_time_resolver.py`, `game/strategy/services/fleet_navigation_service.py`, `game/strategy/services/cargo_transfer_service.py`
**Tests:** `pytest tests/unit/strategy/services/ tests/unit/strategy/validation/ -n 12`

- [x] `component_inspector.py`: Add TYPE_CHECKING block; annotate ship params as `'ShipInstance'`
- [x] `colonize_validator.py`: Add TYPE_CHECKING block; annotate galaxy/fleet/planet params with concrete types
- [x] `action_time_resolver.py`: Already has TYPE_CHECKING block with Fleet, FleetOrder imports
- [x] `fleet_navigation_service.py`: Already has complete type hints via direct imports
- [x] `cargo_transfer_service.py`: Add TYPE_CHECKING block; add `Union['FleetInfo', 'PlanetInfo']` to `get_inventory_items()`
- [x] Run `pytest tests/unit/strategy/services/ tests/unit/strategy/validation/ -n 12` — 124 passed

**Notes:** All service and validation files now have proper TYPE_CHECKING imports and type annotations

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/ -n 12` — 2198 passed
- [x] No circular imports introduced
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
