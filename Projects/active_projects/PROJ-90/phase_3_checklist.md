# Phase 3: Ship.py Late Import Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-90 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Move all 4 unnecessary late imports in ship.py to module level. Deep analysis confirmed none are real circular dependency cycles. Also clean up the same pattern in ship_component_manager.py.

---

## Tasks

### Task 3.1: Move WeaponAbility import to module level [Simple]
**File:** `game/simulation/entities/ship.py`
**Verification:** No transitive Ship dependency in abilities module.
**Tests:** `pytest tests/unit/simulation/entities/ -v`

- [ ] Add at top (after existing component imports ~line 7): `from game.simulation.components.abilities import WeaponAbility, SeekerWeaponAbility`
  - Check exact import path first — may be `.abilities.weapons` or just `.abilities`
- [ ] Remove late import inside `max_weapon_range` property (~line 242-244)
- [ ] Remove the "INTENTIONAL LATE IMPORT" comment above it
- [ ] Verify: `python -c "from game.simulation.entities.ship import Ship; print('OK')"`

**Notes:**

---

### Task 3.2: Move ModifierService import to module level [Simple]
**Files:** `game/simulation/entities/ship.py`, `game/simulation/entities/ship_component_manager.py`
**Verification:** ModifierService does NOT import Ship (no cycle).
**Tests:** `pytest tests/unit/simulation/entities/ -v`

- [ ] In `ship.py`: Add at top: `from game.simulation.services.modifier_service import ModifierService`
- [ ] Remove late import and comment in `add_component()` (~line 505-507)
- [ ] Remove late import and comment in `add_components_bulk()` (~line 550-552)
- [ ] In `ship_component_manager.py`: Add at top: `from game.simulation.services.modifier_service import ModifierService`
- [ ] Remove late import at line 154
- [ ] Remove late import at line 187
- [ ] Verify: `python -c "from game.simulation.entities.ship import Ship; print('OK')"`

**Notes:**

---

### Task 3.3: Move ShipCombatEngine import to module level [Simple]
**File:** `game/simulation/entities/ship.py`
**Verification:** ShipCombatEngine uses TYPE_CHECKING only for Ship (no runtime cycle).
**Tests:** `pytest tests/unit/simulation/entities/ -v`

- [ ] Add at top (with entity imports ~line 16): `from .ship_combat_engine import ShipCombatEngine`
- [ ] Remove late import inside `combat_engine` property (~line 219)
- [ ] Keep the lazy property pattern (create on first access) — only remove the import line
- [ ] Update property docstring if it mentions "import cycles"
- [ ] Verify: `python -c "from game.simulation.entities.ship import Ship; print('OK')"`

**Notes:**

---

### Task 3.4: Move ShipSerializer import to module level [Simple]
**File:** `game/simulation/entities/ship.py`
**Also:** `game/simulation/entities/ship_serialization.py` (add protective comment)
**Verification:** `ship_serialization.py` has NO module-level Ship import (only TYPE_CHECKING + runtime late import in `from_dict`).
**Tests:** `pytest tests/unit/simulation/entities/ -v`

- [ ] In `ship.py`: Add at top: `from .ship_serialization import ShipSerializer`
- [ ] Remove late import in `to_dict()` (~line 835) and its "INTENTIONAL LATE IMPORT" comment
- [ ] Remove late import in `from_dict()` (~line 863) and its comment
- [ ] In `ship_serialization.py` line 133: Add comment above the runtime import of Ship:
  ```python
  # MUST remain a runtime import — ship.py imports ShipSerializer at module level
  ```
- [ ] Verify: `python -c "from game.simulation.entities.ship import Ship; print('OK')"`

**Notes:**

---

### Task 3.5: Move stdlib `import re` to module level [Simple]
**File:** `game/simulation/entities/ship.py`

- [ ] Add `import re` at top with other stdlib imports (after `import math`)
- [ ] Remove `import re` from inside `_format_ability_name` method

**Notes:**

---

### Task 3.6: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] `python -c "from game.simulation.entities.ship import Ship; print('OK')"` — no import errors
- [ ] `pytest tests/ -n 12` — all 7353+ tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `ship.py` has zero late imports (all moved to module level)
- [ ] `ship_component_manager.py` has zero ModifierService late imports
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
