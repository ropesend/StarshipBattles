# Phase 5: Delete duplicated constants + `fleet.py` re-exports

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-424 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete

**Sharded suite:** 20903/20903 passed, wall 142.6s, 12 shards.
**Implementation note:** the `TestOrderTypeCategorization` class in `test_order_types_characterization.py` was dropped in full (per Task 5.4) — the disjointness/subset/size/contents invariants live in `test_command_registry_contract.py` which now asserts them through `order_metadata.<property>`. The previously seen 56 "failures" running a partial subset were pre-existing test-isolation issues; under the full sharded run with the canonical fixtures, all are green.
**Depends on:** phase_4
**Review Mode:** standard
**Files (planned):**
- `game/strategy/data/order_types.py`
- `game/strategy/data/fleet.py`
- `tests/unit/strategy/data/test_order_types_no_duplicated_metadata.py`
- `tests/unit/strategy/data/test_order_types_characterization.py`

**Objective:** remove the redundant truth surfaces. Delete the four frozensets from `order_types.py` and the re-export pair in `fleet.py`. Full sharded suite must pass at this boundary.

---

## Tasks

### Task 5.1: Write the final-guard tests [Simple]
**File:** `tests/unit/strategy/data/test_order_types_no_duplicated_metadata.py`
**Tests:** `pytest tests/unit/strategy/data/test_order_types_no_duplicated_metadata.py -x`

- [ ] `test_order_types_module_no_longer_exports_metadata_constants` — `hasattr(order_types, 'MOVEMENT_ORDER_TYPES')` is False (and same for `ACTION_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES`, `PLANET_FMS_ACTION_ORDER_TYPES`). RED.
- [ ] `test_fleet_module_no_longer_re_exports_metadata_constants` — `hasattr(fleet, 'MOVEMENT_ORDER_TYPES')` is False (and same for `ACTION_ORDER_TYPES`). RED.
- [ ] Run; confirm both fail because the constants still exist

**Notes:** [Filled during implementation]

### Task 5.2: Delete the four frozensets [Simple]
**File:** `game/strategy/data/order_types.py`
**Tests:** `pytest tests/unit/strategy/data/test_order_types_no_duplicated_metadata.py -x`

- [ ] Delete `MOVEMENT_ORDER_TYPES`
- [ ] Delete `ACTION_ORDER_TYPES`
- [ ] Delete `PLANET_ACTION_ORDER_TYPES`
- [ ] Delete `PLANET_FMS_ACTION_ORDER_TYPES`
- [ ] Delete the comment block at lines 53-67 explaining the cycle workaround (no longer applies)
- [ ] **NO** compatibility aliases. **NO** `__getattr__` magic. The end state is explicit imports from `order_metadata_view.py`.
- [ ] Verify: `test_order_types_module_no_longer_exports_metadata_constants` passes

**Notes:** [Filled during implementation]

### Task 5.3: Delete the `fleet.py` re-exports [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/data/test_order_types_no_duplicated_metadata.py -x`

- [ ] Delete the `MOVEMENT_ORDER_TYPES` re-export at line 27
- [ ] Delete the `ACTION_ORDER_TYPES` re-export at line 28
- [ ] Verify: `test_fleet_module_no_longer_re_exports_metadata_constants` passes

**Notes:** [Filled during implementation]

### Task 5.4: Update the characterization test [Medium]
**File:** `tests/unit/strategy/data/test_order_types_characterization.py`
**Tests:** `pytest tests/unit/strategy/data/test_order_types_characterization.py -x`

- [ ] Drop or rewrite any assertion that asserts the existence/contents of the deleted constants
- [ ] Keep only the `OrderType` / `Order` / serialization helper coverage
- [ ] Verify: suite passes

**Notes:** [Filled during implementation]

### Task 5.5: Catch any remaining test imports [Medium]
**File:** any test still importing the deleted constants
**Tests:** `pytest tests/ --testmon` (or focused strategy slice)

- [ ] `rg -n "MOVEMENT_ORDER_TYPES|ACTION_ORDER_TYPES|PLANET_ACTION_ORDER_TYPES|PLANET_FMS_ACTION_ORDER_TYPES" tests/` — every remaining match must be updated to use `order_metadata`
- [ ] Verify: no `ImportError` from the deleted constants anywhere in the suite

**Notes:** [Filled during implementation]

### Task 5.6: Run the full sharded suite [Complex]
**File:** n/a
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded run green at this boundary
- [ ] If anything failed: triage and fix. Do not advance to Phase 6 until green

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] The four duplicated frozensets are gone from `order_types.py`
- [ ] The `fleet.py` re-exports are gone
- [ ] No compatibility aliases anywhere
- [ ] Full sharded suite green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
