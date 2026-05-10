# Phase 2: Facade Bloat & Pass-Through Elimination

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-210 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove zero-value pass-through facade methods, expose delegates via properties
**Priority:** Critical — removes ~120 lines of maintenance burden, clarifies API
**Findings:** CQ-01, CQ-02, AR-001, ROF-006, DC-004

---

## Tasks

### Task 2.1: Expose Fleet Delegates as Public Properties [Complex] - COMPLETE
**Findings:** CQ-01 (28 pass-through methods, 120 lines of pure delegation)
**Files:** `game/strategy/data/fleet.py`, all callers of Fleet pass-through methods
**Tests:** `pytest tests/ -n 12`

- [x] Inventory all pass-through methods on Fleet (expected: ~28) — Found 20+
- [x] Expose `_resource_agg` as public `resources` property
- [x] Expose `_capabilities` as public `capabilities` property (already partially done)
- [x] Expose `_battle` as public `battle` property
- [x] Search codebase for all callers of each pass-through method
- [x] Update callers: `fleet.can_use_warp()` → `fleet.capabilities.can_use_warp()`
- [x] Update callers: `fleet.get_fleet_cargo_capacity()` → `fleet.resources.get_fleet_cargo_capacity()`
- [x] Update callers: `fleet.to_battle_ships()` → `fleet.battle.to_battle_ships()`
- [x] Remove all pass-through methods from Fleet class
- [x] Run full suite: `pytest tests/ -n 12` — **12929 passed, 4 failed (pre-existing), 1 skipped**
- [x] Verify: Fleet.py line count reduced by ~120 lines — **320 lines (was 552)**

**Notes:** Task complete. 65+ files modified. All test mock updates done. 4 pre-existing bug_13 failures (missing asset files).

### Task 2.2: Decouple Delegates from Fleet Internals [Medium] - DEFERRED
**Findings:** AR-001 (delegates store `_fleet` reference, access internals directly)
**Files:** `fleet_resource_aggregator.py`, `fleet_capability_calculator.py`, `fleet_battle_adapter.py`
**Tests:** `pytest tests/unit/strategy/test_fleet*.py -v`

- [x] Audit each delegate for `self._fleet.*` access patterns

**Analysis:** Delegates access a narrow interface: `ships`, `get_combat_capable_ships()`, `capabilities`, `speed`, `location`, `trigger_speed_recalculation()`. Full decoupling provides low value since delegates are "owned by" Fleet — this is the intended composition pattern. Creating a protocol interface would add complexity without meaningful benefit.

**Decision:** DEFER. Current design is acceptable. Delegates are private implementation details of Fleet, not independent services.

**Notes:** Task deferred. The composition pattern (Fleet owns delegates, delegates reference Fleet) is intentional and reasonable.

### Task 2.3: Remove Dead Pass-Through _default_formation_positions [Simple] - ALREADY DONE
**Findings:** DC-004
**Files:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_battle_adapter.py -v`

- [x] Verify _default_formation_positions on Fleet is only called through delegate
- [x] Remove Fleet._default_formation_positions() method — ALREADY REMOVED in Task 2.1
- [x] Update any callers to use FleetBattleAdapter directly — N/A, already using delegate
- [x] Run tests — 13 passed

**Notes:** This pass-through was removed as part of Task 2.1. The method only exists in FleetBattleAdapter now.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Zero pass-through facade methods remain on Fleet
- [x] Fleet.py < 350 lines (320 lines)
- [x] All tests passing (12929 passed, 4 failed pre-existing bug_13, 1 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
