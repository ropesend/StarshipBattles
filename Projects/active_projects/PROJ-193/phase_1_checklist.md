# Phase 1: Foundation — Protocol Extensions + New Protocols + Mock Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-193 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extend IPlanet/IFleet Protocols with UI-needed properties. Create IEmpire, ICombatShip, IShipInstance, IFacility Protocols. Fix all broken mock test objects. Zero UI file changes.

---

## Tasks

### Task 1.1: Extend IPlanet Protocol [Medium]
**File:** `game/core/protocols.py` (lines 169-192)
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [ ] Add properties to `IPlanet` Protocol:
  - `populations` → `List[Any]`
  - `max_population` → `int`
  - `facilities` → `List[Any]`
  - `atmosphere` → `Any`
  - `surface_gravity` → `float`
  - `surface_temperature` → `float`
  - `orbit_distance` → `float`
  - `id` → `Any`
  - `diameter_hexes` → `int`
  - `image_id` → `str`
- [ ] Verify real `Planet` class from `game/strategy/data/planet.py` has all these attributes
- [ ] Run: `pytest tests/unit/core/test_protocols.py` — verify no breakage in protocol tests

**Notes:**

### Task 1.2: Extend IFleet Protocol [Medium]
**File:** `game/core/protocols.py` (lines 221-243)
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [ ] Add properties to `IFleet` Protocol:
  - `speed` → `float`
  - `path` → `List[Any]`
  - `construction_queue` → `Any`
  - `name` → `str`
  - `is_building` → `bool` (property)
  - `has_space_shipyard` → `bool` (property)
- [ ] Verify real `Fleet` class from `game/strategy/data/fleet.py` has all these attributes
- [ ] Run: `pytest tests/unit/core/test_protocols.py`

**Notes:**

### Task 1.3: Create IEmpire Protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [ ] Add new `@runtime_checkable` `IEmpire(Protocol)` class with properties:
  - `id` → `int`
  - `name` → `str`
  - `color` → `Any`
  - `flag_id` → `str`
  - `portrait_id` → `str`
  - `empire_theme_id` → `str`
  - `race_config` → `Optional[Any]`
  - `colonies` → `List[Any]`
  - `fleets` → `List[Any]`
  - `resource_pool` → `Dict[str, float]`
  - `max_storage` → `Dict[str, float]`
  - `built_ship_designs` → `Any` (set)
- [ ] Add `is_empire()` TypeGuard function
- [ ] Verify real `Empire` class satisfies `IEmpire` (check `game/strategy/data/empire.py`)

**Notes:**

### Task 1.4: Create IFacility Protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [ ] Add new `@runtime_checkable` `IFacility(Protocol)` class with properties:
  - `instance_id` → `str`
  - `design_id` → `str`
  - `name` → `str`
  - `design_data` → `Dict[str, Any]`
  - `is_operational` → `bool`
  - `construction_queue` → `Any`
  - `resource_levels` → `Dict[str, float]`
- [ ] Add `is_facility()` TypeGuard function
- [ ] Verify real `PlanetaryFacility` class satisfies `IFacility` (check `game/strategy/data/planet.py:32`)

**Notes:**

### Task 1.5: Create IShipInstance Protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [ ] Add new `@runtime_checkable` `IShipInstance(Protocol)` class with properties:
  - `design_id` → `str`
  - `design_name` → `str`
  - `design_data` → `Dict[str, Any]`
  - `hull_class` → `str`
  - `cargo_contents` → `Dict[str, Any]`
  - `ship_name` → `str`
  - `serial_number` → `int`
- [ ] Add `is_ship_instance()` TypeGuard function
- [ ] Verify real `ShipInstance` class satisfies `IShipInstance` (check `game/strategy/data/ship_instance.py`)

**Notes:**

### Task 1.6: Create ICombatShip Protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [ ] Add new `@runtime_checkable` `ICombatShip(Protocol)` class with properties:
  - `name` → `str`
  - `team_id` → `int`
  - `is_alive` → `bool`
  - `is_derelict` → `bool`
  - `hp` → `int`
  - `max_hp` → `int`
  - `position` → `Any`
  - `layers` → `Dict[Any, Any]`
  - `resources` → `Optional[Any]`
  - `current_target` → `Optional[Any]`
  - `secondary_targets` → `List[Any]`
  - `max_targets` → `int`
  - `total_defense_score` → `float`
  - Method: `get_total_sensor_score()` → `float`
- [ ] Add `is_combat_ship()` TypeGuard function
- [ ] Verify real `Ship` class from `game/simulation/entities/ship.py` satisfies `ICombatShip`
- [ ] NOTE: Do NOT add `crew_onboard`, `crew_required`, `shots_fired`, `shots_hit` — these are dynamically injected

**Notes:**

### Task 1.7: Fix broken mock objects in test files [Medium]
**Files:** 31+ test files
**Tests:** `pytest tests/ -n 12`

- [ ] Grep for all test files using `is_planet()`, `is_fleet()`, `isinstance(..., IPlanet)`, `isinstance(..., IFleet)` to find affected mock objects
- [ ] For each mock Planet: add missing properties (`populations`, `max_population`, `facilities`, `atmosphere`, `surface_gravity`, `surface_temperature`, `orbit_distance`, `id`, `diameter_hexes`, `image_id`)
- [ ] For each mock Fleet: add missing properties (`speed`, `path`, `construction_queue`, `name`, `is_building`, `has_space_shipyard`)
- [ ] Where feasible, convert MagicMock to real objects (following PROJ-159 pattern in `tests/integration/strategy/transfer/conftest.py`)
- [ ] Run: `pytest tests/ -n 12` — verify all tests pass

**Notes:** This is the largest task in Phase 1. Systematic approach: grep → list affected files → fix each.

### Task 1.8: Protocol satisfaction tests [Simple]
**File:** `tests/unit/core/test_protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [ ] Add test: real `Empire` object satisfies `IEmpire` (isinstance check)
- [ ] Add test: real `Planet` object satisfies extended `IPlanet`
- [ ] Add test: real `Fleet` object satisfies extended `IFleet`
- [ ] Add test: real `PlanetaryFacility` object satisfies `IFacility`
- [ ] Add test: real `ShipInstance` object satisfies `IShipInstance`
- [ ] Add test: real `Ship` (simulation) object satisfies `ICombatShip`
- [ ] Verify all existing protocol tests still pass (41 tests)
- [ ] Run: `pytest tests/unit/core/test_protocols.py`

**Notes:**

### Task 1.9: Full Test Suite Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run: `pytest tests/ -n 12`
- [ ] Confirm 12,718+ passing, 0 failures
- [ ] If failures: diagnose and fix mock objects or Protocol definitions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
