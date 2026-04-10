# PROJ-247 Phase 1: Change Ship.id to UUID4

> **BEFORE MARKING THIS PHASE COMPLETE:**
> Run: `pytest tests/unit/simulation/entities/ -x`

## Objective
Ship.id becomes a stable UUID4 string instead of str(id(self)).

## Status: Not Started

---

### Task 1.1: Change Ship.__init__ [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/entities/ -x`

- [ ] Add `import uuid` at top of file
- [ ] Line 78: Change `self.id: str = str(id(self))` to `self.id: str = str(uuid.uuid4())`
- [ ] Ensure Ship clone/copy operations preserve the id (check __copy__, __deepcopy__, or clone() methods)
- [ ] Run tests: `pytest tests/unit/simulation/entities/ -x`

**Notes:** All existing callers use ship.id as an opaque string key. UUID4 strings are still strings — no type change needed.
