# Phase 1: Contract tests (TDD baseline)

**Status:** Not Started
**Objective:** Write the contract tests that the Phase 2-4 implementation must satisfy. These tests will FAIL until the spec table exists; they pin the new contract.

---

## Tasks

### Task 1.1: Create contract test file [Medium]
**File:** `tests/unit/strategy/engine/test_command_registry_contract.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_contract.py -v` — must FAIL before Phase 2 lands the spec table.

- [ ] Module docstring referencing PROJ-363 Phase 1 + review finding #4.
- [ ] Import the (yet-to-exist) `COMMAND_SPECS` from `game.strategy.engine.commands.specs`. The import itself fails before Phase 2 — that's expected and is the failing-test trigger.

**Notes:** _(filled during implementation)_

### Task 1.2: Spec → handler contract test [Simple]
- [ ] `test_every_spec_has_registered_handler`:
  - Build the runtime registry via `create_default_registry()`.
  - For each `spec in COMMAND_SPECS`: assert `spec.command_class.__name__ in registry._handlers` (or whatever the public lookup is).
- [ ] `test_no_orphaned_registrations`:
  - For each handler in `create_default_registry()`: assert there exists a spec with that command_class.

### Task 1.3: Spec → action-time contract test [Simple]
- [ ] `test_every_action_spec_has_action_time_entry`:
  - For each `spec in COMMAND_SPECS` where `spec.execution_model == 'action'` and `spec.action_ability_name is not None`:
    - Assert `ActionTimeResolver().resolve_action_time(<a synthetic order with that order_type>)` returns a positive integer.
- [ ] `test_action_time_never_zero_or_negative`:
  - Parametrized over every `OrderType` member: `resolve_action_time` returns ≥ 1 (or raises a documented error for unknown types).

### Task 1.4: Spec → category-set contract test [Simple]
- [ ] `test_movement_order_types_matches_specs`:
  - Assert `MOVEMENT_ORDER_TYPES == frozenset(s.order_type for s in COMMAND_SPECS if s.category == 'movement' and s.order_type is not None)`.
- [ ] Same for `ACTION_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES`. (BUILD has its own category; assert it lives in the build category subset.)

### Task 1.5: Facade helper resolution test [Medium]
- [ ] `test_every_spec_with_facade_helper_resolves`:
  - Construct a `StrategySessionFacade` (or its dispatch slice) instance.
  - For each `spec in COMMAND_SPECS` where `spec.facade_helper_name is not None`:
    - Assert `getattr(facade, spec.facade_helper_name)` returns a callable.
    - Optionally call it with mock kwargs and assert it returns a `ValidationResult`.

### Task 1.6: OrderType coverage [Simple]
- [ ] `test_every_order_type_has_at_least_one_spec`:
  - For each `OrderType` member: assert at least one `spec in COMMAND_SPECS` has that `order_type` (or it's documented as an order with no command, e.g. derived/internal).
- [ ] `test_no_unknown_order_types_in_specs`:
  - All `spec.order_type` values (excluding None) are valid `OrderType` enum members.

### Task 1.7: Confirm tests fail before Phase 2 [Simple]
- [ ] Run the file. Every test should fail (or error on import) because `COMMAND_SPECS` doesn't exist yet.
- [ ] Document the failure trace in this checklist's notes.

**Notes:** _(filled during implementation)_

---

## Phase Completion Checklist
- [ ] All tests written; all currently fail (or error on import) — proving they are the Phase 2-4 entry contract
- [ ] Update plan.md phase table to `Complete`
- [ ] Update Current State to point to Phase 2
