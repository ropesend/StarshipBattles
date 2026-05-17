# Phase 6: Docs convergence + final grep gate

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-424 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_5
**Review Mode:** standard
**Files (planned):**
- `docs/systems/orders_system.md`
- `docs/04_SERVICES.md`
- `docs/systems/satellites.md`

**Objective:** update docs to describe `order_metadata` as the single read path. Remove all "edit `ORDER_TO_ABILITY_MAP` or frozensets manually" guidance. Document the `planet_fms` subcategory and the lazy-view cycle break. Run the final grep gate and the sharded suite one last time.

---

## Tasks

### Task 6.1: Update `docs/systems/orders_system.md` [Medium]
**File:** `docs/systems/orders_system.md`
**Tests:** n/a (docs)

- [ ] Replace any reference to `MOVEMENT_ORDER_TYPES` / `ACTION_ORDER_TYPES` / `PLANET_ACTION_ORDER_TYPES` / `PLANET_FMS_ACTION_ORDER_TYPES` with `order_metadata.<property>`
- [ ] Add a short section explaining the lazy-view cycle break (one-paragraph rationale: the registry imports handlers; handlers import `OrderType` from `order_types.py`; the view defers the import to `_registry()` so the cycle never closes at module load)
- [ ] Document the `subcategories=frozenset({"planet_fms"})` tag on FMS handlers and how `CommandRegistry.planet_fms_action_order_types()` derives from it
- [ ] Remove any contributor guidance that says "add to the frozenset when you add a new order type" — direct contributors to register a `CommandSpec` instead
- [ ] Verify: file reads correctly with no broken cross-references

**Notes:** [Filled during implementation]

### Task 6.2: Update `docs/04_SERVICES.md` [Simple]
**File:** `docs/04_SERVICES.md`
**Tests:** n/a (docs)

- [ ] If the file references `action_time_resolver.py`'s `ORDER_TO_ABILITY_MAP`, replace with `order_metadata.order_to_ability_map`
- [ ] Note the call-time read (no import-time snapshot)
- [ ] Verify: no stale references

**Notes:** [Filled during implementation]

### Task 6.3: Update `docs/systems/satellites.md` [Simple]
**File:** `docs/systems/satellites.md`
**Tests:** n/a (docs)

- [ ] Replace any `PLANET_FMS_ACTION_ORDER_TYPES` reference with the registry-derivation explanation
- [ ] If satellites doc enumerates the FMS-action orders, cite the `subcategories` tag mechanism rather than the deleted frozenset
- [ ] Verify: no stale references

**Notes:** [Filled during implementation]

### Task 6.4: Final grep gate [Simple]
**File:** n/a
**Tests:** n/a

- [ ] `rg -n "MOVEMENT_ORDER_TYPES|ACTION_ORDER_TYPES|PLANET_ACTION_ORDER_TYPES|PLANET_FMS_ACTION_ORDER_TYPES|ORDER_TO_ABILITY_MAP" game docs tests`
- [ ] Expected matches (production): ONLY `game/strategy/engine/commands/registry.py` derivation method names and `game/strategy/engine/commands/order_metadata_view.py`
- [ ] Expected matches (docs): only explanatory text about the migration, no "edit this constant" guidance
- [ ] Expected matches (tests): only updated assertions referencing `order_metadata` or the registry derivations; no test imports the deleted constants
- [ ] Verify: zero stale references

**Notes:** [Filled during implementation]

### Task 6.5: Final focused + full sharded run [Complex]
**File:** n/a
**Tests:**
- `pytest tests/unit/strategy/engine/commands/test_order_metadata_view.py tests/unit/strategy/engine/test_command_registry_contract.py tests/unit/strategy/services/test_action_time_resolver.py -x`
- `python Tools/test_sharded/test_sharded.py`

- [ ] Focused suite green
- [ ] Full sharded suite green

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All three docs pages reference `order_metadata` as the single read path
- [ ] No stale "edit the constant" guidance anywhere in docs
- [ ] Final grep gate clean
- [ ] Full sharded suite green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Project Complete — awaiting audit`
