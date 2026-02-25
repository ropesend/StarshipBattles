# Phase 1: Type Hints on Engine/Service Signatures [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-191 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add explicit type annotations to all strategy engine and service method signatures. Zero runtime impact — uses TYPE_CHECKING imports only.

---

## Tasks

### Task 1.1: Add TYPE_CHECKING imports and type hints to engine files [Simple]
**Files:** `game/strategy/engine/empire_economy_calculator.py`, `harvesting_engine.py`, `population_engine.py`, `maintenance_engine.py`, `fleet_order_processor.py`, `superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/ -n 12`

- [ ] `empire_economy_calculator.py`: Add `TYPE_CHECKING` block with `Empire, Planet, PlanetaryFacility, Fleet, ShipInstance` imports; annotate `calculate(self, empire: 'Empire')`, `_aggregate_colony_production(self, empire: 'Empire')`, `_aggregate_maintenance(self, empire: 'Empire')`
- [ ] `harvesting_engine.py`: Add TYPE_CHECKING block; annotate empire/colony/facility params on private methods
- [ ] `population_engine.py`: Verify existing type hints cover all methods; add if missing
- [ ] `maintenance_engine.py`: Add TYPE_CHECKING block; annotate `_process_empire()`, `_process_colony_facilities()`, `_process_fleet_ships()` params
- [ ] `fleet_order_processor.py`: Add TYPE_CHECKING block if missing; annotate `process_join_fleet()`, `process_colonize()`, `process_transfer()`, `_transfer_founding_population()` params
- [ ] `superweapon_order_processor.py`: Add TYPE_CHECKING block; annotate all `process_*` method empire/fleet/planet params
- [ ] Run `pytest tests/unit/strategy/engine/ -n 12` — all pass
- [ ] Verify no circular import issues by importing the modules

**Notes:**

### Task 1.2: Add type hints to service and validator files [Simple]
**Files:** `game/strategy/services/component_inspector.py`, `game/strategy/validation/colonize_validator.py`, `game/strategy/services/action_time_resolver.py`, `game/strategy/services/fleet_navigation_service.py`, `game/strategy/services/cargo_transfer_service.py`
**Tests:** `pytest tests/unit/strategy/services/ tests/unit/strategy/validation/ -n 12`

- [ ] `component_inspector.py`: Annotate ship params as `'ShipInstance'`
- [ ] `colonize_validator.py`: Annotate galaxy/fleet/planet params with concrete types
- [ ] `action_time_resolver.py`: Annotate ship param as `'ShipInstance'`
- [ ] `fleet_navigation_service.py`: Verify existing type hints; add where missing
- [ ] `cargo_transfer_service.py`: Add `Union['FleetInfo', 'PlanetInfo']` to `get_inventory_items()`; add TYPE_CHECKING imports
- [ ] Run `pytest tests/unit/strategy/services/ tests/unit/strategy/validation/ -n 12` — all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/ -n 12` — all pass
- [ ] No circular imports introduced
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
