# Phase 1: Planet Command Handlers + Order Validator

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-264 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Raise coverage on `planet_command_handlers.py` (17.9% -> 90%+) and `planet_order_validator.py` (15.0% -> 90%+) by writing comprehensive unit tests for all handler classes and validator methods.

---

## Prerequisites

- [ ] Read `game/strategy/engine/planet_command_handlers.py` -- 4 handler classes
- [ ] Read `game/strategy/validation/planet_order_validator.py` -- 3 static methods
- [ ] Read `game/strategy/engine/command_handlers.py` for `BaseCommandHandler._resolve_planet`
- [ ] Read `game/strategy/engine/commands.py` for planet command dataclass fields
- [ ] Read `game/strategy/data/component_activation_state.py` for `ActivationPhase` enum
- [ ] Read `game/strategy/data/planetary_facility.py` for facility fields and `get_activation_state()`
- [ ] Read existing mock patterns in `tests/unit/strategy/engine/test_fleet_order_transfer.py`

---

## Task 1.1: Create test_planet_command_handlers.py [Complex]
**File:** `tests/unit/strategy/engine/test_planet_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_command_handlers.py -v`

### Setup
- [ ] Create test file with imports for all 4 handler classes and command dataclasses
- [ ] Write `_make_mock_session(planet=None)` helper -- returns mock GameSession with `_get_planet_by_id`, `player_empire`, `registries`
- [ ] Write `_make_mock_planet(owner_id, orders=None, facilities=None)` helper
- [ ] Write `_make_mock_facility(instance_id, is_operational=True)` helper

### TestIssuePlanetOrderCommandHandler
- [ ] `test_planet_not_found_returns_error` -- `_get_planet_by_id` returns None
- [ ] `test_planet_wrong_owner_returns_error` -- planet.owner_id != empire.id
- [ ] `test_unknown_order_type_returns_error` -- cmd.order_type = "INVALID_TYPE"
- [ ] `test_activate_without_ability_name_returns_error` -- cmd.ability_name = None
- [ ] `test_deactivate_without_ability_name_returns_error` -- cmd.ability_name = None
- [ ] `test_activate_validator_rejects_returns_error` -- mock validator to return error
- [ ] `test_activate_success_queues_order` -- planet.add_order called with Order(ACTIVATE_ABILITY)
- [ ] `test_activate_target_includes_component_key` -- target dict has component_key field
- [ ] `test_activate_target_includes_component_id` -- target dict has component_id field
- [ ] `test_deactivate_success_queues_order` -- planet.add_order called
- [ ] `test_unsupported_order_type_returns_error` -- e.g., "MOVE" is valid OrderType but unsupported
- [ ] Run: `pytest tests/unit/strategy/engine/test_planet_command_handlers.py::TestIssuePlanetOrderCommandHandler -v`

### TestClearPlanetOrdersCommandHandler
- [ ] `test_planet_not_found_returns_error`
- [ ] `test_wrong_owner_returns_error`
- [ ] `test_success_clears_orders` -- planet.clear_orders() called
- [ ] Run: `pytest tests/unit/strategy/engine/test_planet_command_handlers.py::TestClearPlanetOrdersCommandHandler -v`

### TestDeletePlanetOrderCommandHandler
- [ ] `test_planet_not_found_returns_error`
- [ ] `test_wrong_owner_returns_error`
- [ ] `test_negative_index_returns_error`
- [ ] `test_index_beyond_length_returns_error` -- index >= len(planet.orders)
- [ ] `test_success_removes_order_at_index` -- planet.orders.pop(index) removes correct order
- [ ] Run: `pytest tests/unit/strategy/engine/test_planet_command_handlers.py::TestDeletePlanetOrderCommandHandler -v`

### TestSetAtmosphereTargetCommandHandler
- [ ] `test_planet_not_found_returns_error`
- [ ] `test_wrong_owner_returns_error`
- [ ] `test_success_sets_atmosphere_target` -- planet.atmosphere_target set to target dict
- [ ] `test_empty_dict_clears_target` -- empty dict accepted, attribute set
- [ ] Run: `pytest tests/unit/strategy/engine/test_planet_command_handlers.py::TestSetAtmosphereTargetCommandHandler -v`

**Notes:** The handler imports `BaseCommandHandler._resolve_planet` lazily inside `execute()`. The mock session must have `_get_planet_by_id` wired so the static method works. Alternatively, patch `BaseCommandHandler._resolve_planet` directly.

---

## Task 1.2: Create test_planet_order_validator.py [Complex]
**File:** `tests/unit/strategy/validation/test_planet_order_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_planet_order_validator.py -v`

### Setup
- [ ] Create test file with imports for `PlanetOrderValidator` and `_facility_has_ability`
- [ ] Write `_make_mock_planet(facilities, orders=None, active_abilities=None)` helper
- [ ] Write `_make_mock_facility(instance_id, is_operational=True, design_data=None)` helper
- [ ] Import `ActivationPhase`, `ComponentActivationState`, `OrderType`, `Order`

### TestValidateActivateAbility
- [ ] `test_facility_not_found_returns_error` -- no matching facility instance_id
- [ ] `test_facility_not_operational_returns_error`
- [ ] `test_facility_lacks_ability_returns_error` -- patch/mock `_facility_has_ability` to False
- [ ] `test_component_key_already_active_returns_error` -- facility.get_activation_state returns ACTIVE
- [ ] `test_component_key_already_activating_returns_error` -- state is ACTIVATING
- [ ] `test_component_key_conflicting_queued_order_returns_error` -- existing ACTIVATE_ABILITY order with same component_key
- [ ] `test_component_key_success` -- INACTIVE state, no conflicts
- [ ] `test_legacy_ability_already_active_returns_error` -- active_abilities has ability=True
- [ ] `test_legacy_activation_already_queued_returns_error` -- existing order with same ability_name
- [ ] `test_legacy_success` -- ability not active, no pending orders
- [ ] Run: `pytest tests/unit/strategy/validation/test_planet_order_validator.py::TestValidateActivateAbility -v`

### TestValidateDeactivateAbility
- [ ] `test_facility_not_found_returns_error`
- [ ] `test_facility_not_operational_returns_error`
- [ ] `test_facility_lacks_ability_returns_error`
- [ ] `test_component_key_not_active_returns_error` -- INACTIVE state
- [ ] `test_component_key_success_when_active` -- ACTIVE state
- [ ] `test_component_key_success_when_activating` -- ACTIVATING state
- [ ] `test_legacy_not_active_no_pending_returns_error` -- not in active_abilities, no pending order
- [ ] `test_legacy_success_when_active` -- active_abilities has ability=True
- [ ] `test_legacy_success_when_activation_pending` -- not active but pending ACTIVATE order
- [ ] Run: `pytest tests/unit/strategy/validation/test_planet_order_validator.py::TestValidateDeactivateAbility -v`

### TestFacilityHasAbility
- [ ] `test_dict_component_with_ability_in_abilities_dict` -- component is dict with abilities key
- [ ] `test_dict_component_ability_via_registry` -- ability not in dict, but component_registry has it
- [ ] `test_string_component_ability_via_registry` -- component is string reference
- [ ] `test_string_component_no_registry_returns_false` -- string comp, no registry
- [ ] `test_no_matching_components_returns_false` -- empty design, no components
- [ ] Run: `pytest tests/unit/strategy/validation/test_planet_order_validator.py::TestFacilityHasAbility -v`

**Notes:** `_facility_has_ability` uses `iter_components(facility.design_data)` which iterates layers. Mock `design_data` with a simple `{"layers": {"core": [...]}}` structure. For registry tests, pass a dict-like mock for `component_registry`.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests passing: `pytest tests/unit/strategy/engine/test_planet_command_handlers.py tests/unit/strategy/validation/test_planet_order_validator.py -v`
- [ ] No regressions: `pytest tests/unit/strategy/ -x --timeout=60`
- [ ] Coverage spot-check: `pytest tests/unit/strategy/engine/test_planet_command_handlers.py tests/unit/strategy/validation/test_planet_order_validator.py --cov=game.strategy.engine.planet_command_handlers --cov=game.strategy.validation.planet_order_validator --cov-report=term-missing`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
