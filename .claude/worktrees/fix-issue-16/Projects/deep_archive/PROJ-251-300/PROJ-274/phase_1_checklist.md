# Phase 1: Design Interface + Failing Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-274 1`
> 2. Only proceed if output shows PASSED

**Status:** Complete
**Objective:** Define `IShipMaterializer` protocol and establish failing unit tests for both implementations before writing any production code.

---

## Tasks

### Task 1.1: Create materializer module skeleton [Simple]
**File:** `game/simulation/services/ship_materializer.py` (NEW)
**Tests:** N/A (scaffold)

- [x] Create file with module docstring explaining the protocol and two implementations
- [x] Define `@runtime_checkable class IShipMaterializer(Protocol)` with single method `materialize(ship_spec, team_id, registries) -> Ship`
- [x] Define empty class stubs for `InstanceBackedMaterializer` and `DesignOnlyMaterializer` (just `pass` for now)

**Notes:** Created module at `game/simulation/services/ship_materializer.py`. Exported symbols: `IShipMaterializer` (protocol), `InstanceBackedMaterializer`, `DesignOnlyMaterializer`, `DesignLoader` (type alias for the callable shape `(design_id: str) -> dict`). Stubs raise `NotImplementedError("PROJ-274 Phase N implementation pending")` rather than `pass` so any accidental early use fails loudly. DesignOnlyMaterializer's `__init__` takes an optional `design_loader` now (not in Phase 2 — the loader contract is stable in Phase 1).

### Task 1.2: Write failing tests for InstanceBackedMaterializer [Medium]
**File:** `tests/unit/simulation/services/test_ship_materializer.py` (NEW)
**Tests:** `pytest tests/unit/simulation/services/test_ship_materializer.py -v`

- [x] Test: constructing materializer works
- [x] Test: `materialize` with `ship_spec.instance_ref` set calls `instance.to_ship(position, team_id, registries)` (use a mock ShipInstance)
- [x] Test: `materialize` with `ship_spec.instance_ref=None` raises `ValueError` with a helpful message mentioning `design_id`
- [x] Test: returned Ship has correct team_id
- [x] Test: `IShipMaterializer` protocol check (`isinstance(InstanceBackedMaterializer(), IShipMaterializer)`)
- [x] Run tests — verify they ALL fail (stub returns nothing)

**Notes:** Tests consolidated into one file for both materializers (Task 1.2 + 1.3). 3 InstanceBacked behavior tests + 1 protocol check fail with `NotImplementedError` / `AssertionError` as expected. Tests use `MagicMock()` for both the `ShipInstance` and `registries` — no layer violation. Key assertion: the position passed to `instance.to_ship` is a `(x, y)` tuple (matching the real `ShipInstance.to_ship(position: Tuple[float, float], team_id, *, registries)` signature at `game/strategy/data/ship_instance.py:592`).

### Task 1.3: Write failing tests for DesignOnlyMaterializer [Medium]
**File:** `tests/unit/simulation/services/test_ship_materializer.py`
**Tests:** `pytest tests/unit/simulation/services/test_ship_materializer.py -v`

- [x] Test: constructing with default design_loader works
- [x] Test: constructing with injected design_loader stores it
- [x] Test: `materialize` loads design by `ship_spec.design_id`, builds Ship, returns with correct team_id
- [x] Test: design_id not found → raises a clear error
- [x] Test: position from `ship_spec.spawn_position` is applied
- [x] Test: `IShipMaterializer` protocol check
- [x] Run tests — verify all fail

**Notes:** `ShipSpec` uses field name `position` (Vector2), NOT `spawn_position` — plan drafted the wrong name. Tests use `position` correctly. `materialize_spec_ships` at `game/simulation/battle_runner.py:128-133` applies pose (`ship.x = ship_spec.position.x`, `ship.y = ship_spec.position.y`, etc.) AFTER ship_builder returns, so materializer implementations do NOT need to set pose themselves. Test-level verification of pose application is thus out of scope for the materializer; it's verified by `materialize_spec_ships` tests instead. 3 DesignOnly behavior tests fail with `NotImplementedError` / `RuntimeError` as expected; 2 pre-implementation pass (constructor + protocol check). `monkeypatch` used to stub `Ship.from_dict` since its real implementation requires a full valid design dict.

### Task 1.4: Add `instance_ref` field to ShipSpec [Simple]
**File:** `game/simulation/battle_spec.py`
**Tests:** `pytest tests/unit/simulation/ -v -k battle_spec`

- [x] Locate `ShipSpec` frozen dataclass definition
- [x] Add field: `instance_ref: Optional[Any] = None` — placed near the end so positional construction isn't broken
- [x] Update dataclass docstring to describe the field: loose typing to avoid simulation-layer importing strategy; InstanceBackedMaterializer reads it
- [x] Run existing ShipSpec tests — they should all still pass (optional field, default None)

**Notes:** Added `instance_ref: Optional[Any] = None` as the LAST field (after `components`) of `ShipSpec` at L102-126. Added `Any` to the `typing` imports. Field documented: "PROJ-274: optional opaque reference to a strategy-layer ShipInstance ... Typed Optional[Any] because the simulation layer cannot import ShipInstance from the strategy layer (layer violation per docs/01_ARCHITECTURE.md). InstanceBackedMaterializer uses duck typing to invoke instance.to_ship(...)." Three dedicated tests confirm: (a) default is None, (b) accepts any object, (c) spec remains frozen. Full sim unit suite: 3324 pre-existing tests pass; only the 6 Phase-1-new failing tests remain (as expected per TDD).

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
- [x] Run `python Projects/scripts/validate_phase.py PROJ-274 1`
