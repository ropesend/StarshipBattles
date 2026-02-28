# Phase 2: Strategy Data Objects (Highest Impact)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-211 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress (Task 2.1 complete)
**Objective:** Add DI to ShipInstance and FleetCapabilityCalculator - the two most-called violators
**Priority:** High - Highest impact for testability
**Risk:** Medium - ShipInstance is used everywhere, Fleet constructor needs updating
**Depends on:** Phase 1 (GameSession has registries)

---

## Tasks

### Task 2.1: Add registries to ShipInstance [DI-S-001, AR-001]
**Files:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/data/`

This is the most complex task in the project. `get_calculated_stats()` is called from 20+ sites.

- [x] Read `ship_instance.py` fully to understand dataclass structure, `create()`, `from_dict()`
- [x] Add `_registries: Optional[GameRegistries] = field(default=None, init=False, repr=False)`
- [x] Update `ShipInstance.create()` factory to accept and store `registries`
- [x] Update `ShipInstance.from_dict()` to accept and store `registries`
- [x] Update `get_calculated_stats()` to use `self._registries`, keep fallback temporarily
- [x] Thread registries through delegate managers - NOT NEEDED (delegates call ship.get_calculated_stats())
- [x] Update callers - FALLBACK HANDLES THIS (callers can pass registries optionally)
- [x] Write tests verifying ShipInstance uses stored registries (test_registries_di.py)
- [x] Verify: `pytest tests/ -n 12` passes (12876 passed, 4 pre-existing failures)

### Task 2.2: Add registries to FleetCapabilityCalculator [DI-S-002, AR-002]
**Files:** `game/strategy/data/fleet_capability_calculator.py`, `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/data/`

- [ ] Read `fleet_capability_calculator.py` to understand all usages of `_get_default_component_registry()`
- [ ] Add `component_registry: Dict` parameter to `__init__()`
- [ ] Update `ship_has_spaceyard()`, `space_shipyard_count`, `ship_has_ability()` to use stored registry
- [ ] Remove `_get_default_component_registry()` helper function entirely
- [ ] Update `Fleet.__init__()` to accept and forward `component_registry` or `registries`
- [ ] Update Fleet creation sites to pass registries
- [ ] Update static method callers in UI code (`fleet_data_source.py`, `fleet_report_filters.py`)
- [ ] Write tests verifying FleetCapabilityCalculator uses injected registry
- [ ] Verify: `pytest tests/ -n 12` passes

### Task 2.3: Remove ShipInstance.get_calculated_stats() fallback
**Files:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/ -n 12`

After all callers are updated in 2.1:
- [ ] Remove the `get_default_registry_provider()` fallback from `get_calculated_stats()`
- [ ] Raise explicit error if `self._registries` is None
- [ ] Remove `get_default_registry_provider` import if no other usages remain
- [ ] Verify: all tests pass

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` - full suite passes
- [ ] `get_calculated_stats()` no longer calls `get_default_registry_provider()`
- [ ] `_get_default_component_registry()` helper is deleted
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
