# Phase 2: Move LayerType to Core [Medium Risk]

**Objective:** Move LayerType enum to core layer for proper architectural placement.

**Status:** Complete

**Depends on:** Phase 1 complete

**Tests to run after phase:** `pytest tests/unit/simulation/ -v`

---

## Task 2.1: Add LayerType to core/constants.py [Simple]

**File:** `game/core/constants.py`

- [x] Open file and scroll to end (after CombatConstants class)
- [x] Add LayerType enum definition:

```python
class LayerType(Enum):
    """Ship layer zones for component placement and damage distribution."""
    HULL = 0    # Innermost Chassis Layer
    CORE = 1
    INNER = 2
    OUTER = 3
    ARMOR = 4

    @staticmethod
    def from_string(s):
        return getattr(LayerType, s.upper())
```

- [x] Verify Enum import exists at top of file (should already have `from enum import Enum`)
- [x] Save file

**Notes:** Added at line 82 with PROJ-17 comment.

---

## Task 2.2: Update component_constants.py Re-export [Simple]

**File:** `game/simulation/components/component_constants.py`

- [x] Remove LayerType class definition (lines 17-26)
- [x] Add re-export after ComponentStatus class:

```python
# Re-export LayerType from core for backward compatibility
from game.core.constants import LayerType
```

- [x] Save file

**Notes:** Replaced class with re-export at line 19.

---

## Task 2.3: Verify Import Chain Works [Simple]

Run these commands to verify the import chain:

- [ ] `python -c "from game.simulation.components.component import LayerType; print(LayerType.CORE)"` - N/A (component.py doesn't export LayerType)
- [x] `python -c "from game.simulation.components.component_constants import LayerType; print(LayerType.ARMOR)"` ✓
- [x] `python -c "from game.core.constants import LayerType; print(LayerType.HULL)"` ✓

Note: First test in checklist is incorrect - component.py doesn't export LayerType, only component_constants.py does.

**Notes:** 2/3 tests passed; first test was invalid.

---

## Phase 2 Verification

After completing all tasks:

- [x] Run: `pytest tests/unit/simulation/ -v` (74 passed)
- [x] Run: `pytest tests/unit/ai/ -v` (189 passed)
- [x] Verify LayerType is in core: `grep -n "class LayerType" game/core/constants.py` → line 82
- [x] Verify re-export in component_constants: `grep -n "from game.core.constants import LayerType" game/simulation/components/component_constants.py` → line 19

**Phase complete when all boxes checked.** ✓
