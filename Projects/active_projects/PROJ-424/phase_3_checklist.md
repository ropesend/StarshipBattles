# Phase 3: Migrate snapshot consumer (`action_time_resolver.py`)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-424 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):**
- `game/strategy/services/action_time_resolver.py`
- `tests/unit/strategy/services/test_action_time_resolver.py`
- `tests/unit/strategy/engine/test_command_specs_contract.py`

**Objective:** remove the most dangerous stale-snapshot in the codebase. Replace the import-time `ORDER_TO_ABILITY_MAP` snapshot with a call-time read of `order_metadata.order_to_ability_map`. Migrate this module's `MOVEMENT_ORDER_TYPES` / `PLANET_ACTION_ORDER_TYPES` imports onto `order_metadata` while we're here.

---

## Tasks

### Task 3.1: Write failing replace-overlay test [Medium]
**File:** `tests/unit/strategy/services/test_action_time_resolver.py`
**Tests:** `pytest tests/unit/strategy/services/test_action_time_resolver.py -k replace -x`

- [ ] Add `test_resolve_action_time_reflects_registry_replace` — register a `replace=True` overlay that maps an OrderType to a different ability; assert `resolve_action_time(order)` uses the new ability's value (not the import-time-snapshotted value). RED.
- [ ] Run the test; confirm it fails BECAUSE the resolver still reads the frozen `ORDER_TO_ABILITY_MAP`

**Notes:** [Filled during implementation]

### Task 3.2: Update the contract test [Simple]
**File:** `tests/unit/strategy/engine/test_command_specs_contract.py`
**Tests:** `pytest tests/unit/strategy/engine/test_command_specs_contract.py -k order_to_ability -x`

- [ ] Switch the order-to-ability contract assertion to read `order_metadata.order_to_ability_map` instead of importing `ORDER_TO_ABILITY_MAP` from `action_time_resolver`
- [ ] Run the test; expect RED until Task 3.3 removes the old constant

**Notes:** [Filled during implementation]

### Task 3.3: Delete the import-time snapshot [Medium]
**File:** `game/strategy/services/action_time_resolver.py`
**Tests:** `pytest tests/unit/strategy/services/test_action_time_resolver.py -x`

- [ ] Delete `_build_order_to_ability_map()` entirely
- [ ] Delete the module-level `ORDER_TO_ABILITY_MAP: Dict[OrderType, str] = _build_order_to_ability_map()`
- [ ] Replace `MOVEMENT_ORDER_TYPES` import with `from game.strategy.engine.commands.order_metadata_view import order_metadata`
- [ ] Replace `PLANET_ACTION_ORDER_TYPES` import with the same `order_metadata`
- [ ] Rewrite the read sites: `order_metadata.movement_order_types`, `order_metadata.planet_action_order_types`, `order_metadata.order_to_ability_map.get(order.type)`
- [ ] Confirm no other reader inside this module still references the deleted constant
- [ ] Verify: `test_resolve_action_time_reflects_registry_replace` now passes
- [ ] Verify: order-to-ability contract test now passes
- [ ] Verify: the rest of `test_action_time_resolver.py` still passes

**Notes:** [Filled during implementation]

### Task 3.4: Run focused validation [Simple]
**File:** n/a
**Tests:**
- `pytest tests/unit/strategy/services/test_action_time_resolver.py -x`
- `pytest tests/unit/strategy/engine/test_command_specs_contract.py -k order_to_ability -x`

- [ ] Both targeted suites pass
- [ ] Verify: `grep ORDER_TO_ABILITY_MAP game/strategy/` returns no matches in production code

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No import-time order-to-ability snapshot remains in production code
- [ ] `action_time_resolver.py` reads through `order_metadata` at call time
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
