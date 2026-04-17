# Phase 1: Design Interface + Failing Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-274 1`
> 2. Only proceed if output shows PASSED

**Status:** Not Started
**Objective:** Define `IShipMaterializer` protocol and establish failing unit tests for both implementations before writing any production code.

---

## Tasks

### Task 1.1: Create materializer module skeleton [Simple]
**File:** `game/simulation/services/ship_materializer.py` (NEW)
**Tests:** N/A (scaffold)

- [ ] Create file with module docstring explaining the protocol and two implementations
- [ ] Define `@runtime_checkable class IShipMaterializer(Protocol)` with single method `materialize(ship_spec, team_id, registries) -> Ship`
- [ ] Define empty class stubs for `InstanceBackedMaterializer` and `DesignOnlyMaterializer` (just `pass` for now)

**Notes:**

### Task 1.2: Write failing tests for InstanceBackedMaterializer [Medium]
**File:** `tests/unit/simulation/services/test_ship_materializer.py` (NEW)
**Tests:** `pytest tests/unit/simulation/services/test_ship_materializer.py -v`

- [ ] Test: constructing materializer works
- [ ] Test: `materialize` with `ship_spec.instance_ref` set calls `instance.to_ship(position, team_id, registries)` (use a mock ShipInstance)
- [ ] Test: `materialize` with `ship_spec.instance_ref=None` raises `ValueError` with a helpful message mentioning `design_id`
- [ ] Test: returned Ship has correct team_id
- [ ] Test: `IShipMaterializer` protocol check (`isinstance(InstanceBackedMaterializer(), IShipMaterializer)`)
- [ ] Run tests — verify they ALL fail (stub returns nothing)

**Notes:**

### Task 1.3: Write failing tests for DesignOnlyMaterializer [Medium]
**File:** `tests/unit/simulation/services/test_ship_materializer.py`
**Tests:** `pytest tests/unit/simulation/services/test_ship_materializer.py -v`

- [ ] Test: constructing with default design_loader works
- [ ] Test: constructing with injected design_loader stores it
- [ ] Test: `materialize` loads design by `ship_spec.design_id`, builds Ship, returns with correct team_id
- [ ] Test: design_id not found → raises a clear error
- [ ] Test: position from `ship_spec.spawn_position` is applied
- [ ] Test: `IShipMaterializer` protocol check
- [ ] Run tests — verify all fail

**Notes:**

### Task 1.4: Add `instance_ref` field to ShipSpec [Simple]
**File:** `game/simulation/battle_spec.py`
**Tests:** `pytest tests/unit/simulation/ -v -k battle_spec`

- [ ] Locate `ShipSpec` frozen dataclass definition
- [ ] Add field: `instance_ref: Optional[Any] = None` — placed near the end so positional construction isn't broken
- [ ] Update dataclass docstring to describe the field: loose typing to avoid simulation-layer importing strategy; InstanceBackedMaterializer reads it
- [ ] Run existing ShipSpec tests — they should all still pass (optional field, default None)

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-274 1`
