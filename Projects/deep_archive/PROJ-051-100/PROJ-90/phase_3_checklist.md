# Phase 3: Ship.py Late Import Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-90 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Move all unnecessary late imports in ship.py to module level. Also clean up the same pattern in ship_component_manager.py.

---

## Tasks

### Task 3.1: Move WeaponAbility import to module level [Simple]
**File:** `game/simulation/entities/ship.py`
**Status:** N/A - Already moved to ShipStatQuerier

- [x] N/A - WeaponAbility import was already refactored out of ship.py in PROJ-88
  - `max_weapon_range` property now delegates to `stat_querier.max_weapon_range`

**Notes:** No late import of WeaponAbility exists in ship.py anymore.

---

### Task 3.2: Move ModifierService import to module level [Simple]
**Files:** `game/simulation/entities/ship.py`, `game/simulation/entities/ship_component_manager.py`
**Status:** CANNOT MOVE - Real circular dependency exists

- [x] Analyzed: `game.simulation.services.__init__.py` imports `VehicleDesignService` which imports `Ship`
- [x] Moving ModifierService to module-level causes: `ImportError: cannot import name 'Ship' from partially initialized module`
- [x] Updated comments to document the real reason for late import
- [x] `ship_component_manager.py` was deleted in PROJ-88, no action needed

**Notes:** ModifierService MUST remain a late import. The cycle is:
Ship -> services/__init__.py -> VehicleDesignService -> Ship

---

### Task 3.3: Move ShipCombatEngine import to module level [Simple]
**File:** `game/simulation/entities/ship.py`

- [x] Add at top: `from .ship_combat_engine import ShipCombatEngine`
- [x] Remove late import inside `combat_engine` property
- [x] Keep the lazy property pattern (create on first access)
- [x] Update property docstring - removed "import cycles" mention
- [x] Verify: `python -c "from game.simulation.entities.ship import Ship; print('OK')"` - OK

**Notes:** ShipCombatEngine uses TYPE_CHECKING for Ship, so no runtime cycle.

---

### Task 3.4: Move ShipSerializer import to module level [Simple]
**File:** `game/simulation/entities/ship.py`

- [x] In `ship.py`: Add at top: `from .ship_serialization import ShipSerializer`
- [x] Remove late import in `to_dict()` and its comment
- [x] Remove late import in `from_dict()` and its comment
- [x] In `ship_serialization.py`: Updated comment to: `# MUST remain a runtime import — ship.py imports ShipSerializer at module level`
- [x] Verify: `python -c "from game.simulation.entities.ship import Ship; print('OK')"` - OK

**Notes:** ShipSerializer has TYPE_CHECKING import of Ship, keeping its from_dict() runtime import.

---

### Task 3.5: Move stdlib `import re` to module level [Simple]
**File:** `game/simulation/entities/ship.py`
**Status:** N/A - No `import re` exists in ship.py

- [x] Verified: No `import re` found in ship.py (checked with grep)

**Notes:** The `_format_ability_name` method no longer exists or uses regex.

---

### Task 3.6: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] `python -c "from game.simulation.entities.ship import Ship; print('OK')"` — OK
- [x] `pytest tests/ -n 12` — 7540 passed

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All applicable task checkboxes above are checked
- [x] `ship.py` has only essential late imports (ModifierService must stay)
- [x] `ship_component_manager.py` deleted in PROJ-88 - N/A
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

## Summary of Changes
- Moved ShipCombatEngine import to module level
- Moved ShipSerializer import to module level
- Updated ShipSerializer.from_dict() comment to document the cycle
- Updated combat_engine docstring to remove "import cycles" mention
- ModifierService MUST stay as late import (real cycle via services/__init__.py)
- WeaponAbility and `import re` were already removed in previous projects
