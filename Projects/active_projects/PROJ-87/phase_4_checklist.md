# Phase 4: Fleet Capability & Battle Extraction [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-87 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract FleetCapabilityCalculator and FleetBattleAdapter

**File:** `game/strategy/data/fleet.py`
**New Files:** `game/strategy/data/fleet_capability_calculator.py`, `game/strategy/data/fleet_battle_adapter.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/fleet_combat/ -n 4`

---

## Tasks

### Task 4.1: Create FleetCapabilityCalculator [Simple]
**File:** `game/strategy/data/fleet_capability_calculator.py` (NEW)
- [x] Create `FleetCapabilityCalculator` class with `__init__(self, fleet)`
- [x] Move from Fleet:
  - `can_use_warp()`
  - `can_build_type()`
  - `has_space_shipyard` (property)
  - `get_warp_limiting_ship()`
- [x] Wire Fleet: `self._capabilities = FleetCapabilityCalculator(self)` + delegation wrappers

**Notes:** `get_capability_summary()` already delegated to FleetResourceAggregator in Phase 3.

### Task 4.2: Create FleetBattleAdapter [Simple]
**File:** `game/strategy/data/fleet_battle_adapter.py` (NEW)
- [x] Create `FleetBattleAdapter` class with `__init__(self, fleet)`
- [x] Move from Fleet:
  - `to_battle_ships()`
  - `update_from_battle_results()`
  - `_default_formation_positions()`
- [x] Wire Fleet: `self._battle = FleetBattleAdapter(self)` + delegation wrappers

**Notes:** These methods bridge strategy/simulation layers. Extraction clarifies the boundary.

### Task 4.3: Write tests and verify [Simple]
- [x] Write tests for FleetCapabilityCalculator (17 tests)
- [x] Write tests for FleetBattleAdapter (11 tests)
- [x] Run `pytest tests/unit/strategy/ -n 4` — 1499 passed
- [x] Run `pytest tests/integration/fleet_combat/ -n 4` — all pass
- [x] Run `pytest tests/integration/strategy/ -n 4` — all pass
- [x] Verify Fleet line count is now ≤ 500 lines (413 lines, 51% reduction from 834)
- [x] Update plan.md Current State

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
