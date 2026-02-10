# Phase 3: Wire Up IResourceReader Protocol

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-94 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Type `IPostBattleShip.resources` properly and clean up unnecessary defensive code.

---

## Tasks

### Task 3.1: Add get_resource_names to IResourceReader protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/ --testmon`

- [x] Add `get_resource_names` method to `IResourceReader` protocol (after line 378):
  ```python
  def get_resource_names(self) -> List[str]:
      """Return list of all registered resource names."""
      ...
  ```
- [x] Verify `List` is imported from typing (check existing imports at top of file)
- [x] Verify: `python -c "from game.core.protocols import IResourceReader"`

**Notes:** Added after get_max_value method.

---

### Task 3.2: Update IPostBattleShip.resources type [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/ --testmon`

- [x] Change line 421 from:
  ```python
  def resources(self) -> Any:
      """Resource registry (may be None). Should satisfy IResourceReader if present."""
  ```
  To:
  ```python
  def resources(self) -> Optional['IResourceReader']:
      """Resource registry (may be None)."""
  ```
- [x] Ensure `Optional` is imported from typing (check existing imports)
- [x] Verify: `python -c "from game.core.protocols import IPostBattleShip, IResourceReader"`

**Notes:** Updated type annotation and simplified docstring.

---

### Task 3.3: Verify IResourceReader protocol matches ResourceRegistry [Simple]
- [x] Confirm `ResourceRegistry` satisfies `IResourceReader`:
  - Has `get_value(name: str) -> float` (resource_manager.py line ~120)
  - Has `get_max_value(name: str) -> float` (resource_manager.py line ~130)
  - Has `get_resource_names() -> List[str]` (resource_manager.py line 197-199, added by PROJ-91)
- [x] Run: `pytest tests/ --testmon`

**Notes:** isinstance(ResourceRegistry(), IResourceReader) returns True.

---

### Task 3.4: Remove defensive getattr for is_derelict [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ tests/integration/strategy/ --testmon`

- [x] Line 188: Change `instance.is_derelict = getattr(ship, 'is_derelict', False)` to `instance.is_derelict = ship.is_derelict`
- [x] Line 549: Change `self.is_derelict = getattr(ship, 'is_derelict', False)` to `self.is_derelict = ship.is_derelict`
- [x] Rationale: `IPostBattleShip` declares `is_derelict` as required property (line 411) -- getattr is unnecessary defensive code
- [x] Run tests: `pytest tests/unit/strategy/ship_instance/ tests/integration/strategy/ --testmon`

**Notes:** Already completed in Phase 1 (verified via grep - no getattr.*is_derelict in ship_instance.py).

---

### Task 3.5: Run full test suite [Simple]
- [x] `pytest tests/ -n 12` -- all tests pass
- [x] Record test count: 7595 passed

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
