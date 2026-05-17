# Phase 4: Migrate remaining production consumers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-424 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/action_execution_engine.py`
- `game/strategy/engine/fleet_movement_engine.py`
- `game/strategy/engine/planet_action_engine.py`
- `game/strategy/services/fleet_navigation_service.py`
- `game/strategy/services/fleet_path_projection.py`
- `game/strategy/services/cargo_transfer_service.py`
- `tests/unit/strategy/engine/test_command_registry_thirdparty.py`
- `tests/unit/strategy/fleet_movement_engine/test_characterization.py`
- `tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py`
- `tests/unit/strategy/test_fleet_order_processor.py`

**Objective:** move all remaining production consumers off the duplicated `order_types.py` frozensets onto `order_metadata`. Production must be clean BEFORE Phase 5 deletes the constants.

---

## Tasks

### Task 4.1: Update tests to expect `order_metadata` imports [Medium]
**File:** the four test modules listed above
**Tests:** `pytest tests/unit/strategy/ -k "order or action or movement" -x`

- [ ] Update each test module so it fails unless production imports come from `order_metadata` (e.g., AST-based assertion that production module imports `order_metadata`, or behavioural test that exercises the view path)
- [ ] Run the suite; confirm the expected RED set is the six production files about to be edited

**Notes:** [Filled during implementation]

### Task 4.2: Migrate `action_execution_engine.py` [Simple]
**File:** `game/strategy/engine/action_execution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py -x`

- [ ] Replace `MOVEMENT_ORDER_TYPES` import with `from game.strategy.engine.commands.order_metadata_view import order_metadata`
- [ ] Replace `ACTION_ORDER_TYPES` and `PLANET_FMS_ACTION_ORDER_TYPES` imports the same way
- [ ] Rewrite read sites to use `order_metadata.<property>` at call time
- [ ] Verify: targeted handler-registry test passes

**Notes:** [Filled during implementation]

### Task 4.3: Migrate `fleet_movement_engine.py` [Simple]
**File:** `game/strategy/engine/fleet_movement_engine.py`
**Tests:** `pytest tests/unit/strategy/fleet_movement_engine/test_characterization.py -x`

- [ ] Replace `MOVEMENT_ORDER_TYPES` + `ACTION_ORDER_TYPES` imports with `order_metadata`
- [ ] Rewrite read sites to use `order_metadata.<property>`
- [ ] Verify: characterization test passes

**Notes:** [Filled during implementation]

### Task 4.4: Migrate `planet_action_engine.py` [Simple]
**File:** `game/strategy/engine/planet_action_engine.py`
**Tests:** `pytest tests/unit/strategy/ -k planet_action -x`

- [ ] Replace `PLANET_ACTION_ORDER_TYPES` import with `order_metadata`
- [ ] Rewrite read sites to use `order_metadata.planet_action_order_types`
- [ ] Verify: targeted suite passes

**Notes:** [Filled during implementation]

### Task 4.5: Migrate the three services [Simple]
**File:** `fleet_navigation_service.py`, `fleet_path_projection.py`, `cargo_transfer_service.py`
**Tests:** `pytest tests/unit/strategy/ -k "fleet or cargo or navigation" -x`

- [ ] `fleet_navigation_service.py`: replace `MOVEMENT_ORDER_TYPES` + `ACTION_ORDER_TYPES` imports with `order_metadata`
- [ ] `fleet_path_projection.py`: replace `MOVEMENT_ORDER_TYPES` import with `order_metadata`
- [ ] `cargo_transfer_service.py`: replace `MOVEMENT_ORDER_TYPES` import with `order_metadata`
- [ ] Verify: targeted suite passes

**Notes:** [Filled during implementation]

### Task 4.6: Run broader regression [Medium]
**File:** n/a
**Tests:**
- `pytest tests/unit/strategy/fleet_movement_engine/test_characterization.py -x`
- `pytest tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py -x`
- `pytest tests/unit/strategy/engine/test_command_registry_contract.py -x`
- `pytest tests/unit/strategy/ -k "order or action or movement" -x`

- [ ] All four suites green
- [ ] `git grep "MOVEMENT_ORDER_TYPES\|ACTION_ORDER_TYPES\|PLANET_ACTION_ORDER_TYPES\|PLANET_FMS_ACTION_ORDER_TYPES" game/strategy/` returns ONLY hits in `data/order_types.py`, `data/fleet.py`, and the registry derivation methods. No remaining production-engine or service references
- [ ] **DO NOT** touch `order_types.py` constants yet — Phase 5 owns the deletion

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No production file under `game/strategy/engine/` or `game/strategy/services/` (other than the registry derivations) still imports the duplicated metadata constants
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
