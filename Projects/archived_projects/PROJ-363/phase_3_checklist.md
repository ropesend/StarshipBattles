# Phase 3: Generate registry / category sets / ORDER_TO_ABILITY_MAP from specs

**Status:** Complete

**Deviation from original plan:** Category frozensets (`MOVEMENT_ORDER_TYPES`, `ACTION_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES`) are NOT runtime-derived from the spec table. Reason: making them runtime-derived created an unbreakable import cycle — `specs.py` imports `OrderType` from `order_types.py`, and `order_types.py` is imported (eagerly, at top of module) by `cargo_transfer_service.py` and `fleet.py` before `specs.py` is on the import path. A `__getattr__` lazy-resolver on `order_types.py` recursed through specs → handlers → services → cargo_transfer_service → order_types.MOVEMENT_ORDER_TYPES → recursion. The frozensets stay as plain constants in `order_types.py`, but their equality with `specs.{movement,action,planet_action}_order_types()` is **pinned by the contract test** in `test_command_specs_contract.py`. The spec table remains the **declarative** source of truth; updating a CommandSpec without updating the constant (or vice versa) is caught by the test before merge.
**Objective:** Make `CommandHandlerRegistry`, `MOVEMENT_ORDER_TYPES`/`ACTION_ORDER_TYPES`/`PLANET_ACTION_ORDER_TYPES`, and `ORDER_TO_ABILITY_MAP` derived from `COMMAND_SPECS` instead of hand-maintained.

---

## Tasks

### Task 3.1: Generate CommandHandlerRegistry from specs [Medium]
**File:** `game/strategy/engine/handlers/registry_factory.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py tests/unit/strategy/engine/test_command_registry_contract.py -v`

- [ ] Replace the body of `create_default_registry()` with:
  ```python
  from game.strategy.engine.commands.specs import COMMAND_SPECS
  registry = CommandHandlerRegistry()
  for spec in COMMAND_SPECS:
      registry.register(spec.command_class.__name__, spec.handler_class())
  return registry
  ```
- [ ] Delete the 31 hand-written `register()` calls and their hand-written imports.
- [ ] Run all command handler tests — green.
- [ ] Run integration tests under `tests/integration/strategy/facade/` — green.

**Notes:** _(filled during implementation)_

### Task 3.2: Generate category frozensets from specs [Simple]
**File:** `game/strategy/data/order_types.py`
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_contract.py::test_movement_order_types_matches_specs -v`

- [ ] Replace hand-maintained `MOVEMENT_ORDER_TYPES`, `ACTION_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES` frozensets with module-level expressions derived from `COMMAND_SPECS` at import time:
  ```python
  # End of order_types.py, AFTER the OrderType enum.
  # Note: import is at end-of-file to avoid circular import (specs.py imports OrderType).
  def _build_category_sets() -> dict[str, frozenset[OrderType]]:
      from game.strategy.engine.commands.specs import COMMAND_SPECS
      return {
          'movement': frozenset(s.order_type for s in COMMAND_SPECS if s.category == 'movement' and s.order_type is not None),
          'action': frozenset(s.order_type for s in COMMAND_SPECS if s.category == 'action' and s.order_type is not None),
          'planet_action': frozenset(s.order_type for s in COMMAND_SPECS if s.category == 'planet' and s.order_type is not None and s.execution_model == 'planet'),
      }
  _categories = _build_category_sets()
  MOVEMENT_ORDER_TYPES = _categories['movement']
  ACTION_ORDER_TYPES = _categories['action']
  PLANET_ACTION_ORDER_TYPES = _categories['planet_action']
  ```
- [ ] Run category-set contract test: green.
- [ ] Run all tests that import these frozensets (find via grep) — green.

**Notes:** _(filled during implementation)_

### Task 3.3: Generate ORDER_TO_ABILITY_MAP from specs [Simple]
**File:** `game/strategy/services/action_time_resolver.py`
**Tests:** `pytest tests/unit/strategy/services/test_action_time_resolver.py tests/unit/strategy/engine/test_command_registry_contract.py -v`

- [ ] Replace hand-maintained `ORDER_TO_ABILITY_MAP` with:
  ```python
  def _build_order_to_ability_map() -> dict[OrderType, str]:
      from game.strategy.engine.commands.specs import COMMAND_SPECS
      return {
          s.order_type: s.action_ability_name
          for s in COMMAND_SPECS
          if s.order_type is not None and s.action_ability_name is not None
          and s.execution_model == 'action'
      }
  ORDER_TO_ABILITY_MAP = _build_order_to_ability_map()
  ```
- [ ] Verify the resulting map contents match the existing hand-coded map (use a temporary debug print or test fixture).
- [ ] Action-time contract test: green.

**Notes:** _(filled during implementation)_

### Task 3.4: Run full focused suite [Simple]
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ --testmon`

- [ ] All green.
- [ ] No remaining hand-maintained metadata for command/order routing outside specs.py.

**Notes:** _(filled during implementation)_

---

## Phase Completion Checklist
- [x] Registry: spec-derived (loops `COMMAND_SPECS` in `create_default_registry`)
- [x] ORDER_TO_ABILITY_MAP: spec-derived (`_build_order_to_ability_map()` in `action_time_resolver.py`)
- [x] Category frozensets: kept as plain constants (see deviation note above); pinned to spec derivations by contract test
- [x] Spec/handler/category/action-time contract tests green
- [x] Update plan.md phase table to `Complete`; Current State → Phase 4

## Phase Outcome
- `registry_factory.py` shrank from ~125 LOC to ~35 LOC.
- `action_time_resolver.py` ORDER_TO_ABILITY_MAP entry shrank from a 9-line literal to a 3-line derivation.
- All existing strategy + integration tests green (4262 passed).
