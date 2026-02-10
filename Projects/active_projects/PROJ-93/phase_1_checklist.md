# Phase 1: Update Protocol Type Annotations

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-93 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update `IPostBattleShip` and `IResourceHolder` protocol `layers` return types from `Dict[str, Any]` to `Dict['LayerType', 'LayerData']` and strengthen conformance tests.

---

## Tasks

### Task 1.1: Update imports in protocols.py [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols_boundary.py`

- [ ] Add direct import `from game.core.constants import LayerType` (after line 37, before the `if TYPE_CHECKING:` block)
- [ ] Add `from game.simulation.entities.layer_data import LayerData` inside the existing `if TYPE_CHECKING:` block (line 39-40), after the existing HexCoord import
- [ ] Verify: file still imports cleanly (no circular import errors)

**Notes:**

---

### Task 1.2: Update IPostBattleShip.layers return type [Simple]
**File:** `game/core/protocols.py` line 416
**Tests:** `pytest tests/unit/core/test_protocols_boundary.py`

- [ ] Change line 416 from:
  ```python
  def layers(self) -> Dict[str, Any]:
  ```
  To:
  ```python
  def layers(self) -> Dict['LayerType', 'LayerData']:
  ```
- [ ] Verify: docstring `"""Ship layers containing components."""` unchanged

**Notes:**

---

### Task 1.3: Update IResourceHolder.layers return type [Simple]
**File:** `game/core/protocols.py` line 459
**Tests:** `pytest tests/unit/core/test_protocols_boundary.py`

- [ ] Change line 459 from:
  ```python
  def layers(self) -> Dict[str, Any]: ...
  ```
  To:
  ```python
  def layers(self) -> Dict['LayerType', 'LayerData']: ...
  ```

**Notes:**

---

### Task 1.4: Strengthen protocol conformance test [Simple]
**File:** `tests/unit/core/test_protocols_boundary.py` lines 74-77
**Tests:** `pytest tests/unit/core/test_protocols_boundary.py`

- [ ] Add imports at top of file:
  ```python
  from game.core.constants import LayerType
  from game.simulation.entities.layer_data import LayerData
  ```
- [ ] In `test_ship_has_layers_attribute` (line 74), keep existing assertion and add:
  ```python
  # Verify typed layer structure (PROJ-84 / PROJ-93)
  for key, value in simple_ship.layers.items():
      assert isinstance(key, LayerType), f"Layer key {key} should be LayerType"
      assert isinstance(value, LayerData), f"Layer value for {key} should be LayerData"
  ```
- [ ] Verify: `pytest tests/unit/core/test_protocols_boundary.py` — all tests pass

**Notes:**

---

### Task 1.5: Run full test suite [Simple]
- [ ] `pytest tests/ -n 12` — all tests pass (baseline: 7615 passed, 1 known flaky)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to audit
