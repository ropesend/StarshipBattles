# Phase 4: Stats Service Location (NCA-006)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-51 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Clean up orphaned `stats.py` from `systems/` directory
**Priority:** Normal (Minor issue)

---

## Overview

Investigation revealed that `game/simulation/systems/stats.py` was an **orphaned/dead code file** - a legacy duplicate of the actual `ShipStatsCalculator` which lives in `game/simulation/entities/ship_stats.py`.

**Key Discovery:**
- The actual `ShipStatsCalculator` used by `Ship` is in `entities/ship_stats.py`
- The `systems/stats.py` file was NOT imported by ANY production code
- Only the test file `test_ship_stats_calculator_phases.py` imported it
- The `stats_config.py` import of the module was unused (dead import)

**Resolution:**
- Deleted the orphaned `systems/stats.py` file
- Updated tests to use the correct `entities/ship_stats.py` module
- Removed dead import from `stats_config.py`

---

## Tasks

### Task 4.1: Investigate and Clean Up [Completed]
**Action Taken:** Delete orphaned dead code file

- [x] Verified `game/simulation/services/` directory exists
- [x] Investigated: `systems/stats.py` is NOT used by production code
- [x] Discovered: Actual ShipStatsCalculator is in `entities/ship_stats.py`
- [x] Deleted orphaned file: `systems/stats.py`
- [x] Did NOT add export to services/__init__.py (not needed)

**Notes:**
- The naming review (NCA-006) was based on outdated information
- The codebase has TWO ShipStatsCalculator classes:
  1. `entities/ship_stats.py` - The REAL one used by Ship entity
  2. `systems/stats.py` - An orphaned legacy version (now deleted)

### Task 4.2: Update Imports [Completed]
**Files Updated:**
- `game/ui/screens/builder/stats_config.py` - Removed unused import
- `tests/unit/simulation/systems/test_ship_stats_calculator_phases.py` - Updated to use correct module

- [x] Removed dead import from `stats_config.py`:
  - Removed: `import game.simulation.systems.stats as ship_stats`
- [x] Updated test file to import from correct location:
  - Changed: `from game.simulation.systems.stats import ShipStatsCalculator`
  - To: `from game.simulation.entities.ship_stats import ShipStatsCalculator`
- [x] Updated test file to use PROJ-50 DI pattern (fresh_registries fixture)
- [x] Verified: All 14 tests pass with correct import

**Notes:**
- Test file was testing the orphaned module, now tests the actual production code
- Test method existence checks updated to match actual class methods

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/simulation/systems/test_ship_stats_calculator_phases.py -v` - 14 passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
