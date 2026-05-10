# Phase 2: Strategy Data Objects (Highest Impact)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-211 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Read `fleet_capability_calculator.py` to understand all usages of `_get_default_component_registry()`
- [x] Add `component_registry: Dict` parameter to `__init__()` (already done in PROJ-212)
- [x] Update `ship_has_spaceyard()`, `ship_has_ability()` to prefer ship._registries.components
- [x] DEFERRED TO PHASE 5: Remove `_get_default_component_registry()` helper
- [x] Update `Fleet.__init__()` to accept and forward `component_registry`
- [x] Update `Fleet.from_dict()` to accept `registries` and pass to ships/calculator
- [x] Update `Empire.from_dict()` to accept `registries` and pass to Fleet.from_dict()
- [x] Static method callers unchanged - use ship._registries when available, fallback otherwise
- [x] Write tests verifying FleetCapabilityCalculator uses injected registry (test_fleet_capability_calculator_di.py)
- [x] Verify: `pytest tests/ -n 12` passes (12885 passed, 4 pre-existing failures)

**Notes:**
- Static methods `ship_has_spaceyard()` and `ship_has_ability()` now check ship._registries.components first
- Global fallback retained for backward compat; will be removed in Phase 5
- Fleet constructor now accepts optional `component_registry` parameter
- Fleet.from_dict() and Empire.from_dict() now accept optional `registries` parameter

### Task 2.3: MOVED TO PHASE 5

The fallback removal requires updating ~200 test files to inject registries via fixtures.
This is now part of Phase 5 (Cleanup) which includes test fixture updates.

See `phase_5_checklist.md` for the expanded scope.

---

## Phase Completion Checklist
- [x] All DI plumbing tasks complete (2.1, 2.2)
- [x] `pytest tests/ -n 12` - full suite passes (12885 passed, 4 pre-existing failures)
- [x] ShipInstance accepts and uses registries when provided
- [x] FleetCapabilityCalculator accepts and uses registry when provided
- [x] Fallback retained temporarily (removed in Phase 5)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
