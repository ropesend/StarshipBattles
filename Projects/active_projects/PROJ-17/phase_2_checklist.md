# Phase 2: Move LayerType to Core [Medium Risk]

**Objective:** Move LayerType enum to core layer for proper architectural placement.

**Status:** Not Started

**Depends on:** Phase 1 complete

**Tests to run after phase:** `pytest tests/unit/simulation/ -v`

---

## Task 2.1: Add LayerType to core/constants.py [Simple]

**File:** `game/core/constants.py`

- [ ] Open file and scroll to end (after CombatConstants class)
- [ ] Add LayerType enum definition:

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

- [ ] Verify Enum import exists at top of file (should already have `from enum import Enum`)
- [ ] Save file

**Notes:**

---

## Task 2.2: Update component_constants.py Re-export [Simple]

**File:** `game/simulation/components/component_constants.py`

- [ ] Remove LayerType class definition (lines 17-26)
- [ ] Add re-export after ComponentStatus class:

```python
# Re-export LayerType from core for backward compatibility
from game.core.constants import LayerType
```

- [ ] Save file

**Notes:**

---

## Task 2.3: Verify Import Chain Works [Simple]

Run these commands to verify the import chain:

- [ ] `python -c "from game.simulation.components.component import LayerType; print(LayerType.CORE)"`
- [ ] `python -c "from game.simulation.components.component_constants import LayerType; print(LayerType.ARMOR)"`
- [ ] `python -c "from game.core.constants import LayerType; print(LayerType.HULL)"`

All three should print the expected enum value without errors.

**Notes:**

---

## Phase 2 Verification

After completing all tasks:

- [ ] Run: `pytest tests/unit/simulation/ -v`
- [ ] Run: `pytest tests/unit/ai/ -v` (AI uses LayerType)
- [ ] Verify LayerType is in core: `grep -n "class LayerType" game/core/constants.py`
- [ ] Verify re-export in component_constants: `grep -n "from game.core.constants import LayerType" game/simulation/components/component_constants.py`

**Phase complete when all boxes checked.**
