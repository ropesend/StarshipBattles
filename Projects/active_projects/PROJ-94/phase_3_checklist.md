# Phase 3: Wire Up IResourceReader Protocol

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-94 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Type `IPostBattleShip.resources` properly and clean up unnecessary defensive code.

---

## Tasks

### Task 3.1: Add get_resource_names to IResourceReader protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `get_resource_names` method to `IResourceReader` protocol (after line 378):
  ```python
  def get_resource_names(self) -> List[str]:
      """Return list of all registered resource names."""
      ...
  ```
- [ ] Verify `List` is imported from typing (check existing imports at top of file)
- [ ] Verify: `python -c "from game.core.protocols import IResourceReader"`

**Notes:**

---

### Task 3.2: Update IPostBattleShip.resources type [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Change line 421 from:
  ```python
  def resources(self) -> Any:
      """Resource registry (may be None). Should satisfy IResourceReader if present."""
  ```
  To:
  ```python
  def resources(self) -> Optional['IResourceReader']:
      """Resource registry (may be None)."""
  ```
- [ ] Ensure `Optional` is imported from typing (check existing imports)
- [ ] Verify: `python -c "from game.core.protocols import IPostBattleShip, IResourceReader"`

**Notes:**

---

### Task 3.3: Verify IResourceReader protocol matches ResourceRegistry [Simple]
- [ ] Confirm `ResourceRegistry` satisfies `IResourceReader`:
  - Has `get_value(name: str) -> float` (resource_manager.py line ~120)
  - Has `get_max_value(name: str) -> float` (resource_manager.py line ~130)
  - Has `get_resource_names() -> List[str]` (resource_manager.py line 197-199, added by PROJ-91)
- [ ] Run: `pytest tests/ --testmon`

**Notes:**

---

### Task 3.4: Remove defensive getattr for is_derelict [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ tests/integration/strategy/ --testmon`

- [ ] Line 188: Change `instance.is_derelict = getattr(ship, 'is_derelict', False)` to `instance.is_derelict = ship.is_derelict`
- [ ] Line 549: Change `self.is_derelict = getattr(ship, 'is_derelict', False)` to `self.is_derelict = ship.is_derelict`
- [ ] Rationale: `IPostBattleShip` declares `is_derelict` as required property (line 411) -- getattr is unnecessary defensive code
- [ ] Run tests: `pytest tests/unit/strategy/ship_instance/ tests/integration/strategy/ --testmon`

**Notes:**

---

### Task 3.5: Run full test suite [Simple]
- [ ] `pytest tests/ -n 12` -- all tests pass
- [ ] Record test count

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
