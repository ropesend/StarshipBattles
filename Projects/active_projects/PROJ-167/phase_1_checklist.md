# Phase 1: Create Ability Color Hint Constants

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-167 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create `game/simulation/components/abilities/ui_colors.py` with all 25 named constants for ability display hints

---

## Tasks

### Task 1.1: Create ui_colors.py [Simple]
**File:** `game/simulation/components/abilities/ui_colors.py` (NEW)
**Tests:** `pytest tests/unit/simulation/components/abilities/ -q` (should pass unchanged — no code using constants yet)

- [ ] Create new file `game/simulation/components/abilities/ui_colors.py`
- [ ] Add module docstring: `"""Centralized color constants for ability UI display hints (PROJ-167)."""`
- [ ] Define all 25 constants (hex strings) — see constant list below
- [ ] Add `__all__` export list with all constant names
- [ ] Verify: file imports cleanly with `python -c "from game.simulation.components.abilities.ui_colors import *"`

**Constants to define:**
```python
# Weapons & Offense
HINT_DAMAGE = '#FF6464'           # Red — damage values, targeting offense
HINT_RANGE = '#FFA500'            # Orange — weapon range, fuel consumption
HINT_RELOAD = '#FFC864'           # Gold — reload time
HINT_PROJECTILE_SPEED = '#C8C832' # Dirty yellow — projectile speed, ammo consumption
HINT_ACCURACY = '#FFFF00'         # Bright yellow — beam accuracy, damage ignore, energy gen, harvest rate

# Defense & Shields
HINT_SHIELD_CAP = '#00FFFF'       # Cyan — shield capacity, warp capable, construction bonus
HINT_SHIELD_REGEN = '#00C8FF'     # Deep sky blue — shield regeneration
HINT_EVASION = '#64FFFF'          # Light cyan — evasion, default resource storage

# Propulsion
HINT_THRUST = '#64FF64'           # Light green — combat thrust
HINT_TURN_SPEED = '#64FF96'       # Mint green — maneuver/turn speed
HINT_STRATEGIC_MOBILITY = '#6496FF' # Slate blue — strategic movement
HINT_WARP_ENERGY = '#64C8FF'      # Light blue — warp energy, energy consumption

# Crew & Support
HINT_CREW_CAP = '#96FF96'         # Pale green — crew capacity, command, structural integrity, optional modifier
HINT_LIFE_SUPPORT = '#96FFFF'     # Pale cyan — life support capacity
HINT_CREW_REQ = '#FF9696'         # Pale red — crew requirement

# Cargo & Resources
HINT_CARGO_PASSENGER = '#98FB98'  # Pale green (web) — passenger cargo
HINT_CARGO_GENERIC = '#FFD700'    # Gold — generic cargo, mandatory modifier
HINT_COLONIZE = '#00FF00'         # Bright green — colonization, resource harvesting, production

# Special
HINT_SUPERWEAPON = '#FF4444'      # Dark red — all superweapon abilities
HINT_REQUIREMENT = '#FFCC66'      # Tan/light orange — requires C&C, requires propulsion

# Neutral / Default
HINT_NEUTRAL = '#C8C8C8'          # Light gray — hangar, cycle time, fallback
HINT_DEFAULT = '#FFFFFF'          # White — max tonnage, default resource types
```

**Notes:**

---

### Task 1.2: Add to __init__.py exports (if applicable) [Simple]
**File:** `game/simulation/components/abilities/__init__.py`
**Tests:** No test changes needed

- [ ] Check if `__init__.py` re-exports submodules — if it uses explicit `__all__`, add `'ui_colors'`
- [ ] If `__init__.py` does NOT re-export submodules, skip this task (constants will be imported directly)
- [ ] Verify: no import errors in existing tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon -q` passes with no failures
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
