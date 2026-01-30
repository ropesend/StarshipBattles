# Phase 4: Stats Service Location (NCA-006)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-51 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Move `stats.py` from `systems/` to `services/` directory
**Priority:** Normal (Minor issue)

---

## Overview

The `stats.py` file contains `ShipStatsCalculator`, which is used like a service (provides calculations without managing state). It should be in `services/` rather than `systems/`.

---

## Tasks

### Task 4.1: Move stats.py [Simple]
**File:** `game/simulation/systems/stats.py` -> `game/simulation/services/stats.py`
**Tests:** `pytest tests/unit/simulation/ -v`

- [ ] Verify `game/simulation/services/` directory exists
- [ ] Move file: `systems/stats.py` -> `services/stats.py`
- [ ] Update `game/simulation/services/__init__.py` to export `ShipStatsCalculator`:
  ```python
  from game.simulation.services.stats import ShipStatsCalculator
  ```
- [ ] Update `game/simulation/systems/__init__.py` - remove export if present
- [ ] Verify: `python -c "from game.simulation.services.stats import ShipStatsCalculator"`

**Notes:** [Filled during implementation]

### Task 4.2: Update Imports [Medium]
**Files:** All files importing from `game.simulation.systems.stats`
**Tests:** `pytest tests/ --testmon`

- [ ] Find all imports: `grep -r "from game.simulation.systems.stats" .`
- [ ] Find all imports: `grep -r "from game.simulation.systems import.*ShipStatsCalculator" .`
- [ ] Update each import to use new path:
  - Change: `from game.simulation.systems.stats import ShipStatsCalculator`
  - To: `from game.simulation.services.stats import ShipStatsCalculator`
- [ ] Common files to check:
  - `game/simulation/entities/ship.py`
  - `game/simulation/entities/ship_loader.py`
  - Test files in `tests/unit/simulation/`
- [ ] Verify: `pytest tests/unit/simulation/ -v`

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/simulation/ -v` - all simulation tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
