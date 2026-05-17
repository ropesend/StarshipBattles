# Phase 1: Explicit `planet_fms` metadata + registry derivation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-424 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_0
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/commands/registry.py`
- `game/strategy/engine/handlers/lay_mines.py`
- `game/strategy/engine/handlers/launch_fighters.py`
- `game/strategy/engine/handlers/launch_satellites.py`
- `game/strategy/engine/handlers/recover_fighters.py`
- `game/strategy/engine/handlers/recover_satellites.py`
- `tests/unit/strategy/engine/test_command_specs_contract.py`
- `tests/unit/strategy/engine/test_command_registry_contract.py`

**Objective:** close the fifth duplicated surface (`PLANET_FMS_ACTION_ORDER_TYPES`) before introducing the shared view in Phase 2. Tag the five FMS handler command specs with `subcategories=frozenset({"planet_fms"})` and add a registry derivation method that reads from those tags.

---

## Tasks

### Task 1.1: Write failing tests for the FMS derivation [Simple]
**File:** `tests/unit/strategy/engine/test_command_specs_contract.py`, `tests/unit/strategy/engine/test_command_registry_contract.py`
**Tests:** `pytest tests/unit/strategy/engine/test_command_specs_contract.py -k planet_fms -x`

- [ ] Add `test_planet_fms_action_order_types_derivation_matches_constant` — calls `CommandRegistry.planet_fms_action_order_types()` and asserts it equals the current `PLANET_FMS_ACTION_ORDER_TYPES` constant. RED.
- [ ] Add `test_exactly_five_specs_carry_planet_fms_subcategory` — iterates registered specs, asserts exactly five carry `"planet_fms"` in `subcategories`. RED.
- [ ] Run both tests; confirm they fail with `AttributeError` (no derivation method yet) or `0 != 5` (no tags yet)

**Notes:** [Filled during implementation]

### Task 1.2: Tag the five FMS handler command specs [Simple]
**File:** five handler files under `game/strategy/engine/handlers/`
**Tests:** `pytest tests/unit/strategy/engine/test_command_specs_contract.py -k planet_fms -x`

- [ ] `lay_mines.py`: add `subcategories=frozenset({"planet_fms"})` to the `@command_spec(...)` decorator
- [ ] `launch_fighters.py`: same
- [ ] `launch_satellites.py`: same
- [ ] `recover_fighters.py`: same
- [ ] `recover_satellites.py`: same
- [ ] Verify: `test_exactly_five_specs_carry_planet_fms_subcategory` now passes

**Notes:** [Filled during implementation]

### Task 1.3: Add `CommandRegistry.planet_fms_action_order_types()` [Medium]
**File:** `game/strategy/engine/commands/registry.py`
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_contract.py -x`

- [ ] Add `planet_fms_action_order_types(self) -> frozenset[OrderType]` to `CommandRegistry` (alongside the other derivation methods `movement_order_types()`, `action_order_types()`, `planet_action_order_types()`, `order_to_ability_map()`)
- [ ] Implementation: filter registered specs by `"planet_fms" in spec.subcategories` and return their order types as a frozenset. **NO** hardcoded order-name list; **NO** filename-based derivation
- [ ] Verify: `test_planet_fms_action_order_types_derivation_matches_constant` passes (derivation matches the current constant exactly)
- [ ] Verify: the existing `test_command_registry_contract.py` regression set stays green

**Notes:** [Filled during implementation]

### Task 1.4: Run targeted validation [Simple]
**File:** n/a
**Tests:**
- `pytest tests/unit/strategy/engine/test_command_specs_contract.py -x`
- `pytest tests/unit/strategy/engine/test_command_registry_contract.py -x`

- [ ] Both targeted test modules pass
- [ ] Verify: no other tests broke (run `pytest tests/ --testmon` if testmon DB is fresh enough; otherwise just the strategy/engine slice)

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Registry exposes `planet_fms_action_order_types()` derived from `subcategories` tags
- [ ] Exactly five command specs carry the `planet_fms` subcategory
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
