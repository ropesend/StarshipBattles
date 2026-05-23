# Phase 5: Typed planet strategic intents

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 4 (Planet/Fleet/Empire contract pinned)
**Objective:** Replace the stringly `IssuePlanetOrderCommand(order_type: str, target: dict)` path with a typed strategic-intent contract for planet ability activation/deactivation. Remove the ad hoc command-string mapping; planet strategic intents become first-class commands rather than a multiplexed escape hatch.

---

## Tasks

### Task 5.1: Failing TDD test for typed planet intents
**Files:** `tests/unit/strategy/engine/test_typed_planet_intents.py` (new)

- [x] Pin that `ActivatePlanetAbilityCommand` and `DeactivatePlanetAbilityCommand` exist with the required fields (`planet_id`, `facility_instance_id`, `ability_name`, `component_key`) and NO stringly `order_type` field.
- [x] Pin that `IssuePlanetOrderCommand` and `IssuePlanetOrderCommandHandler` are deleted from their modules (Rule 4: no compat shims).
- [x] Pin handler behavior: `ActivatePlanetAbilityCommandHandler.execute` queues an `OrderType.ACTIVATE_ABILITY` order; the deactivate handler queues `OrderType.DEACTIVATE_ABILITY`.
- [x] Pin façade surface: `facade.commands.activate_planet_ability` and `commands.deactivate_planet_ability` verbs exist; `commands.issue_planet_order` is absent.

### Task 5.2: Add typed command DTOs
**Files:** `game/strategy/engine/commands/__init__.py`

- [x] Add `ActivatePlanetAbilityCommand(planet_id, facility_instance_id, ability_name, component_key)`.
- [x] Add `DeactivatePlanetAbilityCommand(planet_id, facility_instance_id, ability_name, component_key)`.

### Task 5.3: Add typed handlers
**Files:** `game/strategy/engine/planet_command_handlers.py`

- [x] Add `ActivatePlanetAbilityCommandHandler` with `@command_spec(order_type=ACTIVATE_ABILITY, category='planet', execution_model='planet', facade_helper_name='dispatch_activate_planet_ability')`.
- [x] Add `DeactivatePlanetAbilityCommandHandler` with the matching spec.
- [x] Both handlers route through a shared `_queue_ability_order` helper that builds the marker-dict target payload (preserving the post-load rebinding shape).
- [x] Register both handlers in `register()`.

### Task 5.4: Migrate UI callers
**Files:** `game/ui/screens/planet_abilities_controller.py`, `game/ui/screens/strategy_fleet_command_router.py`

- [x] `PlanetAbilitiesController.toggle_ability`: pick `DeactivatePlanetAbilityCommand` or `ActivatePlanetAbilityCommand` based on `is_active`; drop the stringly `order_type` parameter.
- [x] `StrategyFleetCommandRouter._handle_ability_toggle`: same migration.

### Task 5.5: Migrate tests
**Files:** `tests/unit/strategy/engine/test_planet_command_handlers.py`, `tests/unit/strategy/facade/test_facade_dispatch.py`, `tests/unit/strategy/engine/test_command_registry_contract.py`, `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`, `tests/unit/ui/screens/test_strategy_fleet_command_router.py`

- [x] Replace `TestIssuePlanetOrderCommandHandler` (12 tests) with `TestActivatePlanetAbilityCommandHandler` + `TestDeactivatePlanetAbilityCommandHandler` (8 tests; the 4 "missing kwarg → ValidationResult.error" tests don't apply to typed commands — typed commands require those kwargs at construction).
- [x] `test_facade_dispatch.py`: replace the single `dispatch_issue_planet_order` parametrize row with two rows for the typed dispatchers.
- [x] `test_command_registry_contract.py`: add the two new facade helper names to `EXISTING_FACADE_DISPATCH_HELPERS`; update the comments on `OrderType.ACTIVATE_ABILITY`/`DEACTIVATE_ABILITY`.
- [x] `test_strategy_session_facade_public_api.py`: replace `dispatch_issue_planet_order` in `LEGACY_FLAT_METHODS` with the two typed names (these are pinned as NOT exposed as flat top-level facade methods — verbs live under `facade.commands`).
- [x] `test_strategy_fleet_command_router.py`: replace stringly parametrize on `order_type` with parametrize on `cmd_class_name`; remove the `IssuePlanetOrderCommand` monkeypatch.

### Task 5.6: Final cutover — delete the stringly path
**Files:** `game/strategy/engine/commands/__init__.py`, `game/strategy/engine/planet_command_handlers.py`, `game/strategy/engine/commands/registry.py`

- [x] Delete `IssuePlanetOrderCommand` dataclass.
- [x] Delete `IssuePlanetOrderCommandHandler` class + its registration entry.
- [x] Update the `IMPLICIT_ACTION_ORDER_TYPES` comment in `registry.py`.

### Task 5.7: Doc sync (inline; Phase 8 will do the broader doc pass)
**Files:** `docs/systems/orders_system.md`, `docs/systems/strategy_layer.md`

- [x] `orders_system.md`: update the Planet Ability Orders handler reference.
- [x] `strategy_layer.md`: update the Planet orders row in the command catalog table.

### Task 5.8: Sweep + sharded suite
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] 242 affected tests green.
- [x] Run the canonical sharded suite green.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `python Tools/test_sharded/test_sharded.py` green (no NEW failures vs. Phase 0 baseline)
- [x] Game still runnable / savable / loadable (typed commands queue the same Order types as before — wire-compatible at the save schema level)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
- [x] `python Projects/scripts/validate_phase.py PROJ-438 5` passes
